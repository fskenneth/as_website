//
//  MainTabView.swift
//  Astra Staging Portal
//
//  5-tab navigation shell. Tabs are gated by user role:
//    execution (mover/stager): 3 tabs — Task Board, Items, Me
//    manager: 4 tabs          — + Sales & Management
//    owner:   5 tabs          — + HR & Accounting
//

import SwiftUI

struct MainTabView: View {
    @Environment(AuthStore.self) private var auth

    var body: some View {
        TabView {
            TaskBoardView()
                .tabItem { Label("Task Board", systemImage: "checklist") }

            ItemsView()
                .tabItem { Label("Items", systemImage: "shippingbox") }

            MeView()
                .tabItem { Label("Me", systemImage: "person.circle") }

            if let user = auth.user, user.isManagerPlus {
                SalesManagementView()
                    .tabItem { Label("Sales", systemImage: "briefcase") }
            }

            if let user = auth.user, user.isOwner {
                HRAccountingView()
                    .tabItem { Label("HR", systemImage: "building.2") }
            }
        }
    }
}

// MARK: - Placeholder views for not-yet-built tabs

private struct PlaceholderView: View {
    let title: String
    let subtitle: String
    let systemImage: String

    var body: some View {
        NavigationStack {
            VStack(spacing: 16) {
                Image(systemName: systemImage)
                    .font(.system(size: 56))
                    .foregroundStyle(.secondary)
                Text(title).font(.title2).bold()
                Text(subtitle)
                    .font(.body)
                    .foregroundStyle(.secondary)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal)
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .navigationTitle(title)
        }
    }
}

struct MeView: View {
    @Environment(AuthStore.self) private var auth

    var body: some View {
        NavigationStack {
            List {
                if let user = auth.user {
                    Section("Profile") {
                        LabeledContent("Name", value: "\(user.first_name) \(user.last_name)")
                        LabeledContent("Email", value: user.email)
                        LabeledContent("Role", value: user.user_role.capitalized)
                    }
                }

                Section("Coming soon") {
                    Label("Working Time Tracker", systemImage: "clock")
                        .foregroundStyle(.secondary)
                    Label("Expense", systemImage: "doc.text")
                        .foregroundStyle(.secondary)
                    Label("My Pay", systemImage: "dollarsign.circle")
                        .foregroundStyle(.secondary)
                }

                Section {
                    Button(role: .destructive) {
                        Task { await auth.logout() }
                    } label: {
                        Label("Logout", systemImage: "rectangle.portrait.and.arrow.right")
                    }
                }
            }
            .navigationTitle("Me")
        }
    }
}

struct SalesManagementView: View {
    var body: some View {
        PlaceholderView(
            title: "Sales & Management",
            subtitle: "Inquiries, staging assignment, invoicing, customer portal.\nComing soon.",
            systemImage: "briefcase"
        )
    }
}

struct HRAccountingView: View {
    var body: some View {
        PlaceholderView(
            title: "HR & Accounting",
            subtitle: "Employees, all pay, staging analytics.\nComing soon.",
            systemImage: "building.2"
        )
    }
}
