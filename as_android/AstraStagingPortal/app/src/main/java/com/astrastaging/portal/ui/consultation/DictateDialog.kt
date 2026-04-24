package com.astrastaging.portal.ui.consultation

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Close
import androidx.compose.material.icons.outlined.Send
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardCapitalization
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import com.astrastaging.portal.data.ApiClient
import com.astrastaging.portal.data.DictationRecord
import kotlinx.coroutines.launch

/**
 * Review-only dialog for a completed dictation. Recording + upload are
 * handled upstream by DictationController; by the time this is shown the
 * server already owns the audio, transcript, and summary. The stager can
 * edit the draft emails and send them via Mailgun.
 */
@Composable
fun DictateDialog(
    dictation: DictationRecord,
    customerEmailOnFile: String?,
    token: String,
    onDismiss: () -> Unit,
) {
    val scope = rememberCoroutineScope()

    var customerEmailTo by remember { mutableStateOf(customerEmailOnFile ?: "") }
    var customerSubject by remember { mutableStateOf(dictation.summary?.customer_email_subject ?: "") }
    var customerBody by remember { mutableStateOf(dictation.summary?.customer_email_body ?: "") }
    var salesSubject by remember { mutableStateOf(dictation.summary?.sales_rep_email_subject ?: "") }
    var salesBody by remember { mutableStateOf(dictation.summary?.sales_rep_email_body ?: "") }
    var sendingRecipient by remember { mutableStateOf<String?>(null) }
    var sendError by remember { mutableStateOf<String?>(null) }
    var sentConfirmation by remember { mutableStateOf<String?>(null) }

    fun send(recipient: String) {
        sendingRecipient = recipient
        sendError = null
        sentConfirmation = null
        scope.launch {
            try {
                val resp = ApiClient.sendDictationEmail(
                    dictationId = dictation.id,
                    recipient = recipient,
                    toCustomer = customerEmailTo,
                    customerSubject = customerSubject,
                    customerBody = customerBody,
                    salesRepSubject = salesSubject,
                    salesRepBody = salesBody,
                    token = token,
                )
                if (resp.ok) {
                    val names = resp.sent.joinToString(" + ") {
                        it.recipient.replace("_", " ")
                    }
                    sentConfirmation = "Sent to $names."
                } else {
                    sendError = resp.errors.joinToString("\n")
                }
            } catch (t: Throwable) {
                sendError = t.message ?: "Send failed"
            } finally {
                sendingRecipient = null
            }
        }
    }

    Dialog(
        onDismissRequest = onDismiss,
        properties = DialogProperties(
            dismissOnBackPress = true,
            dismissOnClickOutside = false,
            usePlatformDefaultWidth = false,
        ),
    ) {
        Surface(
            modifier = Modifier.fillMaxSize().padding(12.dp),
            shape = RoundedCornerShape(18.dp),
            color = MaterialTheme.colorScheme.background,
        ) {
            Column(Modifier.fillMaxSize()) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 12.dp, vertical = 8.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text(
                        "Dictation",
                        style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
                        modifier = Modifier.weight(1f),
                    )
                    IconButton(onClick = onDismiss) {
                        Icon(Icons.Outlined.Close, contentDescription = "Close")
                    }
                }
                HorizontalDivider()

                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .verticalScroll(rememberScrollState())
                        .padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp),
                ) {
                    dictation.error?.takeIf { it.isNotBlank() }?.let {
                        Text(it, color = MaterialTheme.colorScheme.error,
                            style = MaterialTheme.typography.bodySmall)
                    }
                    dictation.summary?.key_points?.takeIf { it.isNotEmpty() }?.let { pts ->
                        SectionHeader("Key points")
                        pts.forEach { p ->
                            Row {
                                Text("• ", color = MaterialTheme.colorScheme.onSurfaceVariant)
                                Text(p, style = MaterialTheme.typography.bodyMedium)
                            }
                        }
                    }
                    dictation.summary?.suggested_quote_lines?.takeIf { it.isNotEmpty() }?.let { lines ->
                        SectionHeader("Suggested quote items")
                        lines.forEach { line ->
                            Text("– ${line.description}", style = MaterialTheme.typography.bodyMedium)
                        }
                    }

                    SectionHeader("Customer email")
                    OutlinedTextField(
                        value = customerEmailTo,
                        onValueChange = { customerEmailTo = it },
                        label = { Text("Customer email") },
                        singleLine = true,
                        keyboardOptions = KeyboardOptions(capitalization = KeyboardCapitalization.None),
                        modifier = Modifier.fillMaxWidth(),
                    )
                    OutlinedTextField(
                        value = customerSubject,
                        onValueChange = { customerSubject = it },
                        label = { Text("Subject") },
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth(),
                    )
                    OutlinedTextField(
                        value = customerBody,
                        onValueChange = { customerBody = it },
                        label = { Text("Body") },
                        modifier = Modifier.fillMaxWidth().heightIn(min = 140.dp),
                    )
                    Button(
                        onClick = { send("customer") },
                        enabled = sendingRecipient == null &&
                            customerEmailTo.isNotBlank() &&
                            customerSubject.isNotBlank() &&
                            customerBody.isNotBlank(),
                        modifier = Modifier.fillMaxWidth(),
                    ) {
                        if (sendingRecipient == "customer") {
                            CircularProgressIndicator(modifier = Modifier.size(18.dp), strokeWidth = 2.dp)
                        } else {
                            Icon(Icons.Outlined.Send, contentDescription = null, modifier = Modifier.size(16.dp))
                            Spacer(Modifier.width(6.dp))
                            Text("Send to Customer")
                        }
                    }

                    SectionHeader("Internal note to sales@astrastaging.com")
                    OutlinedTextField(
                        value = salesSubject,
                        onValueChange = { salesSubject = it },
                        label = { Text("Subject") },
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth(),
                    )
                    OutlinedTextField(
                        value = salesBody,
                        onValueChange = { salesBody = it },
                        label = { Text("Body") },
                        modifier = Modifier.fillMaxWidth().heightIn(min = 120.dp),
                    )
                    Button(
                        onClick = { send("sales_rep") },
                        enabled = sendingRecipient == null &&
                            salesSubject.isNotBlank() &&
                            salesBody.isNotBlank(),
                        modifier = Modifier.fillMaxWidth(),
                    ) {
                        if (sendingRecipient == "sales_rep") {
                            CircularProgressIndicator(modifier = Modifier.size(18.dp), strokeWidth = 2.dp)
                        } else {
                            Icon(Icons.Outlined.Send, contentDescription = null, modifier = Modifier.size(16.dp))
                            Spacer(Modifier.width(6.dp))
                            Text("Send to Sales Rep")
                        }
                    }

                    HorizontalDivider(Modifier.padding(vertical = 4.dp))
                    Button(
                        onClick = { send("both") },
                        enabled = sendingRecipient == null,
                        modifier = Modifier.fillMaxWidth().height(48.dp),
                    ) {
                        if (sendingRecipient == "both") {
                            CircularProgressIndicator(modifier = Modifier.size(18.dp), strokeWidth = 2.dp)
                        } else {
                            Icon(Icons.Outlined.Send, contentDescription = null)
                            Spacer(Modifier.width(6.dp))
                            Text("Send BOTH emails")
                        }
                    }
                    sentConfirmation?.let {
                        Text(it, color = Color(0xFF2E7D32), style = MaterialTheme.typography.bodySmall)
                    }
                    sendError?.let {
                        Text(it, color = MaterialTheme.colorScheme.error, style = MaterialTheme.typography.bodySmall)
                    }

                    dictation.transcript.takeIf { it.isNotBlank() }?.let { t ->
                        SectionHeader("Raw transcript")
                        Text(t, style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                }
            }
        }
    }
}

@Composable
private fun SectionHeader(text: String) {
    Text(
        text.uppercase(),
        style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.SemiBold),
        color = MaterialTheme.colorScheme.onSurfaceVariant,
    )
}
