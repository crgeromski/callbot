# In utils/screenshot.py
def take_chart_screenshot(url, parent_window=None, save_dir=None):
    """
    Öffnet einen Link im Standardbrowser und macht einen Screenshot nach Auswahl des Monitors.
    
    Args:
        url: Der Dexscreener-Link
        parent_window: Das übergeordnete Tkinter-Fenster für den Dialog
        save_dir: Das Verzeichnis zum Speichern der Screenshots
    
    Returns:
        Der Pfad zum gespeicherten Screenshot oder None bei Fehler
    """
    import os
    import time
    import webbrowser
    import pyautogui
    import tkinter as tk
    from datetime import datetime
    from tkinter import Toplevel, Button, Frame, Label
    
    if "dexscreener.com" not in url:
        print(f"Ungültiger Dexscreener-Link: {url}")
        return None
    
    # Öffne den Link im Standardbrowser
    print(f"Öffne Link im Browser: {url}")
    webbrowser.open(url)
    
    screenshot_result = [None]  # Variable zum Speichern des Screenshots
    
    # Konfiguration für die Bildschirm-Bereiche
    # Diese Werte können angepasst werden
    screen_configs = {
        "links": {
            "region": (1150, 170, 750, 550),  # PERFEKTES MAß FÜR LINKS! # (x, y, width, height) für linken Monitor - Chart-Bereich
            "label": "Links"
        },
        "rechts": {
            "region": (-500, 200, 1500, 800),  # (x, y, width, height) für rechten Monitor
            "label": "Rechts"
        }
    }
    
    if parent_window:
        dialog = Toplevel(parent_window)
        dialog.title("Screenshot erstellen")
        dialog.geometry("300x180+2250+500")  # Etwas größer für zwei Buttons
        dialog.resizable(False, False)
        dialog.transient(parent_window)
        dialog.grab_set()
        
        # Erklärungstext hinzufügen
        Label(dialog, text="Wähle den Bildschirm für den Screenshot:").pack(pady=10)
        
        button_frame = Frame(dialog)
        button_frame.pack(expand=True)
        
        def make_screenshot(screen_key):
            try:
                # Verwende die konfigurierten Werte für den ausgewählten Bildschirm
                region = screen_configs[screen_key]["region"]
                screenshot = pyautogui.screenshot(region=region)
                screenshot_result[0] = screenshot
                dialog.destroy()
            except Exception as e:
                print(f"Fehler beim Erstellen des Screenshots: {e}")
                dialog.destroy()
        
        # Buttons für die beiden Bildschirme
        Button(button_frame, text=screen_configs["links"]["label"], 
               width=20, command=lambda: make_screenshot("links")).pack(pady=5)
        
        Button(button_frame, text=screen_configs["rechts"]["label"], 
               width=20, command=lambda: make_screenshot("rechts")).pack(pady=5)
        
        # Abbrechen-Button hinzufügen
        Button(button_frame, text="Abbrechen", width=20, command=dialog.destroy).pack(pady=5)
        
        # Warte auf Dialog-Schließung
        parent_window.wait_window(dialog)
        
        return screenshot_result[0]
    
    return None