//
//  CustomCameraView.swift
//  Astra Staging Portal
//
//  AVFoundation-based camera with a 4:3 preview window (matches Google
//  Camera's "Photo 4:3" mode). Replaces UIImagePickerController so we can:
//    - show the preview letterboxed at 4:3 instead of fullscreen
//    - offer ultrawide/wide/tele zoom toggles (0.5× / 1× / 2×) that also
//      ramp gradually on long-press
//    - switch between photo and video modes with a toggle above the
//      zoom chips
//    - pick the staging area inline (incl. "+ New Area") without closing
//      the camera
//
//  Photos are captured at the device's native 4:3 aspect (the JPEG is then
//  downscaled by MediaProcessor.writePhoto to 1920×1440). Video records at
//  720p (1280×720) via the session preset — MediaProcessor.compressVideo
//  handles a further re-encode when needed.
//

import AVFoundation
import AVKit
import SwiftUI
import UIKit

// MARK: - Lens identifier (shared between view + controller)

enum CameraLens: String, Hashable, Sendable {
    case ultraWide, wide, tele

    var label: String {
        switch self {
        case .ultraWide: return ".5"
        case .wide:      return "1×"
        case .tele:      return "2"
        }
    }
    var ratio: CGFloat {
        switch self {
        case .ultraWide: return 0.5
        case .wide:      return 1.0
        case .tele:      return 2.0
        }
    }
}

// MARK: - SwiftUI view

struct CustomCameraView: View {
    let initialMediaType: CaptureMediaType
    let staging: Staging
    let areas: [StagingArea]
    let initialAreaId: String?
    let token: String
    /// Returns the newly-created area or nil on failure.
    let onCreateArea: (String) async -> StagingArea?
    /// Fires for each successful capture while the camera stays open.
    let onCaptureTaken: (CapturedMedia, CaptureMediaType, StagingArea?) -> Void
    /// Fires only when the user explicitly closes the camera.
    let onResult: (CapturedMedia?, CaptureMediaType, StagingArea?) -> Void

    @State private var controller = CameraController()
    @State private var dictationController = DictationController.shared
    @State private var captureStore = CaptureStore.shared
    @State private var galleryOpen = false
    /// Wall-clock time the current video recording started.
    @State private var videoRecordStartedAt: Date?
    @State private var videoElapsedSec: TimeInterval = 0
    @State private var videoTickTimer: Timer?
    @State private var mediaType: CaptureMediaType
    @State private var areaList: [StagingArea]
    @State private var selectedArea: StagingArea?
    @State private var areaPickerOpen = false
    @State private var isRecording = false
    @State private var authorized = false
    @State private var authChecked = false
    @State private var availableLenses: [CameraLens] = []
    @State private var zoomRatio: CGFloat = 1.0
    /// Live max zoom read from the active device, then clamped at 2× —
    /// digital zoom past that is too noisy to be useful on phones
    /// without a dedicated telephoto lens. Adjust if you add a tele.
    @State private var deviceMaxZoom: CGFloat = 2.0
    /// Physical device orientation, updated via UIDevice notifications.
    /// Used to set the capture connection's rotation angle so landscape-
    /// held shots come out as landscape JPEGs instead of rotated portraits.
    @State private var deviceOrientation: UIDeviceOrientation = .portrait
    /// Zoom value captured at the start of a press-and-hold slide gesture.
    /// During the drag, `zoomRatio` is derived from this + the drag offset.
    @State private var slideAnchorZoom: CGFloat = 1.0
    /// True while a press-and-hold dial gesture is active — hides the
    /// chips and overlays the arc dial on top of the preview.
    @State private var zoomDialActive: Bool = false

    init(
        initialMediaType: CaptureMediaType,
        staging: Staging,
        areas: [StagingArea],
        initialAreaId: String?,
        token: String,
        onCreateArea: @escaping (String) async -> StagingArea?,
        onCaptureTaken: @escaping (CapturedMedia, CaptureMediaType, StagingArea?) -> Void,
        onResult: @escaping (CapturedMedia?, CaptureMediaType, StagingArea?) -> Void,
    ) {
        self.initialMediaType = initialMediaType
        self.staging = staging
        self.areas = areas
        self.initialAreaId = initialAreaId
        self.token = token
        self.onCreateArea = onCreateArea
        self.onCaptureTaken = onCaptureTaken
        self.onResult = onResult
        _mediaType = State(initialValue: initialMediaType)
        _areaList = State(initialValue: areas)
        _selectedArea = State(initialValue: areas.first(where: { $0.id == initialAreaId }))
    }

