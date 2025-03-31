# Coin Finder Tab
import tkinter as tk
from tkinter import ttk
import ui.styles as styles
from config import DEFAULT_WINDOW_SIZE
import data.birdeye_api as birdeye_api
import utils.formatters as formatters
from datetime import datetime
import utils.browser as browser
import data.storage as storage
from tkinter import messagebox
import threading

class CoinFinderTab:
    def __init__(self, parent, shared_vars, main_window):
        self.parent = parent
        self.shared_vars = shared_vars
        self.main_window = main_window
        
        # Eigene Variablen für die Konfiguration der Strategie
        self.strategy_vars = {
            'mcap_min_var': tk.StringVar(parent, "100K"),
            'mcap_max_var': tk.StringVar(parent, "3M"),
            'liquidity_min_var': tk.StringVar(parent, "30K"),
            'coin_age_min_var': tk.StringVar(parent, "0"),
            'coin_age_max_var': tk.StringVar(parent, "5"),
            'dip_percentage_var': tk.StringVar(parent, "20"),
            'buy_sell_ratio_var': tk.StringVar(parent, "1.2"),
            'tx_minimum_var': tk.StringVar(parent, "1000"),
            
            # Gewichtungsvariablen
            'pattern_weight_var': tk.StringVar(parent, "40"),
            'volume_weight_var': tk.StringVar(parent, "35"),
            'timeframe_weight_var': tk.StringVar(parent, "15"),
            'rugpull_weight_var': tk.StringVar(parent, "10"),
            
            # Status-Variablen
            'last_refresh_var': tk.StringVar(parent, "Noch kein Refresh"),
            'auto_refresh_var': tk.BooleanVar(parent, False),
            'refresh_interval_var': tk.StringVar(parent, "60"),
        }
        
        # Liste der gefundenen Coins
        self.coins_data = []
        
        # ID des Auto-Refresh-Timers
        self.auto_refresh_timer_id = None
        
        self.create_tab()
        
    def create_tab(self):
        """Erstellt den Coin Finder Tab mit seinen drei Hauptbereichen"""
        # Hauptcontainer für den Tab
        self.frame = tk.Frame(self.parent, bg="white")
        self.frame.pack(fill="both", expand=True)
        
        # Container 1: Oberer Bereich - Strategie-Konfiguration
        self.config_frame = tk.Frame(self.frame, bg="white", bd=1, relief="solid")
        self.config_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        # Container 2: Mittlerer Bereich - Coin-Liste mit Scoring/Ampelsystem
        self.coins_list_frame = tk.Frame(self.frame, bg="white", bd=1, relief="solid")
        self.coins_list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Container 3: Unterer Bereich - Detail-Ansicht für ausgewählte Coins
        self.detail_frame = tk.Frame(self.frame, bg="white", bd=1, relief="solid")
        self.detail_frame.pack(fill="x", padx=10, pady=(5, 10), ipady=10)
        
        # Fülle die Container mit Inhalten
        self.create_config_area()
        self.create_coins_list()
        self.create_detail_area()
    
    def create_config_area(self):
        """Erstellt den Konfigurationsbereich für die Strategie-Parameter"""
        # Innerer Frame mit Padding
        inner_frame = tk.Frame(self.config_frame, bg="white", padx=15, pady=15)
        inner_frame.pack(fill="x", expand=True)
        
        # Überschrift
        title_label = tk.Label(inner_frame, text="Second Bounce Strategy Konfiguration", bg="white")
        styles.apply_typography(title_label, 'section_header')
        title_label.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))
        
        # Grid konfigurieren
        for i in range(4):  # 4 Spalten
            inner_frame.columnconfigure(i, weight=1)
        
        # Parameter-Bereich
        params_label = tk.Label(inner_frame, text="Filterparameter", bg="white", font=("Arial", 10, "bold"))
        params_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 5))
        
        # MCAP-Grenzen
        self.create_param_field(inner_frame, "MCAP Min:", self.strategy_vars['mcap_min_var'], 2, 0)
        self.create_param_field(inner_frame, "MCAP Max:", self.strategy_vars['mcap_max_var'], 2, 1)
        
        # Liquidität und Coin-Alter
        self.create_param_field(inner_frame, "Liquidität Min:", self.strategy_vars['liquidity_min_var'], 3, 0)
        self.create_param_field(inner_frame, "Coin-Alter (Tage) Min:", self.strategy_vars['coin_age_min_var'], 3, 1)
        self.create_param_field(inner_frame, "Coin-Alter (Tage) Max:", self.strategy_vars['coin_age_max_var'], 3, 2)
        
        # Dip-Prozentsatz und Buy/Sell-Ratio
        self.create_param_field(inner_frame, "Dip %:", self.strategy_vars['dip_percentage_var'], 4, 0)
        self.create_param_field(inner_frame, "Buy/Sell Ratio:", self.strategy_vars['buy_sell_ratio_var'], 4, 1)
        self.create_param_field(inner_frame, "Min. Transaktionen (24h):", self.strategy_vars['tx_minimum_var'], 4, 2)
        
        # Gewichtungsbereich
        weights_label = tk.Label(inner_frame, text="Gewichtungen", bg="white", font=("Arial", 10, "bold"))
        weights_label.grid(row=5, column=0, columnspan=2, sticky="w", pady=(15, 5))
        
        # Gewichtungen
        self.create_param_field(inner_frame, "Muster-Erkennung (%):", self.strategy_vars['pattern_weight_var'], 6, 0)
        self.create_param_field(inner_frame, "Volumen-Bestätigung (%):", self.strategy_vars['volume_weight_var'], 6, 1)
        self.create_param_field(inner_frame, "Zeitrahmen-Übereinstimmung (%):", self.strategy_vars['timeframe_weight_var'], 7, 0)
        self.create_param_field(inner_frame, "Rugpull-Sicherheit (%):", self.strategy_vars['rugpull_weight_var'], 7, 1)
        
        # Refresh-Kontrollen
        refresh_frame = tk.Frame(inner_frame, bg="white")
        refresh_frame.grid(row=8, column=0, columnspan=4, sticky="ew", pady=(15, 0))
        
        # Status-Label
        status_label = tk.Label(refresh_frame, textvariable=self.strategy_vars['last_refresh_var'], bg="white", font=("Arial", 9))
        status_label.pack(side="left", padx=(0, 10))
        
        # Auto-Refresh Checkbox
        auto_refresh_cb = tk.Checkbutton(
            refresh_frame, 
            text="Auto-Refresh alle", 
            variable=self.strategy_vars['auto_refresh_var'],
            bg="white",
            command=self.toggle_auto_refresh
        )
        auto_refresh_cb.pack(side="left")
        
        # Intervall-Eingabefeld
        interval_entry = tk.Entry(refresh_frame, textvariable=self.strategy_vars['refresh_interval_var'], width=4)
        interval_entry.pack(side="left", padx=(0, 5))
        
        tk.Label(refresh_frame, text="Sekunden", bg="white").pack(side="left", padx=(0, 10))
        
        # Manueller Refresh-Button
        refresh_btn = tk.Button(refresh_frame, text="Refresh", command=self.refresh_data)
        refresh_btn.pack(side="right")
    
    def create_param_field(self, parent, label_text, variable, row, column):
        """Erstellt ein beschriftetes Eingabefeld für Strategie-Parameter"""
        container = tk.Frame(parent, bg="white")
        container.grid(row=row, column=column, sticky="w", padx=5, pady=2)
        
        # Label
        label = tk.Label(container, text=label_text, bg="white", anchor="w", width=20)
        label.pack(side="left")
        
        # Eingabefeld
        entry = tk.Entry(container, textvariable=variable, width=8)
        entry.pack(side="left", padx=(0, 5))
        
        return container
    
    def create_coins_list(self):
        """Erstellt die Liste der gefundenen Coins mit dem Ampelsystem"""
        # Padding-Frame
        padding_frame = tk.Frame(self.coins_list_frame, bg="white", padx=15, pady=15)
        padding_frame.pack(fill="both", expand=True)
        
        # Überschrift
        title_frame = tk.Frame(padding_frame, bg="white")
        title_frame.pack(fill="x", pady=(0, 10))
        
        title_label = tk.Label(title_frame, text="Gefundene Token", bg="white")
        styles.apply_typography(title_label, 'section_header')
        title_label.pack(side="left")
        
        # Treeview für Coins erstellen
        self.coins_tree_frame = tk.Frame(padding_frame, bg="white")
        self.coins_tree_frame.pack(fill="both", expand=True)
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(self.coins_tree_frame, orient="vertical")
        y_scrollbar.pack(side="right", fill="y")
        
        # Treeview
        self.coins_tree = ttk.Treeview(
            self.coins_tree_frame,
            columns=("Symbol", "MCAP", "Score", "Potential", "Volume", "Reason"),
            show="headings",
            style="Treeview",
            yscrollcommand=y_scrollbar.set
        )
        
        # Konfiguriere die Scrollbars
        y_scrollbar.config(command=self.coins_tree.yview)
        
        # Definiere die Spaltenüberschriften
        self.coins_tree.heading("Symbol", text="Symbol")
        self.coins_tree.heading("MCAP", text="MCAP")
        self.coins_tree.heading("Score", text="Score")
        self.coins_tree.heading("Potential", text="Potential")
        self.coins_tree.heading("Volume", text="Vol. Trend")
        self.coins_tree.heading("Reason", text="Hauptgrund")
        
        # Definiere Zeilen-Farbtags
        self.coins_tree.tag_configure("green", background="#d8ffd8")  # Grün für "Strong Buy"
        self.coins_tree.tag_configure("yellow", background="#fff3cd")  # Gelb für "Potential Entry"
        self.coins_tree.tag_configure("red", background="#ffd8d8")  # Rot für "Monitor Only"
        
        # Definiere die Spaltenbreiten
        self.coins_tree.column("Symbol", width=80, minwidth=80, anchor="w")
        self.coins_tree.column("MCAP", width=80, minwidth=80, anchor="center")
        self.coins_tree.column("Score", width=60, minwidth=60, anchor="center")
        self.coins_tree.column("Potential", width=70, minwidth=70, anchor="center")
        self.coins_tree.column("Volume", width=80, minwidth=80, anchor="center")
        self.coins_tree.column("Reason", width=200, minwidth=200, anchor="w")
        
        self.coins_tree.pack(fill="both", expand=True)
        
        # Binde Ereignisse
        self.coins_tree.bind("<Double-1>", self.on_coin_double_click)
        self.coins_tree.bind("<<TreeviewSelect>>", self.on_coin_select)
        
        # # Zeige Platzhalter-Daten für die Demo
        # self.insert_placeholder_data()
    
    def create_detail_area(self):
        """Erstellt den Detailbereich für ausgewählte Coins"""
        # Padding-Frame
        padding_frame = tk.Frame(self.detail_frame, bg="white", padx=15, pady=15)
        padding_frame.pack(fill="both", expand=True)
        
        # Überschrift
        title_label = tk.Label(padding_frame, text="Token-Details", bg="white")
        styles.apply_typography(title_label, 'section_header')
        title_label.pack(anchor="w", pady=(0, 10))
        
        # Zwei Spalten für Details
        details_frame = tk.Frame(padding_frame, bg="white")
        details_frame.pack(fill="x", expand=True)
        details_frame.columnconfigure(0, weight=1)
        details_frame.columnconfigure(1, weight=1)
        
        # Linke Spalte - Grunddaten
        left_frame = tk.Frame(details_frame, bg="white")
        left_frame.grid(row=0, column=0, sticky="nw", padx=(0, 10))
        
        # Variablen für Detailansicht
        self.detail_vars = {
            'symbol_var': tk.StringVar(self.parent, ""),
            'name_var': tk.StringVar(self.parent, ""),
            'mcap_var': tk.StringVar(self.parent, ""),
            'liquidity_var': tk.StringVar(self.parent, ""),
            'age_var': tk.StringVar(self.parent, ""),
            'holders_var': tk.StringVar(self.parent, ""),
            
            # Score-Details
            'pattern_score_var': tk.StringVar(self.parent, ""),
            'volume_score_var': tk.StringVar(self.parent, ""),
            'timeframe_score_var': tk.StringVar(self.parent, ""),
            'rugpull_score_var': tk.StringVar(self.parent, ""),
            'total_score_var': tk.StringVar(self.parent, ""),
            
            # Hauptgrund
            'main_reason_var': tk.StringVar(self.parent, "")
        }
        
        # Basisdaten
        tk.Label(left_frame, text="Symbol:", bg="white", anchor="w", width=12).grid(row=0, column=0, sticky="w", pady=2)
        tk.Entry(left_frame, textvariable=self.detail_vars['symbol_var'], width=20, state="readonly").grid(row=0, column=1, sticky="w", pady=2)
        
        tk.Label(left_frame, text="Name:", bg="white", anchor="w", width=12).grid(row=1, column=0, sticky="w", pady=2)
        tk.Entry(left_frame, textvariable=self.detail_vars['name_var'], width=20, state="readonly").grid(row=1, column=1, sticky="w", pady=2)
        
        tk.Label(left_frame, text="MCAP:", bg="white", anchor="w", width=12).grid(row=2, column=0, sticky="w", pady=2)
        tk.Entry(left_frame, textvariable=self.detail_vars['mcap_var'], width=20, state="readonly").grid(row=2, column=1, sticky="w", pady=2)
        
        tk.Label(left_frame, text="Liquidität:", bg="white", anchor="w", width=12).grid(row=3, column=0, sticky="w", pady=2)
        tk.Entry(left_frame, textvariable=self.detail_vars['liquidity_var'], width=20, state="readonly").grid(row=3, column=1, sticky="w", pady=2)
        
        tk.Label(left_frame, text="Alter (Tage):", bg="white", anchor="w", width=12).grid(row=4, column=0, sticky="w", pady=2)
        tk.Entry(left_frame, textvariable=self.detail_vars['age_var'], width=20, state="readonly").grid(row=4, column=1, sticky="w", pady=2)
        
        tk.Label(left_frame, text="Holder:", bg="white", anchor="w", width=12).grid(row=5, column=0, sticky="w", pady=2)
        tk.Entry(left_frame, textvariable=self.detail_vars['holders_var'], width=20, state="readonly").grid(row=5, column=1, sticky="w", pady=2)
        
        # Rechte Spalte - Score-Details
        right_frame = tk.Frame(details_frame, bg="white")
        right_frame.grid(row=0, column=1, sticky="nw")
        
        # Überschrift für Score
        tk.Label(right_frame, text="Score-Details:", bg="white", font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))
        
        # Score-Details
        tk.Label(right_frame, text="Muster:", bg="white", anchor="w", width=15).grid(row=1, column=0, sticky="w", pady=2)
        tk.Entry(right_frame, textvariable=self.detail_vars['pattern_score_var'], width=10, state="readonly").grid(row=1, column=1, sticky="w", pady=2)
        
        tk.Label(right_frame, text="Volumen:", bg="white", anchor="w", width=15).grid(row=2, column=0, sticky="w", pady=2)
        tk.Entry(right_frame, textvariable=self.detail_vars['volume_score_var'], width=10, state="readonly").grid(row=2, column=1, sticky="w", pady=2)
        
        tk.Label(right_frame, text="Zeitrahmen:", bg="white", anchor="w", width=15).grid(row=3, column=0, sticky="w", pady=2)
        tk.Entry(right_frame, textvariable=self.detail_vars['timeframe_score_var'], width=10, state="readonly").grid(row=3, column=1, sticky="w", pady=2)
        
        tk.Label(right_frame, text="Rugpull-Sicherheit:", bg="white", anchor="w", width=15).grid(row=4, column=0, sticky="w", pady=2)
        tk.Entry(right_frame, textvariable=self.detail_vars['rugpull_score_var'], width=10, state="readonly").grid(row=4, column=1, sticky="w", pady=2)
        
        tk.Label(right_frame, text="Gesamt-Score:", bg="white", anchor="w", width=15, font=("Arial", 10, "bold")).grid(row=5, column=0, sticky="w", pady=2)
        tk.Entry(right_frame, textvariable=self.detail_vars['total_score_var'], width=10, state="readonly", font=("Arial", 10, "bold")).grid(row=5, column=1, sticky="w", pady=2)
        
        # Hauptgrund
        reason_frame = tk.Frame(padding_frame, bg="white")
        reason_frame.pack(fill="x", pady=(10, 0))
        
        tk.Label(reason_frame, text="Hauptgrund:", bg="white", font=("Arial", 10, "bold")).pack(anchor="w")
        tk.Entry(reason_frame, textvariable=self.detail_vars['main_reason_var'], width=70, state="readonly").pack(fill="x", pady=(5, 0))
        
        # Aktions-Buttons
        action_frame = tk.Frame(padding_frame, bg="white")
        action_frame.pack(fill="x", pady=(10, 0))
        
        open_button = tk.Button(action_frame, text="Im Main Bot öffnen", command=self.open_in_main_bot)
        open_button.pack(side="left", padx=(0, 10))
        
        call_button = tk.Button(action_frame, text="Call erstellen", command=self.create_call)
        call_button.pack(side="left", padx=(0, 10))
        
        watch_button = tk.Button(action_frame, text="Zur Watchlist hinzufügen", command=self.add_to_watchlist)
        watch_button.pack(side="left")
    
    def refresh_data(self):
        """Aktualisiert die Coin-Daten basierend auf der aktuellen Konfiguration"""
        # Update des Refresh-Labels mit aktuellem Timestamp
        current_time = datetime.now().strftime("%H:%M:%S")
        self.strategy_vars['last_refresh_var'].set(f"Letzter Refresh: {current_time}")
        
        # Starte den API-Abruf in einem separaten Thread, um die UI nicht zu blockieren
        threading.Thread(target=self.fetch_data_in_thread).start()

    def fetch_data_in_thread(self):
        """Führt den API-Abruf in einem separaten Thread durch"""
        try:
            # Parameter aus den Eingabefeldern holen
            try:
                mcap_min = formatters.parse_km(self.strategy_vars['mcap_min_var'].get())
                mcap_max = formatters.parse_km(self.strategy_vars['mcap_max_var'].get())
                liquidity_min = formatters.parse_km(self.strategy_vars['liquidity_min_var'].get())
                age_min = int(self.strategy_vars['coin_age_min_var'].get())
                age_max = int(self.strategy_vars['coin_age_max_var'].get())
                min_tx = int(self.strategy_vars['tx_minimum_var'].get())
                
                # Gewichtungen auslesen (mit Fehlerbehandlung für ungültige Eingaben)
                try:
                    pattern_weight = int(self.strategy_vars['pattern_weight_var'].get())
                except ValueError:
                    pattern_weight = 40 # Standardwert
                    self.strategy_vars['pattern_weight_var'].set("40")
                try:
                    volume_weight = int(self.strategy_vars['volume_weight_var'].get())
                except ValueError:
                    volume_weight = 35 # Standardwert
                    self.strategy_vars['volume_weight_var'].set("35")
                try:
                    timeframe_weight = int(self.strategy_vars['timeframe_weight_var'].get())
                except ValueError:
                    timeframe_weight = 15 # Standardwert
                    self.strategy_vars['timeframe_weight_var'].set("15")
                try:
                    rugpull_weight = int(self.strategy_vars['rugpull_weight_var'].get())
                except ValueError:
                    rugpull_weight = 10 # Standardwert
                    self.strategy_vars['rugpull_weight_var'].set("10")

            except ValueError:
                # Standard-Werte bei Fehler für Filter
                mcap_min = 100000    # 100K
                mcap_max = 3000000   # 3M
                liquidity_min = 30000  # 30K
                age_min = 0
                age_max = 5
                min_tx = 1000
                # Standard-Gewichtungen bei Fehler
                pattern_weight = 40
                volume_weight = 35
                timeframe_weight = 15
                rugpull_weight = 10
            
            # Prüfe, ob ein API-Key vorhanden ist
            api_key = birdeye_api.get_api_key()
            if not api_key:
                # Wenn kein API-Key vorhanden ist, zeige Platzhalter-Daten
                # self.parent.after(0, self.insert_placeholder_data) # Auskommentiert
                self.parent.after(0, lambda: messagebox.showinfo("API-Key fehlt", 
                    "Kein Birdeye API-Key gefunden. Bitte speichere einen gültigen API-Key in der Datei unter dem Pfad:\n" + 
                    f"{birdeye_api.API_KEY_FILE}"))
                return
            
            # Scanne Tokens mit der Strategie
            limit = 20  # Maximale Anzahl der zu analysierenden Tokens
            
            # API-Aufruf
            results = birdeye_api.scan_tokens_for_strategy(
                mcap_min=mcap_min,
                mcap_max=mcap_max,
                liquidity_min=liquidity_min,
                age_min=age_min,
                age_max=age_max,
                min_tx=min_tx,
                limit=limit,
                # Gewichtungen übergeben
                pattern_weight=pattern_weight,
                volume_weight=volume_weight,
                timeframe_weight=timeframe_weight,
                rugpull_weight=rugpull_weight
            )
            
            # Speichere die Ergebnisse für später
            self.coins_data = results
            
            # Aktualisiere die UI im Hauptthread
            self.parent.after(0, lambda: self.update_ui_with_results(results))
            
        except Exception as e:
            # Speichere die Fehlermeldung
            error_message = str(e)
            # Fehlermeldung im Hauptthread anzeigen
            self.parent.after(0, lambda: messagebox.showerror("Fehler", f"Fehler beim Abrufen der Daten: {error_message}"))

    def update_ui_with_results(self, results):
        """Aktualisiert die UI mit den API-Ergebnissen"""
        # Lösche vorhandene Daten
        self.coins_tree.delete(*self.coins_tree.get_children())
        
        # Keine Ergebnisse?
        if not results:
            return
        
        # Füge die Ergebnisse in die Treeview ein
        for result in results:
            # Extrahiere die Daten für die UI
            ui_data = birdeye_api.extract_token_data_for_ui(result)
            
            # Bestimme die Farbe basierend auf dem Score
            score_str = ui_data[2]
            if "/" in score_str:
                score = int(score_str.split("/")[0])  # Extrahiere den Score vor dem "/"
            else:
                score = int(score_str) # Fallback, falls kein "/" vorhanden
            if score >= 85:
                tag = "green"
            elif score >= 70:
                tag = "yellow"
            else:
                tag = "red"
            
            # Füge in die Treeview ein
            self.coins_tree.insert(
                "",
                "end",
                values=ui_data, # ui_data enthält jetzt Score als "X/Y"
                tags=(tag,)
            )
    
    def toggle_auto_refresh(self):
        """Aktiviert oder deaktiviert das automatische Aktualisieren"""
        if self.strategy_vars['auto_refresh_var'].get():
            # Auto-Refresh aktivieren
            self.start_auto_refresh()
        else:
            # Auto-Refresh deaktivieren
            self.stop_auto_refresh()
    
    def start_auto_refresh(self):
        """Startet den Auto-Refresh-Timer"""
        # Stoppe vorherige Timer, falls vorhanden
        self.stop_auto_refresh()
        
        # Hole das Intervall (in Sekunden)
        try:
            interval = int(self.strategy_vars['refresh_interval_var'].get()) * 1000  # in Millisekunden umwandeln
            if interval < 10000:  # Minimales Intervall: 10 Sekunden
                interval = 10000
                self.strategy_vars['refresh_interval_var'].set("10")
        except ValueError:
            interval = 60000  # Standard: 60 Sekunden
            self.strategy_vars['refresh_interval_var'].set("60")
        
        # Starte den Timer
        self.refresh_data()  # Sofort aktualisieren
        self.auto_refresh_timer_id = self.parent.after(interval, self.auto_refresh_cycle)
    
    def auto_refresh_cycle(self):
        """Wird periodisch aufgerufen, um die Daten zu aktualisieren"""
        # Aktualisiere die Daten
        self.refresh_data()
        
        # Plane den nächsten Aufruf, wenn Auto-Refresh noch aktiv ist
        if self.strategy_vars['auto_refresh_var'].get():
            try:
                interval = int(self.strategy_vars['refresh_interval_var'].get()) * 1000
                if interval < 10000:
                    interval = 10000
            except ValueError:
                interval = 60000
                
            self.auto_refresh_timer_id = self.parent.after(interval, self.auto_refresh_cycle)
    
    def stop_auto_refresh(self):
        """Stoppt den Auto-Refresh-Timer"""
        if self.auto_refresh_timer_id:
            self.parent.after_cancel(self.auto_refresh_timer_id)
            self.auto_refresh_timer_id = None
    
    def on_coin_select(self, event):
        """Wird aufgerufen, wenn ein Coin in der Liste ausgewählt wird"""
        selected_items = self.coins_tree.selection()
        if not selected_items:
            return
            
        # Hole die Daten des ausgewählten Coins
        item = selected_items[0]
        values = self.coins_tree.item(item, "values")
        
        # Finde die vollständigen Daten in coins_data
        selected_analysis = None
        for analysis in self.coins_data:
            # Versuche, den Symbolnamen aus der Analyse zu extrahieren
            # Beachte, dass die Struktur von 'analysis' jetzt anders sein könnte
            token_info = analysis.get("token_info", {})
            token_symbol = token_info.get("symbol", "") # Direkt aus token_info
            if not token_symbol: # Fallback, falls nicht in token_info
                 token_symbol = analysis.get("symbol", "") # Direkt aus analysis

            if f"${token_symbol}" == values[0]:
                selected_analysis = analysis
                break
        
        if not selected_analysis:
            print(f"Keine Analyse für {values[0]} gefunden.")
            return
        
        # Extrahiere Daten aus der Analyse
        token_info = selected_analysis.get("token_info", {})
        # price_info = selected_analysis.get("price_info", {}).get("data", {}) # Nicht mehr verfügbar
        # holder_info = selected_analysis.get("holder_info", {}).get("data", {}) # Nicht mehr verfügbar
        
        # Aktualisiere die Detailansicht
        self.detail_vars['symbol_var'].set(values[0])
        self.detail_vars['name_var'].set(token_info.get("name", "N/A"))
        self.detail_vars['mcap_var'].set(values[1])  # MCAP aus der Treeview
        
        # Liquidität
        liquidity = token_info.get("liquidity", 0)
        self.detail_vars['liquidity_var'].set(formatters.format_k(liquidity))
        
        # Alter (in Tagen) - Nicht mehr verfügbar
        # created_at = token_info.get("created_at", 0)
        # if created_at:
        #     from datetime import datetime, timezone
        #     created_dt = datetime.fromtimestamp(created_at, tz=timezone.utc)
        #     now = datetime.now(tz=timezone.utc)
        #     age_days = (now - created_dt).days
        #     self.detail_vars['age_var'].set(str(age_days))
        # else:
        self.detail_vars['age_var'].set("N/A")
        
        # Anzahl der Holder - Nicht mehr verfügbar
        # holders_count = len(holder_info.get("items", []))
        self.detail_vars['holders_var'].set("N/A")
        
        # Score-Details
        pattern_score = selected_analysis["score"]["pattern"]
        volume_score = selected_analysis["score"]["volume"]
        timeframe_score = selected_analysis["score"]["timeframe"]
        rugpull_score = selected_analysis["score"]["rugpull"]
        total_score = selected_analysis["score"]["total"]
        
        # Hole die verwendeten Gewichtungen aus der Analyse
        weights = selected_analysis.get("weights", {})
        pattern_weight = weights.get("pattern", 40)
        volume_weight = weights.get("volume", 35)
        timeframe_weight = weights.get("timeframe", 15)
        rugpull_weight = weights.get("rugpull", 10)
        total_weight = sum(weights.values()) if weights else 100

        self.detail_vars['pattern_score_var'].set(f"{pattern_score}/{pattern_weight}")
        self.detail_vars['volume_score_var'].set(f"{volume_score}/{volume_weight}")
        self.detail_vars['timeframe_score_var'].set(f"{timeframe_score}/{timeframe_weight}")
        self.detail_vars['rugpull_score_var'].set(f"{rugpull_score}/{rugpull_weight}")
        self.detail_vars['total_score_var'].set(f"{total_score}/{total_weight}")
        
        # Hauptgrund
        self.detail_vars['main_reason_var'].set(selected_analysis["main_reason"])

    def on_coin_double_click(self, event):
        """Wird aufgerufen, wenn ein Coin in der Liste doppelt angeklickt wird"""
        self.open_in_main_bot()

    def open_in_main_bot(self):
        """Öffnet den ausgewählten Coin im Main Bot Tab"""
        selected_items = self.coins_tree.selection()
        if not selected_items:
            messagebox.showinfo("Hinweis", "Bitte wähle zuerst einen Token aus.")
            return
            
        # Hole die Daten des ausgewählten Coins
        item = selected_items[0]
        values = self.coins_tree.item(item, "values")
        
        # Finde die vollständigen Daten in coins_data
        selected_analysis = None
        for analysis in self.coins_data:
            # Versuche, den Symbolnamen aus der Analyse zu extrahieren
            token_info = analysis.get("token_info", {})
            token_symbol = token_info.get("symbol", "") # Direkt aus token_info
            if not token_symbol: # Fallback, falls nicht in token_info
                 token_symbol = analysis.get("symbol", "") # Direkt aus analysis

            if f"${token_symbol}" == values[0]:
                selected_analysis = analysis
                break
        
        if not selected_analysis:
            messagebox.showerror("Fehler", "Token-Daten nicht gefunden.")
            return
        
        # Hole die Token-Adresse
        token_address = selected_analysis["token_address"]
        
        # Erstelle den DexScreener-Link
        dex_link = f"https://dexscreener.com/solana/{token_address}"
        
        # Setze den Link in das Hauptfenster und öffne es im Main Bot
        self.main_window.shared_vars['entry_var'].set(dex_link)
        self.main_window.fetch_data()
        self.main_window.notebook.select(self.main_window.tabs['main'])

    def create_call(self):
        """Erstellt einen Call für den ausgewählten Coin"""
        selected_items = self.coins_tree.selection()
        if not selected_items:
            messagebox.showinfo("Hinweis", "Bitte wähle zuerst einen Token aus.")
            return
            
        # Hole die Daten des ausgewählten Coins
        item = selected_items[0]
        values = self.coins_tree.item(item, "values")
        
        # Finde die vollständigen Daten in coins_data
        selected_analysis = None
        for analysis in self.coins_data:
            # Versuche, den Symbolnamen aus der Analyse zu extrahieren
            token_info = analysis.get("token_info", {})
            token_symbol = token_info.get("symbol", "") # Direkt aus token_info
            if not token_symbol: # Fallback, falls nicht in token_info
                 token_symbol = analysis.get("symbol", "") # Direkt aus analysis

            if f"${token_symbol}" == values[0]:
                selected_analysis = analysis
                break
        
        if not selected_analysis:
            messagebox.showerror("Fehler", "Token-Daten nicht gefunden.")
            return
        
        # Hole die benötigten Daten
        symbol = values[0]  # Symbol aus der Treeview
        mcap = values[1]    # MCAP aus der Treeview
        token_address = selected_analysis["token_address"]
        
        # Erstelle den DexScreener-Link
        dex_link = f"https://dexscreener.com/solana/{token_address}"
        
        # Liquidität aus der Analyse
        token_info = selected_analysis.get("token_info", {})
        liquidity = token_info.get("liquidity", 0)
        liquidity_str = formatters.format_k(liquidity)
        
        # Erstelle neuen Call
        try:
            new_call = storage.create_new_call(symbol, mcap, liquidity_str, dex_link)
            storage.save_new_call(new_call)
            
            # Aktualisiere die Calls TreeView
            if hasattr(self.main_window, 'update_calls_tree'):
                self.main_window.update_calls_tree()
                
            # Bestätigungsmeldung und Wechsel zum Calls-Tab
            messagebox.showinfo("Erfolg", f"Call für {symbol} wurde erstellt.")
            self.main_window.notebook.select(self.main_window.tabs['calls'])
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Erstellen des Calls: {e}")

    def add_to_watchlist(self):
        """Fügt den ausgewählten Coin zur Beobachtungsliste hinzu"""
        selected_items = self.coins_tree.selection()
        if not selected_items:
            messagebox.showinfo("Hinweis", "Bitte wähle zuerst einen Token aus.")
            return
            
        # Hole die Daten des ausgewählten Coins
        item = selected_items[0]
        values = self.coins_tree.item(item, "values")
        
        # Finde die vollständigen Daten in coins_data
        selected_analysis = None
        for analysis in self.coins_data:
            # Versuche, den Symbolnamen aus der Analyse zu extrahieren
            token_info = analysis.get("token_info", {})
            token_symbol = token_info.get("symbol", "") # Direkt aus token_info
            if not token_symbol: # Fallback, falls nicht in token_info
                 token_symbol = analysis.get("symbol", "") # Direkt aus analysis

            if f"${token_symbol}" == values[0]:
                selected_analysis = analysis
                break
        
        if not selected_analysis:
            messagebox.showerror("Fehler", "Token-Daten nicht gefunden.")
            return
        
        # Hole die benötigten Daten
        symbol = values[0]  # Symbol aus der Treeview
        mcap = values[1]    # MCAP aus der Treeview
        token_address = selected_analysis["token_address"]
        
        # Erstelle den DexScreener-Link
        dex_link = f"https://dexscreener.com/solana/{token_address}"
        
        # Erstelle neuen Watchlist-Eintrag
        try:
            watchlist_item = storage.create_new_watchlist_item(symbol, mcap, dex_link)
            storage.save_new_watchlist_item(watchlist_item)
            
            # Aktualisiere die Watchlist TreeView
            if hasattr(self.main_window, 'update_watchlist_tree'):
                self.main_window.update_watchlist_tree()
                
            # Bestätigungsmeldung und Wechsel zum Watchlist-Tab
            messagebox.showinfo("Erfolg", f"{symbol} wurde zur Beobachtungsliste hinzugefügt.")
            self.main_window.notebook.select(self.main_window.tabs['watchlist'])
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Hinzufügen zur Beobachtungsliste: {e}")
