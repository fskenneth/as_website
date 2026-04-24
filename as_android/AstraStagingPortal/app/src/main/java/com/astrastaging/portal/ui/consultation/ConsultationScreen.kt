package com.astrastaging.portal.ui.consultation

import android.app.Application
import android.content.Intent
import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CloudOff
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Stop
import androidx.compose.material.icons.outlined.Add
import androidx.compose.material.icons.outlined.Delete
import androidx.compose.material.icons.outlined.Apartment
import androidx.compose.material.icons.outlined.AttachMoney
import androidx.compose.material.icons.outlined.AutoAwesome
import androidx.compose.material.icons.outlined.Description
import androidx.compose.material.icons.outlined.CalendarMonth
import androidx.compose.material.icons.outlined.CameraAlt
import androidx.compose.material.icons.outlined.CheckCircle
import androidx.compose.material.icons.outlined.Email
import androidx.compose.material.icons.outlined.Flag
import androidx.compose.material.icons.outlined.Folder
import androidx.compose.material.icons.outlined.Home
import androidx.compose.material.icons.outlined.KeyboardArrowDown
import androidx.compose.material.icons.outlined.LocationOn
import androidx.compose.material.icons.outlined.Numbers
import androidx.compose.material.icons.outlined.Panorama
import androidx.compose.material.icons.outlined.Person
import androidx.compose.material.icons.outlined.Phone
import androidx.compose.material.icons.outlined.PlayCircle
import androidx.compose.material.icons.outlined.Refresh
import androidx.compose.material.icons.outlined.Search
import androidx.compose.material.icons.outlined.Star
import androidx.compose.material.icons.outlined.Videocam
import androidx.compose.material.icons.outlined.Warning
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
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
import com.astrastaging.portal.data.ApiClient
import com.astrastaging.portal.data.DictationRecord
import kotlinx.coroutines.launch
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.PopupProperties
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import coil.compose.AsyncImage
import com.astrastaging.portal.data.Staging
import com.astrastaging.portal.data.StagingArea
import com.astrastaging.portal.data.media.CaptureEntity
import com.astrastaging.portal.data.media.CaptureMediaType
import com.astrastaging.portal.data.media.CaptureStatus
import java.io.File
import java.text.NumberFormat
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import java.util.Locale

