# Neue version für ui/recommendation_frame.py
import tkinter as tk
import ui.styles as styles

class RecommendationFrame:
    def __init__(self, parent, shared_vars, main_window=None):
        self.parent = parent
        self.shared_vars = shared_vars
        self.main_window = main_window
        self.create_frame()
        
    def create_frame(self):
        """Erstellt einen leeren Frame für zukünftige Empfehlungen"""
        # Wir erstellen einen einfachen leeren Frame mit temporärer Hintergrundfarbe
        self.frame = tk.Frame(
            self.parent, 
            bg="#ebebeb",  
            padx=0,
            pady=0
        )
        self.frame.pack(fill="both", expand=True)
        
        # Überschrift mit neuer Typografie
        title_label = tk.Label(
            self.frame,
            text="",
            font=("Arial", 10),
            bg="#ebebeb",
            fg="#888888"
        )
        # Neue Typografie-Anwendung
        styles.apply_typography(title_label, 'section_header')
        title_label.pack(anchor="center", pady=(10,5))
        
        # Optional: Text-Label, um zu bestätigen, dass der Container existiert
        info_label = tk.Label(
            self.frame,
            text="",
            font=("Arial", 10),
            bg="#ebebeb",
            fg="#888888"
        )
        info_label.pack(anchor="center", expand=True)