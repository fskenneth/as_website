package com.astrastaging.portal.ui.consultation

import android.content.Context
import android.util.Log
import kotlinx.serialization.Serializable
import kotlinx.serialization.builtins.ListSerializer
import kotlinx.serialization.json.Json
import java.io.File
import java.util.UUID

/**
 * On-disk queue of voice dictations captured on the Consultation tab.
 * Mirrors the iOS DictationStore: a plain JSON index file alongside the
 * audio files, living under filesDir/DictationQueue/. Survives process
 * death; survives going offline.
 *
 * A pending dictation is audio that hasn't been sent to
 * /api/v1/stagings/{id}/dictations yet. Once the server accepts it, the
 * entry is removed from this store — the server owns the transcript +
 * summary from that point.
 */
@Serializable
enum class PendingDictationStatus { PENDING, UPLOADING, FAILED }

@Serializable
data class PendingDictation(
    val id: String,
    val stagingId: String,
    val stagingDisplayName: String? = null,
    val areaId: String? = null,
    val areaName: String? = null,
    val fileName: String,
    val byteSize: Long = 0,
    val durationSec: Double = 0.0,
    /** Epoch millis. */
    val createdAt: Long,
    val status: PendingDictationStatus = PendingDictationStatus.PENDING,
    val lastError: String? = null,
    val attemptCount: Int = 0,
)

class DictationStore private constructor(private val context: Context) {
    private val folder: File by lazy {
        File(context.filesDir, "DictationQueue").apply { mkdirs() }
    }
    private val indexFile: File by lazy { File(folder, "index.json") }
    private val json = Json {
        ignoreUnknownKeys = true
        encodeDefaults = true
    }

    fun fileFor(dictation: PendingDictation): File = File(folder, dictation.fileName)

    @Synchronized
    fun load(): List<PendingDictation> {
        if (!indexFile.exists()) return emptyList()
        return try {
            val raw = indexFile.readText()
            if (raw.isBlank()) emptyList()
            else json.decodeFromString(
                ListSerializer(PendingDictation.serializer()),
                raw,
            ).filter { fileFor(it).exists() }
        } catch (t: Throwable) {
            Log.w("DictationStore", "load failed: ${t.message}")
            emptyList()
        }
    }

    @Synchronized
    private fun save(all: List<PendingDictation>) {
        try {
            val out = json.encodeToString(
                ListSerializer(PendingDictation.serializer()),
                all,
            )
            indexFile.writeText(out)
        } catch (t: Throwable) {
            Log.w("DictationStore", "save failed: ${t.message}")
        }
    }

    @Synchronized
    fun enqueue(
        stagingId: String,
        stagingDisplayName: String?,
        areaId: String?,
        areaName: String?,
        durationSec: Double,
        sourceFile: File,
    ): PendingDictation {
        val id = UUID.randomUUID().toString()
        val filename = "$id.m4a"
        val dest = File(folder, filename)
        // Move source into our sandbox. If the OS purges the cache dir we
        // lose the recording, but the index stays consistent because load()
        // filters by file existence.
        if (!sourceFile.renameTo(dest)) {
            sourceFile.copyTo(dest, overwrite = true)
            sourceFile.delete()
        }

        val record = PendingDictation(
            id = id,
            stagingId = stagingId,
            stagingDisplayName = stagingDisplayName,
            areaId = areaId,
            areaName = areaName,
            fileName = filename,
            byteSize = dest.length(),
            durationSec = durationSec,
            createdAt = System.currentTimeMillis(),
        )
        val current = load().toMutableList()
        current += record
        save(current)
        return record
    }

    @Synchronized
    fun update(dictation: PendingDictation) {
        val current = load().toMutableList()
        val idx = current.indexOfFirst { it.id == dictation.id }
        if (idx >= 0) {
            current[idx] = dictation
            save(current)
        }
    }

    @Synchronized
    fun remove(dictation: PendingDictation) {
        fileFor(dictation).delete()
        val current = load().filterNot { it.id == dictation.id }
        save(current)
    }

    @Synchronized
    fun nextPending(): PendingDictation? =
        load().filter {
            it.status == PendingDictationStatus.PENDING ||
                it.status == PendingDictationStatus.FAILED
        }.minByOrNull { it.createdAt }

    fun pendingCount(stagingId: String? = null): Int =
        load().count {
            (it.status == PendingDictationStatus.PENDING ||
                it.status == PendingDictationStatus.FAILED) &&
                (stagingId == null || it.stagingId == stagingId)
        }

    companion object {
        @Volatile
        private var instance: DictationStore? = null

        fun get(context: Context): DictationStore =
            instance ?: synchronized(this) {
                instance ?: DictationStore(context.applicationContext).also { instance = it }
            }
    }
}
