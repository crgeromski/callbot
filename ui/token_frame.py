# Token-Daten-Frame
import tkinter as tk
import ui.styles as styles

class TokenFrame:
    def __init__(self, parent, shared_vars, main_window=None):
        self.parent = parent
        self.shared_vars = shared_vars
        self.main_window = main_window
        self.create_frame()

    def create_frame(self):
        """Erstellt den Frame für Token-Daten"""
        # Wir erstellen einen äußeren Frame mit Padding
        self.frame = tk.Frame(self.parent, bg="white", padx=20, pady=20)
        self.frame.pack(fill="both", expand=True)
        
        # Titel für Token-Daten
        tk.Label(
            self.frame, 
            text="Token-Daten", 
            font=("Arial", 11, "bold"), 
            bg="white", 
            anchor="w"
        ).pack(anchor="w", pady=(0,10))
        
        # Container für die Datenzeilen
        data_container = tk.Frame(self.frame, bg="white")
        data_container.pack(fill="both", expand=True)
        data_container.columnconfigure(1, weight=1)
        
        # Datenzeilen mit vorhandenem Styling
        styles.create_data_row(data_container, "Blockchain", self.shared_vars['token_blockchain_var'], 1)
        styles.create_data_row(data_container, "Token-Name", self.shared_vars['token_name_var'], 2)
        styles.create_data_row(data_container, "Symbol", self.shared_vars['token_symbol_var'], 3)
        styles.create_data_row(data_container, "Token-Adresse", self.shared_vars['token_address_var'], 4)