# Future Function Frame 1
import tkinter as tk

class FutureFunctionFrame1:
    def __init__(self, parent, shared_vars):
        self.parent = parent
        self.shared_vars = shared_vars
        self.create_frame()
        
    def create_frame(self):
        """Erstellt den Frame für zukünftige Funktionen (1)"""
        self.frame = tk.Frame(
            self.parent, 
            bg="white", 
            padx=20, 
            pady=20, 
            bd=1, 
            relief="solid",
            highlightbackground="#cccccc",
            highlightthickness=1
        )
        self.frame.grid(row=2, column=0, sticky="nsew")
        
        self.inner = tk.Frame(self.frame, bg="white")
        self.inner.pack(fill="both", expand=True, padx=5, pady=5)
        
        tk.Label(
            self.inner, 
            text="Zukünftige Funktion", 
            font=("Arial", 11, "bold"), 
            bg="white", 
            anchor="w"
        ).pack(anchor="w")