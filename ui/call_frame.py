# Call-Funktionen Frame
import tkinter as tk
from tkinter import messagebox
import data.storage as storage

class CallFrame:
    def __init__(self, parent, shared_vars, main_window):
        self.parent = parent
        self.shared_vars = shared_vars
        self.main_window = main_window  # Referenz auf das Hauptfenster für den Zugriff auf Notebook usw.
        self.create_frame()
        
    def create_frame(self):
        """Erstellt den Frame für Call-Funktionen"""
        self.frame = tk.Frame(self.parent, bg="white", padx=15, pady=15, bd=1, relief="groove")
        self.frame.grid(row=1, column=1, sticky="nsew")
        
        tk.Label(self.frame, text="Call Funktionen", font=("Arial", 12, "bold"), bg="white", anchor="w").pack(anchor="w", pady=(0,10))
        
        # Erstelle einen neuen Unterframe für die Buttons
        self.sheets_btn_frame = tk.Frame(self.frame, bg="white")
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
            if hasattr(self.main_window, 'update_calls_tree'):
                self.main_window.update_calls_tree()
                
            messagebox.showinfo("Erfolg", "Call wurde erfolgreich erstellt.")
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Erstellen des Calls: {e}")