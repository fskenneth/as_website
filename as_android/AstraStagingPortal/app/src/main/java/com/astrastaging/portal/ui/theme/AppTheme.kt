package com.astrastaging.portal.ui.theme

import android.app.Application
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.astrastaging.portal.data.settings.AccentTheme
import com.astrastaging.portal.data.settings.AppSettings
import com.astrastaging.portal.data.settings.ThemeMode

/**
 * Theme wrapper driven by [AppSettings]. Wraps the root Composable tree so
 * every screen picks up the selected accent + dark/light mode without each
 * screen caring.
 */
@Composable
fun AstraAppTheme(content: @Composable () -> Unit) {
    val context = LocalContext.current
    val settings = remember { AppSettings(context.applicationContext as Application) }

    val mode by settings.themeMode.collectAsStateWithLifecycle(initialValue = ThemeMode.AUTO)
    val accent by settings.accent.collectAsStateWithLifecycle(initialValue = AccentTheme.SLATE)

    val systemDark = isSystemInDarkTheme()
    val useDark = when (mode) {
        ThemeMode.AUTO -> systemDark
        ThemeMode.LIGHT -> false
        ThemeMode.DARK -> true
    }

    val accentColor = Color(if (useDark) accent.darkHex else accent.lightHex)
    val scheme = if (useDark) {
        darkColorScheme(primary = accentColor, secondary = accentColor)
    } else {
        lightColorScheme(primary = accentColor, secondary = accentColor)
    }

    MaterialTheme(colorScheme = scheme, content = content)
}
