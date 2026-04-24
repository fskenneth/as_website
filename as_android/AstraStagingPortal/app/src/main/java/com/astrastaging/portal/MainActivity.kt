package com.astrastaging.portal

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.astrastaging.portal.data.media.CaptureRepository
import com.astrastaging.portal.data.network.NetworkMonitor
import com.astrastaging.portal.data.settings.AppSettings
import com.astrastaging.portal.ui.auth.AuthViewModel
import com.astrastaging.portal.ui.auth.LoginScreen
import com.astrastaging.portal.ui.main.MainScreen
import com.astrastaging.portal.ui.theme.AstraAppTheme
import kotlinx.coroutines.flow.first

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        enableEdgeToEdge()
        super.onCreate(savedInstanceState)
        NetworkMonitor.start(applicationContext)
        // Register Coil's VideoFrameDecoder so AsyncImage can render the
        // first frame of .mp4/.mov files as a thumbnail cover.
        coil.Coil.setImageLoader(
            coil.ImageLoader.Builder(applicationContext)
                .components { add(coil.decode.VideoFrameDecoder.Factory()) }
                .build(),
        )
        setContent {
            AstraAppTheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    AppRoot()
                }
            }
        }
    }
}

@Composable
private fun AppRoot() {
    val vm: AuthViewModel = androidx.lifecycle.viewmodel.compose.viewModel()
    val state by vm.state.collectAsStateWithLifecycle()
    val context = androidx.compose.ui.platform.LocalContext.current

    // Kick the upload queue once we're signed in — drains anything left over
    // from a previous session as soon as the network constraint is met.
    LaunchedEffect(state.isSignedIn) {
        if (state.isSignedIn) {
            val appCtx = context.applicationContext
            val settings = AppSettings(appCtx)
            val wifi = settings.wifiOnlyMediaUpload.first()
            CaptureRepository(appCtx).scheduleUpload(wifiOnly = wifi)
        }
    }

    when {
        state.isLoading && !state.isSignedIn -> SplashLoading()
        !state.isSignedIn -> LoginScreen(
            isLoading = state.isLoading,
            loginError = state.loginError,
            onLogin = vm::login,
        )
        else -> MainScreen(
            user = state.user!!,
            token = state.token!!,
            onLogout = vm::logout,
        )
    }
}

@Composable
private fun SplashLoading() {
    Column(
        modifier = Modifier.fillMaxSize(),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        CircularProgressIndicator()
    }
}
