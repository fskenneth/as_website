//
//  ChatView.swift
//  Astra Staging Portal
//
//  Internal team chat — phase 1.
//  Talks to /api/v1/chat/* on as_webapp; live updates via SSE
//  (URLSession.bytes line stream) so the same backend powers the
//  web + Android clients without per-platform plumbing.
//

import Foundation
import Observation
import PhotosUI
import SwiftUI

// MARK: - Models

struct ChatEmployee: Codable, Identifiable, Hashable {
    let id: Int
    let display_name: String
    let email: String
    let user_role: String
}

struct ChatEmployeesResponse: Codable {
    let employees: [ChatEmployee]
}

struct ChatConversation: Codable, Identifiable, Hashable {
    let id: Int
    let channel: String
    let kind: String
    let title: String
    let created_by: Int?
    let created_at: String?
    var last_message_at: String?
    var last_message_preview: String?
    var last_message_sender_id: Int?
    var unread_count: Int?
    var archived: Bool?
    var pinned_position: Int?

    var isGroup: Bool { kind == "group" }
    var isAnna: Bool { channel == "anna" }
}

struct ChatConversationsResponse: Codable {
    let conversations: [ChatConversation]
}

struct ChatMember: Codable, Identifiable, Hashable {
    let id: Int
    let display_name: String
    let email: String?
    let user_role: String?
    let role: String?
}

struct ChatConversationDetail: Codable, Hashable {
    let id: Int
    let channel: String
    let kind: String
    let title: String
    let members: [ChatMember]
}

struct ChatConversationDetailResponse: Codable {
    let conversation: ChatConversationDetail
}

struct ChatMessageSender: Codable, Hashable {
    let id: Int
    let display_name: String?
}

struct ChatReplyPreview: Codable, Hashable {
    let id: Int
    let sender_id: Int
    let sender_name: String
    let body: String
    let deleted: Bool
}

struct ChatReaction: Codable, Hashable, Identifiable {
    let emoji: String
    let count: Int
    let user_ids: [Int]
    var id: String { emoji }
}

struct ChatAttachment: Codable, Hashable, Identifiable {
    let id: Int
    let kind: String  // "photo" | "video" | "file"
    let mime_type: String?
    let size: Int?
    let original_name: String?
    let width: Int?
    let height: Int?
    let url: String

    var isPhoto: Bool { kind == "photo" }
    var isVideo: Bool { kind == "video" }
}

struct ChatMessage: Codable, Identifiable, Hashable {
    let id: Int
    let conversation_id: Int
    let sender_id: Int
    let body: String
    let kind: String
    let created_at: String?
    let edited_at: String?
    let deleted_at: String?
    let deleted: Bool?
    let reply_to: ChatReplyPreview?
    let reactions: [ChatReaction]?
    let attachments: [ChatAttachment]?
    let sender: ChatMessageSender?

    var isDeleted: Bool { deleted == true || deleted_at != nil }
}

struct ChatMessagesResponse: Codable {
    let messages: [ChatMessage]
}

struct ChatSendResponse: Codable {
    let message: ChatMessage
}

struct ChatCreateConversationResponse: Codable {
    let conversation: ChatConversationDetail
}

// MARK: - Service

@MainActor
final class ChatService {
    static let shared = ChatService()
    private var baseURL: URL { APIClient.shared.baseURL }
    private let decoder = JSONDecoder()

    private func req(_ path: String, method: String = "GET",
                     body: [String: Any]? = nil, token: String) -> URLRequest {
        var r = URLRequest(url: baseURL.appendingPathComponent(path))
        r.httpMethod = method
        r.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        if let body {
            r.setValue("application/json", forHTTPHeaderField: "Content-Type")
            r.httpBody = try? JSONSerialization.data(withJSONObject: body)
        }
        return r
    }

    private func send<T: Decodable>(_ r: URLRequest, _: T.Type) async throws -> T {
        let (data, resp) = try await URLSession.shared.data(for: r)
        let status = (resp as? HTTPURLResponse)?.statusCode ?? 0
        guard (200..<300).contains(status) else {
            throw APIError.badStatus(status, String(data: data, encoding: .utf8))
        }
        return try decoder.decode(T.self, from: data)
    }

    func employees(token: String) async throws -> [ChatEmployee] {
        try await send(req("/api/v1/chat/employees", token: token),
                       ChatEmployeesResponse.self).employees
    }

    func conversations(token: String) async throws -> [ChatConversation] {
        try await send(req("/api/v1/chat/conversations", token: token),
                       ChatConversationsResponse.self).conversations
    }

    func conversationDetail(id: Int, token: String) async throws -> ChatConversationDetail {
        try await send(req("/api/v1/chat/conversations/\(id)", token: token),
                       ChatConversationDetailResponse.self).conversation
    }

    func messages(conversationId: Int, limit: Int = 100, token: String) async throws -> [ChatMessage] {
        var comps = URLComponents(url: baseURL.appendingPathComponent("/api/v1/chat/conversations/\(conversationId)/messages"),
                                  resolvingAgainstBaseURL: false)!
        comps.queryItems = [URLQueryItem(name: "limit", value: String(limit))]
        var r = URLRequest(url: comps.url!)
        r.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        return try await send(r, ChatMessagesResponse.self).messages
    }

    func send(
        conversationId: Int,
        body: String,
        replyTo: Int? = nil,
        token: String,
    ) async throws -> ChatMessage {
        var payload: [String: Any] = ["body": body]
        if let replyTo { payload["reply_to_message_id"] = replyTo }
        return try await send(
            req("/api/v1/chat/conversations/\(conversationId)/messages",
                method: "POST", body: payload, token: token),
            ChatSendResponse.self
        ).message
    }

    func editMessage(messageId: Int, body: String, token: String) async throws -> ChatMessage {
        try await send(
            req("/api/v1/chat/messages/\(messageId)",
                method: "PATCH", body: ["body": body], token: token),
            ChatSendResponse.self
        ).message
    }

    func deleteMessage(messageId: Int, token: String) async throws -> ChatMessage {
        var r = URLRequest(url: baseURL.appendingPathComponent("/api/v1/chat/messages/\(messageId)"))
        r.httpMethod = "DELETE"
        r.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        return try await send(r, ChatSendResponse.self).message
    }

    func toggleReaction(messageId: Int, emoji: String, token: String) async throws -> ChatMessage {
        try await send(
            req("/api/v1/chat/messages/\(messageId)/reactions",
                method: "POST", body: ["emoji": emoji], token: token),
            ChatSendResponse.self
        ).message
    }

    /// Upload a single file as a new chat message. The server creates the
    /// message + attachment row in one step; SSE delivers the canonical
    /// hydrated message back to all participants.
    func uploadAttachment(
        conversationId: Int,
        body: String,
        replyTo: Int? = nil,
        fileURL: URL? = nil,
        fileData: Data? = nil,
        fileName: String,
        mimeType: String,
        token: String,
    ) async throws -> ChatMessage {
        let path = "/api/v1/chat/conversations/\(conversationId)/messages/upload"
        var r = URLRequest(url: baseURL.appendingPathComponent(path))
        r.httpMethod = "POST"
        r.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        r.timeoutInterval = 120
        let boundary = "----AstraChat-\(UUID().uuidString)"
        r.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")

        var data = Data()
        func appendField(_ name: String, _ value: String) {
            data.append("--\(boundary)\r\n".data(using: .utf8)!)
            data.append("Content-Disposition: form-data; name=\"\(name)\"\r\n\r\n".data(using: .utf8)!)
            data.append(value.data(using: .utf8)!)
            data.append("\r\n".data(using: .utf8)!)
        }
        if !body.isEmpty { appendField("body", body) }
        if let replyTo { appendField("reply_to_message_id", String(replyTo)) }
        let payload: Data
        if let fileData { payload = fileData }
        else if let fileURL { payload = try Data(contentsOf: fileURL) }
        else { throw APIError.transport(NSError(domain: "ChatService", code: -1)) }
        data.append("--\(boundary)\r\n".data(using: .utf8)!)
        data.append("Content-Disposition: form-data; name=\"file\"; filename=\"\(fileName)\"\r\n".data(using: .utf8)!)
        data.append("Content-Type: \(mimeType)\r\n\r\n".data(using: .utf8)!)
        data.append(payload)
        data.append("\r\n".data(using: .utf8)!)
        data.append("--\(boundary)--\r\n".data(using: .utf8)!)
        r.httpBody = data
        return try await send(r, ChatSendResponse.self).message
    }

    func markRead(conversationId: Int, messageId: Int?, token: String) async {
        var body: [String: Any] = [:]
        if let messageId { body["message_id"] = messageId }
        _ = try? await URLSession.shared.data(
            for: req("/api/v1/chat/conversations/\(conversationId)/read",
                     method: "POST", body: body, token: token))
    }

    func createDM(otherUserId: Int, token: String) async throws -> ChatConversationDetail {
        try await send(
            req("/api/v1/chat/conversations", method: "POST",
                body: ["kind": "dm", "user_id": otherUserId], token: token),
            ChatCreateConversationResponse.self
        ).conversation
    }

    func createGroup(title: String, userIds: [Int], token: String) async throws -> ChatConversationDetail {
        try await send(
            req("/api/v1/chat/conversations", method: "POST",
                body: ["kind": "group", "title": title, "user_ids": userIds], token: token),
            ChatCreateConversationResponse.self
        ).conversation
    }

    func archive(conversationId: Int, archived: Bool, token: String) async throws {
        let r = req(
            "/api/v1/chat/conversations/\(conversationId)/archive",
            method: "POST", body: ["archived": archived], token: token,
        )
        let (_, resp) = try await URLSession.shared.data(for: r)
        let status = (resp as? HTTPURLResponse)?.statusCode ?? 0
        guard (200..<300).contains(status) else { throw APIError.badStatus(status, nil) }
    }

    func reorder(ids: [Int], token: String) async throws {
        let r = req(
            "/api/v1/chat/conversations/reorder",
            method: "POST", body: ["ids": ids], token: token,
        )
        let (_, resp) = try await URLSession.shared.data(for: r)
        let status = (resp as? HTTPURLResponse)?.statusCode ?? 0
        guard (200..<300).contains(status) else { throw APIError.badStatus(status, nil) }
    }

    func delete(conversationId: Int, token: String) async throws {
        var r = URLRequest(url: baseURL.appendingPathComponent("/api/v1/chat/conversations/\(conversationId)"))
        r.httpMethod = "DELETE"
        r.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        let (_, resp) = try await URLSession.shared.data(for: r)
        let status = (resp as? HTTPURLResponse)?.statusCode ?? 0
        guard (200..<300).contains(status) else { throw APIError.badStatus(status, nil) }
    }
}

// MARK: - SSE client

/// SSE consumer using URLSessionDataDelegate. We deliberately avoid
/// URLSession.bytes(for:) because URLSession buffers the response until
/// "complete" for some configurations, which breaks long-lived event
/// streams. The delegate path streams every chunk as it arrives.
@MainActor
final class ChatSSEClient {
    private var session: URLSession?
    private var task: URLSessionDataTask?
    private var delegate: SSEDelegate?
    private var reconnectTask: Task<Void, Never>?
    private(set) var isConnected = false
    var onMessage: (ChatMessage) -> Void = { _ in }
    var onMessageUpdated: (ChatMessage) -> Void = { _ in }
    var onConversationCreated: (Int) -> Void = { _ in }
    var onConversationDeleted: (Int) -> Void = { _ in }
    var onConnectionChange: (Bool) -> Void = { _ in }

    func start(token: String) {
        stop()
        connect(token: token, backoff: 1_000_000_000)
    }

    func stop() {
        reconnectTask?.cancel()
        reconnectTask = nil
        task?.cancel()
        task = nil
        session?.invalidateAndCancel()
        session = nil
        delegate = nil
        if isConnected {
            isConnected = false
            onConnectionChange(false)
        }
    }

    private func connect(token: String, backoff: UInt64) {
        var url = APIClient.shared.baseURL.appendingPathComponent("/api/v1/chat/sse")
        var comps = URLComponents(url: url, resolvingAgainstBaseURL: false)!
        comps.queryItems = [URLQueryItem(name: "token", value: token)]
        url = comps.url!

        var req = URLRequest(url: url, cachePolicy: .reloadIgnoringLocalAndRemoteCacheData)
        req.setValue("text/event-stream", forHTTPHeaderField: "Accept")
        req.setValue("no-cache", forHTTPHeaderField: "Cache-Control")
        req.timeoutInterval = TimeInterval.greatestFiniteMagnitude

        let cfg = URLSessionConfiguration.default
        cfg.timeoutIntervalForRequest = TimeInterval.greatestFiniteMagnitude
        cfg.timeoutIntervalForResource = TimeInterval.greatestFiniteMagnitude
        cfg.requestCachePolicy = .reloadIgnoringLocalAndRemoteCacheData
        cfg.networkServiceType = .responsiveData
        cfg.waitsForConnectivity = false

        let d = SSEDelegate(
            onConnect: { [weak self] in
                Task { @MainActor in
                    guard let self else { return }
                    if !self.isConnected {
                        self.isConnected = true
                        self.onConnectionChange(true)
                    }
                }
            },
            onEvent: { [weak self] type, payload in
                Task { @MainActor in self?.dispatch(type: type, payload: payload) }
            },
            onClose: { [weak self] _ in
                Task { @MainActor in
                    guard let self else { return }
                    if self.isConnected {
                        self.isConnected = false
                        self.onConnectionChange(false)
                    }
                    let next = min(backoff * 2, 15_000_000_000)
                    self.reconnectTask = Task { [weak self] in
                        try? await Task.sleep(nanoseconds: backoff)
                        guard let self, !Task.isCancelled else { return }
                        self.connect(token: token, backoff: next)
                    }
                }
            }
        )
        let s = URLSession(configuration: cfg, delegate: d, delegateQueue: nil)
        let t = s.dataTask(with: req)
        self.delegate = d
        self.session = s
        self.task = t
        t.resume()
    }

    private func dispatch(type: String, payload: [String: Any]) {
        switch type {
        case "message":
            if let data = try? JSONSerialization.data(withJSONObject: payload),
               let msg = try? JSONDecoder().decode(ChatMessage.self, from: data) {
                onMessage(msg)
            }
        case "message_updated":
            if let data = try? JSONSerialization.data(withJSONObject: payload),
               let msg = try? JSONDecoder().decode(ChatMessage.self, from: data) {
                onMessageUpdated(msg)
            }
        case "conversation_created":
            if let cid = payload["conversation_id"] as? Int {
                onConversationCreated(cid)
            }
        case "conversation_deleted":
            if let cid = payload["conversation_id"] as? Int {
                onConversationDeleted(cid)
            }
        default:
            break
        }
    }
}

private final class SSEDelegate: NSObject, URLSessionDataDelegate {
    private var buffer = Data()
    private let onConnect: () -> Void
    private let onEvent: (String, [String: Any]) -> Void
    private let onClose: (Error?) -> Void

    init(onConnect: @escaping () -> Void,
         onEvent: @escaping (String, [String: Any]) -> Void,
         onClose: @escaping (Error?) -> Void) {
        self.onConnect = onConnect
        self.onEvent = onEvent
        self.onClose = onClose
    }

