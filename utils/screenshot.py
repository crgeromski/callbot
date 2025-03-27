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
    import tkinter as tk
    from datetime import datetime
    from tkinter import Toplevel, Button, Frame, Label
    from PIL import Image
    import mss
    
    if "dexscreener.com" not in url:
        return None
    
    # Öffne den Link im Standardbrowser
    webbrowser.open(url)
    
    screenshot_result = [None]  # Variable zum Speichern des Screenshots
    
    # Konfiguration für die Bildschirm-Bereiche
    screen_configs = {
        "links": {
            "region": {"top": 170, "left": 1150, "width": 750, "height": 550},
            "label": "Links",
            "monitor": 1
        },
        "rechts": {
            "region": {"top": 170, "left": 1010, "width": 900, "height": 670},
            "label": "Rechts",
            "monitor": 2
        }
    }
    
    if parent_window:
        dialog = Toplevel(parent_window)
        dialog.title("Screenshot erstellen")
        dialog.geometry("300x150+2250+500")
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
                config = screen_configs[screen_key]
                monitor_idx = config["monitor"]
                region = config["region"]
                
                # Kleine Pause vor dem Screenshot
                time.sleep(0.5)
                
                # Screenshot erstellen mit MSS
                with mss.mss() as sct:
                    monitor = sct.monitors[monitor_idx]
                    
                    # Berechne absolute Koordinaten basierend auf dem gewählten Monitor
                    capture_region = {
                        "top": monitor["top"] + region["top"],
                        "left": monitor["left"] + region["left"],
                        "width": region["width"],
                        "height": region["height"]
                    }
                    
                    # Screenshot erstellen
                    sct_img = sct.grab(capture_region)
                    
                    # Konvertiere in PIL Image
                    screenshot = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                    screenshot_result[0] = screenshot
                
                dialog.destroy()
                
            except Exception:
                dialog.destroy()
        
        # Nur die beiden Hauptbuttons
        Button(button_frame, text=screen_configs["links"]["label"], 
               width=20, command=lambda: make_screenshot("links")).pack(pady=5)
        
        Button(button_frame, text=screen_configs["rechts"]["label"], 
               width=20, command=lambda: make_screenshot("rechts")).pack(pady=5)
        
        # Warte auf Dialog-Schließung
        parent_window.wait_window(dialog)
        
        return screenshot_result[0]
    
    return None