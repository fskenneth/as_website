@file:OptIn(androidx.compose.material3.ExperimentalMaterial3Api::class)

package com.astrastaging.portal.ui.chat

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.Animatable
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.detectDragGesturesAfterLongPress
import androidx.compose.foundation.gestures.detectHorizontalDragGestures
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items as lazyGridItems
import androidx.compose.material.icons.outlined.Close
import androidx.compose.foundation.layout.heightIn
import androidx.compose.material.icons.outlined.Archive
import androidx.compose.foundation.border
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.material.icons.outlined.AttachFile
import androidx.compose.material.icons.outlined.Delete
import androidx.compose.material.icons.outlined.PlayCircle
import androidx.compose.material.icons.outlined.Image
import androidx.compose.material.icons.outlined.Mood
import androidx.compose.material.icons.outlined.PhotoCamera
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.runtime.derivedStateOf
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.zIndex
import kotlinx.coroutines.launch
import kotlin.math.roundToInt
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.systemBars
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.navigationBars
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.only
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.outlined.ArrowBack
import androidx.compose.material.icons.automirrored.outlined.Send
import androidx.compose.material.icons.filled.Add
import androidx.compose.material3.AssistChip
import androidx.compose.material3.AssistChipDefaults
import androidx.compose.material3.Badge
import androidx.compose.material3.BadgedBox
import androidx.compose.material3.Button
import androidx.compose.material3.CenterAlignedTopAppBar
import androidx.compose.material3.Checkbox
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.ListItem
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.derivedStateOf
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.astrastaging.portal.data.ChatAttachment
import com.astrastaging.portal.data.ChatConversation
import com.astrastaging.portal.data.ChatEmployee
import com.astrastaging.portal.data.ChatMessage
import kotlinx.coroutines.withContext
import java.time.Duration
import java.time.LocalDateTime
import java.time.OffsetDateTime
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter

@Composable
fun ChatScreen(
    userId: Int,
    userRole: String,
    userFirstName: String,
    token: String,
    viewModel: ChatViewModel,
    modifier: Modifier = Modifier,
) {
    val state by viewModel.state.collectAsState()
    var openConvId by remember { mutableStateOf<Int?>(null) }
    var showNewSheet by remember { mutableStateOf(false) }

    LaunchedEffect(openConvId) { viewModel.setActiveConversation(openConvId) }
    DisposableEffect(Unit) {
        onDispose { viewModel.setActiveConversation(null) }
    }

    val activeConvId = openConvId
    androidx.compose.runtime.CompositionLocalProvider(LocalChatToken provides token) {
    if (activeConvId != null) {
        ThreadPane(
            modifier = modifier,
            userId = userId,
            userFirstName = userFirstName,
            token = token,
            conversationId = activeConvId,
            state = state,
            onBack = { openConvId = null },
            onSend = { body, replyTo ->
                viewModel.send(activeConvId, body, replyTo = replyTo, token = token)
            },
            onEdit = { msgId, body -> viewModel.editMessage(msgId, body, token) },
            onDelete = { msgId -> viewModel.deleteMessage(msgId, token) },
            onReact = { msgId, emoji -> viewModel.toggleReaction(msgId, emoji, token) },
            onUpload = { body, replyTo, bytes, fileName, mimeType ->
                viewModel.uploadAttachment(
                    activeConvId, body, replyTo, bytes, fileName, mimeType, token,
                )
            },
            onOpened = { viewModel.openConversation(activeConvId, token) },
        )
    } else {
        Box(modifier = modifier.fillMaxSize()) {
            ListPane(
                modifier = Modifier.fillMaxSize(),
                state = state,
                userRole = userRole,
                onOpen = { id -> openConvId = id },
                onArchive = { id -> viewModel.archive(id, archived = true, token = token) },
                onDelete = { id -> viewModel.deleteConversation(id, token = token) },
                onReorder = { from, to -> viewModel.reorder(from, to, token) },
                onRefresh = { viewModel.refreshList(token) },
            )
            // "+" FAB — bottom-right of the chat list. Hidden while
            // the New Chat sheet is open so it doesn't show through
            // a half-height sheet on shorter screens.
            if (!showNewSheet) {
                androidx.compose.material3.FloatingActionButton(
                    onClick = { showNewSheet = true },
                    shape = androidx.compose.foundation.shape.CircleShape,
                    containerColor = MaterialTheme.colorScheme.primary,
                    contentColor = MaterialTheme.colorScheme.onPrimary,
                    modifier = Modifier
                        .align(Alignment.BottomEnd)
                        .padding(end = 18.dp, bottom = 18.dp)
                        .navigationBarsPadding(),
                ) {
                    Icon(
                        Icons.Filled.Add,
                        contentDescription = "New Chat",
                    )
                }
            }
        }
    }

    if (showNewSheet) {
        NewConversationSheet(
            employees = state.employees,
            onDismiss = { showNewSheet = false },
            onConfirmDM = { otherId ->
                viewModel.createDM(otherId, token) { newId ->
                    showNewSheet = false
                    if (newId != null) openConvId = newId
                }
            },
            onConfirmGroup = { title, ids ->
                viewModel.createGroup(title, ids, token) { newId ->
                    showNewSheet = false
                    if (newId != null) openConvId = newId
                }
            },
        )
    }
    }  // closes CompositionLocalProvider
}

