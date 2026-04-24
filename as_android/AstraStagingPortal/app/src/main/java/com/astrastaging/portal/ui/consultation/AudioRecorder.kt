package com.astrastaging.portal.ui.consultation

import android.content.Context
import android.media.MediaRecorder
import android.os.Build
import android.util.Log
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.io.File
import java.util.UUID

/**
 * AAC-LC mono 16 kHz 32 kbps .m4a recorder for the Consultation Dictate flow.
 *
 * Matches the iOS recorder settings byte-for-byte so Whisper receives a
 * consistent input regardless of platform. A 1-hour recording is ~14 MB.
 *
 * Live preview is not provided — Android's SpeechRecognizer can't share the
 * mic with MediaRecorder. The user sees "Recording…" with an elapsed timer
 * and level meter; the final transcript comes back from the server.
 */
class AudioRecorder(private val context: Context) {
    enum class Phase { IDLE, RECORDING, STOPPED, FAILED }

    data class State(
        val phase: Phase = Phase.IDLE,
        val elapsedMs: Long = 0,
        val levelNorm: Float = 0f,       // 0..1 rough amplitude
        val outputFile: File? = null,
        val error: String? = null,
    )

    private val _state = MutableStateFlow(State())
    val state: StateFlow<State> = _state.asStateFlow()

    private var recorder: MediaRecorder? = null
    private var outFile: File? = null
    private var startTime: Long = 0
    private var tickJob: Job? = null

    fun start(scope: CoroutineScope) {
        if (_state.value.phase == Phase.RECORDING) return

        val file = File(
            context.cacheDir,
            "dictation-${UUID.randomUUID()}.m4a",
        )
        outFile = file

        val rec = if (Build.VERSION.SDK_INT >= 31) MediaRecorder(context) else @Suppress("DEPRECATION") MediaRecorder()
        try {
            rec.setAudioSource(MediaRecorder.AudioSource.MIC)
            rec.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
            rec.setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
            rec.setAudioChannels(1)
            rec.setAudioSamplingRate(16_000)
            rec.setAudioEncodingBitRate(32_000)
            rec.setOutputFile(file.absolutePath)
            rec.prepare()
            rec.start()
        } catch (t: Throwable) {
            Log.e("AudioRecorder", "start failed", t)
            runCatching { rec.release() }
            _state.value = State(phase = Phase.FAILED, error = t.message ?: "Could not start recording")
            return
        }

        recorder = rec
        startTime = System.currentTimeMillis()
        _state.value = State(phase = Phase.RECORDING)

        tickJob = scope.launch(Dispatchers.Main) {
            while (_state.value.phase == Phase.RECORDING) {
                delay(100)
                val elapsed = System.currentTimeMillis() - startTime
                val amp = runCatching { recorder?.maxAmplitude ?: 0 }.getOrDefault(0)
                // maxAmplitude: 0..32767 (short). Map log-ish to 0..1 for display.
                val norm = (amp.toFloat() / 8000f).coerceIn(0f, 1f)
                _state.value = _state.value.copy(elapsedMs = elapsed, levelNorm = norm)
            }
        }
    }

    fun stop() {
        val rec = recorder ?: return
        tickJob?.cancel(); tickJob = null

        val finished = runCatching {
            rec.stop()
            true
        }.getOrElse { t ->
            Log.w("AudioRecorder", "stop threw: ${t.message}")
            false
        }
        runCatching { rec.release() }
        recorder = null

        val file = outFile
        outFile = null
        if (finished && file != null && file.exists() && file.length() > 0) {
            _state.value = _state.value.copy(phase = Phase.STOPPED, outputFile = file)
        } else {
            _state.value = _state.value.copy(
                phase = Phase.FAILED,
                error = "Recording ended without producing an audio file.",
            )
        }
    }

    fun cancel() {
        tickJob?.cancel(); tickJob = null
        runCatching { recorder?.stop() }
        runCatching { recorder?.release() }
        recorder = null
        outFile?.takeIf { it.exists() }?.delete()
        outFile = null
        _state.value = State(phase = Phase.IDLE)
    }

    fun reset() {
        _state.value = State(phase = Phase.IDLE)
    }
}
