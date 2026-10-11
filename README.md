# Hypr Auto-Cleanup

A tiny background utility that closes windows which have not been focused for a while. It ships with native implementations for **Hyprland/Linux** and **Windows**.

## Defaults

| Window type | Timeout |
| --- | ---: |
| Firefox, Zen, Chromium, Brave, Chrome | 30 minutes |
| Other applications | 60 minutes |
| Discord, Vesktop, Spotify, Steam, Obsidian | Never closed |

Both editions check once per minute, retain no browsing data, use no network connection, and ask applications to close normally so they can show a save prompt.

## Linux / Hyprland

Requirements: Hyprland, `hyprctl`, and Python 3.10 or newer.

```bash
tar -xzf hypr-auto-cleanup-linux-v1.0.0.tar.gz
cd hypr-auto-cleanup-linux-v1.0.0/linux
./install.sh
```

The installer copies the daemon to `~/.local/bin/auto_cleanup.py`, adds this line to `~/.config/hypr/hyprland.conf`, and starts it immediately when run inside Hyprland:

```ini
exec-once = python3 ~/.local/bin/auto_cleanup.py
```

To remove it, run `linux/uninstall.sh`.

## Windows 10/11

Extract `hypr-auto-cleanup-windows-v1.0.0.zip`, right-click `windows/install.ps1`, and choose **Run with PowerShell**. Alternatively:

```powershell
powershell -ExecutionPolicy Bypass -File .\windows\install.ps1
```

The Windows edition uses the Win32 API to inspect visible top-level windows and sends `WM_CLOSE` after the timeout. Windows shell components are protected in addition to the normal whitelist. It installs only for the current user and requires no administrator rights.

To remove it, run `windows/uninstall.ps1`.

## Safety notes

- A timer begins only after the utility first sees a window.
- The focused window is never closed.
- Linux skips a complete scan if Hyprland returns incomplete data.
- Windows protects Explorer and other system-shell processes.
- `WM_CLOSE` and Hyprland's `closewindow` request a normal close; applications may still prompt to save work.

## License

MIT — see [LICENSE](LICENSE).