@Composable
fun ConsultationScreen(token: String, modifier: Modifier = Modifier) {
    val context = LocalContext.current
    val vm: ConsultationViewModel = viewModel(
        key = "consultation-$token",
        factory = ConsultationViewModel.Factory(
            context.applicationContext as Application,
            token,
        ),
    )
    val state by vm.state.collectAsStateWithLifecycle()
    val network by vm.network.collectAsStateWithLifecycle()
    val wifiOnly by vm.wifiOnly.collectAsStateWithLifecycle()

    var captureTarget by remember { mutableStateOf<CaptureTarget?>(null) }
    var pendingCapture by remember { mutableStateOf<PendingCapture?>(null) }
    var viewerCapture by remember { mutableStateOf<CaptureEntity?>(null) }
    var addAreaForStagingId by remember { mutableStateOf<String?>(null) }
    // Inline expand state for a dictation row: which (id, panel) is
    // currently showing transcript/summary contents.
    var expandedDictation by remember { mutableStateOf<Pair<String, String>?>(null) }
    // Pending delete confirmations.
    var dictationPendingDelete by remember { mutableStateOf<DictationRecord?>(null) }
    var areaPendingDelete by remember { mutableStateOf<Pair<String, StagingArea>?>(null) }
    // Item picker overlay: Triple(area, "add"|"remove", areaNameDisplay).
    var itemPickerFor by remember {
        mutableStateOf<Triple<StagingArea, String, String>?>(null)
    }

    // Dictation controller — app-wide singleton so recording survives
    // tab switches. The current tab observes its state to drive the mic
    // icon and auto-present the review dialog on upload completion.
    val dictationController = remember(context) { DictationController.get(context) }
    val dictationState by dictationController.state.collectAsStateWithLifecycle()
    val audioPlayer = remember(context) { DictationAudioPlayer.get(context) }
    val playerState by audioPlayer.state.collectAsStateWithLifecycle()
    // Server-side dictations keyed by staging id. Fetched on staging
    // change and after a new dictation finishes uploading.
    var dictationsByStaging by remember {
        mutableStateOf<Map<String, List<com.astrastaging.portal.data.DictationRecord>>>(emptyMap())
    }
    val coroutineScope = rememberCoroutineScope()
    var micSnack by remember { mutableStateOf<String?>(null) }
    val micPermissionLauncher = rememberLauncherForActivityResult(
        androidx.activity.result.contract.ActivityResultContracts.RequestPermission(),
    ) { granted ->
        if (!granted) {
            micSnack = "Microphone permission denied. Enable it in Settings to dictate."
        } else {
            val s = state.selected
            if (s != null) dictationController.start(s, area = null)
        }
    }

    LaunchedEffect(token) {
        dictationController.tokenProvider = { token }
        dictationController.drainIfPossible()
    }
    LaunchedEffect(network.isOnline) {
        if (network.isOnline) dictationController.drainIfPossible()
    }

    // Fetch server-side dictations for the selected staging. Refires
    // only when the staging changes or the network comes back — a new
    // dictation upload does NOT trigger a refetch (we append optimistically
    // below instead).
    val selectedStagingId = state.selected?.id
    LaunchedEffect(selectedStagingId, network.isOnline) {
        val sid = selectedStagingId ?: return@LaunchedEffect
        if (!network.isOnline) return@LaunchedEffect
        runCatching { ApiClient.listDictations(sid, token) }
            .getOrNull()
            ?.let { resp ->
                dictationsByStaging = dictationsByStaging + (sid to resp.dictations)
            }
    }

    // Optimistic append + safety-net refetch: when a new record arrives,
    // prepend it AND refetch from the server so any server-side changes
    // (email history, status corrections) are also reflected.
    LaunchedEffect(dictationState.pendingReview?.id) {
        val rec = dictationState.pendingReview ?: return@LaunchedEffect
        val sid = rec.staging_id
        val current = dictationsByStaging[sid].orEmpty()
        if (current.none { it.id == rec.id }) {
            dictationsByStaging = dictationsByStaging +
                (sid to (listOf(rec) + current))
        }
        runCatching { ApiClient.listDictations(sid, token) }
            .getOrNull()
            ?.let { resp -> dictationsByStaging = dictationsByStaging + (sid to resp.dictations) }
    }

    // Extra safety: whenever the controller goes idle (upload finished —
    // even if pendingReview didn't propagate for this composable),
    // refetch the current staging's list.
    LaunchedEffect(dictationState.phase) {
        if (dictationState.phase is DictationController.Phase.Idle) {
            val sid = selectedStagingId ?: return@LaunchedEffect
            runCatching { ApiClient.listDictations(sid, token) }
                .getOrNull()
                ?.let { resp -> dictationsByStaging = dictationsByStaging + (sid to resp.dictations) }
        }
    }

    fun confirmDeleteDictation(rec: com.astrastaging.portal.data.DictationRecord) {
        if (audioPlayer.isPlaying(rec.id)) audioPlayer.stop()
        coroutineScope.launch {
            runCatching {
                ApiClient.deleteDictation(rec.id, token)
                val sid = rec.staging_id
                val cur = dictationsByStaging[sid].orEmpty().filterNot { it.id == rec.id }
                dictationsByStaging = dictationsByStaging + (sid to cur)
            }
        }
    }
    fun confirmDeleteArea(area: com.astrastaging.portal.data.StagingArea, stagingId: String) {
        coroutineScope.launch {
            runCatching {
                ApiClient.deleteArea(stagingId, area.id, token)
                vm.loadAreas(stagingId, forceNetwork = true)
            }
        }
    }

    fun toggleAreaDictation(
        staging: com.astrastaging.portal.data.Staging,
        area: com.astrastaging.portal.data.StagingArea?,
    ) {
        val phase = dictationState.phase
        if (phase is DictationController.Phase.Recording) {
            val matches = phase.stagingId == staging.id && phase.areaId == area?.id
            if (matches) {
                dictationController.stopAndEnqueue()
            } else {
                micSnack = "Another dictation is already recording. Stop it first."
            }
            return
        }
        val granted = androidx.core.content.ContextCompat.checkSelfPermission(
            context, android.Manifest.permission.RECORD_AUDIO,
        ) == android.content.pm.PackageManager.PERMISSION_GRANTED
        if (granted) {
            dictationController.start(staging, area)
        } else {
            micPermissionLauncher.launch(android.Manifest.permission.RECORD_AUDIO)
        }
    }

    LaunchedEffect(Unit) { vm.load() }
    LaunchedEffect(network.isOnline) {
        if (network.isOnline) {
            vm.load()
            vm.retryUploads()
        }
    }

    Column(modifier = modifier.fillMaxSize()) {
        Header(
            isRecording = dictationState.phase is DictationController.Phase.Recording,
            isUploading = dictationState.phase is DictationController.Phase.Uploading,
            elapsedMs = dictationState.elapsedMs,
            onMicTap = {
                if (dictationController.isRecording()) {
                    dictationController.stopAndEnqueue()
                    return@Header
                }
                val s = state.selected
                if (s == null) {
                    micSnack = "Select a staging first."
                    return@Header
                }
                val granted = androidx.core.content.ContextCompat.checkSelfPermission(
                    context, android.Manifest.permission.RECORD_AUDIO,
                ) == android.content.pm.PackageManager.PERMISSION_GRANTED
                if (granted) {
                    dictationController.start(s, area = null)
                } else {
                    micPermissionLauncher.launch(android.Manifest.permission.RECORD_AUDIO)
                }
            },
        )
        when {
            state.isLoading && state.stagings.isEmpty() -> LoadingState()
            state.error != null && state.stagings.isEmpty() -> ErrorState(state.error!!, onRetry = vm::load)
            else -> LazyColumn(
                modifier = Modifier.fillMaxSize(),
                contentPadding = PaddingValues(horizontal = 16.dp, vertical = 12.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp),
            ) {
                if (!network.isOnline) {
                    item { OfflineBanner() }
                }
                item {
                    StagingCard(
                        state = state,
                        onSelect = vm::select,
                        onSearchChange = vm::setSearch,
                    )
                }
                state.selected?.let { s ->
                    item {
                        PhotosByAreaSection(
                            vm = vm,
                            staging = s,
                            areas = state.areasByStaging[s.id].orEmpty(),
                            dictations = dictationsByStaging[s.id].orEmpty(),
                            loadingAreas = state.loadingAreasFor == s.id,
                            areasError = state.areasError,
                            network = network,
                            wifiOnly = wifiOnly,
                            playerState = playerState,
                            dictationState = dictationState,
                            quote = state.quoteByStaging[s.id],
                            onCapture = { area, type ->
                                captureTarget = CaptureTarget(s.id, area, type)
                            },
                            onAddArea = { addAreaForStagingId = s.id },
                            onOpenViewer = { viewerCapture = it },
                            onToggleDictation = { area -> toggleAreaDictation(s, area) },
                            onPlayDictation = { rec ->
                                audioPlayer.toggle(rec.id, token)
                            },
                            onDeleteDictation = { rec -> dictationPendingDelete = rec },
                            onDeleteArea = { area -> areaPendingDelete = s.id to area },
                            onOpenItemPicker = { area, action ->
                                itemPickerFor = Triple(area, action, area.name)
                            },
                            onDeleteLineItem = { area, lineId ->
                                vm.deleteLineItem(s.id, area.id, lineId)
                            },
                            expandedDictation = expandedDictation,
                            onExpandDictation = { id, panel ->
                                expandedDictation = if (expandedDictation?.first == id &&
                                    expandedDictation?.second == panel) null
                                else (id to panel)
                            },
                        )
                    }
                    item { NotesCard(s) }
                }
            }
        }
    }

    // Camera overlay — presented as a Dialog so it covers the app dock.
    // Uses a single unified view: user can toggle photo/video, pick the
    // area (including creating a new one) all without leaving the camera.
    captureTarget?.let { target ->
        val s = state.selected
        val areasForStaging = if (s != null) state.areasByStaging[s.id].orEmpty() else emptyList()
        CameraCaptureDialog(
            initialMediaType = target.mediaType,
            staging = s ?: return@let,
            areas = areasForStaging,
            initialAreaId = target.area?.id,
            token = token,
            onCreateArea = { name ->
                // Call the VM and return the created area; the camera
                // updates its local list so the picker reflects it.
                vm.createAreaSuspend(target.stagingId, name)
            },
            onCaptureTaken = { file, mime, type, area ->
                // Enqueue directly — no confirm dialog. Camera stays up
                // so the stager can keep shooting.
                vm.enqueueCapture(
                    stagingId = target.stagingId,
                    area = area,
                    type = type,
                    file = file,
                    mimeType = mime,
                )
            },
            onResult = { _, _, _, _ ->
                captureTarget = null
            },
        )
    }

    // Fullscreen gallery for the tapped thumbnail. Reuses the same
    // composable as the camera's recent-capture tap.
    viewerCapture?.let { capture ->
        val captures by vm.capturesForStaging(capture.stagingId)
            .collectAsStateWithLifecycle(initialValue = emptyList<CaptureEntity>())
        val scoped = captures.filter { it.areaId == capture.areaId }
        InCameraGallery(
            captures = scoped,
            initialCaptureId = capture.id,
            onDismiss = { viewerCapture = null },
            onDelete = { c ->
                vm.deleteCapture(c)
                if (scoped.size <= 1) viewerCapture = null
            },
        )
    }

    addAreaForStagingId?.let { stagingId ->
        AddAreaDialog(
            stagingId = stagingId,
            token = token,
            onCreated = { area ->
                // Optimistically insert the new area into the VM so the user
                // can capture against it immediately; VM will also refresh.
                val current = (state.areasByStaging[stagingId] ?: emptyList()).toMutableList()
                current += area
                // Push through the VM's public reload (simpler than a setter).
                vm.loadAreas(stagingId, forceNetwork = true)
                addAreaForStagingId = null
            },
            onDismiss = { addAreaForStagingId = null },
        )
    }

    dictationState.pendingReview?.let { rec ->
        DictateDialog(
            dictation = rec,
            customerEmailOnFile = state.stagings.firstOrNull { it.id == rec.staging_id }
                ?.customer?.email,
            token = token,
            onDismiss = { dictationController.clearPendingReview() },
        )
    }

    dictationPendingDelete?.let { rec ->
        AlertDialog(
            onDismissRequest = { dictationPendingDelete = null },
            title = { Text("Delete dictation?") },
            text = {
                Text("This removes the audio, transcript, and summary from the server. This can't be undone.")
            },
            confirmButton = {
                TextButton(onClick = {
                    confirmDeleteDictation(rec)
                    dictationPendingDelete = null
                }) { Text("Delete", color = MaterialTheme.colorScheme.error) }
            },
            dismissButton = {
                TextButton(onClick = { dictationPendingDelete = null }) { Text("Cancel") }
            },
        )
    }

    areaPendingDelete?.let { (sid, area) ->
        AlertDialog(
            onDismissRequest = { areaPendingDelete = null },
            title = { Text("Delete area?") },
            text = {
                Text("Photos and dictations in this area will lose their area tag. The area itself is soft-deleted.")
            },
            confirmButton = {
                TextButton(onClick = {
                    confirmDeleteArea(area, sid)
                    areaPendingDelete = null
                }) { Text("Delete", color = MaterialTheme.colorScheme.error) }
            },
            dismissButton = {
                TextButton(onClick = { areaPendingDelete = null }) { Text("Cancel") }
            },
        )
    }

    // Item picker — add OR remove; single modal serves both.
    itemPickerFor?.let { (area, action, areaName) ->
        val s = state.selected
        val areaQuote = s?.let { state.quoteByStaging[it.id] }
            ?.areas?.firstOrNull { it.area_id == area.id }
        val title = if (action == "add") "Add New Items" else "Remove Existing Items"
        ItemPickerDialog(
            title = title,
            action = action,
            catalog = state.catalog,
            area = areaQuote,
            areaName = areaName,
            onTapItem = { itemName, delta ->
                s?.let { vm.upsertLineItem(it.id, area.id, action, itemName, delta) }
            },
            onDismiss = { itemPickerFor = null },
        )
    }
}

