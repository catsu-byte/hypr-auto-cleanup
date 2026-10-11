#!/usr/bin/env bash
set -euo pipefail

target="$HOME/.local/bin/auto_cleanup.py"
config="$HOME/.config/hypr/hyprland.conf"
entry='exec-once = python3 ~/.local/bin/auto_cleanup.py'

pkill -f "^python3 $target$" 2>/dev/null || true
if [[ -f "$config" ]]; then
  sed -i "\|^${entry//./\\.}$|d" "$config"
fi
if [[ -f "$target" ]]; then
  rm -- "$target"
fi
echo 'Hypr Auto-Cleanup was removed.'
