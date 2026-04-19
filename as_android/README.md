# Astra Staging Portal — Android

Parallel Android companion to `as_ios/`. Kotlin + Jetpack Compose.

## For Peter — setup steps

1. Install **Android Studio** (latest stable, "Ladybug" or newer): https://developer.android.com/studio
2. During first-run wizard, accept default SDK install. Then open **SDK Manager** and ensure:
   - Android SDK Platform 34
   - Android SDK Build-Tools 34.x
   - Android Emulator + one system image (e.g. Pixel 7, API 34)
3. Install **JDK 17** (Android Studio bundles one — use `File > Project Structure > SDK Location > Gradle JDK = jbr-17`).
4. Open this folder: `as_website/as_android/AstraStagingPortal` (choose "Open" → select the project root with `settings.gradle.kts`).
5. Let Gradle sync. Android Studio will auto-generate `gradle/wrapper/gradle-wrapper.jar`, `gradlew`, and `gradlew.bat` on first sync — do not check those in manually, Studio handles it.
6. Create an emulator (Device Manager → Create Device → Pixel 7 → API 34), click **Run ▶**. You should see:

   > Hello, Astra Staging!
   > Android portal — v0.1

## Project layout

```
AstraStagingPortal/
├── settings.gradle.kts
├── build.gradle.kts         # root (plugin versions)
├── gradle.properties
└── app/
    ├── build.gradle.kts     # app module
    └── src/main/
        ├── AndroidManifest.xml
        └── java/com/astrastaging/portal/MainActivity.kt
```

- Package: `com.astrastaging.portal`
- min SDK 24, target/compile SDK 34
- Compose BOM 2024.09, Kotlin 2.0, AGP 8.5.2

## Testing on a physical Android phone (fast iterate loop)

The closest thing to FastHTML hot-reload on Android is **Android Studio's "Apply Changes" button + Compose Live Edit** — edit a Composable, hit the lightning bolt (⚡), UI updates in ~1s without a full reinstall. For everything else there's `scripts/dev.sh`, a one-command build→install→launch→logcat wrapper.

### One-time phone setup

1. Phone: Settings → About phone → tap **Build number 7 times** (enables Developer options).
2. Settings → System → Developer options → turn on:
   - **USB debugging** (needed either way, even for wireless)
   - **Wireless debugging** (optional, Android 11+)
3. **Wired path (fastest, most reliable)**: plug phone into m4 via USB-C. On the phone, tap **Allow** when the "Allow USB debugging?" dialog appears and check "Always allow from this computer". Verify:
   ```bash
   ~/Library/Android/sdk/platform-tools/adb devices
   ```
   You should see your phone listed as `device` (not `unauthorized` or `offline`).
4. **Wireless path** (same Wi-Fi as m4): in **Wireless debugging** tap "Pair device with pairing code", note the IP:PORT + 6-digit code, then on m4:
   ```bash
   cd ~/Desktop/development/as_website/as_android/AstraStagingPortal
   ./scripts/pair_wireless.sh <pair-ip:port> <code>
   ```
   After pairing, note the separate "IP address & Port" shown at the top of the Wireless debugging screen (different port than pairing) — that's what you pass to `dev.sh --connect`.

### Everyday iteration

Once the phone is connected (USB plugged in OR paired & `adb connect`ed):

```bash
cd ~/Desktop/development/as_website/as_android/AstraStagingPortal
./scripts/dev.sh                          # USB
./scripts/dev.sh --connect 192.168.2.50:5555   # wireless
./scripts/dev.sh --no-log                 # skip logcat tail
./scripts/dev.sh --list                   # show connected devices
```

The script: connects if asked → `./gradlew :app:assembleDebug` → `adb install -r` → launches `MainActivity` → tails logcat filtered to the app. Typical cycle after the first build is **10–15s** (incremental Gradle + `adb install -r`).

### Near-instant UI edits (the FastHTML-like loop)

For Compose UI tweaks, **don't rerun the script** — use Android Studio:

1. Open the project in Android Studio, run once to the phone with ▶.
2. Edit any `@Composable` function.
3. Hit the ⚡ button in the top bar ("Apply Changes and Restart Activity") or enable **Live Edit** (File → Settings → Editor → Live Edit → On). UI updates without reinstalling the APK — sub-second for most Compose changes.

Fallback when Live Edit can't apply a change (schema/manifest/new dependencies): `./scripts/dev.sh` rebuilds and reinstalls from the CLI.

## Parallel development with iOS

Mirrors `as_ios/Astra Staging Portal/`. As features land on iOS (login, 5-tab shell, Task Board, milestone write-back), port them here screen-by-screen. Backend endpoints in `as_website/main.py` are shared.
