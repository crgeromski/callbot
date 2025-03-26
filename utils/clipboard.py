# Zwischenablage-Funktionen
import tkinter as tk

def copy_to_clipboard(root, value: str):
    """Kopiert einen Wert in die Zwischenablage."""
    root.clipboard_clear()
    root.clipboard_append(value)
    root.update()  # Stellt sicher, dass die Zwischenablage aktualisiert wird