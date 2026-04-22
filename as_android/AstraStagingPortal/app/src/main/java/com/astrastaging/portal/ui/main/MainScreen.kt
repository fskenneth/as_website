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
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
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
import androidx.compose.runtime.Composable
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
import com.astrastaging.portal.ui.stubs.ConsultationScreen
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

    val visible by remember(user.roleLevel) {
        derivedStateOf { order.filter { it.minRoleLevel <= user.roleLevel } }
    }
    val dock by remember { derivedStateOf { visible.take(4) } }
    val overflow by remember { derivedStateOf { visible.drop(4) } }

    var selected by rememberSaveable { mutableStateOf(MenuItem.TASKS.key) }
    val active = visible.firstOrNull { it.key == selected } ?: visible.firstOrNull() ?: MenuItem.TASKS

    var moreOpen by rememberSaveable { mutableStateOf(false) }
    var editMode by rememberSaveable { mutableStateOf(false) }

    val swap: (MenuItem, MenuItem) -> Unit = { a, b ->
        val i = order.indexOf(a)
        val j = order.indexOf(b)
        if (i != -1 && j != -1 && i != j) {
            order[i] = b
            order[j] = a
            store.save(order.toList())
        }
    }

    BackHandler(enabled = editMode) { editMode = false }

    Box(modifier = Modifier.fillMaxSize()) {
        Scaffold(
            bottomBar = {
                DockBar(
                    items = dock,
                    showMore = overflow.isNotEmpty(),
                    activeKey = active.key,
                    moreActive = moreOpen,
                    onSelect = { selected = it.key },
                    onMore = { moreOpen = true },
                    onLongPress = { editMode = true; moreOpen = false },
                )
            }
        ) { padding ->
            ScreenSwitcher(
                item = active,
                user = user,
                token = token,
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

        AnimatedVisibility(
            visible = editMode,
            enter = fadeIn(animationSpec = tween(180)),
            exit = fadeOut(animationSpec = tween(140)),
        ) {
            EditMenuOverlay(
                dockItems = dock,
                overflowItems = overflow,
                hasOverflow = overflow.isNotEmpty(),
                onSwap = swap,
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
    onLogout: () -> Unit,
    modifier: Modifier = Modifier,
) {
    when (item) {
        MenuItem.TASKS -> TaskBoardScreen(user = user, token = token, modifier = modifier)
        MenuItem.ITEMS -> ItemsScreen(token = token, modifier = modifier)
        MenuItem.ME -> MeScreen(user = user, onLogout = onLogout, modifier = modifier)
        MenuItem.CONSULTATION -> ConsultationScreen(modifier = modifier)
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
    onSelect: (MenuItem) -> Unit,
    onMore: () -> Unit,
    onLongPress: () -> Unit,
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
                    onClick = { onSelect(item) },
                    onLongPress = onLongPress,
                    modifier = Modifier.weight(1f),
                )
            }
            if (showMore) {
                DockButton(
                    label = "More",
                    icon = MenuItem.MoreIcon,
                    active = moreActive,
                    onClick = onMore,
                    onLongPress = onLongPress,
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
    onClick: () -> Unit,
    onLongPress: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val haptics = LocalHapticFeedback.current
    val tint = if (active) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurfaceVariant

    Column(
        modifier = modifier
            .pointerInput(Unit) {
                detectTapGestures(
                    onTap = { onClick() },
                    onLongPress = {
                        haptics.performHapticFeedback(HapticFeedbackType.LongPress)
                        onLongPress()
                    },
                )
            }
            .padding(vertical = 4.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Icon(icon, contentDescription = label, tint = tint, modifier = Modifier.size(24.dp))
        Spacer(Modifier.height(2.dp))
        Text(
            label,
            fontSize = 10.sp,
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
    onSwap: (MenuItem, MenuItem) -> Unit,
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
                    onClick = {}, // swallow taps on the panel itself
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
                                EditTile(item = item, wiggle = wiggle, onSwap = onSwap)
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
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 8.dp)
                        .padding(top = 4.dp, bottom = 16.dp)
                        .navigationBarsPadding(),
                    horizontalArrangement = Arrangement.SpaceEvenly,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    dockItems.forEach { item ->
                        Box(modifier = Modifier.weight(1f)) {
                            EditTile(item = item, wiggle = wiggle, onSwap = onSwap)
                        }
                    }
                    if (hasOverflow) {
                        Column(
                            modifier = Modifier
                                .weight(1f)
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
    onSwap: (MenuItem, MenuItem) -> Unit,
) {
    var isTargeted by remember(item) { mutableStateOf(false) }
    val haptics = LocalHapticFeedback.current

    val phase = remember(item) { (item.key.hashCode() % 100).toFloat() / 100f }
    val rotation = wiggle + phase * 0.6f

    val targetCallback = remember(item) {
        object : DragAndDropTarget {
            override fun onDrop(event: DragAndDropEvent): Boolean {
                val text = event.toAndroidDragEvent().clipData?.getItemAt(0)?.text?.toString()
                val dragged = text?.let { MenuItem.fromKey(it) }
                isTargeted = false
                if (dragged != null && dragged != item) {
                    onSwap(dragged, item)
                    haptics.performHapticFeedback(HapticFeedbackType.LongPress)
                    return true
                }
                return false
            }
            override fun onEntered(event: DragAndDropEvent) { isTargeted = true }
            override fun onExited(event: DragAndDropEvent) { isTargeted = false }
            override fun onEnded(event: DragAndDropEvent) { isTargeted = false }
        }
    }

    val scale by animateFloatAsState(if (isTargeted) 1.08f else 1f, label = "tile_scale")

    val bg = if (isTargeted) MaterialTheme.colorScheme.primary.copy(alpha = 0.25f)
             else MaterialTheme.colorScheme.surfaceVariant
    val fg = MaterialTheme.colorScheme.onSurface

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp)
            .graphicsLayer {
                rotationZ = rotation
                scaleX = scale
                scaleY = scale
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
