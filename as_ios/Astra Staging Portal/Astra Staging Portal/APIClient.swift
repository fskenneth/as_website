//
//  APIClient.swift
//  Astra Staging Portal
//

import Foundation

struct APIUser: Codable, Identifiable {
    let id: Int
    let first_name: String
    let last_name: String
    let email: String
    let user_role: String
    let phone: String?

    /// Tier for nav gating: execution (1) ⊂ manager (2) ⊂ owner (3).
    var roleLevel: Int {
        switch user_role.lowercased() {
        case "owner", "admin": return 3
        case "manager": return 2
        default: return 1  // mover, stager, customer
        }
    }
    var isManagerPlus: Bool { roleLevel >= 2 }
    var isOwner: Bool { roleLevel >= 3 }
}

struct Item: Codable, Identifiable {
    let name: String
    let type: String?
    let color: String?
    let style: String?
    let image_url: String?
    let model_3d: String?
    let width: String?
    let depth: String?
    let height: String?
    let count: Int

    var id: String { name }
}

struct LoginResponse: Codable {
    let token: String
    let user: APIUser
}

struct MeResponse: Codable {
    let user: APIUser
}

struct ItemsResponse: Codable {
    let items: [Item]
    let total: Int
}

// MARK: - Task Board models

struct Person: Codable, Hashable, Identifiable {
    let name: String?
    let id: String?
}

struct Customer: Codable {
    let first_name: String
    let last_name: String
    let phone: String?
    let email: String?
    var fullName: String {
        let n = "\(first_name) \(last_name)".trimmingCharacters(in: .whitespaces)
        return n.isEmpty ? "—" : n
    }
}

struct Fees: Codable {
    let total: Double
    let owing: Double
    let paid: Double
}

struct Milestone: Codable {
    let done: Bool
    let date: String?
}

struct StagingMilestones: Codable {
    let design: Milestone
    let before_pictures: Milestone
    let after_pictures: Milestone
    let packing: Milestone
    let setup: Milestone
    let whatsapp: Milestone
}

struct Staging: Codable, Identifiable {
    let id: String
    let name: String?
    let staging_date: String?
    let destaging_date: String?
    let address: String?
    let occupancy: String?
    let property_type: String?
    let staging_type: String?
    let status: String?
    let customer: Customer
    let stagers: [Person]
    let staging_movers: [Person]
    let destaging_movers: [Person]
    let staging_eta: String?
    let destaging_eta: String?
    let driving_time: String?
    let fees: Fees
    let milestones: StagingMilestones
    let moving_instructions: String?
    let destaging_instructions: String?
    let general_notes: String?
    let mls: String?
    let pictures_folder: String?
    let housesigma_url: String?
    let item_count: JSONStringOrInt?
}

/// Handles fields that Zoho returns as either string or int (e.g. item_count).
struct JSONStringOrInt: Codable {
    let stringValue: String

    init(from decoder: Decoder) throws {
        let c = try decoder.singleValueContainer()
        if let s = try? c.decode(String.self) { stringValue = s }
        else if let i = try? c.decode(Int.self) { stringValue = String(i) }
        else { stringValue = "" }
    }

    func encode(to encoder: Encoder) throws {
        var c = encoder.singleValueContainer()
        try c.encode(stringValue)
    }

    var intValue: Int { Int(stringValue) ?? 0 }
}

struct TaskBoardResponse: Codable {
    let stagings: [Staging]
    let total: Int
    let period: String
    let today: String
}

struct ConsultationStagingsResponse: Codable {
    let stagings: [Staging]
    let total: Int
    let today: String
}

// MARK: - Areas + Media

struct StagingArea: Codable, Identifiable, Hashable {
    let id: String
    let name: String
    let raw_name: String?
    let floor: String?
    let notes: String?
}

struct StagingAreasResponse: Codable {
    let staging_id: String
    let areas: [StagingArea]
    let total: Int
}

struct RemoteMedia: Codable, Identifiable {
    let id: String
    let staging_id: String
    let area_id: String?
    let area_name: String?
    let media_type: String
    let client_id: String?
    let file_size: Int?
    let mime_type: String?
    let uploaded_by: String?
    let uploaded_at: String?
    let zoho_synced: Bool?
    let url: String?
}

struct StagingMediaListResponse: Codable {
    let staging_id: String
    let media: [RemoteMedia]
    let total: Int
}

struct UploadedMedia: Codable {
    let id: String
    let staging_id: String
    let area_id: String?
    let area_name: String?
    let media_type: String
    let file_size: Int?
    let mime_type: String?
    let url: String?
}

