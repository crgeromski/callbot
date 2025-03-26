# Token-Daten-Frame
import tkinter as tk
import ui.styles as styles

class TokenFrame:
    def create_frame(self):
        """Erstellt den Frame für Token-Daten"""
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
        
        self.frame.grid(row=0, column=0, sticky="nsew")
        
        # Konfiguriere die Spalten für responsive Entry-Felder
        self.frame.columnconfigure(1, weight=1)
        
        # Nur DexLink und Paste-Button anzeigen, wenn main_window verfügbar ist
        if self.main_window is not None:
            # DexScreener Link-Eingabe
            tk.Label(
                self.frame, 
                text="DexLink Eingabe", 
                font=("Arial", 11, "bold"), 
                bg="white", 
                anchor="w"
            ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0,5))
            
            entry_frame = tk.Frame(self.frame, bg="white")
            entry_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0,15))
            entry_frame.columnconfigure(0, weight=1)
            
            entry = tk.Entry(entry_frame, textvariable=self.shared_vars['entry_var'])
            entry.grid(row=0, column=0, sticky="ew", padx=(0,5))
            entry.bind("<Return>", lambda event: self.main_window.fetch_data())
            
            # Paste-Button
            paste_btn = tk.Button(
                entry_frame, 
                text="📋", 
                width=2,
                command=self.main_window.paste_and_fetch
            )
            paste_btn.grid(row=0, column=1)
            
            # Titel für Token-Daten
            tk.Label(
                self.frame, 
                text="Token-Daten", 
                font=("Arial", 11, "bold"), 
                bg="white", 
                anchor="w"
            ).grid(row=2, column=0, columnspan=3, sticky="w", pady=(0,10))
            
            # Token-Daten-Zeilen starten bei row=3
            styles.create_data_row(self.frame, "Blockchain", self.shared_vars['token_blockchain_var'], 3)
            styles.create_data_row(self.frame, "Token-Name", self.shared_vars['token_name_var'], 4)
            styles.create_data_row(self.frame, "Symbol", self.shared_vars['token_symbol_var'], 5)
            styles.create_data_row(self.frame, "Token-Adresse", self.shared_vars['token_address_var'], 6)
        else:
            # Original-Layout ohne DexLink-Eingabe
            tk.Label(
                self.frame, 
                text="Token-Daten", 
                font=("Arial", 11, "bold"), 
                bg="white", 
                anchor="w"
            ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0,10))
            
            # Datenzeilen mit vorhandenem Styling
            styles.create_data_row(self.frame, "Blockchain", self.shared_vars['token_blockchain_var'], 1)
            styles.create_data_row(self.frame, "Token-Name", self.shared_vars['token_name_var'], 2)
            styles.create_data_row(self.frame, "Symbol", self.shared_vars['token_symbol_var'], 3)
            styles.create_data_row(self.frame, "Token-Adresse", self.shared_vars['token_address_var'], 4)
        
        # Titel für Token-Daten
        tk.Label(
            self.frame, 
            text="Token-Daten", 
            font=("Arial", 11, "bold"), 
            bg="white", 
            anchor="w"
        ).grid(row=2, column=0, columnspan=3, sticky="w", pady=(0,10))
        
        # Datenzeilen mit vorhandenem Styling
        styles.create_data_row(self.frame, "Blockchain", self.shared_vars['token_blockchain_var'], 1)
        styles.create_data_row(self.frame, "Token-Name", self.shared_vars['token_name_var'], 2)
        styles.create_data_row(self.frame, "Symbol", self.shared_vars['token_symbol_var'], 3)
        styles.create_data_row(self.frame, "Token-Adresse", self.shared_vars['token_address_var'], 4)

    def __init__(self, parent, shared_vars, main_window=None):
        self.parent = parent
        self.shared_vars = shared_vars
        self.main_window = main_window
        self.create_frame()