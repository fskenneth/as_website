//
//  TaskBoardView.swift
//  Astra Staging Portal
//
//  Staging Task Board — cards grouped by date, milestone chips per staging.
//  Mirrors the functional elements of Zoho's Staging_Task_Board: period filter
//  (Today/Week/Upcoming/All), "My Tasks" toggle, and per-staging milestone state
//  (Design / Pictures / Packing / Setup) driven by date-field presence.
//

import SwiftUI

enum TaskPeriod: String, CaseIterable, Identifiable {
    case today, week, upcoming, past, all
    var id: String { rawValue }
    var label: String {
        switch self {
        case .today: return "Today"
        case .week: return "Week"
        case .upcoming: return "Upcoming"
        case .past: return "Past"
        case .all: return "All"
        }
    }
}

struct TaskBoardView: View {
    @Environment(AuthStore.self) private var auth
    @State private var period: TaskPeriod = .upcoming
    @State private var mine: Bool = false
    @State private var stagings: [Staging] = []
    @State private var isLoading = false
    @State private var error: String?
    @State private var serverToday: String = ""

    var body: some View {
        NavigationStack {
            Group {
                if isLoading && stagings.isEmpty {
                    ProgressView("Loading...").frame(maxWidth: .infinity, maxHeight: .infinity)
                } else if let error, stagings.isEmpty {
                    errorState(error)
                } else if stagings.isEmpty {
                    emptyState
                } else {
                    listView
                }
            }
            .navigationTitle("Task Board")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Toggle(isOn: $mine) { Text("Mine").font(.subheadline) }
                        .toggleStyle(.button)
                        .onChange(of: mine) { _, _ in Task { await load() } }
                }
            }
            .safeAreaInset(edge: .top, spacing: 0) {
                periodPicker
                    .padding(.horizontal)
                    .padding(.vertical, 8)
                    .background(.ultraThinMaterial)
            }
            .task { await load() }
        }
    }

    private var periodPicker: some View {
        Picker("Period", selection: $period) {
            ForEach(TaskPeriod.allCases) { p in
                Text(p.label).tag(p)
            }
        }
        .pickerStyle(.segmented)
        .onChange(of: period) { _, _ in Task { await load() } }
    }

    private var listView: some View {
        List {
            ForEach(groupedByDate(), id: \.0) { (dateKey, group) in
                Section {
                    ForEach(group) { staging in
                        StagingCard(staging: staging, serverToday: serverToday)
                            .listRowSeparator(.hidden)
                            .listRowInsets(EdgeInsets(top: 6, leading: 12, bottom: 6, trailing: 12))
                    }
                } header: {
                    Text(dateKey).font(.caption).foregroundStyle(.secondary)
                }
            }
        }
        .listStyle(.plain)
        .refreshable { await load() }
    }

    private var emptyState: some View {
        VStack(spacing: 12) {
            Image(systemName: "tray")
                .font(.system(size: 48))
                .foregroundStyle(.secondary)
            Text("No stagings for this period").font(.headline)
            Text("Try a different period or toggle Mine.")
                .font(.footnote)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }

    private func errorState(_ message: String) -> some View {
        VStack(spacing: 12) {
            Text("Couldn't load").font(.headline)
            Text(message).font(.footnote).foregroundStyle(.secondary).multilineTextAlignment(.center)
            Button("Retry") { Task { await load() } }
        }
        .padding()
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }

    private func groupedByDate() -> [(String, [Staging])] {
        let grouped = Dictionary(grouping: stagings) { $0.staging_date ?? "—" }
        return grouped.sorted { a, b in
            // Sort upcoming ascending, others descending
            if period == .past || period == .all { return a.key > b.key }
            return a.key < b.key
        }.map { (prettyDate($0.key), $0.value) }
    }

    private func prettyDate(_ iso: String) -> String {
        guard iso != "—", let d = dateFromISO(iso) else { return iso }
        let fmt = DateFormatter()
        fmt.dateFormat = "EEE, MMM d, yyyy"
        return fmt.string(from: d)
    }

    private func dateFromISO(_ iso: String) -> Date? {
        let fmt = DateFormatter()
        fmt.dateFormat = "yyyy-MM-dd"
        fmt.timeZone = TimeZone(identifier: "America/Toronto")
        return fmt.date(from: iso)
    }

    private func load() async {
        guard let token = auth.token else { return }
        isLoading = true
        error = nil
        defer { isLoading = false }
        do {
            let resp = try await APIClient.shared.taskBoard(period: period.rawValue, mine: mine, token: token)
            stagings = resp.stagings
            serverToday = resp.today
        } catch let APIError.badStatus(code, _) where code == 401 {
            await auth.logout()
        } catch {
            self.error = error.localizedDescription
        }
    }
}

