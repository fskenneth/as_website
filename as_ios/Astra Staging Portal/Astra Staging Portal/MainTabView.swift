//
//  MainTabView.swift
//  Astra Staging Portal
//
//  Home-screen-style menu shell:
//    • 4-slot dock + "More" button; overflow items live in a pull-up sheet.
//    • Long-press any item (dock or overflow) → enters edit mode. In edit
//      mode every tile wiggles and can be dragged onto any other tile to
//      swap slots (including swaps across the dock / overflow boundary).
//    • Layout is persisted per-install via MenuPreferences (UserDefaults).
//    • Role gating: items with minRoleLevel > user.roleLevel are filtered
//      out before the dock/overflow split.
//

import SwiftUI
import UIKit

struct MainTabView: View {
    @Environment(AuthStore.self) private var auth
    @State private var prefs = MenuPreferences()
    @State private var selected: MenuItem = .tasks
    @State private var moreOpen = false
    @State private var editMode = false

    private var roleLevel: Int { auth.user?.roleLevel ?? 1 }
    private var visibleItems: [MenuItem] { prefs.visibleItems(for: roleLevel) }
    private var dockItems: [MenuItem] { prefs.dockItems(for: roleLevel) }
    private var overflowItems: [MenuItem] { prefs.overflowItems(for: roleLevel) }
    private var activeItem: MenuItem {
        visibleItems.contains(selected) ? selected : (visibleItems.first ?? .tasks)
    }

    var body: some View {
        ZStack {
            VStack(spacing: 0) {
                // All screens are kept alive in a ZStack so state (scroll positions,
                // pickers, etc.) survives tab switches — same as native TabView.
                ZStack {
                    ForEach(MenuItem.allCases) { item in
                        screen(for: item)
                            .opacity(item == activeItem ? 1 : 0)
                            .allowsHitTesting(item == activeItem)
                    }
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)

                DockBar(
                    items: dockItems,
                    selected: activeItem,
                    showMore: !overflowItems.isEmpty,
                    moreActive: moreOpen,
                    onSelect: { selected = $0 },
                    onMore: { moreOpen = true },
                    onLongPress: enterEditMode
                )
            }

            if editMode {
                EditMenuOverlay(
                    prefs: prefs,
                    roleLevel: roleLevel,
                    onDone: { withAnimation(.spring(response: 0.35, dampingFraction: 0.85)) { editMode = false } }
                )
                .transition(.opacity)
                .zIndex(10)
            }
        }
        .sheet(isPresented: $moreOpen) {
            MoreSheet(
                items: overflowItems,
                selected: activeItem,
                onSelect: { item in
                    selected = item
                    moreOpen = false
                },
                onLongPress: {
                    moreOpen = false
                    // Small delay so the sheet can dismiss before the edit
                    // overlay fades in, otherwise the two animations fight.
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.28) {
                        enterEditMode()
                    }
                }
            )
            .presentationDetents([.fraction(0.45), .large])
            .presentationDragIndicator(.visible)
        }
    }

    private func enterEditMode() {
        let gen = UIImpactFeedbackGenerator(style: .medium)
        gen.impactOccurred()
        withAnimation(.spring(response: 0.35, dampingFraction: 0.85)) {
            editMode = true
        }
    }

    @ViewBuilder
    private func screen(for item: MenuItem) -> some View {
        switch item {
        case .tasks:        TaskBoardView()
        case .items:        ItemsView()
        case .me:           MeView()
        case .consultation: ConsultationView()
        case .sales:        SalesManagementView()
        case .hr:           HRAccountingView()
        }
    }
}

// MARK: - Dock Bar

private struct DockBar: View {
    let items: [MenuItem]
    let selected: MenuItem
    let showMore: Bool
    let moreActive: Bool
    let onSelect: (MenuItem) -> Void
    let onMore: () -> Void
    let onLongPress: () -> Void

    var body: some View {
        HStack(spacing: 0) {
            ForEach(items) { item in
                DockButton(
                    label: item.label,
                    symbol: item.sfSymbol,
                    active: item == selected,
                    action: { onSelect(item) },
                    onLongPress: onLongPress
                )
            }
            if showMore {
                DockButton(
                    label: "More",
                    symbol: "ellipsis",
                    active: moreActive,
                    action: onMore,
                    onLongPress: onLongPress
                )
            }
        }
        .padding(.top, 6)
        .background(.bar)
        .overlay(alignment: .top) {
            Divider()
        }
    }
}

