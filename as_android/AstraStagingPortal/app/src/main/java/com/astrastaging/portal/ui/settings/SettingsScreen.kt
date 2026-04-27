package com.astrastaging.portal.ui.settings

import android.app.Application
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.outlined.Delete
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.SegmentedButton
import androidx.compose.material3.SegmentedButtonDefaults
import androidx.compose.material3.SingleChoiceSegmentedButtonRow
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.astrastaging.portal.data.media.CaptureRepository
import com.astrastaging.portal.data.network.NetworkMonitor
import com.astrastaging.portal.data.settings.AccentTheme
import com.astrastaging.portal.data.settings.AppSettings
import com.astrastaging.portal.data.settings.ThemeMode
import kotlinx.coroutines.launch

@Composable
fun SettingsScreen(onBack: () -> Unit, modifier: Modifier = Modifier) {
    val context = LocalContext.current
    val appContext = context.applicationContext as Application
    val settings = remember { AppSettings(appContext) }
    val captures = remember { CaptureRepository(appContext) }
    val wifiOnly by settings.wifiOnlyMediaUpload.collectAsStateWithLifecycle(initialValue = true)
    val enterToSend by settings.enterToSend.collectAsStateWithLifecycle(initialValue = true)
    val pendingCount by captures.pendingCount().collectAsStateWithLifecycle(initialValue = 0)
    val pendingCaptures by captures.observePending()
        .collectAsStateWithLifecycle(initialValue = emptyList<com.astrastaging.portal.data.media.CaptureEntity>())
    val network by NetworkMonitor.snapshot.collectAsStateWithLifecycle()
    val themeMode by settings.themeMode.collectAsStateWithLifecycle(initialValue = ThemeMode.AUTO)
    val accent by settings.accent.collectAsStateWithLifecycle(initialValue = AccentTheme.SLATE)
    val systemDark = isSystemInDarkTheme()
    val useDark = when (themeMode) {
        ThemeMode.AUTO -> systemDark
        ThemeMode.LIGHT -> false
        ThemeMode.DARK -> true
    }
    val scope = rememberCoroutineScope()

    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            IconButton(onClick = onBack) {
                Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
            }
            Text(
                "Settings",
                style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold),
            )
        }
        Spacer(Modifier.height(12.dp))

        Text(
            "UPLOADS",
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.padding(start = 4.dp, bottom = 6.dp),
        )
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
        ) {
            Row(
                modifier = Modifier.fillMaxWidth().padding(16.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Column(Modifier.weight(1f)) {
                    Text(
                        "Upload Photos and Videos on Wi-Fi Only",
                        style = MaterialTheme.typography.bodyMedium,
                    )
                    Text(
                        "Text updates (e.g. task board, milestones) still sync over cellular.",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
                Switch(
                    checked = wifiOnly,
                    onCheckedChange = { newValue ->
                        scope.launch {
                            settings.setWifiOnlyMediaUpload(newValue)
                            captures.scheduleUpload(wifiOnly = newValue)
                        }
                    }
                )
            }
        }

        Spacer(Modifier.height(20.dp))
        Text(
            "CHAT",
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.padding(start = 4.dp, bottom = 6.dp),
        )
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
        ) {
            Row(
                modifier = Modifier.fillMaxWidth().padding(16.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Column(Modifier.weight(1f)) {
                    Text(
                        "Enter to Send",
                        style = MaterialTheme.typography.bodyMedium,
                    )
                    Text(
                        "Off: pressing return inserts a newline; tap the send button to send.",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
                Switch(
                    checked = enterToSend,
                    onCheckedChange = { newValue ->
                        scope.launch { settings.setEnterToSend(newValue) }
                    }
                )
            }
        }

        Spacer(Modifier.height(20.dp))
        Text(
            "APPEARANCE",
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.padding(start = 4.dp, bottom = 6.dp),
        )
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
        ) {
            Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
                SingleChoiceSegmentedButtonRow(modifier = Modifier.fillMaxWidth()) {
                    ThemeMode.entries.forEachIndexed { index, mode ->
                        SegmentedButton(
                            selected = mode == themeMode,
                            onClick = { scope.launch { settings.setThemeMode(mode) } },
                            shape = SegmentedButtonDefaults.itemShape(
                                index = index, count = ThemeMode.entries.size,
                            ),
                        ) {
                            Text(mode.name.lowercase()
                                .replaceFirstChar { it.uppercase() })
                        }
                    }
                }

                Text(
                    "Color",
                    style = MaterialTheme.typography.bodyMedium,
                )
                Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    AccentTheme.entries.forEach { theme ->
                        val color = Color(if (useDark) theme.darkHex else theme.lightHex)
                        Column(
                            horizontalAlignment = Alignment.CenterHorizontally,
                            verticalArrangement = Arrangement.spacedBy(4.dp),
                            modifier = Modifier.clickable {
                                scope.launch { settings.setAccent(theme) }
                            }
                        ) {
                            Box(
                                modifier = Modifier
                                    .size(36.dp)
                                    .clip(CircleShape)
                                    .background(color)
                                    .then(
                                        if (theme == accent)
                                            Modifier.border(
                                                2.dp,
                                                MaterialTheme.colorScheme.onSurface,
                                                CircleShape,
                                            )
                                        else Modifier
                                    ),
                                contentAlignment = Alignment.Center,
                            ) {
                                if (theme == accent) {
                                    Icon(
                                        Icons.Filled.Check,
                                        contentDescription = null,
                                        tint = Color.White,
                                        modifier = Modifier.size(18.dp),
                                    )
                                }
                            }
                            Text(
                                theme.label,
                                style = MaterialTheme.typography.labelSmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                        }
                    }
                }
            }
        }

        Spacer(Modifier.height(20.dp))
        Text(
            "CONNECTION",
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.padding(start = 4.dp, bottom = 6.dp),
        )
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
        ) {
            Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                KV("Status", if (network.isOnline) "Online" else "Offline")
                KV("Network", when {
                    !network.isOnline -> "—"
                    network.isUnmetered -> "Wi-Fi"
                    else -> "Cellular"
                })
            }
        }

        Spacer(Modifier.height(20.dp))
        Text(
            "UPLOAD QUEUE",
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.padding(start = 4.dp, bottom = 6.dp),
        )
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
        ) {
            Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Button(
                    onClick = { captures.scheduleUpload(wifiOnly = wifiOnly) },
                    enabled = pendingCount > 0 && network.isOnline,
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Text("Retry Now")
                }

                if (pendingCaptures.isEmpty()) {
                    Text(
                        "Nothing queued.",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                } else {
                    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        pendingCaptures.forEach { item ->
                            UploadQueueRow(
                                capture = item,
                                onDelete = {
                                    scope.launch { captures.delete(item) }
                                },
                            )
                        }
                    }
                }
            }
        }
    }
}

