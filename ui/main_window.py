# Hauptfenster
import tkinter as tk
from tkinter import ttk, messagebox
import ui.styles as styles
from config import DEFAULT_WINDOW_SIZE, DEFAULT_WINDOW_TITLE
import data.storage as storage

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
        # Globale Tastenkombination für Strg+V
        self.root.bind("<Control-v>", lambda e: self.paste_and_fetch())
        
        # Optional: Mindestgröße setzen
        self.root.minsize(630, 800)

    def create_dashboard(self):
        """Erstellt das Dashboard mit Eingabefeld und Widgets"""
        self.dashboard_frame = tk.Frame(self.root, bg="#cccccc")
        self.dashboard_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        
        # Container für Buttons und Eingabefeld mit vertikaler Zentrierung
        controls_container = tk.Frame(self.dashboard_frame, bg="#cccccc")
        controls_container.pack(fill="x")
        
        # Linke Seite - Eingabefeld mit Paste-Button
        left_section = tk.Frame(controls_container, bg="#cccccc")
        left_section.pack(side="left")
        
        # Eingabefeld erstellen mit fester Breite
        entry_frame = tk.Frame(left_section, bg="#cccccc")
        entry_frame.pack(side="left", padx=(0, 10))
        
        # Höhe auf Knopfhöhe setzen und vertikale Zentrierung
        entry = tk.Entry(entry_frame, textvariable=self.shared_vars['entry_var'], 
                        font=("Arial", 10), width=20, 
                        highlightthickness=1, bd=2)  # Angepasste Höhe durch Border
        entry.pack(side="left", fill="y")
        entry.bind("<Return>", lambda event: self.fetch_data())
        
        # Platzhaltertext hinzufügen
        entry.insert(0, "Link oder CA einfügen")
        entry.config(fg="#888888")
        
        # Event-Handler für Fokusgewinn und -verlust
        def on_entry_focus_in(event):
            if entry.get() == "Link oder CA einfügen":
                entry.delete(0, "end")
                entry.config(fg="black")

        def on_entry_focus_out(event):
            if not entry.get():
                entry.insert(0, "Link oder CA einfügen")
                entry.config(fg="#888888")

        entry.bind("<FocusIn>", on_entry_focus_in)
        entry.bind("<FocusOut>", on_entry_focus_out)
        
        # Paste-Button mit Icon
        def paste_from_clipboard():
            try:
                clipboard_content = self.root.clipboard_get()
                self.shared_vars['entry_var'].set(clipboard_content)
                self.fetch_data()
            except Exception as e:
                import tkinter.messagebox as messagebox
                messagebox.showerror("Fehler", f"Konnte Zwischenablage nicht verarbeiten: {e}")

        paste_btn = tk.Button(
            entry_frame, 
            text="📋", 
            width=2,
            height=1,  # Höhenanpassung
            command=paste_from_clipboard
        )
        paste_btn.pack(side="left", fill="y")
        
        # Rechte Seite - Button zum Zurücksetzen des Kontostands
        right_section = tk.Frame(controls_container, bg="#cccccc")
        right_section.pack(side="right")
        
        # Erstellen des Buttons mit Standardhöhe
        self.reset_budget_btn = tk.Button(right_section, text="Kontostand zurücksetzen", command=self.reset_budget)
        self.reset_budget_btn.pack(side="right")
        
        # Nach dem Erstellen des Reset-Buttons:
        # Hole die Höhe des Reset-Buttons für bessere Abstimmung
        self.dashboard_frame.update_idletasks()  # Aktualisiere Layout
        button_height = self.reset_budget_btn.winfo_height()
        
        # Setze eine minimale Höhe für den Container, um vertikale Zentrierung zu gewährleisten
        controls_container.configure(height=button_height)
        left_section.configure(height=button_height)
        right_section.configure(height=button_height)
        

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
        
        # Container 1: Oberer Bereich 
        container_top = tk.Frame(self.tab1, bg="white")
        container_top.pack(fill="x", padx=10, pady=5)
        
        # Container-Konfiguration für volle Breite
        container_top.columnconfigure(0, weight=1)
        
        # Token-Daten auf volle Breite
        self.top_left = tk.Frame(container_top, bg="white", bd=1, relief="solid")
        self.top_left.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        
        # Container 2: Mittlerer Bereich (50% / 50%)
        container_middle = tk.Frame(self.tab1, bg="white")
        container_middle.pack(fill="x", padx=10, pady=5)

        # Container 2 in zwei Teile aufteilen - mit fester Größe
        container_middle.columnconfigure(0, minsize=300, weight=1)  # 50% Breite, mindestens 300px
        container_middle.columnconfigure(1, minsize=300, weight=1)  # 50% Breite, mindestens 300px

        # Linker Teil (Statistiken)
        self.middle_left = tk.Frame(container_middle, bg="white", bd=1, relief="solid", width=300)
        self.middle_left.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        # Rechter Teil (Social Media)
        self.middle_right = tk.Frame(container_middle, bg="white", bd=1, relief="solid", width=300)
        self.middle_right.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        # Container 3: Unterer Bereich (50% / 50%)
        container_bottom = tk.Frame(self.tab1, bg="white")
        container_bottom.pack(fill="x", padx=10, pady=5)
        
        # Container 3 in zwei Teile aufteilen
        container_bottom.columnconfigure(0, weight=1)  # 50% Breite
        container_bottom.columnconfigure(1, weight=1)  # 50% Breite
        
        # Linker Teil (X-Post)
        from ui.xpost_frame import XPostFrame
        self.bottom_left = tk.Frame(container_bottom, bg="white", bd=1, relief="solid")
        self.bottom_left.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        xpost_frame = XPostFrame(self.bottom_left, self.shared_vars)
        
        # Rechter Teil (Empfehlung - zukünftig)
        self.bottom_right = tk.Frame(container_bottom, bg="white", bd=1, relief="solid")
        self.bottom_right.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        # Speichere die Container im Dictionary für späteren Zugriff
        self.main_containers = {
            'top_left': self.top_left,
            'middle_left': self.middle_left,
            'middle_right': self.middle_right,
            'bottom_left': self.bottom_left,
            'bottom_right': self.bottom_right
        }
        
        # Platzhalter für die zukünftigen Funktionen
        self.create_placeholders()

    def create_placeholders(self):
        """Erstellt Platzhalter für zukünftige Funktionen"""
        # X-Post Frame
        xpost_frame = tk.Frame(self.bottom_left, bg="white", padx=20, pady=20)
        xpost_frame.grid(row=0, column=0, sticky="nsew")  # Verwenden Sie grid statt pack
        
        tk.Label(
            xpost_frame, 
            text="X-Post", 
            font=("Arial", 11, "bold"), 
            bg="white", 
            anchor="w"
        ).pack(anchor="w")

        # Optional: Empfehlung Platzhalter
        rec_frame = tk.Frame(self.bottom_right, bg="white", padx=20, pady=20)
        rec_frame.grid(row=0, column=0, sticky="nsew")  # Auch hier grid
        
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
        entry = tk.Entry(self.profit_container, justify="center", font=("Arial", 9, "bold"))
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
        """Setzt den Kontostand auf 500$ zurück und löscht alle Calls."""
        # Zeige ein Bestätigungsdialog
        confirm = messagebox.askyesno(
            "Kontostand und Calls zurücksetzen",
            "Möchtest du den Kontostand wirklich auf 500$ zurücksetzen und ALLE Calls löschen?\nDiese Aktion kann nicht rückgängig gemacht werden.",
            icon="warning"
        )
        
        if confirm:
            # Kontostand zurücksetzen
            storage.save_budget(500.0)
            
            # Alle Calls löschen (leere Liste speichern)
            storage.save_call_data([])
            
            # Aktualisiere das Label
            self.current_balance_label.config(text=f"Kontostand: 500.00$", bg="white")
            
            # Aktualisiere die Treeviews
            if hasattr(self, 'calls_tree'):
                self.calls_tree.update_tree()
            if hasattr(self, 'archived_calls_tree'):
                self.archived_calls_tree.update_tree()
                
            messagebox.showinfo("Erfolg", "Der Kontostand wurde auf 500$ zurückgesetzt und alle Calls wurden gelöscht.")

    def toggle_live_update(self):
        """Live-Update ein-/ausschalten"""
        # Diese Methode wird später implementiert
        pass