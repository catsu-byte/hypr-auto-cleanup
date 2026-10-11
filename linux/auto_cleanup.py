#!/usr/bin/env python3
"""Close inactive Hyprland windows after an application-specific timeout."""

from __future__ import annotations

import json
import logging
import shutil
import signal
import subprocess
import threading
import time
from typing import Any

CHECK_INTERVAL_SECONDS = 60
BROWSER_TIMEOUT_SECONDS = 30 * 60
DEFAULT_TIMEOUT_SECONDS = 60 * 60
HYPRCTL_TIMEOUT_SECONDS = 5

BROWSERS = frozenset(
    {"firefox", "zen", "chromium", "brave-browser", "google-chrome"}
)
NEVER_CLOSE = frozenset({"discord", "vesktop", "spotify", "steam", "obsidian"})

LOG = logging.getLogger("hypr-auto-cleanup")
STOP_EVENT = threading.Event()


def run_hyprctl(*arguments: str) -> subprocess.CompletedProcess[str] | None:
    try:
        result = subprocess.run(
            ["hyprctl", *arguments],
            check=False,
            capture_output=True,
            text=True,
            timeout=HYPRCTL_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        LOG.warning("hyprctl could not be executed: %s", exc)
        return None

    if result.returncode != 0:
        error = result.stderr.strip() or f"exit status {result.returncode}"
        LOG.warning("hyprctl %s failed: %s", " ".join(arguments), error)
        return None
    return result


def query_json(command: str) -> Any | None:
    result = run_hyprctl(command, "-j")
    if result is None:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        LOG.warning("Invalid JSON from 'hyprctl %s -j': %s", command, exc)
        return None


def application_name(client: dict[str, Any]) -> str:
    value = client.get("class") or client.get("initialClass") or ""
    return str(value).strip().lower()


def matches_any(application: str, names: frozenset[str]) -> bool:
    return any(
        application == name
        or application.startswith(f"{name}.")
        or application.endswith(f".{name}")
        or application.startswith(f"{name}-")
        for name in names
    )


def close_window(address: str, application: str, inactive_seconds: float) -> None:
    result = run_hyprctl("dispatch", "closewindow", f"address:{address}")
    if result is not None:
        LOG.info(
            "Closed %s window %s after %d minutes of inactivity",
            application or "unknown",
            address,
            round(inactive_seconds / 60),
        )


def check_windows(last_active: dict[str, float]) -> bool:
    clients = query_json("clients")
    active_window = query_json("activewindow")
    if not isinstance(clients, list) or not isinstance(active_window, dict):
        return False

    active_address = str(active_window.get("address") or "")
    now = time.monotonic()
    current_addresses: set[str] = set()

    for item in clients:
        if not isinstance(item, dict):
            continue
        address = str(item.get("address") or "")
        if not address:
            continue

        current_addresses.add(address)
        application = application_name(item)

        if address == active_address:
            last_active[address] = now
            continue

        first_inactive = last_active.setdefault(address, now)
        if matches_any(application, NEVER_CLOSE):
            continue

        timeout = (
            BROWSER_TIMEOUT_SECONDS
            if matches_any(application, BROWSERS)
            else DEFAULT_TIMEOUT_SECONDS
        )
        inactive_seconds = now - first_inactive
        if inactive_seconds >= timeout:
            close_window(address, application, inactive_seconds)
            last_active.pop(address, None)

    for address in last_active.keys() - current_addresses:
        del last_active[address]
    return True


def request_stop(signum: int, _frame: object) -> None:
    LOG.info("Received signal %s; stopping", signum)
    STOP_EVENT.set()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    if shutil.which("hyprctl") is None:
        LOG.error("hyprctl was not found in PATH")
        return 1

    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)
    last_active: dict[str, float] = {}
    LOG.info("Started; checking every %d seconds", CHECK_INTERVAL_SECONDS)

    while not STOP_EVENT.is_set():
        try:
            check_windows(last_active)
        except Exception:
            LOG.exception("Unexpected error during window scan")
        STOP_EVENT.wait(CHECK_INTERVAL_SECONDS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