    func urlSession(_ session: URLSession, dataTask: URLSessionDataTask,
                    didReceive response: URLResponse,
                    completionHandler: @escaping (URLSession.ResponseDisposition) -> Void) {
        let status = (response as? HTTPURLResponse)?.statusCode ?? 0
        if status == 200 {
            onConnect()
            completionHandler(.allow)
        } else {
            completionHandler(.cancel)
        }
    }

    func urlSession(_ session: URLSession, dataTask: URLSessionDataTask, didReceive data: Data) {
        buffer.append(data)
        // Split on \n\n event delimiter.
        while let range = buffer.range(of: Data([0x0a, 0x0a])) {
            let eventData = buffer.subdata(in: 0..<range.lowerBound)
            buffer.removeSubrange(0..<range.upperBound)
            handleEvent(eventData)
        }
    }

    func urlSession(_ session: URLSession, task: URLSessionTask, didCompleteWithError error: Error?) {
        onClose(error)
    }

    private func handleEvent(_ data: Data) {
        guard let raw = String(data: data, encoding: .utf8) else { return }
        var dataBuf = ""
        for line in raw.split(separator: "\n", omittingEmptySubsequences: false) {
            let s = String(line)
            if s.hasPrefix(":") { continue }
            if s.hasPrefix("data:") {
                let payload = s.dropFirst("data:".count).trimmingCharacters(in: .whitespaces)
                if dataBuf.isEmpty { dataBuf = payload }
                else { dataBuf += "\n" + payload }
            }
        }
        guard !dataBuf.isEmpty,
              let bytes = dataBuf.data(using: .utf8),
              let obj = try? JSONSerialization.jsonObject(with: bytes) as? [String: Any] else { return }
        let type = (obj["type"] as? String) ?? ""
        let payload = (obj["data"] as? [String: Any]) ?? [:]
        guard !type.isEmpty else { return }
        onEvent(type, payload)
    }
}

// Minimal AnyJSON helper. Kept private — used only by ChatSSEClient.
private struct AnyJSON: Decodable {
    let value: Any
    init(from decoder: Decoder) throws {
        let c = try decoder.singleValueContainer()
        if let v = try? c.decode(String.self) { value = v }
        else if let v = try? c.decode(Bool.self) { value = v }
        else if let v = try? c.decode(Int.self) { value = v }
        else if let v = try? c.decode(Double.self) { value = v }
        else if let v = try? c.decode([String: AnyJSON].self) { value = v.mapValues { $0.value } }
        else if let v = try? c.decode([AnyJSON].self) { value = v.map { $0.value } }
        else { value = NSNull() }
    }
}

// MARK: - Store

struct ChatToast: Identifiable, Equatable {
    let id = UUID()
    let conversationId: Int
    let title: String
    let body: String
}

@Observable
@MainActor
final class ChatStore {
    var conversations: [ChatConversation] = []
    var messagesByConv: [Int: [ChatMessage]] = [:]
    var detailByConv: [Int: ChatConversationDetail] = [:]
    var employees: [ChatEmployee] = []
    var connected: Bool = false
    var loadingList: Bool = false
    var loadingMessages: Bool = false
    var error: String?
    /// Transient toast emitted on incoming chat messages from someone
    /// other than the viewer when the user is NOT in that thread. UI
    /// observes and clears it after a few seconds.
    var toast: ChatToast?
    /// Conversation the user has open right now — used to suppress toasts
    /// for the active thread. Set/cleared by ChatThreadView.
    var activeConversationId: Int?
    /// Self-id, captured from auth so toasts can be filtered without a
    /// separate environment access from the SSE callback.
    var selfId: Int?

    private let sse = ChatSSEClient()
    private var currentToken: String?

    func bind(token: String) {
        if currentToken == token, sse.isConnected { return }
        currentToken = token
        sse.onMessage = { [weak self] msg in self?.ingestMessage(msg) }
        sse.onMessageUpdated = { [weak self] msg in self?.replaceMessage(msg) }
        sse.onConversationCreated = { [weak self] _ in Task { await self?.refreshList(token: token) } }
        sse.onConversationDeleted = { [weak self] cid in
            self?.conversations.removeAll { $0.id == cid }
            self?.messagesByConv.removeValue(forKey: cid)
            self?.detailByConv.removeValue(forKey: cid)
        }
        sse.onConnectionChange = { [weak self] c in self?.connected = c }
        sse.start(token: token)
    }

    /// Replace a cached message with its updated version (edit/delete).
    private func replaceMessage(_ msg: ChatMessage) {
        var thread = messagesByConv[msg.conversation_id] ?? []
        if let idx = thread.firstIndex(where: { $0.id == msg.id }) {
            thread[idx] = msg
            messagesByConv[msg.conversation_id] = thread
        }
        // Update conversation preview if this was the latest message.
        if let cIdx = conversations.firstIndex(where: { $0.id == msg.conversation_id }),
           conversations[cIdx].last_message_sender_id == msg.sender_id {
            conversations[cIdx].last_message_preview =
                msg.isDeleted ? "Message deleted" : String(msg.body.prefix(140))
        }
    }

    func unbind() {
        sse.stop()
        currentToken = nil
        conversations = []
        messagesByConv = [:]
        detailByConv = [:]
        toast = nil
    }

    func refreshList(token: String) async {
        loadingList = true
        defer { loadingList = false }
        do {
            self.conversations = try await ChatService.shared.conversations(token: token)
        } catch {
            self.error = String(describing: error)
        }
    }

    func loadEmployees(token: String) async {
        do {
            self.employees = try await ChatService.shared.employees(token: token)
        } catch {
            self.error = String(describing: error)
        }
    }

    func openConversation(id: Int, token: String) async {
        loadingMessages = true
        defer { loadingMessages = false }
        do {
            async let detail = ChatService.shared.conversationDetail(id: id, token: token)
            async let msgs = ChatService.shared.messages(conversationId: id, token: token)
            self.detailByConv[id] = try await detail
            self.messagesByConv[id] = try await msgs
            // Mark read.
            if let last = (self.messagesByConv[id] ?? []).last {
                await ChatService.shared.markRead(conversationId: id, messageId: last.id, token: token)
                if let idx = conversations.firstIndex(where: { $0.id == id }) {
                    conversations[idx].unread_count = 0
                }
            }
        } catch {
            self.error = String(describing: error)
        }
    }

    func send(
        conversationId: Int,
        body: String,
        replyTo: Int? = nil,
        token: String,
    ) async {
        let trimmed = body.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        do {
            _ = try await ChatService.shared.send(
                conversationId: conversationId, body: trimmed, replyTo: replyTo, token: token,
            )
            // SSE will deliver the canonical row.
        } catch {
            self.error = String(describing: error)
        }
    }

    func editMessage(_ id: Int, body: String, token: String) async {
        do {
            _ = try await ChatService.shared.editMessage(messageId: id, body: body, token: token)
            // SSE updates everywhere.
        } catch {
            self.error = String(describing: error)
        }
    }

    func deleteMessage(_ id: Int, token: String) async {
        do {
            _ = try await ChatService.shared.deleteMessage(messageId: id, token: token)
        } catch {
            self.error = String(describing: error)
        }
    }

    func toggleReaction(_ messageId: Int, emoji: String, token: String) async {
        do {
            _ = try await ChatService.shared.toggleReaction(
                messageId: messageId, emoji: emoji, token: token,
            )
        } catch {
            self.error = String(describing: error)
        }
    }

    func uploadAttachment(
        conversationId: Int,
        body: String,
        replyTo: Int? = nil,
        fileData: Data,
        fileName: String,
        mimeType: String,
        token: String,
    ) async {
        do {
            _ = try await ChatService.shared.uploadAttachment(
                conversationId: conversationId,
                body: body,
                replyTo: replyTo,
                fileData: fileData,
                fileName: fileName,
                mimeType: mimeType,
                token: token,
            )
        } catch {
            self.error = String(describing: error)
        }
    }

