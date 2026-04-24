package com.astrastaging.portal.ui.consultation

import android.net.Uri
import android.widget.VideoView
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
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
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.outlined.Delete
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import coil.compose.AsyncImage
import com.astrastaging.portal.data.ApiClient
import com.astrastaging.portal.data.AreaCatalogEntry
import com.astrastaging.portal.data.StagingArea
import com.astrastaging.portal.data.media.CaptureEntity
import com.astrastaging.portal.data.media.CaptureMediaType
import kotlinx.coroutines.launch
import java.io.File

// ---- Add Area ---------------------------------------------------------------

@Composable
internal fun AddAreaDialog(
    stagingId: String,
    token: String,
    onCreated: (StagingArea) -> Unit,
    onDismiss: () -> Unit,
) {
    val scope = rememberCoroutineScope()
    var catalog by remember { mutableStateOf<List<AreaCatalogEntry>>(emptyList()) }
    var customName by remember { mutableStateOf("") }
    var selectedName by remember { mutableStateOf<String?>(null) }
    var submitting by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    var loadingCatalog by remember { mutableStateOf(true) }

    LaunchedEffect(Unit) {
        loadingCatalog = true
        runCatching { ApiClient.areaCatalog(token) }
            .onSuccess { catalog = it.catalog }
        loadingCatalog = false
    }

    val effectiveName = customName.trim().ifEmpty { selectedName.orEmpty() }

    Dialog(
        onDismissRequest = onDismiss,
        properties = DialogProperties(usePlatformDefaultWidth = false),
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp)
                .clip(RoundedCornerShape(16.dp))
                .background(MaterialTheme.colorScheme.surface)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    "Add Area",
                    style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
                    modifier = Modifier.weight(1f),
                )
                IconButton(onClick = onDismiss) {
                    Icon(Icons.Filled.Close, contentDescription = "Cancel")
                }
            }

            OutlinedTextField(
                value = customName,
                onValueChange = {
                    customName = it
                    if (it.isNotEmpty()) selectedName = null
                },
                label = { Text("Custom name (e.g. Living Room)") },
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
            )

            HorizontalDivider()
            Text(
                "Common areas",
                style = MaterialTheme.typography.labelMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )

            Box(modifier = Modifier.height(260.dp)) {
                when {
                    loadingCatalog -> Row(
                        modifier = Modifier.fillMaxSize(),
                        horizontalArrangement = Arrangement.Center,
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        CircularProgressIndicator(modifier = Modifier.size(18.dp), strokeWidth = 2.dp)
                    }
                    catalog.isEmpty() -> Text(
                        "Type a custom name above.",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                    else -> LazyColumn(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                        items(catalog, key = { it.name }) { entry ->
                            val selected = selectedName == entry.name
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clip(RoundedCornerShape(8.dp))
                                    .background(
                                        if (selected) MaterialTheme.colorScheme.primary.copy(alpha = 0.12f)
                                        else Color.Transparent
                                    )
                                    .clickable {
                                        selectedName = entry.name
                                        customName = ""
                                    }
                                    .padding(horizontal = 10.dp, vertical = 10.dp),
                                verticalAlignment = Alignment.CenterVertically,
                            ) {
                                Text(entry.name, modifier = Modifier.weight(1f))
                                if (selected) {
                                    Icon(
                                        Icons.Filled.Check,
                                        contentDescription = null,
                                        tint = MaterialTheme.colorScheme.primary,
                                    )
                                } else {
                                    Text(
                                        "${entry.count}×",
                                        style = MaterialTheme.typography.labelSmall,
                                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                                    )
                                }
                            }
                        }
                    }
                }
            }

            if (error != null) {
                Text(error!!, color = MaterialTheme.colorScheme.error, style = MaterialTheme.typography.bodySmall)
            }

            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                modifier = Modifier.fillMaxWidth(),
            ) {
                OutlinedButton(onClick = onDismiss, modifier = Modifier.weight(1f)) { Text("Cancel") }
                Button(
                    onClick = {
                        val name = effectiveName
                        if (name.isEmpty() || submitting) return@Button
                        submitting = true
                        error = null
                        scope.launch {
                            runCatching {
                                ApiClient.createArea(stagingId, name, null, token)
                            }.onSuccess { resp ->
                                submitting = false
                                onCreated(resp.area)
                            }.onFailure { t ->
                                submitting = false
                                error = t.message ?: "Failed to add"
                            }
                        }
                    },
                    enabled = effectiveName.isNotEmpty() && !submitting,
                    modifier = Modifier.weight(1f),
                ) {
                    if (submitting) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(14.dp),
                            strokeWidth = 2.dp,
                            color = MaterialTheme.colorScheme.onPrimary,
                        )
                    } else {
                        Text("Add")
                    }
                }
            }
        }
    }
}

// ---- Capture preview (Save / Discard) --------------------------------------

