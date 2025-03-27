# Angepasste Version für ui/xpost_frame.py
import tkinter as tk
import utils.clipboard as clipboard
import utils.browser as browser

class XPostFrame:
    def __init__(self, parent, shared_vars):
        self.parent = parent
        self.shared_vars = shared_vars
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
        text_container.pack(fill="both", expand=True, pady=5)
        
        # Text-Widget mit reduzierter Höhe (nur 5 Zeilen) und bearbeitbar
        self.xpost_text_widget = tk.Text(
            text_container, 
            height=6,  # Reduzierte Höhe auf 5 Zeilen
            wrap="word", 
            relief="sunken", 
            borderwidth=2
        )
        self.xpost_text_widget.insert("1.0", "")
        # State "normal" damit das Textfeld bearbeitbar ist
        self.xpost_text_widget.config(state="normal")  
        self.xpost_text_widget.pack(fill="x", pady=5)  # fill="x" statt "both" damit es nicht vertikal expandiert
        
        # Event-Handler für Klick außerhalb des Textfeldes
        def on_focus_out(event):
            # Fokus vom Textfeld nehmen, wenn woanders hingeklickt wird
            self.parent.focus_set()
            
        # Binding zum Hauptfenster hinzufügen
        root = self.parent.winfo_toplevel()
        root.bind("<Button-1>", lambda event: self._check_focus_out(event))
        
        # Frame für Buttons mit verbesserter Positionierung
        self.btn_frame = tk.Frame(self.frame, bg="white")
        self.btn_frame.pack(fill="x", pady=10)
        
        # Button "Kopieren"
        self.btn_copy = tk.Button(
            self.btn_frame, 
            text="Kopieren",
            width=10,
            command=self.copy_to_clipboard
        )
        self.btn_copy.pack(side="left", padx=(0, 10))
        
        # Button "Auf X posten"
        self.btn_xpost = tk.Button(
            self.btn_frame, 
            text="Auf X posten",
            width=10,
            command=self.post_to_x
        )
        self.btn_xpost.pack(side="left")
    
    def copy_to_clipboard(self):
        """Kopiert den X-Post-Text in die Zwischenablage"""
        root = self.parent.winfo_toplevel()
        text = self.xpost_text_widget.get("1.0", "end").strip()
        clipboard.copy_to_clipboard(root, text)
    
    def post_to_x(self):
        """Öffnet X.com mit dem aktuellen Post-Inhalt"""
        text = self.xpost_text_widget.get("1.0", "end").strip()
        if not text:
            tk.messagebox.showinfo("Hinweis", "Kein Text zum Posten vorhanden.")
            return
        url = browser.create_twitter_post_url(text)
        if url:
            browser.open_link(url)
    
    def update_xpost_container(self):
        """Befüllt das X-Post-Feld basierend auf current_data"""
        current_data = self.shared_vars['current_data']
        
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