@Composable
private fun ListPane(
    modifier: Modifier,
    state: ChatUiState,
    userRole: String,
    onOpen: (Int) -> Unit,
    onArchive: (Int) -> Unit,
    onDelete: (Int) -> Unit,
    onReorder: (fromIndex: Int, toIndex: Int) -> Unit,
    onRefresh: () -> Unit,
) {
    val canDelete = userRole.equals("owner", ignoreCase = true)

    // Long-press drag-to-reorder state. Only one row is "lifted" at a time;
    // its translation tracks the user's finger and the other rows yield by
    // shifting up/down a slot to reveal a drop target.
    val rowHeightPx = with(LocalDensity.current) { 72.dp.toPx() }
    var draggingId by remember { mutableStateOf<Int?>(null) }
    var draggingOriginIdx by remember { mutableStateOf<Int?>(null) }
    var dragOffsetY by remember { mutableStateOf(0f) }

    // Project a target slot from the live drag offset. Anna stays pinned
    // at index 0 so the lower bound is 1 when she's present.
    val total = state.conversations.size
    val annaFirst = state.conversations.firstOrNull()?.isAnna == true
    val minIdx = if (annaFirst) 1 else 0
    val targetIdx: Int? = run {
        val origin = draggingOriginIdx ?: return@run null
        val slots = (dragOffsetY / rowHeightPx).roundToInt()
        (origin + slots).coerceIn(minIdx, total - 1)
    }

    Box(
        modifier = modifier
            .fillMaxSize()
            .statusBarsPadding()
    ) {
        if (state.loadingList && state.conversations.isEmpty()) {
            Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        } else if (state.conversations.isEmpty()) {
            EmptyState()
        } else {
            LazyColumn(modifier = Modifier.fillMaxSize()) {
                itemsIndexed(state.conversations, key = { _, c -> c.id }) { idx, c ->
                    // Compute this row's yield displacement so non-dragged
                    // rows visibly slide aside to expose the drop slot.
                    val isThisDragging = draggingId == c.id
                    val origin = draggingOriginIdx
                    val target = targetIdx
                    val yieldOffset: Float = when {
                        origin == null || target == null -> 0f
                        isThisDragging -> 0f  // dragged row uses dragOffsetY directly
                        idx in (origin + 1)..target -> -rowHeightPx  // slid up to fill
                        idx in target..(origin - 1) -> rowHeightPx    // slid down to make room
                        else -> 0f
                    }
                    val animatedYield by androidx.compose.animation.core.animateFloatAsState(
                        targetValue = yieldOffset,
                        animationSpec = androidx.compose.animation.core.spring(
                            dampingRatio = 0.8f,
                            stiffness = androidx.compose.animation.core.Spring.StiffnessMediumLow,
                        ),
                        label = "yield-row-$idx",
                    )

                    ConversationRow(
                        c = c,
                        canDelete = canDelete,
                        rowHeightPx = rowHeightPx,
                        isDragging = isThisDragging,
                        dragOffsetY = if (isThisDragging) dragOffsetY else animatedYield,
                        onClick = { onOpen(c.id) },
                        onArchive = { onArchive(c.id) },
                        onDelete = { onDelete(c.id) },
                        onReorderStart = {
                            if (!c.isAnna) {
                                draggingId = c.id
                                draggingOriginIdx = idx
                            }
                        },
                        onReorderDrag = { dy -> dragOffsetY += dy },
                        onReorderEnd = {
                            if (draggingId == c.id) {
                                val finalTarget = targetIdx ?: idx
                                if (finalTarget != idx) onReorder(idx, finalTarget)
                            }
                            draggingId = null
                            draggingOriginIdx = null
                            dragOffsetY = 0f
                        },
                    )
                    HorizontalDivider(thickness = 0.5.dp, color = MaterialTheme.colorScheme.surfaceVariant)
                }
            }
        }
    }
}

@Composable
private fun EmptyState() {
    Column(
        modifier = Modifier.fillMaxSize().padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center,
    ) {
        Text("No conversations yet", style = MaterialTheme.typography.titleMedium)
        Spacer(Modifier.height(6.dp))
        Text(
            "Tap + to start a chat with one teammate, or pick several to make a group.",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

/// Deterministic per-conversation avatar palette (matches iOS + web).
private val chatAvatarPalette: List<androidx.compose.ui.graphics.Color> = listOf(
    androidx.compose.ui.graphics.Color(0xFF6366F1), // indigo
    androidx.compose.ui.graphics.Color(0xFF22A8C7), // teal
    androidx.compose.ui.graphics.Color(0xFF2EAF66), // green
    androidx.compose.ui.graphics.Color(0xFFF57336), // orange
    androidx.compose.ui.graphics.Color(0xFFE84D8C), // pink
    androidx.compose.ui.graphics.Color(0xFF8C5CD9), // violet
    androidx.compose.ui.graphics.Color(0xFFF2B233), // amber
    androidx.compose.ui.graphics.Color(0xFF4D82F2), // blue
)

private fun chatAvatarColor(c: ChatConversation): androidx.compose.ui.graphics.Color {
    if (c.isAnna) return androidx.compose.ui.graphics.Color(0xFF8C5CD9)
    return chatAvatarPalette[kotlin.math.abs(c.id) % chatAvatarPalette.size]
}

@Composable
private fun ConversationRow(
    c: ChatConversation,
    canDelete: Boolean,
    rowHeightPx: Float,
    isDragging: Boolean,
    dragOffsetY: Float,
    onClick: () -> Unit,
    onArchive: () -> Unit,
    onDelete: () -> Unit,
    onReorderStart: () -> Unit,
    onReorderDrag: (Float) -> Unit,
    onReorderEnd: () -> Unit,
) {
    val haptics = androidx.compose.ui.platform.LocalHapticFeedback.current
    val density = LocalDensity.current
    val scope = rememberCoroutineScope()

    // Swipe-left-to-reveal action buttons. Foreground row slides over a
    // fixed-width action drawer pinned to the trailing edge.
    val actionWidthDp: androidx.compose.ui.unit.Dp = if (canDelete && !c.isAnna) 168.dp
        else if (!c.isAnna) 84.dp
        else 0.dp
    val revealedPx = -with(density) { actionWidthDp.toPx() }
    val xOffset = remember(c.id) { Animatable(0f) }
    val isOpen by remember { derivedStateOf { xOffset.value <= revealedPx + 1f } }

    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(72.dp)
            // The dragged row floats above siblings.
            .zIndex(if (isDragging) 1f else 0f)
            .offset { androidx.compose.ui.unit.IntOffset(0, dragOffsetY.toInt()) }
            .graphicsLayer {
                if (isDragging) {
                    scaleX = 1.02f; scaleY = 1.02f
                    shadowElevation = 12f
                    alpha = 0.95f
                }
            }
    ) {
        // Action drawer (Archive + optional Delete) anchored to trailing
        // edge, revealed when the foreground slides left.
        if (!c.isAnna) {
            Row(
                modifier = Modifier
                    .matchParentSize()
                    .padding(end = 0.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.End,
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxHeight()
                        .width(84.dp)
                        .background(androidx.compose.ui.graphics.Color(0xFF6B7280))
                        .clickable {
                            scope.launch { xOffset.animateTo(0f) }
                            onArchive()
                        },
                    contentAlignment = Alignment.Center,
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Icon(
                            Icons.Outlined.Archive,
                            contentDescription = "Archive",
                            tint = androidx.compose.ui.graphics.Color.White,
                        )
                        Spacer(Modifier.height(2.dp))
                        Text("Archive",
                            color = androidx.compose.ui.graphics.Color.White,
                            style = MaterialTheme.typography.labelSmall)
                    }
                }
                if (canDelete) {
                    Box(
                        modifier = Modifier
                            .fillMaxHeight()
                            .width(84.dp)
                            .background(MaterialTheme.colorScheme.error)
                            .clickable {
                                scope.launch { xOffset.animateTo(0f) }
                                onDelete()
                            },
                        contentAlignment = Alignment.Center,
                    ) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Icon(
                                Icons.Outlined.Delete,
                                contentDescription = "Delete",
                                tint = MaterialTheme.colorScheme.onError,
                            )
                            Spacer(Modifier.height(2.dp))
                            Text("Delete",
                                color = MaterialTheme.colorScheme.onError,
                                style = MaterialTheme.typography.labelSmall)
                        }
                    }
                }
            }
        }

        // Foreground row — slides left to reveal the drawer; long-press
        // picks it up for vertical reorder (Anna excluded).
        Row(
            modifier = Modifier
                .fillMaxSize()
                .offset { androidx.compose.ui.unit.IntOffset(xOffset.value.toInt(), 0) }
                .background(MaterialTheme.colorScheme.surface)
                .pointerInput(c.id, canDelete) {
                    if (c.isAnna) return@pointerInput
                    detectHorizontalDragGestures(
                        onDragEnd = {
                            val target = if (xOffset.value <= revealedPx / 2f) revealedPx else 0f
                            scope.launch { xOffset.animateTo(target) }
                        },
                        onHorizontalDrag = { _, dx ->
                            val next = (xOffset.value + dx).coerceIn(revealedPx, 0f)
                            scope.launch { xOffset.snapTo(next) }
                        },
                    )
                }
                .pointerInput(c.id, isOpen) {
                    detectDragGesturesAfterLongPress(
                        onDragStart = {
                            if (c.isAnna) return@detectDragGesturesAfterLongPress
                            haptics.performHapticFeedback(
                                androidx.compose.ui.hapticfeedback.HapticFeedbackType.LongPress,
                            )
                            // If the swipe drawer is open, close it before
                            // entering reorder mode.
                            scope.launch { xOffset.animateTo(0f) }
                            onReorderStart()
                        },
                        onDrag = { _, drag -> onReorderDrag(drag.y) },
                        onDragEnd = { onReorderEnd() },
                        onDragCancel = { onReorderEnd() },
                    )
                }
                .clickable {
                    if (isOpen) {
                        scope.launch { xOffset.animateTo(0f) }
                    } else {
                        onClick()
                    }
                }
                .padding(horizontal = 16.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
        Box(
            modifier = Modifier
                .size(40.dp)
                .clip(CircleShape)
                .background(chatAvatarColor(c)),
            contentAlignment = Alignment.Center,
        ) {
            Text(
                initials(c.title),
                style = MaterialTheme.typography.labelMedium,
                fontWeight = FontWeight.SemiBold,
                color = androidx.compose.ui.graphics.Color.White,
            )
        }
        Spacer(Modifier.width(12.dp))
        Column(
            modifier = Modifier.weight(1f),
            verticalArrangement = Arrangement.SpaceBetween,
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    c.title,
                    fontWeight = FontWeight.SemiBold,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                )
                if (c.isGroup) {
                    Spacer(Modifier.width(6.dp))
                    androidx.compose.material3.Surface(
                        shape = androidx.compose.foundation.shape.RoundedCornerShape(4.dp),
                        color = MaterialTheme.colorScheme.surfaceVariant,
                    ) {
                        Text(
                            "Group",
                            style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.SemiBold),
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp),
                        )
                    }
                }
                Spacer(Modifier.weight(1f))
                Text(
                    c.last_message_at?.let { relTime(it) } ?: "",
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            Spacer(Modifier.height(2.dp))
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    c.last_message_preview ?: if (c.isGroup) "New group" else "No messages yet",
                    modifier = Modifier.weight(1f),
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    style = MaterialTheme.typography.bodySmall,
                )
                if (c.unread_count > 0) {
                    Spacer(Modifier.width(8.dp))
                    androidx.compose.material3.Surface(
                        shape = androidx.compose.foundation.shape.RoundedCornerShape(50),
                        color = MaterialTheme.colorScheme.primary,
                    ) {
                        Text(
                            if (c.unread_count > 99) "99+" else c.unread_count.toString(),
                            color = MaterialTheme.colorScheme.onPrimary,
                            style = MaterialTheme.typography.labelSmall,
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp),
                        )
                    }
                }
            }
        }
    }  // closes inner foreground Row
    }  // closes outer Box
}

