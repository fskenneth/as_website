package com.astrastaging.portal.data

import android.content.Context
import com.astrastaging.portal.ui.main.MenuItem

/**
 * Persists the user's menu order across launches. The first 4 visible items
 * (after role filtering) form the dock; the rest live under "More".
 *
 * Stored as a single comma-joined string of [MenuItem.key]s — small enough
 * that plain SharedPreferences is fine; no need for DataStore here.
 */
class MenuPreferencesStore(appContext: Context) {
    private val prefs = appContext.getSharedPreferences("menu_prefs", Context.MODE_PRIVATE)

    fun load(): List<MenuItem> {
        val raw = prefs.getString(KEY_ORDER, null)
        if (raw.isNullOrBlank()) return MenuItem.defaultOrder
        val parsed = raw.split(",").mapNotNull { MenuItem.fromKey(it.trim()) }
        // Backfill items added in a future build so the user sees them.
        val missing = MenuItem.entries.filter { it !in parsed }
        return parsed + missing
    }

    fun save(order: List<MenuItem>) {
        prefs.edit()
            .putString(KEY_ORDER, order.joinToString(",") { it.key })
            .apply()
    }

    private companion object {
        const val KEY_ORDER = "menu_order_v1"
    }
}
