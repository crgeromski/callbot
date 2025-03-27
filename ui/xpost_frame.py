# Angepasste Version für ui/xpost_frame.py
import tkinter as tk
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
        
        # X-Post Label
        tk.Label(
            self.frame, 
            text="X-Post", 
            font=("Arial", 11, "bold"), 
            bg="white", 
            anchor="w"
        ).pack(anchor="w", pady=(0, 10))
        
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
        
        # Event-Handler für Klick außerhalb des Textfeldes
        def on_focus_out(event):
            # Fokus vom Textfeld nehmen, wenn woanders hingeklickt wird
            self.parent.focus_set()
            
        # Binding zum Hauptfenster hinzufügen
        root = self.parent.winfo_toplevel()
        root.bind("<Button-1>", lambda event: self._check_focus_out(event))
        
        # Screenshot-Buttons Bereich - NEUES LAYOUT: Screenshot-Button jetzt vor den anderen Buttons
        self.screenshot_frame = tk.Frame(self.frame, bg="white")
        self.screenshot_frame.pack(fill="x", pady=10)
        
        # Konfiguriere den Screenshot-Frame mit Gewicht für den Hauptbutton
        self.screenshot_frame.columnconfigure(0, weight=1)
        
        # Screenshot erstellen Button - jetzt über die gesamte Breite
        self.screenshot_button = tk.Button(
            self.screenshot_frame,
            text="Screenshot erstellen",
            font=("Arial", 10, "bold"),
            height=2,
            command=self.take_chart_screenshot
        )
        self.screenshot_button.grid(row=0, column=0, sticky="ew", columnspan=2)
        
        # Frame für Buttons mit verbesserter Positionierung und Ausrichtung - JETZT NACH DEM SCREENSHOT-FRAME
        self.btn_frame = tk.Frame(self.frame, bg="white")
        self.btn_frame.pack(fill="x", pady=10)
        
        # Konfiguriere den Button-Frame für gleichmäßige Aufteilung
        self.btn_frame.columnconfigure(0, weight=1)
        self.btn_frame.columnconfigure(1, weight=1)
        
        # Button "Auf X posten" - jetzt links mit Gewicht
        self.btn_xpost = tk.Button(
            self.btn_frame, 
            text="Auf X posten",
            font=("Arial", 10, "bold"),
            height=2,
            command=self.post_to_x
        )
        self.btn_xpost.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        # Call speichern Button - jetzt rechts mit Gewicht
        self.call_button = tk.Button(
            self.btn_frame,
            text="Call speichern",
            font=("Arial", 10, "bold"),
            height=2,
            command=self.create_call
        )
        self.call_button.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
        # Starte die Überwachung auf Linkänderungen
        self.check_link_change()
    
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
        
        # Wenn sich der Link geändert hat, Buttons zurücksetzen
        if current_link != self.current_link and hasattr(self, 'current_link') and self.current_link:
            # X-Button zurücksetzen
            if hasattr(self, 'original_button_bg') and self.original_button_bg:
                self.btn_xpost.config(bg=self.original_button_bg)
                
            # Screenshot-Button zurücksetzen
            if hasattr(self, 'original_screenshot_bg') and self.original_screenshot_bg:
                self.screenshot_button.config(bg=self.original_screenshot_bg)
                
            # Call-Button zurücksetzen
            if hasattr(self, 'original_call_bg') and self.original_call_bg:
                self.call_button.config(bg=self.original_call_bg)
                
            # Aktuellen Link aktualisieren
            self.current_link = current_link
        
        # Plane nächste Überprüfung (alle 500ms)
        self.link_check_id = self.parent.after(500, self.check_link_change)
    
    def update_xpost_container(self):
        """Befüllt das X-Post-Feld basierend auf current_data"""
        current_data = self.shared_vars['current_data']
        
        # WICHTIG: Aktualisiere die aktuellen Link-Informationen für die Button-Farbkontrolle
        self.current_link = self.shared_vars['entry_var'].get()
        
        # WICHTIG: Setze die Button-Farben zurück
        if hasattr(self, 'btn_xpost'):
            self.btn_xpost.config(bg="SystemButtonFace")
            self.original_button_bg = "SystemButtonFace"
            
        if hasattr(self, 'screenshot_button'):
            self.screenshot_button.config(bg="SystemButtonFace")
            self.original_screenshot_bg = "SystemButtonFace"
            
        if hasattr(self, 'call_button'):
            self.call_button.config(bg="SystemButtonFace")
            self.original_call_bg = "SystemButtonFace"
        
        if not current_data:
            self.xpost_text_widget.delete("1.0", "end")
            return
        
        pairs = current_data.get("pairs", [])
        if not pairs:
            self.xpost_text_widget.delete("1.0", "end")
            return
        
        pair_info = pairs[0]
        base_token = pair_info.get("baseToken", {})
        symbol = base_token.get("symbol", "")
        symbol_str = f"${symbol}" if symbol else "N/A"
        token_addr = base_token.get("address", "N/A")
        market_cap = pair_info.get("marketCap",
                                  pair_info.get("mcap",
                                              pair_info.get("fdv", "N/A")))
        try:
            mc_val = float(market_cap)
            market_cap_str = f"{int(round(mc_val/1000))}K"
        except:
            market_cap_str = "N/A"
        
        xpost_text = f"\n💰 MCAP Entry: ${market_cap_str}\n{symbol_str}\n🔗 CA: {token_addr}"
        
        # Aktuellen Text speichern und Cursor-Position merken
        cursor_pos = self.xpost_text_widget.index(tk.INSERT)
        
        # Überprüfen ob der Text bereits bearbeitet wurde und inhaltlich anders ist
        current_text = self.xpost_text_widget.get("1.0", "end").strip()
        if current_text and current_text != xpost_text:
            # Text wurde bereits bearbeitet, nicht überschreiben
            return
            
        # Ansonsten Text aktualisieren
        self.xpost_text_widget.delete("1.0", "end")
        self.xpost_text_widget.insert("1.0", xpost_text)
        
        # Setze Cursor an den Anfang des Textes, damit der Nutzer sofort schreiben kann
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