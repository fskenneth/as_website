@file:OptIn(
    androidx.compose.foundation.ExperimentalFoundationApi::class,
    androidx.compose.material3.ExperimentalMaterial3Api::class,
)

package com.astrastaging.portal.ui.main

import android.content.ClipData
import android.content.ClipDescription
import androidx.activity.compose.BackHandler
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.draganddrop.dragAndDropSource
import androidx.compose.foundation.draganddrop.dragAndDropTarget
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.lazy.items as lazyRowItems
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.foundation.layout.offset
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.derivedStateOf
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.runtime.snapshots.SnapshotStateList
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draganddrop.DragAndDropEvent
import androidx.compose.ui.draganddrop.DragAndDropTarget
import androidx.compose.ui.draganddrop.DragAndDropTransferData
import androidx.compose.ui.draganddrop.mimeTypes
import androidx.compose.ui.draganddrop.toAndroidDragEvent
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.astrastaging.portal.data.ApiUser
import com.astrastaging.portal.data.MenuPreferencesStore
import com.astrastaging.portal.ui.items.ItemsScreen
import com.astrastaging.portal.ui.me.MeScreen
import com.astrastaging.portal.ui.chat.ChatScreen
import com.astrastaging.portal.ui.chat.ChatToastBanner
import com.astrastaging.portal.ui.chat.ChatViewModel
import com.astrastaging.portal.ui.consultation.ConsultationScreen
import com.astrastaging.portal.ui.stubs.HRAccountingScreen
import com.astrastaging.portal.ui.stubs.SalesManagementScreen
import com.astrastaging.portal.ui.taskboard.TaskBoardScreen

private const val MIME_MENU_ITEM = "application/x-astra-menu-item"

/**
 * Home-screen-style menu shell: 4-slot dock + "More" overflow sheet, with a
 * long-press-to-customize edit mode that lets the user drag any tile onto any
 * other tile to swap their slots (across the dock/overflow boundary too).
 *
 * Layout is persisted per-install via [MenuPreferencesStore].
 */
