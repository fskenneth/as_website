package com.astrastaging.portal.ui.stubs

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Apartment
import androidx.compose.material.icons.outlined.Work
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp

@Composable
fun SalesManagementScreen(modifier: Modifier = Modifier) {
    Placeholder(
        modifier = modifier,
        icon = Icons.Outlined.Work,
        title = "Sales & Management",
        subtitle = "Inquiries, staging assignment, invoicing, customer portal.\nComing soon.",
    )
}

@Composable
fun HRAccountingScreen(modifier: Modifier = Modifier) {
    Placeholder(
        modifier = modifier,
        icon = Icons.Outlined.Apartment,
        title = "HR & Accounting",
        subtitle = "Employees, all pay, staging analytics.\nComing soon.",
    )
}

@Composable
private fun Placeholder(modifier: Modifier, icon: ImageVector, title: String, subtitle: String) {
    Column(
        modifier = modifier.fillMaxSize().padding(24.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Icon(icon, contentDescription = null, modifier = Modifier.padding(16.dp), tint = MaterialTheme.colorScheme.onSurfaceVariant)
        Text(title, style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold))
        Text(
            subtitle,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            textAlign = TextAlign.Center,
            modifier = Modifier.padding(top = 12.dp),
        )
    }
}