internal data class CaptureTarget(
    val stagingId: String,
    val area: StagingArea?,
    val mediaType: CaptureMediaType,
)

internal data class PendingCapture(
    val target: CaptureTarget,
    val file: File,
    val mimeType: String,
)

@Composable
private fun Header(
    isRecording: Boolean,
    isUploading: Boolean,
    elapsedMs: Long,
    onMicTap: () -> Unit,
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(MaterialTheme.colorScheme.surface)
            .padding(horizontal = 16.dp, vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(
            "Consultation",
            style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold),
            modifier = Modifier.weight(1f),
        )
        if (isRecording) {
            val sec = elapsedMs / 1000
            Text(
                "%02d:%02d".format(sec / 60, sec % 60),
                color = Color(0xFFD32F2F),
                style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.SemiBold),
            )
            Spacer(Modifier.width(8.dp))
        }
        if (isUploading) {
            CircularProgressIndicator(
                modifier = Modifier.size(18.dp),
                strokeWidth = 2.dp,
            )
            Spacer(Modifier.width(8.dp))
        }
        IconButton(onClick = onMicTap) {
            Icon(
                imageVector = Icons.Filled.Mic,
                contentDescription = if (isRecording) "Stop dictation" else "Start dictation",
                tint = if (isRecording) Color(0xFFD32F2F) else MaterialTheme.colorScheme.onSurface,
            )
        }
    }
}

