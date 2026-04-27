package com.astrastaging.portal.ui.chat

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.astrastaging.portal.data.ApiClient
import com.astrastaging.portal.data.ChatConversation
import com.astrastaging.portal.data.ChatConversationDetail
import com.astrastaging.portal.data.ChatEmployee
import com.astrastaging.portal.data.ChatEvent
import com.astrastaging.portal.data.ChatMessage
import com.astrastaging.portal.data.ChatSseClient
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class ChatToast(
    val id: Long,
    val conversationId: Int,
    val title: String,
    val body: String,
)

data class ChatUiState(
    val conversations: List<ChatConversation> = emptyList(),
    val messagesByConv: Map<Int, List<ChatMessage>> = emptyMap(),
    val detailByConv: Map<Int, ChatConversationDetail> = emptyMap(),
    val employees: List<ChatEmployee> = emptyList(),
    val connected: Boolean = false,
    val loadingList: Boolean = false,
    val loadingMessages: Boolean = false,
    val error: String? = null,
    val toast: ChatToast? = null,
    /** Conversation currently displayed in the thread view; toasts are
     *  suppressed for messages that belong to it. Set by ChatScreen when
     *  a thread is open, cleared when popped. */
    val activeConversationId: Int? = null,
    /** Self user-id, captured so SSE handlers can filter out our own
     *  echoes when deciding whether to bump unread or fire a toast. */
    val selfId: Int? = null,
)

class ChatViewModel : ViewModel() {
    private val _state = MutableStateFlow(ChatUiState())
    val state: StateFlow<ChatUiState> = _state.asStateFlow()

    private var sseJob: Job? = null
    private var currentToken: String? = null

    fun bind(token: String) {
        if (currentToken == token && sseJob?.isActive == true) return
        currentToken = token
        sseJob?.cancel()
        sseJob = viewModelScope.launch {
            ChatSseClient.stream(token).collect { ev ->
                when (ev) {
                    ChatEvent.Connected -> _state.update { it.copy(connected = true) }
                    ChatEvent.Disconnected -> _state.update { it.copy(connected = false) }
                    is ChatEvent.Message -> ingestMessage(ev.message)
                    is ChatEvent.ConversationCreated -> refreshList(token)
                    is ChatEvent.ConversationDeleted -> _state.update { st ->
                        st.copy(
                            conversations = st.conversations.filter { it.id != ev.conversationId },
                            messagesByConv = st.messagesByConv - ev.conversationId,
                            detailByConv = st.detailByConv - ev.conversationId,
                        )
                    }
                    is ChatEvent.MessageUpdated -> {
                        val msg = ev.message
                        _state.update { st ->
                            val list = st.messagesByConv[msg.conversation_id].orEmpty()
                            val idx = list.indexOfFirst { it.id == msg.id }
                            val newList = if (idx >= 0) {
                                list.toMutableList().also { it[idx] = msg }
                            } else list
                            // Update list preview if this was the latest.
                            val convs = st.conversations.map { c ->
                                if (c.id == msg.conversation_id && c.last_message_sender_id == msg.sender_id) {
                                    c.copy(last_message_preview =
                                        if (msg.deleted || msg.deleted_at != null) "Message deleted"
                                        else msg.body.take(140))
                                } else c
                            }
                            st.copy(
                                messagesByConv = st.messagesByConv + (msg.conversation_id to newList),
                                conversations = convs,
                            )
                        }
                    }
                    is ChatEvent.Notification -> {
                        // Local notifications are picked up by the conversation
                        // list refresh; nothing to do here for phase 1.
                    }
                }
            }
        }
    }

    fun unbind() {
        sseJob?.cancel()
        sseJob = null
        currentToken = null
        _state.update { ChatUiState() }
    }

    fun setActiveConversation(id: Int?) {
        _state.update { it.copy(activeConversationId = id) }
    }

    fun setSelfId(id: Int) {
        _state.update { it.copy(selfId = id) }
    }

