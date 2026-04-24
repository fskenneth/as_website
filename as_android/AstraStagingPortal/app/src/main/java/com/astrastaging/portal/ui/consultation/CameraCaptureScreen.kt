package com.astrastaging.portal.ui.consultation

import android.Manifest
import android.content.ContentValues
import android.content.pm.PackageManager
import android.provider.MediaStore
import android.util.Log
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.camera.core.AspectRatio
import androidx.camera.core.Camera
import androidx.camera.core.CameraControl
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageCapture
import androidx.camera.core.ImageCaptureException
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.video.MediaStoreOutputOptions
import androidx.camera.video.Quality
import androidx.camera.video.FallbackStrategy
import androidx.camera.video.QualitySelector
import androidx.camera.video.Recorder
import androidx.camera.video.Recording
import androidx.camera.video.VideoCapture
import androidx.camera.video.VideoRecordEvent
import androidx.camera.view.PreviewView
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.ui.draw.alpha
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.awaitEachGesture
import androidx.compose.foundation.gestures.awaitFirstDown
import androidx.compose.foundation.gestures.detectHorizontalDragGestures
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBars
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.systemBars
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.ui.text.drawText
import androidx.compose.ui.unit.sp
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Camera
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.FiberManualRecord
import androidx.compose.material.icons.filled.Pause
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Stop
import androidx.compose.material.icons.outlined.Delete
import androidx.compose.material.icons.outlined.PlayCircle
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.TextButton
import androidx.compose.ui.draw.clip
import coil.compose.AsyncImage
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableLongStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.core.content.ContextCompat
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.outlined.Mic
import androidx.lifecycle.compose.LocalLifecycleOwner
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.astrastaging.portal.data.ApiClient
import com.astrastaging.portal.data.AreaCatalogEntry
import com.astrastaging.portal.data.StagingArea
import com.astrastaging.portal.data.media.CaptureMediaType
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import java.io.File
import java.util.Locale
import java.util.concurrent.Executor

/**
 * Full-screen camera overlay used by the Consultation tab.
 *
 * Layout (top-down):
 *   [X close]                                      (top safe area)
 *   [       4:3 preview frame (centered)      ]
 *   [Photo | Video]           mode toggle
 *   [  .5x   1x   2x  ]       zoom chips (tap = snap, long-press = gradual)
 *   [     Shutter     Area▼]  bottom row (above nav bar)
 *
 * The area chip shows the current area and opens an in-camera picker with
 * an always-on "+ New Area" entry so stagers never have to leave the
 * camera to file a photo under a new room.
 */
@Composable
fun CameraCaptureDialog(
    initialMediaType: CaptureMediaType,
    staging: com.astrastaging.portal.data.Staging,
    areas: List<StagingArea>,
    initialAreaId: String?,
    token: String,
    onCreateArea: suspend (name: String) -> StagingArea?,
    /** Fires for each successful capture. Camera stays open. */
    onCaptureTaken: (file: File, mime: String, type: CaptureMediaType, area: StagingArea?) -> Unit,
    /** Fires only when the user closes the camera (always nulls). */
    onResult: (file: File?, mime: String?, type: CaptureMediaType, area: StagingArea?) -> Unit,
) {
    Dialog(
        onDismissRequest = { onResult(null, null, initialMediaType, null) },
        properties = DialogProperties(
            usePlatformDefaultWidth = false,
            dismissOnBackPress = true,
            dismissOnClickOutside = false,
        ),
    ) {
        CameraCaptureScreen(
            initialMediaType = initialMediaType,
            staging = staging,
            areas = areas,
            initialAreaId = initialAreaId,
            token = token,
            onCreateArea = onCreateArea,
            onCaptureTaken = onCaptureTaken,
            onResult = onResult,
        )
    }
}