    var body: some View {
        ZStack {
            // Black backdrop extends behind the status bar + home indicator.
            Color.black.ignoresSafeArea()

            // Three stacked sections with no overlap:
            //   [close bar]  fixed
            //   [preview  ]  takes all remaining middle space
            //   [controls ]  fixed: zoom chips → mode toggle → shutter row
            VStack(spacing: 0) {
                HStack {
                    Button { onResult(nil, mediaType, selectedArea) } label: {
                        Image(systemName: "xmark")
                            .font(.title3.bold())
                            .foregroundStyle(.white)
                            .frame(width: 40, height: 40)
                            .background(Color.black.opacity(0.55))
                            .clipShape(Circle())
                            .overlay(Circle().stroke(Color.white.opacity(0.9), lineWidth: 1.5))
                    }
                    Spacer()
                    // Hide the dictation mic entirely in video mode —
                    // the video captures audio already.
                    if mediaType != .video {
                        topRightMicButton
                    }
                }
                .padding(.horizontal, 16)
                .padding(.top, 8)
                .padding(.bottom, 8)

                // Preview occupies the entire middle section. aspectRatio(.fit)
                // lets it scale to the largest 4:3 rectangle that fits.
                ZStack(alignment: .top) {
                    Color.black
                    CameraPreview(session: controller.session)
                        .aspectRatio(3.0 / 4.0, contentMode: .fit)
                        .clipped()
                    recordingBadge
                        .padding(.top, 14)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .contentShape(Rectangle())
                .gesture(
                    // Horizontal swipe toggles photo ↔ video mode, like
                    // the native camera app. Disabled while recording.
                    DragGesture(minimumDistance: 30)
                        .onEnded { value in
                            guard !isRecording else { return }
                            let dx = value.translation.width
                            let dy = value.translation.height
                            if abs(dx) > abs(dy) * 1.5 {
                                if dx < -30 && mediaType == .photo {
                                    mediaType = .video
                                } else if dx > 30 && mediaType == .video {
                                    mediaType = .photo
                                }
                            }
                        }
                )

                // Live zoom readout — slotted between preview and
                // controls so the value is clearly visible while dragging
                // without overlapping the preview.
                Text(String(format: "%.1f×", zoomRatio))
                    .font(.headline.bold())
                    .foregroundStyle(.white)
                    .frame(height: 22)
                    .opacity(zoomDialActive ? 1 : 0)
                    .padding(.top, 6)

                // Bottom cluster. Zoom chips sit ABOVE the mode toggle.
                // While the dial is active the ruler is overlaid AT THE
                // SAME LOCATION as the chips — the chips stay in the
                // hierarchy (opacity 0) so the drag gesture keeps tracking
                // the user's finger.
                VStack(spacing: 12) {
                    ZStack {
                        zoomChips
                            .opacity(zoomDialActive ? 0.001 : 1)
                        if zoomDialActive {
                            HorizontalZoomRuler(
                                zoomRatio: zoomRatio,
                                minZoom: 0.5,
                                maxZoom: deviceMaxZoom,
                            )
                            .allowsHitTesting(false)
                            .transition(.opacity)
                        }
                    }
                    .frame(height: 42)
                    modeToggle
                        .disabled(isRecording)
                    bottomRow
                        .padding(.horizontal, 16)
                }
                .padding(.top, 6)
                .padding(.bottom, 20)
            }
        }
        .task {
            await ensureAuthorised()
            if authorized {
                let lenses = await controller.configure(for: cameraMode(for: mediaType))
                availableLenses = lenses
                deviceMaxZoom = min(controller.currentMaxZoom(), 2.0)
                controller.start()
            }
        }
        .onAppear {
            UIDevice.current.beginGeneratingDeviceOrientationNotifications()
            deviceOrientation = UIDevice.current.orientation
        }
        .onReceive(
            NotificationCenter.default.publisher(for: UIDevice.orientationDidChangeNotification),
        ) { _ in
            let o = UIDevice.current.orientation
            if o.isValidInterfaceOrientation || o.isLandscape || o.isPortrait {
                deviceOrientation = o
            }
        }
        .onChange(of: mediaType) { _, newMode in
            Task {
                controller.stop()
                _ = await controller.configure(for: cameraMode(for: newMode))
                deviceMaxZoom = min(controller.currentMaxZoom(), 2.0)
                controller.start()
            }
        }
        .onDisappear {
            controller.stop()
            UIDevice.current.endGeneratingDeviceOrientationNotifications()
        }
        .fullScreenCover(isPresented: $galleryOpen) {
            InCameraGallery(
                captures: captureStore.captures(forStaging: staging.id),
                captureStore: captureStore,
                token: token,
                onDismiss: { galleryOpen = false },
            )
        }
        .sheet(isPresented: $areaPickerOpen) {
            InCameraAreaPicker(
                areas: areaList,
                selectedId: selectedArea?.id,
                token: token,
                onCreate: { name in
                    if let created = await onCreateArea(name) {
                        areaList.append(created)
                        selectedArea = created
                        areaPickerOpen = false
                    }
                },
                onSelect: { area in
                    selectedArea = area
                    areaPickerOpen = false
                },
                onDismiss: { areaPickerOpen = false }
            )
        }
    }

    // MARK: - Subviews

    private var modeToggle: some View {
        HStack(spacing: 2) {
            modeChip(label: "Photo", active: mediaType == .photo) {
                mediaType = .photo
            }
            modeChip(label: "Video", active: mediaType == .video) {
                mediaType = .video
            }
        }
        .padding(4)
        .background(Color.white.opacity(0.18))
        .clipShape(Capsule())
    }

    private func modeChip(label: String, active: Bool, onTap: @escaping () -> Void) -> some View {
        Button(action: onTap) {
            Text(label)
                .font(.subheadline.bold())
                .foregroundStyle(active ? .black : .white)
                .padding(.horizontal, 18)
                .padding(.vertical, 8)
                .background(active ? Color.white : Color.clear)
                .clipShape(Capsule())
        }
        .buttonStyle(.plain)
    }

    /// Always renders exactly 3 chips. Rule:
    /// - z < 1  → [z×, 1, 2]
    /// - 1 ≤ z ≤ 2 → [0.5, z×, 2]
    /// - z > 2  → [0.5, 1, z×]
    /// The "selected" chip carries the "×" suffix; tapping any other chip
    /// snaps to that value. Press-and-hold any chip opens the ruler.
    private var displayedChipValues: [CGFloat] {
        let z = (zoomRatio * 10).rounded() / 10
        if z < 1   { return [z, 1, 2] }
        if z <= 2  { return [0.5, z, 2] }
        return [0.5, 1, z]
    }

    private var selectedChipIndex: Int {
        if zoomRatio < 1   { return 0 }
        if zoomRatio <= 2  { return 1 }
        return 2
    }

    private var zoomChips: some View {
        HStack(spacing: 10) {
            ForEach(displayedChipValues.indices, id: \.self) { idx in
                let value = displayedChipValues[idx]
                let isSelected = idx == selectedChipIndex
                Text(chipLabel(value: value, selected: isSelected))
                    .font(.caption.bold())
                    .foregroundStyle(isSelected ? .black : .white)
                    .frame(width: 48, height: 42)
                    .background(isSelected ? Color.white : Color.white.opacity(0.2))
                    .clipShape(Capsule())
                    .onTapGesture {
                        // Tap non-selected → snap. Tap selected → no-op.
                        if !isSelected {
                            zoomRatio = value
                            controller.setVideoZoom(value)
                            if let lens = lensFor(value: value) { controller.selectLens(lens) }
                        }
                    }
                    // Press-and-hold any chip → show ruler + drag to
                    // adjust zoom continuously.
                    .gesture(
                        LongPressGesture(minimumDuration: 0.25, maximumDistance: 30)
                            .sequenced(before: DragGesture(minimumDistance: 0))
                            .onChanged { gest in
                                switch gest {
                                case .first(true):
                                    slideAnchorZoom = zoomRatio
                                    withAnimation(.easeOut(duration: 0.15)) {
                                        zoomDialActive = true
                                    }
                                case .second(true, let drag?):
                                    // Drag RIGHT → wider (smaller zoom,
                                    // toward 0.5×). Drag LEFT → tighter
                                    // (bigger zoom, toward 2×). ~80pt = 1×.
                                    let delta = -drag.translation.width / 80.0
                                    let target = (slideAnchorZoom + delta)
                                        .clamped(to: 0.5...deviceMaxZoom)
                                    if abs(target - zoomRatio) >= 0.01 {
                                        zoomRatio = target
                                        controller.setVideoZoom(target)
                                    }
                                default:
                                    break
                                }
                            }
                            .onEnded { _ in
                                withAnimation(.easeIn(duration: 0.15)) {
                                    zoomDialActive = false
                                }
                            }
                    )
            }
        }
    }

    /// Format a chip value. The "selected" one gets the "×" suffix.
    private func chipLabel(value: CGFloat, selected: Bool) -> String {
        let suffix = selected ? "×" : ""
        if value < 1 {
            return String(format: "%.1f%@", value, suffix)
        }
        if abs(value - value.rounded()) < 0.05 {
            return String(format: "%.0f%@", value, suffix)
        }
        return String(format: "%.1f%@", value, suffix)
    }

    /// Best-effort mapping from a fixed chip value to a lens so the
    /// hardware switches when the user taps 0.5×, 1×, or 2×.
    private func lensFor(value: CGFloat) -> CameraLens? {
        switch value {
        case 0.5:  return availableLenses.contains(.ultraWide) ? .ultraWide : nil
        case 1.0:  return availableLenses.contains(.wide) ? .wide : nil
        case 2.0:  return availableLenses.contains(.tele) ? .tele : nil
        default:   return nil
        }
    }

    private var bottomRow: some View {
        HStack {
            // Left: circular last-capture thumbnail. Tap to open the
            // swipeable gallery of all captures for this staging/area.
            ZStack(alignment: .leading) {
                Color.clear
                recentCaptureThumb
            }
            .frame(maxWidth: .infinity, alignment: .leading)

            shutterButton

            ZStack(alignment: .trailing) {
                Color.clear
                Button {
                    areaPickerOpen = true
                } label: {
                    Text(selectedArea?.name ?? "Area")
                        .font(.caption.bold())
                        .foregroundStyle(.white)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 10)
                        .background(Color.white.opacity(0.2))
                        .clipShape(Capsule())
                }
                .buttonStyle(.plain)
            }
            .frame(maxWidth: .infinity, alignment: .trailing)
        }
    }

