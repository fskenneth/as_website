//
//  ConsultationView.swift
//  Astra Staging Portal
//
//  Stager consultation flow: pick the staging being consulted, read the
//  customer/property briefing, capture photos and videos grouped by area.
//  Works offline:
//    - Cached stagings + areas load instantly on launch and are refreshed
//      in the background when the network comes back.
//    - Captured media is queued on disk and drained by UploadQueue when
//      connectivity + settings permit (see AppSettings.wifiOnlyMediaUpload).
//

import SwiftUI
import UIKit

struct ConsultationView: View {
    @Environment(AuthStore.self) private var auth

    @State private var stagings: [Staging] = []
    @State private var selectedID: String?
    @State private var isLoading = false
    @State private var error: String?
    @State private var searchText: String = ""

    // Capture state
    @State private var captureStore = CaptureStore.shared
    @State private var uploadQueue = UploadQueue.shared
    @State private var network = NetworkMonitor.shared
    @State private var settings = AppSettings.shared

    // Per-staging area cache (in-memory; disk-backed via ConsultationCache)
    @State private var areasByStaging: [String: [StagingArea]] = [:]
    @State private var loadingAreasFor: String?
    @State private var areasError: String?

    // Per-staging dictation list (server-side records) + the audio player.
    @State private var dictationsByStaging: [String: [DictationRecord]] = [:]
    @State private var audioPlayer = DictationAudioPlayer.shared
    // Inline expansion state for a dictation row: which id + which
    // panel ("transcript" | "summary") is currently showing.
    @State private var expandedDictation: (id: String, panel: String)?
    // Delete confirmations.
    @State private var dictationPendingDelete: DictationRecord?
    @State private var areaPendingDelete: (stagingId: String, area: StagingArea)?

    // Capture sheet presentation
    @State private var captureTarget: CaptureTarget?

    // Post-capture confirmation: a user has finished a photo/video; if
    // they back out without hitting Save, the file gets discarded.
    @State private var pendingCapture: PendingCapture?

    // Fullscreen viewer triggered by tapping a thumbnail.
    @State private var viewerCapture: ConsultationCapture?

    // Add-area picker (used when Zoho hasn't synced any yet).
    @State private var addAreaForStagingID: String?

    // Staging picker sheet presentation
    @State private var pickerOpen: Bool = false

    // Dictation: the controller is app-wide so a recording survives tab
    // switches. The review sheet is keyed by the `DictationRecord` the
    // controller publishes once an upload finishes.
    @State private var dictation = DictationController.shared
    @State private var reviewTarget: DictationRecord?
    @State private var micAlert: String?

    // Live quote + catalog for the item picker (Remove Existing / Add New).
    @State private var quoteCatalog: [QuoteCatalogItem] = []
    @State private var quoteByStaging: [String: StagingQuote] = [:]
    @State private var itemPickerFor: ItemPickerTarget?

    private struct ItemPickerTarget: Identifiable {
        let id = UUID()
        let staging: Staging
        let area: StagingArea
        let action: String // "add" or "remove"
    }

    private struct CaptureTarget: Identifiable, Equatable {
        let id = UUID()
        let stagingId: String
        let area: StagingArea?
        let mediaType: CaptureMediaType
    }

    private struct PendingCapture: Identifiable {
        let id = UUID()
        let target: CaptureTarget
        let fileURL: URL
        let mimeType: String
    }

    private var selected: Staging? {
        guard let id = selectedID else { return nil }
        return stagings.first { $0.id == id }
    }

    private var filteredStagings: [Staging] {
        let q = searchText.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        guard !q.isEmpty else { return stagings }
        return stagings.filter { s in
            (s.name ?? "").lowercased().contains(q)
                || (s.address ?? "").lowercased().contains(q)
                || s.customer.fullName.lowercased().contains(q)
        }
    }

