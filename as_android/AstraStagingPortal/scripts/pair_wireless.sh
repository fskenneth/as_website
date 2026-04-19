#!/usr/bin/env bash
# pair_wireless.sh — one-time wireless ADB pairing for a physical Android phone.
#
# Prereqs on the phone (Android 11+):
#   Settings → About phone → tap Build number 7× (unlocks Developer options)
#   Settings → System → Developer options → USB debugging: ON
#   Settings → System → Developer options → Wireless debugging: ON
#   Inside "Wireless debugging": "Pair device with pairing code"
#     → note the IP:PORT and the 6-digit code shown on the phone
#
# Usage:
#   ./scripts/pair_wireless.sh <pair-ip:port> <pair-code>
#   Then after pairing succeeds, the phone shows a separate "IP & Port" at the top
#   of the Wireless debugging screen — use that with `dev.sh --connect`.
#
# Re-pair only if the phone forgets this computer or you re-enable Wireless debugging.

set -euo pipefail

ADB="$HOME/Library/Android/sdk/platform-tools/adb"

if [[ $# -ne 2 ]]; then
  echo "usage: $0 <pair-ip:port> <6-digit-code>"
  echo "example: $0 192.168.2.50:37123 482914"
  exit 1
fi

"$ADB" pair "$1" "$2"
echo
echo "==> paired. Now grab the Wireless debugging 'IP address & Port' (different port than pairing)"
echo "==> and run:  ./scripts/dev.sh --connect <ip:port>"
