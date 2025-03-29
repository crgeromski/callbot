# Empfehlungsframe ohne RugCheck-Verweise
import tkinter as tk
import ui.styles as styles

class RecommendationFrame:
    def __init__(self, parent, shared_vars, main_window=None):
        self.parent = parent
        self.shared_vars = shared_vars
        self.main_window = main_window
        self.create_frame()
        
    def create_frame(self):
        """Erstellt einen Frame für Empfehlungen"""
        # Wir erstellen einen einfachen Frame mit einheitlicher Hintergrundfarbe
        self.frame = tk.Frame(
            self.parent, 
            bg="#ebebeb",  
            padx=0,
            pady=0
        )
        self.frame.pack(fill="both", expand=True)
        
        # Überschrift mit Typografie
        title_label = tk.Label(
            self.frame,
            text="",
            font=("Arial", 10),
            bg="#ebebeb",
            fg="#888888"
        )
        # Typografie-Anwendung
        styles.apply_typography(title_label, 'section_header')
        title_label.pack(anchor="center", pady=(10,5))
        
        # Informations-Label
        info_label = tk.Label(
            self.frame,
            text="",
            font=("Arial", 10),
            bg="#ebebeb",
            fg="#888888"
        )
        info_label.pack(anchor="center", expand=True)