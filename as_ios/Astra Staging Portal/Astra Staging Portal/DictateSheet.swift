//
//  DictateSheet.swift
//  Astra Staging Portal
//
//  Review sheet for a completed dictation: shows the server-transcribed
//  text + key-point summary, lets the stager edit the customer + sales-rep
//  email drafts, and sends them via Mailgun. Recording + upload are
//  handled upstream by DictationController; by the time this sheet is
//  presented, the server already owns the audio, transcript, and summary.
//

import SwiftUI

struct DictateSheet: View {
    let dictation: DictationRecord
    let customerEmailOnFile: String?
    let token: String

    @Environment(\.dismiss) private var dismiss

    // Editable drafts, seeded from the server summary.
    @State private var customerEmailTo: String = ""
    @State private var customerSubject: String = ""
    @State private var customerBody: String = ""
    @State private var salesSubject: String = ""
    @State private var salesBody: String = ""
    @State private var sendingEmail: String?  // "customer" | "sales_rep" | "both"
    @State private var sendError: String?
    @State private var sentConfirmation: String?

    var body: some View {
        NavigationStack {
            List {
                if let err = dictation.error, !err.isEmpty {
                    Section {
                        Label(err, systemImage: "exclamationmark.triangle")
                            .foregroundStyle(.orange)
                            .font(.footnote)
                    }
                }

                if let summary = dictation.summary, !summary.key_points.isEmpty {
                    Section("Key points") {
                        ForEach(summary.key_points, id: \.self) { k in
                            HStack(alignment: .top, spacing: 8) {
                                Text("•").foregroundStyle(.secondary)
                                Text(k).font(.subheadline)
                            }
                        }
                    }
                }

                if let summary = dictation.summary, !summary.suggested_quote_lines.isEmpty {
                    Section("Suggested quote items") {
                        ForEach(summary.suggested_quote_lines, id: \.description) { line in
                            Text(line.description).font(.subheadline)
                        }
                    }
                }

                Section("Customer email") {
                    if customerEmailTo.isEmpty {
                        Text("No customer email on file — fill it in:")
                            .font(.caption).foregroundStyle(.secondary)
                    }
                    TextField("Customer email", text: $customerEmailTo)
                        .textContentType(.emailAddress)
                        .keyboardType(.emailAddress)
                        .autocorrectionDisabled()
                        .textInputAutocapitalization(.never)
                    TextField("Subject", text: $customerSubject)
                    TextEditor(text: $customerBody)
                        .frame(minHeight: 140)
                        .font(.callout)
                    Button {
                        Task { await sendEmail("customer") }
                    } label: {
                        if sendingEmail == "customer" {
                            ProgressView()
                        } else {
                            Label("Send to Customer", systemImage: "paperplane")
                        }
                    }
                    .disabled(sendingEmail != nil || customerEmailTo.isEmpty || customerSubject.isEmpty || customerBody.isEmpty)
                }

                Section("Internal note to sales@astrastaging.com") {
                    TextField("Subject", text: $salesSubject)
                    TextEditor(text: $salesBody)
                        .frame(minHeight: 120)
                        .font(.callout)
                    Button {
                        Task { await sendEmail("sales_rep") }
                    } label: {
                        if sendingEmail == "sales_rep" {
                            ProgressView()
                        } else {
                            Label("Send to Sales Rep", systemImage: "paperplane")
                        }
                    }
                    .disabled(sendingEmail != nil || salesSubject.isEmpty || salesBody.isEmpty)
                }

                Section {
                    Button {
                        Task { await sendEmail("both") }
                    } label: {
                        if sendingEmail == "both" {
                            ProgressView()
                        } else {
                            Label("Send BOTH emails", systemImage: "paperplane.fill")
                                .frame(maxWidth: .infinity)
                        }
                    }
                    .buttonStyle(.borderedProminent)
                    .disabled(sendingEmail != nil)
                } footer: {
                    if let msg = sentConfirmation {
                        Text(msg).foregroundStyle(.green).font(.footnote)
                    } else if let err = sendError {
                        Text(err).foregroundStyle(.red).font(.footnote)
                    }
                }

                if !dictation.transcript.isEmpty {
                    Section("Raw transcript") {
                        Text(dictation.transcript).font(.footnote).foregroundStyle(.secondary)
                    }
                }
            }
            .navigationTitle("Dictation")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Done") { dismiss() }
                }
            }
            .onAppear(perform: seedDrafts)
        }
    }

    private func seedDrafts() {
        customerEmailTo = customerEmailOnFile ?? ""
        if let s = dictation.summary {
            customerSubject = s.customer_email_subject
            customerBody = s.customer_email_body
            salesSubject = s.sales_rep_email_subject
            salesBody = s.sales_rep_email_body
        }
    }

    private func sendEmail(_ recipient: String) async {
        sendingEmail = recipient
        sendError = nil
        sentConfirmation = nil
        defer { sendingEmail = nil }

        do {
            let resp = try await APIClient.shared.sendDictationEmail(
                dictationId: dictation.id,
                recipient: recipient,
                toCustomer: customerEmailTo.isEmpty ? nil : customerEmailTo,
                customerSubject: customerSubject,
                customerBody: customerBody,
                salesRepSubject: salesSubject,
                salesRepBody: salesBody,
                token: token,
            )
            if resp.ok {
                let names = resp.sent.map {
                    $0.recipient.replacingOccurrences(of: "_", with: " ")
                }.joined(separator: " + ")
                sentConfirmation = "Sent to \(names)."
            } else {
                sendError = resp.errors.joined(separator: "\n")
            }
        } catch {
            sendError = error.localizedDescription
        }
    }
}
