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

    # Treeview-Styling
    style.configure("Treeview", 
                    background="white",
                    fieldbackground="white",
                    font=("Arial", 9))
    
    style.configure("Treeview.Heading",
                    font=("Arial", 9, "bold"))
    
    # Tag-Konfigurationen für Treeview
    style.map("Treeview", 
              background=[("selected", "#e0e0e0")])

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
    entry = tk.Entry(parent, textvariable=var, state="readonly")
    entry.grid(row=row, column=1, padx=5, pady=2, sticky="ew")
    
    if show_copy_button:
        btn = tk.Button(parent, text="Kopieren", command=lambda: clipboard.copy_to_clipboard(parent.winfo_toplevel(), var.get()))
        btn.grid(row=row, column=2, padx=5, pady=2)

def create_link_row(parent, label_text, var, row):
    """
    Wie create_data_row, aber Button "Aufrufen" öffnet den Link im Browser.
    """
    import utils.browser as browser
    
    lbl = tk.Label(parent, text=label_text, font=("Arial", 10, "bold"), anchor="w")
    lbl.grid(row=row, column=0, padx=5, pady=2, sticky="w")

    entry = tk.Entry(parent, textvariable=var, state="readonly")
    entry.grid(row=row, column=1, padx=5, pady=2, sticky="ew")

    btn = tk.Button(parent, text="Aufrufen", command=lambda: browser.open_link(var.get()))
    btn.grid(row=row, column=2, padx=5, pady=2)