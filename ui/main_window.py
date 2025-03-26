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
        self.create_notebook()
        self.create_header()
        self.create_profit_container()

    def setup_window(self):
        """Grundlegende Fenstereinstellungen"""
        self.root.title(DEFAULT_WINDOW_TITLE)
        self.root.geometry(DEFAULT_WINDOW_SIZE)
        self.root.resizable(False, False)
        self.root.configure(bg="#cccccc")
        # Styles einrichten
        styles.setup_styles()

    def create_header(self):
        """Erstellt den Header-Bereich mit Eingabefeld"""
        self.header_frame = tk.Frame(self.root, bg="#cccccc")
        self.header_frame.pack(side="top", fill="x", padx=25, pady=25)

        lbl_header = tk.Label(self.header_frame, text="Dexscreener Link", bg="#cccccc", font=("Arial", 10, "bold"))
        lbl_header.pack(anchor="w")

        self.entry = tk.Entry(self.header_frame, textvariable=self.shared_vars['entry_var'], width=50)
        self.entry.pack(anchor="w", pady=(5,0))
        self.entry.bind("<Return>", lambda event: self.fetch_data())

        self.paste_button = tk.Button(self.header_frame, text="Zwischenablage einfügen", command=self.paste_and_fetch)
        self.paste_button.pack(anchor="w", pady=(5,0))

        # Button zum Zurücksetzen des Kontostands
        self.reset_budget_btn = tk.Button(self.header_frame, text="Kontostand zurücksetzen", command=self.reset_budget)
        self.reset_budget_btn.pack(side="right", padx=(10, 0))

        # Live Update Button
        self.live_update_btn = tk.Button(self.header_frame, text="Live Update AN", command=self.toggle_live_update, bg="#d8ffd8")
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
        self.tab1.grid_columnconfigure(0, weight=1)  # Linke Spalte
        self.tab1.grid_columnconfigure(1, weight=1)  # Rechte Spalte
        
        self.notebook.add(self.tab1, text="Main Bot")
        self.notebook.add(self.tab2, text="Meine Calls")
        self.notebook.add(self.tab3, text="Abgeschlossene Calls")
        
        # Speichere Tabs im Dictionary für Zugriff aus anderen Modulen
        self.tabs['main'] = self.tab1
        self.tabs['calls'] = self.tab2
        self.tabs['archived'] = self.tab3

    def create_profit_container(self):
        """Erstellt den Container für Gewinnberechnung"""
        self.profit_container = tk.Frame(self.root, bg="white", bd=1, relief="groove", height=300, padx=15, pady=15)
        self.profit_container.pack(fill="both", padx=25, pady=(0,10))
        self.profit_container.pack_propagate(False)  # Verhindert, dass sich der Container an den Inhalt anpasst

        # Konfiguriere das Grid für 2 Reihen und 3 Spalten
        for i in range(2):
            self.profit_container.grid_rowconfigure(i, weight=1)
        for j in range(3):
            self.profit_container.grid_columnconfigure(j, weight=1)

        # Widget 1: Gesamtinvestition
        self.total_invest_label = tk.Label(self.profit_container, text="Investiert: 0.00$", font=("Arial", 10, "bold"), bg="#f0f0f0")
        self.total_invest_label.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Widget 2: Anzahl der Calls
        self.num_calls_label = tk.Label(self.profit_container, text="Calls: 0", font=("Arial", 10, "bold"), bg="#f0f0f0")
        self.num_calls_label.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        # Widget 3: Gesamt Gewinn/Verlust (absolut)
        self.total_profit_label = tk.Label(self.profit_container, text="Gesamt Gewinn/Verlust: 0.00$", font=("Arial", 10, "bold"), bg="#f0f0f0")
        self.total_profit_label.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

        # Widget 4: Gewinn/Verlust in Prozent
        self.profit_percent_label = tk.Label(self.profit_container, text="Gewinn/Verlust (%): 0.00%", font=("Arial", 10, "bold"), bg="#f0f0f0")
        self.profit_percent_label.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        # Widget 5: Durchschnittlicher Gewinn/Verlust pro Call
        self.avg_profit_label = tk.Label(self.profit_container, text="Durchschnitt pro Call: 0.00$", font=("Arial", 10, "bold"), bg="#f0f0f0")
        self.avg_profit_label.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

        # Widget 6: Aktueller Kontostand
        self.current_balance_label = tk.Label(self.profit_container, text="Kontostand: 500.00$", font=("Arial", 10, "bold"), bg="#f0f0f0")
        self.current_balance_label.grid(row=1, column=2, padx=5, pady=5, sticky="nsew")

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