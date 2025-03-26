# API-Funktionen
import requests
from typing import Dict, Any, Optional

def convert_to_api_link(url_or_address: str) -> str:
    """
    Konvertiert einen Dexscreener-Weblink oder eine Contract-Adresse in den API-Link.
    
    Die Funktion unterstützt:
    - Dexscreener-Links (https://dexscreener.com/...)
    - Contract-Adressen (z.B. 9ZpzuppLqYiamNRKnMzeShWTe3iEhV8gousCh5jmpump)
    - Bereits konvertierte API-Links (https://api.dexscreener.com/...)
    """
    url_or_address = url_or_address.strip()
    
    # Fall 1: Es ist bereits ein API-Link
    if url_or_address.startswith("https://api.dexscreener.com/"):
        return url_or_address
    
    # Fall 2: Es ist ein Dexscreener-Link
    if "https://dexscreener.com/" in url_or_address:
        parts = url_or_address.split("dexscreener.com/")
        if len(parts) > 1:
            return "https://api.dexscreener.com/latest/dex/pairs/" + parts[1]
    
    # Fall 3: Es ist eine Contract-Adresse (ohne http oder https)
    if not url_or_address.startswith("http"):
        # Wir nehmen an, dass es eine Contract-Adresse ist
        return f"https://api.dexscreener.com/latest/dex/tokens/{url_or_address}"
    
    # Fallback: Gib den Eingabestring unverändert zurück
    return url_or_address

def fetch_dexscreener_data(link: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
    """
    Ruft Daten von der Dexscreener-API ab.
    
    Args:
        link: Ein Dexscreener-Link oder eine Token-Adresse
        timeout: Timeout in Sekunden
    
    Returns:
        Die API-Antwortdaten als Dictionary oder None bei Fehler
    """
    api_link = convert_to_api_link(link)
    try:
        resp = requests.get(api_link, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"API-Fehler: {e}")
        return None