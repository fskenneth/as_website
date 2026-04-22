//
//  MenuPreferences.swift
//  Astra Staging Portal
//
//  Persists the user's menu ordering across launches via UserDefaults. The
//  first 4 visible items (after role filtering) become the dock; the rest live
//  under "More". Any new MenuItem added in a future build is appended at the
//  end so existing users see it without losing their customization.
//

import Foundation
import Observation

@Observable
@MainActor
final class MenuPreferences {
    var order: [MenuItem]

    private let key = "menu_order_v1"
    private let defaults = UserDefaults.standard

    init() {
        if let raw = UserDefaults.standard.array(forKey: "menu_order_v1") as? [String] {
            let parsed = raw.compactMap { MenuItem(rawValue: $0) }
            let missing = MenuItem.allCases.filter { !parsed.contains($0) }
            self.order = parsed + missing
        } else {
            self.order = MenuItem.defaultOrder
        }
    }

    private func save() {
        defaults.set(order.map { $0.rawValue }, forKey: key)
    }

    /// Swap two items in place. Used by the drag-to-reorder UI: drop A on B → A and B trade slots.
    func swap(_ a: MenuItem, _ b: MenuItem) {
        guard a != b,
              let i = order.firstIndex(of: a),
              let j = order.firstIndex(of: b) else { return }
        order.swapAt(i, j)
        save()
    }

    func visibleItems(for roleLevel: Int) -> [MenuItem] {
        order.filter { $0.minRoleLevel <= roleLevel }
    }

    func dockItems(for roleLevel: Int) -> [MenuItem] {
        Array(visibleItems(for: roleLevel).prefix(4))
    }

    func overflowItems(for roleLevel: Int) -> [MenuItem] {
        Array(visibleItems(for: roleLevel).dropFirst(4))
    }
}
