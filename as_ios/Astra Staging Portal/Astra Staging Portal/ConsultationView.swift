//
//  ConsultationView.swift
//  Astra Staging Portal
//
//  Stager consultation flow: meet a potential customer at the property,
//  capture photos / measurements / existing items, and either convert the
//  lead to a booking or hand off enough data for the design step.
//

import SwiftUI

struct ConsultationView: View {
    var body: some View {
        NavigationStack {
            List {
                Section("On-site capture") {
                    Label("Property photos", systemImage: "camera")
                        .foregroundStyle(.secondary)
                    Label("Room measurements", systemImage: "ruler")
                        .foregroundStyle(.secondary)
                    Label("Existing furniture & items", systemImage: "sofa")
                        .foregroundStyle(.secondary)
                }

                Section("Lead → booking") {
                    Label("Quote builder", systemImage: "doc.text.magnifyingglass")
                        .foregroundStyle(.secondary)
                    Label("Send agreement", systemImage: "signature")
                        .foregroundStyle(.secondary)
                    Label("Schedule staging date", systemImage: "calendar.badge.plus")
                        .foregroundStyle(.secondary)
                }

                Section {
                    Text("Coming soon. This is where stagers will run on-site consultations and convert leads into bookings.")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                }
            }
            .navigationTitle("Consultation")
        }
    }
}
