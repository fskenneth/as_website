//
//  CapturePreviewSheet.swift
//  Astra Staging Portal
//
//  After the camera returns, we show the shot full-size with Save /
//  Discard buttons so the user can bail on a bad frame before it joins
//  the upload queue. Tapping Save enqueues; dismissing the sheet (or
//  tapping Discard) deletes the temp file.
//

import AVKit
import SwiftUI

struct CapturePreviewSheet: View {
    let areaName: String?
    let mediaType: CaptureMediaType
    let fileURL: URL
    let onSave: () -> Void
    let onDiscard: () -> Void

    var body: some View {
        NavigationStack {
            ZStack {
                Color.black.ignoresSafeArea()

                if mediaType == .video {
                    VideoPlayer(player: AVPlayer(url: fileURL))
                        .ignoresSafeArea(edges: .bottom)
                } else if let ui = UIImage(contentsOfFile: fileURL.path) {
                    Image(uiImage: ui)
                        .resizable()
                        .scaledToFit()
                } else {
                    VStack(spacing: 12) {
                        Image(systemName: "exclamationmark.triangle")
                            .font(.title)
                            .foregroundStyle(.white)
                        Text("Preview unavailable").foregroundStyle(.white)
                    }
                }

                VStack {
                    Spacer()
                    HStack(spacing: 12) {
                        Button(role: .destructive) {
                            onDiscard()
                        } label: {
                            Label("Discard", systemImage: "trash")
                                .frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.borderedProminent)
                        .tint(.red)

                        Button {
                            onSave()
                        } label: {
                            Label("Save", systemImage: "checkmark.circle.fill")
                                .frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.borderedProminent)
                        .tint(.green)
                    }
                    .padding()
                    .background(Color.black.opacity(0.4))
                }
            }
            .navigationTitle("\(mediaType.displayLabel) · \(areaName ?? "Unassigned")")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Discard") { onDiscard() }
                        .foregroundStyle(.red)
                }
            }
            .interactiveDismissDisabled(true)
        }
    }
}
