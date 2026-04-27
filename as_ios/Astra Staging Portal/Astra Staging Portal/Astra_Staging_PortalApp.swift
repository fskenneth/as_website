//
//  Astra_Staging_PortalApp.swift
//  Astra Staging Portal
//
//  Created by Kenneth Jin on 2026-04-17.
//

import SwiftUI

@main
struct Astra_Staging_PortalApp: App {
    @State private var auth = AuthStore()
    @State private var chat = ChatStore()
    @State private var settings = AppSettings.shared
    @Environment(\.colorScheme) private var systemScheme

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(auth)
                .environment(chat)
                .preferredColorScheme(settings.themeMode.colorScheme)
                .tint(settings.accent.color(for: settings.themeMode.colorScheme ?? systemScheme))
                .task(id: auth.token ?? "") {
                    // Keep the chat SSE alive whenever we're signed in,
                    // independent of which tab is showing — that's what
                    // makes the FAB badge + toast banners work everywhere.
                    if let t = auth.token {
                        chat.bind(token: t)
                        await chat.refreshList(token: t)
                        await chat.loadEmployees(token: t)
                    } else {
                        chat.unbind()
                    }
                }
        }
    }
}