struct MediaUploadResponse: Codable {
    let ok: Bool
    let deduped: Bool?
    let media: UploadedMedia
}

struct AreaCatalogEntry: Codable, Identifiable, Hashable {
    let name: String
    let count: Int
    var id: String { name }
}

struct AreaCatalogResponse: Codable {
    let catalog: [AreaCatalogEntry]
    let total: Int
}

struct CreateAreaResponse: Codable {
    let ok: Bool
    let area: StagingArea
}

// MARK: - Consultation Dictate

struct DictationQuoteLine: Codable, Hashable {
    let description: String
}

struct DictationSummary: Codable, Hashable {
    let key_points: [String]
    let customer_email_subject: String
    let customer_email_body: String
    let sales_rep_email_subject: String
    let sales_rep_email_body: String
    let suggested_quote_lines: [DictationQuoteLine]
}

struct SentEmailLog: Codable, Hashable {
    let recipient: String
    let to: String
    let subject: String
    let sent_at: String
    let success: Bool
    let message_id: String?
    let error: String?
}

struct DictationRecord: Codable, Identifiable, Hashable {
    let id: String
    let staging_id: String
    let area_id: String?
    let area_name: String?
    let client_id: String?
    let audio_size: Int?
    let duration_sec: Double?
    let transcript: String
    let summary: DictationSummary?
    let status: String
    let error: String?
    let sent_emails: [SentEmailLog]
    let uploaded_by: String?
    let created_at: String?
    let audio_url: String?
}

struct DictationUploadResponse: Codable {
    let ok: Bool
    let deduped: Bool?
    let dictation: DictationRecord
}

struct DictationListResponse: Codable {
    let staging_id: String
    let dictations: [DictationRecord]
    let total: Int
}

struct DictationSendEmailResponse: Codable {
    let ok: Bool
    let sent: [SentEmailLog]
    let errors: [String]
}

struct APIErrorBody: Codable {
    let error: String?
}

// MARK: - Quote / line items

struct QuoteCatalogItem: Codable, Identifiable, Hashable {
    let name: String
    let unit_price: Double
    var id: String { name }
}

struct QuoteCatalogResponse: Codable {
    let items: [QuoteCatalogItem]
    let total: Int
}

struct QuoteLineItem: Codable, Identifiable, Hashable {
    let id: String
    let item_name: String
    let unit_price: Double?
    let quantity: Int
}

struct QuoteArea: Codable, Identifiable, Hashable {
    let area_id: String
    let area_name: String
    let area_key: String?
    let add_items: [QuoteLineItem]
    let remove_items: [QuoteLineItem]
    let items_total: Double
    let cap: Double
    let effective: Double
    var id: String { area_id }
}

struct StagingQuote: Codable {
    let staging_id: String
    let property_type: String?
    let property_size: String?
    let base_fee: Double
    let areas: [QuoteArea]
    let grand_total: Double
}

struct LineItemUpsertBody: Codable {
    let action: String
    let item_name: String
    let delta: Int
}

enum APIError: LocalizedError {
    case badStatus(Int, String?)
    case transport(Error)
    case decoding(Error)

    var errorDescription: String? {
        switch self {
        case .badStatus(let code, let msg): return msg ?? "Server error (\(code))"
        case .transport(let e): return e.localizedDescription
        case .decoding: return "Unexpected server response"
        }
    }
}

final class APIClient {
    static let shared = APIClient()

    // Portal API lives in as_webapp on :5002. Public marketing site stays on :5001.
    // Simulator: localhost. Physical iPhone: change to "http://<m4-lan-ip>:5002"
    let baseURL = URL(string: "http://localhost:5002")!

    private let session: URLSession = {
        let cfg = URLSessionConfiguration.default
        cfg.timeoutIntervalForRequest = 15
        return URLSession(configuration: cfg)
    }()

    private let decoder: JSONDecoder = {
        let d = JSONDecoder()
        return d
    }()