@Composable
fun MainScreen(
    user: ApiUser,
    token: String,
    onLogout: () -> Unit,
) {
    val context = LocalContext.current
    val store = remember { MenuPreferencesStore(context) }
    val order: SnapshotStateList<MenuItem> = remember {
        mutableStateListOf<MenuItem>().apply { addAll(store.load()) }
    }
    // App-scoped chat VM so SSE stays alive on every tab. The FAB badge,
    // toast banner, and chat tab all read from this same instance.
    val chatVm: ChatViewModel = androidx.lifecycle.viewmodel.compose.viewModel()
    LaunchedEffect(token, user.id) {
        chatVm.setSelfId(user.id)
        chatVm.bind(token)
        chatVm.refreshList(token)
        chatVm.loadEmployees(token)
    }

    // Live drag state — the preview reorders tiles the moment a drag
    // enters a target, so the swap animation plays before the drop.
    var draggedKey by remember { mutableStateOf<String?>(null) }
    var hoveredKey by remember { mutableStateOf<String?>(null) }

    val previewOrder by remember {
        derivedStateOf {
            val d = draggedKey
            val h = hoveredKey
            if (d != null && h != null && d != h) {
                val mut = order.toMutableList()
                val i = mut.indexOfFirst { it.key == d }
                val j = mut.indexOfFirst { it.key == h }
                if (i != -1 && j != -1) {
                    val tmp = mut[i]
                    mut[i] = mut[j]
                    mut[j] = tmp
                }
                mut.toList()
            } else order.toList()
        }
    }

    val visible by remember(user.roleLevel) {
        derivedStateOf { previewOrder.filter { it.minRoleLevel <= user.roleLevel } }
    }
    val dock by remember { derivedStateOf { visible.take(4) } }
    val overflow by remember { derivedStateOf { visible.drop(4) } }

    var selected by rememberSaveable { mutableStateOf(MenuItem.TASKS.key) }
    val active = visible.firstOrNull { it.key == selected } ?: visible.firstOrNull() ?: MenuItem.TASKS

    var moreOpen by rememberSaveable { mutableStateOf(false) }
    var editMode by rememberSaveable { mutableStateOf(false) }

    // Safety net: if anything goes wrong and drag state outlives a drop,
    // exiting edit mode wipes it so a re-entry starts clean.
    LaunchedEffect(editMode) {
        if (!editMode) {
            draggedKey = null
            hoveredKey = null
        }
    }

    val swap: (MenuItem, MenuItem) -> Unit = { a, b ->
        // Atomic — without this, the four state writes (two list element
        // assignments + two key clears) commit to the global snapshot one
        // at a time, and `previewOrder` re-evaluates each intermediate
        // step. That produces a frame where order is already swapped but
        // the keys are still set, so the preview inverts and the user
        // sees the icons "fly back" before the final swap.
        androidx.compose.runtime.snapshots.Snapshot.withMutableSnapshot {
            val i = order.indexOf(a)
            val j = order.indexOf(b)
            if (i != -1 && j != -1 && i != j) {
                order[i] = b
                order[j] = a
                store.save(order.toList())
            }
            draggedKey = null
            hoveredKey = null
        }
    }

    // Commit the swap when the drag ends, using the last-known hovered
    // key. We don't rely on onDrop's target tile because the preview
    // reorder slides the source under the user's finger, making
    // onDrop fire on the source itself (`dragged == target`, no-op).
    val commitDragEnd: () -> Unit = {
        androidx.compose.runtime.snapshots.Snapshot.withMutableSnapshot {
            val d = draggedKey
            val h = hoveredKey
            if (d != null && h != null && d != h) {
                val di = order.indexOfFirst { it.key == d }
                val hi = order.indexOfFirst { it.key == h }
                if (di != -1 && hi != -1) {
                    val tmp = order[di]
                    order[di] = order[hi]
                    order[hi] = tmp
                    store.save(order.toList())
                }
            }
            draggedKey = null
            hoveredKey = null
        }
    }

    BackHandler(enabled = editMode) { editMode = false }

    val chatState by chatVm.state.collectAsState()
    val chatUnread = chatState.conversations.sumOf { it.unread_count }
    val chatOnDock = dock.any { it.key == MenuItem.CHAT.key }
    val chatActive = active.key == MenuItem.CHAT.key

    Box(modifier = Modifier.fillMaxSize()) {
        Scaffold(
            bottomBar = {
                DockBar(
                    items = dock,
                    showMore = overflow.isNotEmpty(),
                    activeKey = active.key,
                    moreActive = moreOpen,
                    chatBadge = chatUnread,
                    onSelect = { selected = it.key },
                    onMore = { moreOpen = true },
                    onEditModeStart = { editMode = true; moreOpen = false },
                    onDragStart = { key -> draggedKey = key },
                )
            }
        ) { padding ->
            ScreenSwitcher(
                item = active,
                user = user,
                token = token,
                chatVm = chatVm,
                onLogout = onLogout,
                modifier = Modifier.padding(padding),
            )
        }

        if (moreOpen && !editMode) {
            MoreSheet(
                items = overflow,
                activeKey = active.key,
                onDismiss = { moreOpen = false },
                onSelect = { selected = it.key; moreOpen = false },
                onLongPress = {
                    moreOpen = false
                    editMode = true
                },
            )
        }

        // Floating chat FAB — drag anywhere, snaps to nearest edge.
        // Hidden when chat is reachable from the dock or already on
        // screen (so we don't double up the entry point), or in edit
        // mode (which has its own wiggle-and-drag overlay).
        if (!editMode && !chatOnDock && !chatActive) {
            ChatFab(
                viewModel = chatVm,
                onClick = { selected = MenuItem.CHAT.key },
                modifier = Modifier.fillMaxSize(),
            )
        }

        // Top-of-screen toast for incoming chat messages. Hidden in edit
        // mode so it doesn't fight the customize overlay.
        if (!editMode) {
            ChatToastBanner(
                viewModel = chatVm,
                onTap = { selected = MenuItem.CHAT.key },
                modifier = Modifier
                    .align(Alignment.TopCenter)
                    .padding(top = 8.dp)
                    .statusBarsPadding(),
            )
        }

        AnimatedVisibility(
            visible = editMode,
            enter = fadeIn(animationSpec = tween(180)),
            exit = fadeOut(animationSpec = tween(140)),
        ) {
            EditMenuOverlay(
                dockItems = dock,
                overflowItems = overflow,
                hasOverflow = overflow.isNotEmpty(),
                draggedKey = draggedKey,
                onSwap = swap,
                onDragStart = { item -> draggedKey = item.key },
                onDragEnter = { item -> hoveredKey = item.key },
                // No-op on exit — keeps the preview committed once a target
                // has been entered, which prevents oscillation when the
                // preview reorder slides the target out from under the
                // user's finger and prevents losing the swap on drop.
                onDragExit = {},
                onDragEnd = commitDragEnd,
                onDone = { editMode = false },
            )
        }
    }
}