    fun clearToast() {
        _state.update { it.copy(toast = null) }
    }

    fun refreshList(token: String) {
        viewModelScope.launch {
            _state.update { it.copy(loadingList = true, error = null) }
            try {
                val conv = ApiClient.chatConversations(token).conversations
                _state.update { it.copy(conversations = conv, loadingList = false) }
            } catch (t: Throwable) {
                _state.update { it.copy(loadingList = false, error = t.message) }
            }
        }
    }

    fun loadEmployees(token: String) {
        viewModelScope.launch {
            try {
                val es = ApiClient.chatEmployees(token).employees
                _state.update { it.copy(employees = es) }
            } catch (t: Throwable) {
                _state.update { it.copy(error = t.message) }
            }
        }
    }

    fun openConversation(id: Int, token: String) {
        viewModelScope.launch {
            _state.update { it.copy(loadingMessages = true, error = null) }
            try {
                val detail = ApiClient.chatConversationDetail(id, token).conversation
                val msgs = ApiClient.chatMessages(id, token = token).messages
                _state.update { st ->
                    val cleared = st.conversations.map { c ->
                        if (c.id == id) c.copy(unread_count = 0) else c
                    }
                    st.copy(
                        loadingMessages = false,
                        detailByConv = st.detailByConv + (id to detail),
                        messagesByConv = st.messagesByConv + (id to msgs),
                        conversations = cleared,
                    )
                }
                msgs.lastOrNull()?.let { last ->
                    runCatching { ApiClient.chatMarkRead(id, last.id, token) }
                }
            } catch (t: Throwable) {
                _state.update { it.copy(loadingMessages = false, error = t.message) }
            }
        }
    }

    fun send(conversationId: Int, body: String, replyTo: Int? = null, token: String) {
        val trimmed = body.trim()
        if (trimmed.isEmpty()) return
        viewModelScope.launch {
            try {
                ApiClient.chatSend(conversationId, trimmed, replyTo = replyTo, token = token)
            } catch (t: Throwable) {
                _state.update { it.copy(error = t.message) }
            }
        }
    }

    fun editMessage(messageId: Int, body: String, token: String) {
        val trimmed = body.trim()
        if (trimmed.isEmpty()) return
        viewModelScope.launch {
            try {
                ApiClient.chatEditMessage(messageId, trimmed, token)
            } catch (t: Throwable) {
                _state.update { it.copy(error = t.message) }
            }
        }
    }

    fun deleteMessage(messageId: Int, token: String) {
        viewModelScope.launch {
            try {
                ApiClient.chatDeleteMessage(messageId, token)
            } catch (t: Throwable) {
                _state.update { it.copy(error = t.message) }
            }
        }
    }

    fun toggleReaction(messageId: Int, emoji: String, token: String) {
        viewModelScope.launch {
            try {
                ApiClient.chatToggleReaction(messageId, emoji, token)
            } catch (t: Throwable) {
                _state.update { it.copy(error = t.message) }
            }
        }
    }

    fun uploadAttachment(
        conversationId: Int,
        body: String,
        replyTo: Int?,
        bytes: ByteArray,
        fileName: String,
        mimeType: String,
        token: String,
    ) {
        viewModelScope.launch {
            try {
                ApiClient.chatUploadAttachment(
                    conversationId, body, replyTo, bytes, fileName, mimeType, token,
                )
            } catch (t: Throwable) {
                _state.update { it.copy(error = t.message) }
            }
        }
    }

    fun createDM(otherUserId: Int, token: String, onCreated: (Int?) -> Unit) {
        viewModelScope.launch {
            try {
                val conv = ApiClient.chatCreateDM(otherUserId, token).conversation
                refreshList(token)
                onCreated(conv.id)
            } catch (t: Throwable) {
                _state.update { it.copy(error = t.message) }
                onCreated(null)
            }
        }
    }

