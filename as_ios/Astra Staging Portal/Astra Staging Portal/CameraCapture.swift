//
//  CameraCapture.swift
//  Astra Staging Portal
//
//  Thin SwiftUI wrapper around UIImagePickerController for photo and
//  video capture. We explicitly set the camera to the rear .wide mode
//  so users start on the default lens; they can still tap the 0.5×
//  button in the native picker if they want the ultrawide look.
//
//  The native camera UI is preferred here over a custom AVCapture
//  pipeline because:
//    - native UI gives the stager panorama, HDR, flash, and Live Photo
//      out of the box — all useful for the consultation workflow.
//    - our downscaling runs after capture on the resulting file, so the
//      raw-camera surface doesn't need to live in-app.
//
//  After capture we downscale images and re-encode video to 720p so
//  uploads stay small (a full iPhone 15 photo is ~5 MB; we aim for
//  ~400 KB).
//

import AVFoundation
import SwiftUI
import UIKit

enum CapturedMedia {
    case image(url: URL, mimeType: String)
    case video(url: URL, mimeType: String)
}

struct CameraPicker: UIViewControllerRepresentable {
    enum Mode {
        case photo
        case video
    }

    let mode: Mode
    let onFinish: (CapturedMedia?) -> Void

    func makeCoordinator() -> Coordinator { Coordinator(onFinish: onFinish) }

    func makeUIViewController(context: Context) -> UIImagePickerController {
        let picker = UIImagePickerController()
        picker.delegate = context.coordinator

        if UIImagePickerController.isSourceTypeAvailable(.camera) {
            picker.sourceType = .camera
            picker.cameraDevice = .rear
            // Default flash = auto so low-light consult photos aren't a mess.
            if UIImagePickerController.isFlashAvailable(for: .rear) {
                picker.cameraFlashMode = .auto
            }
        } else {
            // Simulator fallback so the UI is at least previewable.
            picker.sourceType = .photoLibrary
        }

        switch mode {
        case .photo:
            picker.mediaTypes = ["public.image"]
            picker.cameraCaptureMode = .photo
        case .video:
            picker.mediaTypes = ["public.movie"]
            picker.cameraCaptureMode = .video
            // Medium keeps the file manageable; we re-encode afterward anyway.
            picker.videoQuality = .typeMedium
            picker.videoMaximumDuration = 120  // 2 min cap
        }
        picker.allowsEditing = false
        picker.modalPresentationStyle = .fullScreen
        return picker
    }

    func updateUIViewController(_ uiViewController: UIImagePickerController, context: Context) {}

    final class Coordinator: NSObject, UIImagePickerControllerDelegate, UINavigationControllerDelegate {
        let onFinish: (CapturedMedia?) -> Void

        init(onFinish: @escaping (CapturedMedia?) -> Void) {
            self.onFinish = onFinish
        }

        func imagePickerControllerDidCancel(_ picker: UIImagePickerController) {
            picker.dismiss(animated: true) { [onFinish] in onFinish(nil) }
        }

        func imagePickerController(
            _ picker: UIImagePickerController,
            didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey: Any]
        ) {
            let result = Self.extract(info: info)
            picker.dismiss(animated: true) { [onFinish] in onFinish(result) }
        }

        private static func extract(info: [UIImagePickerController.InfoKey: Any]) -> CapturedMedia? {
            if let videoURL = info[.mediaURL] as? URL {
                return .video(url: videoURL, mimeType: "video/quicktime")
            }
            if let image = info[.originalImage] as? UIImage {
                guard let url = MediaProcessor.writePhoto(image) else { return nil }
                return .image(url: url, mimeType: "image/jpeg")
            }
            return nil
        }
    }
}

// MARK: - Media Processing (downscale + compress)

enum MediaProcessor {
    /// Photos are center-cropped to 4:3 and scaled so the long edge is 1920 px
    /// (i.e. landscape = 1920×1440, portrait = 1440×1920). Matches the Zoho
    /// ingestion expectation that all staging photos are consistently 4:3.
    private static let photoLongEdge: CGFloat = 1920
    private static let photoShortEdge: CGFloat = 1440
    private static let photoJPEGQuality: CGFloat = 0.7
    private static let videoExportPreset = AVAssetExportPreset1280x720

