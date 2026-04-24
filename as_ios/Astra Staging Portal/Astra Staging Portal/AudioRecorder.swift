//
//  AudioRecorder.swift
//  Astra Staging Portal
//
//  AAC-LC mono 16 kHz 32 kbps .m4a recorder used by the Consultation Dictate
//  feature. 1 hour of audio ≈ 14 MB — Whisper-native sample rate, small enough
//  to upload over LTE in seconds.
//
//  Separately drives an SFSpeechRecognizer instance for on-screen "live
//  preview" text while recording. The preview is cosmetic: the canonical
//  transcript is Whisper's response from the server. SFSpeechRecognizer is
//  capped at ~1 minute per request, so we restart it every ~50 seconds; the
//  visible text is only the most recent window and is not saved.
//

import AVFoundation
import Foundation
import Observation
import Speech

@Observable
final class AudioRecorder: NSObject, AVAudioRecorderDelegate {
    enum State: Equatable {
        case idle
        case recording
        case finished(URL)
        case failed(String)
    }

    private(set) var state: State = .idle
    private(set) var elapsedSec: TimeInterval = 0
    /// Rolling preview text from SFSpeechRecognizer. Not persisted.
    private(set) var livePreview: String = ""
    /// 0...1 RMS level for a simple waveform dot.
    private(set) var level: Float = 0

    private var recorder: AVAudioRecorder?
    private var recordingURL: URL?
    private var startedAt: Date?
    private var tickTimer: Timer?

