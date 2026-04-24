package com.astrastaging.portal.ui.consultation

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Remove
import androidx.compose.material3.Button
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import com.astrastaging.portal.data.QuoteArea
import com.astrastaging.portal.data.QuoteCatalogItem

/**
 * Modal item picker used for both "Add New Items" and "Remove Existing Items".
 * Tap a row to +1 the quantity; use –/+ icons on the row to step. Running total
 * (add mode only) is shown in the header. Done dismisses.
 *
 * When [action] is "remove" the unit_price is hidden and the running total is
 * also hidden — removes don't affect the quote total.
 */
@Composable
fun ItemPickerDialog(
    title: String,
    action: String, // "add" or "remove"
    catalog: List<QuoteCatalogItem>,
    area: QuoteArea?,
    areaName: String,
    onTapItem: (String, Int) -> Unit, // itemName, delta
    onDismiss: () -> Unit,
) {
    val current = remember(area, action) {
        val src = if (action == "add") area?.add_items.orEmpty() else area?.remove_items.orEmpty()
        src.associate { it.item_name to it.quantity }
    }

    Dialog(
        onDismissRequest = onDismiss,
        properties = DialogProperties(usePlatformDefaultWidth = false),
    ) {
        Column(
            Modifier
                .fillMaxWidth(0.96f)
                .clip(RoundedCornerShape(18.dp))
                .background(MaterialTheme.colorScheme.surface)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            Column {
                Text(
                    title,
                    style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
                )
                Text(
                    areaName,
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }

            if (action == "add") {
                val itemsTotal = area?.items_total ?: 0.0
                val cap = area?.cap ?: 0.0
                val effective = area?.effective ?: 0.0
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(
                        "Items: $${"%.0f".format(itemsTotal)}",
                        style = MaterialTheme.typography.bodyMedium.copy(fontWeight = FontWeight.SemiBold),
                    )
                    Spacer(Modifier.width(10.dp))
                    Text(
                        "Cap: $${"%.0f".format(cap)}",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                    Spacer(Modifier.width(10.dp))
                    Text(
                        "Charge: $${"%.0f".format(effective)}",
                        style = MaterialTheme.typography.bodyMedium.copy(fontWeight = FontWeight.SemiBold),
                        color = MaterialTheme.colorScheme.primary,
                    )
                }
            }

            LazyColumn(
                modifier = Modifier.heightIn(min = 120.dp, max = 520.dp),
                verticalArrangement = Arrangement.spacedBy(4.dp),
                contentPadding = PaddingValues(vertical = 4.dp),
            ) {
                items(items = catalog, key = { it: QuoteCatalogItem -> it.name }) { item ->
                    val qty: Int = current[item.name] ?: 0
                    ItemPickerRow(
                        name = item.name,
                        showPrice = action == "add",
                        unitPrice = item.unit_price,
                        quantity = qty,
                        onTap = { onTapItem(item.name, +1) },
                        onMinus = { onTapItem(item.name, -1) },
                    )
                }
            }

            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.End) {
                Button(onClick = onDismiss) {
                    Text("Done")
                }
            }
        }
    }
}

@Composable
private fun ItemPickerRow(
    name: String,
    showPrice: Boolean,
    unitPrice: Double,
    quantity: Int,
    onTap: () -> Unit,
    onMinus: () -> Unit,
) {
    val bg = if (quantity > 0) MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.35f)
             else MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.4f)
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(10.dp))
            .background(bg)
            .clickable { onTap() }
            .padding(horizontal = 12.dp, vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Column(Modifier.weight(1f)) {
            Text(
                name,
                style = MaterialTheme.typography.bodyMedium.copy(fontWeight = FontWeight.SemiBold),
            )
            if (showPrice) {
                Text(
                    "$${"%.0f".format(unitPrice)} ea",
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }

        if (quantity > 0) {
            IconButton(
                onClick = onMinus,
                modifier = Modifier.size(32.dp),
            ) {
                Icon(Icons.Filled.Remove, contentDescription = "Decrease", modifier = Modifier.size(18.dp))
            }
            Box(
                modifier = Modifier
                    .size(30.dp)
                    .clip(CircleShape)
                    .background(MaterialTheme.colorScheme.primary),
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    quantity.toString(),
                    style = MaterialTheme.typography.labelLarge.copy(fontWeight = FontWeight.Bold),
                    color = MaterialTheme.colorScheme.onPrimary,
                )
            }
            Spacer(Modifier.width(4.dp))
        }
        IconButton(
            onClick = onTap,
            modifier = Modifier.size(32.dp),
        ) {
            Icon(Icons.Filled.Add, contentDescription = "Increase", modifier = Modifier.size(20.dp))
        }
    }
}
