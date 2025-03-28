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
        
        # Titel mit neuer Typografie
        title_label = tk.Label(
            self.frame, 
            text="Social Media Kanäle", 
            bg="white", 
            anchor="w"
        )
        # Neue Typografie-Anwendung
        styles.apply_typography(title_label, 'section_header')
        title_label.pack(anchor="w", pady=(0,10))
        
        # Container für die Datenzeilen
        data_container = tk.Frame(self.frame, bg="white")
        data_container.pack(fill="both", expand=True)
        data_container.columnconfigure(1, weight=1)
        
        # Datenzeilen mit vorhandenem Styling
        styles.create_link_row(data_container, "Website", self.shared_vars['website_var'], 1, 
                              token_name_var=self.shared_vars['token_name_var'], is_website=True)
        styles.create_link_row(data_container, "Twitter", self.shared_vars['twitter_var'], 2)
        styles.create_link_row(data_container, "Telegram", self.shared_vars['telegram_var'], 3)
        styles.create_link_row(data_container, "Discord", self.shared_vars['discord_var'], 4)
        
        # X-Suche Button hinzufügen
        x_search_frame = tk.Frame(data_container, bg="white")
        x_search_frame.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        
        x_search_button = tk.Button(
            x_search_frame, 
            text="$ und CA X Suche", 
            height=2,
            command=self.open_x_search
        )
        # Neue Typografie-Anwendung für Button
        styles.apply_typography(x_search_button, 'button_label')
        x_search_button.pack(fill="x", expand=True, pady=(5, 0))

    def open_x_search(self):
        """Öffnet X (Twitter) mit Suche nach Symbol ODER Contract-Adresse"""
        import urllib.parse
        import webbrowser
        
        # Hole Symbol und Adresse aus den Shared Vars
        symbol = self.shared_vars['token_symbol_var'].get()
        address = self.shared_vars['token_address_var'].get()
        
        if not symbol or not address or symbol == "N/A" or address == "N/A":
            from tkinter import messagebox
            messagebox.showerror("Fehler", "Symbol oder Contract-Adresse nicht verfügbar.")
            return
        
        # Entferne $ vom Symbol, falls vorhanden, und füge es wieder hinzu
        if symbol.startswith('$'):
            symbol_clean = symbol
        else:
            symbol_clean = '$' + symbol
        
        # Erstelle den Suchquery im Format "($SYMBOL OR ADRESSE)"
        search_query = f"({symbol_clean} OR {address})"
        
        # URL-encode des Suchbegriffs
        encoded_query = urllib.parse.quote(search_query)
        
        # Erstelle die vollständige URL mit dem "Neuste" Filter (f=live)
        url = f"https://x.com/search?q={encoded_query}&src=typed_query&f=live"
        
        # Öffne die URL im Standardbrowser
        webbrowser.open(url)

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
                
                # Speichere die Originalfarbe beim ersten Mal
                if not hasattr(self, 'original_screenshot_bg') or not self.original_screenshot_bg:
                    self.original_screenshot_bg = self.screenshot_button.cget("bg")
                
                # Setze grünen Hintergrund (bleibt aktiv bis neuer Link)
                self.screenshot_button.config(bg="#64c264")  # Grüner Hintergrund
                
                # Speichere den aktuellen Link für Vergleiche
                self.current_link = self.shared_vars['entry_var'].get()
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Fehler", f"Fehler beim Erstellen des Screenshots: {str(e)}")
        finally:
            # Reaktiviere den Button
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