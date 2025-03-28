# Angepasste Version für ui/xpost_frame.py
import tkinter as tk
import ui.styles as styles
import utils.clipboard as clipboard
import utils.browser as browser

class XPostFrame:
    def __init__(self, parent, shared_vars):
        self.parent = parent
        self.shared_vars = shared_vars
        self.last_screenshot = None  # Zum Speichern des Screenshots
        self.current_link = ""  # Für die Überwachung von Linkänderungen
        self.original_button_bg = None  # Für die X-Button
        self.original_screenshot_bg = None  # Für Screenshot-Button
        self.original_call_bg = None  # Für Call-Button
        self.link_check_id = None  # ID für after-Aufrufe
        self.create_frame()
        
    def create_frame(self):
        """Erstellt den Frame für X-Posts mit verbessertem Layout"""
        self.frame = tk.Frame(
            self.parent, 
            bg="white", 
            padx=20, 
            pady=20
        )
        self.frame.pack(fill="both", expand=True)
        
        # X-Post Label mit neuer Typografie
        title_label = tk.Label(
            self.frame, 
            text="X-Post", 
            bg="white", 
            anchor="w"
        )
        # Neue Typografie-Anwendung
        styles.apply_typography(title_label, 'section_header')
        title_label.pack(anchor="w", pady=(0, 10))
        
        # X-Post Textfeld (multiline) mit verbesserter Größenanpassung
        text_container = tk.Frame(self.frame, bg="white")
        text_container.pack(fill="x", pady=5)
        
        # Text-Widget mit reduzierter Höhe (nur 5 Zeilen) und bearbeitbar
        self.xpost_text_widget = tk.Text(
            text_container, 
            height=6,  # Höhe auf 6 Zeilen
            wrap="word", 
            relief="sunken", 
            borderwidth=2
        )
        self.xpost_text_widget.insert("1.0", "")
        # State "normal" damit das Textfeld bearbeitbar ist
        self.xpost_text_widget.config(state="normal")  
        self.xpost_text_widget.pack(fill="x", pady=(5, 10))  # Mehr Abstand unten für die Buttons
        
        # Screenshot-Buttons Bereich
        self.screenshot_frame = tk.Frame(self.frame, bg="white")
        self.screenshot_frame.pack(fill="x", pady=(0, 5))  # Einheitlicher Abstand
        
        # Konfiguriere den Screenshot-Frame mit Gewicht für den Hauptbutton
        self.screenshot_frame.columnconfigure(0, weight=1)
        
        # Screenshot erstellen Button
        self.screenshot_button = tk.Button(
            self.screenshot_frame,
            text="Screenshot erstellen",
            font=("Arial", 10, "bold"),
            height=2,
            command=self.take_chart_screenshot
        )
        # Neue Typografie-Anwendung für Button
        styles.apply_typography(self.screenshot_button, 'button_label')
        self.screenshot_button.grid(row=0, column=0, sticky="ew", columnspan=2)
        
        # Frame für Buttons
        self.btn_frame = tk.Frame(self.frame, bg="white")
        self.btn_frame.pack(fill="x", pady=5)  # Einheitlicher Abstand
        
        # Konfiguriere den Button-Frame für gleichmäßige Aufteilung
        self.btn_frame.columnconfigure(0, weight=1)
        self.btn_frame.columnconfigure(1, weight=1)
        
        # Button "Auf X posten"
        self.btn_xpost = tk.Button(
            self.btn_frame, 
            text="Auf X posten",
            font=("Arial", 10, "bold"),
            height=2,
            command=self.post_to_x
        )
        # Neue Typografie-Anwendung für Button
        styles.apply_typography(self.btn_xpost, 'button_label')
        self.btn_xpost.grid(row=0, column=0, sticky="ew", padx=(0, 2))
        
        # Call speichern Button
        self.call_button = tk.Button(
            self.btn_frame,
            text="Call speichern",
            font=("Arial", 10, "bold"),
            height=2,
            command=self.create_call
        )
        # Neue Typografie-Anwendung für Button
        styles.apply_typography(self.call_button, 'button_label')
        self.call_button.grid(row=0, column=1, sticky="ew", padx=(2, 0))
        
        # Call aufrufen Button
        self.call_recall_button = tk.Button(
            self.btn_frame,
            text="Call aufrufen",
            font=("Arial", 10, "bold"),
            height=2,
            command=self.recall_call
        )
        # Neue Typografie-Anwendung für Button
        styles.apply_typography(self.call_recall_button, 'button_label')
        self.call_recall_button.grid(row=1, column=0, columnspan=2, sticky="ew")
        
        # Starte die Überwachung auf Linkänderungen
        self.check_link_change()

    def recall_call(self):
        """
        Öffnet eine X-Suche für den aktuellen Token mit @memehuntercalls
        """
        # Hole die Token-Adresse aus den shared_vars
        token_address = self.shared_vars['token_address_var'].get()
        
        # Importiere die Browser-Funktion
        import utils.browser as browser
        
        # Erstelle die Such-URL und öffne sie
        url = browser.create_memehunter_call_search_url(token_address)
        if url:
            browser.open_link(url)

    def post_to_x(self):
        """Öffnet X.com mit dem aktuellen Post-Inhalt"""
        text = self.xpost_text_widget.get("1.0", "end").strip()
        if not text:
            tk.messagebox.showinfo("Hinweis", "Kein Text zum Posten vorhanden.")
            return
        url = browser.create_twitter_post_url(text)
        if url:
            browser.open_link(url)
            
            # Setze grünen Hintergrund (bleibt aktiv bis neuer Link)
            self.btn_xpost.config(bg="#64c264")  # Grüner Hintergrund
            
            # Speichere den aktuellen Link, um später zu prüfen ob er sich geändert hat
            self.current_link = self.shared_vars['entry_var'].get()
            
            # Beginne die Überwachung auf Linkänderungen
            self.check_link_change()

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
            
            # Aktualisiere die Treeview, wenn im main_window verfügbar
            root = self.parent.winfo_toplevel()
            if hasattr(root, 'update_calls_tree'):
                root.update_calls_tree()
            
            # Speichere die Originalfarbe beim ersten Mal
            if not hasattr(self, 'original_call_bg') or not self.original_call_bg:
                self.original_call_bg = self.call_button.cget("bg")
            
            # Setze grünen Hintergrund (bleibt aktiv bis neuer Link)
            self.call_button.config(bg="#64c264")  # Grüner Hintergrund
            
            # Speichere den aktuellen Link für Vergleiche
            self.current_link = self.shared_vars['entry_var'].get()
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Erstellen des Calls: {e}")

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
            self.screenshot_button.config(state="normal")

    def check_link_change(self):
        """Überprüft, ob sich der Link geändert hat und setzt ggf. die Button-Farben zurück"""
        # Breche alle vorherigen Überprüfungen ab
        if self.link_check_id:
            self.parent.after_cancel(self.link_check_id)
            self.link_check_id = None
            
        current_link = self.shared_vars['entry_var'].get()
        
        # Wenn sich der Link geändert hat
        if current_link != self.current_link and hasattr(self, 'current_link') and self.current_link:
            # Prüfe, ob der aktuelle Link bereits in gespeicherten Calls existiert
            import data.storage as storage
            calls = storage.load_call_data()
            
            # Prüfe, ob der Link in einem der aktiven Calls vorhanden ist
            link_already_saved = any(
                not call.get("abgeschlossen", False) and call.get("Link") == current_link 
                for call in calls
            )
            
            if link_already_saved:
                # Wenn der Link bereits gespeichert ist, setze alle Buttons auf grün
                self.btn_xpost.config(bg="#64c264")
                self.screenshot_button.config(bg="#64c264")
                self.call_button.config(bg="#64c264")
            else:
                # Wenn der Link nicht gespeichert ist, setze alle Buttons auf Standard zurück
                if hasattr(self, 'original_button_bg') and self.original_button_bg:
                    self.btn_xpost.config(bg=self.original_button_bg)
                
                if hasattr(self, 'original_screenshot_bg') and self.original_screenshot_bg:
                    self.screenshot_button.config(bg=self.original_screenshot_bg)
                
                if hasattr(self, 'original_call_bg') and self.original_call_bg:
                    self.call_button.config(bg=self.original_call_bg)
            
            # Aktualisiere den aktuellen Link
            self.current_link = current_link
        
        # Plane nächste Überprüfung (alle 500ms)
        self.link_check_id = self.parent.after(500, self.check_link_change)


    def update_xpost_container(self):
        """Befüllt das X-Post-Feld basierend auf current_data"""
        current_data = self.shared_vars['current_data']
        
        # WICHTIG: Aktualisiere die aktuellen Link-Informationen für die Button-Farbkontrolle
        new_link = self.shared_vars['entry_var'].get()
        
        # Prüfe, ob der aktuelle Link bereits in gespeicherten Calls existiert
        import data.storage as storage
        calls = storage.load_call_data()
        
        # Prüfe, ob der Link in einem der aktiven Calls vorhanden ist
        link_already_saved = any(
            not call.get("abgeschlossen", False) and call.get("Link") == new_link 
            for call in calls
        )
        
        # WICHTIG: Speichere die Button-Farben, falls noch nicht geschehen
        if not hasattr(self, 'original_button_bg') or not self.original_button_bg:
            self.original_button_bg = self.btn_xpost.cget("bg")
            
        if not hasattr(self, 'original_screenshot_bg') or not self.original_screenshot_bg:
            self.original_screenshot_bg = self.screenshot_button.cget("bg")
            
        if not hasattr(self, 'original_call_bg') or not self.original_call_bg:
            self.original_call_bg = self.call_button.cget("bg")
        
        # Setze die Farben der Buttons basierend darauf, ob der Link bereits gespeichert ist
        if link_already_saved:
            # Wenn der Link bereits gespeichert ist, setze alle Buttons auf grün
            self.btn_xpost.config(bg="#64c264")
            self.screenshot_button.config(bg="#64c264")
            self.call_button.config(bg="#64c264")
        else:
            # Wenn der Link nicht gespeichert ist, setze alle Buttons auf Standard zurück
            self.btn_xpost.config(bg=self.original_button_bg)
            self.screenshot_button.config(bg=self.original_screenshot_bg)
            self.call_button.config(bg=self.original_call_bg)
        
        # Aktualisiere den aktuellen Link
        self.current_link = new_link
        
        # Verlasse früh, wenn keine Daten vorhanden sind
        if not current_data:
            self.xpost_text_widget.delete("1.0", "end")
            return
        
        pairs = current_data.get("pairs", [])
        if not pairs:
            self.xpost_text_widget.delete("1.0", "end")
            return
        
        # Speichere den letzten Token, um Änderungen zu erkennen
        if not hasattr(self, 'last_token'):
            self.last_token = ""
        
        # Extrahiere Daten aus der API-Antwort
        pair_info = pairs[0]
        base_token = pair_info.get("baseToken", {})
        
        # Token-Symbol (mit $ Prefix)
        symbol = base_token.get("symbol", "")
        symbol_str = f"${symbol}" if symbol else "N/A"
        
        # Prüfe, ob sich der Token geändert hat
        token_changed = symbol_str != self.last_token
        self.last_token = symbol_str
        
        # Wenn sich der Token nicht geändert hat, behalte den aktuellen Text bei
        if not token_changed:
            return
        
        # Token hat sich geändert - aktualisiere den Text
        
        # Market Cap formatieren
        market_cap = pair_info.get("marketCap", pair_info.get("mcap", pair_info.get("fdv", "N/A")))
        import utils.formatters as formatters
        market_cap_str = formatters.format_k(market_cap)
        
        # Token-Adresse
        token_addr = base_token.get("address", "N/A")
        
        # Erstellen des X-Post-Textes - exaktes Format mit korrekten Zeilenumbrüchen
        xpost_text = f"\n{symbol_str}\n💰 MCAP: {market_cap_str}\n🔗 CA: {token_addr}"
        
        # Aktualisiere den Text
        self.xpost_text_widget.delete("1.0", "end")
        self.xpost_text_widget.insert("1.0", xpost_text)
            
        # Setze Cursor an den Anfang des Textes
        self.xpost_text_widget.mark_set(tk.INSERT, "1.0")

    def _check_focus_out(self, event):
        """
        Prüft, ob außerhalb des Textfelds geklickt wurde und nimmt ggf. den Fokus
        """
        # Hole das Widget, auf das geklickt wurde
        clicked_widget = event.widget
        
        # Wenn es nicht das Textfeld ist und auch kein Kind des Textfelds
        if clicked_widget != self.xpost_text_widget and not self._is_child_of_widget(clicked_widget, self.xpost_text_widget):
            # Fokus vom Textfeld nehmen
            self.parent.focus_set()
    
    def _is_child_of_widget(self, widget, parent):
        """
        Prüft rekursiv, ob ein Widget ein Kind eines anderen Widgets ist
        """
        try:
            if widget.master == parent:
                return True
            else:
                return self._is_child_of_widget(widget.master, parent)
        except:
            return False
            
    def copy_last_screenshot_to_clipboard(self):
        """
        Diese Methode wird nicht mehr verwendet, bleibt aber für die Kompatibilität
        mit anderen Teilen des Programms, die sie möglicherweise aufrufen.
        """
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