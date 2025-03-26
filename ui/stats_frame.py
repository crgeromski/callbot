# Statistiken-Frame
import tkinter as tk
import ui.styles as styles

class StatsFrame:
    def __init__(self, parent, shared_vars, time_price_vars, time_buys_vars, time_sells_vars):
        self.parent = parent
        self.shared_vars = shared_vars
        self.time_price_vars = time_price_vars
        self.time_buys_vars = time_buys_vars
        self.time_sells_vars = time_sells_vars
        self.create_frame()
        
    def create_frame(self):
        """Erstellt den Frame für Statistik-Daten"""
        self.frame = tk.Frame(
            self.parent, 
            bg="white", 
            padx=20, 
            pady=20
        )
        self.frame.pack(fill="both", expand=True)
        
        # Titel hinzufügen
        title_label = tk.Label(
            self.frame, 
            text="Statistiken", 
            font=("Arial", 11, "bold"), 
            bg="white", 
            anchor="w"
        )
        title_label.pack(anchor="w", pady=(0,10))
        
        # Erster Untercontainer für Statistikdaten
        stats_data_container = tk.Frame(self.frame, bg="white")
        stats_data_container.pack(fill="x", pady=(0,10))
        stats_data_container.columnconfigure(1, weight=1)  # Die Spalte mit den Entry-Feldern soll sich ausdehnen
        
        # Datenzeilen in den ersten Container
        styles.create_data_row(stats_data_container, "Market Cap", self.shared_vars['mcap_var'], 1, show_copy_button=False)
        styles.create_data_row(stats_data_container, "Liquidity (USD)", self.shared_vars['liq_var'], 2, show_copy_button=False)
        styles.create_data_row(stats_data_container, "24h Volumen", self.shared_vars['vol24_var'], 3, show_copy_button=False)
        
        # Zweiter Untercontainer für Timeframes
        timeframes_container = tk.Frame(self.frame, bg="white")
        timeframes_container.pack(fill="x")

        # Timeframes-Frame erstellen
        self.timeframes_frame = tk.Frame(timeframes_container, bg="white")
        # Konfiguriere die Spalten für gleichmäßige Verteilung
        for i in range(4):  # Für die 4 Zeitrahmen (5M, 1H, 6H, 24H)
            self.timeframes_frame.columnconfigure(i, weight=1)

        # Timeframes-Titel
        tk.Label(
            timeframes_container,
            text="Preisänderungen & Transaktionen",
            font=("Arial", 10, "bold"),
            bg="white",
            anchor="w"
        ).pack(anchor="w", padx=10, pady=(10,5))
        
        for i, label_text in enumerate(["5M", "1H", "6H", "24H"]):
            # Label für jeden Timeframe
            tk.Label(
                self.timeframes_frame, 
                text=label_text, 
                font=("Arial", 10, "bold"), 
                bg="white"
            ).grid(row=0, column=i, padx=10)
            
            # Frame für jede Spalte
            col_frame = tk.Frame(self.timeframes_frame, bg="white")
            col_frame.grid(row=1, column=i, padx=10, pady=2)
            
            # Verwenden Sie grid statt pack für konsistentere Ausrichtung
            pc_var = tk.StringVar(self.parent.winfo_toplevel())
            e_pc = tk.Entry(col_frame, textvariable=pc_var, state="readonly", justify="center")
            e_pc.grid(row=0, column=0, pady=1, padx=2, sticky="ew")
            col_frame.columnconfigure(0, weight=1)
            
            bs_label_frame = tk.Frame(col_frame, bg="white")
            bs_label_frame.grid(row=1, column=0, pady=1)
            
            tk.Label(bs_label_frame, text="B", font=("Arial", 8, "bold"), bg="white").pack(side="left", padx=(0,5))
            tk.Label(bs_label_frame, text="S", font=("Arial", 8, "bold"), bg="white").pack(side="left", padx=(5,0))
            
            bs_entry_frame = tk.Frame(col_frame, bg="white")
            bs_entry_frame.grid(row=2, column=0, pady=1, sticky="ew")
            # Konfiguriere die Spalten für gleichmäßige Aufteilung
            bs_entry_frame.columnconfigure(0, weight=1, uniform="bs_entries")
            bs_entry_frame.columnconfigure(1, weight=1, uniform="bs_entries")

            buys_var = tk.StringVar(self.parent.winfo_toplevel())
            e_buys = tk.Entry(bs_entry_frame, textvariable=buys_var, state="readonly", bg="white", justify="center", width=8)
            e_buys.grid(row=0, column=0, padx=2, sticky="ew")

            sells_var = tk.StringVar(self.parent.winfo_toplevel())
            e_sells = tk.Entry(bs_entry_frame, textvariable=sells_var, state="readonly", bg="white", justify="center", width=8) 
            e_sells.grid(row=0, column=1, padx=2, sticky="ew")
            
            self.time_price_vars.append((pc_var, e_pc)) 
            self.time_buys_vars.append((buys_var, e_buys))
            self.time_sells_vars.append((sells_var, e_sells))
        
        # Timeframes-Frame packen
        self.timeframes_frame.pack(pady=10, fill="x")
    
    def color_buys_sells_entries(self, buys_entry, sells_entry, buys_str, sells_str):
        """Hintergrund einfärben: Grün wenn Buys > Sells, Rot wenn Sells > Buys."""
        buys_entry.config(readonlybackground="white")
        sells_entry.config(readonlybackground="white")
        try:
            b_val = float(buys_str)
            s_val = float(sells_str)
            if b_val > s_val:
                buys_entry.config(readonlybackground="#d8ffd8")
            elif s_val > b_val:
                sells_entry.config(readonlybackground="#ffd8d8")
        except:
            pass

    def color_price_change_entry(self, entry, value_str):
        """Hintergrund einfärben: Grün wenn positiv, Rot wenn negativ."""
        entry.config(readonlybackground="white")
        try:
            value = float(value_str.rstrip("%"))
            if value > 0:
                entry.config(readonlybackground="#d8ffd8")
            elif value < 0:
                entry.config(readonlybackground="#ffd8d8")
        except:
            pass