    /// Top-right mic shortcut inside the camera. Tap to toggle a
    /// dictation recording tagged to the currently-selected area.
    @ViewBuilder
    private var topRightMicButton: some View {
        let recordingThisArea: Bool = {
            if case .recording(_, let sid, let aid) = dictationController.phase {
                return sid == staging.id && aid == selectedArea?.id
            }
            return false
        }()
        Button {
            Task { await toggleCameraDictation() }
        } label: {
            HStack(spacing: 4) {
                Image(systemName: recordingThisArea ? "mic.fill" : "mic")
                    .font(.title3.bold())
                if recordingThisArea {
                    Text(cameraElapsedLabel)
                        .font(.caption.monospacedDigit().bold())
                }
            }
            .foregroundStyle(.white)
            .frame(minWidth: 40, minHeight: 40)
            .padding(.horizontal, recordingThisArea ? 12 : 0)
            .background(recordingThisArea ? Color.red.opacity(0.7) : Color.black.opacity(0.55))
            .clipShape(recordingThisArea ? AnyShape(Capsule()) : AnyShape(Circle()))
            .overlay {
                (recordingThisArea ? AnyShape(Capsule()) : AnyShape(Circle()))
                    .stroke(Color.white.opacity(0.9), lineWidth: 1.5)
            }
        }
        .buttonStyle(.plain)
    }

    /// Circular thumbnail of the most recent capture for this staging.
    /// Taps open the gallery. Hidden when there are no captures yet.
    @ViewBuilder
    private var recentCaptureThumb: some View {
        let latest = captureStore.captures(forStaging: staging.id).last
        if let latest {
            Button { galleryOpen = true } label: {
                ZStack {
                    Color.black
                    thumbnailImage(for: latest)
                }
                .frame(width: 44, height: 44)
                .clipShape(Circle())
                .overlay(Circle().stroke(Color.white.opacity(0.9), lineWidth: 1.5))
            }
            .buttonStyle(.plain)
        } else {
            Color.clear.frame(width: 44, height: 44)
        }
    }

    @ViewBuilder
    private func thumbnailImage(for c: ConsultationCapture) -> some View {
        let url = captureStore.fileURL(for: c)
        if c.mediaType == .video {
            ZStack {
                if let frame = VideoThumbnailCache.thumbnail(for: url) {
                    Image(uiImage: frame).resizable().scaledToFill()
                } else {
                    Color.black
                }
                Image(systemName: "play.fill")
                    .foregroundStyle(.white)
                    .font(.caption)
                    .padding(4)
                    .background(Color.black.opacity(0.45), in: Circle())
            }
        } else if let ui = UIImage(contentsOfFile: url.path) {
            Image(uiImage: ui).resizable().scaledToFill()
        } else {
            Color.gray
        }
    }

    private var cameraElapsedLabel: String {
        let total = Int(dictationController.elapsed)
        return String(format: "%02d:%02d", total / 60, total % 60)
    }

    private func toggleCameraDictation() async {
        if dictationController.isRecording() {
            if case .recording(_, let sid, let aid) = dictationController.phase,
               sid == staging.id, aid == selectedArea?.id {
                dictationController.stopAndEnqueue()
            }
            return
        }
        let (mic, _) = await dictationController.requestPermissions()
        guard mic else { return }
        try? dictationController.start(staging: staging, area: selectedArea)
    }

    @ViewBuilder
    private var shutterButton: some View {
        if mediaType == .video {
            Button {
                Task {
                    if isRecording {
                        await stopRecording()
                    } else {
                        await startRecording()
                    }
                }
            } label: {
                Circle()
                    .stroke(Color.white, lineWidth: 4)
                    .frame(width: 76, height: 76)
                    .overlay(
                        Group {
                            if isRecording {
                                RoundedRectangle(cornerRadius: 6)
                                    .fill(Color.red)
                                    .frame(width: 28, height: 28)
                            } else {
                                Circle().fill(Color.red).padding(10)
                            }
                        }
                    )
            }
            .buttonStyle(.plain)
        } else {
            Button {
                Task { await capturePhoto() }
            } label: {
                Circle()
                    .stroke(Color.white, lineWidth: 4)
                    .frame(width: 76, height: 76)
                    .overlay(Circle().fill(Color.white).padding(6))
            }
            .buttonStyle(.plain)
        }
    }

    // MARK: - Actions

    private func cameraMode(for type: CaptureMediaType) -> CameraController.Mode {
        type == .video ? .video : .photo
    }

    private func ensureAuthorised() async {
        if authChecked { return }
        let videoOk = await AVCaptureDevice.requestAccess(for: .video)
        let audioOk = await AVCaptureDevice.requestAccess(for: .audio)
        authorized = videoOk && audioOk
        authChecked = true
    }

    private func snapTo(lens: CameraLens) {
        controller.selectLens(lens)
        zoomRatio = lens.ratio
        // Reset the active lens's internal zoom to 1.0 so the chip's
        // nominal label matches what the camera is actually capturing.
        controller.setVideoZoom(1.0)
    }

    private func capturePhoto() async {
        do {
            let angle = captureRotationAngle(for: deviceOrientation)
            let url = try await controller.capturePhoto(rotationAngle: angle)
            // Keep the camera running — the parent saves the file without
            // dismissing us so the stager can keep shooting.
            onCaptureTaken(.image(url: url, mimeType: "image/jpeg"), mediaType, selectedArea)
        } catch {
            // On error, still don't dismiss — leave the camera up.
        }
    }

    /// Map the current physical device orientation to the video rotation
    /// angle the capture connection should use so the saved JPEG matches
    /// what the user saw through the preview.
    private func captureRotationAngle(for o: UIDeviceOrientation) -> CGFloat {
        switch o {
        case .portrait:            return 90
        case .portraitUpsideDown:  return 270
        case .landscapeLeft:       return 0
        case .landscapeRight:      return 180
        default:                   return 90
        }
    }