@Composable
private fun StagingCard(
    state: ConsultationViewModel.State,
    onSelect: (String) -> Unit,
    onSearchChange: (String) -> Unit,
) {
    var expanded by remember { mutableStateOf(false) }
    val sel = state.selected
    Column(
        Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.45f))
            .padding(14.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Text(
            "STAGING",
            style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.SemiBold),
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )

        // Address row doubles as the staging picker trigger.
        AddressPickerRow(
            state = state,
            expanded = expanded,
            onExpand = { expanded = true; onSearchChange("") },
            onCollapse = { expanded = false },
            onSelect = { id ->
                onSelect(id)
                expanded = false
            },
            onSearchChange = onSearchChange,
        )

        if (sel != null) {
            BriefRow(Icons.Outlined.Home, "Occupancy", sel.occupancy ?: "—")
            BriefRow(Icons.Outlined.Apartment, "Property", sel.property_type ?: "—")
            if (!sel.staging_type.isNullOrEmpty()) BriefRow(Icons.Outlined.Star, "Staging type", sel.staging_type!!)
            if (!sel.status.isNullOrEmpty()) BriefRow(Icons.Outlined.Flag, "Status", sel.status!!)
            BriefRow(
                Icons.Outlined.CalendarMonth,
                "Staging date",
                sel.staging_date?.takeIf { it.isNotEmpty() }?.let { prettyDate(it) } ?: "Not scheduled",
            )
            BriefRow(Icons.Outlined.Person, "Customer", sel.customer.fullName)

            val context = LocalContext.current
            sel.customer.phone?.takeIf { it.isNotEmpty() }?.let { phone ->
                BriefRow(Icons.Outlined.Phone, "Phone", phone, clickable = true) {
                    val intent = Intent(Intent.ACTION_DIAL, Uri.parse("tel:" + phone.replace(" ", "")))
                    context.startActivity(intent)
                }
            }
            sel.customer.email?.takeIf { it.isNotEmpty() }?.let { email ->
                BriefRow(Icons.Outlined.Email, "Email", email, clickable = true) {
                    val intent = Intent(Intent.ACTION_SENDTO, Uri.parse("mailto:$email"))
                    context.startActivity(intent)
                }
            }

            BriefRow(Icons.Outlined.AttachMoney, "Quote", money(sel.fees.total))
            if (sel.fees.paid > 0) BriefRow(Icons.Outlined.CheckCircle, "Paid", money(sel.fees.paid))
            if (sel.fees.owing > 0) BriefRow(Icons.Outlined.Warning, "Owing", money(sel.fees.owing))

            if (!sel.mls.isNullOrEmpty()) BriefRow(Icons.Outlined.Numbers, "MLS", sel.mls!!)
            sel.pictures_folder?.takeIf { it.isNotEmpty() }?.let { folder ->
                val context2 = LocalContext.current
                BriefRow(Icons.Outlined.Folder, "Pictures folder", "Open", clickable = true) {
                    runCatching {
                        context2.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(folder)))
                    }
                }
            }
        }
    }
}

@Composable
private fun AddressPickerRow(
    state: ConsultationViewModel.State,
    expanded: Boolean,
    onExpand: () -> Unit,
    onCollapse: () -> Unit,
    onSelect: (String) -> Unit,
    onSearchChange: (String) -> Unit,
) {
    val sel = state.selected
    Box(Modifier.fillMaxWidth()) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .clickable { onExpand() }
                .padding(vertical = 4.dp)
                .semantics { contentDescription = "consultation-staging-picker" },
            verticalAlignment = Alignment.Top,
        ) {
            Icon(
                Icons.Outlined.LocationOn,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.size(20.dp).padding(top = 2.dp),
            )
            Spacer(Modifier.width(10.dp))
            Text(
                "Address",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.width(110.dp),
            )
            Column(Modifier.weight(1f)) {
                Text(
                    sel?.address ?: sel?.name ?: "Select a staging",
                    style = MaterialTheme.typography.bodyMedium,
                    color = if (sel == null) MaterialTheme.colorScheme.onSurfaceVariant
                            else MaterialTheme.colorScheme.onSurface,
                )
                if (sel != null) {
                    Text(
                        stagingSubtitle(sel),
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            }
            Icon(
                Icons.Outlined.KeyboardArrowDown,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(start = 4.dp),
            )
        }

        DropdownMenu(
            expanded = expanded,
            onDismissRequest = onCollapse,
            modifier = Modifier
                .fillMaxWidth(0.95f)
                .background(MaterialTheme.colorScheme.surface),
            properties = PopupProperties(focusable = true),
        ) {
            // Search at the top of the dropdown.
            Box(Modifier.padding(horizontal = 12.dp, vertical = 8.dp)) {
                OutlinedTextField(
                    value = state.search,
                    onValueChange = onSearchChange,
                    placeholder = { Text("Filter by address or customer") },
                    leadingIcon = { Icon(Icons.Outlined.Search, contentDescription = null) },
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth(),
                )
            }
            Text(
                "${state.stagings.size} available · no staging date or in the future",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(horizontal = 16.dp, vertical = 4.dp),
            )
            HorizontalDivider()
            val list = state.filtered
            if (list.isEmpty()) {
                DropdownMenuItem(
                    text = { Text("No matches") },
                    onClick = onCollapse,
                    enabled = false,
                )
            } else {
                list.forEach { s ->
                    DropdownMenuItem(
                        text = {
                            Column {
                                Text(
                                    s.name ?: s.address ?: s.id,
                                    style = MaterialTheme.typography.bodyMedium,
                                )
                                Text(
                                    stagingSubtitle(s),
                                    style = MaterialTheme.typography.bodySmall,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                                )
                            }
                        },
                        onClick = { onSelect(s.id) },
                    )
                }
            }
        }
    }
}

private fun stagingSubtitle(s: Staging): String {
    val parts = mutableListOf<String>()
    if (!s.staging_date.isNullOrEmpty()) parts += prettyDate(s.staging_date!!) else parts += "No date"
    if (!s.status.isNullOrEmpty()) parts += s.status!!
    return parts.joinToString(" · ")
}

