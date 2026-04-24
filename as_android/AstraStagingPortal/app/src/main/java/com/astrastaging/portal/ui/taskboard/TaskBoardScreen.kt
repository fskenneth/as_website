package com.astrastaging.portal.ui.taskboard

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.IntrinsicSize
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CalendarToday
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.outlined.Brush
import androidx.compose.material.icons.outlined.Circle
import androidx.compose.material.icons.outlined.ExpandLess
import androidx.compose.material.icons.outlined.ExpandMore
import androidx.compose.material.icons.outlined.LocalShipping
import androidx.compose.material.icons.outlined.Person
import androidx.compose.material.icons.outlined.Schedule
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextField
import androidx.compose.material3.TextFieldDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.derivedStateOf
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.text.withStyle
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.lifecycle.viewmodel.initializer
import androidx.lifecycle.viewmodel.viewModelFactory
import com.astrastaging.portal.data.ApiUser
import com.astrastaging.portal.data.Milestone
import com.astrastaging.portal.data.Person
import com.astrastaging.portal.data.Staging
import java.text.NumberFormat
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import java.util.Locale

/** Webapp's --accent rose #E11D48 — matches the "Task Board" word and active-toggle highlight. */
private val AccentRose = Color(0xFFE11D48)

@Composable
fun TaskBoardScreen(user: ApiUser, token: String, modifier: Modifier = Modifier) {
    val vm: TaskBoardViewModel = viewModel(
        key = "task-board-$token",
        factory = viewModelFactory { initializer { TaskBoardViewModel(token) } },
    )
    val state by vm.state.collectAsStateWithLifecycle()
    var search by remember { mutableStateOf("") }
    var searchOpen by remember { mutableStateOf(false) }

    LaunchedEffect(Unit) { vm.load() }

    val filtered by remember(state.stagings, search) {
        derivedStateOf { filterStagings(state.stagings, search) }
    }

    Column(modifier = modifier.fillMaxSize()) {
        HeaderBanner(
            period = state.period,
            mine = state.mine,
            count = filtered.size,
            search = search,
            searchOpen = searchOpen,
            onPeriodChange = vm::setPeriod,
            onMineToggle = { vm.setMine(!state.mine) },
            onSearchChange = { search = it },
            onSearchToggle = {
                // If the field is already visible with no query, tapping hides it.
                // Otherwise open it; the field itself handles focus on appear.
                searchOpen = !(searchOpen && search.isEmpty())
            },
            onSearchClose = {
                search = ""
                searchOpen = false
            },
        )
        when {
            state.isLoading && state.stagings.isEmpty() -> LoadingState()
            state.error != null && state.stagings.isEmpty() -> ErrorState(state.error!!, onRetry = vm::load)
            filtered.isEmpty() -> EmptyState(hasSearch = search.isNotBlank())
            else -> StagingList(
                stagings = filtered,
                serverToday = state.serverToday,
                period = state.period,
                togglingField = state.togglingField,
                onToggleMilestone = vm::toggleMilestone,
            )
        }
    }
}

@Composable
private fun HeaderBanner(
    period: TaskPeriod,
    mine: Boolean,
    count: Int,
    search: String,
    searchOpen: Boolean,
    onPeriodChange: (TaskPeriod) -> Unit,
    onMineToggle: () -> Unit,
    onSearchChange: (String) -> Unit,
    onSearchToggle: () -> Unit,
    onSearchClose: () -> Unit,
) {
    val showSearch = searchOpen || search.isNotEmpty()
    Column(
        Modifier
            .fillMaxWidth()
            .background(MaterialTheme.colorScheme.surface)
            .padding(horizontal = 16.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        // Title: "Staging " + "Task Board" (accent)
        Text(
            text = titleAnnotated(),
            style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold),
        )

        // Controls: date range on left; my tasks + search toggle anchored right so
        // the changing stagings-count text can't nudge them.
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .height(IntrinsicSize.Min),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            RangePill(period = period, count = count, onChange = onPeriodChange)
            Spacer(Modifier.weight(1f))
            MineToggle(mine = mine, onToggle = onMineToggle)
            Spacer(Modifier.width(8.dp))
            SearchTogglePill(
                active = showSearch,
                onClick = onSearchToggle,
                modifier = Modifier.fillMaxHeight(),
            )
        }

        // Search — only rendered when the user opens it (or has a query).
        if (showSearch) {
            SearchField(
                value = search,
                onChange = onSearchChange,
                onClose = onSearchClose,
                autoFocus = searchOpen,
            )
        }
    }
}

