//
//  MenuItem.swift
//  Astra Staging Portal
//
//  All possible menu destinations. Order in `defaultOrder` is the seed order
//  for new users; once they customize, `MenuPreferences` persists their order.
//

import Foundation

enum MenuItem: String, CaseIterable, Identifiable, Codable {
    case tasks
    case items
    case me
    case consultation
    case sales
    case hr

    var id: String { rawValue }

    var label: String {
        switch self {
        case .tasks:        return "Tasks"
        case .items:        return "Items"
        case .me:           return "Me"
        case .consultation: return "Consultation"
        case .sales:        return "Sales"
        case .hr:           return "HR"
        }
    }

    var sfSymbol: String {
        switch self {
        case .tasks:        return "checklist"
        case .items:        return "shippingbox"
        case .me:           return "person.circle"
        case .consultation: return "person.2.wave.2"
        case .sales:        return "briefcase"
        case .hr:           return "building.2"
        }
    }

    /// Min user.roleLevel required to see this item (1=execution, 2=manager, 3=owner).
    var minRoleLevel: Int {
        switch self {
        case .tasks, .items, .me, .consultation: return 1
        case .sales: return 2
        case .hr:    return 3
        }
    }

    static let defaultOrder: [MenuItem] = [.tasks, .items, .consultation, .me, .sales, .hr]
}
