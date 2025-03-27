# In utils/screenshot.py
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
    import os
    import time
    import webbrowser
    import pyautogui
    from datetime import datetime
    from tkinter import Toplevel, Button, Frame
    
    if "dexscreener.com" not in url:
        print(f"Ungültiger Dexscreener-Link: {url}")
        return None
    
    # Öffne den Link im Standardbrowser
    print(f"Öffne Link im Browser: {url}")
    webbrowser.open(url)
    
    screenshot_result = [None]  # Variable zum Speichern des Screenshots
    
    if parent_window:
        dialog = Toplevel(parent_window)
        dialog.title("Screenshot erstellen")
        dialog.geometry("250x120+2250+500")  # Schmaler und an den rechten Bildschirmrand
        dialog.resizable(False, False)
        dialog.transient(parent_window)
        dialog.grab_set()
        
        button_frame = Frame(dialog)
        button_frame.pack(expand=True)
        
        def on_confirm():
            try:
                # Erstelle den Screenshot sofort ohne Verzögerung
                screenshot = pyautogui.screenshot()
                screenshot_result[0] = screenshot
                dialog.destroy()
            except Exception as e:
                print(f"Fehler beim Erstellen des Screenshots: {e}")
        
        # Buttons untereinander anordnen
        Button(button_frame, text="Bestätigen", width=20, command=on_confirm).pack(pady=5)
        Button(button_frame, text="Abbrechen", width=20, command=dialog.destroy).pack(pady=5)
        
        # Warte auf Dialog-Schließung
        parent_window.wait_window(dialog)
        
        return screenshot_result[0]
    
    return None