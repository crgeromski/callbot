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
        """Erstellt den Frame für Statistiken"""
        self.frame = tk.Frame(
            self.parent, 
            bg="white", 
            padx=20, 
            pady=20,
            bd=1,
            relief="solid",
            highlightbackground="#cccccc",
            highlightthickness=1
        )
        
        self.frame.grid(row=0, column=1, sticky="nsew")
        
        self.inner = tk.Frame(self.frame, bg="white")
        self.inner.pack(fill="both", expand=True)
        
        # Titel hinzufügen
        title_label = tk.Label(
            self.inner, 
            text="Statistiken", 
            font=("Arial", 11, "bold"), 
            bg="white", 
            anchor="w"
        )
        title_label.pack(anchor="w", pady=(0,10))
        
        # Erster Untercontainer für Statistikdaten
        stats_data_container = tk.Frame(self.inner, bg="white", bd=1, relief="solid")
        stats_data_container.pack(fill="x", pady=(0,10))
        
        # Datenzeilen in den ersten Container
        styles.create_data_row(stats_data_container, "Market Cap", self.shared_vars['mcap_var'], 1)
        styles.create_data_row(stats_data_container, "Liquidity (USD)", self.shared_vars['liq_var'], 2)
        styles.create_data_row(stats_data_container, "24h Volumen", self.shared_vars['vol24_var'], 3)
        
        # Zweiter Untercontainer für Timeframes
        timeframes_container = tk.Frame(self.inner, bg="white", bd=1, relief="solid")
        timeframes_container.pack(fill="x")

        # Timeframes-Frame erstellen
        self.timeframes_frame = tk.Frame(timeframes_container, bg="white")

        # Rest des Codes bleibt gleich
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
            
            # Preis-Änderung
            pc_var = tk.StringVar(self.parent.winfo_toplevel())
            e_pc = tk.Entry(col_frame, textvariable=pc_var, width=7, state="readonly")
            e_pc.pack(pady=1)
            
            # Buys/Sells Labels
            bs_label_frame = tk.Frame(col_frame, bg="white")
            bs_label_frame.pack(pady=1)
            
            tk.Label(bs_label_frame, text="Buys", font=("Arial", 8), bg="white").pack(side="left", padx=(0,5))
            tk.Label(bs_label_frame, text="Sells", font=("Arial", 8), bg="white").pack(side="left", padx=(5,0))
            
            # Buys/Sells Entries
            bs_entry_frame = tk.Frame(col_frame, bg="white")
            bs_entry_frame.pack(pady=1)
            
            buys_var = tk.StringVar(self.parent.winfo_toplevel())
            e_buys = tk.Entry(bs_entry_frame, textvariable=buys_var, width=7, state="readonly", bg="white")
            e_buys.pack(side="left", padx=2)
            
            sells_var = tk.StringVar(self.parent.winfo_toplevel())
            e_sells = tk.Entry(bs_entry_frame, textvariable=sells_var, width=7, state="readonly", bg="white")
            e_sells.pack(side="left", padx=2)
            
            self.time_price_vars.append(pc_var)
            self.time_buys_vars.append((buys_var, e_buys))
            self.time_sells_vars.append((sells_var, e_sells))
        
        # Timeframes-Frame packen
        self.timeframes_frame.pack(pady=10, anchor="w")
    
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