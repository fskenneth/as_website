//
//  TaskBoardView.swift
//  Astra Staging Portal
//
//  Staging Task Board — cards grouped by date, milestone chips per staging.
//  Mirrors Zoho's Staging_Task_Board and the FastHTML webapp's head banner:
//  title with "Task Board" accent, date-range preset button showing live count,
//  "My tasks" toggle, and a unified search field. Date presets map to the
//  existing /api/v1/tasks/board `period` parameter; search filters client-side
//  across address, people, dates, and notes.
//

import SwiftUI

enum TaskPeriod: String, CaseIterable, Identifiable {
    case today, week, all
    var id: String { rawValue }
    var apiValue: String { rawValue }

    /// Phrase used in the banner after the count, e.g. "24 stagings · this week".
    var phrase: String {
        switch self {
        case .today: return "today"
        case .week:  return "this week"
        case .all:   return "all time"
        }
    }

    var menuLabel: String {
        switch self {
        case .today: return "Today"
        case .week:  return "This Week"
        case .all:   return "All Time"
        }
    }
}

struct TaskBoardView: View {
    @Environment(AuthStore.self) private var auth
    @State private var period: TaskPeriod = .week
    @State private var mine: Bool = false
    @State private var search: String = ""
    @State private var searchOpen: Bool = false
    @FocusState private var searchFocused: Bool
    @State private var stagings: [Staging] = []
    @State private var isLoading = false
    @State private var error: String?
    @State private var serverToday: String = ""

    /// Accent used for the "Task Board" word, count, and active toggle — mirrors
    /// the webapp's rose accent (--accent #e11d48).
    private static let accent = Color(red: 225/255, green: 29/255, blue: 72/255)

    var body: some View {
        VStack(spacing: 0) {
            headerBanner
            Divider().opacity(0.3)
            content
        }
        .background(Color(.systemBackground))
        .task { await load() }
    }

    // MARK: - Header Banner

    private var headerBanner: some View {
        VStack(alignment: .leading, spacing: 10) {
            titleRow
            controlsRow
            if searchOpen || !search.isEmpty {
                searchField
                    .transition(.opacity.combined(with: .move(edge: .top)))
            }
        }
        .padding(.horizontal, 16)
        .padding(.top, 10)
        .padding(.bottom, 12)
        .background(Color(.systemBackground))
        .animation(.easeInOut(duration: 0.18), value: searchOpen)
    }

    private var titleRow: some View {
        HStack(spacing: 0) {
            Text("Staging ")
                .font(.title2.weight(.bold))
                .foregroundStyle(Color.primary)
            Text("Task Board")
                .font(.title2.weight(.bold))
                .foregroundStyle(Self.accent)
            Spacer(minLength: 0)
        }
    }

    private var controlsRow: some View {
        HStack(spacing: 8) {
            rangeButton
            mineButton
            searchToggleButton
            Spacer(minLength: 0)
        }
    }