@Composable
private fun CameraCaptureScreen(
    initialMediaType: CaptureMediaType,
    staging: com.astrastaging.portal.data.Staging,
    areas: List<StagingArea>,
    initialAreaId: String?,
    token: String,
    onCreateArea: suspend (name: String) -> StagingArea?,
    onCaptureTaken: (file: File, mime: String, type: CaptureMediaType, area: StagingArea?) -> Unit,
    onResult: (file: File?, mime: String?, type: CaptureMediaType, area: StagingArea?) -> Unit,
) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val executor = remember { ContextCompat.getMainExecutor(context) }
    val scope = rememberCoroutineScope()
    val dictationController = remember(context) { DictationController.get(context) }
    val dictationState by dictationController.state.collectAsStateWithLifecycle()

    // Local state that the user can mutate inside the camera.
    var captureMode by remember { mutableStateOf(initialMediaType) }
    var areaList by remember { mutableStateOf(areas) }
    var selectedArea by remember {
        mutableStateOf(areas.firstOrNull { it.id == initialAreaId })
    }
    var areaPickerOpen by remember { mutableStateOf(false) }
    val selectedAreaRef = rememberUpdatedState(selectedArea)
    val cameraMicLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission(),
    ) { granted ->
        if (granted) dictationController.start(staging, selectedAreaRef.value)
    }

    // Captures for this staging — drives the recent-thumbnail and gallery.
    val captureRepository = remember(context) {
        com.astrastaging.portal.data.media.CaptureRepository(context)
    }
    val allCapturesForStaging by captureRepository
        .observeForStaging(staging.id)
        .collectAsStateWithLifecycle(initialValue = emptyList<com.astrastaging.portal.data.media.CaptureEntity>())
    val recentCapturePath = allCapturesForStaging.lastOrNull()?.filePath
    var galleryOpen by remember { mutableStateOf(false) }

    // Track physical device orientation via gravity (OrientationEventListener).
    // Used to set the ImageCapture targetRotation right before each shot so
    // landscape photos are saved as landscape (correct EXIF rotation).
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

    // Permissions
    var permissionGranted by remember {
        mutableStateOf(hasCameraPerms(context, captureMode))
    }
    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { results -> permissionGranted = results.values.all { it } }
    LaunchedEffect(Unit) {
        if (!permissionGranted) {
            permissionLauncher.launch(requiredPerms(captureMode))
        }
    }

    if (!permissionGranted) {
        PermissionWall(onCancel = { onResult(null, null, captureMode, selectedArea) })
        return
    }

    // CameraX plumbing
    val previewView = remember {
        PreviewView(context).apply { scaleType = PreviewView.ScaleType.FIT_CENTER }
    }
    val imageCapture = remember {
        ImageCapture.Builder()
            .setTargetAspectRatio(AspectRatio.RATIO_4_3)
            .build()
    }
    val recorder = remember {
        Recorder.Builder()
            // Prefer SD (640×480, 4:3) to match the preview aspect; fall
            // back to HD/HIGHEST if the device doesn't expose SD (some
            // modern flagships skip it). Without a fallback a missing
            // quality level caused bindToLifecycle to fail.
            .setQualitySelector(
                QualitySelector.fromOrderedList(
                    listOf(Quality.SD, Quality.HD, Quality.HIGHEST),
                    FallbackStrategy.higherQualityOrLowerThan(Quality.SD),
                )
            )
            .build()
    }
    val videoCapture = remember { VideoCapture.withOutput(recorder) }
    var recording by remember { mutableStateOf<Recording?>(null) }
    var isRecording by remember { mutableStateOf(false) }
    // Timestamp the recording started at, for the on-screen mm:ss badge.
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
    // True while a press-and-hold zoom chip is active — hide the chips
    // and show the arc dial over the preview.
    var zoomDialActive by remember { mutableStateOf(false) }

    // Rebind CameraX whenever the capture mode flips. Some devices
    // (Razr Ultra among them) don't support preview + imageCapture +
    // videoCapture bound together — the video feed comes out black. So
    // we bind only the use case the user is currently in.
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
                Log.w("CameraCapture", "bind failed: ${t.message}", t)
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
        Modifier
            .fillMaxSize()
            .background(Color.Black)
            .windowInsetsPadding(WindowInsets.systemBars),
    ) {
        // 1. Top section: close button on the left, area-mic on the right.
        val topBarRecording = (dictationState.phase as? DictationController.Phase.Recording)
            ?.let { it.stagingId == staging.id && it.areaId == selectedArea?.id } == true
        val topBarElapsed = run {
            val sec = dictationState.elapsedMs / 1000
            "%02d:%02d".format(sec / 60, sec % 60)
        }
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
                    .clickable { onResult(null, null, captureMode, selectedArea) },
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
            // Top-right dictation mic — hidden in video mode entirely
            // (the video captures audio, so a separate dictation mic is
            // redundant even before the user hits record).
            if (captureMode != CaptureMediaType.VIDEO) Row(
                modifier = Modifier
                    .background(
                        if (topBarRecording) Color.Red.copy(alpha = 0.7f)
                        else Color.Black.copy(alpha = 0.45f),
                        if (topBarRecording) RoundedCornerShape(22.dp) else CircleShape,
                    )
                    .border(
                        1.5.dp, Color.White.copy(alpha = 0.9f),
                        if (topBarRecording) RoundedCornerShape(22.dp) else CircleShape,
                    )
                    .clickable {
                        val phase = dictationController.state.value.phase
                        val matches = phase is DictationController.Phase.Recording &&
                            phase.stagingId == staging.id && phase.areaId == selectedArea?.id
                        if (phase is DictationController.Phase.Recording) {
                            if (matches) dictationController.stopAndEnqueue()
                        } else {
                            val granted = androidx.core.content.ContextCompat.checkSelfPermission(
                                context, android.Manifest.permission.RECORD_AUDIO,
                            ) == android.content.pm.PackageManager.PERMISSION_GRANTED
                            if (granted) dictationController.start(staging, selectedArea)
                            else cameraMicLauncher.launch(android.Manifest.permission.RECORD_AUDIO)
                        }
                    }
                    .padding(horizontal = if (topBarRecording) 12.dp else 0.dp, vertical = 0.dp)
                    .then(if (topBarRecording) Modifier else Modifier.size(44.dp)),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.Center,
            ) {
                if (topBarRecording) {
                    Icon(
                        Icons.Filled.Mic,
                        contentDescription = "Stop dictation",
                        tint = Color.White,
                        modifier = Modifier.size(22.dp),
                    )
                    Spacer(Modifier.width(6.dp))
                    Text(
                        topBarElapsed,
                        color = Color.White,
                        fontWeight = FontWeight.Bold,
                        style = MaterialTheme.typography.labelMedium,
                    )
                } else {
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center,
                    ) {
                        Icon(
                            Icons.Outlined.Mic,
                            contentDescription = "Start dictation",
                            tint = Color.White,
                            modifier = Modifier.size(22.dp),
                        )
                    }
                }
            }
        }

        // 2. Middle section: 4:3 preview filling all remaining height.
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
                    // Horizontal swipe toggles Photo ↔ Video mode.
                    // Disabled while recording.
                    .pointerInput(isRecording) {
                        if (isRecording) return@pointerInput
                        // Track cumulative horizontal motion for a full
                        // swipe; flip mode when the user moves ~40dp in
                        // a single gesture.
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

        // 3. Bottom section: live zoom readout → ruler/chips → mode →
        //    shutter. The zoom value floats between preview and ruler
        //    while dragging; the ruler occupies the same slot as the
        //    hidden chips.
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
            // Ruler + drag are capped at 2× — digital zoom past that is
            // too noisy to be useful on phones without a tele lens.
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

            // Bottom row: shutter (center) + area chip (right).
            BottomControlRow(
                captureMode = captureMode,
                isRecording = isRecording,
                selectedArea = selectedArea,
                onShutter = {
                    // Wrap the whole path: any CameraX runtime throw (e.g.
                    // use-case not yet bound after a mode swap) should
                    // surface as a log line, not a process crash.
                    try {
                        if (captureMode == CaptureMediaType.VIDEO) {
                            if (isRecording) {
                                runCatching { recording?.stop() }
                                recording = null
                                recordingStartedAt = null
                                recordingElapsedMs = 0L
                            } else {
                                recording = startRecording(
                                    context = context,
                                    videoCapture = videoCapture,
                                    executor = executor,
                                    onFinished = { file, mime, err ->
                                        isRecording = false
                                        recordingStartedAt = null
                                        recordingElapsedMs = 0L
                                        if (err == null && file != null && mime != null) {
                                            onCaptureTaken(file, mime, captureMode, selectedArea)
                                        }
                                    },
                                )
                                isRecording = true
                                recordingStartedAt = System.currentTimeMillis()
                            }
                        } else {
                            imageCapture.targetRotation = physicalRotation
                            takePhoto(
                                context = context,
                                imageCapture = imageCapture,
                                executor = executor,
                                onDone = { file, mime, err ->
                                    if (err == null && file != null && mime != null) {
                                        onCaptureTaken(file, mime, captureMode, selectedArea)
                                    }
                                },
                            )
                        }
                    } catch (t: Throwable) {
                        Log.w("CameraCapture", "shutter threw: ${t.message}", t)
                    }
                },
                onOpenArea = { areaPickerOpen = true },
                recentCapturePath = recentCapturePath,
                onOpenGallery = { galleryOpen = true },
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 20.dp),
            )
        }

        if (galleryOpen) {
            InCameraGallery(
                captures = allCapturesForStaging,
                onDismiss = { galleryOpen = false },
                onDelete = { capture ->
                    scope.launch { captureRepository.deleteWithServer(capture, token) }
                },
            )
        }

        if (areaPickerOpen) {
            AreaPickerDialog(
                areas = areaList,
                selectedId = selectedArea?.id,
                token = token,
                onSelect = { area ->
                    selectedArea = area
                    areaPickerOpen = false
                },
                onCreateArea = { name ->
                    scope.launch {
                        onCreateArea(name)?.let { created ->
                            areaList = areaList + created
                            selectedArea = created
                            areaPickerOpen = false
                        }
                    }
                },
                onDismiss = { areaPickerOpen = false },
            )
        }
    }
}

