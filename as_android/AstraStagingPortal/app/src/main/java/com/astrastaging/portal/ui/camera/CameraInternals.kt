package com.astrastaging.portal.ui.camera

import android.Manifest
import android.content.ContentValues
import android.content.pm.PackageManager
import android.provider.MediaStore
import androidx.camera.core.ImageCapture
import androidx.camera.core.ImageCaptureException
import androidx.camera.video.MediaStoreOutputOptions
import androidx.camera.video.Recorder
import androidx.camera.video.Recording
import androidx.camera.video.VideoCapture
import androidx.camera.video.VideoRecordEvent
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.awaitEachGesture
import androidx.compose.foundation.gestures.awaitFirstDown
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.text.drawText
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.foundation.border
import androidx.core.content.ContextCompat
import com.astrastaging.portal.data.media.CaptureMediaType
import java.io.File
import java.util.concurrent.Executor

// ---- Permissions -----------------------------------------------------------

internal fun hasCameraPerms(context: android.content.Context, mode: CaptureMediaType): Boolean {
    val cameraOk = ContextCompat.checkSelfPermission(context, Manifest.permission.CAMERA) ==
        PackageManager.PERMISSION_GRANTED
    if (mode != CaptureMediaType.VIDEO) return cameraOk
    val micOk = ContextCompat.checkSelfPermission(context, Manifest.permission.RECORD_AUDIO) ==
        PackageManager.PERMISSION_GRANTED
    return cameraOk && micOk
}

internal fun requiredPerms(mode: CaptureMediaType): Array<String> = when (mode) {
    CaptureMediaType.VIDEO -> arrayOf(Manifest.permission.CAMERA, Manifest.permission.RECORD_AUDIO)
    else -> arrayOf(Manifest.permission.CAMERA)
}

@Composable
internal fun PermissionWall(onCancel: () -> Unit) {
    Box(
        modifier = Modifier.fillMaxSize().background(Color.Black),
        contentAlignment = Alignment.Center,
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Text("Camera access is required.", color = Color.White)
            TextButton(onClick = onCancel) { Text("Close") }
        }
    }
}

// ---- Photo / Video toggle --------------------------------------------------

@Composable
internal fun ModeToggle(
    mode: CaptureMediaType,
    enabled: Boolean,
    onChange: (CaptureMediaType) -> Unit,
    modifier: Modifier = Modifier,
) {
    Row(
        modifier = modifier,
        horizontalArrangement = Arrangement.Center,
    ) {
        Row(
            modifier = Modifier
                .background(Color.White.copy(alpha = 0.18f), RoundedCornerShape(24.dp))
                .padding(4.dp),
            horizontalArrangement = Arrangement.spacedBy(2.dp),
        ) {
            ModeChip(
                label = "Photo",
                selected = mode == CaptureMediaType.PHOTO,
                enabled = enabled,
                onClick = { onChange(CaptureMediaType.PHOTO) },
            )
            ModeChip(
                label = "Video",
                selected = mode == CaptureMediaType.VIDEO,
                enabled = enabled,
                onClick = { onChange(CaptureMediaType.VIDEO) },
            )
        }
    }
}

@Composable
private fun ModeChip(
    label: String,
    selected: Boolean,
    enabled: Boolean,
    onClick: () -> Unit,
) {
    Box(
        modifier = Modifier
            .background(
                if (selected) Color.White else Color.Transparent,
                RoundedCornerShape(20.dp),
            )
            .pointerInput(enabled, selected) {
                if (enabled) {
                    detectTapGestures(onTap = { onClick() })
                }
            }
            .padding(horizontal = 18.dp, vertical = 8.dp),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            label,
            color = if (selected) Color.Black else Color.White,
            fontWeight = if (selected) FontWeight.SemiBold else FontWeight.Normal,
        )
    }
}

// ---- Shutter ---------------------------------------------------------------

@Composable
internal fun ShutterButton(
    captureMode: CaptureMediaType,
    isRecording: Boolean,
    onClick: () -> Unit,
) {
    Box(
        modifier = Modifier
            .size(76.dp)
            .border(4.dp, Color.White, CircleShape)
            .pointerInput(Unit) {
                detectTapGestures(onTap = { onClick() })
            },
        contentAlignment = Alignment.Center,
    ) {
        when (captureMode) {
            CaptureMediaType.VIDEO -> {
                if (isRecording) {
                    Box(
                        modifier = Modifier
                            .size(28.dp)
                            .background(Color.Red, RoundedCornerShape(6.dp)),
                    )
                } else {
                    Box(
                        modifier = Modifier
                            .size(56.dp)
                            .background(Color.Red, CircleShape),
                    )
                }
            }
            else -> {
                Box(
                    modifier = Modifier
                        .size(60.dp)
                        .background(Color.White, CircleShape),
                )
            }
        }
    }
}

// ---- Zoom UI ---------------------------------------------------------------