    private func startRecording() async {
        do {
            try controller.startRecording()
            isRecording = true
            videoRecordStartedAt = Date()
            videoElapsedSec = 0
            videoTickTimer?.invalidate()
            videoTickTimer = Timer.scheduledTimer(withTimeInterval: 0.5, repeats: true) { [weak tim = videoTickTimer] _ in
                _ = tim  // silence warning; real work below
                Task { @MainActor in
                    if let s = videoRecordStartedAt {
                        videoElapsedSec = Date().timeIntervalSince(s)
                    }
                }
            }
        } catch {
            // Leave camera open; user can try again.
        }
    }

    private func stopRecording() async {
        let url = await controller.stopRecording()
        isRecording = false
        videoTickTimer?.invalidate(); videoTickTimer = nil
        videoRecordStartedAt = nil
        videoElapsedSec = 0
        if let url {
            onCaptureTaken(.video(url: url, mimeType: "video/quicktime"), mediaType, selectedArea)
        }
        // No-result case — stay open.
    }

    /// Red-dot + mm:ss badge shown over the preview while recording.
    @ViewBuilder
    private var recordingBadge: some View {
        if isRecording {
            HStack(spacing: 6) {
                Circle()
                    .fill(Color.red)
                    .frame(width: 8, height: 8)
                Text(formatVideoElapsed(videoElapsedSec))
                    .font(.caption.bold().monospacedDigit())
                    .foregroundStyle(.white)
            }
            .padding(.horizontal, 10)
            .padding(.vertical, 6)
            .background(Color.black.opacity(0.55), in: Capsule())
        }
    }

    private func formatVideoElapsed(_ s: TimeInterval) -> String {
        let total = Int(s)
        return String(format: "%02d:%02d", total / 60, total % 60)
    }
}

// MARK: - Capture gallery (shared by camera + area-tap)

/// Fullscreen swipe-through gallery for a list of captures. Used from
/// the camera's recent-thumbnail button AND when the user taps any photo
/// in the Consultation area section. The thumbnail strip sits directly
/// under the photo rather than at the screen bottom.
struct InCameraGallery: View {
    let captures: [ConsultationCapture]
    let captureStore: CaptureStore
    /// Token for the server delete call. If nil, only the local copy
    /// is removed (useful for never-uploaded items).
    var token: String? = nil
    /// Id of the capture to open on. If nil, opens on the most recent.
    var initialCaptureId: String? = nil
    let onDismiss: () -> Void

    @State private var selectedIndex: Int = 0
    @State private var pendingDelete: ConsultationCapture?

