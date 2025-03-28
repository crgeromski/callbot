# Call-Funktionen Frame
import tkinter as tk
from tkinter import messagebox
import data.storage as storage
import utils.formatters as formatters
from datetime import datetime

class CallFrame:
    def __init__(self, parent, shared_vars, main_window):
        self.parent = parent
        self.shared_vars = shared_vars
        self.main_window = main_window  # Referenz auf das Hauptfenster für den Zugriff auf Notebook usw.
        self.create_frame()
        
    def create_frame(self):
        """Erstellt den Frame für Call-Funktionen"""
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
        self.frame.grid(row=1, column=1, sticky="nsew")
        
        self.inner = tk.Frame(self.frame, bg="white")
        self.inner.pack(fill="both", expand=True, padx=5, pady=5)
        
        tk.Label(
            self.inner, 
            text="Call Funktionen", 
            font=("Arial", 11, "bold"), 
            bg="white", 
            anchor="w"
        ).pack(anchor="w", pady=(0,10))
        
        # Erstelle einen neuen Unterframe für die Buttons
        self.sheets_btn_frame = tk.Frame(self.inner, bg="white")
        self.sheets_btn_frame.pack(anchor="w", pady=(5,0))
        
        # Button "Call erstellen"
        self.btn_sheets_transfer = tk.Button(
            self.sheets_btn_frame, 
            text="Call erstellen", 
            command=lambda: [self.post_call_to_sheets(), self.main_window.notebook.select(self.main_window.tabs['calls'])]
        )
        self.btn_sheets_transfer.pack(side="left", padx=(0,10))
    
    def post_call_to_sheets(self):
        """
        Erstellt einen neuen Call und speichert ihn in der JSON-Datei.
        Aktualisiert sofort die Treeview und berechnet schon Initialwerte.
        """
        try:
            # Hole die benötigten Daten aus den Variablen
            symbol = self.shared_vars['token_symbol_var'].get()
            mcap = self.shared_vars['mcap_var'].get()
            liquidity = self.shared_vars['liq_var'].get()
            link = self.shared_vars['entry_var'].get()
            
            if not all([symbol, mcap, liquidity, link]):
                messagebox.showerror("Fehler", "Es fehlen notwendige Daten für den Call.")
                return
            
            # Erstelle neuen Call mit Initialwerten
            new_call = self.create_call_with_initial_values(symbol, mcap, liquidity, link)
            
            # Speichere den neuen Call
            storage.save_new_call(new_call)
            
            # Aktualisiere die Treeview
            if hasattr(self.main_window, 'update_calls_tree'):
                self.main_window.update_calls_tree()
                
            # Optional: Budget aktualisieren
            if hasattr(self.main_window, 'update_ui_stats'):
                self.main_window.update_ui_stats()
                                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Erstellen des Calls: {e}")
    
    def create_call_with_initial_values(self, symbol, mcap, liquidity, link):
        """
        Erstellt einen neuen Call mit sofort berechneten Initialwerten,
        ohne auf das Live-Update zu warten.
        """
        # Standardwerte für einen neuen Call
        call_data = {
            "Datum": datetime.now().strftime("%d.%m."),
            "Symbol": symbol,
            "MCAP_at_Call": mcap,
            "Link": link,
            "Aktuelles_MCAP": mcap,  # initial gleich MCAP_at_Call
            "Invest": "10"       # Fester Investitionswert: 10$
        }
        
        # Berechne sofort die X-Factor, PL_Percent und PL_Dollar Werte
        initial_mcap = formatters.parse_km(mcap)
        # Da es sich um einen neuen Call handelt, sind aktuelles MCAP und initiales MCAP gleich
        x_factor = 1.0
        pl_percent = 0.0
        pl_dollar = 0.0
        
        call_data["X_Factor"] = f"{x_factor:.1f}X"
        call_data["PL_Percent"] = f"{pl_percent:.0f}%"
        call_data["PL_Dollar"] = f"{pl_dollar:.2f}$"
        
        return call_data