@Composable
internal fun ZoomChips(
    currentRatio: Float,
    minZoom: Float,
    maxZoom: Float,
    onSetRatio: (Float) -> Unit,
    onDialActiveChange: (Boolean) -> Unit,
    modifier: Modifier = Modifier,
) {
    val z = (currentRatio * 10f).let { kotlin.math.round(it) / 10f }
    val values: List<Float>
    val selectedIdx: Int
    when {
        z < 1f -> { values = listOf(z, 1f, 2f); selectedIdx = 0 }
        z <= 2f -> { values = listOf(0.5f, z, 2f); selectedIdx = 1 }
        else -> { values = listOf(0.5f, 1f, z); selectedIdx = 2 }
    }
    Row(
        modifier = modifier,
        horizontalArrangement = Arrangement.spacedBy(10.dp, Alignment.CenterHorizontally),
    ) {
        values.forEachIndexed { idx, value ->
            ZoomChip(
                value = value,
                isSelected = idx == selectedIdx,
                minZoom = minZoom,
                maxZoom = maxZoom,
                currentRatio = currentRatio,
                onSetRatio = onSetRatio,
                onDialActiveChange = onDialActiveChange,
            )
        }
    }
}

@Composable
private fun ZoomChip(
    value: Float,
    isSelected: Boolean,
    currentRatio: Float,
    minZoom: Float,
    maxZoom: Float,
    onSetRatio: (Float) -> Unit,
    onDialActiveChange: (Boolean) -> Unit,
) {
    val latestRatio = rememberUpdatedState(currentRatio)
    val latestOnSet = rememberUpdatedState(onSetRatio)
    val latestDial = rememberUpdatedState(onDialActiveChange)
    val latestValue = rememberUpdatedState(value)
    val latestIsSelected = rememberUpdatedState(isSelected)
    val dpPerZoom = with(LocalDensity.current) { 80.dp.toPx() }

    Box(
        modifier = Modifier
            .widthIn(min = 48.dp)
            .height(42.dp)
            .background(
                if (isSelected) Color.White else Color.White.copy(alpha = 0.2f),
                RoundedCornerShape(21.dp),
            )
            .pointerInput(Unit) {
                awaitEachGesture {
                    val down = awaitFirstDown(requireUnconsumed = false)
                    val startX = down.position.x
                    val startTime = System.currentTimeMillis()
                    val anchor = latestValue.value.coerceIn(minZoom, maxZoom)
                    var slidingStarted = false

                    while (true) {
                        val event = awaitPointerEvent()
                        val change = event.changes.firstOrNull { it.id == down.id } ?: break
                        if (!change.pressed) break

                        val dx = change.position.x - startX
                        val heldLongEnough = System.currentTimeMillis() - startTime >= 220L
                        val movedEnough = kotlin.math.abs(dx) >= dpPerZoom * 0.05f

                        if (!slidingStarted && (heldLongEnough || movedEnough)) {
                            slidingStarted = true
                            latestOnSet.value(anchor)
                            latestDial.value(true)
                        }

                        if (slidingStarted) {
                            val next = (anchor - dx / dpPerZoom).coerceIn(minZoom, maxZoom)
                            if (kotlin.math.abs(next - latestRatio.value) >= 0.01f) {
                                latestOnSet.value(next)
                            }
                            change.consume()
                        }
                    }

                    if (slidingStarted) {
                        latestDial.value(false)
                    } else {
                        val elapsed = System.currentTimeMillis() - startTime
                        if (elapsed < 400L && !latestIsSelected.value) {
                            latestOnSet.value(anchor)
                        }
                    }
                }
            },
        contentAlignment = Alignment.Center,
    ) {
        Text(
            chipLabel(value, isSelected),
            color = if (isSelected) Color.Black else Color.White,
            fontWeight = FontWeight.Bold,
        )
    }
}

private fun chipLabel(value: Float, selected: Boolean): String {
    val suffix = if (selected) "x" else ""
    return if (value < 1f) {
        "%.1f%s".format(value, suffix)
    } else if (kotlin.math.abs(value - kotlin.math.round(value)) < 0.05f) {
        "%.0f%s".format(value, suffix)
    } else {
        "%.1f%s".format(value, suffix)
    }
}