    private func request(_ path: String, method: String = "GET", body: [String: Any]? = nil, token: String? = nil) -> URLRequest {
        var req = URLRequest(url: baseURL.appendingPathComponent(path))
        req.httpMethod = method
        // Content-Type only when there's actually a JSON body. Setting it on
        // an empty GET made FastHTML try to parse "" as JSON and return 500.
        if let body {
            req.setValue("application/json", forHTTPHeaderField: "Content-Type")
            req.httpBody = try? JSONSerialization.data(withJSONObject: body)
        }
        if let token { req.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization") }
        return req
    }

    private func send<T: Decodable>(_ req: URLRequest, as _: T.Type) async throws -> T {
        let (data, resp): (Data, URLResponse)
        do {
            (data, resp) = try await session.data(for: req)
        } catch {
            throw APIError.transport(error)
        }
        let status = (resp as? HTTPURLResponse)?.statusCode ?? 0
        guard (200..<300).contains(status) else {
            let msg = (try? decoder.decode(APIErrorBody.self, from: data))?.error
            throw APIError.badStatus(status, msg)
        }
        do {
            return try decoder.decode(T.self, from: data)
        } catch {
            throw APIError.decoding(error)
        }
    }

    // MARK: - Endpoints

    func login(email: String, password: String) async throws -> LoginResponse {
        let req = request("/api/v1/auth/login", method: "POST", body: ["email": email, "password": password])
        return try await send(req, as: LoginResponse.self)
    }

    func me(token: String) async throws -> MeResponse {
        try await send(request("/api/v1/auth/me", token: token), as: MeResponse.self)
    }

    func logout(token: String) async {
        _ = try? await session.data(for: request("/api/v1/auth/logout", method: "POST", token: token))
    }

    func items(search: String = "", token: String) async throws -> ItemsResponse {
        var comps = URLComponents(url: baseURL.appendingPathComponent("/api/v1/items"), resolvingAgainstBaseURL: false)!
        if !search.isEmpty {
            comps.queryItems = [URLQueryItem(name: "search", value: search)]
        }
        var req = URLRequest(url: comps.url!)
        req.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        return try await send(req, as: ItemsResponse.self)
    }

    func consultationStagings(token: String) async throws -> ConsultationStagingsResponse {
        var req = URLRequest(url: baseURL.appendingPathComponent("/api/v1/stagings/consultation"))
        req.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        return try await send(req, as: ConsultationStagingsResponse.self)
    }

    func taskBoard(period: String, mine: Bool, token: String) async throws -> TaskBoardResponse {
        var comps = URLComponents(url: baseURL.appendingPathComponent("/api/v1/tasks/board"), resolvingAgainstBaseURL: false)!
        comps.queryItems = [
            URLQueryItem(name: "period", value: period),
            URLQueryItem(name: "mine", value: mine ? "true" : "false"),
        ]
        var req = URLRequest(url: comps.url!)
        req.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        return try await send(req, as: TaskBoardResponse.self)
    }

    struct MilestoneResponse: Codable {
        let ok: Bool
        let staging_id: String
        let field: String
        let value: String
        let queued: Bool?
    }

    func setMilestone(stagingId: String, field: String, done: Bool, token: String) async throws -> MilestoneResponse {
        let path = "/api/v1/stagings/\(stagingId)/milestone"
        let req = request(path, method: "POST", body: ["field": field, "done": done], token: token)
        return try await send(req, as: MilestoneResponse.self)
    }

    // MARK: - Consultation media

    func stagingAreas(stagingId: String, token: String) async throws -> StagingAreasResponse {
        let path = "/api/v1/stagings/\(stagingId)/areas"
        var req = URLRequest(url: baseURL.appendingPathComponent(path))
        req.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        return try await send(req, as: StagingAreasResponse.self)
    }

    func areaCatalog(token: String) async throws -> AreaCatalogResponse {
        var req = URLRequest(url: baseURL.appendingPathComponent("/api/v1/areas/catalog"))
        req.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        return try await send(req, as: AreaCatalogResponse.self)
    }

    func createArea(stagingId: String, name: String, floor: String?, token: String) async throws -> CreateAreaResponse {
        var body: [String: Any] = ["name": name]
        if let floor, !floor.isEmpty { body["floor"] = floor }
        let req = request("/api/v1/stagings/\(stagingId)/areas", method: "POST", body: body, token: token)
        return try await send(req, as: CreateAreaResponse.self)
    }

    func renameArea(stagingId: String, areaId: String, newName: String, token: String) async throws -> CreateAreaResponse {
        let req = request(
            "/api/v1/stagings/\(stagingId)/areas/\(areaId)/rename",
            method: "POST",
            body: ["name": newName],
            token: token,
        )
        return try await send(req, as: CreateAreaResponse.self)
    }

    func listStagingMedia(stagingId: String, token: String) async throws -> StagingMediaListResponse {
        let path = "/api/v1/stagings/\(stagingId)/media"
        var req = URLRequest(url: baseURL.appendingPathComponent(path))
        req.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        return try await send(req, as: StagingMediaListResponse.self)
    }

    /// Multipart upload of a captured photo/video. `mediaType` is one of
    /// `photo`, `panorama`, `video`. `clientId` makes retries idempotent —
    /// the server returns the existing row if we resend the same id.
    func uploadMedia(
        stagingId: String,
        areaId: String?,
        areaName: String?,
        mediaType: String,
        clientId: String,
        fileURL: URL,
        mimeType: String,
        token: String
    ) async throws -> MediaUploadResponse {
        let path = "/api/v1/stagings/\(stagingId)/media"
        var req = URLRequest(url: baseURL.appendingPathComponent(path))
        req.httpMethod = "POST"
        req.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")

        // Upload timeout is per-request — videos can take 30+ seconds on a
        // weak LTE link, so bump past the default 15s set on the session.
        req.timeoutInterval = 120

        let boundary = "----AstraStaging-\(UUID().uuidString)"
        req.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")

        var body = Data()

        func appendField(_ name: String, _ value: String) {
            body.append("--\(boundary)\r\n".data(using: .utf8)!)
            body.append("Content-Disposition: form-data; name=\"\(name)\"\r\n\r\n".data(using: .utf8)!)
            body.append(value.data(using: .utf8)!)
            body.append("\r\n".data(using: .utf8)!)
        }

        if let areaId { appendField("area_id", areaId) }
        if let areaName { appendField("area_name", areaName) }
        appendField("media_type", mediaType)
        appendField("client_id", clientId)

        let fileData = try Data(contentsOf: fileURL)
        let filename = fileURL.lastPathComponent
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"file\"; filename=\"\(filename)\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: \(mimeType)\r\n\r\n".data(using: .utf8)!)
        body.append(fileData)
        body.append("\r\n".data(using: .utf8)!)

        body.append("--\(boundary)--\r\n".data(using: .utf8)!)
        req.httpBody = body

        return try await send(req, as: MediaUploadResponse.self)
    }

