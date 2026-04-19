package com.astrastaging.portal.ui.main

import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Apartment
import androidx.compose.material.icons.outlined.CheckCircle
import androidx.compose.material.icons.outlined.Inventory2
import androidx.compose.material.icons.outlined.Person
import androidx.compose.material.icons.outlined.Work
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import com.astrastaging.portal.data.ApiUser
import com.astrastaging.portal.ui.items.ItemsScreen
import com.astrastaging.portal.ui.me.MeScreen
import com.astrastaging.portal.ui.stubs.HRAccountingScreen
import com.astrastaging.portal.ui.stubs.SalesManagementScreen
import com.astrastaging.portal.ui.taskboard.TaskBoardScreen

enum class Tab(val label: String, val icon: ImageVector, val minRole: Int) {
    TASK_BOARD("Task Board", Icons.Outlined.CheckCircle, 1),
    ITEMS("Items", Icons.Outlined.Inventory2, 1),
    ME("Me", Icons.Outlined.Person, 1),
    SALES("Sales", Icons.Outlined.Work, 2),
    HR("HR", Icons.Outlined.Apartment, 3),
}

@Composable
fun MainScreen(
    user: ApiUser,
    token: String,
    onLogout: () -> Unit,
) {
    val visible = Tab.entries.filter { it.minRole <= user.roleLevel }
    var selected by rememberSaveable { mutableStateOf(Tab.TASK_BOARD) }
    // Drop invalid selections if role downgrades
    if (selected !in visible) selected = Tab.TASK_BOARD

    Scaffold(
        bottomBar = {
            NavigationBar {
                visible.forEach { tab ->
                    NavigationBarItem(
                        selected = selected == tab,
                        onClick = { selected = tab },
                        icon = { Icon(tab.icon, contentDescription = tab.label) },
                        label = { Text(tab.label) },
                    )
                }
            }
        }
    ) { padding ->
        val modifier = Modifier.padding(padding)
        when (selected) {
            Tab.TASK_BOARD -> TaskBoardScreen(user = user, token = token, modifier = modifier)
            Tab.ITEMS -> ItemsScreen(token = token, modifier = modifier)
            Tab.ME -> MeScreen(user = user, onLogout = onLogout, modifier = modifier)
            Tab.SALES -> SalesManagementScreen(modifier = modifier)
            Tab.HR -> HRAccountingScreen(modifier = modifier)
        }
    }
}
