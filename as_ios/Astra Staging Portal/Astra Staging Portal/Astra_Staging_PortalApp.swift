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
    @State private var settings = AppSettings.shared
    @Environment(\.colorScheme) private var systemScheme

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(auth)
                .preferredColorScheme(settings.themeMode.colorScheme)
                .tint(settings.accent.color(for: settings.themeMode.colorScheme ?? systemScheme))
        }
    }
}