@Composable
private fun ThreadPane(
    modifier: Modifier,
    userId: Int,
    userFirstName: String,
    token: String,
    conversationId: Int,
    state: ChatUiState,
    onBack: () -> Unit,
    onSend: (body: String, replyTo: Int?) -> Unit,
    onEdit: (messageId: Int, body: String) -> Unit,
    onDelete: (messageId: Int) -> Unit,
    onReact: (messageId: Int, emoji: String) -> Unit,
    onUpload: (body: String, replyTo: Int?, bytes: ByteArray, fileName: String, mimeType: String) -> Unit,
    onOpened: () -> Unit,
) {
    LaunchedEffect(conversationId) { onOpened() }

    val ctx = androidx.compose.ui.platform.LocalContext.current
    val settings = remember(ctx) { com.astrastaging.portal.data.settings.AppSettings(ctx) }
    val enterToSend by settings.enterToSend
        .collectAsState(initial = true)

    val msgs = state.messagesByConv[conversationId].orEmpty()
    val detail = state.detailByConv[conversationId]
    val title = detail?.title ?: state.conversations.firstOrNull { it.id == conversationId }?.title ?: "Chat"

    var draft by remember(conversationId) { mutableStateOf("") }
    var replyingTo by remember(conversationId) { mutableStateOf<ChatMessage?>(null) }
    var editing by remember(conversationId) { mutableStateOf<ChatMessage?>(null) }
    var emojiOpen by remember(conversationId) { mutableStateOf(false) }
    var cameraSheetOpen by remember(conversationId) { mutableStateOf(false) }
    var pendingAttachments by remember(conversationId) {
        mutableStateOf<List<PendingAttachment>>(emptyList())
    }
    val listState = rememberLazyListState()

    // System Photo Picker (multi-select) — permission-free, always
    // exposes the full library, and the picker itself shows checkmarks
    // on every selected item.
    val galleryPickerScope = rememberCoroutineScope()
    val galleryLauncher = androidx.activity.compose.rememberLauncherForActivityResult(
        androidx.activity.result.contract.ActivityResultContracts
            .PickMultipleVisualMedia(maxItems = 10)
    ) { uris: List<android.net.Uri> ->
        if (uris.isEmpty()) return@rememberLauncherForActivityResult
        galleryPickerScope.launch {
            val items = kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.IO) {
                uris.map { uri ->
                    val mime = ctx.contentResolver.getType(uri) ?: "image/jpeg"
                    val name = run {
                        var n: String? = null
                        runCatching {
                            ctx.contentResolver.query(uri, null, null, null, null)?.use { c ->
                                val idx = c.getColumnIndex(
                                    android.provider.OpenableColumns.DISPLAY_NAME,
                                )
                                if (idx >= 0 && c.moveToFirst()) n = c.getString(idx)
                            }
                        }
                        n ?: "media-${System.currentTimeMillis()}." +
                            mime.substringAfterLast('/').take(8)
                    }
                    PendingAttachment(uri, mime, name)
                }
            }
            pendingAttachments = pendingAttachments + items
        }
    }

    LaunchedEffect(msgs.size) {
        if (msgs.isNotEmpty()) listState.animateScrollToItem(msgs.lastIndex)
    }

    Scaffold(
        modifier = modifier.fillMaxSize(),
        topBar = {
            CenterAlignedTopAppBar(
                title = {
                    Text(title, fontWeight = FontWeight.SemiBold, maxLines = 1, overflow = TextOverflow.Ellipsis)
                },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Outlined.ArrowBack, contentDescription = "Back")
                    }
                },
            )
        },
        bottomBar = {
            Surface(tonalElevation = 2.dp) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .imePadding()
                ) {
                    val rt = replyingTo
                    if (rt != null) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .background(MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f))
                                .padding(horizontal = 14.dp, vertical = 8.dp),
                            verticalAlignment = Alignment.CenterVertically,
                        ) {
                            Box(modifier = Modifier
                                .width(3.dp).height(28.dp)
                                .background(MaterialTheme.colorScheme.primary))
                            Spacer(Modifier.width(8.dp))
                            Column(modifier = Modifier.weight(1f)) {
                                Text(
                                    "Replying to ${rt.sender?.display_name ?: ""}",
                                    style = MaterialTheme.typography.labelSmall,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                                )
                                Text(
                                    rt.body,
                                    style = MaterialTheme.typography.bodySmall,
                                    maxLines = 1,
                                    overflow = TextOverflow.Ellipsis,
                                )
                            }
                            IconButton(onClick = { replyingTo = null }) {
                                Icon(
                                    Icons.Outlined.Close,
                                    contentDescription = "Cancel reply",
                                    modifier = Modifier.size(18.dp),
                                )
                            }
                        }
                    }
                    val ed = editing
                    if (ed != null) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .background(MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f))
                                .padding(horizontal = 14.dp, vertical = 8.dp),
                            verticalAlignment = Alignment.CenterVertically,
                        ) {
                            Icon(
                                ChatComposeIcon, contentDescription = null,
                                tint = MaterialTheme.colorScheme.primary,
                                modifier = Modifier.size(16.dp),
                            )
                            Spacer(Modifier.width(8.dp))
                            Text("Editing message",
                                style = MaterialTheme.typography.labelSmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant)
                            Spacer(Modifier.weight(1f))
                            IconButton(onClick = { editing = null; draft = "" }) {
                                Icon(
                                    Icons.Outlined.Close,
                                    contentDescription = "Cancel edit",
                                    modifier = Modifier.size(18.dp),
                                )
                            }
                        }
                    }
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 8.dp, vertical = 4.dp),
                        verticalAlignment = Alignment.Bottom,
                    ) {
                        Column(
                            modifier = Modifier
                                .weight(1f)
                                .background(
                                    MaterialTheme.colorScheme.surface,
                                    RoundedCornerShape(20.dp),
                                )
                                .border(
                                    1.dp,
                                    MaterialTheme.colorScheme.primary,
                                    RoundedCornerShape(20.dp),
                                ),
                        ) {
                            if (pendingAttachments.isNotEmpty()) {
                                androidx.compose.foundation.lazy.LazyRow(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .padding(start = 12.dp, end = 8.dp, top = 4.dp),
                                    horizontalArrangement = Arrangement.spacedBy(4.dp),
                                ) {
                                    items(
                                        count = pendingAttachments.size,
                                        key = { i -> pendingAttachments[i].uri.toString() },
                                    ) { i ->
                                        val att = pendingAttachments[i]
                                        PendingAttachmentThumbnail(
                                            attachment = att,
                                            onRemove = {
                                                pendingAttachments =
                                                    pendingAttachments.filter { it.uri != att.uri }
                                            },
                                        )
                                    }
                                }
                            }
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .heightIn(min = 40.dp)
                                    .padding(start = 16.dp, end = 4.dp),
                                verticalAlignment = Alignment.CenterVertically,
                            ) {
                                Box(
                                    modifier = Modifier.weight(1f),
                                    contentAlignment = Alignment.CenterStart,
                                ) {
                                    BasicTextField(
                                        value = draft,
                                        onValueChange = { newValue ->
                                            if (enterToSend && newValue.endsWith("\n")) {
                                                val trimmed = newValue.dropLast(1)
                                                if (trimmed.trim().isNotEmpty() ||
                                                    pendingAttachments.isNotEmpty()) {
                                                    sendComposed(
                                                        body = trimmed.trim(),
                                                        editing = editing,
                                                        replyingTo = replyingTo,
                                                        attachments = pendingAttachments,
                                                        onSend = onSend,
                                                        onEdit = onEdit,
                                                        onUpload = onUpload,
                                                        ctx = ctx,
                                                        scope = galleryPickerScope,
                                                    )
                                                    draft = ""; editing = null; replyingTo = null
                                                    pendingAttachments = emptyList()
                                                } else {
                                                    draft = trimmed
                                                }
                                            } else {
                                                draft = newValue
                                            }
                                        },
                                        textStyle = MaterialTheme.typography.bodyMedium.copy(
                                            color = MaterialTheme.colorScheme.onSurface,
                                        ),
                                        cursorBrush = SolidColor(MaterialTheme.colorScheme.primary),
                                        maxLines = 4,
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .padding(vertical = 8.dp),
                                    )
                                    if (draft.isEmpty()) {
                                        Text(
                                            if (pendingAttachments.isNotEmpty()) "Add a caption…" else "Message",
                                            style = MaterialTheme.typography.bodyMedium,
                                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                                        )
                                    }
                                }
                                if (editing == null) {
                                    IconButton(
                                        onClick = { emojiOpen = true },
                                        modifier = Modifier.size(32.dp),
                                    ) {
                                        Icon(
                                            Icons.Outlined.Mood,
                                            contentDescription = "Insert emoji",
                                            tint = MaterialTheme.colorScheme.primary,
                                            modifier = Modifier.size(22.dp),
                                        )
                                    }
                                    IconButton(
                                        onClick = { cameraSheetOpen = true },
                                        modifier = Modifier.size(32.dp),
                                    ) {
                                        Icon(
                                            Icons.Outlined.PhotoCamera,
                                            contentDescription = "Open camera",
                                            tint = MaterialTheme.colorScheme.primary,
                                            modifier = Modifier.size(22.dp),
                                        )
                                    }
                                    IconButton(
                                        onClick = {
                                            galleryLauncher.launch(
                                                androidx.activity.result.PickVisualMediaRequest(
                                                    androidx.activity.result.contract.ActivityResultContracts
                                                        .PickVisualMedia.ImageAndVideo,
                                                ),
                                            )
                                        },
                                        modifier = Modifier.size(32.dp),
                                    ) {
                                        Icon(
                                            Icons.Outlined.Image,
                                            contentDescription = "Open gallery",
                                            tint = MaterialTheme.colorScheme.primary,
                                            modifier = Modifier.size(22.dp),
                                        )
                                    }
                                }
                            }
                        }
                        Spacer(Modifier.width(4.dp))
                        val canSend = draft.trim().isNotEmpty() || pendingAttachments.isNotEmpty()
                        IconButton(
                            onClick = {
                                if (canSend) {
                                    sendComposed(
                                        body = draft.trim(),
                                        editing = editing,
                                        replyingTo = replyingTo,
                                        attachments = pendingAttachments,
                                        onSend = onSend,
                                        onEdit = onEdit,
                                        onUpload = onUpload,
                                        ctx = ctx,
                                        scope = galleryPickerScope,
                                    )
                                    draft = ""; editing = null; replyingTo = null
                                    pendingAttachments = emptyList()
                                }
                            },
                            enabled = canSend,
                            modifier = Modifier.size(40.dp),
                        ) {
                            Icon(
                                Icons.AutoMirrored.Outlined.Send,
                                contentDescription = "Send",
                                tint = if (canSend) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurface.copy(alpha = 0.3f),
                            )
                        }
                    }
                }
            }
        }
    ) { padding ->
        LazyColumn(
            state = listState,
            modifier = Modifier
                .fillMaxSize()
                .padding(padding),
            contentPadding = PaddingValues(horizontal = 12.dp, vertical = 10.dp),
            verticalArrangement = Arrangement.spacedBy(2.dp),
        ) {
            itemsIndexed(msgs, key = { _, m -> m.id }) { idx, m ->
                if (shouldShowDaySeparator(msgs, idx)) {
                    DaySeparator(text = dayHeader(m.created_at))
                }
                MessageBubble(
                    message = m,
                    isMine = m.sender_id == userId,
                    myUserId = userId,
                    myFirstName = userFirstName,
                    onSwipeReply = { replyingTo = m; editing = null },
                    onEdit = {
                        editing = m
                        replyingTo = null
                        draft = m.body
                    },
                    onDelete = { onDelete(m.id) },
                    onReact = { e -> onReact(m.id, e) },
                )
            }
        }
    }

    if (emojiOpen) {
        EmojiPickerSheet(
            onDismiss = { emojiOpen = false },
            onPick = { e ->
                draft = draft + e
                emojiOpen = false
            },
        )
    }

    if (cameraSheetOpen) {
        ChatCameraDialog(
            onDismiss = { cameraSheetOpen = false },
            onCaptured = { bytes, fileName, mime ->
                val pendingBody = draft
                val pendingReply = replyingTo?.id
                draft = ""; replyingTo = null
                cameraSheetOpen = false
                onUpload(pendingBody, pendingReply, bytes, fileName, mime)
            },
        )
    }

}