    func createDM(otherUserId: Int, token: String) async -> Int? {
        do {
            let conv = try await ChatService.shared.createDM(otherUserId: otherUserId, token: token)
            await refreshList(token: token)
            return conv.id
        } catch {
            self.error = String(describing: error)
            return nil
        }
    }

    func createGroup(title: String, userIds: [Int], token: String) async -> Int? {
        do {
            let conv = try await ChatService.shared.createGroup(title: title, userIds: userIds, token: token)
            await refreshList(token: token)
            return conv.id
        } catch {
            self.error = String(describing: error)
            return nil
        }
    }

    func archive(conversationId: Int, archived: Bool, token: String) async {
        // Optimistic remove from list immediately so the row disappears.
        let snapshot = conversations
        conversations.removeAll { $0.id == conversationId }
        do {
            try await ChatService.shared.archive(
                conversationId: conversationId, archived: archived, token: token,
            )
        } catch {
            self.error = String(describing: error)
            conversations = snapshot
        }
    }

    func deleteConversation(_ id: Int, token: String) async {
        let snapshot = conversations
        conversations.removeAll { $0.id == id }
        messagesByConv.removeValue(forKey: id)
        detailByConv.removeValue(forKey: id)
        do {
            try await ChatService.shared.delete(conversationId: id, token: token)
        } catch {
            self.error = String(describing: error)
            conversations = snapshot
        }
    }

    /// Persist the current `conversations` order (excluding Anna which is
    /// always force-pinned server-side). Call after the user finishes a
    /// drag-to-reorder gesture.
    func persistOrder(token: String) async {
        let ids = conversations.filter { !$0.isAnna }.map { $0.id }
        do {
            try await ChatService.shared.reorder(ids: ids, token: token)
        } catch {
            self.error = String(describing: error)
        }
    }

    private func ingestMessage(_ msg: ChatMessage) {
        // Append to thread cache.
        var thread = messagesByConv[msg.conversation_id] ?? []
        if !thread.contains(where: { $0.id == msg.id }) {
            thread.append(msg)
            messagesByConv[msg.conversation_id] = thread
        }
        // Update conv list (preview + bump to top, but don't dethrone
        // Anna — she stays pinned via the server's list_conversations).
        if let idx = conversations.firstIndex(where: { $0.id == msg.conversation_id }) {
            var c = conversations[idx]
            c.last_message_at = msg.created_at
            c.last_message_preview = String(msg.body.prefix(140))
            c.last_message_sender_id = msg.sender_id
            // Bump unread for the side that didn't send.
            if msg.sender_id != selfId && msg.conversation_id != activeConversationId {
                c.unread_count = (c.unread_count ?? 0) + 1
            }
            conversations.remove(at: idx)
            // Anna conversation stays at index 0; everything else slots in
            // after her if present.
            let insertIdx = (conversations.first?.channel == "anna") ? 1 : 0
            conversations.insert(c, at: insertIdx)
        } else {
            // Brand-new conversation: refresh the list to learn about it.
            if let t = currentToken {
                Task { await refreshList(token: t) }
            }
        }
        // Fire a toast banner for incoming messages (not from us, not in
        // the active thread).
        if msg.sender_id != selfId, msg.conversation_id != activeConversationId {
            let title = msg.sender?.display_name
                ?? conversations.first(where: { $0.id == msg.conversation_id })?.title
                ?? "New message"
            toast = ChatToast(
                conversationId: msg.conversation_id,
                title: title,
                body: msg.body,
            )
        }
    }
}

// MARK: - Views

struct ChatListView: View {
    @Environment(AuthStore.self) private var auth
    @Environment(ChatStore.self) private var store
    @State private var presentNew = false

    var body: some View {
        NavigationStack {
            ZStack(alignment: .bottomTrailing) {
                Group {
                    if store.loadingList && store.conversations.isEmpty {
                        ProgressView().frame(maxWidth: .infinity, maxHeight: .infinity)
                    } else if store.conversations.isEmpty {
                        emptyState
                    } else {
                        list
                    }
                }

                // "+" FAB lives at the bottom-right of the chat list.
                // Hidden while the New Chat sheet is open so it doesn't
                // peek through during the slide-up animation.
                if !presentNew {
                    Button {
                        presentNew = true
                    } label: {
                        Image(systemName: "plus")
                            .font(.system(size: 24, weight: .semibold))
                            .foregroundStyle(.white)
                            .frame(width: 56, height: 56)
                            .background(Circle().fill(Color.accentColor))
                            .shadow(color: .black.opacity(0.25), radius: 6, x: 0, y: 4)
                    }
                    .buttonStyle(.plain)
                    .padding(.trailing, 18)
                    .padding(.bottom, 18)
                    .accessibilityLabel("New Chat")
                    .transition(.opacity)
                }
            }
            .animation(.easeInOut(duration: 0.15), value: presentNew)
            .navigationBarHidden(true)
            .sheet(isPresented: $presentNew) {
                NewConversationSheet { newId in
                    presentNew = false
                }
            }
            .task {
                guard let t = auth.token else { return }
                store.selfId = auth.user?.id
                store.bind(token: t)
                if store.conversations.isEmpty { await store.refreshList(token: t) }
                if store.employees.isEmpty { await store.loadEmployees(token: t) }
            }
        }
    }

    private var emptyState: some View {
        VStack(spacing: 14) {
            Image(systemName: "bubble.left.and.bubble.right")
                .font(.system(size: 48))
                .foregroundStyle(.secondary)
            Text("No conversations yet")
                .font(.headline)
            Text("Tap + to start a chat with one teammate, or pick several to make a group.")
                .font(.subheadline).foregroundStyle(.secondary)
                .multilineTextAlignment(.center).padding(.horizontal, 24)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }

    private var canDelete: Bool {
        (auth.user?.user_role ?? "").lowercased() == "owner"
    }

    private var list: some View {
        List {
            ForEach(store.conversations) { c in
                NavigationLink {
                    ChatThreadView(conversationId: c.id)
                } label: {
                    ConversationRow(conversation: c)
                }
                // Anna can't be archived or deleted (she's a system chat).
                .swipeActions(edge: .trailing, allowsFullSwipe: false) {
                    if !c.isAnna {
                        Button(role: .destructive) {
                            Task {
                                if let t = auth.token {
                                    await store.archive(conversationId: c.id, archived: true, token: t)
                                }
                            }
                        } label: {
                            Label("Archive", systemImage: "archivebox")
                        }
                        .tint(.gray)
                        if canDelete {
                            Button(role: .destructive) {
                                Task {
                                    if let t = auth.token {
                                        await store.deleteConversation(c.id, token: t)
                                    }
                                }
                            } label: {
                                Label("Delete", systemImage: "trash")
                            }
                        }
                    }
                }
            }
            .onMove(perform: moveRows)
        }
        .listStyle(.plain)
        .refreshable {
            if let t = auth.token { await store.refreshList(token: t) }
        }
    }

    /// Reorder rows in the list. Anna stays pinned at the top — any move
    /// that would dislodge her is silently ignored.
    private func moveRows(from source: IndexSet, to destination: Int) {
        // Anna sits at index 0 if present. Refuse moves that touch index 0.
        let annaIdx = store.conversations.firstIndex(where: { $0.isAnna })
        if let a = annaIdx {
            if source.contains(a) { return }
            if destination <= a { return }
        }
        store.conversations.move(fromOffsets: source, toOffset: destination)
        if let t = auth.token {
            Task { await store.persistOrder(token: t) }
        }
    }
}

/// Deterministic per-conversation avatar palette. Picked so the colors
/// distinguish quickly at a glance — cool/warm mix, all in mid-saturation
/// so they look fine on light + dark backgrounds.
private let chatAvatarPalette: [Color] = [
    Color(red: 0.39, green: 0.40, blue: 0.95), // indigo
    Color(red: 0.13, green: 0.66, blue: 0.78), // teal
    Color(red: 0.18, green: 0.69, blue: 0.40), // green
    Color(red: 0.96, green: 0.45, blue: 0.21), // orange
    Color(red: 0.91, green: 0.30, blue: 0.55), // pink
    Color(red: 0.55, green: 0.36, blue: 0.85), // violet
    Color(red: 0.95, green: 0.70, blue: 0.20), // amber
    Color(red: 0.30, green: 0.51, blue: 0.95), // blue
]

private func chatAvatarColor(for conv: ChatConversation) -> Color {
    if conv.isAnna { return Color(red: 0.55, green: 0.36, blue: 0.85) }  // Anna: violet
    let n = conv.id
    return chatAvatarPalette[abs(n) % chatAvatarPalette.count]
}

private struct ConversationRow: View {
    let conversation: ChatConversation

