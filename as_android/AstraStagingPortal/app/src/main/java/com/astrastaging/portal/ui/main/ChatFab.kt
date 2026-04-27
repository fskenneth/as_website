package com.astrastaging.portal.ui.main

import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.spring
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.outlined.Chat
import androidx.compose.material3.Badge
import androidx.compose.material3.BadgedBox
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Modifier
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.dp
import com.astrastaging.portal.data.settings.AppSettings
import com.astrastaging.portal.data.settings.ChatFabSide
import com.astrastaging.portal.ui.chat.ChatViewModel
import kotlinx.coroutines.launch
import kotlin.math.roundToInt

/**
 * Always-visible draggable chat FAB. Wraps the inner [ChatFabInner] in a
 * BoxWithConstraints so the drag math is constrained to the visible window;
 * on release it snaps to the nearer horizontal edge and persists position
 * (side + y-fraction) in [AppSettings].
 */
@Composable
fun ChatFab(
    viewModel: ChatViewModel,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val ctx = LocalContext.current
    val density = LocalDensity.current
    val haptics = LocalHapticFeedback.current
    val scope = rememberCoroutineScope()
    val settings = remember(ctx) { AppSettings(ctx) }
    val side by settings.chatFabSide.collectAsState(initial = ChatFabSide.RIGHT)
    val yFraction by settings.chatFabYFraction.collectAsState(initial = 0.85f)

    val state by viewModel.state.collectAsState()
    val unread = state.conversations.sumOf { it.unread_count }

    val buttonPx = with(density) { 56.dp.toPx() }
    val edgeInsetPx = with(density) { 14.dp.toPx() }
    val topInsetPx = with(density) { 60.dp.toPx() }
    val bottomInsetPx = with(density) { 96.dp.toPx() }  // above the dock

    BoxWithConstraints(modifier = modifier.fillMaxSize()) {
        val widthPx = with(density) { maxWidth.toPx() }
        val heightPx = with(density) { maxHeight.toPx() }
        val usableHeight = (heightPx - topInsetPx - bottomInsetPx - buttonPx).coerceAtLeast(0f)

        val baseX = if (side == ChatFabSide.RIGHT) widthPx - buttonPx - edgeInsetPx else edgeInsetPx
        val baseY = topInsetPx + usableHeight * yFraction

        val offsetX = remember { Animatable(baseX) }
        val offsetY = remember { Animatable(baseY) }

        // Whenever side / y-fraction / window size change (from outside this
        // composable, e.g. a fresh Settings load), snap the animatables to
        // match — without animation, since the user didn't initiate the move.
        LaunchedEffect(side, yFraction, widthPx, heightPx) {
            offsetX.snapTo(baseX)
            offsetY.snapTo(baseY)
        }

        Box(
            modifier = Modifier
                .offset { IntOffset(offsetX.value.roundToInt(), offsetY.value.roundToInt()) }
                .semantics { contentDescription = "Chat" }
                .pointerInput(widthPx, heightPx) {
                    detectDragGestures(
                        onDrag = { change, drag ->
                            change.consume()
                            scope.launch {
                                offsetX.snapTo((offsetX.value + drag.x)
                                    .coerceIn(edgeInsetPx, widthPx - buttonPx - edgeInsetPx))
                                offsetY.snapTo((offsetY.value + drag.y)
                                    .coerceIn(topInsetPx, heightPx - bottomInsetPx - buttonPx))
                            }
                        },
                        onDragEnd = {
                            val centerX = offsetX.value + buttonPx / 2f
                            val newSide = if (centerX < widthPx / 2f) ChatFabSide.LEFT else ChatFabSide.RIGHT
                            val targetX = if (newSide == ChatFabSide.RIGHT)
                                widthPx - buttonPx - edgeInsetPx else edgeInsetPx
                            val clampedY = offsetY.value
                                .coerceIn(topInsetPx, topInsetPx + usableHeight)
                            val newFraction = if (usableHeight > 0f)
                                ((clampedY - topInsetPx) / usableHeight).coerceIn(0f, 1f)
                            else 0.5f
                            scope.launch {
                                offsetX.animateTo(targetX, animationSpec = spring(dampingRatio = 0.7f))
                            }
                            scope.launch {
                                offsetY.animateTo(clampedY, animationSpec = spring(dampingRatio = 0.85f))
                            }
                            scope.launch {
                                settings.setChatFabSide(newSide)
                                settings.setChatFabYFraction(newFraction)
                            }
                            haptics.performHapticFeedback(HapticFeedbackType.LongPress)
                        },
                    )
                }
        ) {
            BadgedBox(
                badge = {
                    if (unread > 0) {
                        Badge(
                            containerColor = MaterialTheme.colorScheme.error,
                            contentColor = MaterialTheme.colorScheme.onError,
                            modifier = Modifier.offset(x = (-12).dp, y = 12.dp),
                        ) {
                            Text(if (unread > 99) "99+" else unread.toString())
                        }
                    }
                }
            ) {
                FloatingActionButton(
                    onClick = onClick,
                    shape = CircleShape,
                    containerColor = MaterialTheme.colorScheme.primary,
                    contentColor = MaterialTheme.colorScheme.onPrimary,
                ) {
                    Icon(Icons.AutoMirrored.Outlined.Chat, contentDescription = null)
                }
            }
        }
    }
}
