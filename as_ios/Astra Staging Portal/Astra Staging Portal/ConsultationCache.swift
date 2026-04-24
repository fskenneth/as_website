//
//  ConsultationCache.swift
//  Astra Staging Portal
//
//  On-disk JSON cache for the Consultation screen so the app opens
//  instantly on flaky/no connectivity. We write-through whenever a fresh
//  response lands, and the screen loads from cache first.
//
//  Cache lives under Application Support/ConsultationCache/.
//

import Foundation

enum ConsultationCache {
    private static let folderName = "ConsultationCache"
    private static let stagingsFile = "stagings.json"

    private static var folderURL: URL {
        let base = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask).first!
        let dir = base.appendingPathComponent(folderName, isDirectory: true)
        if !FileManager.default.fileExists(atPath: dir.path) {
            try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        }
        return dir
    }

    private static func areasFile(for stagingId: String) -> URL {
        folderURL.appendingPathComponent("areas-\(safeName(stagingId)).json", isDirectory: false)
    }

    private static func safeName(_ s: String) -> String {
        s.replacingOccurrences(of: "/", with: "_")
         .replacingOccurrences(of: "..", with: "_")
    }

    // MARK: - Stagings

    static func saveStagings(_ response: ConsultationStagingsResponse) {
        let url = folderURL.appendingPathComponent(stagingsFile)
        guard let data = try? JSONEncoder().encode(response) else { return }
        try? data.write(to: url, options: .atomic)
    }

    static func loadStagings() -> ConsultationStagingsResponse? {
        let url = folderURL.appendingPathComponent(stagingsFile)
        guard let data = try? Data(contentsOf: url) else { return nil }
        return try? JSONDecoder().decode(ConsultationStagingsResponse.self, from: data)
    }

    // MARK: - Areas (per staging)

    static func saveAreas(_ response: StagingAreasResponse) {
        let url = areasFile(for: response.staging_id)
        guard let data = try? JSONEncoder().encode(response) else { return }
        try? data.write(to: url, options: .atomic)
    }

    static func loadAreas(stagingId: String) -> StagingAreasResponse? {
        let url = areasFile(for: stagingId)
        guard let data = try? Data(contentsOf: url) else { return nil }
        return try? JSONDecoder().decode(StagingAreasResponse.self, from: data)
    }
}