@Composable
internal fun CapturePreviewDialog(
    pending: PendingCapture,
    onSave: () -> Unit,
    onDiscard: () -> Unit,
) {
    Dialog(
        onDismissRequest = onDiscard,
        properties = DialogProperties(
            usePlatformDefaultWidth = false,
            dismissOnBackPress = true,
            dismissOnClickOutside = false,
        ),
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color.Black),
        ) {
            when (pending.target.mediaType) {
                CaptureMediaType.VIDEO -> VideoPreview(file = pending.file)
                else -> AsyncImage(
                    model = pending.file,
                    contentDescription = null,
                    contentScale = ContentScale.Fit,
                    modifier = Modifier.fillMaxSize(),
                )
            }

            // Top-left close/discard
            IconButton(
                onClick = onDiscard,
                modifier = Modifier.align(Alignment.TopStart).padding(12.dp),
            ) {
                Icon(Icons.Filled.Close, contentDescription = "Discard", tint = Color.White)
            }

            // Bottom bar
            Row(
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .fillMaxWidth()
                    .background(Color.Black.copy(alpha = 0.55f))
                    .padding(16.dp),
                horizontalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                Button(
                    onClick = onDiscard,
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color(0xFFD32F2F),
                        contentColor = Color.White,
                    ),
                    modifier = Modifier.weight(1f),
                ) {
                    Icon(Icons.Outlined.Delete, contentDescription = null)
                    Spacer(Modifier.width(6.dp))
                    Text("Discard")
                }
                Button(
                    onClick = onSave,
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color(0xFF2E7D32),
                        contentColor = Color.White,
                    ),
                    modifier = Modifier.weight(1f),
                ) {
                    Icon(Icons.Filled.Check, contentDescription = null)
                    Spacer(Modifier.width(6.dp))
                    Text("Save")
                }
            }
        }
    }
}

// ---- Media viewer (tap a thumb) --------------------------------------------

@Composable
internal fun MediaViewerDialog(
    capture: CaptureEntity,
    onDelete: () -> Unit,
    onDismiss: () -> Unit,
) {
    Dialog(
        onDismissRequest = onDismiss,
        properties = DialogProperties(usePlatformDefaultWidth = false),
    ) {
        Box(modifier = Modifier.fillMaxSize().background(Color.Black)) {
            val file = remember(capture.id) { File(capture.filePath) }
            if (CaptureMediaType.fromWire(capture.mediaType) == CaptureMediaType.VIDEO) {
                VideoPreview(file = file)
            } else {
                AsyncImage(
                    model = file,
                    contentDescription = null,
                    contentScale = ContentScale.Fit,
                    modifier = Modifier.fillMaxSize(),
                )
            }

            IconButton(
                onClick = onDismiss,
                modifier = Modifier.align(Alignment.TopStart).padding(12.dp),
            ) {
                Icon(Icons.Filled.Close, contentDescription = "Close", tint = Color.White)
            }
            IconButton(
                onClick = onDelete,
                modifier = Modifier.align(Alignment.TopEnd).padding(12.dp),
            ) {
                Icon(Icons.Outlined.Delete, contentDescription = "Delete", tint = Color.White)
            }

            // Bottom caption so the user sees which area/status they're viewing.
            Column(
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .fillMaxWidth()
                    .background(Color.Black.copy(alpha = 0.4f))
                    .padding(16.dp),
            ) {
                Text(
                    capture.areaName ?: "Unassigned",
                    color = Color.White,
                    style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
                )
                Text(
                    "${CaptureMediaType.fromWire(capture.mediaType).name.lowercase()} · ${capture.status.lowercase()}",
                    color = Color.White.copy(alpha = 0.8f),
                    style = MaterialTheme.typography.labelSmall,
                )
            }
        }
    }
}

// ---- Shared video preview --------------------------------------------------

@Composable
private fun VideoPreview(file: File) {
    // VideoView doesn't preserve aspect ratio by default — it stretches to
    // fill. Wrap it in a Box that sets the width/height based on the video's
    // own dimensions so the frame sits correctly within the black container.
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center,
    ) {
        AndroidView(
            factory = { ctx ->
                VideoView(ctx).apply {
                    setVideoURI(Uri.fromFile(file))
                    setOnPreparedListener { mp ->
                        mp.isLooping = true
                        // Match the VideoView's measured size to the video
                        // dimensions so aspect is preserved. Without this,
                        // VideoView stretches to fill its layout params.
                        val vw = mp.videoWidth
                        val vh = mp.videoHeight
                        if (vw > 0 && vh > 0) {
                            layoutParams = layoutParams.apply {
                                val containerW = (parent as? android.view.View)?.width ?: vw
                                val containerH = (parent as? android.view.View)?.height ?: vh
                                val scale = minOf(
                                    containerW.toFloat() / vw,
                                    containerH.toFloat() / vh,
                                )
                                width = (vw * scale).toInt()
                                height = (vh * scale).toInt()
                            }
                            requestLayout()
                        }
                        start()
                    }
                }
            },
        )
    }
}
