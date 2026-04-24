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

        // DEV bypass: debug builds with a hardcoded token skip login entirely.
        if let bypass = DEV_BYPASS_TOKEN, !bypass.isEmpty {
            do {
                let me = try await APIClient.shared.me(token: bypass)
                self.token = bypass
                self.user = me.user
                return
            } catch {
                // Bypass rejected — fall through to normal flow so login screen shows
            }
        }

        guard let saved = Keychain.get(tokenKey), !saved.isEmpty else { return }
        do {
            let me = try await APIClient.shared.me(token: saved)
            self.token = saved
            self.user = me.user
        } catch APIError.badStatus(401, _) {
            // Server actively rejected the token — it's stale. Clear it.
            Keychain.delete(tokenKey)
        } catch {
            // Transport / non-401 failure (offline, VPN not up, server down, etc.).
            // DO NOT clear the token — the session is likely still valid. User
            // will see login this launch but the next good launch auto-restores.
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
        // Don't invalidate the dev bypass token server-side — next cold
        // start would lose the auto-login.
        if let t = token, t != DEV_BYPASS_TOKEN {
            await APIClient.shared.logout(token: t)
        }
        Keychain.delete(tokenKey)
        token = nil
        user = nil
    }
}