    var body: some View {
        HStack(alignment: .center, spacing: 12) {
            ZStack {
                Circle().fill(chatAvatarColor(for: conversation))
                    .frame(width: 40, height: 40)
                Text(initials(conversation.title))
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundStyle(.white)
            }
            VStack(alignment: .leading, spacing: 2) {
                HStack(spacing: 6) {
                    Text(conversation.title).font(.body).fontWeight(.semibold)
                        .lineLimit(1)
                    if conversation.isGroup {
                        Text("Group")
                            .font(.system(size: 10, weight: .semibold))
                            .foregroundStyle(.secondary)
                            .padding(.horizontal, 6).padding(.vertical, 2)
                            .background(
                                RoundedRectangle(cornerRadius: 4)
                                    .fill(Color.secondary.opacity(0.15))
                            )
                    }
                    Spacer(minLength: 8)
                    Text(conversation.last_message_at.map(relTime) ?? "")
                        .font(.caption2).foregroundStyle(.secondary)
                        .frame(minHeight: 14)
                }
                HStack {
                    Text(conversation.last_message_preview
                            ?? (conversation.isGroup ? "New group" : "No messages yet"))
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                        .lineLimit(1)
                    Spacer(minLength: 8)
                    if let n = conversation.unread_count, n > 0 {
                        Text("\(n)")
                            .font(.caption2).fontWeight(.bold).foregroundStyle(.white)
                            .padding(.horizontal, 7).padding(.vertical, 2)
                            .background(Capsule().fill(Color.accentColor))
                    }
                }
                .frame(minHeight: 18)
            }
        }
        .padding(.vertical, 8)
        .frame(height: 64)
    }

    private func initials(_ s: String) -> String {
        let parts = s.split(separator: " ").prefix(2)
        return parts.compactMap { $0.first.map(String.init) }.joined().uppercased()
    }
}

struct ChatThreadView: View {
    @Environment(AuthStore.self) private var auth
    @Environment(ChatStore.self) private var store
    let conversationId: Int
    @State private var draft = ""
    @State private var sending = false
    @State private var settings = AppSettings.shared
    @State private var replyingTo: ChatMessage?
    @State private var editingMessage: ChatMessage?
    @State private var editDraft: String = ""
    @State private var photoPickerItem: PhotosPickerItem?
    @State private var uploading: Bool = false
    @FocusState private var composerFocused: Bool

    private var msgs: [ChatMessage] { store.messagesByConv[conversationId] ?? [] }
    private var conv: ChatConversation? { store.conversations.first(where: { $0.id == conversationId }) }
    private var detail: ChatConversationDetail? { store.detailByConv[conversationId] }

    var body: some View {
        VStack(spacing: 0) {
            ScrollViewReader { proxy in
                ScrollView {
                    LazyVStack(alignment: .leading, spacing: 0) {
                        ForEach(Array(msgs.enumerated()), id: \.element.id) { idx, m in
                            // Day separator on date change.
                            if shouldShowDaySeparator(at: idx) {
                                DaySeparator(text: dayHeader(for: m.created_at))
                                    .padding(.vertical, 8)
                            }
                            MessageBubble(
                                message: m,
                                isMine: m.sender_id == auth.user?.id,
                                myUserId: auth.user?.id ?? 0,
                                onSwipeReply: { replyingTo = m },
                                onEdit: { startEditing(m) },
                                onDelete: { Task { await deleteOwnMessage(m) } },
                                onReact: { e in
                                    if let t = auth.token {
                                        Task { await store.toggleReaction(m.id, emoji: e, token: t) }
                                    }
                                },
                            )
                            .id(m.id)
                        }
                    }
                    .padding(.horizontal, 14)
                    .padding(.vertical, 8)
                }
                .onChange(of: msgs.count) {
                    if let last = msgs.last {
                        withAnimation { proxy.scrollTo(last.id, anchor: .bottom) }
                    }
                }
                .onAppear {
                    if let last = msgs.last { proxy.scrollTo(last.id, anchor: .bottom) }
                }
            }
            composer
        }
        .navigationTitle(conv?.title ?? detail?.title ?? "Chat")
        .navigationBarTitleDisplayMode(.inline)
        .task {
            guard let t = auth.token else { return }
            store.activeConversationId = conversationId
            await store.openConversation(id: conversationId, token: t)
        }
        .onDisappear {
            if store.activeConversationId == conversationId {
                store.activeConversationId = nil
            }
        }
    }

    @ViewBuilder
    private var composer: some View {
        VStack(spacing: 0) {
            // Reply chip.
            if let r = replyingTo {
                HStack(spacing: 8) {
                    RoundedRectangle(cornerRadius: 2).fill(Color.accentColor)
                        .frame(width: 3)
                    VStack(alignment: .leading, spacing: 2) {
                        Text("Replying to \(r.sender?.display_name ?? "")")
                            .font(.caption2).foregroundStyle(.secondary)
                        Text(r.body)
                            .font(.caption).foregroundStyle(.primary)
                            .lineLimit(1)
                    }
                    Spacer()
                    Button { replyingTo = nil } label: {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundStyle(.secondary)
                    }
                }
                .padding(.horizontal, 12).padding(.vertical, 6)
                .background(Color(.secondarySystemBackground))
            }
            // Edit-in-progress chip.
            if editingMessage != nil {
                HStack(spacing: 8) {
                    Image(systemName: "pencil")
                        .foregroundStyle(Color.accentColor)
                    Text("Editing")
                        .font(.caption2).foregroundStyle(.secondary)
                    Spacer()
                    Button {
                        editingMessage = nil
                        draft = ""
                    } label: {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundStyle(.secondary)
                    }
                }
                .padding(.horizontal, 12).padding(.vertical, 6)
                .background(Color(.secondarySystemBackground))
            }
            HStack(alignment: .bottom, spacing: 8) {
                if editingMessage == nil {
                    PhotosPicker(selection: $photoPickerItem,
                                 matching: .any(of: [.images, .videos])) {
                        Image(systemName: "paperclip")
                            .font(.system(size: 20))
                            .foregroundStyle(Color.accentColor)
                            .frame(width: 36, height: 36)
                    }
                    .disabled(uploading)
                }
                TextField("Message", text: $draft, axis: .vertical)
                    .textFieldStyle(.plain)
                    .lineLimit(1...6)
                    .padding(.horizontal, 14)
                    .padding(.vertical, 8)
                    .background(Capsule().fill(Color(.secondarySystemBackground)))
                    .focused($composerFocused)
                    .submitLabel(settings.enterToSend ? .send : .return)
                    .onChange(of: draft) { _, newValue in
                        guard settings.enterToSend else { return }
                        if newValue.hasSuffix("\n") {
                            let trimmed = String(newValue.dropLast())
                            if !trimmed.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                                draft = trimmed
                                Task { await doSend() }
                            } else {
                                draft = trimmed
                            }
                        }
                    }
                Button {
                    Task { await doSend() }
                } label: {
                    Image(systemName: editingMessage == nil
                          ? "arrow.up.circle.fill" : "checkmark.circle.fill")
                        .font(.system(size: 30))
                        .foregroundStyle(canSend ? Color.accentColor : Color.secondary.opacity(0.5))
                }
                .disabled(!canSend || sending)
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .background(Color(.systemBackground))
            .overlay(alignment: .top) { Divider() }
            .onChange(of: photoPickerItem) { _, item in
                guard let item else { return }
                Task { await uploadPickedItem(item) }
            }
        }
    }

