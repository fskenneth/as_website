package com.astrastaging.portal.ui.items

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.astrastaging.portal.data.ApiClient
import com.astrastaging.portal.data.ApiError
import com.astrastaging.portal.data.Item
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class ItemsViewModel(private val token: String) : ViewModel() {
    data class State(
        val search: String = "",
        val items: List<Item> = emptyList(),
        val isLoading: Boolean = false,
        val error: String? = null,
        val unauthorized: Boolean = false,
    )

    private val _state = MutableStateFlow(State())
    val state: StateFlow<State> = _state.asStateFlow()
    private var searchJob: Job? = null

    fun setSearch(q: String) {
        _state.value = _state.value.copy(search = q)
        searchJob?.cancel()
        searchJob = viewModelScope.launch {
            delay(350)  // debounce
            load()
        }
    }

    fun load() {
        _state.value = _state.value.copy(isLoading = true, error = null)
        viewModelScope.launch {
            try {
                val resp = ApiClient.items(_state.value.search.trim(), token)
                _state.value = _state.value.copy(items = resp.items, isLoading = false)
            } catch (e: ApiError.BadStatus) {
                if (e.code == 401) _state.value = _state.value.copy(isLoading = false, unauthorized = true)
                else _state.value = _state.value.copy(isLoading = false, error = e.message)
            } catch (e: Throwable) {
                _state.value = _state.value.copy(isLoading = false, error = e.message ?: "Failed to load")
            }
        }
    }
}
