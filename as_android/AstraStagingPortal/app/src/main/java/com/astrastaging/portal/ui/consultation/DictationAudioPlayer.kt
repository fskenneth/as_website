package com.astrastaging.portal.ui.consultation

import android.content.Context
import android.media.MediaPlayer
import android.util.Log
import com.astrastaging.portal.data.ApiClient
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.io.File

/**
 * Shared audio player for dictation playback from the Consultation tab.
 * One dictation plays at a time. Bytes are downloaded with Bearer auth,
 * cached to filesDir, then played via MediaPlayer. Progress (0…1) is
 * exposed so rows can render a bar.
 */
class DictationAudioPlayer private constructor(private val context: Context) {
    data class State(
        val currentlyPlayingId: String? = null,
        val loadingId: String? = null,
        val progress: Float = 0f,
        val currentMs: Int = 0,
        val durationMs: Int = 0,
    )

    private val _state = MutableStateFlow(State())
    val state: StateFlow<State> = _state.asStateFlow()

    private val scope = CoroutineScope(Dispatchers.Main + SupervisorJob())
    private var player: MediaPlayer? = null
    private var tickJob: Job? = null

    fun isPlaying(id: String): Boolean = _state.value.currentlyPlayingId == id

    /** Toggle playback for `dictationId`. Same id → stop. Different id →
     *  stop the current one and start the new one. */
    fun toggle(dictationId: String, token: String) {
        if (_state.value.currentlyPlayingId == dictationId) {
            stop(); return
        }
        stop()
        _state.value = _state.value.copy(loadingId = dictationId)
        scope.launch {
            val file = try {
                val bytes = ApiClient.downloadDictationAudio(dictationId, token)
                val out = File(context.cacheDir, "dict-play-$dictationId.m4a")
                out.writeBytes(bytes)
                out
            } catch (t: Throwable) {
                Log.w("DictationAudioPlayer", "download failed", t)
                _state.value = _state.value.copy(loadingId = null)
                return@launch
            }

            val mp = MediaPlayer()
            try {
                mp.setDataSource(file.absolutePath)
                mp.prepare()
                mp.setOnCompletionListener { stop() }
                mp.start()
            } catch (t: Throwable) {
                Log.w("DictationAudioPlayer", "start failed", t)
                runCatching { mp.release() }
                _state.value = _state.value.copy(loadingId = null)
                return@launch
            }
            player = mp
            val dur = mp.duration
            _state.value = State(
                currentlyPlayingId = dictationId,
                loadingId = null,
                progress = 0f,
                currentMs = 0,
                durationMs = dur,
            )
            tickJob?.cancel()
            tickJob = scope.launch {
                while (true) {
                    val cur = player ?: break
                    if (!cur.isPlaying) break
                    val pos = runCatching { cur.currentPosition }.getOrDefault(0)
                    val total = runCatching { cur.duration }.getOrDefault(dur).coerceAtLeast(1)
                    _state.value = _state.value.copy(
                        currentMs = pos,
                        durationMs = total,
                        progress = (pos.toFloat() / total.toFloat()).coerceIn(0f, 1f),
                    )
                    delay(120)
                }
            }
        }
    }

    fun stop() {
        tickJob?.cancel(); tickJob = null
        runCatching { player?.stop() }
        runCatching { player?.release() }
        player = null
        _state.value = State()
    }

    companion object {
        @Volatile private var instance: DictationAudioPlayer? = null

        fun get(context: Context): DictationAudioPlayer =
            instance ?: synchronized(this) {
                instance ?: DictationAudioPlayer(context.applicationContext).also { instance = it }
            }
    }
}
