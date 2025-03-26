# Hauptfenster
import tkinter as tk
from tkinter import ttk, messagebox
import ui.styles as styles
from config import DEFAULT_WINDOW_SIZE, DEFAULT_WINDOW_TITLE

class MainWindow:
    def __init__(self, root):
        self.root = root
        # Dictionary für die Tabs, damit andere Module darauf zugreifen können
        self.tabs = {}
        # Variablen, die zwischen Modulen geteilt werden
        self.shared_vars = {
            'entry_var': tk.StringVar(root),
            'token_blockchain_var': tk.StringVar(root),
            'token_name_var': tk.StringVar(root),
            'token_symbol_var': tk.StringVar(root),
            'token_address_var': tk.StringVar(root),
            'mcap_var': tk.StringVar(root),
            'liq_var': tk.StringVar(root),
            'vol24_var': tk.StringVar(root),
            'dexscreener_var': tk.StringVar(root),
            'website_var': tk.StringVar(root),
            'twitter_var': tk.StringVar(root),
            'telegram_var': tk.StringVar(root),
            'discord_var': tk.StringVar(root),
            'live_update_active': tk.BooleanVar(root, value=True),
            'current_data': None,
        }
        # Listen für Timeframe-Daten
        self.time_price_vars = []
        self.time_buys_vars = []
        self.time_sells_vars = []

        self.setup_window()
        self.create_dashboard()
        self.create_notebook()
        self.create_profit_container()

    def setup_window(self):
        """Grundlegende Fenstereinstellungen"""
        self.root.title(DEFAULT_WINDOW_TITLE)
        self.root.geometry(DEFAULT_WINDOW_SIZE)
        self.root.resizable(True, True)  # Erlaube Größenänderung
        self.root.configure(bg="#cccccc")
        # Styles einrichten
        styles.setup_styles()
        
        # Optional: Mindestgröße setzen
        self.root.minsize(630, 800)

    def create_dashboard(self):
        """Erstellt das Dashboard mit Eingabefeld und Widgets"""
        # Entferne pack_propagate(False)
        self.dashboard_frame = tk.Frame(self.root, bg="#cccccc")
        self.dashboard_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        
        # Konfiguriere Grid für gleichmäßige Spaltenverteilung
        self.dashboard_frame.columnconfigure(0, weight=1)
        self.dashboard_frame.columnconfigure(1, weight=1)
        
        # Erstelle zwei Spalten im Dashboard
        left_column = tk.Frame(self.dashboard_frame, bg="#cccccc")
        left_column.grid(row=0, column=0, sticky="nsew")
        
        right_column = tk.Frame(self.dashboard_frame, bg="#cccccc")
        right_column.grid(row=0, column=1, sticky="nsew")
        
        # Rest des Codes bleibt unverändert, nur mit grid() statt pack()
        ...
        
        # Eingabefeld-Sektion in der linken Spalte
        input_section = tk.Frame(left_column, bg="#cccccc")
        input_section.pack(anchor="w", fill="x", pady=5)
        
        lbl_header = tk.Label(input_section, text="Dexscreener Link", bg="#cccccc", font=("Arial", 10, "bold"))
        lbl_header.pack(anchor="w")
        
        self.entry = tk.Entry(input_section, textvariable=self.shared_vars['entry_var'], width=50)
        self.entry.pack(anchor="w", pady=(5,0))
        self.entry.bind("<Return>", lambda event: self.fetch_data())
        
        self.paste_button = tk.Button(input_section, text="Zwischenablage einfügen", command=self.paste_and_fetch)
        self.paste_button.pack(anchor="w", pady=(5,0))
        
        # Control-Buttons in der rechten Spalte
        control_section = tk.Frame(right_column, bg="#cccccc")
        control_section.pack(anchor="e", fill="x", pady=5)
        
        # Button zum Zurücksetzen des Kontostands
        self.reset_budget_btn = tk.Button(control_section, text="Kontostand zurücksetzen", command=self.reset_budget)
        self.reset_budget_btn.pack(side="right", padx=(10, 0))
        
        # Live Update Button
        self.live_update_btn = tk.Button(control_section, text="Live Update AN", command=self.toggle_live_update, bg="#d8ffd8")
        self.live_update_btn.pack(side="right", padx=(10, 0))
        

    def create_notebook(self):
        """Erstellt das Notebook mit Tabs"""
        self.notebook_frame = tk.Frame(self.root)
        self.notebook_frame.pack(side="top", fill="both", expand=True)
        
        self.notebook = ttk.Notebook(self.notebook_frame)
        self.notebook.pack(fill="both", expand=True)

        # Erstelle die Tabs
        self.tab1 = tk.Frame(self.notebook, bg="white")
        self.tab2 = tk.Frame(self.notebook, bg="white")
        self.tab3 = tk.Frame(self.notebook, bg="white")
        
        # Konfiguriere Grid für gleichmäßige Spaltenbreite im Main Bot Tab
        self.tab1.grid_columnconfigure(0, weight=1, uniform="equal_columns")  # Linke Spalte
        self.tab1.grid_columnconfigure(1, weight=1, uniform="equal_columns")  # Rechte Spalte
        
        self.notebook.add(self.tab1, text="Main Bot")
        self.notebook.add(self.tab2, text="Meine Calls")
        self.notebook.add(self.tab3, text="Abgeschlossene Calls")
        
        # Speichere Tabs im Dictionary für Zugriff aus anderen Modulen
        self.tabs['main'] = self.tab1
        self.tabs['calls'] = self.tab2
        self.tabs['archived'] = self.tab3

    def create_profit_container(self):
        """Erstellt den Container für Gewinnberechnung"""
        self.profit_container = tk.Frame(self.root, bg="#e0e0e0", bd=1, relief="groove")
        self.profit_container.pack(fill="x", padx=10, pady=(0,10))  # Nur horizontales Füllen, nicht vertikal expandieren

        # Konfiguriere das Grid für 2 Reihen und 3 Spalten
        for i in range(2):
            self.profit_container.grid_rowconfigure(i, weight=1)
        for j in range(3):
            self.profit_container.grid_columnconfigure(j, weight=1)

        # Kompaktere Einträge mit einheitlichem Stil
        self.total_invest_label = self.create_profit_entry("Investiert: 0.00$")
        self.total_invest_label.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")

        self.num_calls_label = self.create_profit_entry("Calls: 0")
        self.num_calls_label.grid(row=0, column=1, padx=2, pady=2, sticky="nsew")

        self.total_profit_label = self.create_profit_entry("Gesamt Gewinn/Verlust: 0.00$")
        self.total_profit_label.grid(row=0, column=2, padx=2, pady=2, sticky="nsew")

        self.profit_percent_label = self.create_profit_entry("Gewinn/Verlust (%): 0.00%")
        self.profit_percent_label.grid(row=1, column=0, padx=2, pady=2, sticky="nsew")

        self.avg_profit_label = self.create_profit_entry("Durchschnitt pro Call: 0.00$")
        self.avg_profit_label.grid(row=1, column=1, padx=2, pady=2, sticky="nsew")

        self.current_balance_label = self.create_profit_entry("Kontostand: 500.00$")
        self.current_balance_label.grid(row=1, column=2, padx=2, pady=2, sticky="nsew")

    def create_profit_entry(self, initial_text):
        """Erstellt ein Entry-Widget für den Gewinnrechner im einheitlichen Stil"""
        entry = tk.Entry(self.profit_container, justify="center", font=("Arial", 9))
        entry.insert(0, initial_text)
        entry.config(state="readonly", readonlybackground="white")
        return entry


    def create_profit_section(self, parent):
        """Erstellt die Gewinnrechner-Sektion im Dashboard"""
        profit_section = tk.Frame(parent, bg="white", bd=1, relief="groove", padx=15, pady=10)
        profit_section.pack(fill="x", padx=25, pady=(10,0))
        
        # Titel für die Sektion
        tk.Label(profit_section, text="Gewinnübersicht", font=("Arial", 10, "bold"), bg="white").pack(anchor="w")
        
        # Grid für die Statistik-Labels
        stats_frame = tk.Frame(profit_section, bg="white")
        stats_frame.pack(fill="x", pady=5)
        
        # Konfiguriere das Grid für 2 Reihen und 3 Spalten
        for i in range(2):
            stats_frame.grid_rowconfigure(i, weight=1)
        for j in range(3):
            stats_frame.grid_columnconfigure(j, weight=1)
        
        # Widget 1: Gesamtinvestition
        self.total_invest_label = tk.Label(stats_frame, text="Investiert: 0.00$", font=("Arial", 9), bg="#f0f0f0")
        self.total_invest_label.grid(row=0, column=0, padx=5, pady=2, sticky="nsew")
        
        # Widget 2: Anzahl der Calls
        self.num_calls_label = tk.Label(stats_frame, text="Calls: 0", font=("Arial", 9), bg="#f0f0f0")
        self.num_calls_label.grid(row=0, column=1, padx=5, pady=2, sticky="nsew")
        
        # Widget 3: Gesamt Gewinn/Verlust (absolut)
        self.total_profit_label = tk.Label(stats_frame, text="Gesamt Gewinn/Verlust: 0.00$", font=("Arial", 9), bg="#f0f0f0")
        self.total_profit_label.grid(row=0, column=2, padx=5, pady=2, sticky="nsew")
        
        # Widget 4: Gewinn/Verlust in Prozent
        self.profit_percent_label = tk.Label(stats_frame, text="Gewinn/Verlust (%): 0.00%", font=("Arial", 9), bg="#f0f0f0")
        self.profit_percent_label.grid(row=1, column=0, padx=5, pady=2, sticky="nsew")
        
        # Widget 5: Durchschnittlicher Gewinn/Verlust pro Call
        self.avg_profit_label = tk.Label(stats_frame, text="Durchschnitt pro Call: 0.00$", font=("Arial", 9), bg="#f0f0f0")
        self.avg_profit_label.grid(row=1, column=1, padx=5, pady=2, sticky="nsew")
        
        # Widget 6: Aktueller Kontostand
        self.current_balance_label = tk.Label(stats_frame, text="Kontostand: 500.00$", font=("Arial", 9), bg="#f0f0f0")
        self.current_balance_label.grid(row=1, column=2, padx=5, pady=2, sticky="nsew")
    # Platzhalter für Methoden, die später implementiert werden
    def fetch_data(self):
        """Daten vom API abrufen und anzeigen"""
        # Diese Methode wird später implementiert
        pass

    def paste_and_fetch(self):
        """Clipboard-Inhalt einfügen und Daten abrufen"""
        # Diese Methode wird später implementiert
        pass

    def reset_budget(self):
        """Kontostand zurücksetzen"""
        # Diese Methode wird später implementiert
        pass

    def toggle_live_update(self):
        """Live-Update ein-/ausschalten"""
        # Diese Methode wird später implementiert
        pass