private fun hasCameraPerms(context: android.content.Context, mode: CaptureMediaType): Boolean {
    val cameraOk = ContextCompat.checkSelfPermission(context, Manifest.permission.CAMERA) ==
        PackageManager.PERMISSION_GRANTED
    if (mode != CaptureMediaType.VIDEO) return cameraOk
    val micOk = ContextCompat.checkSelfPermission(context, Manifest.permission.RECORD_AUDIO) ==
        PackageManager.PERMISSION_GRANTED
    return cameraOk && micOk
}

private fun requiredPerms(mode: CaptureMediaType): Array<String> = when (mode) {
    CaptureMediaType.VIDEO -> arrayOf(Manifest.permission.CAMERA, Manifest.permission.RECORD_AUDIO)
    else -> arrayOf(Manifest.permission.CAMERA)
}

// ---- Components -------------------------------------------------------------

@Composable
private fun ModeToggle(
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

/** Fullscreen swipeable gallery. Used both in-camera (recent-thumbnail
 *  tap) and from the Consultation area section (tap any thumbnail).
 *  Thumbnail strip sits directly under the photo, not at the screen bottom. */
@Composable
fun InCameraGallery(
    captures: List<com.astrastaging.portal.data.media.CaptureEntity>,
    onDismiss: () -> Unit,
    initialCaptureId: String? = null,
    onDelete: ((com.astrastaging.portal.data.media.CaptureEntity) -> Unit)? = null,
) {
    var pendingDelete by remember {
        mutableStateOf<com.astrastaging.portal.data.media.CaptureEntity?>(null)
    }
    val initialPage = remember(initialCaptureId, captures) {
        initialCaptureId?.let { id ->
            captures.indexOfFirst { it.id == id }.takeIf { it >= 0 }
        } ?: captures.lastIndex.coerceAtLeast(0)
    }
    val pagerState = androidx.compose.foundation.pager.rememberPagerState(
        initialPage = initialPage,
        pageCount = { captures.size },
    )
    Dialog(
        onDismissRequest = onDismiss,
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
            if (captures.isEmpty()) {
                Text(
                    "No captures yet.",
                    color = Color.White,
                    modifier = Modifier.align(Alignment.Center),
                )
            } else {
                val scope = rememberCoroutineScope()

                // Centered cluster: the photo + thumbnail strip live
                // together in the middle so the strip hugs the bottom
                // edge of the photo rather than the screen bottom.
                Column(
                    modifier = Modifier.fillMaxSize(),
                    verticalArrangement = Arrangement.Center,
                ) {
                    androidx.compose.foundation.pager.HorizontalPager(
                        state = pagerState,
                        modifier = Modifier
                            .fillMaxWidth()
                            .aspectRatio(3f / 4f),
                    ) { index ->
                        val c = captures[index]
                        Box(
                            modifier = Modifier.fillMaxSize(),
                            contentAlignment = Alignment.Center,
                        ) {
                            val isVideo = com.astrastaging.portal.data.media.CaptureMediaType
                                .fromWire(c.mediaType) ==
                                com.astrastaging.portal.data.media.CaptureMediaType.VIDEO
                            if (isVideo) {
                                GalleryVideoPlayer(filePath = c.filePath)
                            } else {
                                AsyncImage(
                                    model = File(c.filePath),
                                    contentDescription = null,
                                    modifier = Modifier.fillMaxSize(),
                                    contentScale = androidx.compose.ui.layout.ContentScale.Fit,
                                )
                            }
                        }
                    }

                    // Thumbnail strip
                    androidx.compose.foundation.lazy.LazyRow(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(Color.Black.copy(alpha = 0.5f))
                            .padding(horizontal = 8.dp, vertical = 8.dp),
                        horizontalArrangement = Arrangement.spacedBy(6.dp),
                    ) {
                        items(captures.size) { index ->
                            val c = captures[index]
                            val active = pagerState.currentPage == index
                            Box(
                                modifier = Modifier
                                    .size(56.dp)
                                    .clip(RoundedCornerShape(6.dp))
                                    .background(Color.Black)
                                    .border(
                                        if (active) 2.5.dp else 1.dp,
                                        if (active) Color.White else Color.White.copy(alpha = 0.3f),
                                        RoundedCornerShape(6.dp),
                                    )
                                    .clickable {
                                        scope.launch { pagerState.animateScrollToPage(index) }
                                    },
                            ) {
                                val isVideo = com.astrastaging.portal.data.media.CaptureMediaType
                                    .fromWire(c.mediaType) ==
                                    com.astrastaging.portal.data.media.CaptureMediaType.VIDEO
                                AsyncImage(
                                    model = File(c.filePath),
                                    contentDescription = null,
                                    modifier = Modifier.fillMaxSize(),
                                    contentScale = androidx.compose.ui.layout.ContentScale.Crop,
                                )
                                if (isVideo) {
                                    Icon(
                                        Icons.Outlined.PlayCircle,
                                        contentDescription = null,
                                        tint = Color.White.copy(alpha = 0.9f),
                                        modifier = Modifier
                                            .align(Alignment.Center)
                                            .size(18.dp),
                                    )
                                }
                            }
                        }
                    }
                }
            }

            // Close button (top-left).
            Box(
                modifier = Modifier
                    .align(Alignment.TopStart)
                    .windowInsetsPadding(WindowInsets.systemBars)
                    .padding(horizontal = 12.dp, vertical = 8.dp)
                    .size(44.dp)
                    .background(Color.Black.copy(alpha = 0.55f), CircleShape)
                    .border(1.5.dp, Color.White.copy(alpha = 0.9f), CircleShape)
                    .clickable { onDismiss() },
                contentAlignment = Alignment.Center,
            ) {
                Icon(
                    Icons.Filled.Close,
                    contentDescription = "Close gallery",
                    tint = Color.White,
                    modifier = Modifier.size(22.dp),
                )
            }

            // Delete button (top-right) — confirms before removing the
            // current capture.
            if (onDelete != null && captures.isNotEmpty()) {
                Box(
                    modifier = Modifier
                        .align(Alignment.TopEnd)
                        .windowInsetsPadding(WindowInsets.systemBars)
                        .padding(horizontal = 12.dp, vertical = 8.dp)
                        .size(44.dp)
                        .background(Color(0xFFD32F2F).copy(alpha = 0.85f), CircleShape)
                        .border(1.5.dp, Color.White.copy(alpha = 0.9f), CircleShape)
                        .clickable {
                            pendingDelete = captures.getOrNull(pagerState.currentPage)
                        },
                    contentAlignment = Alignment.Center,
                ) {
                    Icon(
                        Icons.Outlined.Delete,
                        contentDescription = "Delete capture",
                        tint = Color.White,
                        modifier = Modifier.size(22.dp),
                    )
                }
            }
        }
    }

    pendingDelete?.let { target ->
        AlertDialog(
            onDismissRequest = { pendingDelete = null },
            title = { Text("Delete this capture?") },
            text = {
                Text("This removes the file and cancels any pending upload.")
            },
            confirmButton = {
                TextButton(onClick = {
                    onDelete?.invoke(target)
                    pendingDelete = null
                }) { Text("Delete", color = MaterialTheme.colorScheme.error) }
            },
            dismissButton = {
                TextButton(onClick = { pendingDelete = null }) { Text("Cancel") }
            },
        )
    }
}

