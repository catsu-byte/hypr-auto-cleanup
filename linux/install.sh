#!/usr/bin/env bash
set -euo pipefail

source_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
target="$HOME/.local/bin/auto_cleanup.py"
config="$HOME/.config/hypr/hyprland.conf"
entry='exec-once = python3 ~/.local/bin/auto_cleanup.py'

command -v python3 >/dev/null || { echo 'Python 3 is required.' >&2; exit 1; }
command -v hyprctl >/dev/null || { echo 'Hyprland/hyprctl is required.' >&2; exit 1; }

install -Dm755 "$source_dir/auto_cleanup.py" "$target"
mkdir -p "$(dirname "$config")"
touch "$config"
grep -Fqx "$entry" "$config" || printf '\n%s\n' "$entry" >> "$config"

if [[ -n "${HYPRLAND_INSTANCE_SIGNATURE:-}" ]]; then
  pkill -f "^python3 $target$" 2>/dev/null || true
  nohup python3 "$target" >>"$HOME/.cache/auto_cleanup.log" 2>&1 </dev/null &
fi

echo "Installed to $target"
echo 'It will start automatically with Hyprland.'
