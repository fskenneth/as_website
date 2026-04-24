//
//  MediaViewerSheet.swift
//  Astra Staging Portal
//
//  Fullscreen preview for a single queued capture. Tap-to-expand from the
//  thumbnail grid. Provides a destructive "Delete" action so users don't
//  have to long-press a tiny thumb to remove a mis-framed shot.
//

import AVKit
import SwiftUI

struct MediaViewerSheet: View {
    let capture: ConsultationCapture
    let fileURL: URL
    let onDelete: () -> Void
    let onDismiss: () -> Void

    var body: some View {
        NavigationStack {
            ZStack {
                Color.black.ignoresSafeArea()

                if capture.mediaType == .video {
                    VideoPlayer(player: AVPlayer(url: fileURL))
                        .ignoresSafeArea(edges: .bottom)
                } else if let ui = UIImage(contentsOfFile: fileURL.path) {
                    Image(uiImage: ui)
                        .resizable()
                        .scaledToFit()
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else {
                    VStack(spacing: 12) {
                        Image(systemName: "exclamationmark.triangle")
                            .font(.title)
                            .foregroundStyle(.white)
                        Text("Couldn't load media").foregroundStyle(.white)
                    }
                }
            }
            .navigationTitle(title)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Done") { onDismiss() }
                }
                ToolbarItem(placement: .destructiveAction) {
                    Button(role: .destructive) {
                        onDelete()
                    } label: {
                        Image(systemName: "trash")
                    }
                }
            }
        }
    }

    private var title: String {
        let area = capture.areaName ?? "Unassigned"
        return "\(capture.mediaType.displayLabel) · \(area)"
    }
}