/** Minimal video player. Auto-hides the center play/pause after 2s of
 *  idle while playing; tap anywhere to bring it back. Always visible
 *  while paused. Progress bar is draggable to scrub. Smooth ~33 ms
 *  polling so motion looks continuous. */
@Composable
private fun GalleryVideoPlayer(filePath: String) {
    val videoViewHolder = remember { mutableStateOf<android.widget.VideoView?>(null) }
    var isPlaying by remember { mutableStateOf(false) }
    var progress by remember { mutableFloatStateOf(0f) }
    var durationMs by remember { mutableIntStateOf(1) }
    var controlsVisible by remember { mutableStateOf(true) }
    var isScrubbing by remember { mutableStateOf(false) }
    var lastInteractionAt by remember { mutableLongStateOf(System.currentTimeMillis()) }

    // ~33 ms (30 fps) polling so the bar looks continuous.
    LaunchedEffect(filePath) {
        while (true) {
            val v = videoViewHolder.value
            if (v != null) {
                val dur = v.duration.coerceAtLeast(1)
                durationMs = dur
                if (!isScrubbing) {
                    progress = (v.currentPosition.toFloat() / dur.toFloat())
                        .coerceIn(0f, 1f)
                }
                isPlaying = v.isPlaying
            }
            // Auto-hide the button after 2s of no interaction, but only
            // while playing. When paused the button stays on.
            if (isPlaying &&
                System.currentTimeMillis() - lastInteractionAt > 2000 &&
                controlsVisible &&
                !isScrubbing
            ) {
                controlsVisible = false
            }
            kotlinx.coroutines.delay(33)
        }
    }

    fun flashControls() {
        controlsVisible = true
        lastInteractionAt = System.currentTimeMillis()
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black)
            .pointerInput(Unit) {
                detectTapGestures(onTap = { flashControls() })
            },
    ) {
        androidx.compose.ui.viewinterop.AndroidView(
            modifier = Modifier.fillMaxSize(),
            factory = { ctx ->
                android.widget.VideoView(ctx).apply {
                    setMediaController(null)
                    setVideoURI(android.net.Uri.fromFile(java.io.File(filePath)))
                    setOnPreparedListener { mp ->
                        mp.isLooping = false
                        start()
                    }
                    setOnCompletionListener {
                        isPlaying = false
                        seekTo(0)
                        controlsVisible = true
                    }
                    videoViewHolder.value = this
                }
            },
            update = { view ->
                val uri = android.net.Uri.fromFile(java.io.File(filePath))
                if (view.tag != uri.toString()) {
                    view.tag = uri.toString()
                    view.setVideoURI(uri)
                }
            },
        )

        // Center play/pause — visible when paused, or when the user
        // recently tapped; fades out after 2s while playing.
        androidx.compose.animation.AnimatedVisibility(
            visible = controlsVisible || !isPlaying,
            modifier = Modifier.align(Alignment.Center),
            enter = androidx.compose.animation.fadeIn(),
            exit = androidx.compose.animation.fadeOut(),
        ) {
            IconButton(
                onClick = {
                    val v = videoViewHolder.value ?: return@IconButton
                    if (v.isPlaying) {
                        v.pause()
                        controlsVisible = true
                    } else {
                        if (v.currentPosition >= v.duration - 100) v.seekTo(0)
                        v.start()
                        flashControls()
                    }
                },
            ) {
                Icon(
                    if (isPlaying) Icons.Filled.Pause else Icons.Filled.PlayArrow,
                    contentDescription = if (isPlaying) "Pause" else "Play",
                    tint = Color.White.copy(alpha = 0.9f),
                    modifier = Modifier.size(64.dp),
                )
            }
        }

        // Draggable scrubber inside the bottom of the video frame.
        val density = LocalDensity.current
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .align(Alignment.BottomCenter)
                .padding(horizontal = 10.dp, vertical = 8.dp)
                .height(16.dp)
                .pointerInput(filePath, durationMs) {
                    awaitEachGesture {
                        val down = awaitFirstDown(requireUnconsumed = false)
                        isScrubbing = true
                        flashControls()
                        val widthPx = size.width.toFloat().coerceAtLeast(1f)
                        fun applyAt(x: Float) {
                            val frac = (x / widthPx).coerceIn(0f, 1f)
                            progress = frac
                            val targetMs = (frac * durationMs).toInt().coerceAtLeast(0)
                            videoViewHolder.value?.seekTo(targetMs)
                        }
                        applyAt(down.position.x)
                        while (true) {
                            val ev = awaitPointerEvent()
                            val change = ev.changes.firstOrNull { it.id == down.id } ?: break
                            if (!change.pressed) break
                            applyAt(change.position.x)
                            change.consume()
                        }
                        isScrubbing = false
                        flashControls()
                    }
                },
            contentAlignment = Alignment.CenterStart,
        ) {
            // Track background.
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(3.dp)
                    .background(Color.White.copy(alpha = 0.25f)),
            )
            // Filled portion.
            Box(
                modifier = Modifier
                    .fillMaxWidth(progress.coerceIn(0f, 1f))
                    .height(3.dp)
                    .background(Color.White),
            )
            // Thumb — positioned using BoxWithConstraints so we have a
            // known track width, then offset by fraction × width.
            androidx.compose.foundation.layout.BoxWithConstraints(
                modifier = Modifier.fillMaxWidth().height(12.dp),
            ) {
                val trackW = maxWidth
                val f = progress.coerceIn(0f, 1f)
                Box(
                    modifier = Modifier
                        .size(12.dp)
                        .offset(x = trackW * f - 6.dp)
                        .background(Color.White, androidx.compose.foundation.shape.CircleShape),
                )
            }
        }
    }
}