// region active screen routing -------------------------------------------------

@Composable
private fun ScreenSwitcher(
    item: MenuItem,
    user: ApiUser,
    token: String,
    chatVm: ChatViewModel,
    onLogout: () -> Unit,
    modifier: Modifier = Modifier,
) {
    when (item) {
        MenuItem.TASKS -> TaskBoardScreen(user = user, token = token, modifier = modifier)
        MenuItem.CHAT -> ChatScreen(userId = user.id, userRole = user.user_role, userFirstName = user.first_name, token = token, viewModel = chatVm, modifier = modifier)
        MenuItem.ITEMS -> ItemsScreen(token = token, modifier = modifier)
        MenuItem.ME -> MeScreen(user = user, onLogout = onLogout, modifier = modifier)
        MenuItem.CONSULTATION -> ConsultationScreen(token = token, modifier = modifier)
        MenuItem.SALES -> SalesManagementScreen(modifier = modifier)
        MenuItem.HR -> HRAccountingScreen(modifier = modifier)
    }
}

// endregion

// region dock bar -------------------------------------------------------------

@Composable
private fun DockBar(
    items: List<MenuItem>,
    showMore: Boolean,
    activeKey: String,
    moreActive: Boolean,
    chatBadge: Int,
    onSelect: (MenuItem) -> Unit,
    onMore: () -> Unit,
    onEditModeStart: () -> Unit,
    onDragStart: (String) -> Unit,
) {
    Surface(tonalElevation = 3.dp, shadowElevation = 4.dp) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .navigationBarsPadding()
                .padding(top = 6.dp, bottom = 4.dp),
            horizontalArrangement = Arrangement.SpaceEvenly,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            items.forEach { item ->
                DockButton(
                    label = item.label,
                    icon = item.icon,
                    active = item.key == activeKey,
                    badge = if (item.key == MenuItem.CHAT.key) chatBadge else 0,
                    onClick = { onSelect(item) },
                    onEditModeStart = onEditModeStart,
                    onDragStart = onDragStart,
                    dragKey = item.key,
                    modifier = Modifier.weight(1f),
                )
            }
            if (showMore) {
                DockButton(
                    label = "More",
                    icon = MenuItem.MoreIcon,
                    active = moreActive,
                    badge = 0,
                    onClick = onMore,
                    onEditModeStart = onEditModeStart,
                    onDragStart = onDragStart,
                    dragKey = null,
                    modifier = Modifier.weight(1f),
                )
            }
        }
    }
}

