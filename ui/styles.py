# UI-Styling
import tkinter as tk
from tkinter import ttk

def setup_styles():
    """Richtet die ttk Styles ein."""
    style = ttk.Style()
    style.theme_use("clam")

    # Notebook-Tab-Layout
    style.layout("TNotebook.Tab", [
        ("Notebook.tab", {
            "sticky": "nswe",
            "children": [
                ("Notebook.padding", {
                    "side": "top",
                    "sticky": "nswe",
                    "children": [
                        ("Notebook.label", {"side": "left", "sticky": ""})
                    ]
                })
            ]
        })
    ])

    # Notebook-Styling
    style.configure("TNotebook",
                    background="white",
                    borderwidth=0,
                    tabmargins=[10, 5, 10, 0])

    style.configure("TNotebook.Tab",
                    font=("Arial", 12, "bold"))

    style.map("TNotebook.Tab",
        padding=[("selected", [15, 10]), ("!selected", [10, 6])],
        background=[("selected", "white"), ("!selected", "#dddddd")],
        foreground=[("selected", "black"), ("!selected", "black")]
    )

    # Treeview-Styling mit sehr hellem Auswahlhintergrund
    style.configure("Treeview", 
                   background="white",
                   fieldbackground="white",
                   font=("Arial", 9))
    
    style.configure("Treeview.Heading",
                   font=("Arial", 9, "bold"))
    
    # Deaktiviere die Standard-Auswahlfarben, damit unsere Tags wirksam werden
    style.map("Treeview", 
        background=[('selected', '')],  # Leere Farbe für Auswahl
        foreground=[('selected', 'black')])  # Textfarbe bleibt schwarz

def create_data_row(parent, label_text, var, row, show_copy_button=True):
    """
    Legt eine Label+Entry+Button-Zeile in einem Grid-Parent an.
    parent: Frame, der grid verwendet.
    label_text: Beschriftung
    var: StringVar zum Anzeigen
    row: Zeilennummer in der grid
    show_copy_button: Ob der Kopieren-Button angezeigt werden soll
    """
    import utils.clipboard as clipboard
    
    lbl = tk.Label(parent, text=label_text, font=("Arial", 10, "bold"), anchor="w")
    lbl.grid(row=row, column=0, padx=5, pady=2, sticky="w")
    
    # Prüfe, ob es sich um Token-Daten oder Statistiken handelt (basierend auf dem Label-Text)
    if any(keyword in label_text.lower() for keyword in ["blockchain", "token", "symbol", "adresse", "market cap", "liquidity", "volumen"]):
        # Token-Daten und Statistiken fett darstellen
        entry = tk.Entry(parent, textvariable=var, state="readonly", font=("Arial", 10, "bold"))
    else:
        # Alle anderen Felder normal darstellen
        entry = tk.Entry(parent, textvariable=var, state="readonly")
    
    entry.grid(row=row, column=1, padx=5, pady=2, sticky="ew")
    
    if show_copy_button:
        btn = tk.Button(parent, text="📋", width=2, command=lambda: clipboard.copy_to_clipboard(parent.winfo_toplevel(), var.get()))
        btn.grid(row=row, column=2, padx=5, pady=2)


def create_link_row(parent, label_text, var, row):
    """
    Wie create_data_row, aber Button "🔗" öffnet den Link im Browser.
    Entry wird farblich markiert: grün, wenn Link vorhanden, rot wenn "N/A".
    """
    import utils.browser as browser
    
    lbl = tk.Label(parent, text=label_text, font=("Arial", 10, "bold"), anchor="w")
    lbl.grid(row=row, column=0, padx=5, pady=2, sticky="w")

    entry = tk.Entry(parent, textvariable=var, state="readonly")

    entry.grid(row=row, column=1, padx=5, pady=2, sticky="ew")

    # Farbanpassung basierend auf dem Wert
    def update_entry_color(*args):
        value = var.get()
        if value and value != "N/A":
            entry.config(readonlybackground="#d8ffd8")  # Grün für vorhandenen Link
        else:
            entry.config(readonlybackground="#ffd8d8")  # Rot für N/A oder leeren String
    
    # Trace hinzufügen, um auf Änderungen zu reagieren
    var.trace_add("write", update_entry_color)
    
    # Initial färben
    update_entry_color()

    btn = tk.Button(parent, text="🔗", width=2, command=lambda: browser.open_link(var.get()))
    btn.grid(row=row, column=2, padx=5, pady=2)