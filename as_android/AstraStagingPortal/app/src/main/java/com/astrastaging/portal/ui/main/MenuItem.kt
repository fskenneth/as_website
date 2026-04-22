package com.astrastaging.portal.ui.main

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Apartment
import androidx.compose.material.icons.outlined.Business
import androidx.compose.material.icons.outlined.CheckCircle
import androidx.compose.material.icons.outlined.Inventory2
import androidx.compose.material.icons.outlined.MoreHoriz
import androidx.compose.material.icons.outlined.Person
import androidx.compose.material.icons.outlined.SupportAgent
import androidx.compose.ui.graphics.vector.ImageVector

/**
 * All possible menu destinations. The order in [defaultOrder] is the seed
 * for new installs; once the user customizes, MenuPreferencesStore persists
 * their preferred order.
 *
 * minRoleLevel: 1 = execution (mover/stager), 2 = manager, 3 = owner.
 */
enum class MenuItem(
    val key: String,
    val label: String,
    val icon: ImageVector,
    val minRoleLevel: Int,
) {
    TASKS("tasks", "Tasks", Icons.Outlined.CheckCircle, 1),
    ITEMS("items", "Items", Icons.Outlined.Inventory2, 1),
    ME("me", "Me", Icons.Outlined.Person, 1),
    CONSULTATION("consultation", "Consultation", Icons.Outlined.SupportAgent, 1),
    SALES("sales", "Sales", Icons.Outlined.Business, 2),
    HR("hr", "HR", Icons.Outlined.Apartment, 3);

    companion object {
        val defaultOrder: List<MenuItem> = listOf(TASKS, ITEMS, CONSULTATION, ME, SALES, HR)
        fun fromKey(key: String): MenuItem? = entries.firstOrNull { it.key == key }
        val MoreIcon: ImageVector get() = Icons.Outlined.MoreHoriz
    }
}
