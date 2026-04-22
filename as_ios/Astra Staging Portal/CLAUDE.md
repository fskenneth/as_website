# iOS Build & Test — Astra Staging Portal

## Tools (use in this priority order)
- **Builds:** `mcp__xcodebuildmcp__build_sim_name_proj` (project, not workspace).
  Never fall back to raw `xcodebuild` unless the MCP tool fails. If it does, fall back to:
  `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer xcodebuild ...`
  (`xcode-select -p` may point to CommandLineTools — DEVELOPER_DIR overrides it.)
- **Tests:** `mcp__xcodebuildmcp__test_sim_name_proj`.
- **Runtime logs:** `mcp__xcodebuildmcp__capture_logs`.
- **UI verification:** mobile-mcp tools (`list_devices`, `take_screenshot`, `tap`,
  `swipe`, `read_accessibility_tree`, `launch_app`).

## Project paths
- Project: `Astra Staging Portal.xcodeproj` (in this directory)
- Scheme: `Astra Staging Portal`
- Bundle ID: `com.astrastaging.portal`
- Min iOS: 17 (uses `@Observable` Observation framework)

## Preferred Simulator
- Device: iPhone 17 Pro (or latest iPhone 16+)
- iOS: 26.x
- Pick the booted one via `mcp__xcodebuildmcp__list_devices`. If none are booted,
  boot one first.

## Auth bypass for testing
Debug builds auto-login via `DEV_BYPASS_TOKEN` defined in `DevBypass.swift` —
no login UI tap-through needed for smoke tests.

## Verification loop after a code change
1. Build with `build_sim_name_proj`.
2. Install + launch on the running simulator.
3. Take a screenshot of the main screen.
4. Read the accessibility tree to verify expected elements are present.
5. Report pass/fail with the screenshot path + tree diff (not just "looks good").

## Known constraints (don't try, won't work)
- `xcrun simctl` requires `xcode-select -s /Applications/Xcode.app/...`. If
  simctl errors with "not a developer tool", use `DEVELOPER_DIR` env override
  or ask Kenneth to run `sudo xcode-select -s` once.
- Long-press + drag-and-drop UI tests via `idb` are flaky on Simulator —
  prefer accessibility-tree assertions over gesture replay where possible.
