# Token-Daten-Frame
import tkinter as tk
import ui.styles as styles
import utils.browser as browser

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
        
        # Erstelle einen Button für DexScreener Link - NEUER CODE
        dexlink_frame = tk.Frame(data_container, bg="white")
        dexlink_frame.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        
        dexscreener_button = tk.Button(
            dexlink_frame, 
            text="DexScreener Link", 
            font=("Arial", 10, "bold"),
            height=2,
            command=lambda: self.open_dexscreener()
        )
        dexscreener_button.pack(fill="x", expand=True, pady=(5, 0))
    
    def open_dexscreener(self):
        """Öffnet den DexScreener Link im Browser"""
        link = self.shared_vars['dexscreener_var'].get()
        if link and link != "N/A":
            browser.open_link(link)
        else:
            from tkinter import messagebox
            messagebox.showerror("Fehler", "Kein gültiger DexScreener-Link vorhanden.")