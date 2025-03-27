# RugCheck Frame mit verbesserter Fehlerbehandlung
import tkinter as tk
from tkinter import messagebox
import data.axiom_api as axiom_api
import config
import threading

class RugCheckFrame:
    def __init__(self, parent, shared_vars, main_window=None):
        self.parent = parent
        self.shared_vars = shared_vars
        self.main_window = main_window
        self.metrics_vars = {}  # StringVars für die Metriken
        self.metrics_entries = {}  # Entry-Widgets für die Metriken
        self.is_loading = False  # Flag für Ladevorgang
        self.api_available = False  # Flag für API-Verfügbarkeit
        self.create_frame()
        
    def create_frame(self):
        """Erstellt den Frame für den RugCheck mit Axiom-Daten"""
        self.frame = tk.Frame(
            self.parent, 
            bg="white", 
            padx=20, 
            pady=20
        )
        self.frame.pack(fill="both", expand=True)
        
        # Titel und API-Status
        title_frame = tk.Frame(self.frame, bg="white")
        title_frame.pack(fill="x", pady=(0,10))
        
        # Titel
        tk.Label(
            title_frame,
            text="RugCheck by Axiom", 
            font=("Arial", 11, "bold"), 
            bg="white", 
            anchor="w"
        ).pack(side="left")
        
        # API-Status
        self.api_status_var = tk.StringVar(value="API: Prüfe...")
        self.api_status_label = tk.Label(
            title_frame,
            textvariable=self.api_status_var,
            font=("Arial", 8),
            bg="white",
            fg="#888888"
        )
        self.api_status_label.pack(side="right")
        
        # Beschreibung
        tk.Label(
            self.frame,
            text="Analyse der On-Chain Daten für Risikoeinschätzung",
            font=("Arial", 9),
            bg="white",
            justify="left"
        ).pack(anchor="w", pady=(0,10))
        
        # Container für die Metriken
        self.metrics_container = tk.Frame(self.frame, bg="white")
        self.metrics_container.pack(fill="both", expand=True)
        
        # Grid-Konfiguration für 3x3 Layout
        for i in range(3):
            self.metrics_container.columnconfigure(i, weight=1)
        for i in range(3):
            self.metrics_container.rowconfigure(i, weight=1)
        
        # Erstelle die 9 Metrik-Kacheln
        self._create_metric_tile("top_10_holders", "Top 10 H.", 0, 0)
        self._create_metric_tile("dev_holdings", "Dev H.", 0, 1)
        self._create_metric_tile("snipers_holdings", "Snipers H.", 0, 2)
        self._create_metric_tile("insiders", "Insiders", 1, 0)
        self._create_metric_tile("bundlers", "Bundlers", 1, 1)
        self._create_metric_tile("lp_burned", "LP Burned", 1, 2)
        self._create_metric_tile("holders", "Holders", 2, 0)
        self._create_metric_tile("pro_traders", "Pro Traders", 2, 1)
        self._create_metric_tile("dex_paid", "Dex Paid", 2, 2)
        
        # Reset-Werte setzen
        self.reset_metrics()
        
        # Aktualisierungsstatus
        self.update_status_var = tk.StringVar(value="")
        self.update_status_label = tk.Label(
            self.frame,
            textvariable=self.update_status_var,
            font=("Arial", 8, "italic"),
            bg="white",
            fg="#666666"
        )
        self.update_status_label.pack(anchor="w", pady=(10,0))
        
        # API-Key in separatem Thread prüfen, um die UI nicht zu blockieren
        threading.Thread(target=self.check_api_key, daemon=True).start()
        
    def _create_metric_tile(self, key, label_text, row, col):
        """Erstellt eine Metrik-Kachel im Grid"""
        # Container für die Kachel
        tile = tk.Frame(self.metrics_container, bg="#101010", bd=1, relief="solid", padx=5, pady=5)
        tile.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")
        
        # StringVar für die Metrik
        var = tk.StringVar(value="N/A")
        self.metrics_vars[key] = var
        
        # Label (Beschriftung)
        label = tk.Label(
            tile,
            text=label_text,
            font=("Arial", 9, "bold"),
            bg="#101010",
            fg="#888888",
            anchor="w"
        )
        label.pack(fill="x")
        
        # Entry (Wert)
        entry = tk.Entry(
            tile,
            textvariable=var,
            state="readonly",
            readonlybackground="#101010",
            fg="#FFFFFF",
            font=("Arial", 10, "bold"),
            bd=0,
            justify="center"
        )
        entry.pack(fill="x")
        
        # Speichere das Entry-Widget für späteren Zugriff
        self.metrics_entries[key] = entry
        
    def check_api_key(self):
        """Prüft, ob der API-Key funktioniert"""
        try:
            if not config.AXIOM_API_KEY:
                self.api_status_var.set("API: Kein Key")
                self.api_status_label.config(fg="red")
                self.api_available = False
                return
            
            # API-Test mit größerem Timeout
            is_valid = axiom_api.test_api_key()
            
            if is_valid:
                self.api_status_var.set("API: Verbunden")
                self.api_status_label.config(fg="green")
                self.api_available = True
            else:
                self.api_status_var.set("API: Fehler")
                self.api_status_label.config(fg="red")
                self.api_available = False
        except Exception as e:
            print(f"API-Key Test Fehler: {e}")
            self.api_status_var.set("API: Nicht erreichbar")
            self.api_status_label.config(fg="red")
            self.api_available = False
    
    def update_metrics(self, token_address=None):
        """Aktualisiert die Metriken mit Daten von Axiom"""
        # Setze den Status auf "Anfrage gesendet"
        self.update_status_var.set("Letzte Aktualisierung: gerade eben")
        
        # Wenn API nicht verfügbar ist, zeige Hinweis und kehre zurück
        if not self.api_available:
            for key in self.metrics_vars:
                self.metrics_vars[key].set("API offline")
                if key in self.metrics_entries:
                    self.metrics_entries[key].config(readonlybackground="#101010", fg="#666666")
            self.update_status_var.set("API nicht verfügbar - keine Daten abrufbar")
            return
        
        # Verhindere mehrfaches Laden
        if self.is_loading:
            self.update_status_var.set("Aktualisierung läuft bereits...")
            return
            
        self.is_loading = True
        
        # Wenn keine Token-Adresse übergeben wurde, versuche aus den aktuellen Daten zu extrahieren
        if not token_address:
            # Versuche, die Token-Adresse zu bekommen
            address = self.shared_vars['token_address_var'].get()
            if address and address != "N/A":
                token_address = address
            else:
                # Versuche, aus Link zu extrahieren
                link = self.shared_vars['entry_var'].get()
                if link:
                    token_address = axiom_api.extract_address_from_url(link)
        
        # Wenn immer noch keine gültige Adresse, reset und return
        if not token_address or not axiom_api.is_solana_address_format(token_address):
            self.is_loading = False
            self.reset_metrics()
            self.update_status_var.set("Keine gültige Token-Adresse gefunden")
            return
            
        # Setze Loading-Status
        for key in self.metrics_vars:
            self.metrics_vars[key].set("Laden...")
            
        # Starte Thread für API-Abfrage, um UI nicht zu blockieren
        threading.Thread(target=lambda: self._fetch_data(token_address), daemon=True).start()
    
    def _fetch_data(self, token_address):
        """Holte Daten von der API im Hintergrund"""
        try:
            # Holen der Token-Daten mit erhöhtem Timeout
            timeout = 20  # Erhöhter Timeout
            token_data = axiom_api.fetch_axiom_data(token_address, timeout)
            
            # Wenn keine Daten zurückgegeben wurden, reset und return
            if not token_data:
                self.reset_metrics("N/A")
                self.update_status_var.set("Keine Daten von der API erhalten")
                return
            
            # Hole weitere Daten
            holders_data = axiom_api.fetch_top_holders(token_address, timeout)
            traders_data = axiom_api.fetch_top_traders(token_address, timeout)
            
            # Extrahiere die Metriken
            metrics = axiom_api.extract_rugcheck_metrics(token_data, holders_data, traders_data)
            
            # Aktualisiere die UI
            self.update_ui_with_metrics(metrics)
            self.update_status_var.set("Daten erfolgreich aktualisiert")
            
        except Exception as e:
            print(f"Fehler beim Laden der Axiom-Daten: {e}")
            self.reset_metrics("Fehler")
            self.update_status_var.set(f"Fehler: {str(e)[:50]}...")
        finally:
            self.is_loading = False
    
    def update_ui_with_metrics(self, metrics):
        """Aktualisiert die UI mit den extrahierten Metriken"""
        # Top 10 Holders
        self._update_percentage_metric("top_10_holders", metrics["top_10_holders_percent"])
        
        # Dev Holdings
        self._update_percentage_metric("dev_holdings", metrics["dev_holdings_percent"])
        
        # Snipers Holdings
        self._update_percentage_metric("snipers_holdings", metrics["snipers_holdings_percent"])
        
        # Insiders
        self._update_percentage_metric("insiders", metrics["insiders_percent"])
        
        # Bundlers
        self._update_percentage_metric("bundlers", metrics["bundlers_percent"])
        
        # LP Burned
        self._update_percentage_metric("lp_burned", metrics["lp_burned_percent"])
        
        # Holders Count
        self.metrics_vars["holders"].set(f"{metrics['holders_count']:,}")
        self._color_metric_entry("holders", metrics['holders_count'] > 1000, "#d8ffd8", "#ffd8d8")

        # Pro Traders
        self.metrics_vars["pro_traders"].set(f"{metrics['pro_traders_count']}")
        self._color_metric_entry("pro_traders", metrics['pro_traders_count'] > 0, "#d8ffd8", "#ffffff")
        
        # Dex Paid
        paid_text = "Ja" if metrics["dex_paid"] else "Nein"
        self.metrics_vars["dex_paid"].set(paid_text)
        self._color_metric_entry("dex_paid", metrics["dex_paid"], "#d8ffd8", "#ffffff")
    
    def _update_percentage_metric(self, key, value):
        """Aktualisiert eine prozentuale Metrik"""
        self.metrics_vars[key].set(f"{value:.2f}%")
        
        # Bestimme Risikobewertung basierend auf dem Schlüssel und Wert
        is_good = False
        
        if key == "top_10_holders":
            # Top 10 Holder: Niedrig ist gut
            is_good = value <= 30.0
        elif key == "dev_holdings":
            # Dev Holdings: Niedrig ist gut, aber zu niedrig kann schlechtes Engagement zeigen
            is_good = 1.0 <= value <= 10.0
        elif key == "snipers_holdings":
            # Snipers Holdings: Niedrig ist gut
            is_good = value <= 5.0
        elif key == "insiders":
            # Insiders: Wie Dev Holdings, ein Mittelwert ist am besten
            is_good = value <= 15.0
        elif key == "bundlers":
            # Bundlers: Mittelwert ist gut
            is_good = 0.0 < value <= 10.0
        elif key == "lp_burned":
            # LP Burned: Hoch ist gut (100% ist ideal)
            is_good = value > 90.0
        
        # Färbe das Entry-Widget entsprechend
        self._color_metric_entry(key, is_good, "#d8ffd8", "#ffd8d8")
    
    def _color_metric_entry(self, key, is_good, good_color, bad_color):
        """Färbt ein Entry-Widget basierend auf der Risikobewertung"""
        if key in self.metrics_entries:
            entry = self.metrics_entries[key]
            if is_good:
                entry.config(readonlybackground="#101010", fg=good_color)
            else:
                entry.config(readonlybackground="#101010", fg=bad_color)
    
    def reset_metrics(self, default_value="N/A"):
        """Setzt alle Metriken auf den Standardwert zurück"""
        for key in self.metrics_vars:
            self.metrics_vars[key].set(default_value)
            if key in self.metrics_entries:
                self.metrics_entries[key].config(readonlybackground="#101010", fg="#FFFFFF")