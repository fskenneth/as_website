//
//  UploadQueue.swift
//  Astra Staging Portal
//
//  Drains pending captures from CaptureStore to the backend when the
//  network + settings allow. Runs serially (one upload at a time) so we
//  don't starve the user's data plan or trip HTTP/2 head-of-line blocking
//  on a weak link. Kicked from:
//    - app launch (ContentView.onAppear)
//    - network changes (NetworkMonitor observer)
//    - settings toggles (AppSettings didChange)
//    - successful capture (immediately after enqueue)
//

import Foundation
import Observation

@Observable
@MainActor
final class UploadQueue {
    static let shared = UploadQueue()

    var isDraining = false
    var lastMessage: String?

    private let store = CaptureStore.shared
    private let settings = AppSettings.shared
    private let network = NetworkMonitor.shared

    func drainIfPossible(token: String?) {
        guard let token else { return }
        guard !isDraining else { return }
        guard network.canUploadMedia(wifiOnly: settings.wifiOnlyMediaUpload) else { return }
        guard !store.pendingCaptures().isEmpty else { return }

        Task { await self.drain(token: token) }
    }

    private func drain(token: String) async {
        isDraining = true
        defer { isDraining = false }

        while true {
            // Re-check every loop — the user might toggle wifi-only mid-drain
            // or drop off Wi-Fi, and we want to bail gracefully.
            if !network.canUploadMedia(wifiOnly: settings.wifiOnlyMediaUpload) {
                lastMessage = "Waiting for \(settings.wifiOnlyMediaUpload ? "Wi-Fi" : "connection")"
                return
            }

            guard let next = store.pendingCaptures().first else {
                lastMessage = nil
                return
            }

            await uploadOne(next, token: token)
        }
    }

    private func uploadOne(_ capture: ConsultationCapture, token: String) async {
        var working = capture
        working.status = .uploading
        working.attemptCount += 1
        working.lastError = nil
        store.update(working)

        do {
            let resp = try await APIClient.shared.uploadMedia(
                stagingId: working.stagingId,
                areaId: working.areaId,
                areaName: working.areaName,
                mediaType: working.mediaType.rawValue,
                clientId: working.id,
                fileURL: store.fileURL(for: working),
                mimeType: working.mimeType,
                token: token
            )
            // Mark as uploaded but keep the local file + record so the
            // thumbnail stays visible in the area section. User can
            // delete explicitly via the gallery's trash button.
            working.status = .uploaded
            working.remoteId = resp.media.id
            store.update(working)
            lastMessage = "Uploaded"
        } catch {
            working.status = .failed
            working.lastError = error.localizedDescription
            store.update(working)
            lastMessage = "Upload failed — will retry"
            // Back off: pause the drain so we don't hammer the server when
            // it's down. The next network/settings change will restart us.
            try? await Task.sleep(nanoseconds: 4_000_000_000)
        }
    }
}
