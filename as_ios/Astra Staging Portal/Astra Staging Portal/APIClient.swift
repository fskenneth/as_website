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

    // Simulator: localhost. Physical iPhone: change to "http://192.168.2.236:5001"
    let baseURL = URL(string: "http://localhost:5001")!

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
}
