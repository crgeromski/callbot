# Main Bot-Implementierung
import tkinter as tk
from tkinter import messagebox
import data.api as api
import data.storage as storage
import utils.formatters as formatters
from config import API_TIMEOUT, UPDATE_INTERVAL


class MainBot:
    def __init__(self, main_window):
        self.main_window = main_window
        self.shared_vars = main_window.shared_vars
        self.live_update_active = True  # Immer aktiv
        self.current_tab = None  # Aktiver Tab
        self.main_bot_update_id = None  # ID für den Main-Bot-Refresh
        
        # Update-Methode beim Hauptfenster registrieren
        self.main_window.fetch_data = self.fetch_data
        self.main_window.paste_and_fetch = self.paste_and_fetch
        self.main_window.toggle_live_update = self.toggle_live_update
        self.main_window.reset_budget = self.reset_budget
        
        # Platzhalter für after_id
        self.live_update_after_id = None
        
        # Tab-Wechsel überwachen
        self.main_window.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def on_tab_changed(self, event):
        """Handler für Tab-Wechsel, um den aktuellen Tab zu tracken"""
        self.current_tab = self.main_window.notebook.select()
        
        # Wenn der Main-Bot-Tab ausgewählt ist und noch kein Update läuft, starte es
        if self.current_tab == self.main_window.tabs['main'] and not self.main_bot_update_id:
            self.start_main_bot_update()
        elif self.current_tab != self.main_window.tabs['main'] and self.main_bot_update_id:
            # Wenn ein anderer Tab aktiv ist und ein Update läuft, stoppe es
            self.stop_main_bot_update()

    def toggle_live_update(self):
        """Diese Methode bleibt für Kompatibilität, tut aber nichts mehr."""
        pass
        
    def fetch_data(self):
        """Liest den Link aus entry_var, konvertiert ihn ggf. und ruft die API ab."""
        dex_link = self.shared_vars['entry_var'].get().strip()
        if not dex_link:
            messagebox.showerror("Fehler", "Bitte einen Dexscreener Link eingeben.")
            return

        data = api.fetch_dexscreener_data(dex_link, API_TIMEOUT)
        if not data:
            return  # Fehler wurde bereits in der API-Funktion behandelt

        pairs = data.get("pairs", [])
        if not pairs:
            messagebox.showerror("Fehler", "Keine Daten im 'pairs'-Feld gefunden.")
            return

        self.shared_vars['current_data'] = data
        self.update_ui_with_data(data)
        
        # Starte das automatische Update für den Main Bot Tab
        self.start_main_bot_update()
        
    def update_ui_with_data(self, data):
        """Aktualisiert die UI mit den Daten aus der API"""
        pairs = data.get("pairs", [])
        if not pairs:
            return
            
        pair_info = pairs[0]  # pairs ist nicht leer
        base_token = pair_info.get("baseToken", {})
        
        # Token-Daten
        self.shared_vars['token_blockchain_var'].set(pair_info.get("chainId", "N/A"))
        self.shared_vars['token_name_var'].set(base_token.get("name", "N/A"))
        symbol = base_token.get("symbol", "")
        self.shared_vars['token_symbol_var'].set(f"${symbol}" if symbol else "N/A")
        self.shared_vars['token_address_var'].set(base_token.get("address", "N/A"))
        
        # Finanzwerte
        market_cap = pair_info.get("marketCap", pair_info.get("mcap", pair_info.get("fdv", "N/A")))
        self.shared_vars['mcap_var'].set(formatters.format_k(market_cap))
        
        liquidity = pair_info.get("liquidity", {}).get("usd", "N/A")
        self.shared_vars['liq_var'].set(formatters.format_k(liquidity))
        
        volume = pair_info.get("volume", {}).get("h24", "N/A")
        self.shared_vars['vol24_var'].set(formatters.format_k(volume))
        
        # Preisänderungen + Transaktionen
        for i, lab in enumerate(["m5", "h1", "h6", "h24"]):
            pc_data = pair_info.get("priceChange", {}).get(lab, {})
            pc_str = pc_data.get("priceChange", "N/A") if isinstance(pc_data, dict) else pc_data
            tx_data = pair_info.get("txns", {}).get(lab, {})
            buys = str(tx_data.get("buys", "N/A"))
            sells = str(tx_data.get("sells", "N/A"))
            
            formatted_pc = formatters.format_percentage(pc_str)
            
            if i < len(self.main_window.time_price_vars):
                # Bei den Preis-Variablen gehen wir davon aus, dass sie jetzt als (var, entry) Tupel gespeichert sind
                price_var, price_entry = self.main_window.time_price_vars[i]
                price_var.set(formatted_pc)
                
                # Farbe direkt setzen basierend auf dem Wert
                try:
                    pc_value = float(pc_str) if pc_str != "N/A" else 0
                    if pc_value > 0:
                        price_entry.config(readonlybackground="#d8ffd8")  # Grün für positiv
                    elif pc_value < 0:
                        price_entry.config(readonlybackground="#ffd8d8")  # Rot für negativ
                    else:
                        price_entry.config(readonlybackground="white")  # Neutral für 0
                except (ValueError, TypeError):
                    price_entry.config(readonlybackground="white")  # Fallback
                    
                # Buys/Sells-Aktualisierung
                self.main_window.time_buys_vars[i][0].set(buys)
                self.main_window.time_sells_vars[i][0].set(sells)
                
                # Färbe die Buys/Sells-Felder ein
                if hasattr(self.main_window, 'stats_frame'):
                    self.main_window.stats_frame.color_buys_sells_entries(
                        self.main_window.time_buys_vars[i][1], 
                        self.main_window.time_sells_vars[i][1], 
                        buys, 
                        sells
                    )
        
        # Social Media Links
        entry_link = self.shared_vars['entry_var'].get()
        if "dexscreener.com" in entry_link:
            self.shared_vars['dexscreener_var'].set(entry_link)
        else:
            # Erstelle einen Fallback-Link, der zur Suche führt
            chain_id = pair_info.get("chainId", "").lower()  # Holen der Blockchain aus den API-Daten
            address = base_token.get("address", "")
            pair_address = pair_info.get("pairAddress", "")
            
            if chain_id and pair_address:
                # Wenn wir Blockchain und Pair-Adresse haben, erstelle einen präzisen Link
                self.shared_vars['dexscreener_var'].set(f"https://dexscreener.com/{chain_id}/{pair_address}")
            elif chain_id and address:
                # Wenn wir Blockchain und Token-Adresse haben, erstelle einen Token-Link
                self.shared_vars['dexscreener_var'].set(f"https://dexscreener.com/{chain_id}/{address}")
            else:
                # Fallback auf Suchseite
                self.shared_vars['dexscreener_var'].set(f"https://dexscreener.com/search?q={address}")

        # Setze last_screenshot zurück
        if hasattr(self.main_window, 'xpost_frame') and hasattr(self.main_window.xpost_frame, 'last_screenshot'):
            self.main_window.xpost_frame.last_screenshot = None
            
        # Setze alle Button-Farben zurück
        if hasattr(self.main_window, 'xpost_frame'):
            xpost_frame = self.main_window.xpost_frame
            
            # X-Button zurücksetzen
            if hasattr(xpost_frame, 'original_button_bg') and xpost_frame.original_button_bg and hasattr(xpost_frame, 'btn_xpost'):
                xpost_frame.btn_xpost.config(bg=xpost_frame.original_button_bg)
                
            # Screenshot-Button zurücksetzen
            if hasattr(xpost_frame, 'original_screenshot_bg') and xpost_frame.original_screenshot_bg and hasattr(xpost_frame, 'screenshot_button'):
                xpost_frame.screenshot_button.config(bg=xpost_frame.original_screenshot_bg)
                
            # Call-Button zurücksetzen
            if hasattr(xpost_frame, 'original_call_bg') and xpost_frame.original_call_bg and hasattr(xpost_frame, 'call_button'):
                xpost_frame.call_button.config(bg=xpost_frame.original_call_bg)
                
            # Aktuellen Link aktualisieren
            if hasattr(xpost_frame, 'current_link'):
                xpost_frame.current_link = self.shared_vars['entry_var'].get()

        # Website und soziale Medien
        info = pair_info.get("info", {})
        websites = info.get("websites", [])
        self.shared_vars['website_var'].set(websites[0].get("url", "N/A") if websites else "N/A")
        
        socials = info.get("socials", [])
        self.shared_vars['twitter_var'].set(next((s.get("url") for s in socials if s.get("type") == "twitter"), "N/A"))
        self.shared_vars['telegram_var'].set(next((s.get("url") for s in socials if s.get("type") == "telegram"), "N/A"))
        self.shared_vars['discord_var'].set(next((s.get("url") for s in socials if s.get("type") == "discord"), "N/A"))
        
        # Aktualisiere den X-Post-Container, wenn verfügbar
        if hasattr(self.main_window, 'xpost_frame') and hasattr(self.main_window.xpost_frame, 'update_xpost_container'):
            self.main_window.xpost_frame.update_xpost_container()

    def paste_and_fetch(self):
        """Fügt den Inhalt der Zwischenablage in das Eingabefeld ein und ruft die API ab"""
        try:
            new_link = self.main_window.root.clipboard_get()  # Lese den Inhalt der Zwischenablage
            self.shared_vars['entry_var'].set(new_link)       # Setze den Link in das Eingabefeld
            self.main_window.root.update_idletasks()          # Aktualisiere die GUI-Variablen
            self.fetch_data()                                 # Rufe die API ab
            self.main_window.notebook.select(self.main_window.tabs['main'])  # Wechsle zum "Main Bot"-Tab
        except Exception as e:
            messagebox.showerror("Fehler", f"Konnte Zwischenablage nicht verarbeiten: {e}")
            
    def reset_budget(self):
        """Setzt den Kontostand auf 500$ zurück, nach Bestätigung durch den Benutzer."""
        from tkinter import messagebox
        
        # Zeige ein Bestätigungsdialog
        confirm = messagebox.askyesno(
            "Kontostand zurücksetzen",
            "Möchtest du den Kontostand wirklich auf 500$ zurücksetzen?\nDiese Aktion kann nicht rückgängig gemacht werden.",
            icon="warning"
        )
        
        if confirm:
            storage.save_budget(500.0)
            # Aktualisiere das Label
            self.main_window.current_balance_label.config(text=f"Kontostand: 500.00$", bg="white")
            messagebox.showinfo("Erfolg", "Der Kontostand wurde auf 500$ zurückgesetzt.")
    
    def start_main_bot_update(self):
        """Startet die automatische Aktualisierung des Main Bot Tabs alle 10 Sekunden"""
        # Stoppe vorherige Updates, falls vorhanden
        self.stop_main_bot_update()
        
        # Hole den aktuellen Dexscreener-Link
        dex_link = self.shared_vars['entry_var'].get().strip()
        if not dex_link:
            return  # Kein Link, kein Update
            
        # Starte den Update-Timer (10000 ms = 10 Sekunden)
        self.main_bot_update_id = self.main_window.root.after(10000, self.update_main_bot_data)
    
    def stop_main_bot_update(self):
        """Stoppt die automatische Aktualisierung des Main Bot Tabs"""
        if self.main_bot_update_id:
            self.main_window.root.after_cancel(self.main_bot_update_id)
            self.main_bot_update_id = None
    
    def update_main_bot_data(self):
        """Aktualisiert die Daten im Main Bot Tab"""
        # Nur aktualisieren, wenn der Main Bot Tab aktiv ist
        if self.current_tab == self.main_window.tabs['main']:
            # Hole den aktuellen Dexscreener-Link
            dex_link = self.shared_vars['entry_var'].get().strip()
            if dex_link:
                # Rufe die API ab, ohne Fehlermeldungen anzuzeigen
                data = api.fetch_dexscreener_data(dex_link, API_TIMEOUT)
                if data and "pairs" in data and data["pairs"]:
                    # Aktualisiere die UI mit den neuen Daten
                    self.shared_vars['current_data'] = data
                    self.update_ui_with_data(data)
        
        # Plane das nächste Update
        self.main_bot_update_id = self.main_window.root.after(10000, self.update_main_bot_data)

    def auto_refresh_calls(self):
        """
        Aktualisiert alle Calls und Watchlist-Einträge mit aktuellen Daten.
        Funktioniert jetzt mit verbesserter Watchlist-Unterstützung.
        """
        # Aktualisiere Calls
        self.update_active_calls()
        
        # Aktualisiere Watchlist
        self.update_watchlist_items()
        
        # Aktualisiere UI
        self.update_ui_stats()
        
        # Plane den nächsten Update-Aufruf
        self.live_update_after_id = self.main_window.root.after(UPDATE_INTERVAL, self.auto_refresh_calls)

    def update_active_calls(self):
        """Aktualisiert die aktiven Calls mit aktuellen Daten"""
        calls = storage.load_call_data()
        updated_calls = []
        
        for call in calls:
            # Abgeschlossene Calls direkt übernehmen
            if call.get("abgeschlossen", False):
                updated_calls.append(call)
                continue
                
            # Aktualisierung für aktive Calls
            try:
                # Rufe Daten basierend auf dem Symbol oder Link ab
                symbol = call.get("Symbol")
                link = call.get("Link")
                
                # API-Daten abrufen
                data = api.fetch_dexscreener_data(link, API_TIMEOUT)
                
                if data and "pairs" in data and data["pairs"]:
                    pair_info = data["pairs"][0]
                    
                    # Market Cap aktualisieren
                    market_cap = pair_info.get("marketCap", pair_info.get("mcap", pair_info.get("fdv", "N/A")))
                    call["Aktuelles_MCAP"] = formatters.format_k(market_cap)
                    
                    # Berechnung der Kennzahlen für aktive Calls
                    initial_mcap = formatters.parse_km(call.get("MCAP_at_Call", "0"))
                    current_mcap = formatters.parse_km(call.get("Aktuelles_MCAP", "0"))
                    
                    if initial_mcap > 0 and current_mcap > 0:
                        x_factor = current_mcap / initial_mcap
                        pl_percent = (x_factor - 1) * 100
                        
                        # Invest-Wert aus dem Call verwenden oder auf 10$ setzen
                        invest = 10.0
                        try:
                            invest_str = call.get("Invest", "10")
                            invest = float(invest_str)
                        except:
                            invest = 10.0
                            
                        pl_dollar = invest * x_factor - invest
                        
                        call["X_Factor"] = f"{x_factor:.1f}X"
                        call["PL_Percent"] = f"{pl_percent:.0f}%"
                        call["PL_Dollar"] = f"{pl_dollar:.2f}$"
                        call["Invest"] = f"{invest}"
                    else:
                        # Fallback bei ungültigen Werten
                        call["X_Factor"] = "0.0X"
                        call["PL_Percent"] = "0%"
                        call["PL_Dollar"] = "0.00$"
                        call["Invest"] = "10"
            except Exception as e:
                print(f"Fehler beim Aktualisieren des Calls ({symbol}): {e}")
                
            updated_calls.append(call)
            
        # Speichern der aktualisierten Calls
        storage.save_call_data(updated_calls)

    def update_watchlist_items(self):
        """Aktualisiert die Watchlist-Einträge mit aktuellen Daten"""
        watchlist = storage.load_watchlist_data()
        updated_watchlist = []
        
        for item in watchlist:
            try:
                # Rufe Daten basierend auf dem Link ab
                symbol = item.get("Symbol")
                link = item.get("Link")
                
                # API-Daten abrufen
                data = api.fetch_dexscreener_data(link, API_TIMEOUT)
                
                if data and "pairs" in data and data["pairs"]:
                    pair_info = data["pairs"][0]
                    
                    # Market Cap aktualisieren
                    market_cap = pair_info.get("marketCap", pair_info.get("mcap", pair_info.get("fdv", "N/A")))
                    item["Aktuelles_MCAP"] = formatters.format_k(market_cap)
                    
                    # Berechne X-Factor, PL_Percent und PL_Dollar
                    initial_mcap = formatters.parse_km(item.get("MCAP_at_Call", "0"))
                    current_mcap = formatters.parse_km(item.get("Aktuelles_MCAP", "0"))
                    
                    if initial_mcap > 0 and current_mcap > 0:
                        x_factor = current_mcap / initial_mcap
                        pl_percent = (x_factor - 1) * 100
                        
                        # Fiktiver Invest-Wert für die Anzeige (10$)
                        invest = 10.0
                        pl_dollar = invest * x_factor - invest
                        
                        item["X_Factor"] = f"{x_factor:.1f}X"
                        item["PL_Percent"] = f"{pl_percent:.0f}%"
                        item["PL_Dollar"] = f"{pl_dollar:.2f}$"
                        item["Invest"] = "10"  # Fester Wert für die Anzeige
                    else:
                        # Fallback bei ungültigen Werten
                        item["X_Factor"] = "0.0X"
                        item["PL_Percent"] = "0%"
                        item["PL_Dollar"] = "0.00$"
                        item["Invest"] = "10"
            except Exception as e:
                print(f"Fehler beim Aktualisieren des Watchlist-Items ({symbol}): {e}")
                
            updated_watchlist.append(item)
            
        # Speichern der aktualisierten Watchlist
        storage.save_watchlist_data(updated_watchlist)
        
        # Aktualisiere die Watchlist-Treeview
        if hasattr(self.main_window, 'update_watchlist_tree'):
            self.main_window.update_watchlist_tree()

    def update_ui_stats(self):
        """Aktualisiert die statistischen Daten im UI"""
        # Aktualisiere die Treeviews
        if hasattr(self.main_window, 'calls_tree'):
            self.main_window.calls_tree.update_tree()
        if hasattr(self.main_window, 'archived_calls_tree'):
            self.main_window.archived_calls_tree.update_tree()
            
        # Berechne dynamische Werte und aktualisiere Widgets
        calls = storage.load_call_data()
        active_calls = [call for call in calls if not call.get("abgeschlossen", False)]
        num_calls = len(active_calls)
        total_invest = num_calls * 10.0  # 10$ pro Call
        total_profit, profit_percentage = storage.calculate_total_profit()
        avg_profit = total_profit / num_calls if num_calls > 0 else 0.0
        current_balance = storage.load_budget()
        
        # Update Profit-Labels
        self.update_profit_entry(self.main_window.total_invest_label, f"Investiert: {total_invest:.2f}$")
        self.update_profit_entry(self.main_window.num_calls_label, f"Calls: {num_calls}")
        self.update_profit_entry(self.main_window.total_profit_label, f"Gesamt Gewinn/Verlust: {total_profit:.2f}$", 
                            color="#d8ffd8" if total_profit > 0 else "#ffd8d8" if total_profit < 0 else "white")
                            
        self.update_profit_entry(self.main_window.profit_percent_label, f"Gewinn/Verlust (%): {profit_percentage:.2f}%",
                            color="#d8ffd8" if profit_percentage > 0 else "#ffd8d8" if profit_percentage < 0 else "white")
                            
        self.update_profit_entry(self.main_window.avg_profit_label, f"Durchschnitt pro Call: {avg_profit:.2f}$",
                            color="#d8ffd8" if avg_profit > 0 else "#ffd8d8" if avg_profit < 0 else "white")
                            
        self.update_profit_entry(self.main_window.current_balance_label, f"Kontostand: {current_balance:.2f}$",
                            color="#d8ffd8" if current_balance > 500 else "#ffd8d8" if current_balance < 500 else "white")

    def update_profit_entry(self, entry_widget, text, color="white"):
        """Aktualisiert ein Entry-Widget im Gewinnrechner mit neuem Text und Farbe"""
        entry_widget.config(state="normal")
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, text)
        entry_widget.config(state="readonly", readonlybackground=color)