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
            
            # Visuelles Feedback für den Button
            original_bg = self.call_button.cget("bg")
            self.call_button.config(bg="#64c264")  # Grüner Hintergrund
            
            # Zurücksetzen nach 750 Millisekunden
            self.call_button.after(1500, lambda: self.call_button.config(bg=original_bg))
                
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

        # Call speichern Button
        button_frame = tk.Frame(self.frame, bg="white")
        button_frame.pack(fill="x", pady=10)

        self.call_button = tk.Button(
            button_frame,
            text="Call speichern",
            font=("Arial", 10, "bold"),
            width=20,  # Feste Breite für Konsistenz
            height=2,
            command=self.create_call
        )
        self.call_button.pack(pady=5)  # Dieser Befehl fehlt - dadurch wird der Button nicht angezeigt

        # Zentrierung des Buttons im Container
        button_frame.update_idletasks()
        button_width = self.call_button.winfo_reqwidth()
        button_frame.pack_propagate(False)
        button_frame.configure(height=40, width=button_width)

        # Screenshot-Button Bereich
        screenshot_frame = tk.Frame(self.frame, bg="white")
        screenshot_frame.pack(fill="x", pady=5)

        # Erstelle einen Frame für die Screenshots-Buttons nebeneinander
        screenshot_buttons_frame = tk.Frame(screenshot_frame, bg="white")
        screenshot_buttons_frame.pack(pady=5)

        # Screenshot erstellen Button
        self.screenshot_button = tk.Button(
            screenshot_buttons_frame,
            text="Screenshot erstellen",
            font=("Arial", 10, "bold"),
            command=self.take_chart_screenshot
        )
        self.screenshot_button.pack(side="left")

        # Button zum erneuten Kopieren des letzten Screenshots
        self.copy_last_screenshot_button = tk.Button(
            screenshot_buttons_frame,
            text="📋",
            width=2,
            command=self.copy_last_screenshot_to_clipboard
        )
        self.copy_last_screenshot_button.pack(side="left", padx=(5, 0))
        self.copy_last_screenshot_button.config(state="disabled")  # Initial deaktiviert

    

    def take_chart_screenshot(self):
        """Erstellt einen Screenshot des Dexscreener-Charts"""
        from utils.screenshot import take_chart_screenshot
        import os
        
        # Hole den Dexscreener-Link
        link = self.shared_vars['dexscreener_var'].get()
        
        if not link or link == "N/A" or "dexscreener.com" not in link:
            from tkinter import messagebox
            messagebox.showerror("Fehler", "Kein gültiger Dexscreener-Link vorhanden.")
            return
        
        # Deaktiviere den Screenshot-Button während der Erstellung
        self.screenshot_button.config(state="disabled")
        
        try:
            # Starte den Screenshot-Prozess
            screenshot = take_chart_screenshot(link, self.parent)
            
            # Wenn ein Screenshot erstellt wurde, kopiere ihn in die Zwischenablage
            if screenshot:
                # Importiere die benötigten Module
                import io
                from PIL import Image
                
                # Speichere das Bild in einer globalen Variable für späteren Zugriff
                self.last_screenshot = screenshot
                
                # Aktiviere den Kopier-Button
                self.copy_last_screenshot_button.config(state="normal")
                
                # Kopiere in die Zwischenablage
                import win32clipboard
                from io import BytesIO
                
                output = BytesIO()
                screenshot.convert('RGB').save(output, 'BMP')
                data = output.getvalue()[14:]  # Die BMP-Header entfernen
                output.close()
                
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
                win32clipboard.CloseClipboard()
                
                # Keine Erfolgsmeldung mehr
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Fehler", f"Fehler beim Erstellen des Screenshots: {str(e)}")
        finally:
            # Reaktiviere den Button
            self.screenshot_button.config(state="normal")

    def copy_last_screenshot_to_clipboard(self):
        """Kopiert das letzte erstellte Screenshot in die Zwischenablage"""
        if hasattr(self, 'last_screenshot') and self.last_screenshot:
            try:
                import win32clipboard
                from io import BytesIO
                
                output = BytesIO()
                self.last_screenshot.convert('RGB').save(output, 'BMP')
                data = output.getvalue()[14:]  # Die BMP-Header entfernen
                output.close()
                
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
                win32clipboard.CloseClipboard()
            except Exception as e:
                from tkinter import messagebox
                messagebox.showerror("Fehler", f"Fehler beim Kopieren des Screenshots: {str(e)}")


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