private fun flushDraft(
    body: String,
    editing: ChatMessage?,
    replyingTo: ChatMessage?,
    onSend: (String, Int?) -> Unit,
    onEdit: (Int, String) -> Unit,
) {
    if (editing != null) {
        onEdit(editing.id, body)
    } else {
        onSend(body, replyingTo?.id)
    }
}

/** Compose-step entry point: handles edit, attachment-only, text-only,
 *  and "text + attachments" all in one place. The body text rides along
 *  with the *first* attachment so users get a single "captioned" message
 *  followed by the rest as standalone uploads. */
private fun sendComposed(
    body: String,
    editing: ChatMessage?,
    replyingTo: ChatMessage?,
    attachments: List<PendingAttachment>,
    onSend: (String, Int?) -> Unit,
    onEdit: (Int, String) -> Unit,
    onUpload: (body: String, replyTo: Int?, bytes: ByteArray, fileName: String, mime: String) -> Unit,
    ctx: android.content.Context,
    scope: kotlinx.coroutines.CoroutineScope,
) {
    if (editing != null) {
        onEdit(editing.id, body)
        return
    }
    if (attachments.isEmpty()) {
        if (body.isNotEmpty()) onSend(body, replyingTo?.id)
        return
    }
    val replyId = replyingTo?.id
    scope.launch {
        attachments.forEachIndexed { idx, att ->
            val bytes = kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.IO) {
                runCatching {
                    ctx.contentResolver.openInputStream(att.uri)?.use { it.readBytes() }
                }.getOrNull()
            } ?: return@forEachIndexed
            val attBody = if (idx == 0) body else ""
            val attReply = if (idx == 0) replyId else null
            onUpload(attBody, attReply, bytes, att.displayName, att.mimeType)
        }
    }
}

