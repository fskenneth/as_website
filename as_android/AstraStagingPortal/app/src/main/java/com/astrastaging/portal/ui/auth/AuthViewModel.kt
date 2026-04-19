package com.astrastaging.portal.ui.auth

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
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
        if (t != null) {
            viewModelScope.launch { ApiClient.logout(t) }
        }
    }
}
