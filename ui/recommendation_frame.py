# Empfehlungs-Frame
import tkinter as tk
from tkinter import messagebox
import data.storage as storage

class RecommendationFrame:
    def __init__(self, parent, shared_vars, main_window=None):
        self.parent = parent
        self.shared_vars = shared_vars
        self.main_window = main_window
        self.create_frame()
        
    def create_frame(self):
        """Erstellt den Frame für die Empfehlungsfunktion"""
        self.frame = tk.Frame(
            self.parent, 
            bg="white", 
            padx=20, 
            pady=20
        )
        self.frame.grid(row=0, column=0, sticky="nsew")  # Ändern von pack() zu grid()
        
        # Titel
        tk.Label(
            self.frame, 
            text="Empfehlung & Call-Erstellung", 
            font=("Arial", 11, "bold"), 
            bg="white", 
            anchor="w"
        ).pack(anchor="w", pady=(0,10))

        # Platzhalter für zukünftige Empfehlungsfunktion
        placeholder = tk.Frame(self.frame, bg="#f0f0f0", bd=1, relief="solid")
        placeholder.pack(fill="both", expand=True, pady=10)
        
        tk.Label(
            placeholder,
            text="Empfehlungsfunktion wird derzeit entwickelt...",
            font=("Arial", 10, "italic"),
            bg="#f0f0f0"
        ).pack(expand=True, pady=20)
    
    def create_call(self):
        """
        Erstellt einen neuen Call und speichert ihn in der JSON-Datei.
        (Übernommen aus der alten call_frame.py)
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
            
            # Erstelle neuen Call
            new_call = storage.create_new_call(symbol, mcap, liquidity, link)
            
            # Speichere den neuen Call
            storage.save_new_call(new_call)
            
            # Aktualisiere die Treeview
            if self.main_window and hasattr(self.main_window, 'update_calls_tree'):
                self.main_window.update_calls_tree()
                
            # Wechsle zum Calls-Tab
            if self.main_window and hasattr(self.main_window, 'notebook'):
                self.main_window.notebook.select(self.main_window.tabs['calls'])
                                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Erstellen des Calls: {e}")