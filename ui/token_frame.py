# Token-Daten-Frame
import tkinter as tk
import ui.styles as styles

class TokenFrame:
    def __init__(self, parent, shared_vars):
        self.parent = parent
        self.shared_vars = shared_vars
        self.create_frame()
        
    def create_frame(self):
        """Erstellt den Frame für Token-Daten"""
        self.frame = tk.Frame(
            self.parent, 
            bg="white", 
            padx=10, 
            pady=10, 
            bd=1, 
            relief="solid"
        )
        self.frame.grid(row=0, column=0, sticky="nsew")
        
        self.inner = tk.Frame(self.frame, bg="white")
        self.inner.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Titel
        tk.Label(
            self.inner, 
            text="Token-Daten", 
            font=("Arial", 11, "bold"), 
            bg="white", 
            anchor="w"
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0,10))
        
        # Datenzeilen mit vorhandenem Styling
        styles.create_data_row(self.inner, "Blockchain", self.shared_vars['token_blockchain_var'], 1)
        styles.create_data_row(self.inner, "Token-Name", self.shared_vars['token_name_var'], 2)
        styles.create_data_row(self.inner, "Symbol", self.shared_vars['token_symbol_var'], 3)
        styles.create_data_row(self.inner, "Token-Adresse", self.shared_vars['token_address_var'], 4)