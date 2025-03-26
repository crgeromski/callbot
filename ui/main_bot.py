# Main Bot-Implementierung
import tkinter as tk
from tkinter import messagebox
import data.api as api
import data.storage as storage
import utils.formatters as formatters
from config import API_TIMEOUT, UPDATE_INTERVAL, BACKUP_INTERVAL
from ui.token_frame import TokenFrame  # Diese Zeile hinzufügen

class MainBot:
    def __init__(self, main_window):
        self.main_window = main_window
        self.shared_vars = main_window.shared_vars
        self.live_update_active = self.shared_vars['live_update_active'].get()
        
        self.main_container = main_window.tabs['main']

        # Grid-Einstellungen für den main_container
        for col in range(2):
            self.main_container.grid_columnconfigure(col, weight=1, uniform="col")
        # Einheitliche Zeilenhöhen
        for row in range(3):
            self.main_container.grid_rowconfigure(row, weight=1, uniform="row")

        # Token-Frame für die obere linke Ecke erstellen
        self.token_frame = TokenFrame(self.main_container, self.shared_vars)
        
        
        # Importiere die neuen Frame-Klassen, wenn sie noch nicht oben importiert sind
        from ui.future_function_frame_1 import FutureFunctionFrame1
        from ui.future_function_frame_2 import FutureFunctionFrame2

        # Erstelle die Frames für zukünftige Funktionen
        self.future_frame1 = FutureFunctionFrame1(self.main_container, self.shared_vars)
        self.future_frame2 = FutureFunctionFrame2(self.main_container, self.shared_vars)
        
        # Backup-Zähler
        self.backup_counter = 0
        
        # Update-Methode beim Hauptfenster registrieren
        self.main_window.fetch_data = self.fetch_data
        self.main_window.paste_and_fetch = self.paste_and_fetch
        self.main_window.toggle_live_update = self.toggle_live_update
        self.main_window.reset_budget = self.reset_budget
        
    def fetch_data(self):
        """Liest den Link aus entry_var, konvertiert ihn ggf. und ruft die API ab."""
        link = self.shared_vars['entry_var'].get().strip()
        if not link:
            messagebox.showerror("Fehler", "Bitte einen Dexscreener Link eingeben.")
            return

        data = api.fetch_dexscreener_data(link, API_TIMEOUT)
        if not data:
            return  # Fehler wurde bereits in der API-Funktion behandelt

        pairs = data.get("pairs", [])
        if not pairs:
            messagebox.showerror("Fehler", "Keine Daten im 'pairs'-Feld gefunden.")
            return

        self.shared_vars['current_data'] = data
        self.update_ui_with_data(data)
        
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
            if i < len(self.main_window.time_price_vars):
                self.main_window.time_price_vars[i].set(formatters.format_percentage(pc_str))
                self.main_window.time_buys_vars[i][0].set(buys)
                self.main_window.time_sells_vars[i][0].set(sells)
                
                # Färbe die Felder ein
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
                
        # Website und soziale Medien
        info = pair_info.get("info", {})
        websites = info.get("websites", [])
        self.shared_vars['website_var'].set(websites[0].get("url", "N/A") if websites else "N/A")
        
        socials = info.get("socials", [])
        self.shared_vars['twitter_var'].set(next((s.get("url") for s in socials if s.get("type") == "twitter"), "N/A"))
        self.shared_vars['telegram_var'].set(next((s.get("url") for s in socials if s.get("type") == "telegram"), "N/A"))
        self.shared_vars['discord_var'].set(next((s.get("url") for s in socials if s.get("type") == "discord"), "N/A"))
        
        # X-Post aktualisieren
        if hasattr(self.main_window, 'xpost_frame'):
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
            
    def toggle_live_update(self):
        """Schaltet die Live-Daten-Aktualisierung an oder aus"""
        self.live_update_active = not self.live_update_active
        if self.live_update_active:
            self.main_window.live_update_btn.config(text="Live Update AN", bg="#d8ffd8")
            self.auto_refresh_calls()  # Starte den Call-Update-Loop
        else:
            self.main_window.live_update_btn.config(text="Live Update AUS", bg="#ffd8d8")
            if self.live_update_after_id is not None:
                self.main_window.root.after_cancel(self.live_update_after_id)
                self.live_update_after_id = None
            print("Live-Update gestoppt.")
            
    def auto_refresh_calls(self):
        """Aktualisiert regelmäßig die Calls"""
        if not self.live_update_active:
            return
            
        calls = storage.load_call_data()
        updated_calls = []
        for call in calls:
            if call.get("abgeschlossen", False):
                updated_calls.append(call)
                continue
                
            # Aktualisierung für aktive Calls:
            link = call.get("Link")
            if link:
                api_link = api.convert_to_api_link(link)
                try:
                    data = api.fetch_dexscreener_data(link, API_TIMEOUT)
                    if data:
                        pairs = data.get("pairs", [])
                        if pairs:
                            pair_info = pairs[0]
                            market_cap = pair_info.get("marketCap", pair_info.get("mcap", pair_info.get("fdv", "N/A")))
                            call["Aktuelles_MCAP"] = formatters.format_k(market_cap)
                            liquidity = pair_info.get("liquidity", {}).get("usd", "N/A")
                            call["Live_Liquidity"] = formatters.format_k(liquidity)
                except Exception as e:
                    print(f"Fehler beim Aktualisieren des Calls ({link}): {e}")
                    
            # Berechnung der Kennzahlen für aktive Calls
            call["Invest"] = "10"
            initial_mcap = formatters.parse_km(call.get("MCAP_at_Call", "0"))
            current_mcap = formatters.parse_km(call.get("Aktuelles_MCAP", "0"))
            if initial_mcap > 0:
                x_factor = current_mcap / initial_mcap
                pl_percent = (x_factor - 1) * 100
                pl_dollar = 10.0 * x_factor - 10.0  # basierend auf Invest=10$
            else:
                x_factor = 0
                pl_percent = 0
                pl_dollar = 0
            call["X_Factor"] = f"{x_factor:.1f}X"
            call["PL_Percent"] = f"{pl_percent:.0f}%"
            call["PL_Dollar"] = f"{pl_dollar:.2f}$"
            updated_calls.append(call)
            
        # Speichern der aktualisierten Calls
        storage.save_call_data(updated_calls)
        
        # Aktualisiere UI
        self.update_ui_stats()
        
        # Plane den nächsten Update-Aufruf
        self.live_update_after_id = self.main_window.root.after(UPDATE_INTERVAL, self.auto_refresh_calls)
        
        # Backup-Zähler inkrementieren
        self.backup_counter += 1
        
        # Backup alle X Durchläufe
        if self.backup_counter >= BACKUP_INTERVAL:
            storage.backup_calls()
            storage.save_budget(float(self.main_window.current_balance_label.cget("text").split(":")[1].strip().rstrip("$")))
            self.backup_counter = 0
            
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
        
        # Update UI-Labels
        self.main_window.total_invest_label.config(text=f"Investiert: {total_invest:.2f}$")
        self.main_window.num_calls_label.config(text=f"Calls: {num_calls}")
        self.main_window.total_profit_label.config(text=f"Gesamt Gewinn/Verlust: {total_profit:.2f}$")
        
        # Profit-Label einfärben
        if total_profit > 0:
            self.main_window.total_profit_label.config(bg="#d8ffd8")
        elif total_profit < 0:
            self.main_window.total_profit_label.config(bg="#ffd8d8")
        else:
            self.main_window.total_profit_label.config(bg="white")
            
        # Prozent-Label aktualisieren und einfärben
        self.main_window.profit_percent_label.config(text=f"Gewinn/Verlust (%): {profit_percentage:.2f}%")
        if profit_percentage > 0:
            self.main_window.profit_percent_label.config(bg="#d8ffd8")
        elif profit_percentage < 0:
            self.main_window.profit_percent_label.config(bg="#ffd8d8")
        else:
            self.main_window.profit_percent_label.config(bg="white")
            
        # Durchschnitt pro Call aktualisieren und einfärben
        self.main_window.avg_profit_label.config(text=f"Durchschnitt pro Call: {avg_profit:.2f}$")
        if avg_profit > 0:
            self.main_window.avg_profit_label.config(bg="#d8ffd8")
        elif avg_profit < 0:
            self.main_window.avg_profit_label.config(bg="#ffd8d8")
        else:
            self.main_window.avg_profit_label.config(bg="white")
            
        # Kontostand aktualisieren und einfärben
        self.main_window.current_balance_label.config(text=f"Kontostand: {current_balance:.2f}$")
        if current_balance > 500:
            self.main_window.current_balance_label.config(bg="#d8ffd8")
        elif current_balance < 500:
            self.main_window.current_balance_label.config(bg="#ffd8d8")
        else:
            self.main_window.current_balance_label.config(bg="white")

