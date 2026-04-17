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

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(auth)
        }
    }
}