// MARK: - Staging Card

private struct StagingCard: View {
    let staging: Staging
    let serverToday: String
    @State private var expanded = false

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            header
            addressRow
            if !staging.stagers.isEmpty || !staging.staging_movers.isEmpty {
                peopleSection
            }
            milestonesRow
            if expanded { expandedDetails }
            Button { expanded.toggle() } label: {
                HStack {
                    Text(expanded ? "Less" : "More")
                    Image(systemName: expanded ? "chevron.up" : "chevron.down")
                }
                .font(.caption)
                .foregroundStyle(.secondary)
                .frame(maxWidth: .infinity)
                .padding(.top, 4)
            }
            .buttonStyle(.plain)
        }
        .padding(14)
        .background(cardBackground)
        .overlay(RoundedRectangle(cornerRadius: 12).strokeBorder(borderColor, lineWidth: borderWidth))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }

    private var isToday: Bool {
        staging.staging_date == serverToday
    }

    private var cardBackground: Color {
        isToday ? Color.yellow.opacity(0.18) : Color(.secondarySystemGroupedBackground)
    }

    private var borderColor: Color {
        isToday ? Color.orange.opacity(0.5) : Color(.separator).opacity(0.4)
    }

    private var borderWidth: CGFloat { isToday ? 1.5 : 0.5 }

    private var header: some View {
        HStack(spacing: 8) {
            if let eta = staging.staging_eta, !eta.isEmpty {
                Label(eta, systemImage: "clock")
                    .font(.caption).fontWeight(.medium)
                    .foregroundStyle(.secondary)
            }
            Spacer()
            if let occ = staging.occupancy, !occ.isEmpty {
                Badge(occ, color: occ.lowercased() == "vacant" ? .orange : .blue)
            }
            if let t = staging.staging_type, !t.isEmpty, t != "Regular" {
                Badge(t, color: .purple)
            }
            if let st = staging.status, !st.isEmpty {
                Badge(st, color: status(st))
            }
        }
    }

    private func status(_ s: String) -> Color {
        switch s.lowercased() {
        case "active": return .green
        case "inquired": return .gray
        case "inactive": return .secondary
        default: return .gray
        }
    }

    private var addressRow: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(staging.address ?? staging.name ?? "Untitled")
                .font(.body).fontWeight(.semibold)
            if let p = staging.property_type, !p.isEmpty {
                Text(p).font(.caption).foregroundStyle(.secondary)
            }
        }
    }

    private var peopleSection: some View {
        VStack(alignment: .leading, spacing: 6) {
            if !staging.stagers.isEmpty {
                PeopleRow(label: "Stager", icon: "paintbrush", people: staging.stagers)
            }
            if !staging.staging_movers.isEmpty {
                PeopleRow(label: "Movers", icon: "truck.box", people: staging.staging_movers)
            }
        }
    }

    private var milestonesRow: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 6) {
                MilestoneChip(label: "Design", m: staging.milestones.design)
                MilestoneChip(label: "Before", m: staging.milestones.before_pictures)
                MilestoneChip(label: "After", m: staging.milestones.after_pictures)
                MilestoneChip(label: "Packing", m: staging.milestones.packing)
                MilestoneChip(label: "Setup", m: staging.milestones.setup)
                MilestoneChip(label: "WA", m: staging.milestones.whatsapp)
            }
        }
    }

    @ViewBuilder
    private var expandedDetails: some View {
        Divider().padding(.vertical, 4)
        VStack(alignment: .leading, spacing: 10) {
            KV("Customer", staging.customer.fullName)
            if let p = staging.customer.phone, !p.isEmpty { KV("Phone", p) }
            if let e = staging.customer.email, !e.isEmpty { KV("Email", e) }

            if staging.fees.total > 0 || staging.fees.owing > 0 {
                HStack(spacing: 16) {
                    FeeBlock(label: "Fee", amount: staging.fees.total)
                    FeeBlock(label: "Paid", amount: staging.fees.paid)
                    FeeBlock(label: "Owing", amount: staging.fees.owing, highlight: staging.fees.owing > 0)
                }
            }

            if let dd = staging.destaging_date, !dd.isEmpty {
                KV("Destaging", dd + (staging.destaging_eta.map { " · \($0)" } ?? ""))
            }

            if let inst = staging.moving_instructions, !inst.isEmpty {
                NoteBlock(label: "Moving Instructions", text: inst, color: .blue)
            }
            if let notes = staging.general_notes, !notes.isEmpty {
                NoteBlock(label: "General Notes", text: notes, color: .secondary)
            }

            if let mls = staging.mls, !mls.isEmpty {
                KV("MLS", mls)
            }
        }
    }
}

