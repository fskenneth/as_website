//
//  LoginView.swift
//  Astra Staging Portal
//

import SwiftUI

struct LoginView: View {
    @Environment(AuthStore.self) private var auth
    @State private var email = ""
    @State private var password = ""

    var body: some View {
        VStack(spacing: 20) {
            Spacer()
            Text("Astra Staging Portal")
                .font(.largeTitle).bold()
                .multilineTextAlignment(.center)
            Text("Sign in to continue")
                .foregroundStyle(.secondary)

            VStack(spacing: 12) {
                TextField("Email", text: $email)
                    .textContentType(.emailAddress)
                    .keyboardType(.emailAddress)
                    .textInputAutocapitalization(.never)
                    .disableAutocorrection(true)
                    .padding(12)
                    .background(Color(.secondarySystemBackground))
                    .cornerRadius(10)

                SecureField("Password", text: $password)
                    .textContentType(.password)
                    .padding(12)
                    .background(Color(.secondarySystemBackground))
                    .cornerRadius(10)
            }
            .padding(.horizontal)

            if let err = auth.loginError {
                Text(err)
                    .font(.footnote)
                    .foregroundStyle(.red)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal)
            }

            Button {
                Task { await auth.login(email: email.trimmingCharacters(in: .whitespaces), password: password) }
            } label: {
                HStack {
                    if auth.isLoading { ProgressView().tint(.white) }
                    Text(auth.isLoading ? "Signing in..." : "Sign in")
                        .bold()
                }
                .frame(maxWidth: .infinity)
                .padding(.vertical, 14)
                .background(canSubmit ? Color.blue : Color.gray.opacity(0.5))
                .foregroundStyle(.white)
                .cornerRadius(10)
            }
            .disabled(!canSubmit || auth.isLoading)
            .padding(.horizontal)

            Spacer()
            Spacer()
        }
        .padding()
    }

    private var canSubmit: Bool {
        !email.isEmpty && !password.isEmpty
    }
}
