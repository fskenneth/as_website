//
//  AppSettings.swift
//  Astra Staging Portal
//
//  User-configurable preferences persisted in UserDefaults.
//  - wifiOnlyMediaUpload: photo/video uploads wait for Wi-Fi.
//  - themeMode: system / light / dark override (matches webapp).
//  - accent: six accent palettes matching the webapp theme picker.
//

import Foundation
import Observation
import SwiftUI

enum ThemeMode: String, CaseIterable, Identifiable {
    case auto
    case light
    case dark

    var id: String { rawValue }
    var label: String {
        switch self {
        case .auto: return "Auto"
        case .light: return "Light"
        case .dark: return "Dark"
        }
    }
    var colorScheme: ColorScheme? {
        switch self {
        case .auto: return nil
        case .light: return .light
        case .dark: return .dark
        }
    }
}

enum AccentTheme: String, CaseIterable, Identifiable {
    case slate
    case ocean
    case forest
    case sunset
    case rose
    case noir

    var id: String { rawValue }

    var label: String {
        switch self {
        case .slate:  return "Slate"
        case .ocean:  return "Ocean"
        case .forest: return "Forest"
        case .sunset: return "Sunset"
        case .rose:   return "Rose"
        case .noir:   return "Noir"
        }
    }

    /// Light-mode accent hex — matches `:root[data-theme="..."]` in the webapp.
    var lightHex: String {
        switch self {
        case .slate:  return "#4f46e5"
        case .ocean:  return "#0891b2"
        case .forest: return "#059669"
        case .sunset: return "#ea580c"
        case .rose:   return "#e11d48"
        case .noir:   return "#0a0a0a"
        }
    }

    /// Dark-mode accent hex — lifted from the webapp dark overrides so the
    /// iOS tint stays readable on a dark background.
    var darkHex: String {
        switch self {
        case .slate:  return "#818cf8"
        case .ocean:  return "#22d3ee"
        case .forest: return "#34d399"
        case .sunset: return "#fb923c"
        case .rose:   return "#fb7185"
        case .noir:   return "#e5e5e5"
        }
    }

    func color(for scheme: ColorScheme) -> Color {
        Color(hex: scheme == .dark ? darkHex : lightHex) ?? .accentColor
    }
}

@Observable
@MainActor
final class AppSettings {
    static let shared = AppSettings()

    private let defaults = UserDefaults.standard
    private let wifiOnlyKey = "settings.wifiOnlyMediaUpload"
    private let themeModeKey = "settings.themeMode"
    private let accentKey = "settings.accentTheme"

    var wifiOnlyMediaUpload: Bool {
        didSet { defaults.set(wifiOnlyMediaUpload, forKey: wifiOnlyKey) }
    }

    var themeMode: ThemeMode {
        didSet { defaults.set(themeMode.rawValue, forKey: themeModeKey) }
    }

    var accent: AccentTheme {
        didSet { defaults.set(accent.rawValue, forKey: accentKey) }
    }

    init() {
        if defaults.object(forKey: wifiOnlyKey) == nil {
            defaults.set(true, forKey: wifiOnlyKey)
        }
        self.wifiOnlyMediaUpload = defaults.bool(forKey: wifiOnlyKey)
        self.themeMode = ThemeMode(rawValue: defaults.string(forKey: themeModeKey) ?? "") ?? .auto
        self.accent = AccentTheme(rawValue: defaults.string(forKey: accentKey) ?? "") ?? .slate
    }
}

// MARK: - Color(hex:) helper

extension Color {
    init?(hex: String) {
        var s = hex.trimmingCharacters(in: .whitespacesAndNewlines)
        if s.hasPrefix("#") { s.removeFirst() }
        guard s.count == 6, let value = UInt32(s, radix: 16) else { return nil }
        let r = Double((value >> 16) & 0xFF) / 255.0
        let g = Double((value >> 8) & 0xFF) / 255.0
        let b = Double(value & 0xFF) / 255.0
        self.init(red: r, green: g, blue: b)
    }
}
