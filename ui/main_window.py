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
        # Container für die drei Hauptbereiche
        self.main_containers = {}
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
        right_column = tk.Frame(self.dashboard_frame, bg="#cccccc")
        right_column.grid(row=0, column=1, sticky="nsew")
        
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
        """Erstellt das Notebook mit Tabs und die drei Hauptcontainer im Main-Tab"""
        self.notebook_frame = tk.Frame(self.root)
        self.notebook_frame.pack(side="top", fill="both", expand=True)
        
        self.notebook = ttk.Notebook(self.notebook_frame)
        self.notebook.pack(fill="both", expand=True)

        # Erstelle die Tabs
        self.tab1 = tk.Frame(self.notebook, bg="white")
        self.tab2 = tk.Frame(self.notebook, bg="white")
        self.tab3 = tk.Frame(self.notebook, bg="white")
        
        # Füge die Tabs dem Notebook hinzu
        self.notebook.add(self.tab1, text="Main Bot")
        self.notebook.add(self.tab2, text="Meine Calls")
        self.notebook.add(self.tab3, text="Abgeschlossene Calls")
        
        # Speichere Tabs im Dictionary für Zugriff aus anderen Modulen
        self.tabs['main'] = self.tab1
        self.tabs['calls'] = self.tab2
        self.tabs['archived'] = self.tab3
        
        # Erstelle die drei Hauptcontainer im Main-Tab
        self.create_main_containers()

    def create_main_containers(self):
        """Erstellt die drei Hauptcontainer im Main-Tab"""
        # Main-Tab Konfiguration für vertikales Layout
        self.tab1.pack_propagate(False)
        
        # Container 1: Oberer Bereich (70% links / 30% rechts)
        container_top = tk.Frame(self.tab1, bg="white")
        container_top.pack(fill="x", padx=10, pady=5)
        
        # Container 1 in zwei Teile aufteilen
        container_top.columnconfigure(0, weight=7)  # 70% Breite
        container_top.columnconfigure(1, weight=3)  # 30% Breite
        
        # Linker Teil (Token-Daten)
        self.top_left = tk.Frame(container_top, bg="white", bd=1, relief="solid")
        self.top_left.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Rechter Teil (DexLink-Eingabe)
        self.top_right = tk.Frame(container_top, bg="white", bd=1, relief="solid")
        self.top_right.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        # Container 2: Mittlerer Bereich (50% / 50%)
        container_middle = tk.Frame(self.tab1, bg="white")
        container_middle.pack(fill="x", padx=10, pady=5)
        
        # Container 2 in zwei Teile aufteilen
        container_middle.columnconfigure(0, weight=1)  # 50% Breite
        container_middle.columnconfigure(1, weight=1)  # 50% Breite
        
        # Linker Teil (Statistiken)
        self.middle_left = tk.Frame(container_middle, bg="white", bd=1, relief="solid")
        self.middle_left.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Rechter Teil (Social Media)
        self.middle_right = tk.Frame(container_middle, bg="white", bd=1, relief="solid")
        self.middle_right.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        # Container 3: Unterer Bereich (50% / 50%)
        container_bottom = tk.Frame(self.tab1, bg="white")
        container_bottom.pack(fill="x", padx=10, pady=5)
        
        # Container 3 in zwei Teile aufteilen
        container_bottom.columnconfigure(0, weight=1)  # 50% Breite
        container_bottom.columnconfigure(1, weight=1)  # 50% Breite
        
        # Linker Teil (RugCheck - zukünftig)
        self.bottom_left = tk.Frame(container_bottom, bg="white", bd=1, relief="solid")
        self.bottom_left.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Rechter Teil (Empfehlung - zukünftig)
        self.bottom_right = tk.Frame(container_bottom, bg="white", bd=1, relief="solid")
        self.bottom_right.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        # Speichere die Container im Dictionary für späteren Zugriff
        self.main_containers = {
            'top_left': self.top_left,
            'top_right': self.top_right,
            'middle_left': self.middle_left,
            'middle_right': self.middle_right,
            'bottom_left': self.bottom_left,
            'bottom_right': self.bottom_right
        }
        
        # Platzhalter für die zukünftigen Funktionen
        self.create_placeholders()

    def create_placeholders(self):
        """Erstellt Platzhalter für zukünftige Funktionen"""
        # RugCheck Platzhalter
        rug_frame = tk.Frame(self.bottom_left, bg="white", padx=20, pady=20)
        rug_frame.pack(fill="both", expand=True)
        
        tk.Label(
            rug_frame, 
            text="RugCheck (kommt bald)", 
            font=("Arial", 11, "bold"), 
            bg="white"
        ).pack(anchor="w")
        
        # Empfehlung Platzhalter
        rec_frame = tk.Frame(self.bottom_right, bg="white", padx=20, pady=20)
        rec_frame.pack(fill="both", expand=True)
        
        tk.Label(
            rec_frame, 
            text="Empfehlung (kommt bald)", 
            font=("Arial", 11, "bold"), 
            bg="white"
        ).pack(anchor="w")

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