// MARK: - Subviews

private struct Badge: View {
    let text: String
    let color: Color
    init(_ text: String, color: Color) { self.text = text; self.color = color }
    var body: some View {
        Text(text)
            .font(.caption2).fontWeight(.medium)
            .padding(.horizontal, 8).padding(.vertical, 3)
            .background(color.opacity(0.18))
            .foregroundStyle(color)
            .clipShape(Capsule())
    }
}

private struct PeopleRow: View {
    let label: String
    let icon: String
    let people: [Person]
    var body: some View {
        HStack(alignment: .top, spacing: 6) {
            Image(systemName: icon)
                .font(.caption)
                .foregroundStyle(.secondary)
                .frame(width: 16)
            Text(label)
                .font(.caption).foregroundStyle(.secondary)
                .frame(width: 48, alignment: .leading)
            Text(people.compactMap { $0.name }.joined(separator: ", "))
                .font(.caption)
                .lineLimit(2)
            Spacer(minLength: 0)
        }
    }
}

private struct MilestoneChip: View {
    let label: String
    let m: Milestone
    var body: some View {
        HStack(spacing: 4) {
            Image(systemName: m.done ? "checkmark.circle.fill" : "circle")
                .font(.caption)
            Text(label).font(.caption2)
            if let d = m.date { Text(shortDate(d)).font(.caption2).foregroundStyle(.secondary) }
        }
        .padding(.horizontal, 8).padding(.vertical, 4)
        .background(m.done ? Color.green.opacity(0.18) : Color(.tertiarySystemGroupedBackground))
        .foregroundStyle(m.done ? Color.green : Color.secondary)
        .clipShape(Capsule())
    }

    private func shortDate(_ iso: String) -> String {
        let f = DateFormatter(); f.dateFormat = "yyyy-MM-dd"
        guard let d = f.date(from: iso) else { return iso }
        let out = DateFormatter(); out.dateFormat = "MMM d"
        return out.string(from: d)
    }
}

private struct KV: View {
    let key: String
    let value: String
    init(_ k: String, _ v: String) { key = k; value = v }
    var body: some View {
        HStack(alignment: .top) {
            Text(key).font(.caption).foregroundStyle(.secondary).frame(width: 80, alignment: .leading)
            Text(value).font(.caption).frame(maxWidth: .infinity, alignment: .leading)
        }
    }
}

private struct FeeBlock: View {
    let label: String
    let amount: Double
    var highlight: Bool = false
    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(label).font(.caption2).foregroundStyle(.secondary)
            Text(formatted(amount))
                .font(.callout).fontWeight(.semibold)
                .foregroundStyle(highlight ? .red : .primary)
        }
    }
    private func formatted(_ a: Double) -> String {
        let f = NumberFormatter(); f.numberStyle = .currency; f.currencyCode = "CAD"; f.maximumFractionDigits = 0
        return f.string(from: NSNumber(value: a)) ?? "$\(Int(a))"
    }
}

private struct NoteBlock: View {
    let label: String
    let text: String
    let color: Color
    var body: some View {
        VStack(alignment: .leading, spacing: 3) {
            Text(label).font(.caption2).foregroundStyle(.secondary)
            Text(text)
                .font(.caption)
                .fixedSize(horizontal: false, vertical: true)
                .padding(8)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(color.opacity(0.08))
                .cornerRadius(6)
        }
    }
}
