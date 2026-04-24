//
//  DictationController.swift
//  Astra Staging Portal
//
//  App-wide singleton that owns the voice-dictation lifecycle:
//
//    idle ──tap mic──▶ recording ──tap mic──▶ (enqueue + drain)
//
//  The controller holds a single AudioRecorder so recording survives tab
//  switches (user can tap mic on Consultation and keep moving). When the
//  user taps stop, the file is moved into DictationStore and an upload
//  loop starts — if offline, the record sits in the queue until the
//  network comes back. On successful upload, the resulting
//  `DictationRecord` is published via `pendingReview` so the Consultation
//  view can present the review sheet.
//

import Foundation
import Observation

@Observable
@MainActor
final class DictationController {
    static let shared = DictationController()

    enum Phase: Equatable {
        case idle
        case recording(startedAt: Date, stagingId: String, areaId: String?)
        case uploading(clientId: String, stagingId: String)
    }

    private(set) var phase: Phase = .idle
    private(set) var elapsed: TimeInterval = 0
    /// Set when an upload completes — the Consultation view observes this
    /// and presents the review sheet, then clears it.
    var pendingReview: DictationRecord?
    var lastError: String?

    // Context captured when recording starts (used when building the store
    // entry after stop — staging object is captured, not re-read).
    private var currentStaging: Staging?
    private var currentArea: StagingArea?

    // Token + network are supplied by the owning view each frame because
    // the controller doesn't have direct access to either without coupling.
    var authTokenProvider: () -> String? = { nil }

    private let recorder = AudioRecorder()
    private let store = DictationStore.shared
    private let network = NetworkMonitor.shared

    private var tickTimer: Timer?
    private var draining = false

    // MARK: - Recording

    func isRecording(for stagingId: String? = nil) -> Bool {
        switch phase {
        case .recording(_, let sid, _):
            return stagingId == nil || sid == stagingId
        default:
            return false
        }
    }

    /// Ensure we have mic permission, then begin recording. Returns false
    /// if the mic is denied (caller should surface a prompt to open Settings).
    func requestPermissions() async -> (mic: Bool, speech: Bool) {
        await recorder.requestPermissions()
    }

    /// Start a recording for the given staging/area. Call only after
    /// `requestPermissions()` has confirmed mic access.
    func start(staging: Staging, area: StagingArea?) throws {
        guard case .idle = phase else { return }
        try recorder.start()
        currentStaging = staging
        currentArea = area
        phase = .recording(startedAt: Date(), stagingId: staging.id, areaId: area?.id)
        elapsed = 0

        tickTimer?.invalidate()
        tickTimer = Timer.scheduledTimer(withTimeInterval: 0.5, repeats: true) { [weak self] _ in
            Task { @MainActor [weak self] in
                guard let self else { return }
                if case .recording(let startedAt, _, _) = self.phase {
                    self.elapsed = Date().timeIntervalSince(startedAt)
                }
            }
        }
    }

    /// Stop recording, move the audio into the DictationStore, and try to
    /// drain the queue immediately (upload if online).
    func stopAndEnqueue() {
        guard case .recording = phase else { return }
        tickTimer?.invalidate(); tickTimer = nil

        recorder.stop()
        let duration = elapsed
        guard
            case .finished(let fileURL) = recorder.state,
            let staging = currentStaging
        else {
            phase = .idle
            lastError = "Recording ended without a file."
            return
        }

        do {
            let pending = try store.enqueue(
                stagingId: staging.id,
                stagingDisplayName: staging.address ?? staging.name,
                areaId: currentArea?.id,
                areaName: currentArea?.name,
                durationSec: duration,
                sourceFileURL: fileURL,
            )
            phase = .idle
            elapsed = 0
            currentStaging = nil
            currentArea = nil
            drainIfPossible(preferredId: pending.id)
        } catch {
            lastError = "Could not save recording: \(error.localizedDescription)"
            phase = .idle
        }
    }

    /// Cancel a recording without saving. Used when the app backgrounds or
    /// the user explicitly discards.
    func cancel() {
        tickTimer?.invalidate(); tickTimer = nil
        recorder.cancel()
        currentStaging = nil
        currentArea = nil
        elapsed = 0
        phase = .idle
    }

    // MARK: - Upload queue

    /// Kick the drain loop if we're online and not already draining.
    /// `preferredId` lets the caller prioritise a just-enqueued record so
    /// the review sheet pops for the dictation the user just finished.
    func drainIfPossible(preferredId: String? = nil) {
        guard !draining else { return }
        guard network.isOnline else { return }
        guard let token = authTokenProvider() else { return }
        guard store.nextPending() != nil else { return }
        Task { await self.drain(token: token, preferredId: preferredId) }
    }

    private func drain(token: String, preferredId: String?) async {
        draining = true
        defer { draining = false }

        // On the first pass, try to upload `preferredId` first if present,
        // so the review sheet lines up with the user's latest recording.
        if let preferredId,
           let first = store.pending.first(where: { $0.id == preferredId })
        {
            await uploadOne(first, token: token, isPreferred: true)
        }

        while network.isOnline, let next = store.nextPending() {
            await uploadOne(next, token: token, isPreferred: false)
        }
    }

    private func uploadOne(_ record: PendingDictation, token: String, isPreferred: Bool) async {
        var working = record
        working.status = .uploading
        working.attemptCount += 1
        working.lastError = nil
        store.update(working)
        phase = .uploading(clientId: working.id, stagingId: working.stagingId)

        do {
            let resp = try await APIClient.shared.uploadDictation(
                stagingId: working.stagingId,
                areaId: working.areaId,
                areaName: working.areaName,
                clientId: working.id,
                durationSec: working.durationSec,
                fileURL: store.fileURL(for: working),
                token: token,
            )
            store.remove(working)
            phase = .idle
            // Only auto-present the review sheet if this was the preferred
            // upload (the one the user just finished). Queued uploads from
            // an offline session shouldn't hijack the UI.
            if isPreferred {
                pendingReview = resp.dictation
            }
        } catch {
            working.status = .failed
            working.lastError = error.localizedDescription
            store.update(working)
            phase = .idle
            lastError = "Upload failed — will retry when online."
            // Back off briefly so we don't hammer a flapping server.
            try? await Task.sleep(nanoseconds: 4_000_000_000)
        }
    }
}