    var body: some View {
        ZStack(alignment: .topLeading) {
            Color.black.ignoresSafeArea()

            if captures.isEmpty {
                VStack {
                    Spacer()
                    Text("No captures yet.")
                        .foregroundStyle(.white)
                    Spacer()
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else {
                // Photo area + strip live together as a centered cluster,
                // pushed by Spacers above and below so the strip visually
                // hugs the bottom edge of the rendered photo.
                VStack(spacing: 0) {
                    Spacer(minLength: 0)
                    TabView(selection: $selectedIndex) {
                        ForEach(Array(captures.enumerated()), id: \.element.id) { idx, c in
                            fullFrame(for: c)
                                .tag(idx)
                        }
                    }
                    .tabViewStyle(.page(indexDisplayMode: .never))
                    .frame(maxWidth: .infinity)
                    .frame(maxHeight: .infinity)

                    // Thumbnail strip — sits directly below the photo,
                    // not pinned to the screen bottom.
                    ScrollViewReader { proxy in
                        ScrollView(.horizontal, showsIndicators: false) {
                            HStack(spacing: 6) {
                                ForEach(Array(captures.enumerated()), id: \.element.id) { idx, c in
                                    Button {
                                        selectedIndex = idx
                                    } label: {
                                        stripThumb(for: c, active: idx == selectedIndex)
                                            .id(idx)
                                    }
                                    .buttonStyle(.plain)
                                }
                            }
                            .padding(.horizontal, 12)
                            .padding(.vertical, 8)
                        }
                        .background(Color.black.opacity(0.45))
                        .onChange(of: selectedIndex) { _, new in
                            withAnimation { proxy.scrollTo(new, anchor: .center) }
                        }
                    }
                    Spacer(minLength: 0)
                }
            }

            HStack {
                Button(action: onDismiss) {
                    Image(systemName: "xmark")
                        .font(.title3.bold())
                        .foregroundStyle(.white)
                        .frame(width: 40, height: 40)
                        .background(Color.black.opacity(0.55))
                        .clipShape(Circle())
                        .overlay(Circle().stroke(Color.white.opacity(0.9), lineWidth: 1.5))
                }
                Spacer()
                if !captures.isEmpty && captures.indices.contains(selectedIndex) {
                    Button(role: .destructive) {
                        pendingDelete = captures[selectedIndex]
                    } label: {
                        Image(systemName: "trash")
                            .font(.title3.bold())
                            .foregroundStyle(.white)
                            .frame(width: 40, height: 40)
                            .background(Color.red.opacity(0.75))
                            .clipShape(Circle())
                            .overlay(Circle().stroke(Color.white.opacity(0.9), lineWidth: 1.5))
                    }
                }
            }
            .padding(.horizontal, 16)
            .padding(.top, 8)
        }
        .onAppear {
            if let initial = initialCaptureId,
               let idx = captures.firstIndex(where: { $0.id == initial }) {
                selectedIndex = idx
            } else {
                // Open on the most recent capture.
                selectedIndex = max(captures.count - 1, 0)
            }
        }
        .alert("Delete this capture?", isPresented: Binding(
            get: { pendingDelete != nil },
            set: { if !$0 { pendingDelete = nil } }
        )) {
            Button("Cancel", role: .cancel) { pendingDelete = nil }
            Button("Delete", role: .destructive) {
                if let c = pendingDelete {
                    // Server delete first (if uploaded); local cleanup
                    // happens regardless so the thumbnail disappears even
                    // when offline.
                    if let remoteId = c.remoteId, let tok = token {
                        Task {
                            try? await APIClient.shared.deleteMedia(
                                mediaId: remoteId, token: tok,
                            )
                        }
                    }
                    captureStore.remove(c)
                    if selectedIndex >= captures.count - 1 {
                        selectedIndex = max(captures.count - 2, 0)
                    }
                }
                pendingDelete = nil
            }
        } message: {
            Text("This removes the file and cancels any pending upload.")
        }
    }

    @ViewBuilder
    private func fullFrame(for c: ConsultationCapture) -> some View {
        let url = captureStore.fileURL(for: c)
        if c.mediaType == .video {
            // Minimal video player sized to match the photo frame.
            GalleryVideoView(url: url)
                .aspectRatio(3.0 / 4.0, contentMode: .fit)
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .background(Color.black)
        } else if let ui = UIImage(contentsOfFile: url.path) {
            Image(uiImage: ui)
                .resizable()
                .scaledToFit()
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .background(Color.black)
        } else {
            Color.black
        }
    }

    @ViewBuilder
    private func stripThumb(for c: ConsultationCapture, active: Bool) -> some View {
        let url = captureStore.fileURL(for: c)
        ZStack {
            Color.black
            if c.mediaType == .video {
                if let frame = VideoThumbnailCache.thumbnail(for: url) {
                    Image(uiImage: frame).resizable().scaledToFill()
                }
                Image(systemName: "play.fill")
                    .foregroundStyle(.white)
                    .font(.caption2)
                    .padding(3)
                    .background(Color.black.opacity(0.45), in: Circle())
            } else if let ui = UIImage(contentsOfFile: url.path) {
                Image(uiImage: ui).resizable().scaledToFill()
            }
        }
        .frame(width: 56, height: 56)
        .clipShape(RoundedRectangle(cornerRadius: 6))
        .overlay {
            RoundedRectangle(cornerRadius: 6)
                .stroke(active ? Color.white : Color.white.opacity(0.3),
                        lineWidth: active ? 2.5 : 1)
        }
    }
}

// MARK: - Video thumbnail cache (first-frame cover for thumbnails)

enum VideoThumbnailCache {
    /// Keyed by file path. NSCache would evict on memory pressure; a
    /// plain dict is fine given the handful of captures in-session.
    private static var cache: [String: UIImage] = [:]
    private static let queue = DispatchQueue(label: "com.astrastaging.portal.videoThumb")

    /// Synchronous thumbnail lookup — cached after first call. Returns
    /// nil if the first frame can't be decoded.
    static func thumbnail(for url: URL) -> UIImage? {
        if let cached = cache[url.path] { return cached }
        let asset = AVURLAsset(url: url)
        let generator = AVAssetImageGenerator(asset: asset)
        generator.appliesPreferredTrackTransform = true
        generator.maximumSize = CGSize(width: 400, height: 400)
        guard let cg = try? generator.copyCGImage(at: .zero, actualTime: nil) else {
            return nil
        }
        let ui = UIImage(cgImage: cg)
        queue.sync { cache[url.path] = ui }
        return ui
    }
}

// MARK: - Minimal video player (used in gallery)

/// Video surface + auto-hiding center play/pause + draggable scrubber.
/// While playing: center button fades after 2s of idle; tap anywhere to
/// bring it back. While paused: always visible.
private struct GalleryVideoView: View {
    let url: URL

    @State private var player: AVPlayer = AVPlayer()
    @State private var isPlaying: Bool = false
    @State private var durationSec: Double = 1
    @State private var currentSec: Double = 0
    @State private var timeObserverToken: Any?
    @State private var hideControlsWorkItem: DispatchWorkItem?
    @State private var controlsVisible: Bool = true
    @State private var isScrubbing: Bool = false

    var body: some View {
        ZStack {
            PlayerLayerView(player: player)
                .contentShape(Rectangle())
                .onTapGesture { flashControls() }

            // Center play/pause — dims on its own after 2s while playing.
            if controlsVisible || !isPlaying {
                Button { togglePlayPause() } label: {
                    Image(systemName: isPlaying ? "pause.circle.fill" : "play.circle.fill")
                        .font(.system(size: 64))
                        .foregroundStyle(.white)
                        .shadow(color: .black.opacity(0.4), radius: 4)
                }
                .buttonStyle(.plain)
                .transition(.opacity)
            }

            // Draggable scrubber pinned to the bottom inside the video.
            VStack {
                Spacer()
                GeometryReader { geo in
                    let W = geo.size.width
                    let fraction = min(max(currentSec / max(durationSec, 0.001), 0), 1)
                    ZStack(alignment: .leading) {
                        Rectangle()
                            .fill(Color.white.opacity(0.25))
                            .frame(height: 3)
                        Rectangle()
                            .fill(Color.white)
                            .frame(width: W * CGFloat(fraction), height: 3)
                        Circle()
                            .fill(Color.white)
                            .frame(width: 12, height: 12)
                            .offset(x: W * CGFloat(fraction) - 6, y: 0)
                    }
                    .frame(height: 12, alignment: .center)
                    .contentShape(Rectangle())
                    .gesture(
                        DragGesture(minimumDistance: 0)
                            .onChanged { val in
                                isScrubbing = true
                                flashControls()
                                let x = min(max(val.location.x, 0), W)
                                let frac = Double(x / W)
                                let target = frac * durationSec
                                currentSec = target
                                let t = CMTime(seconds: target, preferredTimescale: 600)
                                player.seek(to: t, toleranceBefore: .zero, toleranceAfter: .zero)
                            }
                            .onEnded { _ in
                                isScrubbing = false
                                scheduleAutoHide()
                            }
                    )
                }
                .frame(height: 12)
                .padding(.horizontal, 10)
                .padding(.bottom, 8)
            }
        }
        .onAppear {
            player.replaceCurrentItem(with: AVPlayerItem(url: url))
            durationSec = max(CMTimeGetSeconds(player.currentItem?.asset.duration ?? .zero), 0.1)
            addTimeObserver()
            NotificationCenter.default.addObserver(
                forName: .AVPlayerItemDidPlayToEndTime,
                object: player.currentItem,
                queue: .main,
            ) { _ in
                isPlaying = false
                controlsVisible = true
                player.seek(to: .zero)
                currentSec = 0
            }
            player.play()
            isPlaying = true
            scheduleAutoHide()
        }
        .onDisappear {
            player.pause()
            hideControlsWorkItem?.cancel()
            if let token = timeObserverToken {
                player.removeTimeObserver(token)
                timeObserverToken = nil
            }
        }
        .animation(.easeInOut(duration: 0.2), value: controlsVisible)
    }

    private func togglePlayPause() {
        if isPlaying {
            player.pause()
            isPlaying = false
            controlsVisible = true
            hideControlsWorkItem?.cancel()
        } else {
            if currentSec >= durationSec - 0.1 {
                player.seek(to: .zero)
                currentSec = 0
            }
            player.play()
            isPlaying = true
            flashControls()
        }
    }

    private func flashControls() {
        controlsVisible = true
        scheduleAutoHide()
    }

    private func scheduleAutoHide() {
        hideControlsWorkItem?.cancel()
        guard isPlaying else { return }
        let w = DispatchWorkItem {
            if isPlaying && !isScrubbing { controlsVisible = false }
        }
        hideControlsWorkItem = w
        DispatchQueue.main.asyncAfter(deadline: .now() + 2, execute: w)
    }

    private func addTimeObserver() {
        // 30 fps tick so the progress bar motion feels continuous.
        let interval = CMTime(value: 1, timescale: 30)
        let token = player.addPeriodicTimeObserver(forInterval: interval, queue: .main) { time in
            if isScrubbing { return }  // don't overwrite user drag
            currentSec = max(CMTimeGetSeconds(time), 0)
            if let d = player.currentItem?.asset.duration,
               CMTimeGetSeconds(d).isFinite {
                durationSec = max(CMTimeGetSeconds(d), 0.1)
            }
        }
        timeObserverToken = token
    }
}

/// UIKit bridge that hosts an AVPlayerLayer so SwiftUI can frame it.
private struct PlayerLayerView: UIViewRepresentable {
    let player: AVPlayer

    func makeUIView(context: Context) -> PlayerContainer {
        let v = PlayerContainer()
        v.backgroundColor = .black
        v.playerLayer.player = player
        v.playerLayer.videoGravity = .resizeAspect
        return v
    }
    func updateUIView(_ uiView: PlayerContainer, context: Context) {
        if uiView.playerLayer.player !== player {
            uiView.playerLayer.player = player
        }
    }

    final class PlayerContainer: UIView {
        override class var layerClass: AnyClass { AVPlayerLayer.self }
        var playerLayer: AVPlayerLayer { layer as! AVPlayerLayer }
    }
}

// MARK: - Horizontal zoom ruler (press-and-hold overlay)

/// Horizontal sliding ruler that takes the same slot as the chip row
/// while the user press-drags. Ticks slide under a fixed centre pointer;
/// major labels at 0.5×, 1×, 2×, 4×, 10× (capped at device max). The
/// live zoom value is rendered separately above this view.
private struct HorizontalZoomRuler: View {
    let zoomRatio: CGFloat
    let minZoom: CGFloat
    let maxZoom: CGFloat

    /// Pixels between consecutive 0.1× ticks.
    private let pxPerStep: CGFloat = 16
    private let majorStops: [CGFloat] = [0.5, 1.0, 2.0, 4.0, 10.0]

    var body: some View {
        Canvas(rendersAsynchronously: true) { ctx, size in
            let W = size.width
            let H = size.height
            let cx = W / 2
            let midY = H / 2

            // Render ticks within the visible horizontal window, clamped
            // to the device's actual supported zoom range.
            let halfW = W / 2 + pxPerStep
            let zoomHalf = (halfW / pxPerStep) * 0.1
            var z = max(minZoom, (zoomRatio - zoomHalf))
            z = (z * 10).rounded() / 10
            let zMax = min(maxZoom, zoomRatio + zoomHalf)

            while z <= zMax + 0.001 {
                let dx = (z - zoomRatio) / 0.1 * pxPerStep
                let x = cx + dx
                let isMajor = majorStops.contains { abs($0 - z) < 0.05 && $0 <= maxZoom + 0.01 }
                let tickH: CGFloat = isMajor ? 12 : 5
                var path = Path()
                path.move(to: CGPoint(x: x, y: midY - tickH))
                path.addLine(to: CGPoint(x: x, y: midY + tickH))
                ctx.stroke(
                    path,
                    with: .color(.white.opacity(isMajor ? 0.95 : 0.5)),
                    lineWidth: isMajor ? 2 : 1,
                )
                if isMajor {
                    let label = z < 1
                        ? String(format: "%.1f", z)
                        : String(format: "%.0f", z)
                    let txt = Text(label)
                        .font(.system(size: 10, weight: .semibold))
                        .foregroundColor(.white.opacity(0.9))
                    ctx.draw(txt, at: CGPoint(x: x, y: midY + tickH + 8))
                }
                z = ((z + 0.1) * 10).rounded() / 10
            }

            // Fixed centre pointer — small downward triangle.
            var tri = Path()
            tri.move(to: CGPoint(x: cx - 5, y: midY - 20))
            tri.addLine(to: CGPoint(x: cx + 5, y: midY - 20))
            tri.addLine(to: CGPoint(x: cx,     y: midY - 12))
            tri.closeSubpath()
            ctx.fill(tri, with: .color(.white))
        }
    }
}

// MARK: - Legacy arc dial (unused — kept for reference)

private struct ZoomDial: View {
    let zoomRatio: CGFloat
    let minZoom: CGFloat
    let maxZoom: CGFloat

    /// How many degrees of arc each 0.1× tick occupies. Smaller = more
    /// zoom range visible at once across a wider arc.
    private let anglePerStep: CGFloat = 1.9

    /// Which zoom values get a prominent label.
    private let majorStops: [CGFloat] = [0.5, 1.0, 2.0, 4.0, 10.0]

    var body: some View {
        GeometryReader { geo in
            Canvas { ctx, size in
                let W = size.width
                let H = size.height

                // Smaller radius so the arc visibly curves — the full
                // 180° half-circle arc shows above the circle center.
                let radius: CGFloat = max(W * 0.6, 260)
                let cx = W / 2
                // Centre low in the canvas so the top half of the circle
                // lives in the visible area (the arc).
                let cy = H * 0.85
                let center = CGPoint(x: cx, y: cy)

                // 180° total visible arc (90° each side of the indicator).
                let visibleHalfDeg: CGFloat = 90
                let zoomHalf = (visibleHalfDeg / anglePerStep) * 0.1
                var z = max(minZoom, (zoomRatio - zoomHalf))
                // Snap to the nearest 0.1 multiple so ticks don't shimmer.
                z = (z * 10).rounded() / 10
                let zMax = min(maxZoom, zoomRatio + zoomHalf)

                while z <= zMax + 0.001 {
                    let deltaDeg = (z - zoomRatio) * anglePerStep
                    let angleRad = deltaDeg * .pi / 180
                    let isMajor = majorStops.contains(where: { abs($0 - z) < 0.05 })
                    let tickLen: CGFloat = isMajor ? 18 : 9
                    let innerR = radius - tickLen
                    let outerR = radius

                    let p1 = CGPoint(
                        x: center.x + sin(angleRad) * innerR,
                        y: center.y - cos(angleRad) * innerR,
                    )
                    let p2 = CGPoint(
                        x: center.x + sin(angleRad) * outerR,
                        y: center.y - cos(angleRad) * outerR,
                    )

                    var path = Path()
                    path.move(to: p1)
                    path.addLine(to: p2)
                    ctx.stroke(
                        path,
                        with: .color(.white.opacity(isMajor ? 1.0 : 0.55)),
                        lineWidth: isMajor ? 2 : 1,
                    )

                    if isMajor {
                        let labelR = innerR - 22
                        let labelPos = CGPoint(
                            x: center.x + sin(angleRad) * labelR,
                            y: center.y - cos(angleRad) * labelR,
                        )
                        let txt = Text(labelText(for: z))
                            .font(.system(size: 13, weight: .semibold))
                            .foregroundColor(.white)
                        ctx.draw(txt, at: labelPos)
                    }

                    z = ((z + 0.1) * 10).rounded() / 10
                }

                // Current-value indicator: small downward triangle at the
                // top of the arc + "1.4×" in the center.
                let topY = center.y - radius
                let triBase = topY - 10
                let triTip = triBase + 10
                var tri = Path()
                tri.move(to: CGPoint(x: center.x - 7, y: triBase))
                tri.addLine(to: CGPoint(x: center.x + 7, y: triBase))
                tri.addLine(to: CGPoint(x: center.x,     y: triTip))
                tri.closeSubpath()
                ctx.fill(tri, with: .color(.white))

                let valTxt = Text(String(format: "%.1f×", zoomRatio))
                    .font(.system(size: 22, weight: .bold))
                    .foregroundColor(.white)
                ctx.draw(valTxt, at: CGPoint(x: center.x, y: triBase - 22))
            }
        }
        .frame(height: 280)
    }

    private func labelText(for z: CGFloat) -> String {
        if abs(z - z.rounded()) < 0.05 {
            return String(format: "%.0f", z)
        }
        return String(format: "%.1f", z)
    }
}

// MARK: - Preview layer

private struct CameraPreview: UIViewRepresentable {
    let session: AVCaptureSession

    func makeUIView(context: Context) -> PreviewContainer {
        let v = PreviewContainer()
        v.videoPreviewLayer.session = session
        v.videoPreviewLayer.videoGravity = .resizeAspectFill
        return v
    }

    func updateUIView(_ uiView: PreviewContainer, context: Context) {}

    final class PreviewContainer: UIView {
        override class var layerClass: AnyClass { AVCaptureVideoPreviewLayer.self }
        var videoPreviewLayer: AVCaptureVideoPreviewLayer {
            layer as! AVCaptureVideoPreviewLayer
        }
    }
}

// MARK: - In-camera area picker

/// Three-step area picker used inside the camera.
///  - root: list of areas already on this staging + "+ New Area" row
///  - catalog: the curated server list (Living Room, Dining Room, …) + "Other"
///  - custom: free-form name entry, reached via "Other"
private struct InCameraAreaPicker: View {
    enum Step { case root, catalog, custom }

    let areas: [StagingArea]
    let selectedId: String?
    let token: String
    let onCreate: (String) async -> Void
    let onSelect: (StagingArea) -> Void
    let onDismiss: () -> Void

    @State private var step: Step = .root
    @State private var catalog: [AreaCatalogEntry] = []
    @State private var loadingCatalog = false
    @State private var customName = ""
    @State private var submitting = false
    @State private var newAreaEditing = false
    @State private var newAreaText = ""

    var body: some View {
        NavigationStack {
            Group {
                switch step {
                case .root: rootList
                case .catalog: catalogList
                case .custom: customEntry
                }
            }
            .navigationTitle(title)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                if step != .root {
                    ToolbarItem(placement: .topBarLeading) {
                        Button("Back") { step = .root; customName = "" }
                    }
                }
                ToolbarItem(placement: .cancellationAction) {
                    Button("Close") { onDismiss() }
                }
            }
            .presentationDetents([.medium, .large])
        }
    }

    private var title: String {
        switch step {
        case .root: return "Choose area"
        case .catalog: return "Pick a name"
        case .custom: return "Custom name"
        }
    }

    private var rootList: some View {
        List {
            // "+ New Area" removed — areas are sourced from Zoho Creator
            // and this m4 instance is read-only. Users can only pick
            // from the already-synced list.
            if !areas.isEmpty {
                Section("Existing areas") {
                    ForEach(areas) { area in
                        Button {
                            onSelect(area)
                        } label: {
                            HStack {
                                Text(area.name).foregroundStyle(.primary)
                                Spacer()
                                if area.id == selectedId {
                                    Image(systemName: "checkmark")
                                        .foregroundStyle(Color.accentColor)
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    private var catalogList: some View {
        List {
            if loadingCatalog && catalog.isEmpty {
                HStack {
                    ProgressView().controlSize(.small)
                    Text("Loading…").foregroundStyle(.secondary)
                }
            } else {
                Section {
                    ForEach(catalog) { entry in
                        if entry.name.lowercased() == "new area" {
                            newAreaRow(entry: entry)
                        } else {
                            Button {
                                Task {
                                    submitting = true
                                    await onCreate(entry.name)
                                    submitting = false
                                }
                            } label: {
                                Text(entry.name).foregroundStyle(.primary)
                            }
                        }
                    }
                }
            }
        }
    }

    @ViewBuilder
    private func newAreaRow(entry: AreaCatalogEntry) -> some View {
        if newAreaEditing {
            HStack(spacing: 8) {
                TextField("New Area", text: $newAreaText)
                    .textInputAutocapitalization(.words)
                    .autocorrectionDisabled()
                Button("Add") {
                    Task {
                        let typed = newAreaText.trimmingCharacters(in: .whitespacesAndNewlines)
                        // Empty typed text → let the server-side/VM apply
                        // the auto-numbering rule ("New Area" → "New Area 2"
                        // on collision).
                        let name = typed.isEmpty ? "New Area" : typed
                        submitting = true
                        await onCreate(name)
                        submitting = false
                        newAreaEditing = false
                        newAreaText = ""
                    }
                }
                .disabled(submitting)
                .buttonStyle(.borderedProminent)
                .controlSize(.small)
            }
        } else {
            Button {
                newAreaEditing = true
            } label: {
                Label("New Area", systemImage: "plus.circle.fill")
                    .foregroundStyle(Color.accentColor)
            }
        }
    }

    private var customEntry: some View {
        Form {
            Section {
                TextField("Area name", text: $customName)
                    .textInputAutocapitalization(.words)
                    .autocorrectionDisabled()
            }
            Section {
                Button {
                    Task {
                        let name = customName.trimmingCharacters(in: .whitespacesAndNewlines)
                        guard !name.isEmpty else { return }
                        submitting = true
                        await onCreate(name)
                        submitting = false
                    }
                } label: {
                    HStack {
                        Spacer()
                        Text("Add").fontWeight(.semibold)
                        Spacer()
                    }
                }
                .disabled(submitting ||
                          customName.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
            }
        }
    }

    private func loadCatalogIfNeeded() {
        if !catalog.isEmpty || loadingCatalog { return }
        loadingCatalog = true
        Task {
            let resp = try? await APIClient.shared.areaCatalog(token: token)
            catalog = resp?.catalog ?? []
            loadingCatalog = false
        }
    }
}

// MARK: - Misc helpers

private extension CGFloat {
    func clamped(to range: ClosedRange<CGFloat>) -> CGFloat {
        Swift.min(Swift.max(self, range.lowerBound), range.upperBound)
    }
}

// MARK: - Nonisolated AVFoundation controller

nonisolated final class CameraController: NSObject, @unchecked Sendable,
    AVCapturePhotoCaptureDelegate, AVCaptureFileOutputRecordingDelegate {

    enum Mode: Sendable {
        case photo
        case video
    }

    let session = AVCaptureSession()

    private let sessionQueue = DispatchQueue(label: "com.astrastaging.portal.CameraController")
    private let photoOutput = AVCapturePhotoOutput()
    private let movieOutput = AVCaptureMovieFileOutput()
    private var currentInput: AVCaptureDeviceInput?
    private var mode: Mode = .photo
    /// Created per-input. Reads the live "horizon-level capture" rotation
    /// angle so photos come out aligned with how the user was holding
    /// the phone, regardless of whether the app UI is portrait-locked.
    private var rotationCoordinator: AVCaptureDevice.RotationCoordinator?

    private var photoContinuation: CheckedContinuation<URL, Error>?
    private var videoContinuation: CheckedContinuation<URL?, Never>?

    func configure(for mode: Mode) async -> [CameraLens] {
        await withCheckedContinuation { cont in
            sessionQueue.async { [self] in
                self.mode = mode
                session.beginConfiguration()

                for output in session.outputs { session.removeOutput(output) }
                for input in session.inputs { session.removeInput(input) }
                currentInput = nil

                // `.vga640x480` is the best 4:3 preset AVCaptureSession
                // offers for video; `.hd1280x720` would be 16:9 and
                // mismatch the 4:3 preview. `.photo` stays for stills.
                session.sessionPreset = (mode == .video) ? .vga640x480 : .photo

                let discovery = AVCaptureDevice.DiscoverySession(
                    deviceTypes: [
                        .builtInUltraWideCamera,
                        .builtInWideAngleCamera,
                        .builtInTelephotoCamera,
                    ],
                    mediaType: .video,
                    position: .back,
                )
                var lenses: [CameraLens] = []
                for d in discovery.devices {
                    switch d.deviceType {
                    case .builtInUltraWideCamera:  lenses.append(.ultraWide)
                    case .builtInWideAngleCamera:  lenses.append(.wide)
                    case .builtInTelephotoCamera:  lenses.append(.tele)
                    default: break
                    }
                }
                let ordered = lenses.sorted { a, b in
                    let order: [CameraLens: Int] = [.ultraWide: 0, .wide: 1, .tele: 2]
                    return (order[a] ?? 99) < (order[b] ?? 99)
                }

                let startingLens: CameraLens = ordered.contains(.wide)
                    ? .wide
                    : (ordered.first ?? .wide)
                attachInputLocked(for: startingLens)

                if mode == .video {
                    if let mic = AVCaptureDevice.default(for: .audio),
                       let micInput = try? AVCaptureDeviceInput(device: mic),
                       session.canAddInput(micInput) {
                        session.addInput(micInput)
                    }
                    if session.canAddOutput(movieOutput) {
                        session.addOutput(movieOutput)
                    }
                } else {
                    if session.canAddOutput(photoOutput) {
                        session.addOutput(photoOutput)
                        photoOutput.maxPhotoQualityPrioritization = .quality
                    }
                }

                session.commitConfiguration()
                cont.resume(returning: ordered)
            }
        }
    }

    func selectLens(_ lens: CameraLens) {
        sessionQueue.async { [self] in
            session.beginConfiguration()
            attachInputLocked(for: lens)
            session.commitConfiguration()
        }
    }

    /// The current input device's max supported zoom factor. Used by
    /// the SwiftUI ruler so it doesn't draw ticks past what the camera
    /// can actually reach.
    func currentMaxZoom() -> CGFloat {
        guard let device = currentInput?.device else { return 10.0 }
        return device.maxAvailableVideoZoomFactor
    }

    /// Smoothly ramp the *active lens's* internal zoom factor. Used by the
    /// long-press gesture so a user holding the "2×" chip sees the zoom
    /// roll continuously (1.1, 1.2, 1.3, ...) rather than snapping.
    func setVideoZoom(_ factor: CGFloat) {
        sessionQueue.async { [self] in
            guard let device = currentInput?.device else { return }
            let clamped = max(device.minAvailableVideoZoomFactor,
                              min(device.maxAvailableVideoZoomFactor, factor))
            do {
                try device.lockForConfiguration()
                device.videoZoomFactor = clamped
                device.unlockForConfiguration()
            } catch {
                // Ignore — the chip's tap fallback still works.
            }
        }
    }

    private func attachInputLocked(for lens: CameraLens) {
        if let currentInput {
            session.removeInput(currentInput)
            self.currentInput = nil
        }
        let deviceType: AVCaptureDevice.DeviceType = {
            switch lens {
            case .ultraWide: return .builtInUltraWideCamera
            case .wide:      return .builtInWideAngleCamera
            case .tele:      return .builtInTelephotoCamera
            }
        }()
        guard let device = AVCaptureDevice.default(deviceType, for: .video, position: .back)
            ?? AVCaptureDevice.default(for: .video) else { return }
        guard let input = try? AVCaptureDeviceInput(device: device) else { return }
        if session.canAddInput(input) {
            session.addInput(input)
            currentInput = input
            // Pair a rotation coordinator with this input. With no preview
            // layer it falls back to internal device-orientation tracking,
            // which is what we want since our SwiftUI preview is 4:3 and
            // locked to portrait.
            rotationCoordinator = AVCaptureDevice.RotationCoordinator(
                device: device, previewLayer: nil,
            )
        }
    }

    func start() {
        sessionQueue.async { [self] in
            if !session.isRunning { session.startRunning() }
        }
    }

    func stop() {
        sessionQueue.async { [self] in
            if session.isRunning { session.stopRunning() }
        }
    }

    // MARK: - Photo

    func capturePhoto(rotationAngle: CGFloat? = nil) async throws -> URL {
        try await withCheckedThrowingContinuation { cont in
            self.photoContinuation = cont
            sessionQueue.async { [self] in
                if let conn = photoOutput.connection(with: .video) {
                    // Prefer the coordinator's live angle — it's
                    // authoritative. Fall back to the caller's hint
                    // (derived from UIDevice orientation) if it's not
                    // available yet.
                    let angle = rotationCoordinator?.videoRotationAngleForHorizonLevelCapture
                        ?? rotationAngle
                        ?? 90
                    if conn.isVideoRotationAngleSupported(angle) {
                        conn.videoRotationAngle = angle
                    }
                }
                let settings = AVCapturePhotoSettings()
                settings.photoQualityPrioritization = .quality
                photoOutput.capturePhoto(with: settings, delegate: self)
            }
        }
    }

    func photoOutput(_ output: AVCapturePhotoOutput,
                     didFinishProcessingPhoto photo: AVCapturePhoto,
                     error: Error?) {
        if let error {
            photoContinuation?.resume(throwing: error)
            photoContinuation = nil
            return
        }
        guard let data = photo.fileDataRepresentation() else {
            photoContinuation?.resume(
                throwing: NSError(domain: "Camera", code: -1,
                                  userInfo: [NSLocalizedDescriptionKey: "No photo data"])
            )
            photoContinuation = nil
            return
        }
        let url = FileManager.default.temporaryDirectory
            .appendingPathComponent("capture-\(UUID().uuidString).jpg")
        do {
            try data.write(to: url, options: .atomic)
            photoContinuation?.resume(returning: url)
        } catch {
            photoContinuation?.resume(throwing: error)
        }
        photoContinuation = nil
    }

    // MARK: - Video

    func startRecording() throws {
        let url = FileManager.default.temporaryDirectory
            .appendingPathComponent("video-\(UUID().uuidString).mov")
        sessionQueue.async { [self] in
            if movieOutput.isRecording { movieOutput.stopRecording() }
            movieOutput.startRecording(to: url, recordingDelegate: self)
        }
    }

    func stopRecording() async -> URL? {
        await withCheckedContinuation { cont in
            self.videoContinuation = cont
            sessionQueue.async { [self] in
                if movieOutput.isRecording {
                    movieOutput.stopRecording()
                } else {
                    let existing = self.videoContinuation
                    self.videoContinuation = nil
                    existing?.resume(returning: nil)
                }
            }
        }
    }

    func fileOutput(_ output: AVCaptureFileOutput,
                    didFinishRecordingTo outputFileURL: URL,
                    from connections: [AVCaptureConnection],
                    error: Error?) {
        if error != nil {
            videoContinuation?.resume(returning: nil)
        } else {
            videoContinuation?.resume(returning: outputFileURL)
        }
        videoContinuation = nil
    }
}
