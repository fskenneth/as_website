//
//  DictationAudioPlayer.swift
//  Astra Staging Portal
//
//  Shared audio player for dictation playback from the Consultation tab.
//  One dictation plays at a time. Audio is fetched with Bearer auth
//  (downloaded to a cache file keyed by id), then played via
//  AVAudioPlayer. Progress (0…1) is exposed so rows can draw a bar.
//

import AVFoundation
import Foundation
import Observation

@Observable
@MainActor
final class DictationAudioPlayer: NSObject {
    static let shared = DictationAudioPlayer()

    private(set) var currentlyPlayingId: String?
    private(set) var progress: Double = 0        // 0…1
    private(set) var currentTime: TimeInterval = 0
    private(set) var duration: TimeInterval = 0
    private(set) var loadingId: String?

    private var player: AVAudioPlayer?
    private var tickTimer: Timer?
    private let delegateHolder = DelegateHolder()

    override init() {
        super.init()
        delegateHolder.onFinish = { [weak self] in
            Task { @MainActor in self?.stop() }
        }
    }

    func isPlaying(_ id: String) -> Bool { currentlyPlayingId == id }

    /// Start or stop playback for a dictation. If the same id is already
    /// playing, stops. If a different id is playing, stops it first.
    func toggle(dictationId: String, token: String) async {
        if currentlyPlayingId == dictationId {
            stop()
            return
        }
        stop()
        loadingId = dictationId
        defer { loadingId = nil }

        let url: URL
        do {
            let data = try await APIClient.shared.downloadDictationAudio(
                dictationId: dictationId, token: token,
            )
            let tmp = URL(fileURLWithPath: NSTemporaryDirectory())
                .appendingPathComponent("dictation-play-\(dictationId).m4a")
            try data.write(to: tmp, options: .atomic)
            url = tmp
        } catch {
            return
        }

        do {
            try AVAudioSession.sharedInstance().setCategory(.playback, mode: .spokenAudio, options: [])
            try AVAudioSession.sharedInstance().setActive(true, options: [])
            let p = try AVAudioPlayer(contentsOf: url)
            p.delegate = delegateHolder
            guard p.play() else { return }
            player = p
            currentlyPlayingId = dictationId
            duration = p.duration
            currentTime = 0
            progress = 0

            tickTimer?.invalidate()
            tickTimer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { [weak self] _ in
                Task { @MainActor [weak self] in
                    guard let self, let p = self.player, p.isPlaying else { return }
                    self.currentTime = p.currentTime
                    self.progress = p.duration > 0 ? p.currentTime / p.duration : 0
                }
            }
        } catch {
            stop()
        }
    }

    func stop() {
        tickTimer?.invalidate(); tickTimer = nil
        player?.stop()
        player = nil
        currentlyPlayingId = nil
        currentTime = 0
        duration = 0
        progress = 0
        try? AVAudioSession.sharedInstance().setActive(false, options: [.notifyOthersOnDeactivation])
    }

    // AVAudioPlayerDelegate can't be directly on the actor-isolated class,
    // so we route through a nonisolated NSObject holder.
    private final class DelegateHolder: NSObject, AVAudioPlayerDelegate {
        var onFinish: (() -> Void)?
        func audioPlayerDidFinishPlaying(_ player: AVAudioPlayer, successfully flag: Bool) {
            onFinish?()
        }
    }
}
