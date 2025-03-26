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