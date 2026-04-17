//
//  ItemsView.swift
//  Astra Staging Portal
//

import SwiftUI

struct ItemsView: View {
    @Environment(AuthStore.self) private var auth
    @State private var items: [Item] = []
    @State private var search = ""
    @State private var isLoading = false
    @State private var error: String?

    var body: some View {
        NavigationStack {
            Group {
                if isLoading && items.isEmpty {
                    ProgressView("Loading items...").frame(maxWidth: .infinity, maxHeight: .infinity)
                } else if let error, items.isEmpty {
                    VStack(spacing: 12) {
                        Text("Couldn't load items").font(.headline)
                        Text(error).font(.footnote).foregroundStyle(.secondary).multilineTextAlignment(.center)
                        Button("Retry") { Task { await load() } }
                    }
                    .padding()
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else {
                    List(items) { item in
                        ItemRow(item: item)
                    }
                    .listStyle(.plain)
                    .refreshable { await load() }
                }
            }
            .navigationTitle("Items")
            .searchable(text: $search, prompt: "Search items or types")
            .onSubmit(of: .search) { Task { await load() } }
            .onChange(of: search) { _, newValue in
                if newValue.isEmpty { Task { await load() } }
            }
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    if let u = auth.user {
                        Text("\(u.first_name) · \(u.user_role)")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Logout") { Task { await auth.logout() } }
                }
            }
            .task { await load() }
        }
    }

    private func load() async {
        guard let token = auth.token else { return }
        isLoading = true
        error = nil
        defer { isLoading = false }
        do {
            let resp = try await APIClient.shared.items(search: search.trimmingCharacters(in: .whitespaces), token: token)
            items = resp.items
        } catch let APIError.badStatus(code, _) where code == 401 {
            // Token invalid — kick to login
            await auth.logout()
        } catch {
            self.error = error.localizedDescription
        }
    }
}

private struct ItemRow: View {
    let item: Item

    var body: some View {
        HStack(spacing: 12) {
            AsyncImage(url: URL(string: item.image_url ?? "")) { phase in
                switch phase {
                case .empty: Color(.tertiarySystemBackground)
                case .success(let img): img.resizable().scaledToFill()
                case .failure: Color(.tertiarySystemBackground)
                @unknown default: Color(.tertiarySystemBackground)
                }
            }
            .frame(width: 56, height: 56)
            .clipShape(RoundedRectangle(cornerRadius: 8))

            VStack(alignment: .leading, spacing: 4) {
                Text(item.name).font(.body).lineLimit(2)
                HStack(spacing: 8) {
                    if let t = item.type, !t.isEmpty {
                        Text(t).font(.caption).foregroundStyle(.secondary)
                    }
                    if item.count > 1 {
                        Text("× \(item.count)").font(.caption).foregroundStyle(.secondary)
                    }
                }
            }
            Spacer()
        }
        .padding(.vertical, 4)
    }
}
