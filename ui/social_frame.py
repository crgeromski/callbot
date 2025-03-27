# Social Media Frame
import tkinter as tk
import ui.styles as styles

class SocialFrame:
    def __init__(self, parent, shared_vars, main_window=None):
        self.parent = parent
        self.shared_vars = shared_vars
        self.main_window = main_window
        self.create_frame()
        
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
                
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Erstellen des Calls: {e}")

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

        # Screenshot-Button hinzufügen (nach dem Call-Button)
        screenshot_frame = tk.Frame(self.frame, bg="white")
        screenshot_frame.pack(fill="x", pady=5)
        
        self.screenshot_button = tk.Button(
            screenshot_frame,
            text="Chart Screenshot erstellen",
            font=("Arial", 10, "bold"),  # Bold-Schrift
            command=self.take_chart_screenshot
        )
        self.screenshot_button.pack(pady=5)

    def take_chart_screenshot(self):
        """Erstellt einen Screenshot des Dexscreener-Charts"""
        from tkinter import messagebox
        import threading
        from utils.screenshot import take_chart_screenshot
        
        # Hole den Dexscreener-Link
        link = self.shared_vars['dexscreener_var'].get()
        
        if not link or link == "N/A" or "dexscreener.com" not in link:
            messagebox.showerror("Fehler", "Kein gültiger Dexscreener-Link vorhanden.")
            return
        
        # Info-Dialog
        info_dialog = tk.Toplevel(self.parent)
        info_dialog.title("Screenshot wird erstellt")
        info_dialog.geometry("300x100")
        info_dialog.resizable(False, False)
        info_dialog.transient(self.parent)
        info_dialog.grab_set()
        
        info_label = tk.Label(
            info_dialog,
            text="Screenshot wird erstellt...\nBitte warten.",
            font=("Arial", 12)
        )
        info_label.pack(expand=True)
        
        # Deaktiviere den Screenshot-Button während der Erstellung
        self.screenshot_button.config(state="disabled")
        
        # Funktion, die im Thread ausgeführt wird
        def screenshot_thread():
            screenshot_path = take_chart_screenshot(link)
            
            # UI-Updates müssen im Hauptthread erfolgen
            self.parent.after(0, lambda: self._handle_screenshot_result(screenshot_path, info_dialog))
        
        # Starte den Screenshot-Prozess in einem separaten Thread
        threading.Thread(target=screenshot_thread).start()

    def _handle_screenshot_result(self, screenshot_path, info_dialog):
        """Verarbeitet das Ergebnis des Screenshots"""
        from tkinter import messagebox
        import os
        
        # Reaktiviere den Screenshot-Button
        self.screenshot_button.config(state="normal")
        
        # Schließe den Info-Dialog
        info_dialog.destroy()
        
        # Zeige eine Erfolgsmeldung oder Fehlermeldung
        if screenshot_path:
            # Zeigen wir den absoluten Pfad an
            abs_path = os.path.abspath(screenshot_path)
            
            messagebox.showinfo(
                "Screenshot erstellt", 
                f"Der Chart-Screenshot wurde erfolgreich erstellt und gespeichert unter:\n{abs_path}"
            )
        else:
            messagebox.showerror(
                "Fehler", 
                "Es ist ein Fehler beim Erstellen des Screenshots aufgetreten.\n"
                "Bitte stelle sicher, dass der Dexscreener-Link gültig ist."
            )