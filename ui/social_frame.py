# Social Media Frame
import tkinter as tk
import ui.styles as styles

class SocialFrame:
    def create_frame(self):
        """Erstellt den Frame für Social Media Kanäle"""
        self.frame = tk.Frame(
            self.parent, 
            bg="white", 
            padx=20, 
            pady=20
        )
        self.frame.pack(fill="both", expand=True)
        
        # Titel
        tk.Label(
            self.frame, 
            text="Social Media Kanäle", 
            font=("Arial", 11, "bold"), 
            bg="white", 
            anchor="w"
        ).pack(anchor="w", pady=(0,10))
        
        # Container für die Datenzeilen
        data_container = tk.Frame(self.frame, bg="white")
        data_container.pack(fill="both", expand=True)
        data_container.columnconfigure(1, weight=1)
        
        # Datenzeilen mit vorhandenem Styling
        styles.create_link_row(data_container, "DexLink", self.shared_vars['dexscreener_var'], 1)
        styles.create_link_row(data_container, "Website", self.shared_vars['website_var'], 2)
        styles.create_link_row(data_container, "Twitter", self.shared_vars['twitter_var'], 3)
        styles.create_link_row(data_container, "Telegram", self.shared_vars['telegram_var'], 4)
        styles.create_link_row(data_container, "Discord", self.shared_vars['discord_var'], 5)

        # Call erstellen Button
        button_frame = tk.Frame(self.frame, bg="white")
        button_frame.pack(fill="x", pady=10)

        self.call_button = tk.Button(
            button_frame,
            text="Call erstellen",
            font=("Arial", 10, "bold"),  # Bold-Schrift
            height=2,  # Erhöhe Höhe um 2px
            command=self.create_call
        )
        self.call_button.pack(pady=5)

        # Zentrierung des Buttons im Container
        button_frame.update_idletasks()
        button_width = self.call_button.winfo_reqwidth()
        button_frame.pack_propagate(False)
        button_frame.configure(height=40, width=button_width)


    def create_call(self):
        """
        Erstellt einen neuen Call und speichert ihn in der JSON-Datei.
        """
        try:
            # Importiere storage hier, um zirkuläre Importe zu vermeiden
            import data.storage as storage
            from tkinter import messagebox
            
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
            
            # Aktualisiere die Treeview, wenn main_window verfügbar ist
            if hasattr(self, 'main_window') and self.main_window and hasattr(self.main_window, 'update_calls_tree'):
                self.main_window.update_calls_tree()
                
            # Wechsle zum Calls-Tab, wenn main_window verfügbar ist
            if hasattr(self, 'main_window') and self.main_window and hasattr(self.main_window, 'notebook'):
                self.main_window.notebook.select(self.main_window.tabs['calls'])
                
            messagebox.showinfo("Erfolg", "Call wurde erfolgreich erstellt.")
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Erstellen des Calls: {e}")


    def __init__(self, parent, shared_vars, main_window=None):
        self.parent = parent
        self.shared_vars = shared_vars
        self.main_window = main_window
        self.create_frame()