@Composable
private fun ZoomChips(
    currentRatio: Float,
    minZoom: Float,
    maxZoom: Float,
    onSetRatio: (Float) -> Unit,
    onDialActiveChange: (Boolean) -> Unit,
    modifier: Modifier = Modifier,
) {
    // Dynamic 3-chip row. The selected chip reflects the live zoom and
    // carries the "x" suffix; the other two are fixed anchors.
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
    // Capture the chip's current value + "isSelected" in refs so the
    // pointerInput doesn't need them as keys — keeping the gesture alive
    // across recompositions when the chip's displayed value changes
    // mid-drag (e.g. middle chip flipping 1.0 → 1.3 → 1.6).
    val latestValue = rememberUpdatedState(value)
    val latestIsSelected = rememberUpdatedState(isSelected)
    // ~80 dp of drag = 1× zoom change. Continuous (no step quantization).
    val dpPerZoom = with(LocalDensity.current) { 80.dp.toPx() }

    Box(
        modifier = Modifier
            .widthIn(min = 48.dp)
            .height(42.dp)
            .background(
                if (isSelected) Color.White else Color.White.copy(alpha = 0.2f),
                RoundedCornerShape(21.dp),
            )
            // Stable key — the pointerInput is never re-created, so a
            // gesture in flight survives every recomposition that comes
            // from zoom ratio updates.
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
                            // Drag RIGHT → smaller zoom (toward 0.5×),
                            // drag LEFT → bigger zoom (toward 2×). Note
                            // the minus sign compared to the drag delta.
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

/**
 * Horizontal ruler shown just above the chip row while the user presses
 * and holds a chip. The ruler slides under a fixed centre pointer —
 * drag right = zoom in. Ticks every 0.1×, major labels at 0.5×, 1×, 2×,
 * 4×, 10×. On release the ruler fades and the chip row shows three
 * values reflecting the new zoom.
 */
@Composable
private fun ZoomDial(
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
    val valueStyle = androidx.compose.ui.text.TextStyle(
        color = Color.White,
        fontWeight = FontWeight.Bold,
        fontSize = 20.sp,
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

        // Centre pointer — small downward triangle above the ticks.
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
    // Silence the unused-style compiler hint (kept for future value label).
    @Suppress("UNUSED_EXPRESSION") valueStyle
}

@Composable
private fun BottomControlRow(
    captureMode: CaptureMediaType,
    isRecording: Boolean,
    selectedArea: StagingArea?,
    recentCapturePath: String?,
    onShutter: () -> Unit,
    onOpenArea: () -> Unit,
    onOpenGallery: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Row(
        modifier = modifier,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        // Left: circular recent-capture thumbnail. Tap opens gallery.
        Box(modifier = Modifier.weight(1f), contentAlignment = Alignment.CenterStart) {
            if (recentCapturePath != null) {
                Box(
                    modifier = Modifier
                        .size(44.dp)
                        .clip(CircleShape)
                        .background(Color.Black)
                        .border(1.5.dp, Color.White.copy(alpha = 0.9f), CircleShape)
                        .clickable { onOpenGallery() },
                ) {
                    AsyncImage(
                        model = File(recentCapturePath),
                        contentDescription = null,
                        modifier = Modifier.fillMaxSize(),
                        contentScale = androidx.compose.ui.layout.ContentScale.Crop,
                    )
                }
            }
        }

        ShutterButton(
            captureMode = captureMode,
            isRecording = isRecording,
            onClick = onShutter,
        )

        Box(modifier = Modifier.weight(1f), contentAlignment = Alignment.CenterEnd) {
            AreaChip(selectedArea = selectedArea, onClick = onOpenArea)
        }
    }
}

@Composable
private fun ShutterButton(
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
                    // Red rounded square inside the white ring.
                    Box(
                        modifier = Modifier
                            .size(28.dp)
                            .background(Color.Red, RoundedCornerShape(6.dp)),
                    )
                } else {
                    // Solid red dot inside the white ring.
                    Box(
                        modifier = Modifier
                            .size(56.dp)
                            .background(Color.Red, CircleShape),
                    )
                }
            }
            else -> {
                // White puck inside the white ring for photo mode — a small
                // dark gap reads visually as a separate "shutter" surface.
                Box(
                    modifier = Modifier
                        .size(60.dp)
                        .background(Color.White, CircleShape),
                )
            }
        }
    }
}

