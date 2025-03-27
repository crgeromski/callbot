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
        # Datenzeilen mit vorhandenem Styling
        styles.create_link_row(data_container, "DexLink", self.shared_vars['dexscreener_var'], 1)
        styles.create_link_row(data_container, "Website", self.shared_vars['website_var'], 2, 
                              token_name_var=self.shared_vars['token_name_var'], is_website=True)
        styles.create_link_row(data_container, "Twitter", self.shared_vars['twitter_var'], 3)
        styles.create_link_row(data_container, "Telegram", self.shared_vars['telegram_var'], 4)
        styles.create_link_row(data_container, "Discord", self.shared_vars['discord_var'], 5)

        # Wir entfernen den Screenshot Button von hier und verschieben ihn in den XPostFrame

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
        if hasattr(self.main_window, 'xpost_frame') and hasattr(self.main_window.xpost_frame, 'screenshot_button'):
            self.main_window.xpost_frame.screenshot_button.config(state="disabled")
        
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
                
                # Aktiviere den Kopier-Button im XPostFrame
                if hasattr(self.main_window, 'xpost_frame') and hasattr(self.main_window.xpost_frame, 'copy_last_screenshot_button'):
                    self.main_window.xpost_frame.copy_last_screenshot_button.config(state="normal")
                
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
            # Reaktiviere den Button im XPostFrame
            if hasattr(self.main_window, 'xpost_frame') and hasattr(self.main_window.xpost_frame, 'screenshot_button'):
                self.main_window.xpost_frame.screenshot_button.config(state="normal")

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
        if hasattr(self.main_window, 'xpost_frame') and hasattr(self.main_window.xpost_frame, 'screenshot_button'):
            self.main_window.xpost_frame.screenshot_button.config(state="normal")
        
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