    fun createGroup(title: String, userIds: List<Int>, token: String, onCreated: (Int?) -> Unit) {
        viewModelScope.launch {
            try {
                val conv = ApiClient.chatCreateGroup(title, userIds, token).conversation
                refreshList(token)
                onCreated(conv.id)
            } catch (t: Throwable) {
                _state.update { it.copy(error = t.message) }
                onCreated(null)
            }
        }
    }

    fun archive(conversationId: Int, archived: Boolean, token: String) {
        // Optimistic remove from list.
        val snapshot = _state.value.conversations
        _state.update { st ->
            st.copy(conversations = st.conversations.filter { it.id != conversationId })
        }
        viewModelScope.launch {
            try {
                ApiClient.chatArchive(conversationId, archived, token)
            } catch (t: Throwable) {
                _state.update { it.copy(error = t.message, conversations = snapshot) }
            }
        }
    }

    fun deleteConversation(conversationId: Int, token: String) {
        val snapshot = _state.value.conversations
        _state.update { st ->
            st.copy(
                conversations = st.conversations.filter { it.id != conversationId },
                messagesByConv = st.messagesByConv - conversationId,
                detailByConv = st.detailByConv - conversationId,
            )
        }
        viewModelScope.launch {
            try {
                ApiClient.chatDeleteConversation(conversationId, token)
            } catch (t: Throwable) {
                _state.update { it.copy(error = t.message, conversations = snapshot) }
            }
        }
    }

    /** Locally re-order the conversation list (ignoring Anna which is
     *  always force-pinned) and persist the order on the server. */
    fun reorder(fromIndex: Int, toIndex: Int, token: String) {
        _state.update { st ->
            val list = st.conversations.toMutableList()
            if (fromIndex !in list.indices || toIndex !in list.indices) return@update st
            // Don't let Anna (always at index 0) be moved or displaced.
            val annaIdx = list.indexOfFirst { it.isAnna }
            if (annaIdx == 0 && (fromIndex == 0 || toIndex == 0)) return@update st
            val item = list.removeAt(fromIndex)
            list.add(toIndex, item)
            st.copy(conversations = list)
        }
        viewModelScope.launch {
            try {
                val ids = _state.value.conversations.filterNot { it.isAnna }.map { it.id }
                ApiClient.chatReorder(ids, token)
            } catch (t: Throwable) {
                _state.update { it.copy(error = t.message) }
            }
        }
    }

    private fun ingestMessage(msg: ChatMessage) {
        _state.update { st ->
            val list = st.messagesByConv[msg.conversation_id].orEmpty()
            val merged = if (list.any { it.id == msg.id }) list else list + msg
            val newMsgs = st.messagesByConv + (msg.conversation_id to merged)

            val convIdx = st.conversations.indexOfFirst { it.id == msg.conversation_id }
            val newConvs = if (convIdx >= 0) {
                val orig = st.conversations[convIdx]
                val bumpUnread = msg.sender_id != st.selfId &&
                                 msg.conversation_id != st.activeConversationId
                val c = orig.copy(
                    last_message_at = msg.created_at,
                    last_message_preview = msg.body.take(140),
                    last_message_sender_id = msg.sender_id,
                    unread_count = if (bumpUnread) orig.unread_count + 1 else orig.unread_count,
                )
                val without = st.conversations.toMutableList().apply { removeAt(convIdx) }
                // Anna stays pinned at index 0.
                val insertIdx = if (without.firstOrNull()?.channel == "anna") 1 else 0
                without.toMutableList().apply { add(insertIdx, c) }
            } else st.conversations

            val newToast = if (
                msg.sender_id != st.selfId &&
                msg.conversation_id != st.activeConversationId
            ) {
                val title = msg.sender?.display_name
                    ?: newConvs.firstOrNull { it.id == msg.conversation_id }?.title
                    ?: "New message"
                ChatToast(
                    id = System.currentTimeMillis(),
                    conversationId = msg.conversation_id,
                    title = title,
                    body = msg.body,
                )
            } else st.toast

            st.copy(messagesByConv = newMsgs, conversations = newConvs, toast = newToast)
        }
    }
}