@Composable
private fun DockButton(
    label: String,
    icon: ImageVector,
    active: Boolean,
    badge: Int,
    onClick: () -> Unit,
    onEditModeStart: () -> Unit,
    onDragStart: (String) -> Unit,
    dragKey: String?,
    modifier: Modifier = Modifier,
) {
    val haptics = LocalHapticFeedback.current
    val tint = if (active) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurfaceVariant

    // dragAndDropSource is built on pointerInput(Unit), so its block is
    // captured once on first composition and never re-binds. Without the
    // rememberUpdatedState dance below, the closure keeps the dragKey it
    // saw at first composition — meaning after a swap, long-pressing a
    // dock slot drags whatever icon ORIGINALLY sat there, not the one
    // currently rendered. Same hazard for the three callbacks.
    val latestDragKey = androidx.compose.runtime.rememberUpdatedState(dragKey)
    val latestOnClick = androidx.compose.runtime.rememberUpdatedState(onClick)
    val latestOnEditModeStart = androidx.compose.runtime.rememberUpdatedState(onEditModeStart)
    val latestOnDragStart = androidx.compose.runtime.rememberUpdatedState(onDragStart)

    // The dragAndDropSource modifier owns the long-press itself: when the
    // user holds for ~500ms it kicks off a system drag carrying `dragKey`.
    // The moment the drag transfer starts, `onEditModeStart()` fires so
    // the EditMenuOverlay's drop targets are ready by the time the user's
    // finger reaches them — no need to release and re-press.
    val dragSource: Modifier = if (dragKey != null) {
        Modifier.dragAndDropSource {
            detectTapGestures(
                onTap = { latestOnClick.value() },
                onLongPress = {
                    val keyNow = latestDragKey.value ?: return@detectTapGestures
                    haptics.performHapticFeedback(HapticFeedbackType.LongPress)
                    latestOnEditModeStart.value()
                    // Mark this tile as the active drag source so the
                    // EditMenuOverlay's previewOrder swap activates the
                    // moment the drag enters another tile — without
                    // this, draggedKey stays null and the very first
                    // drag (the one that flips into edit mode) doesn't
                    // animate.
                    latestOnDragStart.value(keyNow)
                    startTransfer(
                        DragAndDropTransferData(
                            clipData = ClipData(
                                ClipDescription("menu_item", arrayOf(MIME_MENU_ITEM)),
                                ClipData.Item(keyNow),
                            ),
                        ),
                    )
                },
            )
        }
    } else {
        // "More" stays a plain tap target — long-press still toggles edit mode.
        Modifier.pointerInput(Unit) {
            detectTapGestures(
                onTap = { latestOnClick.value() },
                onLongPress = {
                    haptics.performHapticFeedback(HapticFeedbackType.LongPress)
                    latestOnEditModeStart.value()
                },
            )
        }
    }

    Column(
        modifier = modifier
            .then(dragSource)
            .padding(vertical = 4.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Box {
            Icon(icon, contentDescription = label, tint = tint, modifier = Modifier.size(30.dp))
            if (badge > 0) {
                androidx.compose.material3.Badge(
                    containerColor = MaterialTheme.colorScheme.error,
                    contentColor = MaterialTheme.colorScheme.onError,
                    modifier = Modifier
                        .align(Alignment.TopEnd)
                        .offset(x = 12.dp, y = (-6).dp),
                ) {
                    Text(if (badge > 99) "99+" else badge.toString())
                }
            }
        }
        Spacer(Modifier.height(2.dp))
        Text(
            label,
            fontSize = 11.sp,
            color = tint,
            fontWeight = if (active) FontWeight.SemiBold else FontWeight.Normal,
        )
    }
}

// endregion

// region More sheet (read-only) -----------------------------------------------

@Composable
private fun MoreSheet(
    items: List<MenuItem>,
    activeKey: String,
    onDismiss: () -> Unit,
    onSelect: (MenuItem) -> Unit,
    onLongPress: () -> Unit,
) {
    val sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = false)
    ModalBottomSheet(
        onDismissRequest = onDismiss,
        sheetState = sheetState,
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 8.dp),
        ) {
            Text(
                "More",
                style = MaterialTheme.typography.titleMedium,
                modifier = Modifier.padding(start = 4.dp, bottom = 8.dp),
            )
            LazyVerticalGrid(
                columns = GridCells.Adaptive(96.dp),
                contentPadding = PaddingValues(8.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .height(280.dp),
            ) {
                items(items, key = { it.key }) { item ->
                    MoreTile(
                        item = item,
                        active = item.key == activeKey,
                        onClick = { onSelect(item) },
                        onLongPress = onLongPress,
                    )
                }
            }
            Text(
                "Long-press an icon to rearrange your menu.",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 4.dp, bottom = 16.dp),
            )
        }
    }
}