    // MARK: - Consultation Dictate

    /// Upload a dictation audio file (AAC .m4a). Server runs Whisper + gpt-4o-mini
    /// inline and returns the full record with transcript + summary + email drafts.
    /// Can take 30s–90s for long audio; bump timeout accordingly.
    func uploadDictation(
        stagingId: String,
        areaId: String?,
        areaName: String?,
        clientId: String,
        durationSec: Double,
        fileURL: URL,
        token: String
    ) async throws -> DictationUploadResponse {
        let path = "/api/v1/stagings/\(stagingId)/dictations"
        var req = URLRequest(url: baseURL.appendingPathComponent(path))
        req.httpMethod = "POST"
        req.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        req.timeoutInterval = 300  // Whisper + summary can be slow on long audio

        let boundary = "----AstraStaging-\(UUID().uuidString)"
        req.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")

        var body = Data()
        func appendField(_ name: String, _ value: String) {
            body.append("--\(boundary)\r\n".data(using: .utf8)!)
            body.append("Content-Disposition: form-data; name=\"\(name)\"\r\n\r\n".data(using: .utf8)!)
            body.append(value.data(using: .utf8)!)
            body.append("\r\n".data(using: .utf8)!)
        }

        if let areaId { appendField("area_id", areaId) }
        if let areaName { appendField("area_name", areaName) }
        appendField("client_id", clientId)
        appendField("duration_sec", String(format: "%.2f", durationSec))

        let fileData = try Data(contentsOf: fileURL)
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"file\"; filename=\"\(fileURL.lastPathComponent)\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: audio/m4a\r\n\r\n".data(using: .utf8)!)
        body.append(fileData)
        body.append("\r\n".data(using: .utf8)!)
        body.append("--\(boundary)--\r\n".data(using: .utf8)!)
        req.httpBody = body

