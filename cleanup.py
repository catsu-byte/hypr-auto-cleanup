#!/usr/bin/env python3
import json
import subprocess
import time

# --- KONFIGURATION (In Sekunden) ---
BROWSER_TIMEOUT = 30 * 60  # 30 Minuten
APP_TIMEOUT = 60 * 60      # 60 Minuten
CHECK_INTERVAL = 60        # Alle 60 Sekunden prüfen

# Liste von Apps (class Name), die NIEMALS geschlossen werden dürfen
ALWAYS_KEEP = [
    "discord",
    "spotify",
    "steam",
    "vesktop",
    "obsidian"
]

# Bekannte Browser-Klassen
BROWSERS = ["firefox", "chromium", "google-chrome", "brave-browser", "zen"]

# Wörter im Titel, die auf aktive KI-Arbeit hinweisen
AI_ACTIVE_KEYWORDS = ["thinking", "generating", "schreibt", "generiert", "working", "processing"]

# Speicher für den letzten Inaktivitäts-Zeitstempel je Fenster-Adresse
last_active_time = {}

def get_hyprland_data():
    """Holt die Liste aller aktiven Fenster und den aktuellen Fokus von hyprctl"""
    try:
        clients_raw = subprocess.check_output(["hyprctl", "clients", "-j"]).decode("utf-8")
        active_raw = subprocess.check_output(["hyprctl", "activewindow", "-j"]).decode("utf-8")
        clients = json.loads(clients_raw) if clients_raw else []
        active = json.loads(active_raw) if active_raw else {}
        return clients, active
    except Exception as e:
        print(f"Fehler beim Abrufen der Hyprland-Daten: {e}")
        return [], {}

def close_window(address):
    """Schließt ein bestimmtes Fenster sauber über Hyprland"""
    subprocess.run(["hyprctl", "dispatch", "closewindow", f"address:{address}"])

def main():
    current_time = time.time()
    clients, active_window = get_hyprland_data()
    active_address = active_window.get("address", "")

    # Aktualisiere die Zeit für das aktuell genutzte Fenster
    if active_address:
        last_active_time[active_address] = current_time

    for client in clients:
        addr = client.get("address")
        app_class = client.get("class", "").lower()
        title = client.get("title", "").lower()

        # 1. Ausnahme: Dauerhafte Hintergrund-Apps
        if any(keep_app in app_class for keep_app in ALWAYS_KEEP):
            continue

        # 2. Ausnahme: KI-Prozesse, die gerade arbeiten
        if any(keyword in title for keyword in AI_ACTIVE_KEYWORDS):
            last_active_time[addr] = current_time  # Reset Timer, solange die KI arbeitet
            continue

        # Falls ein Fenster neu geöffnet wurde, füge es mit der aktuellen Zeit hinzu
        if addr not in last_active_time:
            last_active_time[addr] = current_time
            continue

        # Berechne wie lange das Fenster nicht mehr angeklickt/fokussiert wurde
        inactive_duration = current_time - last_active_time[addr]

        # 3. Regel: Browser-Fenster nach 30 Min schließen
        is_browser = any(b in app_class for b in BROWSERS)
        if is_browser and inactive_duration > BROWSER_TIMEOUT:
            print(f"[Auto-Cleanup] Schließe inaktiven Browser: {client.get('title')} ({addr})")
            close_window(addr)
            del last_active_time[addr]

        # 4. Regel: Alle anderen Apps nach 60 Min schließen
        elif not is_browser and inactive_duration > APP_TIMEOUT:
            print(f"[Auto-Cleanup] Schließe inaktive App: {client.get('class')} ({addr})")
            close_window(addr)
            del last_active_time[addr]

if __name__ == "__main__":
    while True:
        main()
        time.sleep(CHECK_INTERVAL)
