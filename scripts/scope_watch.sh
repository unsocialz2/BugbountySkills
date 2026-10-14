#!/usr/bin/env bash
set -euo pipefail

TARGET=${1:?usage: scope_watch.sh <hackerone-handle>}
URL="https://hackerone.com/${TARGET}/policy_scopes/all_eligible/json"
DIR="$HOME/scope_watch/${TARGET}"
mkdir -p "$DIR"

curl -sk "$URL" -o "$DIR/now.json"
[ -f "$DIR/last.json" ] || cp "$DIR/now.json" "$DIR/last.json"
diff <(jq -S . "$DIR/last.json") <(jq -S . "$DIR/now.json") > "$DIR/diff.txt" || true

if [ -s "$DIR/diff.txt" ]; then
  python3 "$HOME/scripts/notify_discord.py" "[$TARGET] scope changed" < "$DIR/diff.txt"
  cp "$DIR/now.json" "$DIR/last.json"
fi
