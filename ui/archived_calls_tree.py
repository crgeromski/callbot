# Archivierte Calls TreeView
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import webbrowser
import data.storage as storage

class ArchivedCallsTreeView:
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.create_treeview()
        
    def create_treeview(self):
        """Erstellt den TreeView für archivierte Calls"""
        # Container für die Treeview mit Scrollbars
        self.frame = tk.Frame(self.parent)
        self.frame.pack(fill="both", expand=True)
        
        # Nur vertikaler Scrollbar
        yscrollbar = ttk.Scrollbar(self.frame, orient="vertical")
        yscrollbar.pack(side="right", fill="y")
        
        # Erstelle den Treeview für archivierte Calls mit Scrollbars
        self.archived_calls_tree = ttk.Treeview(
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
        yscrollbar.config(command=self.archived_calls_tree.yview)
        
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
        
        # Neue Tags für ausgewählte Zeilen
        self.archived_calls_tree.tag_configure("selected_green", background="#64c264")  # Dunkleres Grün
        self.archived_calls_tree.tag_configure("selected_red", background="#f48a8a")    # Dunkleres Rot
        
        # Definiere die Spaltenbreiten und Ausrichtung mit optimierten Breiten
        self.archived_calls_tree.column("Datum", width=60, minwidth=60, anchor="center")         # 60px
        self.archived_calls_tree.column("Symbol", width=80, minwidth=80, anchor="center")        # 80px
        self.archived_calls_tree.column("MCAP_at_Call", width=100, minwidth=100, anchor="center") # 100px
        self.archived_calls_tree.column("Aktuelles_MCAP", width=90, minwidth=90, anchor="center") # 90px
        self.archived_calls_tree.column("X_Factor", width=70, minwidth=70, anchor="center")      # 70px
        self.archived_calls_tree.column("PL_Percent", width=70, minwidth=70, anchor="center")    # 70px
        self.archived_calls_tree.column("PL_Dollar", width=70, minwidth=70, anchor="center")     # 70px
        self.archived_calls_tree.column("Invest", width=60, minwidth=60, anchor="center")        # 60px
        # Summe: 600px
        
        # Doppelklick-Event
        self.archived_calls_tree.bind("<Double-1>", self.on_archived_double_click)
        # Klick-Event zum Aufheben der Auswahl
        self.archived_calls_tree.bind("<Button-1>", self.on_archived_click)
        # Überwache die Auswahl und wende die Tags erneut an
        self.archived_calls_tree.bind("<<TreeviewSelect>>", self.ensure_custom_selection)
        
        self.archived_calls_tree.pack(fill="both", expand=True)
        
        # Kontextmenü hinzufügen
        self.context_menu = tk.Menu(self.archived_calls_tree, tearoff=0)
        self.archived_calls_tree.bind("<Button-3>", self.show_context_menu)
        
        # Einträge zum Kontextmenü hinzufügen
        self.context_menu.add_command(label="MCAP at Call ändern", command=self.edit_mcap_at_call)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Call löschen", command=self.delete_selected_archived_call)
    

    def edit_mcap_at_call(self):
        """Bearbeitet den MCAP at Call Wert des ausgewählten archivierten Eintrags"""
        selected_items = self.archived_calls_tree.selection()
        if not selected_items:
            messagebox.showinfo("Hinweis", "Bitte wähle zuerst einen Call aus.")
            return
            
        # Wenn mehrere ausgewählt sind, nur den ersten bearbeiten
        item = selected_items[0]
        values = self.archived_calls_tree.item(item, "values")
        
        # Datum, Symbol und MCAP_at_Call aus den Werten extrahieren
        datum = values[0]
        symbol = values[1]
        current_mcap = values[2]
        
        # Dialog zur Eingabe des neuen MCAP-Wertes
        new_mcap = simpledialog.askstring(
            "MCAP at Call ändern",
            f"Neuen MCAP-Wert für {symbol} eingeben (z.B. 500K, 1.2M):",
            initialvalue=current_mcap
        )
        
        if not new_mcap:
            return  # Abbruch, wenn keine Eingabe
        
        # Vereinfachte Validierung
        new_mcap = new_mcap.strip().upper()  # Entferne Leerzeichen und konvertiere zu Großbuchstaben
        
        # Direktes Parsen ohne zu strenge Validierung
        try:
            # Standardisiere das Format: Ersetze Komma durch Punkt
            new_mcap = new_mcap.replace(",", ".")
            
            # Extrahiere den numerischen Teil
            if new_mcap.endswith("K"):
                parsed_value = float(new_mcap[:-1]) * 1000
            elif new_mcap.endswith("M"):
                parsed_value = float(new_mcap[:-1]) * 1000000
            else:
                # Versuche es als direkten Zahlenwert zu interpretieren
                parsed_value = float(new_mcap)
        except:
            messagebox.showerror("Fehler", "Bitte gib einen gültigen MCAP-Wert ein (z.B. 500K, 1.2M)")
            return
        
        # Einfache Positivprüfung
        if parsed_value <= 0:
            messagebox.showerror("Fehler", "Der MCAP-Wert muss positiv sein.")
            return
            
        # Formatiere den neuen Wert im K/M Format
        if parsed_value >= 1000000:
            formatted_mcap = f"{parsed_value/1000000:.1f}M"
        elif parsed_value >= 1000:
            formatted_mcap = f"{parsed_value/1000:.0f}K"
        else:
            formatted_mcap = f"{parsed_value:.0f}"
        
        # Lade alle Calls
        calls = storage.load_call_data()
        
        # Finde den entsprechenden Call und aktualisiere den MCAP-Wert
        call_found = False
        for call in calls:
            # Nur abgeschlossene Calls prüfen
            if not call.get("abgeschlossen", False):
                continue
                
            if call.get("Datum") == datum and call.get("Symbol") == symbol:
                # MCAP-Wert aktualisieren
                call["MCAP_at_Call"] = formatted_mcap
                
                # X-Factor, PL_Percent und PL_Dollar neu berechnen
                try:
                    initial_mcap = parsed_value  # Verwende direkt unseren bereits geparsten Wert
                    
                    # Parse aktuelles MCAP
                    current_mcap_str = call.get("Aktuelles_MCAP", "0")
                    if current_mcap_str.endswith("K"):
                        current_mcap = float(current_mcap_str[:-1]) * 1000
                    elif current_mcap_str.endswith("M"):
                        current_mcap = float(current_mcap_str[:-1]) * 1000000
                    else:
                        current_mcap = float(current_mcap_str)
                    
                    if initial_mcap > 0 and current_mcap > 0:
                        x_factor = current_mcap / initial_mcap
                        pl_percent = (x_factor - 1) * 100
                        
                        # Invest-Wert aus dem Call verwenden oder auf 10$ setzen
                        invest = 10.0
                        try:
                            invest_str = call.get("Invest", "10")
                            invest = float(invest_str)
                        except:
                            invest = 10.0
                            
                        pl_dollar = invest * x_factor - invest
                        
                        call["X_Factor"] = f"{x_factor:.1f}X"
                        call["PL_Percent"] = f"{pl_percent:.0f}%"
                        call["PL_Dollar"] = f"{pl_dollar:.2f}$"
                except Exception as e:
                    messagebox.showerror("Fehler bei Berechnung", f"Fehler: {str(e)}")
                    return
                    
                call_found = True
                break
                
        if not call_found:
            messagebox.showerror("Fehler", f"Der Call für {symbol} konnte nicht gefunden werden.")
            return
            
        # Speichere die aktualisierten Calls
        storage.save_call_data(calls)
        
        # Aktualisiere die Anzeige
        self.update_tree()
        
        # Optional: Aktualisiere den Kontostand im Hauptfenster
        if hasattr(self.main_window, 'update_ui_stats'):
            self.main_window.update_ui_stats()
            
        # Bestätigungsmeldung
        messagebox.showinfo("Erfolg", f"Der MCAP-Wert für {symbol} wurde auf {formatted_mcap} geändert.")

    def ensure_custom_selection(self, event):
        """Stellt sicher, dass ausgewählte Elemente die benutzerdefinierten Tags behalten"""
        for item in self.archived_calls_tree.selection():
            tags = list(self.archived_calls_tree.item(item, "tags"))
            if "row_green" in tags and "selected_green" not in tags:
                tags.append("selected_green")
                self.archived_calls_tree.item(item, tags=tuple(tags))
            elif "row_red" in tags and "selected_red" not in tags:
                tags.append("selected_red")
                self.archived_calls_tree.item(item, tags=tuple(tags))
        self.archived_calls_tree.update()
        
    def on_archived_click(self, event):
        """Behandelt Klicks auf die Treeview und setzt dunklere Auswahlfarben"""
        # Identifiziere das Element unter dem Mauszeiger
        item = self.archived_calls_tree.identify_row(event.y)
        
        # Wenn ein Klick ins Leere erfolgt, die Auswahl aufheben
        if not item:
            self.archived_calls_tree.selection_remove(self.archived_calls_tree.selection())
            return
        
        # Zurücksetzen aller Tags auf ihre Basisfarbe
        for i in self.archived_calls_tree.get_children():
            current_tags = list(self.archived_calls_tree.item(i, "tags"))
            
            # Entferne alle Auswahl-Tags
            if "selected_green" in current_tags:
                current_tags.remove("selected_green")
            if "selected_red" in current_tags:
                current_tags.remove("selected_red")
                
            # Setze die Tags zurück
            if "row_green" in current_tags or "row_red" in current_tags:
                self.archived_calls_tree.item(i, tags=tuple(current_tags))
        
        # Wenn das angeklickte Element bereits ausgewählt war, hebe die Auswahl auf
        if item in self.archived_calls_tree.selection():
            self.archived_calls_tree.selection_remove(item)
            return
            
        # Ansonsten: Neues Tag für die Auswahl anwenden
        current_tags = list(self.archived_calls_tree.item(item, "tags"))
        
        # Setze das entsprechende Auswahl-Tag basierend auf der Zeilenfarbe
        if "row_green" in current_tags:
            current_tags.append("selected_green")
        elif "row_red" in current_tags:
            current_tags.append("selected_red")
            
        # Auswahl setzen
        self.archived_calls_tree.selection_set(item)
        self.archived_calls_tree.item(item, tags=tuple(current_tags))
        
        # Nach jeder Auswahländerung neu zeichnen, um sicherzustellen, dass die Tags sichtbar sind
        self.archived_calls_tree.update()
        
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