private fun shouldShowDaySeparator(msgs: List<ChatMessage>, idx: Int): Boolean {
    if (idx == 0) return true
    val cur = msgs[idx].created_at ?: return false
    val prev = msgs[idx - 1].created_at ?: return false
    return cur.take(10) != prev.take(10)  // YYYY-MM-DD prefix
}

private fun dayHeader(iso: String?): String {
    if (iso == null) return ""
    val parsed = runCatching {
        java.time.LocalDateTime.parse(iso, java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"))
    }.getOrNull() ?: return ""
    val date = parsed.toLocalDate()
    val today = java.time.LocalDate.now(java.time.ZoneOffset.UTC)
    return when {
        date == today -> "Today"
        date == today.minusDays(1) -> "Yesterday"
        else -> date.format(java.time.format.DateTimeFormatter.ofPattern("EEEE, MMM d"))
    }
}

@Composable
private fun DaySeparator(text: String) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text,
            style = MaterialTheme.typography.labelMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

private fun senderAvatarColor(senderId: Int): androidx.compose.ui.graphics.Color {
    return chatAvatarPalette[kotlin.math.abs(senderId) % chatAvatarPalette.size]
}

private fun messageHeaderTimestamp(iso: String?): String {
    if (iso == null) return ""
    val parsed = runCatching {
        java.time.LocalDateTime.parse(iso, java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"))
    }.getOrNull() ?: return ""
    return parsed.format(java.time.format.DateTimeFormatter.ofPattern("MMM d, h:mm a"))
}

private fun isWithinEditWindow(iso: String?): Boolean {
    if (iso == null) return false
    val parsed = runCatching {
        java.time.LocalDateTime.parse(iso, java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"))
    }.getOrNull() ?: return false
    val nowUtc = java.time.LocalDateTime.now(java.time.ZoneOffset.UTC)
    val secs = java.time.Duration.between(parsed, nowUtc).seconds
    return secs in 0..10
}

private val chatQuickEmojis = listOf("👍", "❤️", "😂", "😮", "😢", "🎉")

/** Bearer token piped down to AttachmentBubble so Coil can authenticate
 *  requests to /api/v1/chat/attachments/{id}. Provided by ChatScreen. */
private val LocalChatToken =
    androidx.compose.runtime.compositionLocalOf<String> {
        error("LocalChatToken not provided")
    }

@Composable
private fun MessageBubble(
    message: ChatMessage,
    isMine: Boolean,
    myUserId: Int,
    myFirstName: String,
    onSwipeReply: () -> Unit,
    onEdit: () -> Unit,
    onDelete: () -> Unit,
    onReact: (String) -> Unit,
) {
    val haptics = androidx.compose.ui.platform.LocalHapticFeedback.current
    val density = LocalDensity.current
    val scope = rememberCoroutineScope()
    val xOffset = remember(message.id) { Animatable(0f) }
    val swipeThresholdPx = with(density) { 70.dp.toPx() }
    var menuOpen by remember(message.id) { mutableStateOf(false) }
    var morePickerOpen by remember(message.id) { mutableStateOf(false) }
    val isDeleted = message.deleted || message.deleted_at != null
    val canEditDelete = isMine && !isDeleted && isWithinEditWindow(message.created_at)
    val senderName = if (isMine) "You" else (message.sender?.display_name ?: "Unknown")
    // Avatar uses the actual first name even when isMine — header still says "You"
    // but the circle should match the per-person color/initial scheme everywhere else.
    val avatarLabel = if (isMine) myFirstName.ifBlank { senderName }
                      else (message.sender?.display_name ?: senderName)

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .offset { androidx.compose.ui.unit.IntOffset(xOffset.value.toInt(), 0) }
            .pointerInput(message.id, isDeleted) {
                if (isDeleted) return@pointerInput
                detectHorizontalDragGestures(
                    onDragEnd = {
                        if (xOffset.value > swipeThresholdPx) {
                            haptics.performHapticFeedback(
                                androidx.compose.ui.hapticfeedback.HapticFeedbackType.LongPress,
                            )
                            onSwipeReply()
                        }
                        scope.launch { xOffset.animateTo(0f) }
                    },
                    onHorizontalDrag = { _, dx ->
                        if (dx > 0 || xOffset.value > 0) {
                            val next = (xOffset.value + dx).coerceIn(0f, 90f)
                            scope.launch { xOffset.snapTo(next) }
                        }
                    },
                )
            }
            .pointerInput(message.id, isDeleted) {
                if (isDeleted) return@pointerInput
                detectTapGestures(onLongPress = {
                    haptics.performHapticFeedback(
                        androidx.compose.ui.hapticfeedback.HapticFeedbackType.LongPress,
                    )
                    menuOpen = true
                })
            }
            .padding(horizontal = 4.dp, vertical = 6.dp),
        verticalAlignment = Alignment.Top,
    ) {
        Box(
            modifier = Modifier
                .size(32.dp)
                .clip(CircleShape)
                .background(senderAvatarColor(message.sender_id)),
            contentAlignment = Alignment.Center,
        ) {
            Text(
                initials(avatarLabel),
                style = MaterialTheme.typography.labelMedium,
                fontWeight = FontWeight.SemiBold,
                color = androidx.compose.ui.graphics.Color.White,
            )
        }
        Spacer(Modifier.width(10.dp))
        Column(modifier = Modifier.weight(1f)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    senderName,
                    style = MaterialTheme.typography.bodyMedium.copy(fontWeight = FontWeight.SemiBold),
                )
                Spacer(Modifier.width(6.dp))
                Text(
                    messageHeaderTimestamp(message.created_at),
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            Spacer(Modifier.height(2.dp))
            // Reply-to chip
            message.reply_to?.let { r ->
                Row(modifier = Modifier
                    .padding(bottom = 4.dp)
                    .fillMaxWidth()
                ) {
                    Box(modifier = Modifier
                        .width(3.dp).height(28.dp)
                        .background(MaterialTheme.colorScheme.outline))
                    Spacer(Modifier.width(6.dp))
                    Column {
                        Text(
                            r.sender_name,
                            style = MaterialTheme.typography.labelSmall,
                            fontWeight = FontWeight.SemiBold,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                        Text(
                            if (r.deleted) "(message deleted)" else r.body,
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            maxLines = 2, overflow = TextOverflow.Ellipsis,
                        )
                    }
                }
            }
            // Body bubble (or deleted placeholder)
            if (isDeleted) {
                Surface(
                    shape = RoundedCornerShape(12.dp),
                    color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f),
                ) {
                    Text(
                        "Message deleted",
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
                        style = MaterialTheme.typography.bodyMedium.copy(
                            fontStyle = androidx.compose.ui.text.font.FontStyle.Italic,
                        ),
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            } else {
                if (message.attachments.isNotEmpty()) {
                    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        message.attachments.forEach { a ->
                            AttachmentBubble(attachment = a, token = LocalChatToken.current)
                        }
                    }
                }
                if (message.body.isNotEmpty() && message.body != "📎") {
                    Surface(
                        shape = RoundedCornerShape(12.dp),
                        color = if (isMine)
                            MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.4f)
                        else MaterialTheme.colorScheme.surfaceVariant,
                    ) {
                        Text(
                            message.body,
                            modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
                            color = MaterialTheme.colorScheme.onSurface,
                        )
                    }
                }
            }
            if (message.edited_at != null && !isDeleted) {
                Text(
                    "(edited)",
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }

            // Reaction chips.
            if (message.reactions.isNotEmpty()) {
                Row(
                    modifier = Modifier.padding(top = 4.dp),
                    horizontalArrangement = Arrangement.spacedBy(6.dp),
                ) {
                    message.reactions.forEach { r ->
                        val mine = myUserId in r.user_ids
                        Surface(
                            shape = RoundedCornerShape(50),
                            color = if (mine)
                                MaterialTheme.colorScheme.primary.copy(alpha = 0.15f)
                            else MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.7f),
                            border = androidx.compose.foundation.BorderStroke(
                                1.dp,
                                if (mine) MaterialTheme.colorScheme.primary
                                else MaterialTheme.colorScheme.outline.copy(alpha = 0.3f),
                            ),
                            modifier = Modifier.clickable { onReact(r.emoji) },
                        ) {
                            Row(
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp),
                                verticalAlignment = Alignment.CenterVertically,
                            ) {
                                Text(r.emoji, style = MaterialTheme.typography.bodyMedium)
                                Spacer(Modifier.width(4.dp))
                                Text(
                                    r.count.toString(),
                                    style = MaterialTheme.typography.labelMedium,
                                    color = if (mine) MaterialTheme.colorScheme.primary
                                    else MaterialTheme.colorScheme.onSurface,
                                )
                            }
                        }
                    }
                }
            }
        }

        androidx.compose.material3.DropdownMenu(
            expanded = menuOpen,
            onDismissRequest = { menuOpen = false },
        ) {
            // Quick reactions row.
            Row(
                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                horizontalArrangement = Arrangement.spacedBy(4.dp),
            ) {
                chatQuickEmojis.forEach { e ->
                    Box(
                        modifier = Modifier
                            .size(36.dp)
                            .clip(CircleShape)
                            .clickable { menuOpen = false; onReact(e) },
                        contentAlignment = Alignment.Center,
                    ) {
                        Text(e, style = MaterialTheme.typography.titleMedium)
                    }
                }
                Box(
                    modifier = Modifier
                        .size(36.dp)
                        .clip(CircleShape)
                        .clickable { menuOpen = false; morePickerOpen = true },
                    contentAlignment = Alignment.Center,
                ) {
                    Text("➕", style = MaterialTheme.typography.titleMedium)
                }
            }
            HorizontalDivider()
            androidx.compose.material3.DropdownMenuItem(
                text = { Text("Reply") },
                onClick = { menuOpen = false; onSwipeReply() },
            )
            if (canEditDelete) {
                androidx.compose.material3.DropdownMenuItem(
                    text = { Text("Edit") },
                    onClick = { menuOpen = false; onEdit() },
                )
                androidx.compose.material3.DropdownMenuItem(
                    text = { Text("Delete", color = MaterialTheme.colorScheme.error) },
                    onClick = { menuOpen = false; onDelete() },
                )
            }
        }

        if (morePickerOpen) {
            EmojiPickerSheet(
                onDismiss = { morePickerOpen = false },
                onPick = { e -> morePickerOpen = false; onReact(e) },
            )
        }
    }
}

/**
 * Render a single chat attachment. Photos use Coil with an Authorization
 * header (the attachment endpoint is auth-protected). Videos and files
 * fall back to a tappable card that opens via Intent.ACTION_VIEW.
 */
@Composable
private fun AttachmentBubble(attachment: ChatAttachment, token: String) {
    val ctx = androidx.compose.ui.platform.LocalContext.current
    val fullUrl = remember(attachment.url) {
        com.astrastaging.portal.BuildConfig.API_BASE_URL.trimEnd('/') + attachment.url
    }
    var viewerOpen by remember(attachment.id) { mutableStateOf(false) }
    when (attachment.kind) {
        "photo" -> {
            val request = remember(fullUrl, token) {
                coil.request.ImageRequest.Builder(ctx)
                    .data(fullUrl)
                    .addHeader("Authorization", "Bearer $token")
                    .build()
            }
            coil.compose.AsyncImage(
                model = request,
                contentDescription = attachment.original_name,
                contentScale = androidx.compose.ui.layout.ContentScale.Fit,
                modifier = Modifier
                    .heightIn(max = 240.dp)
                    .clip(RoundedCornerShape(10.dp))
                    .clickable { viewerOpen = true },
            )
            if (viewerOpen) {
                FullscreenPhotoViewer(
                    url = fullUrl,
                    token = token,
                    onDismiss = { viewerOpen = false },
                )
            }
        }
        "video" -> {
            Surface(
                shape = RoundedCornerShape(10.dp),
                color = MaterialTheme.colorScheme.surfaceVariant,
            ) {
                Row(
                    modifier = Modifier.padding(horizontal = 12.dp, vertical = 10.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text("▶", style = MaterialTheme.typography.headlineSmall)
                    Spacer(Modifier.width(8.dp))
                    Text(
                        attachment.original_name ?: "Video",
                        maxLines = 1, overflow = TextOverflow.Ellipsis,
                    )
                }
            }
        }
        else -> {
            Surface(
                shape = RoundedCornerShape(10.dp),
                color = MaterialTheme.colorScheme.surfaceVariant,
            ) {
                Row(
                    modifier = Modifier.padding(horizontal = 12.dp, vertical = 10.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text("📎", style = MaterialTheme.typography.titleMedium)
                    Spacer(Modifier.width(8.dp))
                    Text(
                        attachment.original_name ?: "File",
                        maxLines = 1, overflow = TextOverflow.Ellipsis,
                    )
                }
            }
        }
    }
}

/** Full-screen image viewer with bearer-auth headers. The chat
 *  attachment endpoint is authenticated, so opening the URL in a browser
 *  via Intent.ACTION_VIEW returns 401 — we render in-app instead. */
@Composable
private fun FullscreenPhotoViewer(
    url: String,
    token: String,
    onDismiss: () -> Unit,
) {
    val ctx = androidx.compose.ui.platform.LocalContext.current
    val request = remember(url, token) {
        coil.request.ImageRequest.Builder(ctx)
            .data(url)
            .addHeader("Authorization", "Bearer $token")
            .build()
    }
    androidx.compose.ui.window.Dialog(
        onDismissRequest = onDismiss,
        properties = androidx.compose.ui.window.DialogProperties(
            usePlatformDefaultWidth = false,
            dismissOnBackPress = true,
            dismissOnClickOutside = true,
        ),
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(androidx.compose.ui.graphics.Color.Black)
                .clickable { onDismiss() },
            contentAlignment = Alignment.Center,
        ) {
            coil.compose.AsyncImage(
                model = request,
                contentDescription = null,
                contentScale = androidx.compose.ui.layout.ContentScale.Fit,
                modifier = Modifier.fillMaxSize(),
            )
            Box(
                modifier = Modifier
                    .align(Alignment.TopStart)
                    .windowInsetsPadding(WindowInsets.systemBars)
                    .padding(horizontal = 12.dp, vertical = 8.dp)
                    .size(44.dp)
                    .background(
                        androidx.compose.ui.graphics.Color.Black.copy(alpha = 0.55f),
                        CircleShape,
                    )
                    .border(
                        1.5.dp,
                        androidx.compose.ui.graphics.Color.White.copy(alpha = 0.9f),
                        CircleShape,
                    )
                    .clickable { onDismiss() },
                contentAlignment = Alignment.Center,
            ) {
                Icon(
                    Icons.Outlined.Close,
                    contentDescription = "Close",
                    tint = androidx.compose.ui.graphics.Color.White,
                    modifier = Modifier.size(22.dp),
                )
            }
        }
    }
}

@Composable
private fun EmojiPickerSheet(onDismiss: () -> Unit, onPick: (String) -> Unit) {
    val sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)
    val palette = listOf(
        "👍", "👎", "❤️", "🔥", "🎉", "👏", "🙏", "😂",
        "😄", "😎", "😮", "😢", "😡", "🤔", "💯", "✅",
        "❌", "⏰", "📌", "📷", "🚚", "🛠️", "💪", "💰",
    )
    ModalBottomSheet(onDismissRequest = onDismiss, sheetState = sheetState) {
        LazyVerticalGrid(
            columns = GridCells.Fixed(6),
            contentPadding = PaddingValues(16.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
            modifier = Modifier.fillMaxWidth(),
        ) {
            lazyGridItems(palette, key = { it }) { e ->
                Box(
                    modifier = Modifier
                        .size(52.dp)
                        .clip(RoundedCornerShape(12.dp))
                        .background(MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f))
                        .clickable { onPick(e) },
                    contentAlignment = Alignment.Center,
                ) {
                    Text(e, style = MaterialTheme.typography.headlineSmall)
                }
            }
        }
    }
}

@Composable
private fun NewConversationSheet(
    employees: List<ChatEmployee>,
    onDismiss: () -> Unit,
    onConfirmDM: (Int) -> Unit,
    onConfirmGroup: (String, List<Int>) -> Unit,
) {
    val sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)
    // Selection in tap order — drives the auto-generated group title.
    var pickedOrder by remember { mutableStateOf(emptyList<Int>()) }
    var groupTitle by remember { mutableStateOf("") }
    var userEditedTitle by remember { mutableStateOf(false) }

    val byId = remember(employees) { employees.associateBy { it.id } }
    val autoTitle by remember(pickedOrder, employees) {
        derivedStateOf {
            pickedOrder.mapNotNull { byId[it]?.display_name }.joinToString(", ")
        }
    }
    val isGroupMode = pickedOrder.size >= 2

    LaunchedEffect(autoTitle) {
        if (!userEditedTitle) groupTitle = autoTitle
    }

    ModalBottomSheet(onDismissRequest = onDismiss, sheetState = sheetState) {
        Column(modifier = Modifier
            .fillMaxWidth()
            .padding(bottom = 24.dp)
        ) {
            // No "New chat" title, per spec.
            if (isGroupMode) {
                OutlinedTextField(
                    value = groupTitle,
                    onValueChange = { newValue ->
                        groupTitle = newValue
                        userEditedTitle = newValue.isNotEmpty() && newValue != autoTitle
                        if (newValue.isEmpty()) userEditedTitle = false
                    },
                    label = { Text("Group name") },
                    singleLine = true,
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp, vertical = 6.dp),
                )
            }
            // 2-column grid of employee cards.
            if (employees.isEmpty()) {
                Box(
                    modifier = Modifier.fillMaxWidth().padding(40.dp),
                    contentAlignment = Alignment.Center,
                ) { CircularProgressIndicator() }
            } else {
                LazyVerticalGrid(
                    columns = GridCells.Fixed(2),
                    contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
                    horizontalArrangement = Arrangement.spacedBy(10.dp),
                    verticalArrangement = Arrangement.spacedBy(10.dp),
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(420.dp),
                ) {
                    lazyGridItems(employees, key = { it.id }) { e ->
                        EmployeeCard(
                            employee = e,
                            selected = pickedOrder.contains(e.id),
                            onTap = {
                                pickedOrder = if (pickedOrder.contains(e.id)) {
                                    pickedOrder - e.id
                                } else {
                                    pickedOrder + e.id
                                }
                            },
                        )
                    }
                }
            }
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp),
                horizontalArrangement = Arrangement.End,
            ) {
                TextButton(onClick = onDismiss) { Text("Cancel") }
                Spacer(Modifier.width(8.dp))
                val canConfirm = when {
                    pickedOrder.size == 1 -> true
                    pickedOrder.size >= 2 -> {
                        val resolved = if (userEditedTitle) groupTitle.trim() else autoTitle
                        resolved.isNotEmpty()
                    }
                    else -> false
                }
                Button(
                    enabled = canConfirm,
                    onClick = {
                        if (pickedOrder.size == 1) {
                            onConfirmDM(pickedOrder.first())
                        } else if (pickedOrder.size >= 2) {
                            val resolved = if (userEditedTitle) groupTitle.trim() else autoTitle
                            onConfirmGroup(resolved, pickedOrder)
                        }
                    }
                ) {
                    Text(if (isGroupMode) "Create" else "Start")
                }
            }
        }
    }
}

