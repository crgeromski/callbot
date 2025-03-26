# X-Post Frame
import tkinter as tk
import utils.clipboard as clipboard
import utils.browser as browser

class XPostFrame:
    def __init__(self, parent, shared_vars):
        self.parent = parent
        self.shared_vars = shared_vars
        self.create_frame()
        
    def create_frame(self):
        """Erstellt den Frame für X-Posts"""
        self.frame = tk.Frame(
            self.parent, 
            bg="white", 
            padx=20, 
            pady=20,
            bd=1,
            relief="solid",
            highlightbackground="#cccccc",
            highlightthickness=1
        )
        self.frame.grid(row=1, column=1, sticky="nsew")  # Ändern von (0,1) zu (1,1)
        
        self.inner = tk.Frame(self.frame, bg="white")
        self.inner.pack(fill="both", expand=True)
        
        # X-Post Label
        self.xpost_label = tk.Label(
            self.inner, 
            text="X-Post", 
            font=("Arial", 11, "bold"), 
            bg="white", 
            anchor="w"
        )
        self.xpost_label.pack(anchor="w", pady=(0, 8))
        
        # Rest des Codes bleibt unverändert
        
        # X-Post Textfeld (multiline)
        self.xpost_text_widget = tk.Text(
            self.inner, 
            height=3, 
            wrap="word", 
            relief="sunken", 
            borderwidth=2
        )
        self.xpost_text_widget.insert("1.0", "")
        self.xpost_text_widget.config(state="disabled")  
        self.xpost_text_widget.pack(anchor="w", padx=0, pady=2, fill="x", expand=True)
        
        # Frame für Buttons
        self.btn_subframe = tk.Frame(self.inner, bg="white")
        self.btn_subframe.pack(anchor="w", pady=(5,0))
        
        # Button "Kopieren"
        self.btn_copy = tk.Button(
            self.btn_subframe, 
            text="Kopieren",
            command=self.copy_to_clipboard
        )
        self.btn_copy.pack(side="left", padx=(0,10))
        
        # Button "Auf X posten"
        self.btn_xpost = tk.Button(
            self.btn_subframe, 
            text="Auf X posten", 
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