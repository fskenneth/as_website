//
//  CaptureStore.swift
//  Astra Staging Portal
//
//  On-disk queue of photos/videos captured on the Consultation tab.
//  Built on plain Codable + the Application Support directory so we don't
//  need SwiftData plumbing — the store reliably survives relaunch and is
//  easy to audit in the sandbox.
//
//  Each capture keeps its media file next to the index. Files stay on disk
//  until the server confirms the upload, at which point we drop both the
//  record and the bytes.
//

import Foundation
import Observation

enum CaptureMediaType: String, Codable, CaseIterable {
    case photo
    case panorama
    case video

    var displayLabel: String {
        switch self {
        case .photo: return "Photo"
        case .panorama: return "Panorama"
        case .video: return "Video"
        }
    }

    var symbol: String {
        switch self {
        case .photo: return "photo"
        case .panorama: return "pano"
        case .video: return "video"
        }
    }
}

enum CaptureStatus: String, Codable {
    case pending          // captured, waiting for a good connection
    case uploading        // POST in-flight
    case uploaded         // server acknowledged
    case failed           // last attempt errored — will retry
}

struct ConsultationCapture: Codable, Identifiable, Hashable {
    /// UUID used both as local primary key and as the `client_id` sent
    /// to the backend so retries are idempotent.
    let id: String
    let stagingId: String
    var areaId: String?
    var areaName: String?
    let mediaType: CaptureMediaType
    var mimeType: String
    var fileName: String
    var byteSize: Int
    var createdAt: Date
    var status: CaptureStatus
    var lastError: String?
    var attemptCount: Int
    /// Server-side media id once uploaded — stays nil while pending.
    var remoteId: String?
}

@Observable
@MainActor
final class CaptureStore {
    static let shared = CaptureStore()

    private let folderName = "CaptureQueue"
    private let indexName = "index.json"

    private(set) var captures: [ConsultationCapture] = []

    init() {
        loadFromDisk()
    }

    // MARK: - Paths

    var folderURL: URL {
        let base = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask).first!
        let dir = base.appendingPathComponent(folderName, isDirectory: true)
        if !FileManager.default.fileExists(atPath: dir.path) {
            try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        }
        return dir
    }

    private var indexURL: URL { folderURL.appendingPathComponent(indexName) }

    func fileURL(for capture: ConsultationCapture) -> URL {
        folderURL.appendingPathComponent(capture.fileName)
    }

    // MARK: - CRUD

    func enqueue(
        stagingId: String,
        areaId: String?,
        areaName: String?,
        mediaType: CaptureMediaType,
        mimeType: String,
        sourceFileURL: URL
    ) throws -> ConsultationCapture {
        let id = UUID().uuidString
        let ext = sourceFileURL.pathExtension.isEmpty ? (mediaType == .video ? "mp4" : "jpg") : sourceFileURL.pathExtension
        let filename = "\(id).\(ext)"
        let destURL = folderURL.appendingPathComponent(filename)

        // Move into our sandbox — the caller may have written to a temp dir
        // that iOS will sweep away.
        if FileManager.default.fileExists(atPath: destURL.path) {
            try FileManager.default.removeItem(at: destURL)
        }
        try FileManager.default.moveItem(at: sourceFileURL, to: destURL)

        let size = (try? FileManager.default.attributesOfItem(atPath: destURL.path)[.size] as? Int) ?? 0

        let capture = ConsultationCapture(
            id: id,
            stagingId: stagingId,
            areaId: areaId,
            areaName: areaName,
            mediaType: mediaType,
            mimeType: mimeType,
            fileName: filename,
            byteSize: size,
            createdAt: Date(),
            status: .pending,
            lastError: nil,
            attemptCount: 0,
            remoteId: nil
        )
        captures.append(capture)
        writeToDisk()
        return capture
    }

    func captures(forStaging stagingId: String) -> [ConsultationCapture] {
        captures.filter { $0.stagingId == stagingId }.sorted { $0.createdAt < $1.createdAt }
    }

    func captures(forStaging stagingId: String, areaId: String?) -> [ConsultationCapture] {
        captures.filter { $0.stagingId == stagingId && $0.areaId == areaId }
            .sorted { $0.createdAt < $1.createdAt }
    }

    func update(_ capture: ConsultationCapture) {
        if let idx = captures.firstIndex(where: { $0.id == capture.id }) {
            captures[idx] = capture
            writeToDisk()
        }
    }

    func remove(_ capture: ConsultationCapture) {
        let file = fileURL(for: capture)
        try? FileManager.default.removeItem(at: file)
        captures.removeAll { $0.id == capture.id }
        writeToDisk()
    }

    func pendingCaptures() -> [ConsultationCapture] {
        captures.filter { $0.status == .pending || $0.status == .failed }
            .sorted { $0.createdAt < $1.createdAt }
    }

    // MARK: - Persistence

    private func writeToDisk() {
        do {
            let data = try JSONEncoder().encode(captures)
            try data.write(to: indexURL, options: .atomic)
        } catch {
            // Non-fatal: the queue is an optimisation, not the source of truth.
        }
    }

    private func loadFromDisk() {
        guard let data = try? Data(contentsOf: indexURL) else { return }
        if let decoded = try? JSONDecoder().decode([ConsultationCapture].self, from: data) {
            // Drop anything whose backing file got purged by iOS.
            self.captures = decoded.filter {
                FileManager.default.fileExists(atPath: fileURL(for: $0).path)
            }
        }
    }
}
