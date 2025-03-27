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
                "Aktuelles_MCAP",
                "X_Factor",
                "PL_Percent",
                "PL_Dollar",
                "Invest"
            ),
            show="headings"
        )
        
        # Definiere die Spaltenüberschriften
        self.archived_calls_tree.heading("Datum", text="Datum")
        self.archived_calls_tree.heading("Symbol", text="Symbol")
        self.archived_calls_tree.heading("MCAP_at_Call", text="MCAP at Call")
        self.archived_calls_tree.heading("Aktuelles_MCAP", text="Live MCAP")
        self.archived_calls_tree.heading("X_Factor", text="X-Factor")
        self.archived_calls_tree.heading("PL_Percent", text="% P/L")
        self.archived_calls_tree.heading("PL_Dollar", text="$ P/L")
        self.archived_calls_tree.heading("Invest", text="Invest")
        
        # Definiere Zeilen-Farbtags
        self.archived_calls_tree.tag_configure("row_green", background="#d8ffd8")
        self.archived_calls_tree.tag_configure("row_red", background="#ffd8d8")
        
        # Definiere die Spaltenbreiten und Ausrichtung
        self.archived_calls_tree.column("Datum", width=80, anchor="center")
        self.archived_calls_tree.column("Symbol", width=80, anchor="center")
        self.archived_calls_tree.column("MCAP_at_Call", width=100, anchor="center")
        self.archived_calls_tree.column("Aktuelles_MCAP", width=100, anchor="center")
        self.archived_calls_tree.column("X_Factor", width=80, anchor="center")
        self.archived_calls_tree.column("PL_Percent", width=80, anchor="center")
        self.archived_calls_tree.column("PL_Dollar", width=80, anchor="center")
        self.archived_calls_tree.column("Invest", width=80, anchor="center")
        
        # Doppelklick-Event
        self.archived_calls_tree.bind("<Double-1>", self.on_archived_double_click)
        self.archived_calls_tree.pack(fill="both", expand=True)
        
        # Kontextmenü hinzufügen
        self.context_menu = tk.Menu(self.archived_calls_tree, tearoff=0)
        self.archived_calls_tree.bind("<Button-3>", self.show_context_menu)
        
        # Einträge zum Kontextmenü hinzufügen
        self.context_menu.add_command(label="Call löschen", command=self.delete_selected_archived_call)
        
    def show_context_menu(self, event):
        """Zeigt das Kontextmenü bei Rechtsklick an"""
        # Wähle das Item unter dem Cursor
        item = self.archived_calls_tree.identify_row(event.y)
        if item:
            # Setze die Auswahl auf das Item unter dem Cursor
            self.archived_calls_tree.selection_set(item)
            # Zeige das Kontextmenü
            self.context_menu.post(event.x_root, event.y_root)
        
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
                    call.get("Aktuelles_MCAP", ""),
                    call.get("X_Factor", ""),
                    call.get("PL_Percent", ""),
                    call.get("PL_Dollar", ""),
                    call.get("Invest", "")
                ),
                tags=(row_tag,)
            )
            
    def on_archived_double_click(self, event):
        """Reagiert auf Doppelklick in der Treeview für archivierte Calls"""
        item = self.archived_calls_tree.identify_row(event.y)
        if item:
            # Hole alle Werte der ausgewählten Zeile
            values = self.archived_calls_tree.item(item, "values")
            
            # Suche nach dem Link für diesen Call
            calls = storage.load_call_data()
            matching_calls = [call for call in calls if 
                              call.get("Symbol") == values[1] and  # Symbol stimmt überein
                              call.get("Datum") == values[0] and  # Datum stimmt überein
                              call.get("abgeschlossen", False)]   # Nur abgeschlossene Calls
            
            if matching_calls and len(matching_calls) > 0:
                call = matching_calls[0]
                link = call.get("Link")
                
                if link:
                    # Setze den Link in die Entry-Variable
                    self.main_window.shared_vars['entry_var'].set(link)
                    
                    # Rufe Daten ab
                    self.main_window.fetch_data()
                    
                    # Wechsle zum Main Bot Tab
                    self.main_window.notebook.select(self.main_window.tabs['main'])
    

    def delete_selected_archived_call(self):
        """Löscht nur die ausgewählten archivierten Calls"""
        selected_items = self.archived_calls_tree.selection()
        if not selected_items:
            messagebox.showinfo("Hinweis", "Bitte wähle zuerst mindestens einen Call aus, den du löschen möchtest.")
            return
        
        # Lade vorhandene Calls
        calls = storage.load_call_data()
        new_calls = []
        
        # Details für jeden ausgewählten Call sammeln
        to_delete = []
        for item in selected_items:
            values = self.archived_calls_tree.item(item, "values")
            # Speichere Datum, Symbol UND MCAP als eindeutige Identifikation
            to_delete.append((values[0], values[1], values[2]))  # (Datum, Symbol, MCAP_at_Call)
            
        # Nur Calls behalten, die nicht gelöscht werden sollen
        for call in calls:
            # Überspringe nicht-abgeschlossene Calls
            if not call.get("abgeschlossen", False):
                new_calls.append(call)
                continue
                
            # Prüfe, ob dieser Call gelöscht werden soll
            current_call_id = (call.get("Datum", ""), call.get("Symbol", ""), call.get("MCAP_at_Call", ""))
            if current_call_id in to_delete:
                continue  # Diesen Call nicht behalten
            
            # Ansonsten Call behalten
            new_calls.append(call)
        
        # Speichern und aktualisieren
        storage.save_call_data(new_calls)
        self.update_tree()