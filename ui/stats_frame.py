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
            padx=10, 
            pady=10, 
            bd=1, 
            relief="solid"
        )
        self.frame.grid(row=1, column=0, sticky="nsew")
        
        self.inner = tk.Frame(self.frame, bg="white")
        self.inner.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Titel
        tk.Label(
            self.inner, 
            text="Statistiken", 
            font=("Arial", 11, "bold"), 
            bg="white", 
            anchor="w"
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0,10))
        
        # Datenzeilen
        styles.create_data_row(self.inner, "Market Cap", self.shared_vars['mcap_var'], 1)
        styles.create_data_row(self.inner, "Liquidity (USD)", self.shared_vars['liq_var'], 2)
        styles.create_data_row(self.inner, "24h Volumen", self.shared_vars['vol24_var'], 3)
        
        # Timeframes-Frame
        self.timeframes_frame = tk.Frame(self.inner, bg="white")
        self.timeframes_frame.grid(row=4, column=0, columnspan=3, pady=10, sticky="n")
        self.timeframes_frame.grid_configure(padx=50)
        
        # Timeframe-Beschriftungen
        lbl_5m = tk.Label(self.timeframes_frame, text="5M", font=("Arial", 10, "bold"), bg="white")
        lbl_5m.grid(row=0, column=0, padx=10)
        lbl_1h = tk.Label(self.timeframes_frame, text="1H", font=("Arial", 10, "bold"), bg="white")
        lbl_1h.grid(row=0, column=1, padx=10)
        lbl_6h = tk.Label(self.timeframes_frame, text="6H", font=("Arial", 10, "bold"), bg="white")
        lbl_6h.grid(row=0, column=2, padx=10)
        lbl_24h = tk.Label(self.timeframes_frame, text="24H", font=("Arial", 10, "bold"), bg="white")
        lbl_24h.grid(row=0, column=3, padx=10)
        
        # Erstelle Entries für die Timeframes
        for i in range(4):
            pc_var = tk.StringVar(self.parent.winfo_toplevel())
            e_pc = tk.Entry(self.timeframes_frame, textvariable=pc_var, width=7, state="readonly")
            e_pc.grid(row=1, column=i, padx=2, pady=1)
            subf = tk.Frame(self.timeframes_frame, bg="white")
            subf.grid(row=2, column=i, padx=5, pady=1)
            lb_b = tk.Label(subf, text="Buys", font=("Arial", 8), bg="white")
            lb_b.grid(row=0, column=0, padx=(0,5), sticky="e")
            lb_s = tk.Label(subf, text="Sells", font=("Arial", 8), bg="white")
            lb_s.grid(row=0, column=1, padx=(5,0), sticky="w")
            buys_var = tk.StringVar(self.parent.winfo_toplevel())
            e_buys = tk.Entry(subf, textvariable=buys_var, width=7, state="readonly", bg="white")
            e_buys.grid(row=1, column=0, padx=2, pady=1)
            sells_var = tk.StringVar(self.parent.winfo_toplevel())
            e_sells = tk.Entry(subf, textvariable=sells_var, width=7, state="readonly", bg="white")
            e_sells.grid(row=1, column=1, padx=2, pady=1)
            self.time_price_vars.append(pc_var)
            self.time_buys_vars.append((buys_var, e_buys))
            self.time_sells_vars.append((sells_var, e_sells))
    
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