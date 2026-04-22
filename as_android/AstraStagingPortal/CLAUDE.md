# Android Build & Test — AstraStagingPortal

## Tools (use in this priority order)
- **Builds:** `./gradlew :app:assembleDebug` via Bash.
- **Compile-only fast check:** `./gradlew :app:compileDebugKotlin` (~2s incremental).
- **Unit tests:** `./gradlew :app:test`.
- **Instrumented tests:** `./gradlew :app:connectedAndroidTest` (needs running emulator).
- **Install:** `./gradlew :app:installDebug`.
- **UI verification:** mobile-mcp tools (`list_devices`, `take_screenshot`, `tap`,
  `swipe`, `read_accessibility_tree`, `launch_app`).

## Project identifiers
- Application ID: `com.astrastaging.portal`
- Main activity: `com.astrastaging.portal/.MainActivity`
- Min SDK: 24, Target: 34
- Compose BOM: `2024.09.00`

## Preferred Emulator
- Pixel 7 / Pixel 8 API 34 (any AVD works, but we test against API 34).
- ADB device: `emulator-5554` (default port).
- ADB lives at `~/Library/Android/sdk/platform-tools/adb` and is on PATH.

## Auth bypass for testing
Debug builds auto-login via `DEV_BYPASS_TOKEN` in `app/build.gradle.kts`
(buildConfigField). Token expires 2027-04-19. No login flow needed for smoke
tests.

## Launch
```bash
adb shell am force-stop com.astrastaging.portal
adb shell am start -n com.astrastaging.portal/.MainActivity
```

## Verification loop after a code change
1. `./gradlew :app:installDebug` (also compiles).
2. Force-stop + restart the activity (commands above).
3. Screenshot via mobile-mcp.
4. Read accessibility tree to verify expected elements / labels.
5. Report pass/fail with screenshot path + tree excerpt (not just "looks good").

## Backend
- Debug API base URL: `http://100.114.47.80:5002` (m4 over Tailscale).
- Release: `https://portal.astrastaging.com`.
- If the emulator can't hit the Tailscale IP, fall back to `http://10.0.2.2:5002`
  (only works if the FastHTML server on m4 is started locally).

## Known constraints
- Long-press + drag-and-drop via `adb input` won't simulate Compose's
  `dragAndDropSource` properly (system DnD requires gesture state Compose
  ignores from synthetic events). Verify visually via screenshots before/after,
  or check persisted `menu_prefs` SharedPreferences via
  `adb shell run-as com.astrastaging.portal cat /data/data/com.astrastaging.portal/shared_prefs/menu_prefs.xml`.
