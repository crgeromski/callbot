# Watchlist TreeView
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import webbrowser
import data.storage as storage
import utils.formatters as formatters

class WatchlistTreeView:
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.create_treeview()
        
    def create_treeview(self):
        """Erstellt den TreeView für die Beobachtungsliste"""
        # Container für die Treeview mit Scrollbars
        self.frame = tk.Frame(self.parent)
        self.frame.pack(fill="both", expand=True)
        
        # Nur vertikaler Scrollbar
        yscrollbar = ttk.Scrollbar(self.frame, orient="vertical")
        yscrollbar.pack(side="right", fill="y")
        
        # Erstelle eine Treeview mit den gewünschten Spalten
        self.watchlist_tree = ttk.Treeview(
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
            yscrollcommand=yscrollbar.set
        )
        
        # Konfiguriere die Scrollbars
        yscrollbar.config(command=self.watchlist_tree.yview)
        
        # Definiere die Spaltenüberschriften
        self.watchlist_tree.heading("Datum", text="Datum", command=lambda: self.sort_treeview("Datum", False))
        self.watchlist_tree.heading("Symbol", text="Symbol", command=lambda: self.sort_treeview("Symbol", False))
        self.watchlist_tree.heading("MCAP_at_Call", text="MCAP at Safe", command=lambda: self.sort_treeview("MCAP_at_Call", False))
        self.watchlist_tree.heading("Aktuelles_MCAP", text="Live MCAP", command=lambda: self.sort_treeview("Aktuelles_MCAP", False))
        self.watchlist_tree.heading("X_Factor", text="X-Factor", command=lambda: self.sort_treeview("X_Factor", False))
        self.watchlist_tree.heading("PL_Percent", text="% P/L", command=lambda: self.sort_treeview("PL_Percent", False))
        self.watchlist_tree.heading("PL_Dollar", text="$ P/L", command=lambda: self.sort_treeview("PL_Dollar", False))
        self.watchlist_tree.heading("Invest", text="Invest", command=lambda: self.sort_treeview("Invest", False))
        
        # Definiere Zeilen-Farbtags
        self.watchlist_tree.tag_configure("row_green", background="#d8ffd8")
        self.watchlist_tree.tag_configure("row_red", background="#ffd8d8")
        
        # Definiere die Spaltenbreiten und Ausrichtung
        # Gesamtbreite verfügbar: 630px, weniger Padding und Scrollbar ~ 600px
        # 8 Spalten: Datum, Symbol, MCAP_at_Call, Aktuelles_MCAP, X_Factor, PL_Percent, PL_Dollar, Invest
        self.watchlist_tree.column("Datum", width=60, minwidth=60, anchor="center")         # 60px
        self.watchlist_tree.column("Symbol", width=80, minwidth=80, anchor="center")        # 80px
        self.watchlist_tree.column("MCAP_at_Call", width=100, minwidth=100, anchor="center") # 100px
        self.watchlist_tree.column("Aktuelles_MCAP", width=90, minwidth=90, anchor="center") # 90px
        self.watchlist_tree.column("X_Factor", width=70, minwidth=70, anchor="center")      # 70px
        self.watchlist_tree.column("PL_Percent", width=70, minwidth=70, anchor="center")    # 70px
        self.watchlist_tree.column("PL_Dollar", width=70, minwidth=70, anchor="center")     # 70px
        self.watchlist_tree.column("Invest", width=60, minwidth=60, anchor="center")        # 60px
        # Summe: 600px

        # Packe den Treeview in den Tab
        self.watchlist_tree.pack(fill="both", expand=True)
        
        # Binde das Doppelklick-Event an die Treeview
        self.watchlist_tree.bind("<Double-1>", self.on_treeview_double_click)
        
        # Binde das Klick-Event zum Aufheben der Auswahl
        self.watchlist_tree.bind("<Button-1>", self.on_treeview_click)
        
        # Kontextmenü hinzufügen
        self.context_menu = tk.Menu(self.watchlist_tree, tearoff=0)
        self.watchlist_tree.bind("<Button-3>", self.show_context_menu)
        
        # Einträge zum Kontextmenü hinzufügen
        self.context_menu.add_command(label="MCAP at Safe ändern", command=self.edit_mcap_at_call)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Entfernen", command=self.delete_selected_watchlist_item)
        self.context_menu.add_command(label="Call erstellen", command=self.create_call_from_watchlist)
        
        # Die internen Tag-Variablen initialisieren
        self.current_selected_item = None
        self.current_selected_tag = None
        
        # Sortierungsstatus initialisieren
        self.sort_status = {"column": None, "reverse": False}
    
    def edit_mcap_at_call(self):
        """Bearbeitet den MCAP at Safe Wert des ausgewählten Eintrags"""
        selected_items = self.watchlist_tree.selection()
        if not selected_items:
            messagebox.showinfo("Hinweis", "Bitte wähle zuerst einen Eintrag aus.")
            return
            
        # Wenn mehrere ausgewählt sind, nur den ersten bearbeiten
        item = selected_items[0]
        values = self.watchlist_tree.item(item, "values")
        
        # Datum, Symbol und MCAP_at_Call aus den Werten extrahieren
        datum = values[0]
        symbol = values[1]
        current_mcap = values[2]
        
        # Dialog zur Eingabe des neuen MCAP-Wertes
        new_mcap = simpledialog.askstring(
            "MCAP at Safe ändern",
            f"Neuen MCAP-Wert für {symbol} eingeben (z.B. 500K, 1.2M):",
            initialvalue=current_mcap
        )
        
        if not new_mcap:
            return  # Abbruch, wenn keine Eingabe
            
        # Prüfe, ob der MCAP-Wert gültig ist (K/M Format)
        try:
            parsed_value = formatters.parse_km(new_mcap)
            if parsed_value <= 0:
                messagebox.showerror("Fehler", "Bitte gib einen gültigen MCAP-Wert ein (z.B. 500K, 1.2M)")
                return
        except:
            messagebox.showerror("Fehler", "Bitte gib einen gültigen MCAP-Wert ein (z.B. 500K, 1.2M)")
            return
            
        # Formatiere den neuen Wert im K/M Format
        formatted_mcap = formatters.format_k(parsed_value)
        
        # Lade alle Watchlist-Einträge
        watchlist_items = storage.load_watchlist_data()
        
        # Finde den entsprechenden Eintrag und aktualisiere den MCAP-Wert
        item_found = False
        for item in watchlist_items:
            if item.get("Datum") == datum and item.get("Symbol") == symbol:
                # MCAP-Wert aktualisieren
                item["MCAP_at_Call"] = formatted_mcap
                
                # X-Factor, PL_Percent und PL_Dollar neu berechnen
                initial_mcap = formatters.parse_km(formatted_mcap)
                current_mcap = formatters.parse_km(item.get("Aktuelles_MCAP", "0"))
                
                if initial_mcap > 0 and current_mcap > 0:
                    x_factor = current_mcap / initial_mcap
                    pl_percent = (x_factor - 1) * 100
                    
                    # Fiktiver Invest-Wert für die Anzeige (10$)
                    invest = 10.0
                    pl_dollar = invest * x_factor - invest
                    
                    item["X_Factor"] = f"{x_factor:.1f}X"
                    item["PL_Percent"] = f"{pl_percent:.0f}%"
                    item["PL_Dollar"] = f"{pl_dollar:.2f}$"
                
                item_found = True
                break
                
        if not item_found:
            messagebox.showerror("Fehler", f"Der Eintrag für {symbol} konnte nicht gefunden werden.")
            return
            
        # Speichere die aktualisierten Watchlist-Einträge
        storage.save_watchlist_data(watchlist_items)
        
        # Aktualisiere die Anzeige
        self.update_tree()
            
        # Bestätigungsmeldung
        messagebox.showinfo("Erfolg", f"Der MCAP-Wert für {symbol} wurde auf {formatted_mcap} geändert.")
    
    def sort_treeview(self, column, reverse):
        """Sortiert die Treeview nach der angegebenen Spalte"""
        # Speichere die aktuelle Auswahl, bevor wir sortieren
        selected_items = self.watchlist_tree.selection()
        
        # Liste aller Zeilen-IDs und ihre Werte in der Sortierspalte
        data = []
        for child in self.watchlist_tree.get_children(''):
            values = self.watchlist_tree.item(child, 'values')
            col_index = self.watchlist_tree["columns"].index(column)
            data.append((child, values[col_index]))
        
        # Custom Sortierfunktion basierend auf dem Datentyp
        def sort_by_value(item):
            value = item[1]
            if column in ["X_Factor"]:
                # Entferne 'X' und konvertiere zu float
                try:
                    return float(value.rstrip("X"))
                except ValueError:
                    return 0
            elif column in ["MCAP_at_Call", "Aktuelles_MCAP"]:
                # Konvertiere K/M Notation zu float
                try:
                    return formatters.parse_km(value)
                except ValueError:
                    return 0
            # Für Datum und Symbol: alphabetische Sortierung
            return value
        
        # Sortiere die Daten
        data.sort(key=sort_by_value, reverse=reverse)
        
        # Neu anordnen der Elemente im Treeview
        for i, item in enumerate(data):
            self.watchlist_tree.move(item[0], '', i)
        
        # Aktualisiere den Sortierungsstatus
        self.sort_status = {"column": column, "reverse": reverse}
        
        # Ändere den Headingtext, um die Sortierrichtung anzuzeigen
        if reverse:
            self.watchlist_tree.heading(column, text=f"{self.get_original_heading(column)} ▼", 
                                  command=lambda c=column: self.sort_treeview(c, False))
        else:
            self.watchlist_tree.heading(column, text=f"{self.get_original_heading(column)} ▲", 
                                  command=lambda c=column: self.sort_treeview(c, True))
        
        # Stelle sicher, dass alle anderen Spaltenüberschriften keine Pfeile haben
        for col in self.watchlist_tree["columns"]:
            if col != column:
                self.watchlist_tree.heading(col, text=self.get_original_heading(col), 
                                      command=lambda c=col: self.sort_treeview(c, False))
        
        # Stelle die Auswahl wieder her
        if selected_items:
            for item in selected_items:
                try:
                    self.watchlist_tree.selection_add(item)
                except:
                    pass  # Item existiert möglicherweise nicht mehr
    
    def get_original_heading(self, column):
        """Gibt den ursprünglichen Spaltennamen ohne Sortierpfeile zurück"""
        headings = {
            "Datum": "Datum",
            "Symbol": "Symbol",
            "MCAP_at_Call": "MCAP at Safe",
            "Aktuelles_MCAP": "Live MCAP",
            "X_Factor": "X-Factor",
            "PL_Percent": "% P/L",
            "PL_Dollar": "$ P/L",
            "Invest": "Invest"
        }
        return headings.get(column, column)
    
    def on_treeview_click(self, event):
        """Behandelt Klicks auf die Treeview und ändert die Hintergrundfarbe basierend auf X-Faktor"""
        # Identifiziere das Element unter dem Mauszeiger
        item = self.watchlist_tree.identify_row(event.y)
        
        # Wenn die vorherige Auswahl existiert, setze sie zurück
        if self.current_selected_item:
            current_tags = list(self.watchlist_tree.item(self.current_selected_item, "tags"))
            if self.current_selected_tag in current_tags:
                current_tags.remove(self.current_selected_tag)
                self.watchlist_tree.item(self.current_selected_item, tags=current_tags)
        
        # Wenn kein Element gefunden wurde (Klick ins Leere), hebe die Auswahl auf
        if not item:
            self.watchlist_tree.selection_remove(self.watchlist_tree.selection())
            self.current_selected_item = None
            self.current_selected_tag = None
            return
        
        # Wenn das geklickte Element bereits ausgewählt ist, hebe die Auswahl auf
        if item in self.watchlist_tree.selection():
            self.watchlist_tree.selection_remove(item)
            self.current_selected_item = None
            self.current_selected_tag = None
            return
            
        # Auswahl setzen
        self.watchlist_tree.selection_set(item)
        
        # Bestimme, ob der Watchlist-Eintrag positiven X-Faktor hat
        values = self.watchlist_tree.item(item, "values")
        try:
            x_factor_str = values[4]  # X_Factor ist an Position 4
            if x_factor_str:
                x_factor = float(x_factor_str.rstrip("X"))
                is_positive = x_factor >= 1
            else:
                is_positive = False
        except (ValueError, IndexError):
            is_positive = False
        
        # Ändere die Hintergrundfarbe direkt ohne Tags
        if is_positive:
            self.watchlist_tree.configure(style="profitable.Treeview")
            
            # Manuell das Hintergrundstil-Tag ändern
            style = ttk.Style()
            style.map('Treeview', 
                  background=[('selected', '#64c264')])  # Dunkleres Grün
        else:
            self.watchlist_tree.configure(style="unprofitable.Treeview")
            
            # Manuell das Hintergrundstil-Tag ändern
            style = ttk.Style()
            style.map('Treeview', 
                  background=[('selected', '#f48a8a')])  # Dunkleres Rot
        
        # Aktualisiere Referenzen
        self.current_selected_item = item
        self.current_selected_tag = "profitable" if is_positive else "unprofitable"
    
    def show_context_menu(self, event):
        """Zeigt das Kontextmenü bei Rechtsklick an"""
        # Wähle das Item unter dem Cursor
        item = self.watchlist_tree.identify_row(event.y)
        if item:
            # Setze die Auswahl auf das Item unter dem Cursor
            self.watchlist_tree.selection_set(item)
            
            # Bestimme, ob der Watchlist-Eintrag positiven X-Faktor hat
            values = self.watchlist_tree.item(item, "values")
            try:
                x_factor_str = values[4]  # X_Factor ist an Position 4
                if x_factor_str:
                    x_factor = float(x_factor_str.rstrip("X"))
                    is_positive = x_factor >= 1
                else:
                    is_positive = False
            except (ValueError, IndexError):
                is_positive = False
            
            # Ändere die Hintergrundfarbe direkt ohne Tags
            style = ttk.Style()
            if is_positive:
                style.map('Treeview', 
                    background=[('selected', '#64c264')])  # Dunkleres Grün
            else:
                style.map('Treeview', 
                    background=[('selected', '#f48a8a')])  # Dunkleres Rot
            
            # Aktualisiere Referenzen
            self.current_selected_item = item
            self.current_selected_tag = "profitable" if is_positive else "unprofitable"
            
            # Zeige das Kontextmenü
            self.context_menu.post(event.x_root, event.y_root)
    
    def update_tree(self):
        """Aktualisiert den Treeview in der Beobachtungsliste mit den gespeicherten Watchlist-Einträgen."""
        # Speichere die aktuelle Auswahl, bevor wir die Daten aktualisieren
        selected_item_values = None
        if self.watchlist_tree.selection():
            item_id = self.watchlist_tree.selection()[0]
            selected_item_values = self.watchlist_tree.item(item_id, "values")
        
        self.watchlist_tree.delete(*self.watchlist_tree.get_children())
        
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
        
        for watchlist_item in storage.load_watchlist_data():
            # Versuche, die Zahlenwerte aus dem Watchlist-Eintrag zu holen
            try:
                x_factor_str = watchlist_item.get("X_Factor") or "0"
                # Entferne das "X", damit wir float-Werte haben
                x_factor_val = float(x_factor_str.rstrip("X"))
                
                # Berechne PL_Percent und PL_Dollar
                initial_mcap = formatters.parse_km(watchlist_item.get("MCAP_at_Call", "0"))
                current_mcap = formatters.parse_km(watchlist_item.get("Aktuelles_MCAP", "0"))
                
                if initial_mcap > 0 and x_factor_val > 0:
                    pl_percent = (x_factor_val - 1) * 100
                    # Fiktiver Invest Wert für Darstellung (wirkt sich nicht auf Gewinnrechner aus)
                    invest = 10.0
                    pl_dollar = invest * x_factor_val - invest
                else:
                    pl_percent = 0
                    pl_dollar = 0
                
                pl_percent_str = f"{pl_percent:.0f}%"
                pl_dollar_str = f"{pl_dollar:.2f}$"
                invest_str = "10"  # Fiktiver Wert für Anzeige
            except:
                x_factor_val = 0
                pl_percent_str = "0%"
                pl_dollar_str = "0.00$"
                invest_str = "10"
                
            # Standard-Tag (keine Färbung)
            row_tag = ""
                
            # Falls X-Faktor >= 1 => ganze Zeile hellgrün, sonst hellrot
            if x_factor_val >= 1:
                row_tag = "row_green"
            else:
                row_tag = "row_red"
            
            # Symbol und Datum für die Identifikation des Watchlist-Eintrags
            symbol = watchlist_item.get("Symbol", "")
            datum = watchlist_item.get("Datum", "")
                
            # Einfügen der Werte in den Treeview
            item_id = self.watchlist_tree.insert(
                "",
                "end",
                values=(
                    datum,
                    symbol,
                    watchlist_item.get("MCAP_at_Call", ""),
                    watchlist_item.get("Aktuelles_MCAP", ""),
                    watchlist_item.get("X_Factor", ""),
                    pl_percent_str,
                    pl_dollar_str,
                    invest_str
                ),
                tags=(row_tag,)
            )
            
            # Speichere die ID für die spätere Wiederherstellung der Auswahl
            id_map[(datum, symbol)] = item_id

        # Fügen Sie diese Zeile hinzu, um standardmäßig nach $ P/L zu sortieren
        self.sort_treeview("PL_Dollar", True)
        
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
                self.watchlist_tree.selection_set(item_id)
                self.current_selected_item = item_id
                # Bestimme den Tag basierend auf X-Faktor
                try:
                    x_factor_str = selected_item_values[4]  # X_Factor ist an Position 4
                    if x_factor_str:
                        x_factor = float(x_factor_str.rstrip("X"))
                        is_positive = x_factor >= 1
                    else:
                        is_positive = False
                except (ValueError, IndexError):
                    is_positive = False
                
                self.current_selected_tag = "profitable" if is_positive else "unprofitable"
                
                # Setze den Stil basierend auf dem X-Faktor
                if is_positive:
                    style.map('Treeview', background=[('selected', '#64c264')])  # Dunkleres Grün
                else:
                    style.map('Treeview', background=[('selected', '#f48a8a')])  # Dunkleres Rot
    
    def on_treeview_double_click(self, event):
        """Reagiert auf Doppelklick in der Treeview"""
        item = self.watchlist_tree.identify_row(event.y)
        if item:
            # Hole alle Werte der ausgewählten Zeile
            values = self.watchlist_tree.item(item, "values")
            
            # Suche nach dem Link für diesen Watchlist-Eintrag
            watchlist_items = storage.load_watchlist_data()
            matching_items = [item for item in watchlist_items if 
                              item.get("Symbol") == values[1] and  # Symbol stimmt überein
                              item.get("Datum") == values[0]]     # Datum stimmt überein
            
            if matching_items and len(matching_items) > 0:
                item = matching_items[0]
                link = item.get("Link")
                
                if link:
                    # Setze den Link in die Entry-Variable
                    self.main_window.shared_vars['entry_var'].set(link)
                    
                    # Rufe Daten ab
                    self.main_window.fetch_data()
                    
                    # Wechsle zum Main Bot Tab
                    self.main_window.notebook.select(self.main_window.tabs['main'])
    
    def delete_selected_watchlist_item(self):
        """Löscht nur die ausgewählten Watchlist-Einträge aus der Liste"""
        selected_items = self.watchlist_tree.selection()
        if not selected_items:
            messagebox.showinfo("Hinweis", "Bitte wähle zuerst mindestens einen Eintrag aus, den du löschen möchtest.")
            return
        
        # Lade vorhandene Watchlist-Einträge
        watchlist_items = storage.load_watchlist_data()
        new_watchlist = []
        
        # Details für jeden ausgewählten Eintrag sammeln
        to_delete = []
        for item in selected_items:
            values = self.watchlist_tree.item(item, "values")
            # Speichere Datum, Symbol UND MCAP als eindeutige Identifikation
            to_delete.append((values[0], values[1], values[2]))  # (Datum, Symbol, MCAP_at_Call)
            
        # Nur Einträge behalten, die nicht gelöscht werden sollen
        for item in watchlist_items:
            # Prüfe, ob dieser Eintrag gelöscht werden soll
            current_item_id = (item.get("Datum", ""), item.get("Symbol", ""), item.get("MCAP_at_Call", ""))
            if current_item_id in to_delete:
                continue  # Diesen Eintrag nicht behalten
            
            # Ansonsten Eintrag behalten
            new_watchlist.append(item)
        
        # Speichern und aktualisieren
        storage.save_watchlist_data(new_watchlist)
        
        # Setze die Auswahl zurück
        self.current_selected_item = None
        self.current_selected_tag = None
        
        self.update_tree()
    
    def create_call_from_watchlist(self):
        """Erstellt einen Call aus dem ausgewählten Watchlist-Eintrag"""
        selected_items = self.watchlist_tree.selection()
        if not selected_items:
            messagebox.showinfo("Hinweis", "Bitte wähle einen Eintrag aus, um einen Call zu erstellen.")
            return
            
        # Beschränkung auf einen Eintrag
        if len(selected_items) > 1:
            messagebox.showinfo("Hinweis", "Bitte wähle nur einen Eintrag aus, um einen Call zu erstellen.")
            return
            
        item = selected_items[0]
        values = self.watchlist_tree.item(item, "values")
        
        # Lade vorhandene Watchlist-Einträge
        watchlist_items = storage.load_watchlist_data()
        
        # Finde den entsprechenden Watchlist-Eintrag
        matching_items = [wi for wi in watchlist_items if 
                          wi.get("Symbol") == values[1] and  # Symbol stimmt überein
                          wi.get("Datum") == values[0]]     # Datum stimmt überein
        
        if not matching_items:
            messagebox.showerror("Fehler", "Der ausgewählte Eintrag konnte nicht gefunden werden.")
            return
            
        watchlist_item = matching_items[0]
        
        # Erstelle einen neuen Call
        call_data = {
            "Datum": watchlist_item.get("Datum"),
            "Symbol": watchlist_item.get("Symbol"),
            "MCAP_at_Call": watchlist_item.get("MCAP_at_Call"),
            "Link": watchlist_item.get("Link"),
            "Aktuelles_MCAP": watchlist_item.get("Aktuelles_MCAP"),  # Aktuelles MCAP übernehmen
            "Invest": "10",  # Fester Investitionswert: 10$
            "X_Factor": watchlist_item.get("X_Factor", "1.0X"),
            "PL_Percent": "0%",  # Initialer Wert
            "PL_Dollar": "0.00$"  # Initialer Wert
        }
        
        # Speichere den neuen Call
        storage.save_new_call(call_data)
        
        # Aktualisiere die Calls TreeView
        if hasattr(self.main_window, 'update_calls_tree'):
            self.main_window.update_calls_tree()
            
        # Optional: Entferne den Eintrag aus der Watchlist
        self.delete_selected_watchlist_item()
        
        # Zeige Erfolgsmeldung
        messagebox.showinfo("Erfolg", f"Call für {call_data['Symbol']} wurde erstellt.")