@Composable
private fun SearchTogglePill(active: Boolean, onClick: () -> Unit, modifier: Modifier = Modifier) {
    val bg = if (active) AccentRose.copy(alpha = 0.12f) else MaterialTheme.colorScheme.surfaceVariant
    val border = if (active) AccentRose else MaterialTheme.colorScheme.outlineVariant
    val borderWidth = if (active) 1.dp else 0.5.dp
    val fg = if (active) AccentRose else MaterialTheme.colorScheme.onSurface
    Row(
        modifier = modifier
            .clip(RoundedCornerShape(50))
            .background(bg)
            .border(borderWidth, border, RoundedCornerShape(50))
            .clickable { onClick() }
            .padding(horizontal = 12.dp, vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(
            Icons.Filled.Search,
            contentDescription = if (active) "Close search" else "Open search",
            modifier = Modifier.size(14.dp),
            tint = fg,
        )
    }
}

private fun titleAnnotated(): AnnotatedString = buildAnnotatedString {
    append("Staging ")
    withStyle(SpanStyle(color = AccentRose)) { append("Task Board") }
}

@Composable
private fun RangePill(
    period: TaskPeriod,
    count: Int,
    onChange: (TaskPeriod) -> Unit,
) {
    var open by remember { mutableStateOf(false) }
    Box {
        Row(
            modifier = Modifier
                .clip(RoundedCornerShape(50))
                .background(MaterialTheme.colorScheme.surfaceVariant)
                .border(0.5.dp, MaterialTheme.colorScheme.outlineVariant, RoundedCornerShape(50))
                .clickable { open = true }
                .padding(horizontal = 12.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Icon(
                Icons.Filled.CalendarToday,
                contentDescription = null,
                modifier = Modifier.size(14.dp),
                tint = MaterialTheme.colorScheme.onSurface,
            )
            Spacer(Modifier.width(6.dp))
            Text(
                text = rangeLabelAnnotated(count, period),
                style = MaterialTheme.typography.bodyMedium,
            )
        }
        DropdownMenu(expanded = open, onDismissRequest = { open = false }) {
            TaskPeriod.BANNER_CHOICES.forEach { p ->
                DropdownMenuItem(
                    text = {
                        val marker = if (p == period) "✓  " else "    "
                        Text("$marker${p.menuLabel}")
                    },
                    onClick = {
                        open = false
                        if (p != period) onChange(p)
                    },
                )
            }
        }
    }
}

private fun rangeLabelAnnotated(count: Int, period: TaskPeriod): AnnotatedString = buildAnnotatedString {
    withStyle(SpanStyle(color = AccentRose, fontWeight = FontWeight.SemiBold)) {
        append(count.toString())
    }
    append(" stagings · ")
    append(period.phrase)
}

@Composable
private fun MineToggle(mine: Boolean, onToggle: () -> Unit) {
    val bg = if (mine) AccentRose.copy(alpha = 0.12f) else MaterialTheme.colorScheme.surfaceVariant
    val border = if (mine) AccentRose else MaterialTheme.colorScheme.outlineVariant
    val borderWidth = if (mine) 1.dp else 0.5.dp
    val fg = if (mine) AccentRose else MaterialTheme.colorScheme.onSurface
    Row(
        modifier = Modifier
            .clip(RoundedCornerShape(50))
            .background(bg)
            .border(borderWidth, border, RoundedCornerShape(50))
            .clickable { onToggle() }
            .padding(horizontal = 12.dp, vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(
            Icons.Outlined.Person,
            contentDescription = null,
            modifier = Modifier.size(14.dp),
            tint = fg,
        )
        Spacer(Modifier.width(4.dp))
        Text("My tasks", style = MaterialTheme.typography.bodyMedium, color = fg)
    }
}

@Composable
private fun SearchField(
    value: String,
    onChange: (String) -> Unit,
    onClose: () -> Unit,
    autoFocus: Boolean,
) {
    val focusRequester = remember { FocusRequester() }
    LaunchedEffect(autoFocus) {
        if (autoFocus) focusRequester.requestFocus()
    }
    TextField(
        value = value,
        onValueChange = onChange,
        modifier = Modifier
            .fillMaxWidth()
            .focusRequester(focusRequester),
        placeholder = {
            Text(
                "Search address, person, date, notes",
                style = MaterialTheme.typography.bodyMedium,
                maxLines = 1,
                softWrap = false,
                overflow = TextOverflow.Ellipsis,
            )
        },
        leadingIcon = {
            Icon(Icons.Filled.Search, contentDescription = null, modifier = Modifier.size(18.dp))
        },
        trailingIcon = {
            Icon(
                Icons.Filled.Close,
                contentDescription = "Close search",
                modifier = Modifier
                    .size(18.dp)
                    .clickable { onClose() },
            )
        },
        singleLine = true,
        shape = RoundedCornerShape(10.dp),
        keyboardOptions = KeyboardOptions(imeAction = ImeAction.Search),
        colors = TextFieldDefaults.colors(
            focusedContainerColor = MaterialTheme.colorScheme.surfaceVariant,
            unfocusedContainerColor = MaterialTheme.colorScheme.surfaceVariant,
            disabledContainerColor = MaterialTheme.colorScheme.surfaceVariant,
            focusedIndicatorColor = Color.Transparent,
            unfocusedIndicatorColor = Color.Transparent,
            disabledIndicatorColor = Color.Transparent,
        ),
    )
}

@Composable
private fun LoadingState() {
    Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
        CircularProgressIndicator()
    }
}

@Composable
private fun EmptyState(hasSearch: Boolean) {
    Column(
        Modifier.fillMaxSize().padding(32.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text(
            if (hasSearch) "No stagings match your search" else "No stagings for this period",
            style = MaterialTheme.typography.titleMedium,
        )
        Text(
            if (hasSearch) "Try a wider range, clear the search, or toggle My tasks off."
            else "Try a different date range or toggle My tasks off.",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            textAlign = TextAlign.Center,
            modifier = Modifier.padding(top = 6.dp),
        )
    }
}

@Composable
private fun ErrorState(message: String, onRetry: () -> Unit) {
    Column(
        Modifier.fillMaxSize().padding(32.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text("Couldn't load", style = MaterialTheme.typography.titleMedium)
        Text(message, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant, textAlign = TextAlign.Center, modifier = Modifier.padding(vertical = 8.dp))
        Button(onClick = onRetry) { Text("Retry") }
    }
}

private fun filterStagings(stagings: List<Staging>, search: String): List<Staging> {
    val query = search.trim().lowercase()
    if (query.isEmpty()) return stagings
    val tokens = query.split(Regex("\\s+")).filter { it.isNotEmpty() }
    return stagings.filter { s ->
        val people = (s.stagers + s.staging_movers + s.destaging_movers)
            .mapNotNull { it.name }
            .joinToString(" ")
        val parts = listOfNotNull(
            s.address, s.name, s.staging_date, s.destaging_date,
            s.property_type, s.occupancy, s.staging_type, s.status,
            s.general_notes, s.moving_instructions, s.mls,
            s.customer.fullName, s.customer.email, s.customer.phone,
            s.staging_eta, s.destaging_eta, people,
        )
        val haystack = parts.joinToString(" ").lowercase()
        tokens.all { haystack.contains(it) }
    }
}

@Composable
private fun StagingList(
    stagings: List<Staging>,
    serverToday: String,
    period: TaskPeriod,
    togglingField: Pair<String, String>?,
    onToggleMilestone: (String, String, Boolean) -> Unit,
) {
    val grouped = remember(stagings, period) {
        val byDate = stagings.groupBy { it.staging_date ?: "—" }
        val entries = byDate.entries.toList()
        val sorted = if (period == TaskPeriod.PAST || period == TaskPeriod.ALL) {
            entries.sortedByDescending { it.key }
        } else {
            entries.sortedBy { it.key }
        }
        sorted.map { it.key to it.value }
    }

    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(12.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        grouped.forEach { (dateKey, group) ->
            item(key = "header-$dateKey") {
                Text(
                    prettyDate(dateKey),
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.padding(start = 4.dp, top = 8.dp, bottom = 2.dp),
                )
            }
            items(group, key = { it.id }) { staging ->
                StagingCard(
                    staging = staging,
                    serverToday = serverToday,
                    togglingField = togglingField,
                    onToggleMilestone = onToggleMilestone,
                )
            }
        }
    }
}

@Composable
private fun StagingCard(
    staging: Staging,
    serverToday: String,
    togglingField: Pair<String, String>?,
    onToggleMilestone: (String, String, Boolean) -> Unit,
) {
    var expanded by remember { mutableStateOf(false) }
    val isToday = staging.staging_date == serverToday
    val bg = if (isToday) Color(0xFFFFF4C2) else MaterialTheme.colorScheme.surfaceVariant
    val borderColor = if (isToday) Color(0xFFE58E00) else Color(0xFFD0D0D0)
    val borderWidth = if (isToday) 1.5.dp else 0.5.dp

    Column(
        Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(bg)
            .border(borderWidth, borderColor, RoundedCornerShape(12.dp))
            .padding(14.dp),
    ) {
        Header(staging)
        Spacer(Modifier.height(6.dp))
        AddressRow(staging)
        if (staging.stagers.isNotEmpty() || staging.staging_movers.isNotEmpty()) {
            Spacer(Modifier.height(6.dp))
            if (staging.stagers.isNotEmpty()) PeopleRow("Stager", Icons.Outlined.Brush, staging.stagers)
            if (staging.staging_movers.isNotEmpty()) PeopleRow("Movers", Icons.Outlined.LocalShipping, staging.staging_movers)
        }
        Spacer(Modifier.height(8.dp))
        MilestonesRow(staging, togglingField, onToggleMilestone)
        if (expanded) {
            Spacer(Modifier.height(8.dp))
            ExpandedDetails(staging)
        }
        Row(
            modifier = Modifier.fillMaxWidth().padding(top = 6.dp).clickable { expanded = !expanded },
            horizontalArrangement = Arrangement.Center,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(if (expanded) "Less" else "More", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
            Icon(
                if (expanded) Icons.Outlined.ExpandLess else Icons.Outlined.ExpandMore,
                contentDescription = null,
                modifier = Modifier.size(16.dp),
                tint = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

@Composable
private fun Header(staging: Staging) {
    Row(verticalAlignment = Alignment.CenterVertically) {
        if (!staging.staging_eta.isNullOrEmpty()) {
            Icon(Icons.Outlined.Schedule, contentDescription = null, modifier = Modifier.size(14.dp), tint = MaterialTheme.colorScheme.onSurfaceVariant)
            Text(" ${staging.staging_eta}", style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
        Spacer(Modifier.weight(1f))
        Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
            if (!staging.occupancy.isNullOrEmpty()) {
                Badge(staging.occupancy, if (staging.occupancy.lowercase() == "vacant") Color(0xFFE58E00) else Color(0xFF1976D2))
            }
            if (!staging.staging_type.isNullOrEmpty() && staging.staging_type != "Regular") {
                Badge(staging.staging_type, Color(0xFF7B1FA2))
            }
            if (!staging.status.isNullOrEmpty()) {
                val c = when (staging.status.lowercase()) {
                    "active" -> Color(0xFF388E3C)
                    "inquired" -> Color(0xFF616161)
                    else -> Color(0xFF757575)
                }
                Badge(staging.status, c)
            }
        }
    }
}

@Composable
private fun Badge(text: String, color: Color) {
    Text(
        text,
        style = MaterialTheme.typography.labelSmall.copy(fontSize = 10.sp),
        color = color,
        modifier = Modifier
            .clip(RoundedCornerShape(50))
            .background(color.copy(alpha = 0.18f))
            .padding(horizontal = 8.dp, vertical = 3.dp),
    )
}

@Composable
private fun AddressRow(staging: Staging) {
    Column {
        Text(staging.address ?: staging.name ?: "Untitled", style = MaterialTheme.typography.bodyMedium.copy(fontWeight = FontWeight.SemiBold))
        if (!staging.property_type.isNullOrEmpty()) {
            Text(staging.property_type, style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
    }
}

@Composable
private fun PeopleRow(label: String, icon: ImageVector, people: List<Person>) {
    Row(verticalAlignment = Alignment.Top, modifier = Modifier.padding(vertical = 1.dp)) {
        Icon(icon, contentDescription = null, modifier = Modifier.size(14.dp).padding(top = 2.dp), tint = MaterialTheme.colorScheme.onSurfaceVariant)
        Text(
            " $label ",
            style = MaterialTheme.typography.labelMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.width(62.dp),
        )
        Text(
            people.mapNotNull { it.name }.joinToString(", "),
            style = MaterialTheme.typography.labelMedium,
            maxLines = 2,
        )
    }
}

@Composable
private fun MilestonesRow(
    staging: Staging,
    togglingField: Pair<String, String>?,
    onToggleMilestone: (String, String, Boolean) -> Unit,
) {
    Row(
        modifier = Modifier.horizontalScroll(rememberScrollState()),
        horizontalArrangement = Arrangement.spacedBy(6.dp),
    ) {
        MILESTONE_DEFS.forEach { def ->
            val m = staging.milestones.forField(def.field)
            val busy = togglingField?.first == staging.id && togglingField.second == def.field
            MilestoneChip(
                label = def.label,
                m = m,
                busy = busy,
                onClick = { onToggleMilestone(staging.id, def.field, m.done) },
            )
        }
    }
}

@Composable
private fun MilestoneChip(label: String, m: Milestone, busy: Boolean, onClick: () -> Unit) {
    val done = m.done
    val color = if (done) Color(0xFF2E7D32) else MaterialTheme.colorScheme.onSurfaceVariant
    val bg = if (done) Color(0xFF2E7D32).copy(alpha = 0.18f) else MaterialTheme.colorScheme.surface
    Row(
        modifier = Modifier
            .clip(RoundedCornerShape(50))
            .background(bg)
            .clickable(enabled = !busy) { onClick() }
            .padding(horizontal = 10.dp, vertical = 5.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        if (busy) {
            CircularProgressIndicator(modifier = Modifier.size(10.dp), strokeWidth = 1.5.dp, color = color)
        } else {
            Icon(
                if (done) Icons.Filled.CheckCircle else Icons.Outlined.Circle,
                contentDescription = null,
                modifier = Modifier.size(12.dp),
                tint = color,
            )
        }
        Text(
            "  $label${m.date?.let { "  ${shortDate(it)}" } ?: ""}",
            style = MaterialTheme.typography.labelSmall,
            color = color,
        )
    }
}

@Composable
private fun ExpandedDetails(staging: Staging) {
    Column(Modifier.fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
        KV("Customer", staging.customer.fullName)
        if (!staging.customer.phone.isNullOrEmpty()) KV("Phone", staging.customer.phone)
        if (!staging.customer.email.isNullOrEmpty()) KV("Email", staging.customer.email)

        if (staging.fees.total > 0 || staging.fees.owing > 0) {
            Spacer(Modifier.height(4.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(18.dp)) {
                FeeBlock("Fee", staging.fees.total)
                FeeBlock("Paid", staging.fees.paid)
                FeeBlock("Owing", staging.fees.owing, highlight = staging.fees.owing > 0)
            }
        }
        if (!staging.destaging_date.isNullOrEmpty()) {
            val eta = staging.destaging_eta?.let { " · $it" } ?: ""
            KV("Destaging", staging.destaging_date + eta)
        }
        if (!staging.moving_instructions.isNullOrEmpty()) NoteBlock("Moving Instructions", staging.moving_instructions, Color(0xFF1976D2))
        if (!staging.general_notes.isNullOrEmpty()) NoteBlock("General Notes", staging.general_notes, Color(0xFF616161))
        if (!staging.mls.isNullOrEmpty()) KV("MLS", staging.mls)
    }
}

@Composable
private fun KV(k: String, v: String) {
    Row(modifier = Modifier.fillMaxWidth(), verticalAlignment = Alignment.Top) {
        Text(k, style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.onSurfaceVariant, modifier = Modifier.width(80.dp))
        Text(v, style = MaterialTheme.typography.labelMedium, modifier = Modifier.weight(1f))
    }
}

@Composable
private fun FeeBlock(label: String, amount: Double, highlight: Boolean = false) {
    Column {
        Text(label, style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Text(
            currency(amount),
            style = MaterialTheme.typography.bodyMedium.copy(fontWeight = FontWeight.SemiBold),
            color = if (highlight) Color(0xFFD32F2F) else MaterialTheme.colorScheme.onSurface,
        )
    }
}

@Composable
private fun NoteBlock(label: String, text: String, color: Color) {
    Column(Modifier.fillMaxWidth()) {
        Text(label, style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Text(
            text,
            style = MaterialTheme.typography.labelMedium,
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(6.dp))
                .background(color.copy(alpha = 0.08f))
                .padding(8.dp),
        )
    }
}

private fun prettyDate(iso: String): String {
    if (iso == "—") return iso
    return try {
        val d = LocalDate.parse(iso)
        d.format(DateTimeFormatter.ofPattern("EEE, MMM d, yyyy", Locale.getDefault()))
    } catch (_: Throwable) {
        iso
    }
}

private fun shortDate(iso: String): String {
    return try {
        val d = LocalDate.parse(iso)
        d.format(DateTimeFormatter.ofPattern("MMM d", Locale.getDefault()))
    } catch (_: Throwable) {
        iso
    }
}

private fun currency(v: Double): String {
    val f = NumberFormat.getCurrencyInstance(Locale.CANADA)
    f.maximumFractionDigits = 0
    return f.format(v)
}
