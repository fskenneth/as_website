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

struct APIErrorBody: Codable {
    let error: String?
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
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        if let token { req.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization") }
        if let body { req.httpBody = try? JSONSerialization.data(withJSONObject: body) }
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
}
