package com.astrastaging.portal.ui.chat

import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.StrokeJoin
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.graphics.vector.path
import androidx.compose.ui.unit.dp

/**
 * "Compose" / new-message icon — open square with a pencil overlapping the
 * top-right corner. Cross-platform match for iOS's `square.and.pencil`
 * (SF Symbol) and the inline SVG used by the web chat panel. Built by
 * hand because Material Icons Extended doesn't ship `EditSquare`.
 */
val ChatComposeIcon: ImageVector by lazy {
    ImageVector.Builder(
        name = "ChatCompose",
        defaultWidth = 24.dp,
        defaultHeight = 24.dp,
        viewportWidth = 24f,
        viewportHeight = 24f,
    ).apply {
        // Square: drawn with a notched top-right corner so the pencil
        // appears to "land" on its edge.
        path(
            stroke = SolidColor(Color.Unspecified),  // tinted by Icon()
            fill = null,
            strokeLineWidth = 2f,
            strokeLineCap = StrokeCap.Round,
            strokeLineJoin = StrokeJoin.Round,
        ) {
            moveTo(11f, 4f)
            horizontalLineTo(4f)
            curveToRelative(-1.1f, 0f, -2f, 0.9f, -2f, 2f)
            verticalLineToRelative(14f)
            curveToRelative(0f, 1.1f, 0.9f, 2f, 2f, 2f)
            horizontalLineToRelative(14f)
            curveToRelative(1.1f, 0f, 2f, -0.9f, 2f, -2f)
            verticalLineToRelative(-7f)
        }
        // Pencil overlapping the top-right corner.
        path(
            stroke = SolidColor(Color.Unspecified),
            fill = null,
            strokeLineWidth = 2f,
            strokeLineCap = StrokeCap.Round,
            strokeLineJoin = StrokeJoin.Round,
        ) {
            moveTo(18.5f, 2.5f)
            curveToRelative(0.83f, -0.83f, 2.17f, -0.83f, 3f, 0f)
            curveToRelative(0.83f, 0.83f, 0.83f, 2.17f, 0f, 3f)
            lineTo(12f, 15f)
            lineTo(8f, 16f)
            lineToRelative(1f, -4f)
            lineTo(18.5f, 2.5f)
            close()
        }
    }.build()
}