/** Row for a single pending capture: filename + size + status + delete. */
@Composable
private fun UploadQueueRow(
    capture: com.astrastaging.portal.data.media.CaptureEntity,
    onDelete: () -> Unit,
) {
    val status = runCatching {
        com.astrastaging.portal.data.media.CaptureStatus.valueOf(capture.status)
    }.getOrDefault(com.astrastaging.portal.data.media.CaptureStatus.PENDING)
    val fileName = java.io.File(capture.filePath).name

    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Column(Modifier.weight(1f)) {
            Text(
                fileName,
                style = MaterialTheme.typography.bodySmall,
                maxLines = 1,
            )
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    formatBytes(capture.fileSize),
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                Spacer(Modifier.width(8.dp))
                val (statusLabel, statusColor) = when (status) {
                    com.astrastaging.portal.data.media.CaptureStatus.PENDING ->
                        "Queued" to androidx.compose.ui.graphics.Color(0xFFB66A00)
                    com.astrastaging.portal.data.media.CaptureStatus.UPLOADING ->
                        "Uploading…" to androidx.compose.ui.graphics.Color(0xFF1E88E5)
                    com.astrastaging.portal.data.media.CaptureStatus.FAILED ->
                        ("Failed — ${capture.lastError.orEmpty()}").trim(' ', '—') to
                            MaterialTheme.colorScheme.error
                    com.astrastaging.portal.data.media.CaptureStatus.UPLOADED ->
                        "Done" to androidx.compose.ui.graphics.Color(0xFF2E7D32)
                }
                if (status == com.astrastaging.portal.data.media.CaptureStatus.UPLOADING) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(12.dp),
                        strokeWidth = 2.dp,
                    )
                    Spacer(Modifier.width(4.dp))
                }
                Text(
                    statusLabel,
                    style = MaterialTheme.typography.labelSmall,
                    color = statusColor,
                    maxLines = 1,
                )
            }
        }
        IconButton(onClick = onDelete) {
            Icon(
                Icons.Outlined.Delete,
                contentDescription = "Delete queued upload",
                tint = MaterialTheme.colorScheme.error,
                modifier = Modifier.size(18.dp),
            )
        }
    }
}

private fun formatBytes(bytes: Long): String {
    if (bytes <= 0) return "0 KB"
    val kb = bytes / 1024.0
    if (kb < 1024) return "%.0f KB".format(kb)
    val mb = kb / 1024.0
    if (mb < 1024) return "%.1f MB".format(mb)
    return "%.2f GB".format(mb / 1024.0)
}

@Composable
private fun KV(key: String, value: String) {
    Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
        Text(key, style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.weight(1f))
        Text(value, style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.Medium)
    }
}