@Composable
private fun BriefRow(
    icon: ImageVector,
    label: String,
    value: String,
    clickable: Boolean = false,
    onClick: (() -> Unit)? = null,
) {
    val baseMod = Modifier.fillMaxWidth()
    val mod = if (clickable && onClick != null) baseMod.clickable { onClick() } else baseMod
    Row(
        modifier = mod.padding(vertical = 4.dp),
        verticalAlignment = Alignment.Top,
    ) {
        Icon(
            icon,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.size(20.dp).padding(top = 2.dp),
        )
        Spacer(Modifier.width(10.dp))
        Text(
            label,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.width(110.dp),
        )
        Text(
            value,
            style = MaterialTheme.typography.bodyMedium,
            color = if (clickable) MaterialTheme.colorScheme.primary
                    else MaterialTheme.colorScheme.onSurface,
            modifier = Modifier.weight(1f),
        )
    }
}

@Composable
private fun OfflineBanner() {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(10.dp))
            .background(Color(0xFFFFF5E1))
            .padding(12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(
            Icons.Filled.CloudOff,
            contentDescription = null,
            tint = Color(0xFFB66A00),
            modifier = Modifier.size(18.dp),
        )
        Spacer(Modifier.width(10.dp))
        Column {
            Text(
                "Offline — showing cached data",
                style = MaterialTheme.typography.bodySmall.copy(fontWeight = FontWeight.SemiBold),
            )
            Text(
                "New captures stay on-device until you reconnect.",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

@Composable
private fun PhotosByAreaSection(
    vm: ConsultationViewModel,
    staging: Staging,
    areas: List<StagingArea>,
    dictations: List<com.astrastaging.portal.data.DictationRecord>,
    loadingAreas: Boolean,
    areasError: String?,
    network: com.astrastaging.portal.data.network.NetworkSnapshot,
    wifiOnly: Boolean,
    playerState: DictationAudioPlayer.State,
    dictationState: DictationController.State,
    quote: com.astrastaging.portal.data.StagingQuote?,
    onCapture: (StagingArea?, CaptureMediaType) -> Unit,
    onAddArea: () -> Unit,
    onOpenViewer: (CaptureEntity) -> Unit,
    onToggleDictation: (StagingArea?) -> Unit,
    onPlayDictation: (com.astrastaging.portal.data.DictationRecord) -> Unit,
    onDeleteDictation: (com.astrastaging.portal.data.DictationRecord) -> Unit,
    onDeleteArea: (StagingArea) -> Unit,
    onOpenItemPicker: (StagingArea, String) -> Unit,
    onDeleteLineItem: (StagingArea, String) -> Unit,
    expandedDictation: Pair<String, String>?,
    onExpandDictation: (String, String) -> Unit,
) {
    val captures by vm.capturesForStaging(staging.id).collectAsStateWithLifecycle(initialValue = emptyList())
    val byArea: Map<String?, List<CaptureEntity>> = captures.groupBy { it.areaId }
    val queueBlocked = !com.astrastaging.portal.data.network.NetworkMonitor.canUploadMedia(wifiOnly)

    Column(
        Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.45f))
            .padding(14.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(
                "PHOTOS & VIDEO BY AREA",
                style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.SemiBold),
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.weight(1f),
            )
            if (queueBlocked) {
                Icon(
                    Icons.Filled.CloudOff,
                    contentDescription = null,
                    tint = Color(0xFFB66A00),
                    modifier = Modifier.size(14.dp),
                )
                Spacer(Modifier.width(4.dp))
                Text(
                    if (wifiOnly) "Queued · waiting Wi-Fi" else "Queued · offline",
                    style = MaterialTheme.typography.labelSmall,
                    color = Color(0xFFB66A00),
                )
            }
        }

        when {
            loadingAreas && areas.isEmpty() -> {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    CircularProgressIndicator(modifier = Modifier.size(16.dp), strokeWidth = 2.dp)
                    Spacer(Modifier.width(8.dp))
                    Text("Loading areas…", style = MaterialTheme.typography.bodySmall)
                }
            }
            areas.isEmpty() -> {
                Text(
                    "No areas for this staging yet.",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                if (areasError != null) {
                    Text(
                        areasError,
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.error,
                    )
                }
                // Areas come from Zoho; creating one here would drift
                // the m4 test DB from live Zoho. Refresh-only.
                androidx.compose.material3.OutlinedButton(
                    onClick = { vm.loadAreas(staging.id, forceNetwork = true) },
                    enabled = network.isOnline,
                ) {
                    Icon(Icons.Outlined.Refresh, contentDescription = null, modifier = Modifier.size(16.dp))
                    Spacer(Modifier.width(4.dp))
                    Text("Refresh")
                }
            }
            else -> {
                areas.forEach { area ->
                    val areaQuote = quote?.areas?.firstOrNull { it.area_id == area.id }
                    AreaCaptureRow(
                        area = area,
                        stagingId = staging.id,
                        captures = byArea[area.id].orEmpty(),
                        dictations = dictations.filter { it.area_id == area.id },
                        playerState = playerState,
                        dictationState = dictationState,
                        areaQuote = areaQuote,
                        onCapture = onCapture,
                        onOpenViewer = onOpenViewer,
                        onToggleDictation = onToggleDictation,
                        onPlayDictation = onPlayDictation,
                        onDeleteDictation = onDeleteDictation,
                        onDeleteArea = onDeleteArea,
                        onOpenItemPicker = { action -> onOpenItemPicker(area, action) },
                        onDeleteLineItem = { lineId -> onDeleteLineItem(area, lineId) },
                        expandedDictation = expandedDictation,
                        onExpandDictation = onExpandDictation,
                    )
                }
                // "Add another area" removed — area list read-only.
            }
        }

        // Standalone list of global (title-bar mic) recordings —
        // rendered flat under the area grid, not as a fake "Unassigned"
        // area row. Hides entirely when there are none.
        val globalRecordings = dictations.filter { it.area_id == null }
        if (globalRecordings.isNotEmpty()) {
            Text(
                "RECORDINGS",
                style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.SemiBold),
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                globalRecordings.forEach { rec ->
                    DictationRow(
                        record = rec,
                        playing = playerState.currentlyPlayingId == rec.id,
                        loading = playerState.loadingId == rec.id,
                        progress = if (playerState.currentlyPlayingId == rec.id)
                            playerState.progress else 0f,
                        expandedPanel = null,
                        onPlay = { onPlayDictation(rec) },
                        onDelete = { onDeleteDictation(rec) },
                        onExpand = { _ -> },
                    )
                }
            }
        }

        Text(
            "Photos are downscaled and videos recorded at 720p to keep data use low.",
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

@Composable
private fun AreaCaptureRow(
    area: StagingArea?,
    stagingId: String,
    captures: List<CaptureEntity>,
    dictations: List<com.astrastaging.portal.data.DictationRecord>,
    playerState: DictationAudioPlayer.State,
    dictationState: DictationController.State,
    areaQuote: com.astrastaging.portal.data.QuoteArea? = null,
    onCapture: (StagingArea?, CaptureMediaType) -> Unit,
    onOpenViewer: (CaptureEntity) -> Unit,
    onToggleDictation: (StagingArea?) -> Unit,
    onPlayDictation: (com.astrastaging.portal.data.DictationRecord) -> Unit,
    onDeleteDictation: (com.astrastaging.portal.data.DictationRecord) -> Unit,
    onDeleteArea: (StagingArea) -> Unit,
    onOpenItemPicker: (String) -> Unit = {},
    onDeleteLineItem: (String) -> Unit = {},
    expandedDictation: Pair<String, String>?,
    onExpandDictation: (String, String) -> Unit,
) {
    val phase = dictationState.phase
    val recordingThis = phase is DictationController.Phase.Recording &&
        phase.stagingId == stagingId && phase.areaId == area?.id
    val elapsedLabel = run {
        val sec = dictationState.elapsedMs / 1000
        "%02d:%02d".format(sec / 60, sec % 60)
    }

    Column(
        Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(10.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(12.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Column(Modifier.weight(1f)) {
                Text(
                    area?.name ?: "Unassigned",
                    style = MaterialTheme.typography.bodyMedium.copy(fontWeight = FontWeight.SemiBold),
                )
                area?.floor?.takeIf { it.isNotEmpty() }?.let {
                    Text(it, style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
            }
            // Live area charge (items capped by area cap).
            areaQuote?.let { aq ->
                val capped = aq.items_total > 0 && aq.items_total >= aq.cap
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(8.dp))
                        .background(
                            if (capped) MaterialTheme.colorScheme.tertiaryContainer
                            else MaterialTheme.colorScheme.primaryContainer
                        )
                        .padding(horizontal = 8.dp, vertical = 4.dp),
                ) {
                    Text(
                        "$${"%.0f".format(aq.effective)}",
                        style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.SemiBold),
                        color = if (capped) MaterialTheme.colorScheme.onTertiaryContainer
                                else MaterialTheme.colorScheme.onPrimaryContainer,
                    )
                }
                Spacer(Modifier.width(6.dp))
            }
            // Icon-only header buttons (no captions).
            InlineHeaderButton(
                icon = Icons.Outlined.CameraAlt,
                tint = MaterialTheme.colorScheme.onSurface,
                onClick = { onCapture(area, CaptureMediaType.PHOTO) },
            )
            Spacer(Modifier.width(6.dp))
            InlineHeaderButton(
                icon = Icons.Filled.Mic,
                tint = if (recordingThis) Color(0xFFD32F2F) else MaterialTheme.colorScheme.onSurface,
                accessory = if (recordingThis) elapsedLabel else null,
                onClick = { onToggleDictation(area) },
            )
            // Area delete icon removed — areas are read-only on m4.
        }

        if (captures.isNotEmpty()) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                captures.forEach { c ->
                    CaptureThumb(capture = c, onClick = { onOpenViewer(c) })
                }
            }
        }

        if (dictations.isNotEmpty()) {
            Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                dictations.forEach { rec ->
                    val panel = if (expandedDictation?.first == rec.id) expandedDictation.second else null
                    DictationRow(
                        record = rec,
                        playing = playerState.currentlyPlayingId == rec.id,
                        loading = playerState.loadingId == rec.id,
                        progress = if (playerState.currentlyPlayingId == rec.id)
                            playerState.progress else 0f,
                        expandedPanel = panel,
                        onPlay = { onPlayDictation(rec) },
                        onDelete = { onDeleteDictation(rec) },
                        onExpand = { p -> onExpandDictation(rec.id, p) },
                    )
                }
            }
        }

        // Items buttons — only for real areas (not the fake "Unassigned").
        if (area != null) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                ItemsActionButton(
                    label = "Remove Existing",
                    count = areaQuote?.remove_items?.sumOf { it.quantity } ?: 0,
                    onClick = { onOpenItemPicker("remove") },
                    modifier = Modifier.weight(1f),
                )
                ItemsActionButton(
                    label = "Add New Items",
                    count = areaQuote?.add_items?.sumOf { it.quantity } ?: 0,
                    onClick = { onOpenItemPicker("add") },
                    modifier = Modifier.weight(1f),
                )
            }

            val removeItems = areaQuote?.remove_items.orEmpty()
            if (removeItems.isNotEmpty()) {
                LineItemList(
                    label = "REMOVE",
                    items = removeItems,
                    showPrice = false,
                    onDelete = onDeleteLineItem,
                )
            }
            val addItems = areaQuote?.add_items.orEmpty()
            if (addItems.isNotEmpty()) {
                LineItemList(
                    label = "ADD",
                    items = addItems,
                    showPrice = true,
                    onDelete = onDeleteLineItem,
                )
            }
        }
    }
}