@Composable
private fun AreaChip(selectedArea: StagingArea?, onClick: () -> Unit) {
    Row(
        modifier = Modifier
            .background(Color.White.copy(alpha = 0.18f), RoundedCornerShape(20.dp))
            .pointerInput(Unit) { detectTapGestures(onTap = { onClick() }) }
            .padding(horizontal = 12.dp, vertical = 10.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(
            selectedArea?.name ?: "Area",
            color = Color.White,
            style = MaterialTheme.typography.labelMedium,
        )
    }
}

@Composable
private fun AreaPickerDialog(
    areas: List<StagingArea>,
    selectedId: String?,
    token: String,
    onSelect: (StagingArea) -> Unit,
    onCreateArea: (String) -> Unit,
    onDismiss: () -> Unit,
) {
    // Three-step state machine:
    //   ROOT — existing areas + "+ New Area" button
    //   CATALOG — predefined list from the backend, plus "Other" at the end
    //   CUSTOM — free-form text input (reached by tapping "Other")
    var step by remember { mutableStateOf(PickerStep.ROOT) }
    var catalog by remember { mutableStateOf<List<AreaCatalogEntry>>(emptyList()) }
    var loadingCatalog by remember { mutableStateOf(false) }
    var customName by remember { mutableStateOf("") }
    val scope = rememberCoroutineScope()

    Dialog(onDismissRequest = onDismiss) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(MaterialTheme.colorScheme.surface, RoundedCornerShape(16.dp))
                .padding(16.dp),
        ) {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                // Header — tappable "back" when we're not at root.
                Row(verticalAlignment = Alignment.CenterVertically) {
                    if (step != PickerStep.ROOT) {
                        TextButton(onClick = { step = PickerStep.ROOT; customName = "" }) {
                            Text("Back")
                        }
                    }
                    Text(
                        when (step) {
                            PickerStep.ROOT -> "Choose area"
                            PickerStep.CATALOG -> "Pick a name"
                            PickerStep.CUSTOM -> "Custom name"
                        },
                        style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
                        modifier = Modifier.weight(1f),
                    )
                    IconButton(onClick = onDismiss) {
                        Icon(Icons.Filled.Close, contentDescription = "Close")
                    }
                }

                when (step) {
                    PickerStep.ROOT -> RootStep(
                        areas = areas,
                        selectedId = selectedId,
                        onSelect = onSelect,
                        onNewArea = {
                            step = PickerStep.CATALOG
                            if (catalog.isEmpty() && !loadingCatalog) {
                                loadingCatalog = true
                                scope.launch {
                                    catalog = runCatching { ApiClient.areaCatalog(token).catalog }
                                        .getOrDefault(emptyList())
                                    loadingCatalog = false
                                }
                            }
                        },
                    )

                    PickerStep.CATALOG -> CatalogStep(
                        catalog = catalog,
                        loading = loadingCatalog,
                        onPick = { name -> onCreateArea(name) },
                    )

                    PickerStep.CUSTOM -> CustomNameStep(
                        value = customName,
                        onValueChange = { customName = it },
                        onSubmit = {
                            val name = customName.trim()
                            if (name.isNotEmpty()) onCreateArea(name)
                        },
                    )
                }
            }
        }
    }
}

