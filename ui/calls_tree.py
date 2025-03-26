# Calls TreeView
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import data.storage as storage
from utils.formatters import parse_km

class CallsTreeView:
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.create_treeview()
        
    def create_treeview(self):
        """Erstellt den TreeView für aktive Calls"""
        # Erstelle eine Treeview mit den gewünschten Spalten
        self.calls_tree = ttk.Treeview(
            self.parent,
            columns=(
                "Datum",
                "Symbol",
                "MCAP_at_Call",
                "Liquidity_at_Call",
                "Aktuelles_MCAP",
                "Live_Liquidity",
                "X_Factor",
                "PL_Percent",
                "PL_Dollar",
                "Invest",
                "Link"
            ),
            show="headings"
        )
        
        # Definiere die Spaltenüberschriften
        self.calls_tree.heading("Datum", text="Datum")
        self.calls_tree.heading("Symbol", text="Symbol")
        self.calls_tree.heading("MCAP_at_Call", text="MCAP at Call")
        self.calls_tree.heading("Liquidity_at_Call", text="Liquidity at Call")
        self.calls_tree.heading("Aktuelles_MCAP", text="Live MCAP")
        self.calls_tree.heading("Live_Liquidity", text="Live Liquidity")
        self.calls_tree.heading("X_Factor", text="X-Factor")
        self.calls_tree.heading("PL_Percent", text="% P/L")
        self.calls_tree.heading("PL_Dollar", text="$ P/L")
        self.calls_tree.heading("Invest", text="Invest")
        self.calls_tree.heading("Link", text="Link")
        
        # Definiere die Zeilen-Farbtags für positives/negatives P/L
        self.calls_tree.tag_configure("row_green", background="#d8ffd8")
        self.calls_tree.tag_configure("row_red", background="#ffd8d8")
        
        # Definiere die Spaltenbreiten und Ausrichtung
        self.calls_tree.column("Datum", width=80, anchor="center")
        self.calls_tree.column("Symbol", width=80, anchor="center")
        self.calls_tree.column("MCAP_at_Call", width=100, anchor="center")
        self.calls_tree.column("Liquidity_at_Call", width=120, anchor="center")
        self.calls_tree.column("Aktuelles_MCAP", width=100, anchor="center")
        self.calls_tree.column("Live_Liquidity", width=120, anchor="center")
        self.calls_tree.column("X_Factor", width=80, anchor="center")
        self.calls_tree.column("PL_Percent", width=80, anchor="center")
        self.calls_tree.column("PL_Dollar", width=80, anchor="center")
        self.calls_tree.column("Invest", width=80, anchor="center")
        self.calls_tree.column("Link", width=150, anchor="center")
        
        # Packe den Treeview in den Tab
        self.calls_tree.pack(fill="both", expand=True)
        
        # Binde das Doppelklick-Event an die Treeview
        self.calls_tree.bind("<Double-1>", self.on_treeview_double_click)
        
        # Hinzufügen von Schaltflächen für Verwaltungsaktionen
        self.btn_frame = tk.Frame(self.parent)
        self.btn_frame.pack(pady=10)
        
        self.delete_button = tk.Button(self.btn_frame, text="Call löschen", command=self.delete_selected_call)
        self.delete_button.pack(side='left', padx=5)
        
        self.close_button = tk.Button(self.btn_frame, text="Call abschließen", command=self.close_selected_call)
        self.close_button.pack(side='left', padx=5)
    
    def update_tree(self):
        """Aktualisiert den Treeview im 'Meine Calls'-Tab mit den gespeicherten Calls."""
        self.calls_tree.delete(*self.calls_tree.get_children())
        
        for call in storage.load_call_data():
            # Überspringe abgeschlossene Calls
            if call.get("abgeschlossen", False):
                continue
                
            # Versuche, die Zahlenwerte aus dem Call zu holen
            try:
                x_factor_str = call.get("X_Factor") or "0"
                pl_dollar_str = call.get("PL_Dollar") or "0"
                # Entferne das "X" und "$", damit wir float-Werte haben
                x_factor_val = float(x_factor_str.rstrip("X"))
                pl_dollar_val = float(pl_dollar_str.rstrip("$"))
            except:
                x_factor_val = 0
                pl_dollar_val = 0
                
            # Standard-Tag (keine Färbung)
            row_tag = ""
                
            # 1) Falls X-Faktor >= 5 => ganze Zeile hellgrün
            if x_factor_val >= 5:
                row_tag = "row_green"
            # 2) Sonst, falls $ P/L >= 0 => ganze Zeile hellgrün
            elif pl_dollar_val >= 0:
                row_tag = "row_green"
            # 3) Sonst, falls $ P/L < 0 => ganze Zeile hellrot
            else:
                row_tag = "row_red"
                
            # Einfügen der Werte in den Treeview
            self.calls_tree.insert(
                "",
                "end",
                values=(
                    call.get("Datum", ""),
                    call.get("Symbol", ""),
                    call.get("MCAP_at_Call", ""),
                    call.get("Liquidity_at_Call", ""),
                    call.get("Aktuelles_MCAP", ""),
                    call.get("Live_Liquidity", ""),
                    call.get("X_Factor", ""),
                    call.get("PL_Percent", ""),
                    call.get("PL_Dollar", ""),
                    call.get("Invest", ""),
                    call.get("Link", "")
                ),
                tags=(row_tag,)
            )
    
    def on_treeview_double_click(self, event):
        """Reagiert auf Doppelklick in der Treeview"""
        item = self.calls_tree.identify_row(event.y)
        column = self.calls_tree.identify_column(event.x)
        if item:
            values = self.calls_tree.item(item, "values")
            link = values[10]  # Link-Spalte (11. Spalte)
            if column == "#11":
                if link:
                    webbrowser.open(link)
            else:
                # Neuladen des Calls im Main Bot:
                self.main_window.shared_vars['entry_var'].set(link)
                self.main_window.fetch_data()
                self.main_window.notebook.select(self.main_window.tabs['main'])
    
    def delete_selected_call(self):
        """Löscht die ausgewählten Calls aus der Liste"""
        selected_items = self.calls_tree.selection()
        if not selected_items:
            messagebox.showinfo("Hinweis", "Bitte wähle zuerst mindestens einen Call aus, den du löschen möchtest.")
            return
            
        # Sammle alle Links der ausgewählten Zeilen (Spalte 11, Index 10)
        selected_links = [self.calls_tree.item(item, "values")[10] for item in selected_items]
            
        # Lade die vorhandenen Calls
        calls = storage.load_call_data()
            
        # Filtere alle Calls heraus, deren Link in den ausgewählten Links enthalten ist
        updated_calls = [call for call in calls if call.get("Link") not in selected_links]
            
        # Speichere die aktualisierte Liste in der JSON-Datei
        storage.save_call_data(updated_calls)
            
        # Aktualisiere den Treeview
        self.update_tree()
    
    def close_selected_call(self):
        """Schließt die ausgewählten Calls ab"""
        selected_items = self.calls_tree.selection()
        if not selected_items:
            messagebox.showinfo("Hinweis", "Bitte wähle zuerst mindestens einen Call aus, den du abschließen möchtest.")
            return
            
        # Sammle alle Links der ausgewählten Zeilen (Spalte 11, Index 10)
        selected_links = [self.calls_tree.item(item, "values")[10] for item in selected_items]
            
        # Lade die vorhandenen Calls
        calls = storage.load_call_data()
            
        # Aktualisiere alle Calls, die in den ausgewählten Links enthalten sind:
        # - Setze "abgeschlossen" auf True
        # - Die finalen Live-Daten bleiben so, wie sie aktuell sind (z.B. "Aktuelles_MCAP" etc.)
        total_profit = 0
        for call in calls:
            if call.get("Link") in selected_links and not call.get("abgeschlossen", False):
                try:
                    profit = float(call.get("PL_Dollar", "0").rstrip("$"))
                except Exception:
                    profit = 0.0
                total_profit += profit
                call["abgeschlossen"] = True
            
        # Aktualisiere das Budget
        current_budget = storage.load_budget()
        new_budget = current_budget + total_profit
        storage.save_budget(new_budget)
            
        # Speichere die aktualisierte Liste in der JSON-Datei
        storage.save_call_data(calls)
            
        # Aktualisiere das UI
        self.update_tree()
        if hasattr(self.main_window, 'update_archived_calls_tree'):
            self.main_window.update_archived_calls_tree()
            
        # Aktualisiere Budget-Anzeige
        self.main_window.current_balance_label.config(text=f"Kontostand: {new_budget:.2f}$")
        if new_budget > 500:
            self.main_window.current_balance_label.config(bg="#d8ffd8")
        elif new_budget < 500:
            self.main_window.current_balance_label.config(bg="#ffd8d8")
        else:
            self.main_window.current_balance_label.config(bg="white")