//
//  ContentView.swift
//  Astra Staging Portal
//
//  Root view: routes between LoginView and ItemsView based on auth state.
//

import SwiftUI

struct ContentView: View {
    @Environment(AuthStore.self) private var auth
    @State private var network = NetworkMonitor.shared
    @State private var uploadQueue = UploadQueue.shared

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
        .task {
            // Try draining any captures left over from a previous session.
            uploadQueue.drainIfPossible(token: auth.token)
        }
        .onChange(of: network.isOnline) { _, online in
            if online { uploadQueue.drainIfPossible(token: auth.token) }
        }
        .onChange(of: network.isOnWiFi) { _, _ in
            uploadQueue.drainIfPossible(token: auth.token)
        }
    }
}
