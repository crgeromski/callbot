# Archivierte Calls TreeView
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import data.storage as storage

class ArchivedCallsTreeView:
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.create_treeview()
        
    def create_treeview(self):
        """Erstellt den TreeView für archivierte Calls"""
        # Erstelle den Treeview für archivierte Calls
        self.archived_calls_tree = ttk.Treeview(
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
        self.archived_calls_tree.heading("Datum", text="Datum")
        self.archived_calls_tree.heading("Symbol", text="Symbol")
        self.archived_calls_tree.heading("MCAP_at_Call", text="MCAP at Call")
        self.archived_calls_tree.heading("Liquidity_at_Call", text="Liquidity at Call")
        self.archived_calls_tree.heading("Aktuelles_MCAP", text="Live MCAP")
        self.archived_calls_tree.heading("Live_Liquidity", text="Live Liquidity")
        self.archived_calls_tree.heading("X_Factor", text="X-Factor")
        self.archived_calls_tree.heading("PL_Percent", text="% P/L")
        self.archived_calls_tree.heading("PL_Dollar", text="$ P/L")
        self.archived_calls_tree.heading("Invest", text="Invest")
        self.archived_calls_tree.heading("Link", text="Link")
        
        # Definiere Zeilen-Farbtags
        self.archived_calls_tree.tag_configure("row_green", background="#d8ffd8")
        self.archived_calls_tree.tag_configure("row_red", background="#ffd8d8")
        
        # Definiere die Spaltenbreiten und Ausrichtung
        self.archived_calls_tree.column("Datum", width=80, anchor="center")
        self.archived_calls_tree.column("Symbol", width=80, anchor="center")
        self.archived_calls_tree.column("MCAP_at_Call", width=100, anchor="center")
        self.archived_calls_tree.column("Liquidity_at_Call", width=120, anchor="center")
        self.archived_calls_tree.column("Aktuelles_MCAP", width=100, anchor="center")
        self.archived_calls_tree.column("Live_Liquidity", width=120, anchor="center")
        self.archived_calls_tree.column("X_Factor", width=80, anchor="center")
        self.archived_calls_tree.column("PL_Percent", width=80, anchor="center")
        self.archived_calls_tree.column("PL_Dollar", width=80, anchor="center")
        self.archived_calls_tree.column("Invest", width=80, anchor="center")
        self.archived_calls_tree.column("Link", width=150, anchor="center")
        
        # Lösch-Button
        self.delete_button = tk.Button(self.parent, text="Call löschen", command=self.delete_selected_archived_call)
        self.delete_button.pack(pady=10)
        
        # Doppelklick-Event
        self.archived_calls_tree.bind("<Double-1>", self.on_archived_double_click)
        self.archived_calls_tree.pack(fill="both", expand=True)
        
    def update_tree(self):
        """Aktualisiert den Treeview für archivierte Calls"""
        self.archived_calls_tree.delete(*self.archived_calls_tree.get_children())
        
        for call in storage.load_call_data():
            # Nur abgeschlossene Calls anzeigen
            if not call.get("abgeschlossen", False):
                continue
                
            try:
                x_factor_str = call.get("X_Factor", "0")
                pl_dollar_str = call.get("PL_Dollar", "0")
                # Entferne das "X" bzw. "$", um float-Werte zu erhalten
                x_factor_val = float(x_factor_str.rstrip("X"))
                pl_dollar_val = float(pl_dollar_str.rstrip("$"))
            except Exception:
                x_factor_val = 0
                pl_dollar_val = 0
                
            # Wähle die Zeilenfarbe
            if x_factor_val >= 5:
                row_tag = "row_green"
            elif pl_dollar_val >= 0:
                row_tag = "row_green"
            else:
                row_tag = "row_red"
                
            self.archived_calls_tree.insert(
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
            
    def on_archived_double_click(self, event):
        """Reagiert auf Doppelklick in der Treeview für archivierte Calls"""
        item = self.archived_calls_tree.identify_row(event.y)
        column = self.archived_calls_tree.identify_column(event.x)
        if item:
            values = self.archived_calls_tree.item(item, "values")
            link = values[10]  # Link-Spalte (11. Spalte)
            if column == "#11":
                if link:
                    webbrowser.open(link)
            else:
                # Neuladen des Calls im Main Bot:
                self.main_window.shared_vars['entry_var'].set(link)
                self.main_window.fetch_data()
                self.main_window.notebook.select(self.main_window.tabs['main'])
                
    def delete_selected_archived_call(self):
        """Löscht die ausgewählten Calls aus der Liste der abgeschlossenen Calls."""
        selected_items = self.archived_calls_tree.selection()
        if not selected_items:
            messagebox.showinfo("Hinweis", "Bitte wähle zuerst mindestens einen Call aus, den du löschen möchtest.")
            return
            
        # Sammle alle Links der ausgewählten Zeilen (Spalte 11, Index 10)
        selected_links = [self.archived_calls_tree.item(item, "values")[10] for item in selected_items]
            
        # Lade die vorhandenen Calls
        calls = storage.load_call_data()
            
        # Filtere alle Calls heraus, deren Link in den ausgewählten Links enthalten ist und die abgeschlossen sind
        updated_calls = [call for call in calls if not (call.get("abgeschlossen", False) and call.get("Link") in selected_links)]
            
        # Speichere die aktualisierte Liste in der JSON-Datei
        storage.save_call_data(updated_calls)
            
        # Aktualisiere den Treeview
        self.update_tree()