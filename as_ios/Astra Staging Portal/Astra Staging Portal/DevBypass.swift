//
//  DevBypass.swift
//  Astra Staging Portal
//
//  DEV-ONLY auto-login. When DEV_BYPASS_TOKEN is non-nil, debug builds
//  skip the login screen and sign in with this token on launch. Release
//  builds have DEV_BYPASS_TOKEN = nil, so LoginView shows normally.
//
//  Delete (or set to nil) before shipping a release build.
//

import Foundation

#if DEBUG
let DEV_BYPASS_TOKEN: String? = "dFF4hOUwq9s6nnOFzYBITC8OZ5_dyOqIBP8qzYHxyzU"  // expires 2027-04-19
#else
let DEV_BYPASS_TOKEN: String? = nil
#endif
