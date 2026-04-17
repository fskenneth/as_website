//
//  AuthStore.swift
//  Astra Staging Portal
//

import Foundation
import Observation

@Observable
@MainActor
final class AuthStore {
    var user: APIUser?
    var isLoading = true
    var loginError: String?

    @ObservationIgnored private(set) var token: String?

    private let tokenKey = "auth_token"

    init() {
        Task { await restoreSession() }
    }

    var isSignedIn: Bool { user != nil && token != nil }

    func restoreSession() async {
        defer { isLoading = false }
        guard let saved = Keychain.get(tokenKey), !saved.isEmpty else { return }
        do {
            let me = try await APIClient.shared.me(token: saved)
            self.token = saved
            self.user = me.user
        } catch {
            // Token stale or server down — clear it so user sees login
            Keychain.delete(tokenKey)
        }
    }

    func login(email: String, password: String) async {
        loginError = nil
        isLoading = true
        defer { isLoading = false }
        do {
            let resp = try await APIClient.shared.login(email: email, password: password)
            Keychain.set(resp.token, for: tokenKey)
            self.token = resp.token
            self.user = resp.user
        } catch let APIError.badStatus(_, msg) {
            loginError = msg ?? "Login failed"
        } catch {
            loginError = error.localizedDescription
        }
    }

    func logout() async {
        if let t = token { await APIClient.shared.logout(token: t) }
        Keychain.delete(tokenKey)
        token = nil
        user = nil
    }
}
