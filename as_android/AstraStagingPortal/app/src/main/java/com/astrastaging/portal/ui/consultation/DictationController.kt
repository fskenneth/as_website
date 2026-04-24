package com.astrastaging.portal.ui.consultation

import android.content.Context
import android.util.Log
import com.astrastaging.portal.data.ApiClient
import com.astrastaging.portal.data.DictationRecord
import com.astrastaging.portal.data.Staging
import com.astrastaging.portal.data.StagingArea
import com.astrastaging.portal.data.network.NetworkMonitor
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

/**
 * App-wide singleton owning the voice-dictation lifecycle:
 *
 *   idle ──tap mic──▶ recording ──tap mic──▶ (enqueue + drain)
 *
 * The controller holds a single AudioRecorder so recording survives tab
 * switches. When the user stops, the file is moved into DictationStore
 * and an upload loop drains the queue. If offline, the record stays
 * queued until the network comes back. On successful upload, the
 * resulting DictationRecord is published via `pendingReview` so the
 * Consultation view can auto-present the review sheet.
 */
class DictationController(context: Context) {

    sealed class Phase {
        data object Idle : Phase()
        data class Recording(val stagingId: String, val areaId: String?) : Phase()
        data class Uploading(val clientId: String, val stagingId: String) : Phase()
    }

    data class State(
        val phase: Phase = Phase.Idle,
        val elapsedMs: Long = 0,
        val lastError: String? = null,
        /** When an upload completes from a freshly-stopped recording, the
         *  review sheet is presented from this. The view nulls it out. */
        val pendingReview: DictationRecord? = null,
    )

    private val appContext = context.applicationContext
    private val store = DictationStore.get(appContext)
    private val recorder = AudioRecorder(appContext)
    private val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())
    private val drainLock = Mutex()

    private val _state = MutableStateFlow(State())
    val state: StateFlow<State> = _state.asStateFlow()

    // Supplied by the owning view so the controller can fetch the token
    // lazily on upload without having to observe AuthStore directly.
    @Volatile var tokenProvider: () -> String? = { null }

    private var currentStaging: Staging? = null
    private var currentArea: StagingArea? = null
    private var tickJob: Job? = null
    private var recordingStartedAt: Long = 0

    // MARK: - Recording

    fun isRecording(stagingId: String? = null): Boolean {
        val p = _state.value.phase
        return p is Phase.Recording && (stagingId == null || p.stagingId == stagingId)
    }

    fun start(staging: Staging, area: StagingArea?) {
        if (_state.value.phase != Phase.Idle) return
        recorder.start(scope)
        currentStaging = staging
        currentArea = area
        recordingStartedAt = System.currentTimeMillis()
        _state.value = _state.value.copy(
            phase = Phase.Recording(staging.id, area?.id),
            elapsedMs = 0,
            lastError = null,
        )
        tickJob?.cancel()
        tickJob = scope.launch(Dispatchers.Main) {
            while (_state.value.phase is Phase.Recording) {
                val elapsed = System.currentTimeMillis() - recordingStartedAt
                _state.value = _state.value.copy(elapsedMs = elapsed)
                delay(250)
            }
        }
    }

    /** Stop the recording, move the audio into DictationStore, and try
     *  to drain the queue immediately (upload if online). */
    fun stopAndEnqueue() {
        if (_state.value.phase !is Phase.Recording) return
        tickJob?.cancel(); tickJob = null
        recorder.stop()
        val file = recorder.state.value.outputFile
        val staging = currentStaging
        val duration = _state.value.elapsedMs / 1000.0

        if (file == null || staging == null) {
            _state.value = _state.value.copy(
                phase = Phase.Idle,
                lastError = "Recording ended without a file.",
                elapsedMs = 0,
            )
            currentStaging = null
            currentArea = null
            return
        }

        val pending = try {
            store.enqueue(
                stagingId = staging.id,
                stagingDisplayName = staging.address ?: staging.name,
                areaId = currentArea?.id,
                areaName = currentArea?.name,
                durationSec = duration,
                sourceFile = file,
            )
        } catch (t: Throwable) {
            Log.w("DictationController", "enqueue failed", t)
            _state.value = _state.value.copy(
                phase = Phase.Idle,
                lastError = "Could not save recording: ${t.message}",
                elapsedMs = 0,
            )
            currentStaging = null; currentArea = null
            return
        }
        recorder.reset()
        currentStaging = null
        currentArea = null
        _state.value = _state.value.copy(phase = Phase.Idle, elapsedMs = 0)
        drainIfPossible(preferredId = pending.id)
    }

    fun cancel() {
        tickJob?.cancel(); tickJob = null
        recorder.cancel()
        currentStaging = null
        currentArea = null
        _state.value = _state.value.copy(phase = Phase.Idle, elapsedMs = 0)
    }

    /** Called by the view after it consumes a pendingReview value. */
    fun clearPendingReview() {
        if (_state.value.pendingReview != null) {
            _state.value = _state.value.copy(pendingReview = null)
        }
    }

    // MARK: - Upload queue

    fun drainIfPossible(preferredId: String? = null) {
        val token = tokenProvider() ?: return
        if (!NetworkMonitor.snapshot.value.isOnline) return
        if (store.nextPending() == null) return

        scope.launch {
            if (!drainLock.tryLock()) return@launch
            try {
                preferredId?.let { id ->
                    store.load().firstOrNull { it.id == id }?.let { uploadOne(it, token, preferred = true) }
                }
                while (NetworkMonitor.snapshot.value.isOnline) {
                    val next = store.nextPending() ?: break
                    uploadOne(next, token, preferred = false)
                }
            } finally {
                drainLock.unlock()
            }
        }
    }

    private suspend fun uploadOne(record: PendingDictation, token: String, preferred: Boolean) {
        val working = record.copy(
            status = PendingDictationStatus.UPLOADING,
            attemptCount = record.attemptCount + 1,
            lastError = null,
        )
        store.update(working)
        _state.value = _state.value.copy(
            phase = Phase.Uploading(working.id, working.stagingId),
        )

        try {
            val resp = ApiClient.uploadDictation(
                stagingId = working.stagingId,
                areaId = working.areaId,
                areaName = working.areaName,
                clientId = working.id,
                durationSec = working.durationSec,
                file = store.fileFor(working),
                token = token,
            )
            store.remove(working)
            _state.value = _state.value.copy(
                phase = Phase.Idle,
                // Only auto-present for the freshly-stopped recording. A
                // queue drain from an offline session shouldn't hijack UI.
                pendingReview = if (preferred) resp.dictation else _state.value.pendingReview,
            )
        } catch (t: Throwable) {
            Log.w("DictationController", "upload failed", t)
            store.update(working.copy(
                status = PendingDictationStatus.FAILED,
                lastError = t.message ?: "Upload failed",
            ))
            _state.value = _state.value.copy(
                phase = Phase.Idle,
                lastError = "Upload failed — will retry when online.",
            )
            delay(4_000)
        }
    }

    companion object {
        @Volatile
        private var instance: DictationController? = null

        fun get(context: Context): DictationController =
            instance ?: synchronized(this) {
                instance ?: DictationController(context.applicationContext).also { instance = it }
            }
    }
}
