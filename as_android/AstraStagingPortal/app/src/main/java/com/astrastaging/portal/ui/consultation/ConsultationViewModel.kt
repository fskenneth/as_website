package com.astrastaging.portal.ui.consultation

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.astrastaging.portal.data.ApiClient
import com.astrastaging.portal.data.ApiError
import com.astrastaging.portal.data.ConsultationCache
import com.astrastaging.portal.data.Staging
import com.astrastaging.portal.data.StagingArea
import com.astrastaging.portal.data.media.CaptureEntity
import com.astrastaging.portal.data.media.CaptureMediaType
import com.astrastaging.portal.data.media.CaptureRepository
import com.astrastaging.portal.data.media.MediaProcessor
import com.astrastaging.portal.data.network.NetworkMonitor
import com.astrastaging.portal.data.network.NetworkSnapshot
import com.astrastaging.portal.data.settings.AppSettings
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import java.io.File

class ConsultationViewModel(
    app: Application,
    private val token: String,
) : AndroidViewModel(app) {
    data class State(
        val stagings: List<Staging> = emptyList(),
        val selectedId: String? = null,
        val search: String = "",
        val isLoading: Boolean = false,
        val error: String? = null,
        val unauthorized: Boolean = false,
        val areasByStaging: Map<String, List<StagingArea>> = emptyMap(),
        val loadingAreasFor: String? = null,
        val areasError: String? = null,
        val pickerOpen: Boolean = false,
        val catalog: List<com.astrastaging.portal.data.QuoteCatalogItem> = emptyList(),
        val quoteByStaging: Map<String, com.astrastaging.portal.data.StagingQuote> = emptyMap(),
    ) {
        val selected: Staging? get() = stagings.firstOrNull { it.id == selectedId }

        val filtered: List<Staging>
            get() {
                val q = search.trim().lowercase()
                if (q.isEmpty()) return stagings
                return stagings.filter {
                    (it.name ?: "").lowercase().contains(q)
                        || (it.address ?: "").lowercase().contains(q)
                        || it.customer.fullName.lowercase().contains(q)
                }
            }
    }

    private val appContext = app.applicationContext
    private val cache = ConsultationCache(appContext)
    private val settings = AppSettings(appContext)
    val captures = CaptureRepository(appContext)

    private val _state = MutableStateFlow(State())
    val state: StateFlow<State> = _state.asStateFlow()

    val network: StateFlow<NetworkSnapshot> = NetworkMonitor.snapshot

    val wifiOnly: StateFlow<Boolean> = settings.wifiOnlyMediaUpload
        .stateIn(viewModelScope, SharingStarted.Eagerly, true)

    init {
        // Hydrate from cache first so the UI is never blank offline.
        cache.loadStagings()?.let { cached ->
            _state.value = _state.value.copy(
                stagings = cached.stagings,
                selectedId = cached.stagings.firstOrNull()?.id,
            )
            cached.stagings.firstOrNull()?.id?.let {
                loadAreas(it)
                loadQuote(it)
            }
        }
        ensureCatalogLoaded()
    }

    fun load() {
        _state.value = _state.value.copy(isLoading = true, error = null)
        viewModelScope.launch {
            if (!NetworkMonitor.snapshot.value.isOnline) {
                _state.value = _state.value.copy(isLoading = false)
                return@launch
            }
            try {
                val resp = ApiClient.consultationStagings(token)
                cache.saveStagings(resp)
                val current = _state.value.selectedId
                val keep = current != null && resp.stagings.any { it.id == current }
                _state.value = _state.value.copy(
                    stagings = resp.stagings,
                    selectedId = if (keep) current else resp.stagings.firstOrNull()?.id,
                    isLoading = false,
                )
                _state.value.selectedId?.let {
                    loadAreas(it)
                    loadQuote(it)
                }
                ensureCatalogLoaded()
            } catch (e: ApiError.BadStatus) {
                if (e.code == 401) _state.value = _state.value.copy(isLoading = false, unauthorized = true)
                else _state.value = _state.value.copy(isLoading = false, error = e.message)
            } catch (e: Throwable) {
                _state.value = _state.value.copy(isLoading = false, error = e.message ?: "Failed to load")
            }
        }
    }

    fun loadAreas(stagingId: String, forceNetwork: Boolean = false) {
        // Cache-first so areas are available offline.
        if (!forceNetwork) {
            cache.loadAreas(stagingId)?.let { cached ->
                val current = _state.value.areasByStaging.toMutableMap()
                current[stagingId] = cached.areas
                _state.value = _state.value.copy(areasByStaging = current)
            }
        }
        if (!NetworkMonitor.snapshot.value.isOnline) return
        _state.value = _state.value.copy(loadingAreasFor = stagingId, areasError = null)
        viewModelScope.launch {
            try {
                val resp = ApiClient.stagingAreas(stagingId, token)
                cache.saveAreas(resp)
                val current = _state.value.areasByStaging.toMutableMap()
                current[stagingId] = resp.areas
                _state.value = _state.value.copy(
                    areasByStaging = current,
                    loadingAreasFor = null,
                )
            } catch (t: Throwable) {
                _state.value = _state.value.copy(
                    loadingAreasFor = null,
                    areasError = t.message ?: "Couldn't load areas",
                )
            }
        }
    }

    fun select(id: String) {
        _state.value = _state.value.copy(selectedId = id, pickerOpen = false)
        loadAreas(id)
        loadQuote(id)
    }

    fun ensureCatalogLoaded() {
        if (_state.value.catalog.isNotEmpty()) return
        if (!NetworkMonitor.snapshot.value.isOnline) return
        viewModelScope.launch {
            runCatching { ApiClient.quoteCatalog(token) }
                .onSuccess { resp -> _state.value = _state.value.copy(catalog = resp.items) }
        }
    }

    fun loadQuote(stagingId: String) {
        if (!NetworkMonitor.snapshot.value.isOnline) return
        viewModelScope.launch {
            runCatching { ApiClient.stagingQuote(stagingId, token) }
                .onSuccess { q ->
                    val map = _state.value.quoteByStaging.toMutableMap()
                    map[stagingId] = q
                    _state.value = _state.value.copy(quoteByStaging = map)
                }
        }
    }

    fun upsertLineItem(
        stagingId: String,
        areaId: String,
        action: String,
        itemName: String,
        delta: Int,
    ) {
        viewModelScope.launch {
            runCatching {
                ApiClient.upsertLineItem(stagingId, areaId, action, itemName, delta, token)
            }.onSuccess { q ->
                val map = _state.value.quoteByStaging.toMutableMap()
                map[stagingId] = q
                _state.value = _state.value.copy(quoteByStaging = map)
            }
        }
    }

    fun deleteLineItem(stagingId: String, areaId: String, lineId: String) {
        viewModelScope.launch {
            runCatching {
                ApiClient.deleteLineItem(stagingId, areaId, lineId, token)
            }.onSuccess { q ->
                val map = _state.value.quoteByStaging.toMutableMap()
                map[stagingId] = q
                _state.value = _state.value.copy(quoteByStaging = map)
            }
        }
    }

    fun setSearch(q: String) {
        _state.value = _state.value.copy(search = q)
    }

    fun setPickerOpen(open: Boolean) {
        _state.value = _state.value.copy(pickerOpen = open)
    }

    fun capturesForStaging(stagingId: String) =
        captures.observeForStaging(stagingId)

    /**
     * Persist a captured file and kick the upload worker.
     * Photos are downscaled first; video was already captured at 720p.
     */
    fun enqueueCapture(
        stagingId: String,
        area: StagingArea?,
        type: CaptureMediaType,
        file: File,
        mimeType: String,
    ) {
        viewModelScope.launch {
            val finalFile = if (type != CaptureMediaType.VIDEO)
                MediaProcessor.downscalePhoto(appContext, file)
            else file
            captures.enqueue(
                stagingId = stagingId,
                areaId = area?.id,
                areaName = area?.name,
                mediaType = type,
                mimeType = mimeType,
                sourceFile = finalFile,
            )
            captures.scheduleUpload(wifiOnly = wifiOnly.value)
        }
    }

    fun deleteCapture(capture: CaptureEntity) {
        viewModelScope.launch { captures.deleteWithServer(capture, token) }
    }

    fun retryUploads() {
        captures.scheduleUpload(wifiOnly = wifiOnly.value)
    }

    /**
     * Create a new area and refresh the VM cache. If [requestedName] is
     * literally "New Area" and there's already one on this staging, we:
     *   - rename the first "New Area" to "New Area 1" (if no numbered
     *     variants exist yet), then create this as "New Area 2"; or
     *   - skip the rename and assign the next unused "New Area N".
     * Returns the created area, or null on failure.
     */
    suspend fun createAreaSuspend(stagingId: String, requestedName: String): StagingArea? {
        return try {
            val existing = _state.value.areasByStaging[stagingId].orEmpty()
            val finalName = resolveNewAreaName(existing, requestedName)

            // If the requested name is "New Area" and there's already an
            // unnumbered "New Area", rename it to "New Area 1" first so the
            // two coexist cleanly.
            val updatedExisting = if (
                requestedName.equals("New Area", ignoreCase = true) &&
                existing.any { it.name.equals("New Area", ignoreCase = true) } &&
                existing.none { it.name.matches(Regex("""(?i)New Area \d+""")) }
            ) {
                val target = existing.first { it.name.equals("New Area", ignoreCase = true) }
                runCatching {
                    ApiClient.renameArea(stagingId, target.id, "New Area 1", token).area
                }
                existing.map {
                    if (it.id == target.id) it.copy(name = "New Area 1") else it
                }
            } else existing

            val resp = ApiClient.createArea(stagingId, finalName, null, token)
            val current = updatedExisting + resp.area

            val map = _state.value.areasByStaging.toMutableMap()
            map[stagingId] = current
            _state.value = _state.value.copy(areasByStaging = map)
            cache.saveAreas(
                com.astrastaging.portal.data.StagingAreasResponse(
                    staging_id = stagingId,
                    areas = current,
                    total = current.size,
                )
            )
            resp.area
        } catch (t: Throwable) {
            null
        }
    }

    /**
     * When the user taps "Add" with no custom name, we want a sensible
     * fallback. Apply the "New Area" → "New Area 2" → "New Area 3" rule.
     * Any other input is passed through verbatim.
     */
    private fun resolveNewAreaName(
        existing: List<StagingArea>,
        requested: String,
    ): String {
        val trimmed = requested.trim()
        if (!trimmed.equals("New Area", ignoreCase = true)) return trimmed

        val hasUnnumbered = existing.any { it.name.equals("New Area", ignoreCase = true) }
        val numbers = existing.mapNotNull {
            Regex("""(?i)New Area (\d+)""").matchEntire(it.name)?.groupValues?.get(1)?.toIntOrNull()
        }
        return when {
            !hasUnnumbered && numbers.isEmpty() -> "New Area"
            numbers.isEmpty() -> "New Area 2"   // rename-first branch handles "1"
            else -> "New Area ${numbers.max() + 1}"
        }
    }

    class Factory(
        private val app: Application,
        private val token: String,
    ) : ViewModelProvider.Factory {
        @Suppress("UNCHECKED_CAST")
        override fun <T : ViewModel> create(modelClass: Class<T>): T {
            return ConsultationViewModel(app, token) as T
        }
    }
}