    private var canSend: Bool {
        !draft.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
    }

    private func doSend() async {
        guard let t = auth.token, canSend, !sending else { return }
        sending = true
        defer { sending = false }
        let body = draft
        draft = ""

        if let m = editingMessage {
            editingMessage = nil
            await store.editMessage(m.id, body: body, token: t)
        } else {
            let replyId = replyingTo?.id
            replyingTo = nil
            await store.send(conversationId: conversationId, body: body, replyTo: replyId, token: t)
        }
    }

    private func startEditing(_ m: ChatMessage) {
        editingMessage = m
        draft = m.body
        replyingTo = nil
        composerFocused = true
    }

    private func deleteOwnMessage(_ m: ChatMessage) async {
        guard let t = auth.token else { return }
        await store.deleteMessage(m.id, token: t)
    }

    private func uploadPickedItem(_ item: PhotosPickerItem) async {
        guard let t = auth.token else { return }
        defer { photoPickerItem = nil }
        uploading = true
        defer { uploading = false }
        guard let data = try? await item.loadTransferable(type: Data.self) else { return }
        let mime = item.supportedContentTypes.first?.preferredMIMEType ?? "image/jpeg"
        let ext = item.supportedContentTypes.first?.preferredFilenameExtension ?? "jpg"
        let name = "photo-\(Int(Date().timeIntervalSince1970)).\(ext)"
        let body = draft
        draft = ""
        let replyId = replyingTo?.id
        replyingTo = nil
        await store.uploadAttachment(
            conversationId: conversationId,
            body: body, replyTo: replyId,
            fileData: data, fileName: name, mimeType: mime,
            token: t,
        )
    }

    private func shouldShowDaySeparator(at idx: Int) -> Bool {
        guard idx >= 0, idx < msgs.count else { return false }
        let cur = msgs[idx]
        if idx == 0 { return true }
        let prev = msgs[idx - 1]
        return dayKey(cur.created_at) != dayKey(prev.created_at)
    }

    private func dayKey(_ iso: String?) -> String {
        guard let iso else { return "" }
        let f = DateFormatter()
        f.dateFormat = "yyyy-MM-dd HH:mm:ss"
        f.timeZone = TimeZone(identifier: "UTC")
        f.locale = Locale(identifier: "en_US_POSIX")
        guard let d = f.date(from: iso) else { return iso }
        let out = DateFormatter()
        out.dateFormat = "yyyy-MM-dd"
        return out.string(from: d)
    }

    private func dayHeader(for iso: String?) -> String {
        guard let iso else { return "" }
        let f = DateFormatter()
        f.dateFormat = "yyyy-MM-dd HH:mm:ss"
        f.timeZone = TimeZone(identifier: "UTC")
        f.locale = Locale(identifier: "en_US_POSIX")
        guard let d = f.date(from: iso) else { return iso }
        let cal = Calendar.current
        if cal.isDateInToday(d) { return "Today" }
        if cal.isDateInYesterday(d) { return "Yesterday" }
        let out = DateFormatter()
        out.dateFormat = "EEEE, MMM d"
        return out.string(from: d)
    }
}

private struct DaySeparator: View {
    let text: String
    var body: some View {
        HStack {
            Spacer()
            Text(text)
                .font(.caption.weight(.medium))
                .foregroundStyle(.secondary)
            Spacer()
        }
    }
}

/// A 2-column-grid card for the New Chat picker. Avatar + first name +
/// selection state. Color follows the chat avatar palette so each
/// teammate keeps a consistent identity color.
private struct EmployeeCard: View {
    let employee: ChatEmployee
    let selected: Bool
    let onTap: () -> Void

    private var avatarColor: Color {
        let palette: [Color] = [
            Color(red: 0.39, green: 0.40, blue: 0.95),
            Color(red: 0.13, green: 0.66, blue: 0.78),
            Color(red: 0.18, green: 0.69, blue: 0.40),
            Color(red: 0.96, green: 0.45, blue: 0.21),
            Color(red: 0.91, green: 0.30, blue: 0.55),
            Color(red: 0.55, green: 0.36, blue: 0.85),
            Color(red: 0.95, green: 0.70, blue: 0.20),
            Color(red: 0.30, green: 0.51, blue: 0.95),
        ]
        return palette[abs(employee.id) % palette.count]
    }

    private var initials: String {
        let parts = employee.display_name.split(separator: " ").prefix(2)
        return parts.compactMap { $0.first.map(String.init) }.joined().uppercased()
    }

    var body: some View {
        Button(action: onTap) {
            VStack(spacing: 8) {
                ZStack(alignment: .topTrailing) {
                    Circle().fill(avatarColor)
                        .frame(width: 52, height: 52)
                    Text(initials)
                        .font(.system(size: 18, weight: .semibold))
                        .foregroundStyle(.white)
                        .frame(width: 52, height: 52)
                    if selected {
                        Image(systemName: "checkmark.circle.fill")
                            .foregroundStyle(Color.accentColor)
                            .background(Circle().fill(Color(.systemBackground)))
                            .offset(x: 4, y: -4)
                    }
                }
                Text(employee.display_name)
                    .font(.system(size: 14, weight: .medium))
                    .foregroundStyle(.primary)
                    .lineLimit(1)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 14)
            .background(
                RoundedRectangle(cornerRadius: 14, style: .continuous)
                    .fill(selected ? Color.accentColor.opacity(0.12)
                          : Color(.secondarySystemBackground))
            )
            .overlay(
                RoundedRectangle(cornerRadius: 14, style: .continuous)
                    .stroke(selected ? Color.accentColor : Color.clear, lineWidth: 1.5)
            )
        }
        .buttonStyle(.plain)
    }
}

private let chatQuickEmojis: [String] = ["👍", "❤️", "😂", "😮", "😢", "🎉"]

private struct MessageBubble: View {
    let message: ChatMessage
    let isMine: Bool
    let myUserId: Int
    let onSwipeReply: () -> Void
    let onEdit: () -> Void
    let onDelete: () -> Void
    let onReact: (String) -> Void

    @State private var swipeOffset: CGFloat = 0
    @State private var pickerVisible: Bool = false
    private let swipeThreshold: CGFloat = 70

    private var senderName: String {
        if isMine { return "You" }
        return message.sender?.display_name ?? "Unknown"
    }

    private var avatarColorForSender: Color {
        // Mirror the conversation palette but key off sender id so each
        // person stays a consistent color across all chats.
        let palette: [Color] = [
            Color(red: 0.39, green: 0.40, blue: 0.95),
            Color(red: 0.13, green: 0.66, blue: 0.78),
            Color(red: 0.18, green: 0.69, blue: 0.40),
            Color(red: 0.96, green: 0.45, blue: 0.21),
            Color(red: 0.91, green: 0.30, blue: 0.55),
            Color(red: 0.55, green: 0.36, blue: 0.85),
            Color(red: 0.95, green: 0.70, blue: 0.20),
            Color(red: 0.30, green: 0.51, blue: 0.95),
        ]
        return palette[abs(message.sender_id) % palette.count]
    }

