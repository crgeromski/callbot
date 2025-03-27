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


def create_link_row(parent, label_text, var, row, token_name_var=None, is_website=False):
    """
    Wie create_data_row, aber Button "🔗" öffnet den Link im Browser.
    Entry wird farblich markiert: 
    - grün, wenn Link vorhanden und (bei Website) der Token-Name im Domain-Teil des Links enthalten ist
    - gelb, wenn Link vorhanden, aber (bei Website) der Token-Name nicht im Domain-Teil des Links enthalten ist
    - rot wenn "N/A" oder leerer Link
    Das http:// oder https:// wird in der Anzeige ausgeblendet.
    """
    import utils.browser as browser
    import utils.formatters as formatters
    
    lbl = tk.Label(parent, text=label_text, font=("Arial", 10, "bold"), anchor="w")
    lbl.grid(row=row, column=0, padx=5, pady=2, sticky="w")

    # Erstelle ein neues StringVar für die formatierte Anzeige
    display_var = tk.StringVar(parent)
    
    entry = tk.Entry(parent, textvariable=display_var, state="readonly")
    entry.grid(row=row, column=1, padx=5, pady=2, sticky="ew")

    # Farbanpassung und Formatierung basierend auf dem Wert
    def update_entry(*args):
        value = var.get()
        # Formatiere den Link für die Anzeige (ohne http://, https://)
        formatted_value = formatters.format_url(value)
        display_var.set(formatted_value)
        
        if value and value != "N/A":
            # Standardfarbe für vorhandenen Link
            bg_color = "#d8ffd8"  # Grün
            
            # Für Website-Links: Prüfe, ob Token-Name enthalten ist
            if is_website and token_name_var:
                token_name = token_name_var.get()
                token_symbol = None
                
                # Versuche, den Symbol-Text zu bekommen (ohne $)
                if parent.winfo_toplevel().__dict__.get('shared_vars'):
                    symbol_var = parent.winfo_toplevel().__dict__['shared_vars'].get('token_symbol_var')
                    if symbol_var:
                        token_symbol = symbol_var.get()
                        if token_symbol and token_symbol.startswith('$'):
                            token_symbol = token_symbol[1:]  # Entferne das $ am Anfang
                
                # Extrahiere nur den Domainnamen für den Vergleich
                import re
                domain_part = formatted_value
                # Schneide alles nach dem ersten Schrägstrich ab
                if '/' in domain_part:
                    domain_part = domain_part.split('/', 1)[0]
                
                # Liste bekannter Social-Media und Video-Plattformen
                known_platforms = [
                    'tiktok.com', 'twitter.com', 'x.com', 'youtube.com', 
                    'instagram.com', 'facebook.com', 'pinterest.com',
                    'linkedin.com', 'snapchat.com', 'reddit.com',
                    'twitch.tv', 'vimeo.com', 'dailymotion.com',
                    'tumblr.com', 'flickr.com', 'medium.com',
                    'quora.com', 'discord.com', 'telegram.org',
                    'whatsapp.com', 'wechat.com', 'line.me'
                ]
                
                # Überprüfe, ob es sich um eine bekannte Plattform handelt
                is_known_platform = any(platform in domain_part.lower() for platform in known_platforms)
                website_lower = domain_part.lower()
                
                # Für bekannte Plattformen immer gelb, da es keine "eigene" Website ist
                if is_known_platform:
                    bg_color = "#fff3cd"  # Gelb für Warnung
                # Für andere Websites prüfen, ob der Name im Domain-Teil enthalten ist
                else:
                    # Prüfe verschiedene Varianten des Token-Namens
                    name_in_domain = False
                    
                    if token_name and token_name != "N/A":
                        # Versuche verschiedene Formatierungen des Namens
                        token_variants = []
                        
                        # Originaler Token-Name
                        token_variants.append(token_name.lower())
                        
                        # Ohne Leerzeichen
                        token_variants.append(token_name.lower().replace(" ", ""))
                        
                        # Symbol (falls vorhanden)
                        if token_symbol and token_symbol != "N/A":
                            token_variants.append(token_symbol.lower())
                        
                        # Prüfe jede Variante
                        for variant in token_variants:
                            if variant in website_lower:
                                name_in_domain = True
                                break
                        
                        if not name_in_domain:
                            bg_color = "#fff3cd"  # Gelb für Warnung
            
            entry.config(readonlybackground=bg_color)
        else:
            entry.config(readonlybackground="#ffd8d8")  # Rot für N/A oder leeren String
    
    # Trace hinzufügen, um auf Änderungen zu reagieren
    var.trace_add("write", update_entry)
    
    # Wenn es sich um eine Website handelt und der Token-Name verfügbar ist,
    # reagiere auch auf Änderungen des Token-Namens
    if is_website and token_name_var:
        token_name_var.trace_add("write", update_entry)
    
    # Initial formatieren und färben
    update_entry()

    btn = tk.Button(parent, text="🔗", width=2, command=lambda: browser.open_link(var.get()))
    btn.grid(row=row, column=2, padx=5, pady=2)
    