    /// Magnifying-glass icon that expands/collapses the search field.
    /// If there's a query already, tapping won't collapse — the field stays
    /// visible until the user clears it.
    private var searchToggleButton: some View {
        Button {
            if searchOpen && search.isEmpty {
                searchOpen = false
                searchFocused = false
            } else {
                searchOpen = true
                // Delay focus so the field is mounted before becoming first responder.
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.05) {
                    searchFocused = true
                }
            }
        } label: {
            Image(systemName: "magnifyingglass")
                .font(.footnote)
                .padding(.horizontal, 12)
                .padding(.vertical, 8)
                .foregroundStyle(searchOpen || !search.isEmpty ? Self.accent : Color.primary)
                .background(
                    (searchOpen || !search.isEmpty)
                        ? Self.accent.opacity(0.12)
                        : Color(.secondarySystemBackground)
                )
                .clipShape(Capsule())
                .overlay(
                    Capsule().strokeBorder(
                        (searchOpen || !search.isEmpty) ? Self.accent : Color(.separator).opacity(0.5),
                        lineWidth: (searchOpen || !search.isEmpty) ? 1 : 0.5
                    )
                )
        }
        .buttonStyle(.plain)
        .accessibilityLabel(searchOpen ? "Close search" : "Open search")
    }

    private var rangeButton: some View {
        Menu {
            ForEach(TaskPeriod.allCases) { p in
                Button {
                    if period != p {
                        period = p
                        Task { await load() }
                    }
                } label: {
                    if period == p {
                        Label(p.menuLabel, systemImage: "checkmark")
                    } else {
                        Text(p.menuLabel)
                    }
                }
            }
        } label: {
            HStack(spacing: 6) {
                Image(systemName: "calendar")
                    .font(.footnote)
                (
                    Text("\(filteredStagings.count)")
                        .foregroundStyle(Self.accent)
                        .fontWeight(.semibold)
                    + Text(" stagings ")
                        .foregroundStyle(Color.primary)
                    + Text("· ")
                        .foregroundStyle(Color.secondary)
                    + Text(period.phrase)
                        .foregroundStyle(Color.primary)
                )
                .font(.subheadline)
                .lineLimit(1)
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .background(Color(.secondarySystemBackground))
            .clipShape(Capsule())
            .overlay(Capsule().strokeBorder(Color(.separator).opacity(0.5), lineWidth: 0.5))
            .foregroundStyle(Color.primary)
        }
    }

    private var mineButton: some View {
        Button {
            mine.toggle()
            Task { await load() }
        } label: {
            HStack(spacing: 4) {
                Image(systemName: "person")
                    .font(.footnote)
                Text("My tasks")
                    .font(.subheadline)
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .foregroundStyle(mine ? Self.accent : Color.primary)
            .background(mine ? Self.accent.opacity(0.12) : Color(.secondarySystemBackground))
            .clipShape(Capsule())
            .overlay(
                Capsule().strokeBorder(
                    mine ? Self.accent : Color(.separator).opacity(0.5),
                    lineWidth: mine ? 1 : 0.5
                )
            )
        }
        .buttonStyle(.plain)
    }

    private var searchField: some View {
        HStack(spacing: 8) {
            Image(systemName: "magnifyingglass")
                .font(.footnote)
                .foregroundStyle(.secondary)
            TextField("Search address, person, date, notes", text: $search)
                .textFieldStyle(.plain)
                .font(.subheadline)
                .autocorrectionDisabled()
                .textInputAutocapitalization(.never)
                .submitLabel(.search)
                .lineLimit(1)
                .focused($searchFocused)
            Button {
                search = ""
                searchOpen = false
                searchFocused = false
            } label: {
                Image(systemName: "xmark.circle.fill")
                    .foregroundStyle(.secondary)
            }
            .buttonStyle(.plain)
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 9)
        .background(Color(.secondarySystemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))
    }

    // MARK: - Content

    @ViewBuilder
    private var content: some View {
        if isLoading && stagings.isEmpty {
            ProgressView("Loading...").frame(maxWidth: .infinity, maxHeight: .infinity)
        } else if let error, stagings.isEmpty {
            errorState(error)
        } else if filteredStagings.isEmpty {
            emptyState
        } else {
            listView
        }
    }

    private var listView: some View {
        List {
            ForEach(groupedByDate(), id: \.0) { (dateKey, group) in
                Section {
                    ForEach(group) { staging in
                        StagingCard(
                            staging: staging,
                            serverToday: serverToday,
                            onMilestoneToggle: { field, currentlyDone in
                                await toggleMilestone(stagingId: staging.id, field: field, currentlyDone: currentlyDone)
                            }
                        )
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
            Image(systemName: search.isEmpty ? "tray" : "magnifyingglass")
                .font(.system(size: 48))
                .foregroundStyle(.secondary)
            Text(search.isEmpty ? "No stagings for this period" : "No stagings match your search")
                .font(.headline)
            Text(search.isEmpty
                 ? "Try a different date range or toggle My tasks off."
                 : "Try a wider range, clear the search, or toggle My tasks off.")
                .font(.footnote)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 24)
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

    // MARK: - Filtering

    /// Client-side search over the fields the webapp banner advertises:
    /// address, person, date, notes. Space-separated tokens are AND-matched.
    private var filteredStagings: [Staging] {
        let query = search.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        guard !query.isEmpty else { return stagings }
        let tokens = query.split(whereSeparator: { $0.isWhitespace }).map(String.init)

        return stagings.filter { s in
            let people = (s.stagers + s.staging_movers + s.destaging_movers)
                .compactMap { $0.name }
                .joined(separator: " ")
            let parts: [String?] = [
                s.address, s.name, s.staging_date, s.destaging_date,
                s.property_type, s.occupancy, s.staging_type, s.status,
                s.general_notes, s.moving_instructions, s.mls,
                s.customer.fullName, s.customer.email, s.customer.phone,
                s.staging_eta, s.destaging_eta, people,
            ]
            let haystack = parts.compactMap { $0 }.joined(separator: " ").lowercased()
            return tokens.allSatisfy { haystack.contains($0) }
        }
    }

    private func groupedByDate() -> [(String, [Staging])] {
        let grouped = Dictionary(grouping: filteredStagings) { $0.staging_date ?? "—" }
        return grouped.sorted { a, b in
            // Upcoming-leaning presets sort ascending; "all time" falls back
            // to ascending too since there's no single natural direction.
            a.key < b.key
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

    // MARK: - Load / mutate

    private func load() async {
        guard let token = auth.token else { return }
        isLoading = true
        error = nil
        defer { isLoading = false }
        do {
            let resp = try await APIClient.shared.taskBoard(period: period.apiValue, mine: mine, token: token)
            stagings = resp.stagings
            serverToday = resp.today
        } catch let APIError.badStatus(code, _) where code == 401 {
            await auth.logout()
        } catch {
            self.error = error.localizedDescription
        }
    }

    fileprivate func toggleMilestone(stagingId: String, field: String, currentlyDone: Bool) async {
        guard let token = auth.token else { return }
        do {
            _ = try await APIClient.shared.setMilestone(
                stagingId: stagingId, field: field, done: !currentlyDone, token: token
            )
            await load()
        } catch let APIError.badStatus(code, _) where code == 401 {
            await auth.logout()
        } catch {
            self.error = error.localizedDescription
        }
    }
}

/// Milestone definitions kept alongside the view so the field→label mapping lives in one place.
struct MilestoneDef {
    let label: String
    let field: String   // Zoho column name (must match server-side allowlist)
}

let MILESTONE_DEFS: [MilestoneDef] = [
    MilestoneDef(label: "Design",  field: "Design_Items_Matched_Date"),
    MilestoneDef(label: "Before",  field: "Before_Picture_Upload_Date"),
    MilestoneDef(label: "After",   field: "After_Picture_Upload_Date"),
    MilestoneDef(label: "Packing", field: "Staging_Accessories_Packing_Finish_Date"),
    MilestoneDef(label: "Setup",   field: "Staging_Furniture_Design_Finish_Date"),
    MilestoneDef(label: "WA",      field: "WhatsApp_Group_Created_Date"),
]

extension StagingMilestones {
    func milestone(for field: String) -> Milestone {
        switch field {
        case "Design_Items_Matched_Date": return design
        case "Before_Picture_Upload_Date": return before_pictures
        case "After_Picture_Upload_Date": return after_pictures
        case "Staging_Accessories_Packing_Finish_Date": return packing
        case "Staging_Furniture_Design_Finish_Date": return setup
        case "WhatsApp_Group_Created_Date": return whatsapp
        default: return Milestone(done: false, date: nil)
        }
    }
}

// MARK: - Staging Card

private struct StagingCard: View {
    let staging: Staging
    let serverToday: String
    let onMilestoneToggle: (String, Bool) async -> Void  // (field, currentlyDone)
    @State private var expanded = false
    @State private var togglingField: String?

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
                ForEach(MILESTONE_DEFS, id: \.field) { def in
                    let m = staging.milestones.milestone(for: def.field)
                    MilestoneChip(
                        label: def.label,
                        m: m,
                        busy: togglingField == def.field,
                        onTap: {
                            Task {
                                togglingField = def.field
                                await onMilestoneToggle(def.field, m.done)
                                togglingField = nil
                            }
                        }
                    )
                }
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
    var busy: Bool = false
    var onTap: (() -> Void)? = nil
    var body: some View {
        Button(action: { onTap?() }) {
            HStack(spacing: 4) {
                if busy {
                    ProgressView().scaleEffect(0.6).frame(width: 12, height: 12)
                } else {
                    Image(systemName: m.done ? "checkmark.circle.fill" : "circle")
                        .font(.caption)
                }
                Text(label).font(.caption2)
                if let d = m.date { Text(shortDate(d)).font(.caption2).opacity(0.8) }
            }
            .padding(.horizontal, 8).padding(.vertical, 4)
            .background(m.done ? Color.green.opacity(0.18) : Color(.tertiarySystemGroupedBackground))
            .foregroundStyle(m.done ? Color.green : Color.secondary)
            .clipShape(Capsule())
        }
        .buttonStyle(.plain)
        .disabled(busy || onTap == nil)
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
