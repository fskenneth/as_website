//
//  SettingsView.swift
//  Astra Staging Portal
//
//  Small settings screen reachable from the Me menu.
//

import SwiftUI

struct SettingsView: View {
    @Environment(AuthStore.self) private var auth
    @Environment(\.colorScheme) private var systemScheme

    @State private var settings = AppSettings.shared
    @State private var network = NetworkMonitor.shared
    @State private var uploads = UploadQueue.shared
    @State private var captureStore = CaptureStore.shared

    var body: some View {
        Form {
            Section("Uploads") {
                Toggle(isOn: Binding(
                    get: { settings.wifiOnlyMediaUpload },
                    set: { newValue in
                        settings.wifiOnlyMediaUpload = newValue
                        uploads.drainIfPossible(token: auth.token)
                    }
                )) {
                    VStack(alignment: .leading, spacing: 2) {
                        Text("Upload Photos and Videos on Wi-Fi Only")
                        Text("Text updates (e.g. task board, milestones) still sync over cellular.")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }
            }

            Section("Chat") {
                Toggle(isOn: Binding(
                    get: { settings.enterToSend },
                    set: { settings.enterToSend = $0 }
                )) {
                    VStack(alignment: .leading, spacing: 2) {
                        Text("Enter to Send")
                        Text("Off: pressing return inserts a newline; tap the send button to send.")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }
            }

            Section("Appearance") {
                Picker("Mode", selection: Binding(
                    get: { settings.themeMode },
                    set: { settings.themeMode = $0 }
                )) {
                    ForEach(ThemeMode.allCases) { mode in
                        Text(mode.label).tag(mode)
                    }
                }
                .pickerStyle(.segmented)

                VStack(alignment: .leading, spacing: 8) {
                    Text("Color").font(.subheadline)
                    HStack(spacing: 12) {
                        ForEach(AccentTheme.allCases) { theme in
                            Button {
                                settings.accent = theme
                            } label: {
                                VStack(spacing: 4) {
                                    ZStack {
                                        Circle()
                                            .fill(theme.color(for: effectiveScheme))
                                            .frame(width: 32, height: 32)
                                        if settings.accent == theme {
                                            Image(systemName: "checkmark")
                                                .font(.caption.bold())
                                                .foregroundStyle(.white)
                                        }
                                    }
                                    .overlay(
                                        Circle()
                                            .stroke(settings.accent == theme ? Color.primary : .clear, lineWidth: 2)
                                            .padding(-3)
                                    )
                                    Text(theme.label)
                                        .font(.caption2)
                                        .foregroundStyle(.secondary)
                                }
                            }
                            .buttonStyle(.plain)
                        }
                    }
                    .padding(.vertical, 4)
                }
            }

            Section("Connection") {
                LabeledContent("Status", value: network.isOnline ? "Online" : "Offline")
                LabeledContent("Network", value: network.isOnWiFi ? "Wi-Fi" : (network.isOnline ? "Cellular" : "—"))
            }

            Section("Upload Queue") {
                let pendingCaptures = captureStore.pendingCaptures()
                if let msg = uploads.lastMessage {
                    LabeledContent("Last", value: msg)
                }
                Button("Retry Now") {
                    uploads.drainIfPossible(token: auth.token)
                }
                .disabled(pendingCaptures.isEmpty || !network.isOnline)

                if pendingCaptures.isEmpty {
                    Text("Nothing queued.")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                } else {
                    ForEach(pendingCaptures) { capture in
                        UploadQueueRow(
                            capture: capture,
                            onDelete: {
                                // Stop any in-flight upload + drop the
                                // file from disk so the next drain pass
                                // doesn't pick it back up.
                                captureStore.remove(capture)
                            }
                        )
                    }
                }
            }
        }
        .navigationTitle("Settings")
    }

    private var effectiveScheme: ColorScheme {
        settings.themeMode.colorScheme ?? systemScheme
    }
}

/// Row rendered per pending item in the Upload Queue section: filename,
/// size, live status (pending/uploading/failed + attempt count), and a
/// delete button that stops the upload and drops the file from disk.
private struct UploadQueueRow: View {
    let capture: ConsultationCapture
    let onDelete: () -> Void

    var body: some View {
        HStack(alignment: .center, spacing: 12) {
            Image(systemName: iconSymbol)
                .font(.body)
                .foregroundStyle(.secondary)
                .frame(width: 22)

            VStack(alignment: .leading, spacing: 2) {
                Text(capture.fileName)
                    .font(.footnote.monospaced())
                    .lineLimit(1)
                    .truncationMode(.middle)
                HStack(spacing: 8) {
                    Text(formatBytes(capture.byteSize))
                        .font(.caption2)
                        .foregroundStyle(.secondary)
                    statusPill
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)

            Button(role: .destructive) {
                onDelete()
            } label: {
                Image(systemName: "trash")
                    .foregroundStyle(.red)
            }
            .buttonStyle(.plain)
        }
        .padding(.vertical, 2)
    }

    private var iconSymbol: String {
        switch capture.mediaType {
        case .photo:    return "photo"
        case .panorama: return "pano"
        case .video:    return "video"
        }
    }

    @ViewBuilder
    private var statusPill: some View {
        switch capture.status {
        case .pending:
            Label("Queued", systemImage: "clock")
                .font(.caption2)
                .foregroundStyle(.orange)
                .labelStyle(.titleAndIcon)
        case .uploading:
            HStack(spacing: 4) {
                ProgressView().controlSize(.mini)
                Text("Uploading…").font(.caption2).foregroundStyle(.blue)
            }
        case .failed:
            let detail = capture.lastError.flatMap { $0.isEmpty ? nil : " · \($0)" } ?? ""
            Label("Failed (try \(capture.attemptCount))\(detail)",
                  systemImage: "exclamationmark.triangle")
                .font(.caption2)
                .foregroundStyle(.red)
                .labelStyle(.titleAndIcon)
                .lineLimit(1)
        case .uploaded:
            Label("Done", systemImage: "checkmark")
                .font(.caption2)
                .foregroundStyle(.green)
                .labelStyle(.titleAndIcon)
        }
    }
}

/// Human-readable byte count (KB / MB / GB).
private func formatBytes(_ bytes: Int) -> String {
    let fmt = ByteCountFormatter()
    fmt.allowedUnits = [.useKB, .useMB, .useGB]
    fmt.countStyle = .file
    return fmt.string(fromByteCount: Int64(bytes))
}