    private var canEditDelete: Bool {
        guard isMine, !message.isDeleted, let iso = message.created_at else { return false }
        let f = DateFormatter()
        f.dateFormat = "yyyy-MM-dd HH:mm:ss"
        f.timeZone = TimeZone(identifier: "UTC")
        f.locale = Locale(identifier: "en_US_POSIX")
        guard let d = f.date(from: iso) else { return false }
        return Date().timeIntervalSince(d) <= 10
    }

    private func initials(_ s: String) -> String {
        let parts = s.split(separator: " ").prefix(2)
        return parts.compactMap { $0.first.map(String.init) }.joined().uppercased()
    }

    private func headerTimestamp() -> String {
        guard let iso = message.created_at else { return "" }
        let f = DateFormatter()
        f.dateFormat = "yyyy-MM-dd HH:mm:ss"
        f.timeZone = TimeZone(identifier: "UTC")
        f.locale = Locale(identifier: "en_US_POSIX")
        guard let d = f.date(from: iso) else { return "" }
        let out = DateFormatter()
        out.dateFormat = "MMM d, h:mm a"
        return out.string(from: d)
    }

    var body: some View {
        HStack(alignment: .top, spacing: 10) {
            // Avatar
            ZStack {
                Circle().fill(avatarColorForSender)
                    .frame(width: 32, height: 32)
                Text(initials(senderName))
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundStyle(.white)
            }

            VStack(alignment: .leading, spacing: 4) {
                // Header: name + timestamp
                HStack(spacing: 6) {
                    Text(senderName)
                        .font(.system(size: 14, weight: .semibold))
                    Text(headerTimestamp())
                        .font(.system(size: 12))
                        .foregroundStyle(.secondary)
                }

                // Quote chip (if reply)
                if let r = message.reply_to {
                    HStack(alignment: .top, spacing: 6) {
                        RoundedRectangle(cornerRadius: 2)
                            .fill(Color.secondary.opacity(0.4))
                            .frame(width: 3)
                        VStack(alignment: .leading, spacing: 2) {
                            Text(r.sender_name)
                                .font(.caption2).fontWeight(.semibold)
                                .foregroundStyle(.secondary)
                            Text(r.deleted ? "(message deleted)" : r.body)
                                .font(.caption)
                                .foregroundStyle(.secondary)
                                .lineLimit(2)
                        }
                    }
                }

                // Body bubble
                if message.isDeleted {
                    Text("Message deleted")
                        .font(.system(size: 14)).italic()
                        .foregroundStyle(.tertiary)
                        .padding(.horizontal, 12).padding(.vertical, 8)
                        .background(
                            RoundedRectangle(cornerRadius: 14, style: .continuous)
                                .fill(Color(.tertiarySystemBackground))
                        )
                } else {
                    // Attachments first (above text), so an empty body
                    // doesn't render an empty bubble.
                    if let atts = message.attachments, !atts.isEmpty {
                        VStack(alignment: .leading, spacing: 6) {
                            ForEach(atts) { a in
                                AttachmentView(attachment: a)
                            }
                        }
                    }
                    if !message.body.isEmpty && message.body != "📎" {
                        Text(message.body)
                            .font(.system(size: 15))
                            .foregroundStyle(Color.primary)
                            .padding(.horizontal, 12).padding(.vertical, 8)
                            .background(
                                RoundedRectangle(cornerRadius: 14, style: .continuous)
                                    .fill(isMine ? Color.accentColor.opacity(0.15) : Color(.secondarySystemBackground))
                            )
                    }
                }

                if message.edited_at != nil && !message.isDeleted {
                    Text("(edited)")
                        .font(.caption2).foregroundStyle(.secondary)
                }

                // Reaction chips (one per emoji).
                if let rxns = message.reactions, !rxns.isEmpty {
                    HStack(spacing: 6) {
                        ForEach(rxns) { r in
                            ReactionChip(
                                reaction: r,
                                mine: r.user_ids.contains(myUserId),
                                onTap: { onReact(r.emoji) },
                            )
                        }
                    }
                    .padding(.top, 4)
                }
            }
            Spacer(minLength: 0)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.vertical, 6)
        .offset(x: swipeOffset)
        .gesture(
            DragGesture(minimumDistance: 12)
                .onChanged { v in
                    if !message.isDeleted, v.translation.width > 0 {
                        swipeOffset = min(v.translation.width, 90)
                    }
                }
                .onEnded { v in
                    if !message.isDeleted, v.translation.width > swipeThreshold {
                        onSwipeReply()
                    }
                    withAnimation(.spring(response: 0.25)) {
                        swipeOffset = 0
                    }
                }
        )
        .contextMenu {
            if !message.isDeleted {
                ControlGroup {
                    ForEach(chatQuickEmojis, id: \.self) { e in
                        Button(e) { onReact(e) }
                    }
                }
                Button {
                    pickerVisible = true
                } label: { Label("More reactions…", systemImage: "face.smiling") }

                Button { onSwipeReply() } label: {
                    Label("Reply", systemImage: "arrowshape.turn.up.left")
                }
            }
            if canEditDelete {
                Button { onEdit() } label: { Label("Edit", systemImage: "pencil") }
                Button(role: .destructive) { onDelete() } label: {
                    Label("Delete", systemImage: "trash")
                }
            }
        }
        .sheet(isPresented: $pickerVisible) {
            EmojiReactionPicker(
                onPick: { e in
                    pickerVisible = false
                    onReact(e)
                },
                onCancel: { pickerVisible = false },
            )
            .presentationDetents([.medium])
        }
    }
}

/// Render a single attachment inside a message bubble. Photos load via
/// AsyncImage with the bearer token attached so the auth-protected
/// /api/v1/chat/attachments/{id} endpoint accepts the request.
private struct AttachmentView: View {
    let attachment: ChatAttachment
    @Environment(AuthStore.self) private var auth

    private var fullURL: URL? {
        URL(string: attachment.url, relativeTo: APIClient.shared.baseURL)
    }

    var body: some View {
        Group {
            if attachment.isPhoto {
                AuthedAsyncImage(urlString: attachment.url, token: auth.token)
                    .frame(maxWidth: 240)
                    .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))
            } else if attachment.isVideo {
                HStack(spacing: 8) {
                    Image(systemName: "play.circle.fill")
                        .font(.system(size: 22))
                    Text(attachment.original_name ?? "Video")
                        .font(.system(size: 14)).lineLimit(1)
                }
                .padding(.horizontal, 12).padding(.vertical, 10)
                .background(
                    RoundedRectangle(cornerRadius: 10).fill(Color(.secondarySystemBackground)),
                )
            } else {
                HStack(spacing: 8) {
                    Image(systemName: "doc")
                        .font(.system(size: 18))
                    Text(attachment.original_name ?? "File")
                        .font(.system(size: 14)).lineLimit(1)
                }
                .padding(.horizontal, 12).padding(.vertical, 10)
                .background(
                    RoundedRectangle(cornerRadius: 10).fill(Color(.secondarySystemBackground)),
                )
            }
        }
    }
}

/// AsyncImage doesn't let us inject Authorization headers, so for our
/// auth-protected media we fetch via URLSession and decode into a UIImage.
private struct AuthedAsyncImage: View {
    let urlString: String
    let token: String?
    @State private var image: UIImage?
    @State private var failed: Bool = false

    var body: some View {
        Group {
            if let img = image {
                Image(uiImage: img).resizable().scaledToFit()
            } else if failed {
                Image(systemName: "photo")
                    .font(.system(size: 32))
                    .foregroundStyle(.secondary)
                    .frame(width: 120, height: 90)
            } else {
                ProgressView().frame(width: 120, height: 90)
            }
        }
        .task(id: urlString) { await load() }
    }

