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
        
        self.xpost_text_widget = tk.Text(
            text_container, 
            height=10,  # Höhere Starthöhe für bessere Sichtbarkeit
            wrap="word", 
            relief="sunken", 
            borderwidth=2
        )
        self.xpost_text_widget.insert("1.0", "")
        self.xpost_text_widget.config(state="disabled")  
        self.xpost_text_widget.pack(fill="both", expand=True, pady=5)
        
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
            self.xpost_text_widget.config(state="normal")
            self.xpost_text_widget.delete("1.0", "end")
            self.xpost_text_widget.config(state="disabled")
            return
        
        pairs = current_data.get("pairs", [])
        if not pairs:
            self.xpost_text_widget.config(state="normal")
            self.xpost_text_widget.delete("1.0", "end")
            self.xpost_text_widget.config(state="disabled")
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
        
        xpost_text = f"{symbol_str}\n🔗 CA: {token_addr}\n💰 MCAP Entry: ${market_cap_str}"
        self.xpost_text_widget.config(state="normal")
        self.xpost_text_widget.delete("1.0", "end")
        self.xpost_text_widget.insert("1.0", xpost_text)
        self.xpost_text_widget.config(state="disabled")