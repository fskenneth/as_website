//
//  ItemPickerSheet.swift
//  Astra Staging Portal
//
//  Modal item picker for the consultation flow. Used for both
//  "Add New Items" (with live pricing + area cap display) and
//  "Remove Existing Items" (no prices; quantity only).
//  Tap a row to add +1; use the inline +/– controls to step.
//

import SwiftUI

struct ItemPickerSheet: View {
    let title: String
    let action: String // "add" or "remove"
    let catalog: [QuoteCatalogItem]
    let areaQuote: QuoteArea?
    let areaName: String
    let onTap: (String, Int) -> Void
    let onDone: () -> Void

    private var currentQty: [String: Int] {
        let src = action == "add"
            ? (areaQuote?.add_items ?? [])
            : (areaQuote?.remove_items ?? [])
        return Dictionary(uniqueKeysWithValues: src.map { ($0.item_name, $0.quantity) })
    }

    var body: some View {
        NavigationStack {
            VStack(alignment: .leading, spacing: 0) {
                if action == "add", let aq = areaQuote {
                    HStack(spacing: 12) {
                        Text("Items: $\(Int(aq.items_total))")
                            .font(.subheadline.weight(.semibold))
                        Text("Cap: $\(Int(aq.cap))")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                        Text("Charge: $\(Int(aq.effective))")
                            .font(.subheadline.weight(.semibold))
                            .foregroundStyle(.blue)
                    }
                    .padding(.horizontal, 16)
                    .padding(.vertical, 10)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(Color(.secondarySystemGroupedBackground))
                }

                List {
                    ForEach(catalog) { item in
                        let qty = currentQty[item.name] ?? 0
                        ItemPickerRow(
                            name: item.name,
                            showPrice: action == "add",
                            unitPrice: item.unit_price,
                            quantity: qty,
                            onTap: { onTap(item.name, +1) },
                            onMinus: { onTap(item.name, -1) },
                        )
                        .listRowInsets(EdgeInsets(top: 4, leading: 12, bottom: 4, trailing: 12))
                        .listRowBackground(
                            qty > 0
                                ? Color.blue.opacity(0.12)
                                : Color(.secondarySystemGroupedBackground),
                        )
                        .contentShape(Rectangle())
                        .onTapGesture { onTap(item.name, +1) }
                    }
                }
                .listStyle(.insetGrouped)
            }
            .navigationTitle(title)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Text(areaName).font(.caption).foregroundStyle(.secondary)
                }
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Done", action: onDone).bold()
                }
            }
        }
    }
}

private struct ItemPickerRow: View {
    let name: String
    let showPrice: Bool
    let unitPrice: Double
    let quantity: Int
    let onTap: () -> Void
    let onMinus: () -> Void

    var body: some View {
        HStack(spacing: 8) {
            VStack(alignment: .leading, spacing: 2) {
                Text(name).font(.subheadline.weight(.semibold))
                if showPrice {
                    Text("$\(Int(unitPrice)) ea")
                        .font(.caption2)
                        .foregroundStyle(.secondary)
                }
            }
            Spacer()
            if quantity > 0 {
                Button {
                    onMinus()
                } label: {
                    Image(systemName: "minus.circle.fill")
                        .font(.title3)
                        .foregroundStyle(.secondary)
                }
                .buttonStyle(.plain)

                Text("\(quantity)")
                    .font(.subheadline.bold())
                    .frame(minWidth: 28, minHeight: 28)
                    .background(Color.blue)
                    .foregroundStyle(.white)
                    .clipShape(Circle())
            }
            Button {
                onTap()
            } label: {
                Image(systemName: "plus.circle.fill")
                    .font(.title3)
                    .foregroundStyle(.blue)
            }
            .buttonStyle(.plain)
        }
        .padding(.vertical, 2)
    }
}