private struct DockButton: View {
    let label: String
    let symbol: String
    let active: Bool
    let action: () -> Void
    let onLongPress: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 3) {
                Image(systemName: symbol).font(.system(size: 22))
                Text(label).font(.system(size: 10))
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 4)
            .foregroundStyle(active ? Color.accentColor : Color.secondary)
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .simultaneousGesture(
            LongPressGesture(minimumDuration: 0.5).onEnded { _ in onLongPress() }
        )
    }
}

// MARK: - More Sheet (read-only grid)

private struct MoreSheet: View {
    let items: [MenuItem]
    let selected: MenuItem
    let onSelect: (MenuItem) -> Void
    let onLongPress: () -> Void

    private let cols = [GridItem(.adaptive(minimum: 84, maximum: 120), spacing: 20)]

    var body: some View {
        NavigationStack {
            ScrollView {
                LazyVGrid(columns: cols, spacing: 20) {
                    ForEach(items) { item in
                        Button { onSelect(item) } label: {
                            MoreTile(item: item, active: item == selected)
                        }
                        .buttonStyle(.plain)
                        .simultaneousGesture(
                            LongPressGesture(minimumDuration: 0.5).onEnded { _ in onLongPress() }
                        )
                    }
                }
                .padding(20)

                Text("Long-press any icon to rearrange your menu.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .padding(.top, 4)
                    .padding(.bottom, 24)
            }
            .navigationTitle("More")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
}

private struct MoreTile: View {
    let item: MenuItem
    let active: Bool
    var body: some View {
        VStack(spacing: 8) {
            Image(systemName: item.sfSymbol)
                .font(.system(size: 28))
                .frame(width: 60, height: 60)
                .background(active ? Color.accentColor.opacity(0.18) : Color(.secondarySystemGroupedBackground))
                .foregroundStyle(active ? Color.accentColor : Color.primary)
                .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
            Text(item.label)
                .font(.caption)
                .foregroundStyle(.primary)
                .lineLimit(1)
        }
    }
}

// MARK: - Edit Mode Overlay (drag-and-drop swap)

private struct EditMenuOverlay: View {
    let prefs: MenuPreferences
    let roleLevel: Int
    let onDone: () -> Void

    @State private var wiggle = false

    private var dockItems: [MenuItem] { prefs.dockItems(for: roleLevel) }
    private var overflowItems: [MenuItem] { prefs.overflowItems(for: roleLevel) }
    private let gridCols = [GridItem(.adaptive(minimum: 84, maximum: 120), spacing: 20)]

    var body: some View {
        ZStack {
            // Backdrop dims the underlying app
            Color.black.opacity(0.35).ignoresSafeArea()
                .onTapGesture { onDone() }

            VStack(spacing: 0) {
                header
                overflowArea
                Divider().padding(.horizontal, 12)
                dockSectionLabel
                dockArea
            }
            .background(
                RoundedRectangle(cornerRadius: 0)
                    .fill(.regularMaterial)
                    .ignoresSafeArea()
            )
        }
        .onAppear {
            withAnimation(.easeInOut(duration: 0.16).repeatForever(autoreverses: true)) {
                wiggle.toggle()
            }
        }
    }

    private var header: some View {
        HStack {
            VStack(alignment: .leading, spacing: 2) {
                Text("Customize Menu").font(.headline)
                Text("Drag an icon onto another to swap.")
                    .font(.caption).foregroundStyle(.secondary)
            }
            Spacer()
            Button("Done") { onDone() }
                .buttonStyle(.borderedProminent)
                .controlSize(.small)
        }
        .padding(.horizontal, 16)
        .padding(.top, 16)
        .padding(.bottom, 8)
    }

    private var overflowArea: some View {
        ScrollView {
            if overflowItems.isEmpty {
                VStack(spacing: 8) {
                    Image(systemName: "rectangle.dashed")
                        .font(.system(size: 36))
                        .foregroundStyle(.tertiary)
                    Text("All your items are in the dock.")
                        .font(.footnote).foregroundStyle(.secondary)
                }
                .frame(maxWidth: .infinity)
                .padding(.vertical, 40)
            } else {
                LazyVGrid(columns: gridCols, spacing: 20) {
                    ForEach(overflowItems) { item in
                        EditTile(item: item, wiggle: wiggle, prefs: prefs)
                    }
                }
                .padding(20)
            }
        }
        .frame(maxHeight: .infinity)
    }

    private var dockSectionLabel: some View {
        HStack {
            Text("DOCK")
                .font(.caption2).fontWeight(.semibold)
                .foregroundStyle(.secondary)
                .tracking(0.8)
            Spacer()
        }
        .padding(.horizontal, 20)
        .padding(.top, 10)
        .padding(.bottom, 4)
    }

    private var dockArea: some View {
        HStack(spacing: 4) {
            ForEach(dockItems) { item in
                EditTile(item: item, wiggle: wiggle, prefs: prefs)
                    .frame(maxWidth: .infinity)
            }
            // Placeholder for the "More" slot in the dock so the layout matches
            // the real bar — it's not draggable and not a drop target.
            if !overflowItems.isEmpty {
                VStack(spacing: 8) {
                    Image(systemName: "ellipsis")
                        .font(.system(size: 22))
                        .frame(width: 56, height: 56)
                        .foregroundStyle(.tertiary)
                        .background(Color(.quaternarySystemFill))
                        .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
                    Text("More").font(.caption2).foregroundStyle(.tertiary)
                }
                .frame(maxWidth: .infinity)
            }
        }
        .padding(.horizontal, 12)
        .padding(.top, 4)
        .padding(.bottom, 20)
    }
}

// MARK: - Draggable / droppable tile

private struct EditTile: View {
    let item: MenuItem
    let wiggle: Bool
    let prefs: MenuPreferences

    @State private var isTargeted = false
    @State private var isBeingDragged = false

    // A small per-item offset so the wiggle feels organic rather than
    // a fleet of icons rotating in unison.
    private var phase: Double {
        Double(abs(item.rawValue.hashValue) % 100) / 100.0
    }

    var body: some View {
        VStack(spacing: 8) {
            Image(systemName: item.sfSymbol)
                .font(.system(size: 28))
                .frame(width: 60, height: 60)
                .background(tileBackground)
                .foregroundStyle(.primary)
                .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
                .overlay(
                    RoundedRectangle(cornerRadius: 14, style: .continuous)
                        .strokeBorder(isTargeted ? Color.accentColor : Color.clear, lineWidth: 2)
                )
                .scaleEffect(isTargeted ? 1.08 : 1.0)

            Text(item.label)
                .font(.caption)
                .foregroundStyle(.primary)
                .lineLimit(1)
        }
        .opacity(isBeingDragged ? 0.35 : 1)
        .rotationEffect(.degrees(wiggle ? 1.5 + phase : -(1.5 + phase)))
        .animation(.easeInOut(duration: 0.16).repeatForever(autoreverses: true), value: wiggle)
        .contentShape(Rectangle())
        .draggable(item.rawValue) {
            DragPreview(item: item)
                .onAppear { isBeingDragged = true }
                .onDisappear { isBeingDragged = false }
        }
        .dropDestination(for: String.self) { payload, _ in
            guard let raw = payload.first,
                  let dragged = MenuItem(rawValue: raw),
                  dragged != item else {
                isTargeted = false
                return false
            }
            withAnimation(.spring(response: 0.35, dampingFraction: 0.75)) {
                prefs.swap(dragged, item)
            }
            UIImpactFeedbackGenerator(style: .medium).impactOccurred()
            isTargeted = false
            return true
        } isTargeted: { hovering in
            withAnimation(.easeOut(duration: 0.12)) { isTargeted = hovering }
            if hovering {
                UISelectionFeedbackGenerator().selectionChanged()
            }
        }
    }

    private var tileBackground: Color {
        isTargeted ? Color.accentColor.opacity(0.25) : Color(.secondarySystemGroupedBackground)
    }
}

private struct DragPreview: View {
    let item: MenuItem
    var body: some View {
        VStack(spacing: 8) {
            Image(systemName: item.sfSymbol)
                .font(.system(size: 28))
                .frame(width: 60, height: 60)
                .background(Color(.systemBackground))
                .foregroundStyle(.primary)
                .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
                .shadow(radius: 10, y: 4)
            Text(item.label).font(.caption)
        }
        .padding(4)
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

                Section {
                    NavigationLink {
                        SettingsView()
                    } label: {
                        Label("Settings", systemImage: "gear")
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