/** Compact button for the two item-picker entry points.
 *  Shows a count badge when items are selected. */
@Composable
private fun ItemsActionButton(
    label: String,
    count: Int,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Row(
        modifier = modifier
            .clip(RoundedCornerShape(8.dp))
            .background(MaterialTheme.colorScheme.surfaceVariant)
            .clickable { onClick() }
            .padding(horizontal = 12.dp, vertical = 10.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(
            label,
            style = MaterialTheme.typography.labelLarge.copy(fontWeight = FontWeight.SemiBold),
            modifier = Modifier.weight(1f),
        )
        if (count > 0) {
            Box(
                modifier = Modifier
                    .clip(CircleShape)
                    .background(MaterialTheme.colorScheme.primary)
                    .padding(horizontal = 7.dp, vertical = 2.dp),
            ) {
                Text(
                    count.toString(),
                    style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold),
                    color = MaterialTheme.colorScheme.onPrimary,
                )
            }
        }
    }
}

@Composable
private fun LineItemList(
    label: String,
    items: List<com.astrastaging.portal.data.QuoteLineItem>,
    showPrice: Boolean,
    onDelete: (String) -> Unit,
) {
    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
        Text(
            label,
            style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.SemiBold),
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        items.forEach { li ->
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(8.dp))
                    .background(MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f))
                    .padding(horizontal = 10.dp, vertical = 6.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    "${li.item_name} × ${li.quantity}",
                    style = MaterialTheme.typography.bodySmall.copy(fontWeight = FontWeight.SemiBold),
                    modifier = Modifier.weight(1f),
                )
                if (showPrice) {
                    Text(
                        "$${"%.0f".format(li.unit_price * li.quantity)}",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                    Spacer(Modifier.width(6.dp))
                }
                IconButton(
                    onClick = { onDelete(li.id) },
                    modifier = Modifier.size(28.dp),
                ) {
                    Icon(
                        Icons.Outlined.Delete,
                        contentDescription = "Remove",
                        tint = MaterialTheme.colorScheme.error,
                        modifier = Modifier.size(16.dp),
                    )
                }
            }
        }
    }
}