    private func load() async {
        guard let url = URL(string: urlString, relativeTo: APIClient.shared.baseURL),
              let token else { failed = true; return }
        var req = URLRequest(url: url)
        req.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        do {
            let (data, _) = try await URLSession.shared.data(for: req)
            if let img = UIImage(data: data) { self.image = img }
            else { self.failed = true }
        } catch {
            self.failed = true
        }
    }
}

private struct ReactionChip: View {
    let reaction: ChatReaction
    let mine: Bool
    let onTap: () -> Void

    var body: some View {
        Button(action: onTap) {
            HStack(spacing: 4) {
                Text(reaction.emoji).font(.system(size: 13))
                Text("\(reaction.count)")
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundStyle(mine ? Color.accentColor : .primary)
            }
            .padding(.horizontal, 8).padding(.vertical, 3)
            .background(
                Capsule().fill(mine
                    ? Color.accentColor.opacity(0.15)
                    : Color(.tertiarySystemBackground))
            )
            .overlay(
                Capsule().stroke(
                    mine ? Color.accentColor.opacity(0.5) : Color.secondary.opacity(0.2),
                    lineWidth: 1,
                )
            )
        }
        .buttonStyle(.plain)
    }
}

/// Bigger emoji picker shown when the user taps "More reactions…".
private struct EmojiReactionPicker: View {
    let onPick: (String) -> Void
    let onCancel: () -> Void

    private let palette: [String] = [
        "👍", "👎", "❤️", "🔥", "🎉", "👏", "🙏", "😂",
        "😄", "😎", "😮", "😢", "😡", "🤔", "💯", "✅",
        "❌", "⏰", "📌", "📷", "🚚", "🛠️", "💪", "💰",
    ]
    private let cols = [GridItem(.adaptive(minimum: 56), spacing: 8)]

    var body: some View {
        NavigationStack {
            ScrollView {
                LazyVGrid(columns: cols, spacing: 8) {
                    ForEach(palette, id: \.self) { e in
                        Button(action: { onPick(e) }) {
                            Text(e).font(.system(size: 28))
                                .frame(width: 52, height: 52)
                                .background(
                                    RoundedRectangle(cornerRadius: 12)
                                        .fill(Color(.secondarySystemBackground))
                                )
                        }
                        .buttonStyle(.plain)
                    }
                }
                .padding(20)
            }
            .navigationTitle("Pick a reaction")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Cancel") { onCancel() }
                }
            }
        }
    }
}

// MARK: - New Conversation Sheet

private struct NewConversationSheet: View {
    @Environment(AuthStore.self) private var auth
    @Environment(ChatStore.self) private var store
    @Environment(\.dismiss) private var dismiss
    let onCreated: (Int?) -> Void

    /// Selection in tap order. Order drives the auto-generated group title
    /// ("Abhijeet, Clara") so that matches what the user picked first.
    @State private var pickedOrder: [Int] = []
    @State private var groupTitle: String = ""
    @State private var userEditedTitle: Bool = false
    @State private var search: String = ""
    @State private var creating: Bool = false

    private var employees: [ChatEmployee] {
        if search.isEmpty { return store.employees }
        let q = search.lowercased()
        return store.employees.filter {
            $0.display_name.lowercased().contains(q) || $0.email.lowercased().contains(q)
        }
    }

    private var isGroupMode: Bool { pickedOrder.count >= 2 }

    /// Auto-generated group name: first names joined by ", ", in pick order.
    /// `display_name` already equals the first name (set server-side).
    private var autoGroupTitle: String {
        let byId = Dictionary(uniqueKeysWithValues: store.employees.map { ($0.id, $0) })
        return pickedOrder.compactMap { byId[$0]?.display_name }
            .joined(separator: ", ")
    }

    private let columns = [
        GridItem(.flexible(), spacing: 10),
        GridItem(.flexible(), spacing: 10),
    ]

    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                if isGroupMode {
                    HStack(spacing: 8) {
                        Image(systemName: "person.2.fill")
                            .foregroundStyle(.secondary)
                        TextField(autoGroupTitle, text: $groupTitle, axis: .horizontal)
                            .textFieldStyle(.plain)
                            .onChange(of: groupTitle) { _, newValue in
                                if newValue.isEmpty {
                                    userEditedTitle = false
                                } else if newValue != autoGroupTitle {
                                    userEditedTitle = true
                                }
                            }
                    }
                    .padding(.horizontal, 14).padding(.vertical, 10)
                    .background(Capsule().fill(Color(.secondarySystemBackground)))
                    .padding(.horizontal, 16).padding(.top, 12)
                }

                ScrollView {
                    LazyVGrid(columns: columns, spacing: 10) {
                        if employees.isEmpty && store.employees.isEmpty {
                            ProgressView().frame(maxWidth: .infinity).padding(40)
                        } else {
                            ForEach(employees) { e in
                                EmployeeCard(
                                    employee: e,
                                    selected: pickedOrder.contains(e.id),
                                    onTap: { togglePick(e) }
                                )
                            }
                        }
                    }
                    .padding(16)
                }
            }
            .searchable(text: $search, placement: .navigationBarDrawer(displayMode: .always))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button("Cancel") { dismiss() }
                }
                ToolbarItem(placement: .topBarTrailing) {
                    Button(isGroupMode ? "Create" : "Start") {
                        Task { await create() }
                    }
                    .disabled(!canCreate || creating)
                }
            }
            .task {
                if store.employees.isEmpty, let t = auth.token {
                    await store.loadEmployees(token: t)
                }
            }
            .onChange(of: pickedOrder) { _, _ in
                if !userEditedTitle { groupTitle = autoGroupTitle }
            }
        }
    }

    private var canCreate: Bool {
        if pickedOrder.count == 1 { return true }
        if pickedOrder.count >= 2 {
            let resolved = userEditedTitle
                ? groupTitle.trimmingCharacters(in: .whitespacesAndNewlines)
                : autoGroupTitle
            return !resolved.isEmpty
        }
        return false
    }

    private func togglePick(_ e: ChatEmployee) {
        if let idx = pickedOrder.firstIndex(of: e.id) {
            pickedOrder.remove(at: idx)
        } else {
            pickedOrder.append(e.id)
        }
    }

    private func create() async {
        guard let t = auth.token, !creating else { return }
        creating = true
        defer { creating = false }
        var newId: Int?
        if pickedOrder.count == 1 {
            newId = await store.createDM(otherUserId: pickedOrder[0], token: t)
        } else if pickedOrder.count >= 2 {
            let resolved = userEditedTitle
                ? groupTitle.trimmingCharacters(in: .whitespacesAndNewlines)
                : autoGroupTitle
            newId = await store.createGroup(title: resolved, userIds: pickedOrder, token: t)
        }
        onCreated(newId)
        dismiss()
    }
}

// MARK: - Helpers

private func relTime(_ iso: String) -> String {
    // Server ISO8601 with space separator and no Z. Parse permissively.
    let f = DateFormatter()
    f.dateFormat = "yyyy-MM-dd HH:mm:ss"
    f.timeZone = TimeZone(identifier: "UTC")
    f.locale = Locale(identifier: "en_US_POSIX")
    let d: Date
    if let parsed = f.date(from: iso) {
        d = parsed
    } else {
        let alt = ISO8601DateFormatter()
        d = alt.date(from: iso) ?? Date()
    }
    let diff = Date().timeIntervalSince(d)
    if diff < 60 { return "just now" }
    if diff < 3600 { return "\(Int(diff/60))m" }
    if diff < 86400 { return "\(Int(diff/3600))h" }
    if diff < 7 * 86400 { return "\(Int(diff/86400))d" }
    let out = DateFormatter()
    out.dateStyle = .short
    return out.string(from: d)
}
