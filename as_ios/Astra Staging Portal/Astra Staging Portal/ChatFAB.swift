//
//  ChatFAB.swift
//  Astra Staging Portal
//
//  Always-visible floating chat button. Reads unread count straight from
//  the app-scoped ChatStore so the badge tracks SSE in real time without
//  a separate poll loop.
//

import SwiftUI

struct ChatFAB: View {
    let onTap: () -> Void
    @Environment(ChatStore.self) private var store

    private var unreadCount: Int {
        store.conversations.reduce(0) { $0 + ($1.unread_count ?? 0) }
    }

    var body: some View {
        Button(action: onTap) {
            ZStack(alignment: .topTrailing) {
                Circle()
                    .fill(Color.accentColor)
                    .frame(width: 56, height: 56)
                    .shadow(color: Color.black.opacity(0.25), radius: 6, x: 0, y: 4)
                    .overlay(
                        Image(systemName: "bubble.left.and.bubble.right.fill")
                            .font(.system(size: 22, weight: .semibold))
                            .foregroundStyle(.white)
                    )
                if unreadCount > 0 {
                    Text(unreadCount > 99 ? "99+" : "\(unreadCount)")
                        .font(.system(size: 11, weight: .bold))
                        .foregroundStyle(.white)
                        .padding(.horizontal, 6).padding(.vertical, 2)
                        .background(Capsule().fill(Color.red))
                        .overlay(Capsule().stroke(Color.white, lineWidth: 2))
                        .offset(x: 6, y: -4)
                }
            }
        }
        .buttonStyle(.plain)
        .accessibilityLabel("Chat")
        .accessibilityValue(unreadCount > 0 ? "\(unreadCount) unread" : "")
    }
}

/// Wraps `ChatFAB` with a drag gesture. On release the FAB snaps to the
/// nearest horizontal edge (left or right); vertical position is free
/// within the safe area. Both axes are persisted in AppSettings so
/// position survives across launches.
struct DraggableChatFAB: View {
    let onTap: () -> Void

    @State private var settings = AppSettings.shared
    @State private var dragOffset: CGSize = .zero
    @State private var isDragging: Bool = false

    private let buttonSize: CGFloat = 56
    private let edgeInset: CGFloat = 14
    private let minTopInset: CGFloat = 60   // below the status bar / nav title
    private let minBottomInset: CGFloat = 60 // above the dock bar

    var body: some View {
        GeometryReader { geo in
            let usableHeight = max(0, geo.size.height - minTopInset - minBottomInset - buttonSize)
            let baseY = minTopInset + usableHeight * settings.chatFabYFraction
            let baseX: CGFloat = settings.chatFabSide == .right
                ? geo.size.width - buttonSize - edgeInset
                : edgeInset

            ChatFAB(onTap: onTap)
                .frame(width: buttonSize, height: buttonSize)
                .scaleEffect(isDragging ? 1.08 : 1.0)
                .animation(.spring(response: 0.25, dampingFraction: 0.75), value: isDragging)
                .position(
                    x: baseX + buttonSize / 2 + dragOffset.width,
                    y: baseY + buttonSize / 2 + dragOffset.height,
                )
                .gesture(
                    DragGesture(minimumDistance: 4)
                        .onChanged { value in
                            isDragging = true
                            dragOffset = value.translation
                        }
                        .onEnded { value in
                            isDragging = false
                            // Project final center coordinates within the geometry.
                            let centerX = baseX + buttonSize / 2 + value.translation.width
                            let centerY = baseY + buttonSize / 2 + value.translation.height

                            let newSide: ChatFabSide = (centerX < geo.size.width / 2) ? .left : .right
                            let clampedY = max(minTopInset + buttonSize / 2,
                                               min(geo.size.height - minBottomInset - buttonSize / 2, centerY))
                            let newFraction = usableHeight > 0
                                ? Double((clampedY - minTopInset - buttonSize / 2) / usableHeight)
                                : 0.5

                            withAnimation(.spring(response: 0.4, dampingFraction: 0.8)) {
                                settings.chatFabSide = newSide
                                settings.chatFabYFraction = max(0, min(1, newFraction))
                                dragOffset = .zero
                            }

                            let haptic = UIImpactFeedbackGenerator(style: .light)
                            haptic.impactOccurred()
                        }
                )
        }
        .ignoresSafeArea(.keyboard)  // FAB stays put when the keyboard rises
    }
}

/// Top-of-screen banner that pops in when ChatStore.toast is set.
/// Auto-dismisses after a few seconds; tapping it jumps to the chat tab.
struct ChatToastBanner: View {
    @Environment(ChatStore.self) private var store
    let onTap: () -> Void

    @State private var dismissTask: Task<Void, Never>?

    var body: some View {
        let toast = store.toast
        Group {
            if let t = toast {
                Button {
                    onTap()
                    store.toast = nil
                } label: {
                    HStack(alignment: .top, spacing: 12) {
                        Image(systemName: "bubble.left.fill")
                            .font(.system(size: 14, weight: .bold))
                            .foregroundStyle(.white)
                            .frame(width: 32, height: 32)
                            .background(Circle().fill(Color.accentColor))
                        VStack(alignment: .leading, spacing: 2) {
                            Text(t.title)
                                .font(.system(size: 14, weight: .semibold))
                                .foregroundStyle(.primary)
                            Text(t.body)
                                .font(.system(size: 13))
                                .foregroundStyle(.secondary)
                                .lineLimit(2)
                                .multilineTextAlignment(.leading)
                        }
                        Spacer(minLength: 0)
                    }
                    .padding(12)
                    .background(
                        RoundedRectangle(cornerRadius: 14, style: .continuous)
                            .fill(Color(.systemBackground))
                            .shadow(color: .black.opacity(0.25), radius: 14, x: 0, y: 6)
                    )
                    .padding(.horizontal, 12)
                }
                .buttonStyle(.plain)
            } else {
                Color.clear.frame(height: 0)
            }
        }
        .frame(maxWidth: .infinity, alignment: .top)
        .onChange(of: toast?.id) { _, newId in
            dismissTask?.cancel()
            guard newId != nil else { return }
            dismissTask = Task {
                try? await Task.sleep(nanoseconds: 4_500_000_000)
                if !Task.isCancelled { store.toast = nil }
            }
        }
    }
}