@Composable
internal fun ZoomDial(
    zoomRatio: Float,
    minZoom: Float,
    maxZoom: Float,
    modifier: Modifier = Modifier,
) {
    val density = LocalDensity.current
    val majorStops = listOf(0.5f, 1f, 2f, 4f, 10f)
    val pxPerStep = with(density) { 16.dp.toPx() }
    val majorLabelStyle = androidx.compose.ui.text.TextStyle(
        color = Color.White.copy(alpha = 0.9f),
        fontWeight = FontWeight.SemiBold,
        fontSize = 11.sp,
    )
    val textMeasurer = androidx.compose.ui.text.rememberTextMeasurer()

    androidx.compose.foundation.Canvas(
        modifier = modifier
            .fillMaxWidth()
            .height(42.dp),
    ) {
        val W = size.width
        val H = size.height
        val cx = W / 2f
        val midY = H / 2f

        val halfW = W / 2f + pxPerStep
        val zoomHalf = (halfW / pxPerStep) * 0.1f
        var z = kotlin.math.round(maxOf(minZoom, zoomRatio - zoomHalf) * 10f) / 10f
        val zMax = minOf(maxZoom, zoomRatio + zoomHalf)

        while (z <= zMax + 0.001f) {
            val dx = (z - zoomRatio) / 0.1f * pxPerStep
            val x = cx + dx
            val isMajor = majorStops.any { kotlin.math.abs(it - z) < 0.05f && it <= maxZoom + 0.01f }
            val tickH = with(density) { (if (isMajor) 10.dp else 5.dp).toPx() }
            drawLine(
                color = Color.White.copy(alpha = if (isMajor) 0.95f else 0.5f),
                start = androidx.compose.ui.geometry.Offset(x, midY - tickH),
                end = androidx.compose.ui.geometry.Offset(x, midY + tickH),
                strokeWidth = with(density) { (if (isMajor) 2.dp else 1.dp).toPx() },
            )

            if (isMajor) {
                val label = if (kotlin.math.abs(z - kotlin.math.round(z)) < 0.05f) {
                    "%d".format(z.toInt())
                } else {
                    "%.1f".format(z)
                }
                val lay = textMeasurer.measure(label, majorLabelStyle)
                drawText(
                    lay,
                    topLeft = androidx.compose.ui.geometry.Offset(
                        x - lay.size.width / 2f,
                        midY + tickH + with(density) { 2.dp.toPx() },
                    ),
                )
            }
            z = kotlin.math.round((z + 0.1f) * 10f) / 10f
        }

        val triTop = midY - with(density) { 16.dp.toPx() }
        val triBottom = midY - with(density) { 10.dp.toPx() }
        val triHalf = with(density) { 5.dp.toPx() }
        val tri = androidx.compose.ui.graphics.Path().apply {
            moveTo(cx - triHalf, triTop)
            lineTo(cx + triHalf, triTop)
            lineTo(cx, triBottom)
            close()
        }
        drawPath(tri, color = Color.White)
    }
}

// ---- Capture helpers --------------------------------------------------------

internal fun takePhotoToCache(
    context: android.content.Context,
    imageCapture: ImageCapture,
    executor: Executor,
    onDone: (File?, String?, Throwable?) -> Unit,
) {
    val outDir = File(context.cacheDir, "camera").apply { mkdirs() }
    val file = File(outDir, "photo-${System.currentTimeMillis()}.jpg")
    val output = ImageCapture.OutputFileOptions.Builder(file).build()
    imageCapture.takePicture(
        output, executor,
        object : ImageCapture.OnImageSavedCallback {
            override fun onImageSaved(result: ImageCapture.OutputFileResults) {
                onDone(file, "image/jpeg", null)
            }
            override fun onError(exception: ImageCaptureException) {
                onDone(null, null, exception)
            }
        }
    )
}

@androidx.annotation.OptIn(androidx.camera.video.ExperimentalPersistentRecording::class)
internal fun startVideoRecording(
    context: android.content.Context,
    videoCapture: VideoCapture<Recorder>,
    executor: Executor,
    onFinished: (File?, String?, Throwable?) -> Unit,
): Recording {
    val name = "camera-video-${System.currentTimeMillis()}"
    val contentValues = ContentValues().apply {
        put(MediaStore.Video.Media.DISPLAY_NAME, name)
        put(MediaStore.Video.Media.MIME_TYPE, "video/mp4")
    }
    val outputOptions = MediaStoreOutputOptions.Builder(
        context.contentResolver,
        MediaStore.Video.Media.EXTERNAL_CONTENT_URI,
    ).setContentValues(contentValues).build()

    val pendingRecording = videoCapture.output.prepareRecording(context, outputOptions)

    val finish: (VideoRecordEvent) -> Unit = { event ->
        if (event is VideoRecordEvent.Finalize) {
            if (event.hasError()) {
                onFinished(null, null, event.cause)
            } else {
                val uri = event.outputResults.outputUri
                val copy = copyVideoUriToCache(context, uri)
                onFinished(copy, "video/mp4", null)
            }
        }
    }

    return try {
        pendingRecording.withAudioEnabled().start(executor, finish)
    } catch (_: SecurityException) {
        pendingRecording.start(executor, finish)
    }
}

private fun copyVideoUriToCache(
    context: android.content.Context,
    uri: android.net.Uri,
): File? = runCatching {
    val outDir = File(context.cacheDir, "camera").apply { mkdirs() }
    val dest = File(outDir, "video-${System.currentTimeMillis()}.mp4")
    context.contentResolver.openInputStream(uri)?.use { input ->
        dest.outputStream().use { output -> input.copyTo(output) }
    }
    dest
}.getOrNull()
