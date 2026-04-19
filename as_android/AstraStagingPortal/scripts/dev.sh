#!/usr/bin/env bash
# dev.sh — one-command build + install + launch + logcat for AstraStagingPortal
#
# Usage:
#   ./scripts/dev.sh              # build, install to first connected device, launch, tail logcat
#   ./scripts/dev.sh --no-log     # skip logcat tail
#   ./scripts/dev.sh --connect 192.168.2.50:5555  # wireless: connect first, then build/install
#   ./scripts/dev.sh --list       # list connected devices and exit
#
# Tip: pair once with `./scripts/pair_wireless.sh`, then use --connect on subsequent runs.

set -euo pipefail

ADB="$HOME/Library/Android/sdk/platform-tools/adb"
PKG="com.astrastaging.portal"
ACTIVITY="$PKG/.MainActivity"
APK="app/build/outputs/apk/debug/app-debug.apk"

cd "$(dirname "$0")/.."

log=1
connect=""
for a in "$@"; do
  case "$a" in
    --no-log) log=0 ;;
    --connect) shift; connect="$1" ;;
    --connect=*) connect="${a#*=}" ;;
    --list) "$ADB" devices -l; exit 0 ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
  esac
  shift || true
done

if [[ -n "$connect" ]]; then
  echo "==> connecting wireless device: $connect"
  "$ADB" connect "$connect"
  # Drop any mDNS (_adb-tls-connect) duplicate of the same physical phone to avoid "more than one device"
  while read -r serial _; do
    [[ "$serial" == *_adb-tls-connect._tcp ]] && "$ADB" disconnect "$serial" >/dev/null || true
  done < <("$ADB" devices | tail -n +2)
  TARGET="-s $connect"
else
  TARGET=""
fi

echo "==> devices:"
"$ADB" devices -l

echo "==> gradle :app:assembleDebug"
./gradlew :app:assembleDebug

echo "==> installing $APK"
"$ADB" $TARGET install -r "$APK"

echo "==> launching $ACTIVITY"
"$ADB" $TARGET shell am start -n "$ACTIVITY" >/dev/null

if [[ "$log" -eq 1 ]]; then
  echo "==> logcat (Ctrl-C to stop — app keeps running)"
  sleep 1
  pid="$("$ADB" $TARGET shell pidof "$PKG" | tr -d '\r')"
  if [[ -n "$pid" ]]; then
    exec "$ADB" $TARGET logcat --pid="$pid"
  else
    exec "$ADB" $TARGET logcat | grep -iE "$PKG|AndroidRuntime"
  fi
fi
