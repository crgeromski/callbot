# Calls TreeView
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import data.storage as storage

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
                "Aktuelles_MCAP",
                "X_Factor",
                "PL_Percent",
                "PL_Dollar",
                "Invest"
            ),
            show="headings"
        )
        
        # Definiere die Spaltenüberschriften
        self.calls_tree.heading("Datum", text="Datum")
        self.calls_tree.heading("Symbol", text="Symbol")
        self.calls_tree.heading("MCAP_at_Call", text="MCAP at Call")
        self.calls_tree.heading("Aktuelles_MCAP", text="Live MCAP")
        self.calls_tree.heading("X_Factor", text="X-Factor")
        self.calls_tree.heading("PL_Percent", text="% P/L")
        self.calls_tree.heading("PL_Dollar", text="$ P/L")
        self.calls_tree.heading("Invest", text="Invest")
        
        # Definiere die Spaltenbreiten und Ausrichtung
        self.calls_tree.column("Datum", width=80, anchor="center")
        self.calls_tree.column("Symbol", width=80, anchor="center")
        self.calls_tree.column("MCAP_at_Call", width=100, anchor="center")
        self.calls_tree.column("Aktuelles_MCAP", width=100, anchor="center")
        self.calls_tree.column("X_Factor", width=80, anchor="center")
        self.calls_tree.column("PL_Percent", width=80, anchor="center")
        self.calls_tree.column("PL_Dollar", width=80, anchor="center")
        self.calls_tree.column("Invest", width=80, anchor="center")

        # Definiere die Zeilen-Farbtags für positives/negatives P/L
        self.calls_tree.tag_configure("row_green", background="#d8ffd8")
        self.calls_tree.tag_configure("row_red", background="#ffd8d8")
        
        # Packe den Treeview in den Tab
        self.calls_tree.pack(fill="both", expand=True)
        
        # Binde das Doppelklick-Event an die Treeview
        self.calls_tree.bind("<Double-1>", self.on_treeview_double_click)
        
        # Kontextmenü hinzufügen
        self.context_menu = tk.Menu(self.calls_tree, tearoff=0)
        self.calls_tree.bind("<Button-3>", self.show_context_menu)
        
        # Einträge zum Kontextmenü hinzufügen
        self.context_menu.add_command(label="Call abschließen", command=self.close_selected_call)
        self.context_menu.add_command(label="Call löschen", command=self.delete_selected_call)
    
    def show_context_menu(self, event):
        """Zeigt das Kontextmenü bei Rechtsklick an"""
        # Wähle das Item unter dem Cursor
        item = self.calls_tree.identify_row(event.y)
        if item:
            # Setze die Auswahl auf das Item unter dem Cursor
            self.calls_tree.selection_set(item)
            # Zeige das Kontextmenü
            self.context_menu.post(event.x_root, event.y_root)
    
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
                    call.get("Aktuelles_MCAP", ""),
                    call.get("X_Factor", ""),
                    call.get("PL_Percent", ""),
                    call.get("PL_Dollar", ""),
                    call.get("Invest", "")
                ),
                tags=(row_tag,)
            )
    
    def on_treeview_double_click(self, event):
        """Reagiert auf Doppelklick in der Treeview"""
        item = self.calls_tree.identify_row(event.y)
        if item:
            # Hole alle Werte der ausgewählten Zeile
            values = self.calls_tree.item(item, "values")
            
            # Suche nach dem Link für diesen Call
            calls = storage.load_call_data()
            matching_calls = [call for call in calls if 
                              call.get("Symbol") == values[1] and  # Symbol stimmt überein
                              call.get("Datum") == values[0]]     # Datum stimmt überein
            
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
    
    # Nur die delete_selected_call Funktion, da nur diese geändert werden muss

    def delete_selected_call(self):
        """Löscht nur die ausgewählten Calls aus der Liste"""
        selected_items = self.calls_tree.selection()
        if not selected_items:
            messagebox.showinfo("Hinweis", "Bitte wähle zuerst mindestens einen Call aus, den du löschen möchtest.")
            return
        
        # Lade vorhandene Calls
        calls = storage.load_call_data()
        new_calls = []
        
        # Details für jeden ausgewählten Call sammeln
        to_delete = []
        for item in selected_items:
            values = self.calls_tree.item(item, "values")
            # Speichere Datum, Symbol UND MCAP als eindeutige Identifikation
            to_delete.append((values[0], values[1], values[2]))  # (Datum, Symbol, MCAP_at_Call)
            
        # Nur Calls behalten, die nicht gelöscht werden sollen
        for call in calls:
            # Überspringe abgeschlossene Calls
            if call.get("abgeschlossen", False):
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
    
    def close_selected_call(self):
        """Schließt die ausgewählten Calls ab"""
        selected_items = self.calls_tree.selection()
        if not selected_items:
            messagebox.showinfo("Hinweis", "Bitte wähle zuerst mindestens einen Call aus, den du abschließen möchtest.")
            return
            
        # Lade vorhandene Calls
        calls = storage.load_call_data()
        
        # Details für jeden ausgewählten Call sammeln
        to_close = []
        for item in selected_items:
            values = self.calls_tree.item(item, "values")
            # Speichere Datum, Symbol UND MCAP als eindeutige Identifikation
            to_close.append((values[0], values[1], values[2]))  # (Datum, Symbol, MCAP_at_Call)
        
        # Profit-Summe für Budget-Aktualisierung
        total_profit = 0
        
        # Alle Calls durchgehen und abschließen
        for call in calls:
            # Überspringe bereits abgeschlossene Calls
            if call.get("abgeschlossen", False):
                continue
                
            # Prüfe, ob dieser Call abgeschlossen werden soll
            current_call_id = (call.get("Datum", ""), call.get("Symbol", ""), call.get("MCAP_at_Call", ""))
            if current_call_id in to_close:
                try:
                    profit = float(call.get("PL_Dollar", "0").rstrip("$"))
                except Exception:
                    profit = 0.0
                total_profit += profit
                call["abgeschlossen"] = True
        
        # Budget aktualisieren
        current_budget = storage.load_budget()
        new_budget = current_budget + total_profit
        storage.save_budget(new_budget)
            
        # Daten speichern und UI aktualisieren
        storage.save_call_data(calls)
        self.update_tree()
        if hasattr(self.main_window, 'update_archived_calls_tree'):
            self.main_window.update_archived_calls_tree()
            
        # Budget-Anzeige aktualisieren
        self.main_window.current_balance_label.config(text=f"Kontostand: {new_budget:.2f}$")
        if new_budget > 500:
            self.main_window.current_balance_label.config(bg="#d8ffd8")
        elif new_budget < 500:
            self.main_window.current_balance_label.config(bg="#ffd8d8")
        else:
            self.main_window.current_balance_label.config(bg="white")