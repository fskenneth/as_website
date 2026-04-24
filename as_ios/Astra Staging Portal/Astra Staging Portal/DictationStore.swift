//
//  DictationStore.swift
//  Astra Staging Portal
//
//  On-disk queue of voice dictations captured on the Consultation tab.
//  Mirrors CaptureStore: plain Codable index + a sibling audio file per
//  record, living in Application Support so iOS won't sweep it.
//
//  A pending dictation is an audio recording that hasn't yet been sent to
//  `/api/v1/stagings/{id}/dictations`. Once the server accepts it, the
//  entry is removed from this store (the server owns the transcript +
//  summary from that point on).
//

import Foundation
import Observation

enum PendingDictationStatus: String, Codable {
    case pending
    case uploading
    case failed
}

struct PendingDictation: Codable, Identifiable, Hashable {
    /// UUID used both as local primary key and as the `client_id` sent to
    /// the backend so retries are idempotent.
    let id: String
    let stagingId: String
    let stagingDisplayName: String?
    let areaId: String?
    let areaName: String?
    var fileName: String
    var byteSize: Int
    var durationSec: Double
    var createdAt: Date
    var status: PendingDictationStatus
    var lastError: String?
    var attemptCount: Int
}

@Observable
@MainActor
final class DictationStore {
    static let shared = DictationStore()

    private let folderName = "DictationQueue"
    private let indexName = "index.json"

    private(set) var pending: [PendingDictation] = []

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

    func fileURL(for dictation: PendingDictation) -> URL {
        folderURL.appendingPathComponent(dictation.fileName)
    }

    // MARK: - CRUD

    func enqueue(
        stagingId: String,
        stagingDisplayName: String?,
        areaId: String?,
        areaName: String?,
        durationSec: Double,
        sourceFileURL: URL,
    ) throws -> PendingDictation {
        let id = UUID().uuidString
        let ext = sourceFileURL.pathExtension.isEmpty ? "m4a" : sourceFileURL.pathExtension
        let filename = "\(id).\(ext)"
        let destURL = folderURL.appendingPathComponent(filename)

        if FileManager.default.fileExists(atPath: destURL.path) {
            try FileManager.default.removeItem(at: destURL)
        }
        try FileManager.default.moveItem(at: sourceFileURL, to: destURL)

        let size = (try? FileManager.default.attributesOfItem(atPath: destURL.path)[.size] as? Int) ?? 0

        let record = PendingDictation(
            id: id,
            stagingId: stagingId,
            stagingDisplayName: stagingDisplayName,
            areaId: areaId,
            areaName: areaName,
            fileName: filename,
            byteSize: size,
            durationSec: durationSec,
            createdAt: Date(),
            status: .pending,
            lastError: nil,
            attemptCount: 0,
        )
        pending.append(record)
        writeToDisk()
        return record
    }

    func update(_ dictation: PendingDictation) {
        if let idx = pending.firstIndex(where: { $0.id == dictation.id }) {
            pending[idx] = dictation
            writeToDisk()
        }
    }

    func remove(_ dictation: PendingDictation) {
        let file = fileURL(for: dictation)
        try? FileManager.default.removeItem(at: file)
        pending.removeAll { $0.id == dictation.id }
        writeToDisk()
    }

    func nextPending() -> PendingDictation? {
        pending.filter { $0.status == .pending || $0.status == .failed }
            .sorted { $0.createdAt < $1.createdAt }
            .first
    }

    func pendingCount(for stagingId: String? = nil) -> Int {
        pending.filter {
            ($0.status == .pending || $0.status == .failed)
                && (stagingId == nil || $0.stagingId == stagingId)
        }.count
    }

    // MARK: - Persistence

    private func writeToDisk() {
        do {
            let data = try JSONEncoder().encode(pending)
            try data.write(to: indexURL, options: .atomic)
        } catch {
            // Non-fatal: index is an optimisation, not source of truth.
        }
    }

    private func loadFromDisk() {
        guard let data = try? Data(contentsOf: indexURL) else { return }
        if let decoded = try? JSONDecoder().decode([PendingDictation].self, from: data) {
            self.pending = decoded.filter {
                FileManager.default.fileExists(atPath: fileURL(for: $0).path)
            }
        }
    }
}
