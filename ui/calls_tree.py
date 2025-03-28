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
        # Container für die Treeview mit Scrollbars
        self.frame = tk.Frame(self.parent)
        self.frame.pack(fill="both", expand=True)
        
        # Horizontaler Scrollbar
        xscrollbar = ttk.Scrollbar(self.frame, orient="horizontal")
        xscrollbar.pack(side="bottom", fill="x")
        
        # Vertikaler Scrollbar
        yscrollbar = ttk.Scrollbar(self.frame, orient="vertical")
        yscrollbar.pack(side="right", fill="y")
        
        # Erstelle eine Treeview mit den gewünschten Spalten
        self.calls_tree = ttk.Treeview(
            self.frame,
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
            show="headings",
            style="Treeview",
            xscrollcommand=xscrollbar.set,
            yscrollcommand=yscrollbar.set
        )
        
        # Konfiguriere die Scrollbars
        xscrollbar.config(command=self.calls_tree.xview)
        yscrollbar.config(command=self.calls_tree.yview)
        
        # Definiere die Spaltenüberschriften
        self.calls_tree.heading("Datum", text="Datum")
        self.calls_tree.heading("Symbol", text="Symbol")
        self.calls_tree.heading("MCAP_at_Call", text="MCAP at Call")
        self.calls_tree.heading("Aktuelles_MCAP", text="Live MCAP")
        self.calls_tree.heading("X_Factor", text="X-Factor")
        self.calls_tree.heading("PL_Percent", text="% P/L")
        self.calls_tree.heading("PL_Dollar", text="$ P/L")
        self.calls_tree.heading("Invest", text="Invest")
        
        # Definiere Zeilen-Farbtags
        self.calls_tree.tag_configure("row_green", background="#d8ffd8")
        self.calls_tree.tag_configure("row_red", background="#ffd8d8")
        
        # Definiere die Spaltenbreiten und Ausrichtung
        # Minimale Breite für alle Spalten, damit sie immer sichtbar sind
        min_column_width = 70
        self.calls_tree.column("Datum", width=min_column_width, minwidth=min_column_width, anchor="center")
        self.calls_tree.column("Symbol", width=min_column_width, minwidth=min_column_width, anchor="center")
        self.calls_tree.column("MCAP_at_Call", width=min_column_width, minwidth=min_column_width, anchor="center")
        self.calls_tree.column("Aktuelles_MCAP", width=min_column_width, minwidth=min_column_width, anchor="center")
        self.calls_tree.column("X_Factor", width=min_column_width, minwidth=min_column_width, anchor="center")
        self.calls_tree.column("PL_Percent", width=min_column_width, minwidth=min_column_width, anchor="center")
        self.calls_tree.column("PL_Dollar", width=min_column_width, minwidth=min_column_width, anchor="center")
        self.calls_tree.column("Invest", width=min_column_width, minwidth=min_column_width, anchor="center")

        # Packe den Treeview in den Tab
        self.calls_tree.pack(fill="both", expand=True)
        
        # Binde das Doppelklick-Event an die Treeview
        self.calls_tree.bind("<Double-1>", self.on_treeview_double_click)
        
        # Binde das Klick-Event zum Aufheben der Auswahl
        self.calls_tree.bind("<Button-1>", self.on_treeview_click)
        
        # Kontextmenü hinzufügen
        self.context_menu = tk.Menu(self.calls_tree, tearoff=0)
        self.calls_tree.bind("<Button-3>", self.show_context_menu)
        
        # Einträge zum Kontextmenü hinzufügen
        self.context_menu.add_command(label="Call abschließen", command=self.close_selected_call)
        self.context_menu.add_command(label="Call löschen", command=self.delete_selected_call)
        
        # Die internen Tag-Variablen initialisieren
        self.current_selected_item = None
        self.current_selected_tag = None
    
    def on_treeview_click(self, event):
        """Behandelt Klicks auf die Treeview und ändert die Hintergrundfarbe basierend auf Profitabilität"""
        # Identifiziere das Element unter dem Mauszeiger
        item = self.calls_tree.identify_row(event.y)
        
        # Wenn die vorherige Auswahl existiert, setze sie zurück
        if self.current_selected_item:
            current_tags = list(self.calls_tree.item(self.current_selected_item, "tags"))
            if self.current_selected_tag in current_tags:
                current_tags.remove(self.current_selected_tag)
                self.calls_tree.item(self.current_selected_item, tags=current_tags)
        
        # Wenn kein Element gefunden wurde (Klick ins Leere), hebe die Auswahl auf
        if not item:
            self.calls_tree.selection_remove(self.calls_tree.selection())
            self.current_selected_item = None
            self.current_selected_tag = None
            return
        
        # Wenn das geklickte Element bereits ausgewählt ist, hebe die Auswahl auf
        if item in self.calls_tree.selection():
            self.calls_tree.selection_remove(item)
            self.current_selected_item = None
            self.current_selected_tag = None
            return
            
        # Auswahl setzen
        self.calls_tree.selection_set(item)
        
        # Bestimme, ob der Call profitabel ist
        values = self.calls_tree.item(item, "values")
        try:
            pl_dollar_str = values[6]  # PL_Dollar ist an Position 6
            if pl_dollar_str:
                pl_dollar = float(pl_dollar_str.rstrip("$"))
                is_profitable = pl_dollar >= 0
            else:
                is_profitable = False
        except (ValueError, IndexError):
            is_profitable = False
        
        # Ändere die Hintergrundfarbe direkt ohne Tags
        if is_profitable:
            self.calls_tree.configure(style="profitable.Treeview")
            
            # Manuell das Hintergrundstil-Tag ändern
            style = ttk.Style()
            style.map('Treeview', 
                  background=[('selected', '#64c264')])  # Dunkleres Grün
        else:
            self.calls_tree.configure(style="unprofitable.Treeview")
            
            # Manuell das Hintergrundstil-Tag ändern
            style = ttk.Style()
            style.map('Treeview', 
                  background=[('selected', '#f48a8a')])  # Dunkleres Rot
        
        # Aktualisiere Referenzen
        self.current_selected_item = item
        self.current_selected_tag = "profitable" if is_profitable else "unprofitable"
    
    def show_context_menu(self, event):
        """Zeigt das Kontextmenü bei Rechtsklick an"""
        # Wähle das Item unter dem Cursor
        item = self.calls_tree.identify_row(event.y)
        if item:
            # Setze die Auswahl auf das Item unter dem Cursor
            self.calls_tree.selection_set(item)
            
            # Bestimme, ob der Call profitabel ist
            values = self.calls_tree.item(item, "values")
            try:
                pl_dollar_str = values[6]  # PL_Dollar ist an Position 6
                if pl_dollar_str:
                    pl_dollar = float(pl_dollar_str.rstrip("$"))
                    is_profitable = pl_dollar >= 0
                else:
                    is_profitable = False
            except (ValueError, IndexError):
                is_profitable = False
            
            # Ändere die Hintergrundfarbe direkt ohne Tags
            style = ttk.Style()
            if is_profitable:
                style.map('Treeview', 
                      background=[('selected', '#64c264')])  # Dunkleres Grün
            else:
                style.map('Treeview', 
                      background=[('selected', '#f48a8a')])  # Dunkleres Rot
            
            # Aktualisiere Referenzen
            self.current_selected_item = item
            self.current_selected_tag = "profitable" if is_profitable else "unprofitable"
            
            # Zeige das Kontextmenü
            self.context_menu.post(event.x_root, event.y_root)
    
    def update_tree(self):
        """Aktualisiert den Treeview im 'Meine Calls'-Tab mit den gespeicherten Calls."""
        self.calls_tree.delete(*self.calls_tree.get_children())
        
        # Stil für aktive/inaktive Auswahl konfigurieren
        style = ttk.Style()
        style.configure("profitable.Treeview", 
                    background="white",
                    fieldbackground="white",
                    font=("Arial", 9))
        style.map('profitable.Treeview', 
              background=[('selected', '#64c264')])  # Dunkleres Grün
              
        style.configure("unprofitable.Treeview", 
                    background="white",
                    fieldbackground="white",
                    font=("Arial", 9))
        style.map('unprofitable.Treeview', 
              background=[('selected', '#f48a8a')])  # Dunkleres Rot
        
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
        
        # Setze die gespeicherte Auswahl zurück
        if self.current_selected_item:
            try:
                self.calls_tree.selection_set(self.current_selected_item)
            except:
                self.current_selected_item = None
                self.current_selected_tag = None
    
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
        
        # Setze die Auswahl zurück
        self.current_selected_item = None
        self.current_selected_tag = None
        
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
        
        # Setze die Auswahl zurück
        self.current_selected_item = None
        self.current_selected_tag = None
        
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