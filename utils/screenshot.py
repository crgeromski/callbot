# Screenshot-Funktionen
import os
import time
import pyautogui
import webbrowser
from datetime import datetime
from tkinter import Toplevel, Label, Button, Frame

def take_chart_screenshot(url, parent_window=None, save_dir=None):
    """
    Öffnet einen Link im Standardbrowser und macht einen Screenshot nach Bestätigung.
    
    Args:
        url: Der Dexscreener-Link
        parent_window: Das übergeordnete Tkinter-Fenster für den Dialog
        save_dir: Das Verzeichnis zum Speichern der Screenshots
    
    Returns:
        Der Pfad zum gespeicherten Screenshot oder None bei Fehler
    """
    if "dexscreener.com" not in url:
        print(f"Ungültiger Dexscreener-Link: {url}")
        return None
    
    # Wenn kein save_dir angegeben, im Projektordner einen screenshots-Ordner erstellen
    if save_dir is None:
        # Finde den Pfad zum Projektordner
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        save_dir = os.path.join(project_dir, "screenshots")
    
    # Erstelle das Verzeichnis, falls es nicht existiert
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # Öffne den Link im Standardbrowser
    print(f"Öffne Link im Browser: {url}")
    webbrowser.open(url)
    
    # Warte einen Moment, bis der Browser geöffnet ist
    time.sleep(1)
    
    # Zeige einen Dialog mit Anweisungen
    if parent_window:
        dialog = Toplevel(parent_window)
        dialog.title("Screenshot vorbereiten")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        dialog.transient(parent_window)
        dialog.grab_set()
        
        Label(dialog, text="Bitte folge diesen Schritten:", font=("Arial", 12, "bold")).pack(pady=(10, 5))
        
        instructions = [
            "1. Warte, bis der Chart vollständig geladen ist",
            "2. Stelle sicher, dass der Chart-Bereich sichtbar ist",
            "3. Klicke auf 'Screenshot erstellen', wenn du bereit bist",
            "4. Nach dem Klick hast du 3 Sekunden Zeit, um zum Browser zu wechseln"
        ]
        
        for instr in instructions:
            Label(dialog, text=instr, anchor="w", justify="left").pack(fill="x", padx=20, pady=2)
        
        # Timestamp für den Dateinamen
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Token-Symbol aus URL extrahieren
        token_parts = url.split("/")
        token_identifier = token_parts[-1][:10]  # Nimm die ersten 10 Zeichen
        
        # Pfad für den Screenshot
        screenshot_path = os.path.join(save_dir, f"chart_{token_identifier}_{timestamp}.png")
        
        def on_screenshot_button():
            dialog.destroy()
            print("Screenshot wird in 3 Sekunden erstellt...")
            # Gib dem Benutzer Zeit, zum Browser zu wechseln
            time.sleep(3)
            
            try:
                # Erstelle den Screenshot
                screenshot = pyautogui.screenshot()
                screenshot.save(screenshot_path)
                print(f"Screenshot gespeichert unter: {screenshot_path}")
                return screenshot_path
            except Exception as e:
                print(f"Fehler beim Erstellen des Screenshots: {e}")
                return None
        
        button_frame = Frame(dialog)
        button_frame.pack(pady=20)
        
        Button(button_frame, text="Screenshot erstellen", command=on_screenshot_button).pack(side="left", padx=10)
        Button(button_frame, text="Abbrechen", command=dialog.destroy).pack(side="left", padx=10)
        
        # Warte auf Dialog-Schließung
        parent_window.wait_window(dialog)
        
        return screenshot_path
    else:
        print("Kein Parent-Window angegeben.")
        return None