    /// Writes a 4:3 JPEG at ~1920×1440 (long edge) / quality 0.7 into the
    /// app's tmp directory. Returns nil if encoding fails.
    static func writePhoto(_ image: UIImage) -> URL? {
        let processed = cropAndScale(image)
        guard let data = processed.jpegData(compressionQuality: photoJPEGQuality) else { return nil }
        let url = FileManager.default.temporaryDirectory
            .appendingPathComponent("capture-\(UUID().uuidString).jpg")
        do {
            try data.write(to: url, options: .atomic)
            return url
        } catch {
            return nil
        }
    }

    /// Center-crop to 4:3 (preserving orientation), then scale so the long
    /// edge = 1920.
    private static func cropAndScale(_ image: UIImage) -> UIImage {
        // Normalise the orientation first so Core Graphics draws the pixels
        // the user sees, not the raw sensor buffer.
        let normalised = normalised(image)

        let srcW = normalised.size.width
        let srcH = normalised.size.height
        guard srcW > 0 && srcH > 0 else { return normalised }

        // Target aspect: 4:3 in whichever direction matches the source.
        let isLandscape = srcW >= srcH
        let targetAspect: CGFloat = isLandscape ? (4.0 / 3.0) : (3.0 / 4.0)
        let srcAspect = srcW / srcH

        let cropRect: CGRect
        if srcAspect > targetAspect {
            // Too wide — trim the sides.
            let cropW = srcH * targetAspect
            cropRect = CGRect(x: (srcW - cropW) / 2, y: 0, width: cropW, height: srcH)
        } else {
            // Too tall — trim top/bottom.
            let cropH = srcW / targetAspect
            cropRect = CGRect(x: 0, y: (srcH - cropH) / 2, width: srcW, height: cropH)
        }

        guard let cg = normalised.cgImage?.cropping(to: cropRect) else { return normalised }
        let cropped = UIImage(cgImage: cg, scale: 1, orientation: .up)

        // Scale so the long edge = 1920.
        let targetLong = photoLongEdge
        let targetShort = photoShortEdge
        let target = isLandscape
            ? CGSize(width: targetLong, height: targetShort)
            : CGSize(width: targetShort, height: targetLong)

        let format = UIGraphicsImageRendererFormat()
        format.scale = 1
        let renderer = UIGraphicsImageRenderer(size: target, format: format)
        return renderer.image { _ in
            cropped.draw(in: CGRect(origin: .zero, size: target))
        }
    }

    /// Burn in orientation so later Core Graphics steps don't double-rotate.
    private static func normalised(_ image: UIImage) -> UIImage {
        if image.imageOrientation == .up { return image }
        let format = UIGraphicsImageRendererFormat()
        format.scale = image.scale
        let renderer = UIGraphicsImageRenderer(size: image.size, format: format)
        return renderer.image { _ in
            image.draw(in: CGRect(origin: .zero, size: image.size))
        }
    }

    /// Re-encodes a captured video to 720p H.264 so uploads stay small.
    /// Returns the original URL if we can't export (better than nothing).
    static func compressVideo(at sourceURL: URL) async -> URL {
        let asset = AVURLAsset(url: sourceURL)
        guard let exporter = AVAssetExportSession(asset: asset, presetName: videoExportPreset) else {
            return sourceURL
        }

        let outURL = FileManager.default.temporaryDirectory
            .appendingPathComponent("compressed-\(UUID().uuidString).mp4")
        exporter.outputURL = outURL
        exporter.outputFileType = .mp4
        exporter.shouldOptimizeForNetworkUse = true

        await exporter.export()
        guard exporter.status == .completed else { return sourceURL }

        // Replace the tmp original to save sandbox space.
        try? FileManager.default.removeItem(at: sourceURL)
        return outURL
    }
}
