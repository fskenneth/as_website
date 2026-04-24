//
//  NetworkMonitor.swift
//  Astra Staging Portal
//
//  Observable wrapper around NWPathMonitor. `isOnline` gates any sync that
//  needs the server; `isOnWiFi` lets the upload queue defer heavy media
//  when the user has opted into Wi-Fi-only uploads.
//

import Foundation
import Network
import Observation

@Observable
@MainActor
final class NetworkMonitor {
    static let shared = NetworkMonitor()

    var isOnline: Bool = false
    var isOnWiFi: Bool = false
    var isExpensive: Bool = false

    private let monitor = NWPathMonitor()
    private let queue = DispatchQueue(label: "com.astrastaging.portal.NetworkMonitor")

    init() {
        monitor.pathUpdateHandler = { [weak self] path in
            let online = path.status == .satisfied
            let wifi = path.usesInterfaceType(.wifi)
            let expensive = path.isExpensive
            Task { @MainActor [weak self] in
                self?.isOnline = online
                self?.isOnWiFi = wifi
                self?.isExpensive = expensive
            }
        }
        monitor.start(queue: queue)
    }

    deinit { monitor.cancel() }

    /// Shorthand: can the upload queue push heavy media right now?
    func canUploadMedia(wifiOnly: Bool) -> Bool {
        guard isOnline else { return false }
        if wifiOnly { return isOnWiFi }
        return true
    }
}