/** Icon-only header button. Shows an optional accessory label (e.g. the
 *  elapsed timer) to the right of the icon while recording. */
@Composable
private fun InlineHeaderButton(
    icon: ImageVector,
    tint: Color,
    accessory: String? = null,
    onClick: () -> Unit,
) {
    Row(
        modifier = Modifier
            .clip(RoundedCornerShape(8.dp))
            .background(MaterialTheme.colorScheme.surfaceVariant)
            .clickable { onClick() }
            .padding(horizontal = 10.dp, vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(icon, contentDescription = null, tint = tint, modifier = Modifier.size(18.dp))
        if (accessory != null) {
            Spacer(Modifier.width(4.dp))
            Text(accessory, style = MaterialTheme.typography.labelSmall, color = tint)
        }
    }
}

/** A single dictation row: play/stop + duration + progress bar +
 *  delete (with confirm) + transcript/summary expand icons. */
@Composable
private fun DictationRow(
    record: com.astrastaging.portal.data.DictationRecord,
    playing: Boolean,
    loading: Boolean,
    progress: Float,
    expandedPanel: String?,
    onPlay: () -> Unit,
    onDelete: () -> Unit,
    onExpand: (String) -> Unit,
) {
    val durationLabel = record.duration_sec?.takeIf { it > 0 }?.let {
        val total = it.toInt()
        "%d:%02d".format(total / 60, total % 60)
    } ?: "—"
    val sizeLabel = record.audio_size?.takeIf { it > 0 }?.let { bytes ->
        val kb = bytes / 1024.0
        if (kb < 1024) "%.0f KB".format(kb) else "%.1f MB".format(kb / 1024.0)
    } ?: "—"

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(8.dp))
            .background(MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f))
            .padding(horizontal = 10.dp, vertical = 6.dp),
        verticalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            IconButton(onClick = onPlay, enabled = !loading) {
                if (loading) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(18.dp),
                        strokeWidth = 2.dp,
                    )
                } else {
                    Icon(
                        if (playing) Icons.Filled.Stop else Icons.Filled.PlayArrow,
                        contentDescription = if (playing) "Stop" else "Play",
                        tint = Color(0xFF1E88E5),
                    )
                }
            }
            Column(Modifier.weight(1f)) {
                Text(
                    sizeLabel,
                    style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.SemiBold),
                )
                Text(
                    durationLabel,
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }

            IconButton(onClick = { onExpand("transcript") }) {
                Icon(
                    Icons.Outlined.Description,
                    contentDescription = "Transcript",
                    tint = if (expandedPanel == "transcript") Color(0xFF1E88E5)
                           else MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.size(18.dp),
                )
            }
            IconButton(onClick = { onExpand("summary") }) {
                Icon(
                    Icons.Outlined.AutoAwesome,
                    contentDescription = "Summary",
                    tint = if (expandedPanel == "summary") Color(0xFF1E88E5)
                           else MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.size(18.dp),
                )
            }
            IconButton(onClick = onDelete) {
                Icon(
                    Icons.Outlined.Delete,
                    contentDescription = "Delete",
                    tint = MaterialTheme.colorScheme.error,
                    modifier = Modifier.size(18.dp),
                )
            }
        }
        if (playing) {
            androidx.compose.material3.LinearProgressIndicator(
                progress = { progress.coerceIn(0f, 1f) },
                modifier = Modifier.fillMaxWidth(),
                color = Color(0xFF1E88E5),
            )
        }

        when (expandedPanel) {
            "transcript" -> {
                HorizontalDivider(Modifier.padding(vertical = 2.dp))
                Text(
                    record.transcript.ifBlank { "Transcript not available yet." },
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            "summary" -> {
                HorizontalDivider(Modifier.padding(vertical = 2.dp))
                val s = record.summary
                if (s == null) {
                    Text(
                        "Summary not available yet.",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                } else {
                    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                        if (s.key_points.isNotEmpty()) {
                            Text(
                                "Key points",
                                style = MaterialTheme.typography.labelMedium
                                    .copy(fontWeight = FontWeight.SemiBold),
                            )
                            s.key_points.forEach { p ->
                                Row {
                                    Text("• ", color = MaterialTheme.colorScheme.onSurfaceVariant)
                                    Text(p, style = MaterialTheme.typography.bodySmall)
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun CaptureButton(
    icon: ImageVector,
    label: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier
            .clip(RoundedCornerShape(8.dp))
            .background(MaterialTheme.colorScheme.surfaceVariant)
            .clickable { onClick() }
            .padding(vertical = 10.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        Icon(icon, contentDescription = null, modifier = Modifier.size(18.dp))
        Text(label, style = MaterialTheme.typography.labelSmall)
    }
}

@Composable
private fun CaptureThumb(capture: CaptureEntity, onClick: () -> Unit) {
    // Landscape photos render wider than tall so the user can tell at a
    // glance how the phone was oriented when captured.
    val mediaType = CaptureMediaType.fromWire(capture.mediaType)
    val (wDp, hDp) = remember(capture.filePath) {
        photoDimensions(capture.filePath, isVideo = mediaType == CaptureMediaType.VIDEO)
    }
    Box(
        modifier = Modifier
            .height(hDp)
            .width(wDp)
            .clip(RoundedCornerShape(8.dp))
            .background(MaterialTheme.colorScheme.surface)
            .clickable { onClick() },
    ) {
        if (mediaType == CaptureMediaType.VIDEO) {
            Box(modifier = Modifier.fillMaxSize().background(Color.Black)) {
                // First frame via Coil's VideoFrameDecoder.
                AsyncImage(
                    model = File(capture.filePath),
                    contentDescription = null,
                    modifier = Modifier.fillMaxSize(),
                    contentScale = androidx.compose.ui.layout.ContentScale.Crop,
                )
                Icon(
                    Icons.Outlined.PlayCircle,
                    contentDescription = null,
                    tint = Color.White.copy(alpha = 0.9f),
                    modifier = Modifier.align(Alignment.Center).size(28.dp),
                )
            }
        } else {
            AsyncImage(
                model = File(capture.filePath),
                contentDescription = null,
                modifier = Modifier.fillMaxSize(),
            )
        }
    }
}

/** Returns the thumbnail size (width, height) in dp for a capture: base
 *  72 dp, but landscape photos scale horizontally to preserve aspect. */
private fun photoDimensions(
    path: String,
    isVideo: Boolean,
    base: Int = 72,
): Pair<androidx.compose.ui.unit.Dp, androidx.compose.ui.unit.Dp> {
    val dp = androidx.compose.ui.unit.Dp
    fun d(v: Int) = v.dp
    if (isVideo) return d(base) to d(base)
    return try {
        val opts = android.graphics.BitmapFactory.Options().apply { inJustDecodeBounds = true }
        android.graphics.BitmapFactory.decodeFile(path, opts)
        val w = opts.outWidth
        val h = opts.outHeight
        // Honour EXIF orientation — decoded dimensions are raw pixels.
        val orientation = runCatching {
            androidx.exifinterface.media.ExifInterface(path)
                .getAttributeInt(
                    androidx.exifinterface.media.ExifInterface.TAG_ORIENTATION,
                    androidx.exifinterface.media.ExifInterface.ORIENTATION_NORMAL,
                )
        }.getOrDefault(androidx.exifinterface.media.ExifInterface.ORIENTATION_NORMAL)
        val swap = orientation == androidx.exifinterface.media.ExifInterface.ORIENTATION_ROTATE_90 ||
            orientation == androidx.exifinterface.media.ExifInterface.ORIENTATION_ROTATE_270 ||
            orientation == androidx.exifinterface.media.ExifInterface.ORIENTATION_TRANSPOSE ||
            orientation == androidx.exifinterface.media.ExifInterface.ORIENTATION_TRANSVERSE
        val (effW, effH) = if (swap) h to w else w to h
        if (effW <= 0 || effH <= 0) return d(base) to d(base)
        when {
            effW > effH * 1.05 -> d((base * effW.toDouble() / effH.toDouble()).toInt()) to d(base)
            effH > effW * 1.05 -> d(base) to d((base * effH.toDouble() / effW.toDouble()).toInt())
            else -> d(base) to d(base)
        }
    } catch (_: Throwable) {
        d(base) to d(base)
    }
}

@Composable
private fun NotesCard(s: Staging) {
    Column(
        Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.45f))
            .padding(14.dp),
    ) {
        Text(
            "NOTES",
            style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.SemiBold),
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Spacer(Modifier.height(6.dp))
        val notes = s.general_notes?.takeIf { it.isNotBlank() }
        Text(
            notes ?: "No notes on this staging yet.",
            style = if (notes != null) MaterialTheme.typography.bodyMedium
                    else MaterialTheme.typography.bodySmall,
            color = if (notes != null) MaterialTheme.colorScheme.onSurface
                    else MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

@Composable
private fun LoadingState() {
    Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
        CircularProgressIndicator()
    }
}

@Composable
private fun ErrorState(message: String, onRetry: () -> Unit) {
    Column(
        Modifier
            .fillMaxSize()
            .padding(32.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text("Couldn't load", style = MaterialTheme.typography.titleMedium)
        Spacer(Modifier.height(6.dp))
        Text(
            message,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            textAlign = TextAlign.Center,
        )
        Spacer(Modifier.height(12.dp))
        Button(onClick = onRetry) { Text("Retry") }
    }
}

private fun prettyDate(iso: String): String = try {
    val d = LocalDate.parse(iso)
    d.format(DateTimeFormatter.ofPattern("EEE, MMM d, yyyy", Locale.ENGLISH))
} catch (_: Throwable) {
    iso
}

private fun money(v: Double): String {
    val nf = NumberFormat.getCurrencyInstance(Locale.CANADA)
    nf.maximumFractionDigits = 0
    return nf.format(v)
}
