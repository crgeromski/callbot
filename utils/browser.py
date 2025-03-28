# Browser-Funktionen
import webbrowser
import urllib.parse
import tkinter.messagebox as messagebox

def open_link(url):
    """Öffnet einen Link im Standard-Browser."""
    url = url.strip()
    if url.startswith("http"):
        webbrowser.open(url)
    else:
        messagebox.showerror("Fehler", f"Ungültiger Link: {url}")

def create_twitter_post_url(text):
    """Erstellt eine URL zum Posten auf Twitter/X."""
    if not text:
        return None
    
    enc = urllib.parse.quote(text, safe="")
    return f"https://x.com/intent/tweet?text={enc}"

def create_memehunter_call_search_url(token_address):
    """
    Erstellt eine Such-URL für MemeHunter Calls mit gegebener Token-Adresse.
    
    Args:
        token_address (str): Die Token-Adresse 
    
    Returns:
        str: Die vollständige Such-URL auf X
    """
    if not token_address or token_address == "N/A":
        messagebox.showerror("Fehler", "Keine gültige Token-Adresse gefunden.")
        return None
    
    # URL-Enkodierung für die Suche
    search_query = urllib.parse.quote(f"from:@memehuntercalls {token_address}")
    return f"https://x.com/search?q={search_query}&src=typed_query&f=live"