@Composable
private fun MoreTile(
    item: MenuItem,
    active: Boolean,
    onClick: () -> Unit,
    onLongPress: () -> Unit,
) {
    val haptics = LocalHapticFeedback.current
    val bg = if (active) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surfaceVariant
    val fg = if (active) MaterialTheme.colorScheme.onPrimaryContainer else MaterialTheme.colorScheme.onSurface

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp)
            .pointerInput(Unit) {
                detectTapGestures(
                    onTap = { onClick() },
                    onLongPress = {
                        haptics.performHapticFeedback(HapticFeedbackType.LongPress)
                        onLongPress()
                    },
                )
            },
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Box(
            modifier = Modifier
                .size(56.dp)
                .background(bg, RoundedCornerShape(14.dp)),
            contentAlignment = Alignment.Center,
        ) {
            Icon(item.icon, contentDescription = item.label, tint = fg)
        }
        Spacer(Modifier.height(6.dp))
        Text(
            item.label,
            style = MaterialTheme.typography.labelSmall,
            color = fg,
            maxLines = 1,
            softWrap = false,
            overflow = androidx.compose.ui.text.style.TextOverflow.Visible,
        )
    }
}

// endregion

// region edit mode overlay ----------------------------------------------------

@Composable
private fun EditMenuOverlay(
    dockItems: List<MenuItem>,
    overflowItems: List<MenuItem>,
    hasOverflow: Boolean,
    draggedKey: String?,
    onSwap: (MenuItem, MenuItem) -> Unit,
    onDragStart: (MenuItem) -> Unit,
    onDragEnter: (MenuItem) -> Unit,
    onDragExit: () -> Unit,
    onDragEnd: () -> Unit,
    onDone: () -> Unit,
) {
    val wiggle by rememberInfiniteTransition(label = "wiggle").animateFloat(
        initialValue = -1.5f,
        targetValue = 1.5f,
        animationSpec = infiniteRepeatable(
            animation = tween(160, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse,
        ),
        label = "wiggle_rotation",
    )

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.scrim.copy(alpha = 0.45f))
            .clickable(
                interactionSource = remember { MutableInteractionSource() },
                indication = null,
                onClick = onDone,
            ),
    ) {
        Surface(
            modifier = Modifier
                .fillMaxSize()
                .clickable(
                    interactionSource = remember { MutableInteractionSource() },
                    indication = null,
                    // Tap on any empty space inside the panel = Done.
                    // Tile taps are consumed by their own detectTapGestures
                    // so they don't bubble up here, and long-press still
                    // initiates a drag normally.
                    onClick = onDone,
                ),
            color = MaterialTheme.colorScheme.surface,
            tonalElevation = 6.dp,
        ) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .statusBarsPadding(),
            ) {
                EditHeader(onDone = onDone)
                Box(
                    modifier = Modifier
                        .weight(1f)
                        .fillMaxWidth(),
                ) {
                    if (overflowItems.isEmpty()) {
                        Column(
                            modifier = Modifier.fillMaxSize(),
                            verticalArrangement = Arrangement.Center,
                            horizontalAlignment = Alignment.CenterHorizontally,
                        ) {
                            Text(
                                "All your items are in the dock.",
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                                style = MaterialTheme.typography.bodySmall,
                            )
                        }
                    } else {
                        LazyVerticalGrid(
                            columns = GridCells.Adaptive(96.dp),
                            contentPadding = PaddingValues(20.dp),
                            modifier = Modifier.fillMaxSize(),
                        ) {
                            items(overflowItems, key = { it.key }) { item ->
                                EditTile(
                                    item = item,
                                    wiggle = wiggle,
                                    isDragging = item.key == draggedKey,
                                    onSwap = onSwap,
                                    onDragStart = onDragStart,
                                    onDragEnter = onDragEnter,
                                    onDragExit = onDragExit,
                                    onDragEnd = onDragEnd,
                                    modifier = Modifier.animateItem(
                                        placementSpec = androidx.compose.animation.core.tween(
                                            durationMillis = 350,
                                            easing = FastOutSlowInEasing,
                                        ),
                                    ),
                                )
                            }
                        }
                    }
                }
                HorizontalDivider()
                Text(
                    "DOCK",
                    style = MaterialTheme.typography.labelSmall.copy(
                        fontWeight = FontWeight.SemiBold,
                        letterSpacing = 1.sp,
                    ),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.padding(start = 20.dp, top = 10.dp, bottom = 4.dp),
                )
                val totalDockSlots = (dockItems.size + (if (hasOverflow) 1 else 0))
                    .coerceAtLeast(1)
                LazyRow(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 8.dp)
                        .padding(top = 4.dp, bottom = 16.dp)
                        .navigationBarsPadding(),
                    horizontalArrangement = Arrangement.SpaceEvenly,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    lazyRowItems(items = dockItems, key = { it.key }) { item ->
                        Box(
                            modifier = Modifier
                                .fillParentMaxWidth(1f / totalDockSlots)
                                .animateItem(
                                    placementSpec = androidx.compose.animation.core.tween(
                                        durationMillis = 350,
                                        easing = FastOutSlowInEasing,
                                    ),
                                ),
                        ) {
                            EditTile(
                                item = item,
                                wiggle = wiggle,
                                isDragging = item.key == draggedKey,
                                onSwap = onSwap,
                                onDragStart = onDragStart,
                                onDragEnter = onDragEnter,
                                onDragExit = onDragExit,
                                onDragEnd = onDragEnd,
                            )
                        }
                    }
                    if (hasOverflow) {
                        item(key = "__more__") {
                            Column(
                                modifier = Modifier
                                    .fillParentMaxWidth(1f / totalDockSlots)
                                    .padding(8.dp),
                                horizontalAlignment = Alignment.CenterHorizontally,
                            ) {
                                Box(
                                    modifier = Modifier
                                        .size(56.dp)
                                        .background(
                                            MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f),
                                            RoundedCornerShape(14.dp),
                                        ),
                                    contentAlignment = Alignment.Center,
                                ) {
                                    Icon(
                                        MenuItem.MoreIcon,
                                        contentDescription = "More",
                                        tint = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.5f),
                                    )
                                }
                                Spacer(Modifier.height(6.dp))
                                Text(
                                    "More",
                                    style = MaterialTheme.typography.labelSmall,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.5f),
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun EditHeader(onDone: () -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(start = 20.dp, end = 16.dp, top = 14.dp, bottom = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Column(modifier = Modifier.weight(1f)) {
            Text("Customize Menu", style = MaterialTheme.typography.titleMedium)
            Text(
                "Drag an icon onto another to swap.",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        Button(onClick = onDone) { Text("Done") }
    }
}

@Composable
private fun EditTile(
    item: MenuItem,
    wiggle: Float,
    isDragging: Boolean,
    onSwap: (MenuItem, MenuItem) -> Unit,
    onDragStart: (MenuItem) -> Unit,
    onDragEnter: (MenuItem) -> Unit,
    onDragExit: () -> Unit,
    onDragEnd: () -> Unit,
    modifier: Modifier = Modifier,
) {
    var isTargeted by remember(item) { mutableStateOf(false) }
    val haptics = LocalHapticFeedback.current

    val phase = remember(item) { (item.key.hashCode() % 100).toFloat() / 100f }
    val rotation = wiggle + phase * 0.6f

    // Hold the latest callback references inside a stable wrapper so the
    // DragAndDropTarget object isn't re-created on every recomposition
    // (which would silently remount the dragAndDropTarget modifier mid-
    // drag and drop the onEnded delivery, leaving draggedKey stuck).
    val latestOnSwap = androidx.compose.runtime.rememberUpdatedState(onSwap)
    val latestOnDragEnter = androidx.compose.runtime.rememberUpdatedState(onDragEnter)
    val latestOnDragExit = androidx.compose.runtime.rememberUpdatedState(onDragExit)
    val latestOnDragEnd = androidx.compose.runtime.rememberUpdatedState(onDragEnd)
    val latestIsDragging = androidx.compose.runtime.rememberUpdatedState(isDragging)
    val targetCallback = remember(item) {
        object : DragAndDropTarget {
            override fun onDrop(event: DragAndDropEvent): Boolean {
                val text = event.toAndroidDragEvent().clipData?.getItemAt(0)?.text?.toString()
                val dragged = text?.let { MenuItem.fromKey(it) }
                isTargeted = false
                if (dragged != null) {
                    // Commit via the hovered-key path rather than against
                    // this drop target. After a preview reorder the drop
                    // target tile isn't necessarily the user's intended
                    // swap partner — they could be dropping on the
                    // source's own preview slot or on a third tile.
                    latestOnDragEnd.value()
                    haptics.performHapticFeedback(HapticFeedbackType.LongPress)
                    // Consume the drop unconditionally — when we return
                    // false the OS plays a "fly back to source" animation
                    // on the drag shadow, which the user explicitly
                    // doesn't want.
                    return true
                }
                return false
            }
            override fun onEntered(event: DragAndDropEvent) {
                // Ignore enter when the source tile slides under the
                // finger after a preview swap — otherwise it sets the
                // hoveredKey to itself, the preview reverts, the target
                // slides back, and we ping-pong forever.
                if (latestIsDragging.value) return
                isTargeted = true
                latestOnDragEnter.value(item)
            }
            override fun onExited(event: DragAndDropEvent) {
                isTargeted = false
                latestOnDragExit.value()
            }
            override fun onEnded(event: DragAndDropEvent) {
                isTargeted = false
                latestOnDragEnd.value()
            }
        }
    }

    val scale by animateFloatAsState(if (isTargeted) 1.08f else 1f, label = "tile_scale")

    val bg = if (isTargeted) MaterialTheme.colorScheme.primary.copy(alpha = 0.25f)
             else MaterialTheme.colorScheme.surfaceVariant
    val fg = MaterialTheme.colorScheme.onSurface

    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(8.dp)
            .graphicsLayer {
                rotationZ = rotation
                scaleX = scale
                scaleY = scale
                // While this tile is the active drag source we hide the
                // in-list copy so only the system drag-shadow is visible
                // and the swap reads as a clean "fly into empty slot".
                alpha = if (isDragging) 0f else 1f
            }
            .dragAndDropTarget(
                shouldStartDragAndDrop = { event -> event.mimeTypes().contains(MIME_MENU_ITEM) },
                target = targetCallback,
            ),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Box(
            modifier = Modifier
                .size(56.dp)
                .background(bg, RoundedCornerShape(14.dp))
                .dragAndDropSource {
                    detectTapGestures(
                        onLongPress = {
                            haptics.performHapticFeedback(HapticFeedbackType.LongPress)
                            startTransfer(
                                DragAndDropTransferData(
                                    clipData = ClipData(
                                        ClipDescription("menu_item", arrayOf(MIME_MENU_ITEM)),
                                        ClipData.Item(item.key),
                                    ),
                                ),
                            )
                            onDragStart(item)
                        },
                    )
                },
            contentAlignment = Alignment.Center,
        ) {
            Icon(item.icon, contentDescription = item.label, tint = fg)
        }
        Spacer(Modifier.height(6.dp))
        Text(
            item.label,
            style = MaterialTheme.typography.labelSmall,
            color = fg,
            maxLines = 1,
            softWrap = false,
            overflow = androidx.compose.ui.text.style.TextOverflow.Visible,
        )
    }
}

// endregion
