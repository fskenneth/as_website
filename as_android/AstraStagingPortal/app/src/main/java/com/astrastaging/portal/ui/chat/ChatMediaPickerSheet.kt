package com.astrastaging.portal.ui.chat

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import com.astrastaging.portal.data.media.CaptureMediaType
import com.astrastaging.portal.ui.camera.CameraSheet

/**
 * Camera-only full-screen dialog. Wraps the reusable [CameraSheet] in a
 * [Dialog] sized to the full window and feeds each capture back as raw
 * bytes ready for upload.
 *
 * The gallery side of the picker has been replaced with Android's
 * system Photo Picker (PickVisualMedia), which is permission-free and
 * always exposes the full local library — see ChatScreen.kt's image
 * icon onClick.
 */
@Composable
fun ChatCameraDialog(
    onDismiss: () -> Unit,
    onCaptured: (bytes: ByteArray, fileName: String, mime: String) -> Unit,
) {
    Dialog(
        onDismissRequest = onDismiss,
        properties = DialogProperties(
            usePlatformDefaultWidth = false,
            dismissOnBackPress = true,
            dismissOnClickOutside = false,
        ),
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color.Black),
        ) {
            CameraSheet(
                initialMediaType = CaptureMediaType.PHOTO,
                onClose = onDismiss,
                onCapture = { file, mime, _ ->
                    val bytes = runCatching { file.readBytes() }.getOrNull()
                    if (bytes != null) onCaptured(bytes, file.name, mime)
                },
                modifier = Modifier.fillMaxSize(),
            )
        }
    }
}
