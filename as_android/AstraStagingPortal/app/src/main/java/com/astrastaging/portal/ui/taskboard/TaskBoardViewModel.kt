package com.astrastaging.portal.ui.taskboard

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.astrastaging.portal.data.ApiClient
import com.astrastaging.portal.data.ApiError
import com.astrastaging.portal.data.Staging
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

enum class TaskPeriod(val wire: String, val label: String) {
    TODAY("today", "Today"),
    WEEK("week", "Week"),
    UPCOMING("upcoming", "Upcoming"),
    PAST("past", "Past"),
    ALL("all", "All"),
}

class TaskBoardViewModel(private val token: String) : ViewModel() {
    data class State(
        val period: TaskPeriod = TaskPeriod.UPCOMING,
        val mine: Boolean = false,
        val stagings: List<Staging> = emptyList(),
        val serverToday: String = "",
        val isLoading: Boolean = false,
        val error: String? = null,
        val unauthorized: Boolean = false,
        val togglingField: Pair<String, String>? = null,  // (stagingId, field)
    )

    private val _state = MutableStateFlow(State())
    val state: StateFlow<State> = _state.asStateFlow()

    fun setPeriod(p: TaskPeriod) {
        if (_state.value.period == p) return
        _state.value = _state.value.copy(period = p)
        load()
    }

    fun setMine(m: Boolean) {
        if (_state.value.mine == m) return
        _state.value = _state.value.copy(mine = m)
        load()
    }

    fun load() {
        _state.value = _state.value.copy(isLoading = true, error = null)
        viewModelScope.launch {
            try {
                val s = _state.value
                val resp = ApiClient.taskBoard(s.period.wire, s.mine, token)
                _state.value = _state.value.copy(
                    stagings = resp.stagings,
                    serverToday = resp.today,
                    isLoading = false,
                )
            } catch (e: ApiError.BadStatus) {
                if (e.code == 401) _state.value = _state.value.copy(isLoading = false, unauthorized = true)
                else _state.value = _state.value.copy(isLoading = false, error = e.message)
            } catch (e: Throwable) {
                _state.value = _state.value.copy(isLoading = false, error = e.message ?: "Failed to load")
            }
        }
    }

    fun toggleMilestone(stagingId: String, field: String, currentlyDone: Boolean) {
        _state.value = _state.value.copy(togglingField = stagingId to field)
        viewModelScope.launch {
            try {
                ApiClient.setMilestone(stagingId, field, !currentlyDone, token)
                load()
            } catch (e: ApiError.BadStatus) {
                if (e.code == 401) _state.value = _state.value.copy(unauthorized = true, togglingField = null)
                else _state.value = _state.value.copy(error = e.message, togglingField = null)
            } catch (e: Throwable) {
                _state.value = _state.value.copy(error = e.message ?: "Milestone update failed", togglingField = null)
            } finally {
                _state.value = _state.value.copy(togglingField = null)
            }
        }
    }
}

data class MilestoneDef(val label: String, val field: String)

val MILESTONE_DEFS = listOf(
    MilestoneDef("Design", "Design_Items_Matched_Date"),
    MilestoneDef("Before", "Before_Picture_Upload_Date"),
    MilestoneDef("After", "After_Picture_Upload_Date"),
    MilestoneDef("Packing", "Staging_Accessories_Packing_Finish_Date"),
    MilestoneDef("Setup", "Staging_Furniture_Design_Finish_Date"),
    MilestoneDef("WA", "WhatsApp_Group_Created_Date"),
)
