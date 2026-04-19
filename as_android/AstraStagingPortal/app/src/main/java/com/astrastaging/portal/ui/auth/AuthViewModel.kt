package com.astrastaging.portal.ui.auth

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.astrastaging.portal.BuildConfig
import com.astrastaging.portal.data.ApiClient
import com.astrastaging.portal.data.ApiError
import com.astrastaging.portal.data.ApiUser
import com.astrastaging.portal.data.TokenStore
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

/** Holds the signed-in user + token. Mirrors as_ios/AuthStore.swift. */
class AuthViewModel(app: Application) : AndroidViewModel(app) {
    private val tokenStore = TokenStore(app.applicationContext)

    data class State(
        val user: ApiUser? = null,
        val token: String? = null,
        val isLoading: Boolean = true,  // start true; flips false after restore attempt
        val loginError: String? = null,
    ) {
        val isSignedIn get() = user != null && token != null
    }

    private val _state = MutableStateFlow(State())
    val state: StateFlow<State> = _state.asStateFlow()

    init { restoreSession() }

    private fun restoreSession() {
        viewModelScope.launch {
            // DEV bypass: debug builds with a hardcoded token skip the login
            // screen entirely. Release builds have DEV_BYPASS_TOKEN="" so
            // this branch is dead code.
            val bypass = BuildConfig.DEV_BYPASS_TOKEN
            if (bypass.isNotEmpty()) {
                try {
                    val me = ApiClient.me(bypass)
                    _state.value = State(user = me.user, token = bypass, isLoading = false)
                    return@launch
                } catch (_: Throwable) {
                    // Bypass token rejected by server — fall through to normal flow
                }
            }

            val saved = tokenStore.get()
            if (saved.isNullOrEmpty()) {
                _state.value = _state.value.copy(isLoading = false)
                return@launch
            }
            try {
                val me = ApiClient.me(saved)
                _state.value = State(user = me.user, token = saved, isLoading = false)
            } catch (_: Throwable) {
                // Token stale or server down — clear it so user sees login
                tokenStore.clear()
                _state.value = State(isLoading = false)
            }
        }
    }

    fun login(email: String, password: String) {
        _state.value = _state.value.copy(isLoading = true, loginError = null)
        viewModelScope.launch {
            try {
                val resp = ApiClient.login(email.trim(), password)
                tokenStore.set(resp.token)
                _state.value = State(user = resp.user, token = resp.token, isLoading = false)
            } catch (e: ApiError.BadStatus) {
                _state.value = _state.value.copy(isLoading = false, loginError = e.serverMessage ?: "Login failed")
            } catch (e: Throwable) {
                _state.value = _state.value.copy(isLoading = false, loginError = e.message ?: "Login failed")
            }
        }
    }

    fun logout() {
        val t = _state.value.token
        _state.value = State(isLoading = false)
        tokenStore.clear()
        // Don't invalidate the dev bypass token server-side — next cold
        // start would lose the auto-login.
        val bypass = BuildConfig.DEV_BYPASS_TOKEN
        if (t != null && t != bypass) {
            viewModelScope.launch { ApiClient.logout(t) }
        }
    }
}