@Composable
private fun EmployeeCard(
    employee: ChatEmployee,
    selected: Boolean,
    onTap: () -> Unit,
) {
    val color = chatAvatarPalette[kotlin.math.abs(employee.id) % chatAvatarPalette.size]
    Surface(
        shape = RoundedCornerShape(14.dp),
        color = if (selected)
            MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.4f)
        else MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f),
        border = if (selected)
            androidx.compose.foundation.BorderStroke(1.5.dp, MaterialTheme.colorScheme.primary)
        else null,
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onTap),
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 14.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Box(
                modifier = Modifier
                    .size(52.dp)
                    .clip(CircleShape)
                    .background(color),
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    initials(employee.display_name),
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold,
                    color = androidx.compose.ui.graphics.Color.White,
                )
            }
            Spacer(Modifier.height(8.dp))
            Text(
                employee.display_name,
                style = MaterialTheme.typography.bodyMedium.copy(fontWeight = FontWeight.Medium),
                maxLines = 1, overflow = TextOverflow.Ellipsis,
            )
        }
    }
}

private fun initials(s: String): String {
    val parts = s.trim().split(" ").filter { it.isNotEmpty() }.take(2)
    return parts.mapNotNull { it.firstOrNull()?.toString() }.joinToString("").uppercase()
}

