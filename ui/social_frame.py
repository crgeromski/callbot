# Social Media Frame
import tkinter as tk
import ui.styles as styles

class SocialFrame:
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


    def __init__(self, parent, shared_vars):
        self.parent = parent
        self.shared_vars = shared_vars
        self.create_frame()