        return try await send(req, as: DictationUploadResponse.self)
    }

    func listDictations(stagingId: String, token: String) async throws -> DictationListResponse {
        let path = "/api/v1/stagings/\(stagingId)/dictations"
        var req = URLRequest(url: baseURL.appendingPathComponent(path))
        req.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        return try await send(req, as: DictationListResponse.self)
    }

    /// Send email draft(s) for a dictation via Mailgun. `recipient` is one of
    /// "customer", "sales_rep", "both". Any subject/body left nil falls back
    /// to the summary draft stored on the server.
    /// Delete a media row + file on the server. No-op for records
    /// that were never uploaded (remoteId missing) — caller handles that.
    func deleteMedia(mediaId: String, token: String) async throws {
        let path = "/api/v1/media/\(mediaId)"
        var req = URLRequest(url: baseURL.appendingPathComponent(path))
        req.httpMethod = "DELETE"
        req.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        let (data, resp) = try await session.data(for: req)
        let status = (resp as? HTTPURLResponse)?.statusCode ?? 0
        // 404 means the server already doesn't have it — fine either way.
        guard (200..<300).contains(status) || status == 404 else {
            let msg = (try? decoder.decode(APIErrorBody.self, from: data))?.error
            throw APIError.badStatus(status, msg)
        }
    }

    func deleteDictation(dictationId: String, token: String) async throws {
        let path = "/api/v1/dictations/\(dictationId)"
        var req = URLRequest(url: baseURL.appendingPathComponent(path))
        req.httpMethod = "DELETE"
        req.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        let (data, resp) = try await session.data(for: req)
        let status = (resp as? HTTPURLResponse)?.statusCode ?? 0
        guard (200..<300).contains(status) else {
            let msg = (try? decoder.decode(APIErrorBody.self, from: data))?.error
            throw APIError.badStatus(status, msg)
        }
    }

    func deleteArea(stagingId: String, areaId: String, token: String) async throws {
        let path = "/api/v1/stagings/\(stagingId)/areas/\(areaId)"
        var req = URLRequest(url: baseURL.appendingPathComponent(path))
        req.httpMethod = "DELETE"
        req.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        let (data, resp) = try await session.data(for: req)
        let status = (resp as? HTTPURLResponse)?.statusCode ?? 0
        guard (200..<300).contains(status) else {
            let msg = (try? decoder.decode(APIErrorBody.self, from: data))?.error
            throw APIError.badStatus(status, msg)
        }
    }

    // MARK: - Quote / line items

    func quoteCatalog(token: String) async throws -> QuoteCatalogResponse {
        let req = request("/api/v1/quote/catalog", token: token)
        return try await send(req, as: QuoteCatalogResponse.self)
    }

    func stagingQuote(stagingId: String, token: String) async throws -> StagingQuote {
        let req = request("/api/v1/stagings/\(stagingId)/quote", token: token)
        return try await send(req, as: StagingQuote.self)
    }

    /// Tap once → quantity +1. Pass delta = -1 to decrement. Returns the
    /// full recomputed quote so the UI can refresh in one round-trip.
    func upsertLineItem(
        stagingId: String,
        areaId: String,
        action: String,
        itemName: String,
        delta: Int,
        token: String
    ) async throws -> StagingQuote {
        let body: [String: Any] = [
            "action": action,
            "item_name": itemName,
            "delta": delta,
        ]
        let req = request(
            "/api/v1/stagings/\(stagingId)/areas/\(areaId)/line-items",
            method: "POST", body: body, token: token,
        )
        return try await send(req, as: StagingQuote.self)
    }

    func deleteLineItem(
        stagingId: String,
        areaId: String,
        lineId: String,
        token: String
    ) async throws -> StagingQuote {
        let path = "/api/v1/stagings/\(stagingId)/areas/\(areaId)/line-items/\(lineId)"
        var req = URLRequest(url: baseURL.appendingPathComponent(path))
        req.httpMethod = "DELETE"
        req.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        let (data, resp) = try await session.data(for: req)
        let status = (resp as? HTTPURLResponse)?.statusCode ?? 0
        guard (200..<300).contains(status) else {
            let msg = (try? decoder.decode(APIErrorBody.self, from: data))?.error
            throw APIError.badStatus(status, msg)
        }
        return try decoder.decode(StagingQuote.self, from: data)
    }

    /// Download dictation audio bytes with Bearer auth. Used by
    /// DictationAudioPlayer to fetch before playback.
    func downloadDictationAudio(dictationId: String, token: String) async throws -> Data {
        let path = "/api/v1/dictations/\(dictationId)/audio"
        var req = URLRequest(url: baseURL.appendingPathComponent(path))
        req.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        req.timeoutInterval = 60
        let (data, resp) = try await session.data(for: req)
        let status = (resp as? HTTPURLResponse)?.statusCode ?? 0
        guard (200..<300).contains(status) else {
            throw APIError.badStatus(status, nil)
        }
        return data
    }

    func sendDictationEmail(
        dictationId: String,
        recipient: String,
        toCustomer: String?,
        customerSubject: String?,
        customerBody: String?,
        salesRepSubject: String?,
        salesRepBody: String?,
        token: String
    ) async throws -> DictationSendEmailResponse {
        var body: [String: Any] = ["recipient": recipient]
        if let toCustomer, !toCustomer.isEmpty { body["to_customer"] = toCustomer }
        if let customerSubject { body["customer_subject"] = customerSubject }
        if let customerBody { body["customer_body"] = customerBody }
        if let salesRepSubject { body["sales_rep_subject"] = salesRepSubject }
        if let salesRepBody { body["sales_rep_body"] = salesRepBody }
        let req = request("/api/v1/dictations/\(dictationId)/send-email", method: "POST", body: body, token: token)
        return try await send(req, as: DictationSendEmailResponse.self)
    }
}
