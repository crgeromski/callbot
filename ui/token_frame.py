# Token-Daten-Frame
import tkinter as tk
import ui.styles as styles
import utils.browser as browser
from tkinter import messagebox
import data.storage as storage

class TokenFrame:
    def __init__(self, parent, shared_vars, main_window=None):
        self.parent = parent
        self.shared_vars = shared_vars
        self.main_window = main_window
        self.original_button_bg = None  # Für den Watchlist-Button
        self.original_dex_bg = None     # Für den DexScreener-Button
        self.current_link = ""          # Für die Link-Überwachung
        self.link_check_id = None       # Für after_cancel
        self.create_frame()

    def create_frame(self):
        """Erstellt den Frame für Token-Daten"""
        # Wir erstellen einen äußeren Frame mit Padding
        self.frame = tk.Frame(self.parent, bg="white", padx=20, pady=20)
        self.frame.pack(fill="both", expand=True)
        
        # Titel für Token-Daten
        title_label = tk.Label(
            self.frame, 
            text="Token-Daten", 
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
        styles.create_data_row(data_container, "Token-Name", self.shared_vars['token_name_var'], 1)
        styles.create_data_row(data_container, "Symbol", self.shared_vars['token_symbol_var'], 2)
        styles.create_data_row(data_container, "Token-Adresse", self.shared_vars['token_address_var'], 3)
        
        # Erstelle einen Button für DexScreener Link
        dexlink_frame = tk.Frame(data_container, bg="white")
        dexlink_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        
        # Buttons-Container für gleiche Breite
        buttons_container = tk.Frame(dexlink_frame, bg="white")
        buttons_container.pack(fill="x", expand=True, pady=(5, 0))
        buttons_container.columnconfigure(0, weight=1)
        buttons_container.columnconfigure(1, weight=1)
        
        # DexScreener Button
        self.dexscreener_button = tk.Button(
            buttons_container, 
            text="DexScreener Link", 
            font=("Arial", 10, "bold"),
            height=2,
            command=lambda: self.open_dexscreener()
        )
        # Neue Typografie-Anwendung für Button
        styles.apply_typography(self.dexscreener_button, 'button_label')
        self.dexscreener_button.grid(row=0, column=0, sticky="ew", padx=(0, 2))
        
        # Beobachten Button
        self.watchlist_button = tk.Button(
            buttons_container, 
            text="Auf Watchlist", 
            font=("Arial", 10, "bold"),
            height=2,
            command=lambda: self.add_to_watchlist()
        )
        # Neue Typografie-Anwendung für Button
        styles.apply_typography(self.watchlist_button, 'button_label')
        self.watchlist_button.grid(row=0, column=1, sticky="ew", padx=(2, 0))
        
        # Speichere die Originalfarben
        self.original_button_bg = self.watchlist_button.cget("bg")
        self.original_dex_bg = self.dexscreener_button.cget("bg")
        
        # Starte die Farbaktualisierung
        self.check_watchlist_status()

    # Restliche Methoden bleiben unverändert
    def open_dexscreener(self):
        """Öffnet den DexScreener Link im Browser"""
        link = self.shared_vars['dexscreener_var'].get()
        if link and link != "N/A":
            browser.open_link(link)
        else:
            messagebox.showerror("Fehler", "Kein gültiger DexScreener-Link vorhanden.")
            
    def add_to_watchlist(self):
        """
        Fügt den aktuellen Token zur Beobachtungsliste hinzu.
        """
        try:
            # Hole die benötigten Daten aus den Variablen
            symbol = self.shared_vars['token_symbol_var'].get()
            mcap = self.shared_vars['mcap_var'].get()
            link = self.shared_vars['entry_var'].get()
            
            if not all([symbol, mcap, link]):
                messagebox.showerror("Fehler", "Es fehlen notwendige Daten für die Beobachtungsliste.")
                return
            
            # Prüfe, ob der Coin bereits auf der Watchlist ist
            watchlist_items = storage.load_watchlist_data()
            already_on_watchlist = any(
                item.get("Symbol") == symbol for item in watchlist_items
            )
            
            if already_on_watchlist:
                # Keine Benachrichtigung, einfach nichts tun
                return
            
            # Erstelle neuen Watchlist-Eintrag
            watchlist_item = storage.create_new_watchlist_item(symbol, mcap, link)
            
            # Speichere den neuen Eintrag
            storage.save_new_watchlist_item(watchlist_item)
            
            # Aktualisiere die Watchlist TreeView
            if hasattr(self.main_window, 'update_watchlist_tree'):
                self.main_window.update_watchlist_tree()
                
            # Aktualisiere die Button-Farbe
            self.watchlist_button.config(bg="#64c264")  # Grün für "auf Watchlist"
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Hinzufügen zur Beobachtungsliste: {e}")
    
    def check_watchlist_status(self):
        """Überprüft, ob der aktuelle Token auf der Watchlist ist und aktualisiert die Button-Farbe"""
        try:
            # Breche vorherige Timer ab
            if self.link_check_id:
                self.frame.after_cancel(self.link_check_id)
            
            # Hole aktuelle Daten
            symbol = self.shared_vars['token_symbol_var'].get()
            current_link = self.shared_vars['entry_var'].get()
            
            # Wenn ein Symbol geladen ist
            if symbol and symbol != "N/A":
                # Prüfe, ob auf Watchlist
                watchlist_items = storage.load_watchlist_data()
                on_watchlist = any(
                    item.get("Symbol") == symbol for item in watchlist_items
                )
                
                # Aktualisiere Button-Farbe
                if on_watchlist:
                    self.watchlist_button.config(bg="#64c264")  # Grün für "auf Watchlist"
                else:
                    self.watchlist_button.config(bg=self.original_button_bg)
            
            # Aktualisiere Link-Referenz
            if current_link != self.current_link:
                self.current_link = current_link
            
            # Plane nächste Überprüfung
            self.link_check_id = self.frame.after(500, self.check_watchlist_status)
            
        except Exception as e:
            print(f"Fehler bei Watchlist-Statusüberprüfung: {e}")
            # Trotz Fehler weitermachen mit Timer
            self.link_check_id = self.frame.after(500, self.check_watchlist_status)