private fun relTime(s: String): String {
    val d: LocalDateTime = runCatching {
        // server returns "yyyy-MM-dd HH:mm:ss" UTC
        LocalDateTime.parse(s, DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"))
    }.getOrNull() ?: runCatching {
        OffsetDateTime.parse(s).toLocalDateTime()
    }.getOrNull() ?: return s

    val now = LocalDateTime.now(ZoneOffset.UTC)
    val secs = Duration.between(d, now).seconds
    return when {
        secs < 60 -> "just now"
        secs < 3600 -> "${secs / 60}m"
        secs < 86400 -> "${secs / 3600}h"
        secs < 7 * 86400 -> "${secs / 86400}d"
        else -> d.toLocalDate().toString()
    }
}

/** A photo or video the user has staged in the composer but not yet
 *  sent. Renders as a square thumbnail with an X to remove. */
internal data class PendingAttachment(
    val uri: android.net.Uri,
    val mimeType: String,
    val displayName: String,
)

@Composable
private fun PendingAttachmentThumbnail(
    attachment: PendingAttachment,
    onRemove: () -> Unit,
) {
    Box(
        modifier = Modifier
            .size(64.dp)
            .padding(top = 6.dp, end = 6.dp),
    ) {
        coil.compose.AsyncImage(
            model = attachment.uri,
            contentDescription = null,
            contentScale = androidx.compose.ui.layout.ContentScale.Crop,
            modifier = Modifier
                .matchParentSize()
                .clip(RoundedCornerShape(8.dp))
                .background(androidx.compose.ui.graphics.Color.Black),
        )
        if (attachment.mimeType.startsWith("video/")) {
            Icon(
                Icons.Outlined.PlayCircle,
                contentDescription = null,
                tint = androidx.compose.ui.graphics.Color.White.copy(alpha = 0.9f),
                modifier = Modifier
                    .align(Alignment.Center)
                    .size(22.dp),
            )
        }
        Box(
            modifier = Modifier
                .align(Alignment.TopEnd)
                .size(20.dp)
                .background(
                    androidx.compose.ui.graphics.Color.Black.copy(alpha = 0.75f),
                    CircleShape,
                )
                .border(
                    1.dp,
                    androidx.compose.ui.graphics.Color.White.copy(alpha = 0.9f),
                    CircleShape,
                )
                .clickable { onRemove() },
            contentAlignment = Alignment.Center,
        ) {
            Icon(
                Icons.Outlined.Close,
                contentDescription = "Remove attachment",
                tint = androidx.compose.ui.graphics.Color.White,
                modifier = Modifier.size(12.dp),
            )
        }
    }
}

