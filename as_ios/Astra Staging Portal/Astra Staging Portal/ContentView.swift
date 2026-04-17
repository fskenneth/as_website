//
//  ContentView.swift
//  Astra Staging Portal
//
//  Root view: routes between LoginView and ItemsView based on auth state.
//

import SwiftUI

struct ContentView: View {
    @Environment(AuthStore.self) private var auth

    var body: some View {
        Group {
            if auth.isLoading && !auth.isSignedIn {
                VStack(spacing: 16) {
                    ProgressView()
                    Text("Loading...").foregroundStyle(.secondary)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else if auth.isSignedIn {
                MainTabView()
            } else {
                LoginView()
            }
        }
    }
}