private enum class PickerStep { ROOT, CATALOG, CUSTOM }

@Composable
private fun RootStep(
    areas: List<StagingArea>,
    selectedId: String?,
    onSelect: (StagingArea) -> Unit,
    onNewArea: () -> Unit,
) {
    // "+ New Area" removed — this m4 instance is read-only for Zoho-
    // sourced Area_Report data.
    @Suppress("UNUSED_PARAMETER") val _unused = onNewArea

    if (areas.isEmpty()) {
        Text(
            "No areas synced yet.",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    } else {
        LazyColumn(
            modifier = Modifier.size(320.dp, 300.dp),
            verticalArrangement = Arrangement.spacedBy(2.dp),
        ) {
            items(areas, key = { it.id }) { area ->
                val sel = area.id == selectedId
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(
                            if (sel) MaterialTheme.colorScheme.primary.copy(alpha = 0.12f)
                            else Color.Transparent,
                            RoundedCornerShape(8.dp),
                        )
                        .clickable { onSelect(area) }
                        .padding(horizontal = 12.dp, vertical = 12.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text(area.name, modifier = Modifier.weight(1f))
                    if (sel) {
                        Icon(
                            Icons.Filled.Check,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.primary,
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun CatalogStep(
    catalog: List<AreaCatalogEntry>,
    loading: Boolean,
    onPick: (String) -> Unit,
) {
    if (loading && catalog.isEmpty()) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(16.dp),
            horizontalArrangement = Arrangement.Center,
        ) {
            CircularProgressIndicator(
                modifier = Modifier.size(20.dp), strokeWidth = 2.dp,
            )
        }
        return
    }
    // "New Area" behaves specially: tapping the entry reveals an inline
    // text field so the stager can type a custom name without leaving the
    // catalog. Leaving the field blank falls back to an auto-numbered
    // "New Area" / "New Area 2" / "New Area 3" (handled by the caller).
    var newAreaEditing by remember { mutableStateOf(false) }
    var newAreaText by remember { mutableStateOf("") }

    LazyColumn(
        modifier = Modifier.size(320.dp, 400.dp),
        verticalArrangement = Arrangement.spacedBy(2.dp),
    ) {
        items(catalog, key = { it.name }) { entry ->
            val isNewArea = entry.name.equals("New Area", ignoreCase = true)
            if (isNewArea && newAreaEditing) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 4.dp, vertical = 4.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    OutlinedTextField(
                        value = newAreaText,
                        onValueChange = { newAreaText = it },
                        placeholder = { Text("New Area") },
                        singleLine = true,
                        modifier = Modifier.weight(1f),
                    )
                    TextButton(onClick = {
                        // Empty text → signal auto-name by sending the
                        // literal "New Area"; the caller picks the next
                        // available suffix when there's a collision.
                        val name = newAreaText.trim().ifEmpty { "New Area" }
                        onPick(name)
                        newAreaEditing = false
                        newAreaText = ""
                    }) {
                        Text("Add")
                    }
                }
            } else {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(
                            if (isNewArea)
                                MaterialTheme.colorScheme.primary.copy(alpha = 0.08f)
                            else Color.Transparent,
                            RoundedCornerShape(8.dp),
                        )
                        .clickable {
                            if (isNewArea) newAreaEditing = true
                            else onPick(entry.name)
                        }
                        .padding(horizontal = 12.dp, vertical = 12.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    if (isNewArea) {
                        Icon(
                            Icons.Filled.Add,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.primary,
                            modifier = Modifier.size(18.dp),
                        )
                        Text(
                            "  ${entry.name}",
                            color = MaterialTheme.colorScheme.primary,
                            fontWeight = FontWeight.SemiBold,
                            modifier = Modifier.weight(1f),
                        )
                    } else {
                        Text(entry.name, modifier = Modifier.weight(1f))
                    }
                }
            }
        }
    }
}

@Composable
private fun CustomNameStep(
    value: String,
    onValueChange: (String) -> Unit,
    onSubmit: () -> Unit,
) {
    OutlinedTextField(
        value = value,
        onValueChange = onValueChange,
        label = { Text("Area name") },
        singleLine = true,
        modifier = Modifier.fillMaxWidth(),
    )
    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        TextButton(
            onClick = onSubmit,
            enabled = value.trim().isNotEmpty(),
            modifier = Modifier.fillMaxWidth(),
        ) { Text("Add") }
    }
}

@Composable
private fun PermissionWall(onCancel: () -> Unit) {
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

// ---- Capture helpers --------------------------------------------------------

private fun takePhoto(
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
private fun startRecording(
    context: android.content.Context,
    videoCapture: VideoCapture<Recorder>,
    executor: Executor,
    onFinished: (File?, String?, Throwable?) -> Unit,
): Recording {
    val name = "staging-video-${System.currentTimeMillis()}"
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
                val copy = copyUriToCache(context, uri)
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

private fun copyUriToCache(
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
