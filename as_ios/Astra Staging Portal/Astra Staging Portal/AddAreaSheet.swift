//
//  AddAreaSheet.swift
//  Astra Staging Portal
//
//  Picker for adding a new area to the staging when Zoho hasn't synced
//  any yet. Pre-fills a catalog of the most common names (fetched from
//  /api/v1/areas/catalog), and accepts a custom name if none match.
//

import SwiftUI

struct AddAreaSheet: View {
    let stagingId: String
    @Environment(AuthStore.self) private var auth

    let onCreated: (StagingArea) -> Void
    let onDismiss: () -> Void

    @State private var catalog: [AreaCatalogEntry] = []
    @State private var customName: String = ""
    @State private var selectedCatalogName: String?
    @State private var submitting = false
    @State private var error: String?

    private var effectiveName: String {
        let custom = customName.trimmingCharacters(in: .whitespacesAndNewlines)
        if !custom.isEmpty { return custom }
        return selectedCatalogName ?? ""
    }

    var body: some View {
        NavigationStack {
            Form {
                Section("Custom") {
                    TextField("Area name (e.g. Living Room)", text: $customName)
                        .textInputAutocapitalization(.words)
                        .autocorrectionDisabled()
                        .onChange(of: customName) { _, _ in
                            if !customName.isEmpty { selectedCatalogName = nil }
                        }
                }

                if !catalog.isEmpty {
                    Section("Common areas") {
                        ForEach(catalog) { entry in
                            Button {
                                selectedCatalogName = entry.name
                                customName = ""
                            } label: {
                                HStack {
                                    Text(entry.name)
                                        .foregroundStyle(.primary)
                                    Spacer()
                                    if selectedCatalogName == entry.name {
                                        Image(systemName: "checkmark")
                                            .foregroundStyle(Color.accentColor)
                                    } else {
                                        Text("\(entry.count)×")
                                            .font(.caption2)
                                            .foregroundStyle(.secondary)
                                    }
                                }
                            }
                        }
                    }
                }

                if let error {
                    Section { Text(error).font(.footnote).foregroundStyle(.red) }
                }
            }
            .navigationTitle("Add Area")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { onDismiss() }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Add") { Task { await create() } }
                        .disabled(effectiveName.isEmpty || submitting)
                }
            }
            .task { await loadCatalog() }
        }
    }

    private func loadCatalog() async {
        guard let token = auth.token else { return }
        do {
            let resp = try await APIClient.shared.areaCatalog(token: token)
            self.catalog = resp.catalog
        } catch {
            // Non-fatal — user can still type a custom name.
        }
    }

    private func create() async {
        guard let token = auth.token else { return }
        let name = effectiveName
        guard !name.isEmpty else { return }
        submitting = true
        defer { submitting = false }
        do {
            let resp = try await APIClient.shared.createArea(
                stagingId: stagingId, name: name, floor: nil, token: token,
            )
            onCreated(resp.area)
        } catch {
            self.error = error.localizedDescription
        }
    }
}
