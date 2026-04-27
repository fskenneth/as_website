package com.astrastaging.portal.ui.camera

import android.util.Log
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.camera.core.AspectRatio
import androidx.camera.core.Camera
import androidx.camera.core.CameraControl
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageCapture
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.video.FallbackStrategy
import androidx.camera.video.Quality
import androidx.camera.video.QualitySelector
import androidx.camera.video.Recorder
import androidx.camera.video.Recording
import androidx.camera.video.VideoCapture
import androidx.camera.view.PreviewView
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.detectHorizontalDragGestures
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.systemBars
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableLongStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
import androidx.lifecycle.compose.LocalLifecycleOwner
import com.astrastaging.portal.data.media.CaptureMediaType
import java.io.File

/**
 * Reusable camera surface — preview + zoom + photo/video toggle + shutter
 * + close. No consultation/staging/area chrome. Bind once anywhere a quick
 * camera capture is needed (chat picker, future profile photo, etc.).
 *
 * Callers receive each capture via [onCapture] and dismiss via [onClose].
 * The composable handles its own permission prompt (camera + mic for
 * video).
 */
@Composable
fun CameraSheet(
    initialMediaType: CaptureMediaType = CaptureMediaType.PHOTO,
    onClose: () -> Unit,
    onCapture: (file: File, mime: String, type: CaptureMediaType) -> Unit,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val executor = remember { ContextCompat.getMainExecutor(context) }

    var captureMode by remember { mutableStateOf(initialMediaType) }

    // Permission gate.
    var permissionGranted by remember {
        mutableStateOf(hasCameraPerms(context, captureMode))
    }
    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { results -> permissionGranted = results.values.all { it } }
    LaunchedEffect(captureMode) {
        if (!permissionGranted) permissionLauncher.launch(requiredPerms(captureMode))
    }
    if (!permissionGranted) {
        PermissionWall(onCancel = onClose)
        return
    }

    // Track physical orientation so saved photos carry correct EXIF rotation.
    var physicalRotation by remember { mutableIntStateOf(android.view.Surface.ROTATION_0) }
    DisposableEffect(Unit) {
        val listener = object : android.view.OrientationEventListener(context) {
            override fun onOrientationChanged(orientation: Int) {
                if (orientation == ORIENTATION_UNKNOWN) return
                physicalRotation = when {
                    orientation in 45..134  -> android.view.Surface.ROTATION_270
                    orientation in 135..224 -> android.view.Surface.ROTATION_180
                    orientation in 225..314 -> android.view.Surface.ROTATION_90
                    else                    -> android.view.Surface.ROTATION_0
                }
            }
        }
        listener.enable()
        onDispose { listener.disable() }
    }

    // CameraX wiring.
    val previewView = remember {
        PreviewView(context).apply { scaleType = PreviewView.ScaleType.FIT_CENTER }
    }
    val imageCapture = remember {
        ImageCapture.Builder().setTargetAspectRatio(AspectRatio.RATIO_4_3).build()
    }
    val recorder = remember {
        Recorder.Builder()
            .setQualitySelector(
                QualitySelector.fromOrderedList(
                    listOf(Quality.SD, Quality.HD, Quality.HIGHEST),
                    FallbackStrategy.higherQualityOrLowerThan(Quality.SD),
                )
            )
            .build()
    }
    val videoCapture = remember { VideoCapture.withOutput(recorder) }
    var activeRecording by remember { mutableStateOf<Recording?>(null) }
    var isRecording by remember { mutableStateOf(false) }
    var recordingStartedAt by remember { mutableStateOf<Long?>(null) }
    var recordingElapsedMs by remember { mutableLongStateOf(0L) }
    LaunchedEffect(recordingStartedAt) {
        val s = recordingStartedAt ?: return@LaunchedEffect
        while (recordingStartedAt == s) {
            recordingElapsedMs = System.currentTimeMillis() - s
            kotlinx.coroutines.delay(500)
        }
    }
    var zoomRatio by remember { mutableFloatStateOf(1f) }
    var minZoom by remember { mutableFloatStateOf(1f) }
    var maxZoom by remember { mutableFloatStateOf(2f) }
    var cameraControl by remember { mutableStateOf<CameraControl?>(null) }
    var boundCamera by remember { mutableStateOf<Camera?>(null) }
    var zoomDialActive by remember { mutableStateOf(false) }

    // Rebind on mode flip — some devices need exclusive use cases.
    DisposableEffect(lifecycleOwner, captureMode) {
        val providerFuture = ProcessCameraProvider.getInstance(context)
        providerFuture.addListener({
            val provider = providerFuture.get()
            val preview = Preview.Builder().build().also {
                it.setSurfaceProvider(previewView.surfaceProvider)
            }
            val selector = CameraSelector.DEFAULT_BACK_CAMERA
            runCatching { provider.unbindAll() }
            val camera = try {
                if (captureMode == CaptureMediaType.VIDEO) {
                    provider.bindToLifecycle(
                        lifecycleOwner, selector, preview, videoCapture,
                    )
                } else {
                    provider.bindToLifecycle(
                        lifecycleOwner, selector, preview, imageCapture,
                    )
                }
            } catch (t: Throwable) {
                Log.w("CameraSheet", "bind failed: ${t.message}", t)
                null
            }
            camera?.let {
                boundCamera = it
                cameraControl = it.cameraControl
                val zoomState = it.cameraInfo.zoomState.value
                minZoom = zoomState?.minZoomRatio ?: 0.5f
                maxZoom = zoomState?.maxZoomRatio ?: 5f
                val target = 1f.coerceIn(minZoom, maxZoom)
                it.cameraControl.setZoomRatio(target)
                zoomRatio = target
            }
        }, executor)
        onDispose {
            runCatching { providerFuture.get().unbindAll() }
        }
    }

    Column(
        modifier
            .fillMaxSize()
            .background(Color.Black)
            .windowInsetsPadding(WindowInsets.systemBars),
    ) {
        // Top bar: only the close button (no dictation/area chrome here).
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 12.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Box(
                modifier = Modifier
                    .size(44.dp)
                    .background(Color.Black.copy(alpha = 0.45f), CircleShape)
                    .border(1.5.dp, Color.White.copy(alpha = 0.9f), CircleShape)
                    .clickable { onClose() },
                contentAlignment = Alignment.Center,
            ) {
                Icon(
                    Icons.Filled.Close,
                    contentDescription = "Close",
                    tint = Color.White,
                    modifier = Modifier.size(22.dp),
                )
            }
            Spacer(Modifier.weight(1f))
        }

        // Preview window — 4:3 with horizontal-swipe mode toggle.
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f),
            contentAlignment = Alignment.Center,
        ) {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .aspectRatio(3f / 4f)
                    .pointerInput(isRecording) {
                        if (isRecording) return@pointerInput
                        detectHorizontalDragGestures(
                            onDragStart = {},
                            onDragEnd = {},
                            onDragCancel = {},
                        ) { _, dragAmount: Float ->
                            if (dragAmount < -20f && captureMode == CaptureMediaType.PHOTO) {
                                captureMode = CaptureMediaType.VIDEO
                            } else if (dragAmount > 20f && captureMode == CaptureMediaType.VIDEO) {
                                captureMode = CaptureMediaType.PHOTO
                            }
                        }
                    },
            ) {
                AndroidView(
                    factory = { previewView },
                    modifier = Modifier.fillMaxSize(),
                )
                if (isRecording) {
                    val sec = recordingElapsedMs / 1000
                    Row(
                        modifier = Modifier
                            .align(Alignment.TopCenter)
                            .padding(top = 14.dp)
                            .background(Color.Black.copy(alpha = 0.55f), CircleShape)
                            .padding(horizontal = 10.dp, vertical = 6.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Box(
                            modifier = Modifier
                                .size(8.dp)
                                .background(Color.Red, CircleShape),
                        )
                        Spacer(Modifier.width(6.dp))
                        Text(
                            "%02d:%02d".format(sec / 60, sec % 60),
                            color = Color.White,
                            fontWeight = FontWeight.Bold,
                            style = MaterialTheme.typography.labelMedium,
                        )
                    }
                }
            }
        }

        // Bottom controls: zoom readout, zoom chips/dial, mode toggle, shutter.
        Column(modifier = Modifier.fillMaxWidth()) {
            Text(
                "%.1fx".format(zoomRatio),
                color = Color.White,
                fontWeight = FontWeight.Bold,
                style = MaterialTheme.typography.titleMedium,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 4.dp)
                    .alpha(if (zoomDialActive) 1f else 0f),
                textAlign = androidx.compose.ui.text.style.TextAlign.Center,
            )
            val usefulMaxZoom = minOf(maxZoom, 2f)
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(42.dp)
                    .padding(bottom = 8.dp),
                contentAlignment = Alignment.Center,
            ) {
                ZoomChips(
                    currentRatio = zoomRatio,
                    minZoom = minZoom,
                    maxZoom = usefulMaxZoom,
                    onSetRatio = { r ->
                        val clamped = r.coerceIn(minZoom, usefulMaxZoom)
                        cameraControl?.setZoomRatio(clamped)
                        zoomRatio = clamped
                    },
                    onDialActiveChange = { zoomDialActive = it },
                    modifier = Modifier
                        .fillMaxWidth()
                        .alpha(if (zoomDialActive) 0.001f else 1f),
                )
                if (zoomDialActive) {
                    ZoomDial(
                        zoomRatio = zoomRatio,
                        minZoom = minZoom,
                        maxZoom = usefulMaxZoom,
                        modifier = Modifier.fillMaxWidth(),
                    )
                }
            }

            ModeToggle(
                mode = captureMode,
                enabled = !isRecording,
                onChange = { captureMode = it },
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 32.dp, vertical = 8.dp),
            )

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 16.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.Center,
            ) {
                ShutterButton(
                    captureMode = captureMode,
                    isRecording = isRecording,
                    onClick = {
                        try {
                            if (captureMode == CaptureMediaType.VIDEO) {
                                if (isRecording) {
                                    runCatching { activeRecording?.stop() }
                                    activeRecording = null
                                    recordingStartedAt = null
                                    recordingElapsedMs = 0L
                                } else {
                                    activeRecording = startVideoRecording(
                                        context = context,
                                        videoCapture = videoCapture,
                                        executor = executor,
                                        onFinished = { file, mime, err ->
                                            isRecording = false
                                            recordingStartedAt = null
                                            recordingElapsedMs = 0L
                                            if (err == null && file != null && mime != null) {
                                                onCapture(file, mime, CaptureMediaType.VIDEO)
                                            }
                                        },
                                    )
                                    isRecording = true
                                    recordingStartedAt = System.currentTimeMillis()
                                }
                            } else {
                                imageCapture.targetRotation = physicalRotation
                                takePhotoToCache(
                                    context = context,
                                    imageCapture = imageCapture,
                                    executor = executor,
                                    onDone = { file, mime, err ->
                                        if (err == null && file != null && mime != null) {
                                            onCapture(file, mime, CaptureMediaType.PHOTO)
                                        }
                                    },
                                )
                            }
                        } catch (t: Throwable) {
                            Log.w("CameraSheet", "shutter threw: ${t.message}", t)
                        }
                    },
                )
            }
        }
    }
}
