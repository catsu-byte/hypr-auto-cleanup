# Hyprland Auto-Cleanup

An intelligent background daemon for Hyprland (Wayland) that monitors window activity and automatically closes inactive applications and browser windows to keep your workspace clean and preserve system resources.

## Features

- Browser Timeout (30 min): Closes inactive browser windows after 30 minutes without focus.
- General App Timeout (60 min): Closes normal inactive applications after 1 hour.
- Whitelist Protection: Apps like Discord, Spotify, Steam, Vesktop, and Obsidian are never closed automatically.
- AI Work Protection: Automatically detects if AI tools like Claude or ChatGPT are currently generating/thinking (based on window titles) and prevents them from being closed while working.
- Lightweight: Uses native hyprctl JSON calls with virtually zero CPU overhead.

## Requirements

- Linux with Hyprland
- Python 3

## Installation & Usage

1. Clone the repository:
