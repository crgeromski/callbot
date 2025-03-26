# Social Media Frame
import tkinter as tk
import ui.styles as styles

class SocialFrame:
    def create_frame(self):
        self.frame.grid(row=2, column=0, sticky="nsew")
        
        self.inner = tk.Frame(self.frame, bg="white")
        self.inner.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Titel
        tk.Label(
            self.inner, 
            text="Social Media Kanäle", 
            font=("Arial", 11, "bold"), 
            bg="white", 
            anchor="w"
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0,10))
        
        # Datenzeilen
        styles.create_link_row(self.inner, "DexScreener", self.shared_vars['dexscreener_var'], 1)
        styles.create_link_row(self.inner, "Website", self.shared_vars['website_var'], 2)
        styles.create_link_row(self.inner, "Twitter", self.shared_vars['twitter_var'], 3)
        styles.create_link_row(self.inner, "Telegram", self.shared_vars['telegram_var'], 4)
        styles.create_link_row(self.inner, "Discord", self.shared_vars['discord_var'], 5)

    def __init__(self, parent, shared_vars):
        self.parent = parent
        self.shared_vars = shared_vars
        self.create_frame()