    var body: some View {
        NavigationStack {
            Group {
                if isLoading && stagings.isEmpty {
                    ProgressView("Loading stagings...")
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else if let error, stagings.isEmpty {
                    errorState(error)
                } else {
                    content
                }
            }
            .navigationTitle("Consultation")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    dictateToolbarButton
                }
            }
            .task { await load() }
            .task { await loadQuoteCatalogIfNeeded() }
            .onAppear {
                // Wire the token provider once — DictationController asks
                // for it lazily during uploads.
                dictation.authTokenProvider = { [auth] in auth.token }
                dictation.drainIfPossible()
                // Kick a dictation fetch for the already-selected staging
                // (onChange only fires on mutation, not on first appear).
                if let id = selectedID {
                    Task { await loadDictations(for: id) }
                    Task { await loadQuote(for: id) }
                }
            }
            .onChange(of: network.isOnline) { _, isOnline in
                if isOnline {
                    Task { await load() }
                    uploadQueue.drainIfPossible(token: auth.token)
                    dictation.drainIfPossible()
                    if let id = selectedID {
                        Task { await loadDictations(for: id) }
                    }
                }
            }
            .onChange(of: selectedID) { _, newID in
                guard let newID else { return }
                Task { await loadAreas(for: newID) }
                Task { await loadDictations(for: newID) }
                Task { await loadQuote(for: newID) }
            }
            .onChange(of: dictation.pendingReview) { _, new in
                if let new {
                    reviewTarget = new
                    dictation.pendingReview = nil
                    // Optimistic append — instant row.
                    var list = dictationsByStaging[new.staging_id] ?? []
                    if !list.contains(where: { $0.id == new.id }) {
                        list.insert(new, at: 0)
                        dictationsByStaging[new.staging_id] = list
                    }
                    // Safety net: refetch so the row reflects whatever the
                    // server decided (email history, status corrections).
                    Task { await loadDictations(for: new.staging_id) }
                }
            }
            // Extra safety net: any transition of the controller's phase
            // to idle (upload just finished, even if pendingReview didn't
            // fire for this view) triggers a refresh for the current staging.
            .onChange(of: dictation.phase) { _, new in
                if case .idle = new, let id = selectedID {
                    Task { await loadDictations(for: id) }
                }
            }
            .alert("Microphone", isPresented: Binding(
                get: { micAlert != nil },
                set: { if !$0 { micAlert = nil } }
            )) {
                Button("OK", role: .cancel) { micAlert = nil }
            } message: {
                Text(micAlert ?? "")
            }
            .alert("Delete dictation?", isPresented: Binding(
                get: { dictationPendingDelete != nil },
                set: { if !$0 { dictationPendingDelete = nil } }
            )) {
                Button("Cancel", role: .cancel) { dictationPendingDelete = nil }
                Button("Delete", role: .destructive) {
                    if let rec = dictationPendingDelete {
                        Task { await deleteDictation(rec) }
                    }
                    dictationPendingDelete = nil
                }
            } message: {
                Text("This removes the audio, transcript, and summary from the server. This can't be undone.")
            }
            .alert("Delete area?", isPresented: Binding(
                get: { areaPendingDelete != nil },
                set: { if !$0 { areaPendingDelete = nil } }
            )) {
                Button("Cancel", role: .cancel) { areaPendingDelete = nil }
                Button("Delete", role: .destructive) {
                    if let pair = areaPendingDelete {
                        Task { await deleteArea(pair.area, stagingId: pair.stagingId) }
                    }
                    areaPendingDelete = nil
                }
            } message: {
                Text("Photos and dictations in this area will lose their area tag. The area itself is soft-deleted.")
            }
        }
        .fullScreenCover(item: $captureTarget) { target in
            CustomCameraView(
                initialMediaType: target.mediaType,
                staging: stagings.first(where: { $0.id == target.stagingId }) ?? selected!,
                areas: areasByStaging[target.stagingId] ?? [],
                initialAreaId: target.area?.id,
                token: auth.token ?? "",
                onCreateArea: { name in
                    await createAreaInline(stagingId: target.stagingId, name: name)
                },
                onCaptureTaken: { media, finalType, finalArea in
                    // Enqueue without dismissing — camera stays open so
                    // the stager can keep shooting.
                    let liveTarget = CaptureTarget(
                        stagingId: target.stagingId,
                        area: finalArea,
                        mediaType: finalType,
                    )
                    Task { await autoSaveCaptured(media, target: liveTarget) }
                },
                onResult: { _, _, _ in
                    captureTarget = nil
                },
            )
            // Intentionally no .ignoresSafeArea() — CustomCameraView
            // handles its own black backdrop internally while keeping
            // the close button / shutter inside the safe area.
        }
        .sheet(item: $pendingCapture) { pending in
            CapturePreviewSheet(
                areaName: pending.target.area?.name,
                mediaType: pending.target.mediaType,
                fileURL: pending.fileURL,
                onSave: {
                    Task { await savePending(pending) }
                },
                onDiscard: {
                    discardPending(pending)
                }
            )
        }
        .fullScreenCover(item: $viewerCapture) { c in
            // Use the same gallery the camera uses, scoped to the area
            // the tapped thumbnail belongs to (nil area → unassigned).
            InCameraGallery(
                captures: captureStore.captures(forStaging: c.stagingId, areaId: c.areaId),
                captureStore: captureStore,
                token: auth.token,
                initialCaptureId: c.id,
                onDismiss: { viewerCapture = nil },
            )
        }
        .sheet(item: Binding(
            get: { addAreaForStagingID.map { IdentifiedString(value: $0) } },
            set: { addAreaForStagingID = $0?.value }
        )) { wrapper in
            AddAreaSheet(
                stagingId: wrapper.value,
                onCreated: { area in
                    var current = areasByStaging[wrapper.value] ?? []
                    current.append(area)
                    areasByStaging[wrapper.value] = current
                    addAreaForStagingID = nil
                    // Refresh from server so the new area persists across relaunch.
                    Task { await loadAreas(for: wrapper.value, forceNetwork: true) }
                },
                onDismiss: { addAreaForStagingID = nil }
            )
        }
        .sheet(item: $reviewTarget) { record in
            DictateSheet(
                dictation: record,
                customerEmailOnFile: stagings.first(where: { $0.id == record.staging_id })?.customer.email,
                token: auth.token ?? "",
            )
        }
        .sheet(item: $itemPickerFor) { target in
            let areaQuote = quoteByStaging[target.staging.id]?.areas
                .first(where: { $0.area_id == target.area.id })
            ItemPickerSheet(
                title: target.action == "add" ? "Add New Items" : "Remove Existing Items",
                action: target.action,
                catalog: quoteCatalog,
                areaQuote: areaQuote,
                areaName: target.area.name,
                onTap: { itemName, delta in
                    Task {
                        await upsertLineItem(
                            stagingId: target.staging.id,
                            areaId: target.area.id,
                            action: target.action,
                            itemName: itemName,
                            delta: delta,
                        )
                    }
                },
                onDone: { itemPickerFor = nil },
            )
        }
    }

    // MARK: - Dictate toolbar button

    /// Mic icon in the Consultation title bar. Tap to toggle recording
    /// for the currently selected staging. While recording, shows the
    /// elapsed timer on the left and turns red.
    @ViewBuilder
    private var dictateToolbarButton: some View {
        HStack(spacing: 8) {
            if case .recording = dictation.phase {
                Text(formatElapsed(dictation.elapsed))
                    .font(.caption.monospacedDigit().bold())
                    .foregroundStyle(.red)
            }
            if case .uploading = dictation.phase {
                ProgressView().controlSize(.small)
            }
            Button {
                Task { await toggleDictation() }
            } label: {
                Image(systemName: dictation.isRecording() ? "mic.fill" : "mic")
                    .font(.body)
                    .foregroundStyle(dictation.isRecording() ? .red : .primary)
                    .frame(width: 32, height: 32)
                    .background(
                        Circle().fill(dictation.isRecording()
                                      ? Color.red.opacity(0.15)
                                      : Color.clear)
                    )
            }
            .accessibilityLabel(dictation.isRecording() ? "Stop dictation" : "Start dictation")
        }
    }

    private func toggleDictation() async {
        if dictation.isRecording() {
            dictation.stopAndEnqueue()
            return
        }
        guard let staging = selected else {
            micAlert = "Select a staging first."
            return
        }
        let (mic, _) = await dictation.requestPermissions()
        guard mic else {
            micAlert = "Microphone access is denied. Enable it in Settings to dictate."
            return
        }
        do {
            try dictation.start(staging: staging, area: nil)
        } catch {
            micAlert = "Could not start recording: \(error.localizedDescription)"
        }
    }

    private func formatElapsed(_ s: TimeInterval) -> String {
        let total = Int(s)
        return String(format: "%02d:%02d", total / 60, total % 60)
    }

    private struct IdentifiedString: Identifiable {
        let value: String
        var id: String { value }
    }

    // MARK: - Main content

    private var content: some View {
        List {
            if !network.isOnline {
                offlineBanner
            }

            Section("Staging") {
                stagingPickerRow

                if let s = selected {
                    briefingRows(for: s)
                }
            }

            if let s = selected {
                // Photos section: grouped by Area
                photosSection(for: s)

                Section("Notes") {
                    if let notes = s.general_notes, !notes.isEmpty {
                        Text(notes).font(.callout)
                    } else {
                        Text("No notes on this staging yet.")
                            .font(.footnote)
                            .foregroundStyle(.secondary)
                    }
                }
            }
        }
        .listStyle(.insetGrouped)
        .refreshable { await load() }
        .sheet(isPresented: $pickerOpen) { stagingPickerSheet }
    }

    private var offlineBanner: some View {
        Section {
            HStack(spacing: 10) {
                Image(systemName: "wifi.slash")
                    .foregroundStyle(.orange)
                VStack(alignment: .leading, spacing: 2) {
                    Text("Offline — showing cached data").font(.footnote).bold()
                    Text("New captures stay on-device until you reconnect.")
                        .font(.caption2).foregroundStyle(.secondary)
                }
            }
        }
    }

    // MARK: - Staging picker row + sheet

    /// Address row that doubles as the staging picker trigger.
    /// Tapping it presents `stagingPickerSheet`.
    private var stagingPickerRow: some View {
        Button {
            searchText = ""
            pickerOpen = true
        } label: {
            HStack(alignment: .firstTextBaseline, spacing: 12) {
                Image(systemName: "mappin.and.ellipse")
                    .foregroundStyle(.secondary)
                    .frame(width: 22)
                Text("Address")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .frame(width: 110, alignment: .leading)
                VStack(alignment: .leading, spacing: 2) {
                    Text(selected?.address ?? selected?.name ?? "Select a staging")
                        .font(.subheadline)
                        .foregroundStyle(selected == nil ? Color.secondary : Color.primary)
                        .lineLimit(2)
                        .multilineTextAlignment(.leading)
                    if let s = selected {
                        Text(stagingSubtitle(s))
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                Image(systemName: "chevron.up.chevron.down")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .accessibilityIdentifier("consultation-staging-picker")
    }

    private var stagingPickerSheet: some View {
        NavigationStack {
            List {
                if filteredStagings.isEmpty {
                    Text("No matches")
                        .foregroundStyle(.secondary)
                } else {
                    ForEach(filteredStagings) { s in
                        Button {
                            selectedID = s.id
                            pickerOpen = false
                        } label: {
                            HStack(alignment: .top) {
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(s.name ?? s.address ?? s.id)
                                        .foregroundStyle(.primary)
                                        .multilineTextAlignment(.leading)
                                    Text(stagingSubtitle(s))
                                        .font(.caption)
                                        .foregroundStyle(.secondary)
                                }
                                Spacer()
                                if s.id == selectedID {
                                    Image(systemName: "checkmark")
                                        .foregroundStyle(Color.accentColor)
                                }
                            }
                        }
                        .buttonStyle(.plain)
                    }
                }
            }
            .listStyle(.plain)
            .searchable(text: $searchText, placement: .navigationBarDrawer(displayMode: .always), prompt: "Filter by address or customer")
            .navigationTitle("\(stagings.count) available")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Done") { pickerOpen = false }
                }
            }
        }
        .presentationDetents([.large])
    }

    private func stagingSubtitle(_ s: Staging) -> String {
        var parts: [String] = []
        if let d = s.staging_date, !d.isEmpty { parts.append(prettyDate(d)) } else { parts.append("No date") }
        if let st = s.status, !st.isEmpty { parts.append(st) }
        return parts.joined(separator: " · ")
    }

    // MARK: - Briefing

    @ViewBuilder
    private func briefingRows(for s: Staging) -> some View {
        // Address is now rendered by stagingPickerRow at the top of the section.
        briefRow("Occupancy", value: s.occupancy ?? "—", symbol: "house")
        briefRow("Property", value: s.property_type ?? "—", symbol: "building.2")
        if let type = s.staging_type, !type.isEmpty {
            briefRow("Staging type", value: type, symbol: "sparkles")
        }
        if let status = s.status, !status.isEmpty {
            briefRow("Status", value: status, symbol: "flag")
        }
        briefRow("Staging date", value: s.staging_date.flatMap { $0.isEmpty ? nil : prettyDate($0) } ?? "Not scheduled", symbol: "calendar")

        briefRow("Customer", value: s.customer.fullName, symbol: "person")
        if let phone = s.customer.phone, !phone.isEmpty {
            Button {
                if let url = URL(string: "tel:\(phone.replacingOccurrences(of: " ", with: ""))") {
                    UIApplication.shared.open(url)
                }
            } label: {
                briefRow("Phone", value: phone, symbol: "phone")
            }
            .buttonStyle(.plain)
        }
        if let email = s.customer.email, !email.isEmpty {
            Button {
                if let url = URL(string: "mailto:\(email)") {
                    UIApplication.shared.open(url)
                }
            } label: {
                briefRow("Email", value: email, symbol: "envelope")
            }
            .buttonStyle(.plain)
        }

        briefRow("Quote", value: money(s.fees.total), symbol: "dollarsign.circle")
        if s.fees.paid > 0 {
            briefRow("Paid", value: money(s.fees.paid), symbol: "checkmark.seal")
        }
        if s.fees.owing > 0 {
            briefRow("Owing", value: money(s.fees.owing), symbol: "exclamationmark.circle")
        }

        if let mls = s.mls, !mls.isEmpty {
            briefRow("MLS", value: mls, symbol: "number")
        }
        if let folder = s.pictures_folder, let url = URL(string: folder) {
            Link(destination: url) {
                briefRow("Pictures folder", value: "Open", symbol: "folder")
            }
        }
    }

    private func briefRow(_ label: String, value: String, symbol: String) -> some View {
        HStack(alignment: .firstTextBaseline, spacing: 12) {
            Image(systemName: symbol)
                .foregroundStyle(.secondary)
                .frame(width: 22)
            Text(label)
                .font(.subheadline)
                .foregroundStyle(.secondary)
                .frame(width: 110, alignment: .leading)
            Text(value)
                .font(.subheadline)
                .foregroundStyle(.primary)
                .multilineTextAlignment(.leading)
                .frame(maxWidth: .infinity, alignment: .leading)
        }
    }

    // MARK: - Photos (area-grouped)

    @ViewBuilder
    private func photosSection(for s: Staging) -> some View {
        let areas = areasByStaging[s.id] ?? []

        Section {
            if loadingAreasFor == s.id && areas.isEmpty {
                HStack {
                    ProgressView().controlSize(.small)
                    Text("Loading areas…").font(.footnote).foregroundStyle(.secondary)
                }
            } else if areas.isEmpty {
                VStack(alignment: .leading, spacing: 10) {
                    Text("No areas for this staging yet.")
                        .font(.footnote).foregroundStyle(.secondary)
                    if let err = areasError {
                        Text(err).font(.caption2).foregroundStyle(.tertiary)
                    }
                    // Area list comes from Zoho. Add-Area removed from
                    // the app to keep this m4 instance read-only for
                    // Zoho-sourced data. Refresh is still useful.
                    Button("Refresh") {
                        Task { await loadAreas(for: s.id, forceNetwork: true) }
                    }
                    .buttonStyle(.bordered)
                    .controlSize(.small)
                    .disabled(!network.isOnline)
                }
                .padding(.vertical, 4)
            } else {
                ForEach(areas) { area in
                    areaCaptureRow(for: s, area: area)
                }
                // "Add another area" removed — Zoho Creator is the
                // source of truth for Area_Report.
            }

            // Standalone list of global (title-bar mic) recordings —
            // not tied to any area. Only shows when there's at least one.
            let globalRecordings = (dictationsByStaging[s.id] ?? []).filter { $0.area_id == nil }
            if !globalRecordings.isEmpty {
                VStack(alignment: .leading, spacing: 6) {
                    Text("RECORDINGS")
                        .font(.caption2.bold())
                        .foregroundStyle(.secondary)
                    ForEach(globalRecordings) { rec in
                        dictationRow(rec)
                    }
                }
                .padding(.top, 6)
            }
        } header: {
            HStack {
                Text("Photos & Video by Area")
                Spacer()
                if !network.canUploadMedia(wifiOnly: settings.wifiOnlyMediaUpload) {
                    Label(
                        settings.wifiOnlyMediaUpload ? "Queued · waiting Wi-Fi" : "Queued · offline",
                        systemImage: "icloud.slash"
                    )
                    .font(.caption2)
                    .foregroundStyle(.orange)
                    .labelStyle(.titleAndIcon)
                }
            }
        } footer: {
            Text("Photos are downscaled and videos re-encoded to 720p before upload to keep data use low.")
                .font(.caption2).foregroundStyle(.tertiary)
        }
    }

    @ViewBuilder
    private func areaCaptureRow(for s: Staging, area: StagingArea?) -> some View {
        let captures = captureStore.captures(forStaging: s.id, areaId: area?.id)
        let dictations = (dictationsByStaging[s.id] ?? [])
            .filter { $0.area_id == area?.id }
        let recordingThis = isRecordingArea(area?.id, stagingId: s.id)
        let areaQuote: QuoteArea? = {
            guard let aid = area?.id else { return nil }
            return quoteByStaging[s.id]?.areas.first(where: { $0.area_id == aid })
        }()

        VStack(alignment: .leading, spacing: 10) {
            HStack(alignment: .center, spacing: 10) {
                VStack(alignment: .leading, spacing: 2) {
                    Text(area?.name ?? "Unassigned")
                        .font(.subheadline).bold()
                    if let floor = area?.floor, !floor.isEmpty {
                        Text(floor).font(.caption2).foregroundStyle(.secondary)
                    }
                }
                Spacer()
                if let aq = areaQuote {
                    let capped = aq.items_total > 0 && aq.items_total >= aq.cap
                    Text("$\(Int(aq.effective))")
                        .font(.caption.bold())
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(capped ? Color.orange.opacity(0.25) : Color.blue.opacity(0.2))
                        .foregroundStyle(capped ? Color.orange : Color.blue)
                        .clipShape(RoundedRectangle(cornerRadius: 8))
                }
                // Icon-only controls on the area header row.
                inlineIconButton(symbol: "camera", tint: .primary) {
                    captureTarget = CaptureTarget(
                        stagingId: s.id,
                        area: area,
                        mediaType: .photo,
                    )
                }
                inlineIconButton(
                    symbol: recordingThis ? "mic.fill" : "mic",
                    tint: recordingThis ? .red : .primary,
                    accessory: recordingThis ? elapsedLabel : nil,
                ) {
                    Task { await toggleAreaDictation(staging: s, area: area) }
                }
            }

            if !captures.isEmpty {
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        ForEach(captures) { c in
                            captureThumb(c)
                        }
                    }
                    .padding(.vertical, 2)
                }
            }

            if !dictations.isEmpty {
                VStack(spacing: 6) {
                    ForEach(dictations) { rec in
                        dictationRow(rec)
                    }
                }
            }

            // Remove Existing / Add New Items buttons — only for real areas.
            if let realArea = area {
                HStack(spacing: 8) {
                    itemsActionButton(
                        label: "Remove Existing",
                        count: areaQuote?.remove_items.reduce(0) { $0 + $1.quantity } ?? 0,
                    ) {
                        itemPickerFor = ItemPickerTarget(staging: s, area: realArea, action: "remove")
                    }
                    itemsActionButton(
                        label: "Add New Items",
                        count: areaQuote?.add_items.reduce(0) { $0 + $1.quantity } ?? 0,
                    ) {
                        itemPickerFor = ItemPickerTarget(staging: s, area: realArea, action: "add")
                    }
                }

                if let aq = areaQuote, !aq.remove_items.isEmpty {
                    lineItemList(
                        title: "REMOVE",
                        items: aq.remove_items,
                        showPrice: false,
                        onDelete: { lineId in
                            Task { await deleteLineItem(stagingId: s.id, areaId: realArea.id, lineId: lineId) }
                        },
                    )
                }
                if let aq = areaQuote, !aq.add_items.isEmpty {
                    lineItemList(
                        title: "ADD",
                        items: aq.add_items,
                        showPrice: true,
                        onDelete: { lineId in
                            Task { await deleteLineItem(stagingId: s.id, areaId: realArea.id, lineId: lineId) }
                        },
                    )
                }
            }
        }
        .padding(.vertical, 4)
        // Area delete removed: Zoho Creator is the source of truth for
        // Areas and this m4 instance is read-only to avoid overwrites.
    }

    /// Compact entry-point button for the two item pickers (Remove / Add).
    private func itemsActionButton(
        label: String,
        count: Int,
        action: @escaping () -> Void,
    ) -> some View {
        Button(action: action) {
            HStack(spacing: 6) {
                Text(label).font(.subheadline.weight(.semibold))
                Spacer()
                if count > 0 {
                    Text("\(count)")
                        .font(.caption.bold())
                        .foregroundStyle(.white)
                        .padding(.horizontal, 7)
                        .padding(.vertical, 2)
                        .background(Color.blue)
                        .clipShape(Capsule())
                }
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 10)
            .frame(maxWidth: .infinity)
            .background(Color(.secondarySystemGroupedBackground))
            .clipShape(RoundedRectangle(cornerRadius: 8))
        }
        .buttonStyle(.plain)
        .foregroundStyle(.primary)
    }

    private func lineItemList(
        title: String,
        items: [QuoteLineItem],
        showPrice: Bool,
        onDelete: @escaping (String) -> Void,
    ) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title).font(.caption2.bold()).foregroundStyle(.secondary)
            ForEach(items) { li in
                HStack {
                    Text("\(li.item_name) × \(li.quantity)")
                        .font(.caption.weight(.semibold))
                    Spacer()
                    if showPrice {
                        Text("$\(Int((li.unit_price ?? 0) * Double(li.quantity)))")
                            .font(.caption).foregroundStyle(.secondary)
                    }
                    Button {
                        onDelete(li.id)
                    } label: {
                        Image(systemName: "trash")
                            .font(.caption)
                            .foregroundStyle(.red)
                    }
                    .buttonStyle(.plain)
                }
                .padding(.horizontal, 10)
                .padding(.vertical, 6)
                .background(Color(.secondarySystemGroupedBackground).opacity(0.5))
                .clipShape(RoundedRectangle(cornerRadius: 8))
            }
        }
    }

    private var elapsedLabel: String {
        let total = Int(dictation.elapsed)
        return String(format: "%02d:%02d", total / 60, total % 60)
    }

    /// Icon-only button on the area header row. If `accessory` is given
    /// (e.g. the elapsed timer while recording), it's shown inline to
    /// the right of the icon so the width still stays compact.
    private func inlineIconButton(
        symbol: String,
        tint: Color,
        accessory: String? = nil,
        action: @escaping () -> Void,
    ) -> some View {
        Button(action: action) {
            HStack(spacing: 4) {
                Image(systemName: symbol).font(.body)
                if let accessory {
                    Text(accessory).font(.caption2.monospacedDigit())
                }
            }
            .foregroundStyle(tint)
            .frame(minWidth: 32, minHeight: 32)
            .padding(.horizontal, 8)
            .padding(.vertical, 6)
            .background(Color(.secondarySystemGroupedBackground))
            .clipShape(RoundedRectangle(cornerRadius: 8))
        }
        .buttonStyle(.plain)
    }

    /// Toggle a dictation recording tied to a specific area (or nil for
    /// the Unassigned row). Mirrors the title-bar mic logic but passes
    /// the area along so the server tags it correctly.
    private func toggleAreaDictation(staging: Staging, area: StagingArea?) async {
        if dictation.isRecording() {
            // If THIS area is the one being recorded, stop it. Otherwise
            // warn — only one recording at a time.
            if isRecordingArea(area?.id, stagingId: staging.id) {
                dictation.stopAndEnqueue()
            } else {
                micAlert = "Another dictation is already recording. Stop it first."
            }
            return
        }
        let (mic, _) = await dictation.requestPermissions()
        guard mic else {
            micAlert = "Microphone access is denied. Enable it in Settings to dictate."
            return
        }
        do {
            try dictation.start(staging: staging, area: area)
        } catch {
            micAlert = "Could not start recording: \(error.localizedDescription)"
        }
    }

    /// A single dictation entry: play/stop + duration + progress bar
    /// while playing + delete (with confirm) + expand transcript/summary.
    @ViewBuilder
    private func dictationRow(_ rec: DictationRecord) -> some View {
        let playing = audioPlayer.isPlaying(rec.id)
        let loading = audioPlayer.loadingId == rec.id
        let expandedPanel = expandedDictation?.id == rec.id
            ? expandedDictation?.panel : nil

        VStack(alignment: .leading, spacing: 4) {
            HStack(spacing: 10) {
                Button {
                    guard let token = auth.token else { return }
                    Task { await audioPlayer.toggle(dictationId: rec.id, token: token) }
                } label: {
                    Image(systemName: playing ? "stop.circle.fill" : "play.circle.fill")
                        .font(.title3)
                        .foregroundStyle(.blue)
                }
                .buttonStyle(.plain)
                .disabled(loading)

                VStack(alignment: .leading, spacing: 1) {
                    Text(formatAudioSize(rec.audio_size))
                        .font(.caption.bold())
                        .foregroundStyle(.primary)
                    Text(formatDuration(rec.duration_sec))
                        .font(.caption2.monospacedDigit())
                        .foregroundStyle(.secondary)
                }
                Spacer()

                // Transcript + summary expand icons — tap to toggle
                // inline expansion below the row.
                Button {
                    expandedDictation = (expandedPanel == "transcript")
                        ? nil
                        : (id: rec.id, panel: "transcript")
                } label: {
                    Image(systemName: "text.alignleft")
                        .foregroundStyle(expandedPanel == "transcript" ? .blue : .secondary)
                }
                .buttonStyle(.plain)

                Button {
                    expandedDictation = (expandedPanel == "summary")
                        ? nil
                        : (id: rec.id, panel: "summary")
                } label: {
                    Image(systemName: "sparkles")
                        .foregroundStyle(expandedPanel == "summary" ? .blue : .secondary)
                }
                .buttonStyle(.plain)

                // Delete sits at the end of the row with a confirm dialog.
                Button {
                    dictationPendingDelete = rec
                } label: {
                    Image(systemName: "trash")
                        .foregroundStyle(.red)
                }
                .buttonStyle(.plain)
            }
            if playing {
                ProgressView(value: audioPlayer.progress)
                    .progressViewStyle(.linear)
                    .tint(.blue)
            }

            if let panel = expandedPanel {
                Divider().padding(.vertical, 2)
                if panel == "transcript" {
                    Text(rec.transcript.isEmpty ? "Transcript not available yet." : rec.transcript)
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                        .frame(maxWidth: .infinity, alignment: .leading)
                } else if panel == "summary" {
                    if let s = rec.summary {
                        VStack(alignment: .leading, spacing: 6) {
                            if !s.key_points.isEmpty {
                                Text("Key points").font(.caption.bold())
                                ForEach(s.key_points, id: \.self) { p in
                                    HStack(alignment: .top, spacing: 4) {
                                        Text("•").foregroundStyle(.secondary)
                                        Text(p).font(.footnote)
                                    }
                                }
                            }
                            Button {
                                reviewTarget = rec
                            } label: {
                                Label("Open full review & send email", systemImage: "arrow.up.right")
                                    .font(.caption)
                            }
                        }
                    } else {
                        Text("Summary not available yet.")
                            .font(.footnote)
                            .foregroundStyle(.secondary)
                    }
                }
            }
        }
        .padding(.vertical, 6)
        .padding(.horizontal, 8)
        .background(Color(.tertiarySystemGroupedBackground))
        .clipShape(RoundedRectangle(cornerRadius: 8))
    }

    private func formatDuration(_ seconds: Double?) -> String {
        guard let s = seconds, s > 0 else { return "—" }
        let total = Int(s)
        return String(format: "%d:%02d", total / 60, total % 60)
    }

    private func formatAudioSize(_ bytes: Int?) -> String {
        guard let b = bytes, b > 0 else { return "—" }
        let fmt = ByteCountFormatter()
        fmt.allowedUnits = [.useKB, .useMB]
        fmt.countStyle = .file
        return fmt.string(fromByteCount: Int64(b))
    }

    private func captureThumb(_ c: ConsultationCapture) -> some View {
        let url = captureStore.fileURL(for: c)
        // Landscape photos render wider than tall so the user can tell
        // at a glance how the phone was oriented when captured.
        let (w, h): (CGFloat, CGFloat) = thumbnailSize(for: c, at: url)
        return Button {
            viewerCapture = c
        } label: {
            thumbnail(for: c, at: url)
                .frame(width: w, height: h)
                .clipShape(RoundedRectangle(cornerRadius: 8))
        }
        .buttonStyle(.plain)
    }

    private func thumbnailSize(for c: ConsultationCapture, at url: URL) -> (CGFloat, CGFloat) {
        let base: CGFloat = 72
        guard c.mediaType != .video,
              let ui = UIImage(contentsOfFile: url.path)
        else {
            return (base, base)
        }
        let sz = ui.size
        guard sz.width > 0, sz.height > 0 else { return (base, base) }
        if sz.width > sz.height * 1.05 {
            // Landscape — same height, wider.
            return (base * (sz.width / sz.height), base)
        } else if sz.height > sz.width * 1.05 {
            return (base, base * (sz.height / sz.width))
        }
        return (base, base)
    }

    @ViewBuilder
    private func thumbnail(for c: ConsultationCapture, at url: URL) -> some View {
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
            Color(.secondarySystemGroupedBackground)
        }
    }

    @ViewBuilder
    private func statusBadge(for c: ConsultationCapture) -> some View {
        switch c.status {
        case .uploading:
            ProgressView().controlSize(.mini).tint(.white)
                .padding(3)
                .background(Color.black.opacity(0.55))
                .clipShape(Circle())
        case .pending:
            Image(systemName: "clock.fill")
                .font(.caption2)
                .foregroundStyle(.white)
                .padding(3)
                .background(Color.orange)
                .clipShape(Circle())
        case .failed:
            Image(systemName: "exclamationmark.triangle.fill")
                .font(.caption2)
                .foregroundStyle(.white)
                .padding(3)
                .background(Color.red)
                .clipShape(Circle())
        case .uploaded:
            Image(systemName: "checkmark.circle.fill")
                .font(.caption2)
                .foregroundStyle(.white)
                .padding(3)
                .background(Color.green)
                .clipShape(Circle())
        }
    }

    // MARK: - Capture handling

    /// Camera returned a file. Rather than enqueuing immediately, we show a
    /// confirmation sheet — the user has to tap Save. Backing out deletes the
    /// file (the user dismissed without tapping).
    private func handleCaptured(_ media: CapturedMedia, target: CaptureTarget) async {
        switch media {
        case .image(let url, let mime):
            pendingCapture = PendingCapture(target: target, fileURL: url, mimeType: mime)
        case .video(let srcURL, let mime):
            let compressed = await MediaProcessor.compressVideo(at: srcURL)
            let finalMime = compressed == srcURL ? mime : "video/mp4"
            pendingCapture = PendingCapture(target: target, fileURL: compressed, mimeType: finalMime)
        }
    }

    /// Auto-save flow used by the camera's stay-open path: no confirmation
    /// sheet, capture is enqueued immediately and the upload queue drains
    /// in the background.
    private func autoSaveCaptured(_ media: CapturedMedia, target: CaptureTarget) async {
        let fileURL: URL
        let mimeType: String
        let mediaType: CaptureMediaType
        switch media {
        case .image(let url, let mime):
            fileURL = url
            mimeType = mime
            mediaType = .photo
        case .video(let srcURL, let mime):
            let compressed = await MediaProcessor.compressVideo(at: srcURL)
            fileURL = compressed
            mimeType = compressed == srcURL ? mime : "video/mp4"
            mediaType = .video
        }
        do {
            _ = try captureStore.enqueue(
                stagingId: target.stagingId,
                areaId: target.area?.id,
                areaName: target.area?.name,
                mediaType: mediaType,
                mimeType: mimeType,
                sourceFileURL: fileURL,
            )
            uploadQueue.drainIfPossible(token: auth.token)
        } catch {
            self.error = "Couldn't save capture: \(error.localizedDescription)"
        }
    }

    private func savePending(_ pending: PendingCapture) async {
        let target = pending.target
        do {
            let mediaType: CaptureMediaType = target.mediaType == .video ? .video : .photo
            _ = try captureStore.enqueue(
                stagingId: target.stagingId,
                areaId: target.area?.id,
                areaName: target.area?.name,
                mediaType: mediaType,
                mimeType: pending.mimeType,
                sourceFileURL: pending.fileURL
            )
            pendingCapture = nil
            uploadQueue.drainIfPossible(token: auth.token)
        } catch {
            self.error = "Couldn't save capture: \(error.localizedDescription)"
            pendingCapture = nil
        }
    }

    private func discardPending(_ pending: PendingCapture) {
        try? FileManager.default.removeItem(at: pending.fileURL)
        pendingCapture = nil
    }

    // MARK: - States

    private func errorState(_ message: String) -> some View {
        VStack(spacing: 12) {
            Text("Couldn't load").font(.headline)
            Text(message).font(.footnote).foregroundStyle(.secondary).multilineTextAlignment(.center)
            Button("Retry") { Task { await load() } }
        }
        .padding()
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }

    // MARK: - Helpers

    private func prettyDate(_ iso: String) -> String {
        let fmt = DateFormatter()
        fmt.dateFormat = "yyyy-MM-dd"
        fmt.timeZone = TimeZone(identifier: "America/Toronto")
        guard let d = fmt.date(from: iso) else { return iso }
        let out = DateFormatter()
        out.dateFormat = "EEE, MMM d, yyyy"
        return out.string(from: d)
    }

    private func money(_ v: Double) -> String {
        let f = NumberFormatter()
        f.numberStyle = .currency
        f.currencyCode = "CAD"
        f.maximumFractionDigits = 0
        return f.string(from: NSNumber(value: v)) ?? "$\(Int(v))"
    }

    // MARK: - Load

    private func load() async {
        // Hydrate from cache first so the UI is never blank on launch.
        if stagings.isEmpty, let cached = ConsultationCache.loadStagings() {
            self.stagings = cached.stagings
            if selectedID == nil { selectedID = cached.stagings.first?.id }
        }

        guard let token = auth.token else { return }
        guard network.isOnline else {
            // Offline: rely on whatever the cache provided.
            if stagings.isEmpty {
                self.error = "No cached consultations available offline."
            }
            return
        }

        isLoading = true
        error = nil
        defer { isLoading = false }
        do {
            let resp = try await APIClient.shared.consultationStagings(token: token)
            self.stagings = resp.stagings
            ConsultationCache.saveStagings(resp)
            if let id = selectedID, resp.stagings.contains(where: { $0.id == id }) {
                // keep selection
            } else {
                selectedID = resp.stagings.first?.id
            }
        } catch {
            // Keep whatever we loaded from cache — just surface the error.
            self.error = error.localizedDescription
        }
    }

    /// Create an area inline (invoked from the in-camera picker). Writes
    /// through the cache + in-memory map so the picker reflects it
    /// immediately without a full refresh. Handles the "New Area" →
    /// "New Area 1" / "New Area 2" auto-numbering rule when the user
    /// creates duplicates without typing a custom name.
    private func createAreaInline(stagingId: String, name: String) async -> StagingArea? {
        guard let token = auth.token else { return nil }
        let trimmed = name.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return nil }

        var existing = areasByStaging[stagingId] ?? []
        let finalName = Self.resolveNewAreaName(existing: existing, requested: trimmed)

        // If the user asked for "New Area" and there's already one without
        // a number, rename the first to "New Area 1" so the two coexist
        // cleanly.
        if trimmed.caseInsensitiveCompare("New Area") == .orderedSame,
           let unnumberedIndex = existing.firstIndex(where: { $0.name.caseInsensitiveCompare("New Area") == .orderedSame }),
           !existing.contains(where: { $0.name.range(of: #"(?i)^New Area \d+$"#, options: .regularExpression) != nil })
        {
            let target = existing[unnumberedIndex]
            if let renamed = try? await APIClient.shared.renameArea(
                stagingId: stagingId, areaId: target.id, newName: "New Area 1", token: token,
            ) {
                existing[unnumberedIndex] = renamed.area
            }
        }

        do {
            let resp = try await APIClient.shared.createArea(
                stagingId: stagingId, name: finalName, floor: nil, token: token,
            )
            var current = existing
            current.append(resp.area)
            areasByStaging[stagingId] = current
            ConsultationCache.saveAreas(
                StagingAreasResponse(
                    staging_id: stagingId,
                    areas: current,
                    total: current.count,
                )
            )
            return resp.area
        } catch {
            return nil
        }
    }

    private static func resolveNewAreaName(existing: [StagingArea], requested: String) -> String {
        guard requested.caseInsensitiveCompare("New Area") == .orderedSame else {
            return requested
        }
        let numberRegex = try? NSRegularExpression(pattern: #"(?i)^New Area (\d+)$"#)
        let numbers: [Int] = existing.compactMap { area in
            guard let regex = numberRegex else { return nil }
            let range = NSRange(area.name.startIndex..., in: area.name)
            guard let m = regex.firstMatch(in: area.name, range: range),
                  let r = Range(m.range(at: 1), in: area.name) else { return nil }
            return Int(area.name[r])
        }
        let hasUnnumbered = existing.contains { $0.name.caseInsensitiveCompare("New Area") == .orderedSame }
        if !hasUnnumbered && numbers.isEmpty { return "New Area" }
        if numbers.isEmpty { return "New Area 2" }
        return "New Area \((numbers.max() ?? 0) + 1)"
    }

    private func loadAreas(for stagingId: String, forceNetwork: Bool = false) async {
        if !forceNetwork, let cached = ConsultationCache.loadAreas(stagingId: stagingId) {
            areasByStaging[stagingId] = cached.areas
        }

        guard let token = auth.token else { return }
        guard network.isOnline else { return }

        loadingAreasFor = stagingId
        defer { if loadingAreasFor == stagingId { loadingAreasFor = nil } }
        areasError = nil
        do {
            let resp = try await APIClient.shared.stagingAreas(stagingId: stagingId, token: token)
            areasByStaging[stagingId] = resp.areas
            ConsultationCache.saveAreas(resp)
        } catch {
            areasError = error.localizedDescription
        }
    }

    /// Fetch server-side dictations for a staging. Stored in memory only —
    /// the pending (not-yet-uploaded) queue lives in DictationStore.
    private func loadDictations(for stagingId: String) async {
        guard let token = auth.token, network.isOnline else { return }
        do {
            let resp = try await APIClient.shared.listDictations(stagingId: stagingId, token: token)
            dictationsByStaging[stagingId] = resp.dictations
        } catch {
            // Keep whatever we had — not fatal.
        }
    }

    private func deleteDictation(_ record: DictationRecord) async {
        guard let token = auth.token else { return }
        do {
            try await APIClient.shared.deleteDictation(dictationId: record.id, token: token)
            // Optimistic removal.
            if var list = dictationsByStaging[record.staging_id] {
                list.removeAll { $0.id == record.id }
                dictationsByStaging[record.staging_id] = list
            }
            if audioPlayer.isPlaying(record.id) { audioPlayer.stop() }
        } catch {
            // Fallback: reload from server to resync.
            await loadDictations(for: record.staging_id)
        }
    }

    private func deleteArea(_ area: StagingArea, stagingId: String) async {
        guard let token = auth.token else { return }
        do {
            try await APIClient.shared.deleteArea(stagingId: stagingId, areaId: area.id, token: token)
            if var list = areasByStaging[stagingId] {
                list.removeAll { $0.id == area.id }
                areasByStaging[stagingId] = list
            }
        } catch {
            await loadAreas(for: stagingId, forceNetwork: true)
        }
    }

    /// True when the active recording is tagged with this exact area id
    /// (nil = Unassigned / the global toolbar mic).
    private func isRecordingArea(_ areaId: String?, stagingId: String) -> Bool {
        if case .recording(_, let sid, let aid) = dictation.phase {
            return sid == stagingId && aid == areaId
        }
        return false
    }

    // MARK: - Quote / line items

    private func loadQuoteCatalogIfNeeded() async {
        guard quoteCatalog.isEmpty, let token = auth.token, network.isOnline else { return }
        if let resp = try? await APIClient.shared.quoteCatalog(token: token) {
            quoteCatalog = resp.items
        }
    }

    private func loadQuote(for stagingId: String) async {
        guard let token = auth.token, network.isOnline else { return }
        if let q = try? await APIClient.shared.stagingQuote(stagingId: stagingId, token: token) {
            quoteByStaging[stagingId] = q
        }
    }

    private func upsertLineItem(
        stagingId: String, areaId: String, action: String, itemName: String, delta: Int,
    ) async {
        guard let token = auth.token else { return }
        if let q = try? await APIClient.shared.upsertLineItem(
            stagingId: stagingId, areaId: areaId,
            action: action, itemName: itemName, delta: delta, token: token,
        ) {
            quoteByStaging[stagingId] = q
        }
    }

    private func deleteLineItem(
        stagingId: String, areaId: String, lineId: String,
    ) async {
        guard let token = auth.token else { return }
        if let q = try? await APIClient.shared.deleteLineItem(
            stagingId: stagingId, areaId: areaId, lineId: lineId, token: token,
        ) {
            quoteByStaging[stagingId] = q
        }
    }
}