    // MARK: Speech recognizer (live preview only)
    private let speechRecognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))
    private var speechRequest: SFSpeechAudioBufferRecognitionRequest?
    private var speechTask: SFSpeechRecognitionTask?
    private var speechEngine: AVAudioEngine?
    private var speechRestartTimer: Timer?
    private var committedPreview: String = ""  // text from past windows

    // MARK: - Permissions

    /// Request microphone + speech recognition permission. Returns true only
    /// when the user granted at least the microphone; speech is optional (the
    /// live preview just stays blank without it).
    @MainActor
    func requestPermissions() async -> (mic: Bool, speech: Bool) {
        // Microphone
        let micGranted: Bool = await withCheckedContinuation { cont in
            AVAudioApplication.requestRecordPermission { granted in
                cont.resume(returning: granted)
            }
        }
        // Speech recognition
        let speechStatus: SFSpeechRecognizerAuthorizationStatus = await withCheckedContinuation { cont in
            SFSpeechRecognizer.requestAuthorization { status in
                cont.resume(returning: status)
            }
        }
        return (micGranted, speechStatus == .authorized)
    }

    // MARK: - Recording

    @MainActor
    func start() throws {
        guard case .idle = state else { return }
        livePreview = ""
        committedPreview = ""
        elapsedSec = 0
        level = 0

        let session = AVAudioSession.sharedInstance()
        try session.setCategory(.playAndRecord, mode: .spokenAudio, options: [.defaultToSpeaker, .allowBluetoothHFP])
        try session.setActive(true, options: [])

        let tmpURL = URL(fileURLWithPath: NSTemporaryDirectory())
            .appendingPathComponent("dictation-\(UUID().uuidString).m4a")

        // AAC-LC mono 16 kHz 32 kbps — matches what Whisper expects.
        let settings: [String: Any] = [
            AVFormatIDKey: Int(kAudioFormatMPEG4AAC),
            AVSampleRateKey: 16000,
            AVNumberOfChannelsKey: 1,
            AVEncoderBitRateKey: 32000,
            AVEncoderAudioQualityKey: AVAudioQuality.medium.rawValue,
        ]

        let rec = try AVAudioRecorder(url: tmpURL, settings: settings)
        rec.delegate = self
        rec.isMeteringEnabled = true
        guard rec.prepareToRecord(), rec.record() else {
            throw NSError(domain: "AudioRecorder", code: 1,
                          userInfo: [NSLocalizedDescriptionKey: "Could not start recording"])
        }

        recorder = rec
        recordingURL = tmpURL
        startedAt = Date()
        state = .recording

        tickTimer?.invalidate()
        tickTimer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { [weak self] _ in
            guard let self, let started = self.startedAt, self.recorder?.isRecording == true else { return }
            Task { @MainActor in
                self.elapsedSec = Date().timeIntervalSince(started)
                self.recorder?.updateMeters()
                let db = self.recorder?.averagePower(forChannel: 0) ?? -160
                // map -60dB..0dB to 0..1
                let norm = max(0, min(1, (db + 60) / 60))
                self.level = norm
            }
        }

        startSpeechRecognition()
    }

    @MainActor
    func stop() {
        guard case .recording = state else { return }
        tickTimer?.invalidate(); tickTimer = nil
        stopSpeechRecognition(finalize: true)

        recorder?.stop()
        let url = recordingURL
        recorder = nil
        recordingURL = nil
        startedAt = nil
        try? AVAudioSession.sharedInstance().setActive(false, options: [.notifyOthersOnDeactivation])

        if let url, FileManager.default.fileExists(atPath: url.path) {
            state = .finished(url)
        } else {
            state = .failed("Recording finished but the file is missing.")
        }
    }

    @MainActor
    func cancel() {
        tickTimer?.invalidate(); tickTimer = nil
        stopSpeechRecognition(finalize: false)
        recorder?.stop()
        if let url = recordingURL {
            try? FileManager.default.removeItem(at: url)
        }
        recorder = nil
        recordingURL = nil
        startedAt = nil
        state = .idle
        try? AVAudioSession.sharedInstance().setActive(false, options: [.notifyOthersOnDeactivation])
    }

    // MARK: - Speech recognition (live preview)

    private func startSpeechRecognition() {
        guard SFSpeechRecognizer.authorizationStatus() == .authorized,
              let recognizer = speechRecognizer, recognizer.isAvailable else {
            return
        }

        let engine = AVAudioEngine()
        let request = SFSpeechAudioBufferRecognitionRequest()
        request.shouldReportPartialResults = true
        if #available(iOS 13, *) { request.requiresOnDeviceRecognition = false }

        let inputNode = engine.inputNode
        let format = inputNode.outputFormat(forBus: 0)
        inputNode.installTap(onBus: 0, bufferSize: 1024, format: format) { buffer, _ in
            request.append(buffer)
        }

        do {
            engine.prepare()
            try engine.start()
        } catch {
            return
        }

        let task = recognizer.recognitionTask(with: request) { [weak self] result, error in
            guard let self else { return }
            if let result {
                let windowText = result.bestTranscription.formattedString
                Task { @MainActor in
                    let combined = (self.committedPreview + " " + windowText).trimmingCharacters(in: .whitespaces)
                    self.livePreview = combined
                }
            }
            if error != nil {
                // Ignore — the window will restart on timer or stop() will clean up.
            }
        }

        speechEngine = engine
        speechRequest = request
        speechTask = task

        // SFSpeechRecognizer buffer sessions cap around 1 minute. Rotate at 50s
        // to avoid silent drops, committing what we have into `committedPreview`.
        speechRestartTimer?.invalidate()
        speechRestartTimer = Timer.scheduledTimer(withTimeInterval: 50, repeats: false) { _ in
            Task { @MainActor [weak self] in self?.rotateSpeechWindow() }
        }
    }

    @MainActor
    private func rotateSpeechWindow() {
        guard case .recording = state else { return }
        // Commit current window text, tear down, restart.
        committedPreview = livePreview
        stopSpeechRecognition(finalize: false)
        startSpeechRecognition()
    }

    private func stopSpeechRecognition(finalize: Bool) {
        speechRestartTimer?.invalidate()
        speechRestartTimer = nil
        if finalize { speechRequest?.endAudio() }
        speechTask?.cancel()
        speechTask = nil
        speechRequest = nil
        speechEngine?.inputNode.removeTap(onBus: 0)
        speechEngine?.stop()
        speechEngine = nil
    }

    // MARK: - AVAudioRecorderDelegate

    func audioRecorderDidFinishRecording(_ recorder: AVAudioRecorder, successfully flag: Bool) {
        if !flag {
            Task { @MainActor in self.state = .failed("Recording ended abnormally.") }
        }
    }
}
