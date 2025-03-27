# Neue version für ui/recommendation_frame.py
import tkinter as tk

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
            bg="#e8e8ff",  # Leicht bläulicher Hintergrund zur Visualisierung
            padx=0,
            pady=0
        )
        self.frame.pack(fill="both", expand=True)
        
        # Optional: Text-Label, um zu bestätigen, dass der Container existiert
        tk.Label(
            self.frame,
            text="Leer (30%)",
            font=("Arial", 10),
            bg="#e8e8ff",
            fg="#888888"
        ).pack(anchor="center", expand=True)