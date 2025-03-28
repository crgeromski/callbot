# Calls TreeView
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import data.storage as storage
import utils.formatters as formatters

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
        self.calls_tree.heading("Datum", text="Datum", command=lambda: self.sort_treeview("Datum", False))
        self.calls_tree.heading("Symbol", text="Symbol", command=lambda: self.sort_treeview("Symbol", False))
        self.calls_tree.heading("MCAP_at_Call", text="MCAP at Call", command=lambda: self.sort_treeview("MCAP_at_Call", False))
        self.calls_tree.heading("Aktuelles_MCAP", text="Live MCAP", command=lambda: self.sort_treeview("Aktuelles_MCAP", False))
        self.calls_tree.heading("X_Factor", text="X-Factor", command=lambda: self.sort_treeview("X_Factor", False))
        self.calls_tree.heading("PL_Percent", text="% P/L", command=lambda: self.sort_treeview("PL_Percent", False))
        self.calls_tree.heading("PL_Dollar", text="$ P/L", command=lambda: self.sort_treeview("PL_Dollar", False))
        self.calls_tree.heading("Invest", text="Invest", command=lambda: self.sort_treeview("Invest", False))
        
        # Definiere Zeilen-Farbtags
        self.calls_tree.tag_configure("row_green", background="#d8ffd8")
        self.calls_tree.tag_configure("row_red", background="#ffd8d8")
        
        # Definiere die Spaltenbreiten und Ausrichtung
        # Gesamtbreite verfügbar: 630px, weniger Padding und Scrollbar ~ 600px
        # 8 Spalten: Datum, Symbol, MCAP_at_Call, Aktuelles_MCAP, X_Factor, PL_Percent, PL_Dollar, Invest
        self.calls_tree.column("Datum", width=60, minwidth=60, anchor="center")         # 60px
        self.calls_tree.column("Symbol", width=80, minwidth=80, anchor="center")        # 80px
        self.calls_tree.column("MCAP_at_Call", width=100, minwidth=100, anchor="center") # 100px
        self.calls_tree.column("Aktuelles_MCAP", width=90, minwidth=90, anchor="center") # 90px
        self.calls_tree.column("X_Factor", width=70, minwidth=70, anchor="center")      # 70px
        self.calls_tree.column("PL_Percent", width=70, minwidth=70, anchor="center")    # 70px
        self.calls_tree.column("PL_Dollar", width=70, minwidth=70, anchor="center")     # 70px
        self.calls_tree.column("Invest", width=60, minwidth=60, anchor="center")        # 60px
        # Summe: 600px

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
        
        # Sortierungsstatus initialisieren
        self.sort_status = {"column": None, "reverse": False}
    
    def sort_treeview(self, column, reverse):
        """Sortiert die Treeview nach der angegebenen Spalte"""
        # Speichere die aktuelle Auswahl, bevor wir sortieren
        selected_items = self.calls_tree.selection()
        
        # Liste aller Zeilen-IDs und ihre Werte in der Sortierspalte
        data = []
        for child in self.calls_tree.get_children(''):
            values = self.calls_tree.item(child, 'values')
            col_index = self.calls_tree["columns"].index(column)
            data.append((child, values[col_index]))
        
        # Custom Sortierfunktion basierend auf dem Datentyp
        def sort_by_value(item):
            value = item[1]
            if column in ["X_Factor", "PL_Percent", "PL_Dollar"]:
                # Entferne 'X', '%', '$' und konvertiere zu float
                try:
                    if column == "X_Factor":
                        return float(value.rstrip("X"))
                    elif column == "PL_Percent":
                        return float(value.rstrip("%"))
                    elif column == "PL_Dollar":
                        return float(value.rstrip("$"))
                except ValueError:
                    return 0
            elif column in ["MCAP_at_Call", "Aktuelles_MCAP"]:
                # Konvertiere K/M Notation zu float
                try:
                    return formatters.parse_km(value)
                except ValueError:
                    return 0
            elif column == "Invest":
                # Konvertiere zu float
                try:
                    return float(value)
                except ValueError:
                    return 0
            # Für Datum und Symbol: alphabetische Sortierung
            return value
        
        # Sortiere die Daten
        data.sort(key=sort_by_value, reverse=reverse)
        
        # Neu anordnen der Elemente im Treeview
        for i, item in enumerate(data):
            self.calls_tree.move(item[0], '', i)
        
        # Aktualisiere den Sortierungsstatus
        self.sort_status = {"column": column, "reverse": reverse}
        
        # Ändere den Headingtext, um die Sortierrichtung anzuzeigen
        if reverse:
            self.calls_tree.heading(column, text=f"{self.get_original_heading(column)} ▼", 
                                  command=lambda c=column: self.sort_treeview(c, False))
        else:
            self.calls_tree.heading(column, text=f"{self.get_original_heading(column)} ▲", 
                                  command=lambda c=column: self.sort_treeview(c, True))
        
        # Stelle sicher, dass alle anderen Spaltenüberschriften keine Pfeile haben
        for col in self.calls_tree["columns"]:
            if col != column:
                self.calls_tree.heading(col, text=self.get_original_heading(col), 
                                      command=lambda c=col: self.sort_treeview(c, False))
        
        # Stelle die Auswahl wieder her
        if selected_items:
            for item in selected_items:
                try:
                    self.calls_tree.selection_add(item)
                except:
                    pass  # Item existiert möglicherweise nicht mehr
    
    def get_original_heading(self, column):
        """Gibt den ursprünglichen Spaltennamen ohne Sortierpfeile zurück"""
        headings = {
            "Datum": "Datum",
            "Symbol": "Symbol",
            "MCAP_at_Call": "MCAP at Call",
            "Aktuelles_MCAP": "Live MCAP",
            "X_Factor": "X-Factor",
            "PL_Percent": "% P/L",
            "PL_Dollar": "$ P/L",
            "Invest": "Invest"
        }
        return headings.get(column, column)
    
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
        # Speichere die aktuelle Auswahl, bevor wir die Daten aktualisieren
        selected_item_values = None
        if self.calls_tree.selection():
            item_id = self.calls_tree.selection()[0]
            selected_item_values = self.calls_tree.item(item_id, "values")
        
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
        
        # Dictionary zum Speichern der IDs nach Symbol und Datum für die Wiederherstellung der Auswahl
        id_map = {}
        
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
            
            # Symbol und Datum für die Identifikation des Calls
            symbol = call.get("Symbol", "")
            datum = call.get("Datum", "")
                
            # Einfügen der Werte in den Treeview
            item_id = self.calls_tree.insert(
                "",
                "end",
                values=(
                    datum,
                    symbol,
                    call.get("MCAP_at_Call", ""),
                    call.get("Aktuelles_MCAP", ""),
                    call.get("X_Factor", ""),
                    call.get("PL_Percent", ""),
                    call.get("PL_Dollar", ""),
                    call.get("Invest", "")
                ),
                tags=(row_tag,)
            )
            
            # Speichere die ID für die spätere Wiederherstellung der Auswahl
            id_map[(datum, symbol)] = item_id
        
        # Wende die aktuelle Sortierung an, falls vorhanden
        if self.sort_status["column"]:
            self.sort_treeview(self.sort_status["column"], self.sort_status["reverse"])
        
        # Stelle die Auswahl wieder her, falls zuvor eine Auswahl vorhanden war
        if selected_item_values:
            # Versuche, das Element anhand von Datum und Symbol zu finden
            datum = selected_item_values[0]
            symbol = selected_item_values[1]
            if (datum, symbol) in id_map:
                item_id = id_map[(datum, symbol)]
                self.calls_tree.selection_set(item_id)
                self.current_selected_item = item_id
                # Bestimme den Tag basierend auf der Profitabilität
                try:
                    pl_dollar_str = selected_item_values[6]  # PL_Dollar ist an Position 6
                    if pl_dollar_str:
                        pl_dollar = float(pl_dollar_str.rstrip("$"))
                        is_profitable = pl_dollar >= 0
                    else:
                        is_profitable = False
                except (ValueError, IndexError):
                    is_profitable = False
                
                self.current_selected_tag = "profitable" if is_profitable else "unprofitable"
                
                # Setze den Stil basierend auf der Profitabilität
                if is_profitable:
                    style.map('Treeview', background=[('selected', '#64c264')])  # Dunkleres Grün
                else:
                    style.map('Treeview', background=[('selected', '#f48a8a')])  # Dunkleres Rot
    
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