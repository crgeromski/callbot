# Verbesserte Axiom API-Funktionen
import requests
from typing import Dict, Any, Optional
import config
import re
import time

def fetch_axiom_data(token_address: str, timeout: int = 30) -> Optional[Dict[str, Any]]:
    """
    Ruft Daten von der Axiom API für eine Token-Adresse ab.
    
    Args:
        token_address: Die Token-Adresse (bei Solana ohne Präfix)
        timeout: Timeout in Sekunden
    
    Returns:
        Die API-Antwortdaten als Dictionary oder None bei Fehler
    """
    # Stelle sicher, dass die Adresse kein Solana-Präfix enthält
    token_address = token_address.strip()
    if token_address.lower().startswith("sol:"):
        token_address = token_address[4:]
    
    # API-Endpunkt für Token-Daten
    api_url = f"https://api.solanatracker.io/tokens/{token_address}"
    
    # Headers mit API-Key
    headers = {
        "X-API-KEY": config.AXIOM_API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        # Verwende Session für bessere Performance
        session = requests.Session()
        
        # Setze optionale Konfiguration für eine robustere Verbindung
        adapter = requests.adapters.HTTPAdapter(
            max_retries=3,  # Versuche 3 Mal, wenn die Verbindung fehlschlägt
            pool_connections=10,
            pool_maxsize=10
        )
        session.mount('https://', adapter)
        
        # Führe die Anfrage durch
        resp = session.get(api_url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.Timeout:
        print(f"Axiom API-Timeout: Die Anfrage hat die Zeitbeschränkung von {timeout} Sekunden überschritten.")
        return None
    except requests.exceptions.ConnectionError:
        print("Axiom API-Verbindungsfehler: Konnte keine Verbindung zum Server herstellen.")
        return None
    except Exception as e:
        print(f"Axiom API-Fehler: {e}")
        return None

def fetch_top_holders(token_address: str, timeout: int = 30) -> Optional[Dict[str, Any]]:
    """
    Ruft die Top-Holder für eine Token-Adresse ab.
    
    Args:
        token_address: Die Token-Adresse (bei Solana ohne Präfix)
        timeout: Timeout in Sekunden
    
    Returns:
        Die API-Antwortdaten als Dictionary oder None bei Fehler
    """
    # Stelle sicher, dass die Adresse kein Solana-Präfix enthält
    token_address = token_address.strip()
    if token_address.lower().startswith("sol:"):
        token_address = token_address[4:]
    
    # API-Endpunkt für Top-Holder
    api_url = f"https://api.solanatracker.io/tokens/{token_address}/holders/top"
    
    # Headers mit API-Key
    headers = {
        "X-API-KEY": config.AXIOM_API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        # Verwende Session für bessere Performance
        session = requests.Session()
        
        # Setze optionale Konfiguration für eine robustere Verbindung
        adapter = requests.adapters.HTTPAdapter(
            max_retries=3,  # Versuche 3 Mal, wenn die Verbindung fehlschlägt
            pool_connections=10,
            pool_maxsize=10
        )
        session.mount('https://', adapter)
        
        # Führe die Anfrage durch
        resp = session.get(api_url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.Timeout:
        print(f"Axiom API-Timeout (Top-Holder): Die Anfrage hat die Zeitbeschränkung von {timeout} Sekunden überschritten.")
        return None
    except requests.exceptions.ConnectionError:
        print("Axiom API-Verbindungsfehler (Top-Holder): Konnte keine Verbindung zum Server herstellen.")
        return None
    except Exception as e:
        print(f"Axiom API-Fehler (Top-Holder): {e}")
        return None

def fetch_top_traders(token_address: str, timeout: int = 30) -> Optional[Dict[str, Any]]:
    """
    Ruft die Top-Trader für eine Token-Adresse ab.
    
    Args:
        token_address: Die Token-Adresse (bei Solana ohne Präfix)
        timeout: Timeout in Sekunden
    
    Returns:
        Die API-Antwortdaten als Dictionary oder None bei Fehler
    """
    # Stelle sicher, dass die Adresse kein Solana-Präfix enthält
    token_address = token_address.strip()
    if token_address.lower().startswith("sol:"):
        token_address = token_address[4:]
    
    # API-Endpunkt für Top-Trader
    api_url = f"https://api.solanatracker.io/top-traders/{token_address}"
    
    # Headers mit API-Key
    headers = {
        "X-API-KEY": config.AXIOM_API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        # Verwende Session für bessere Performance
        session = requests.Session()
        
        # Setze optionale Konfiguration für eine robustere Verbindung
        adapter = requests.adapters.HTTPAdapter(
            max_retries=3,  # Versuche 3 Mal, wenn die Verbindung fehlschlägt
            pool_connections=10,
            pool_maxsize=10
        )
        session.mount('https://', adapter)
        
        # Führe die Anfrage durch
        resp = session.get(api_url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.Timeout:
        print(f"Axiom API-Timeout (Top-Trader): Die Anfrage hat die Zeitbeschränkung von {timeout} Sekunden überschritten.")
        return None
    except requests.exceptions.ConnectionError:
        print("Axiom API-Verbindungsfehler (Top-Trader): Konnte keine Verbindung zum Server herstellen.")
        return None
    except Exception as e:
        print(f"Axiom API-Fehler (Top-Trader): {e}")
        return None

def test_api_key() -> bool:
    """
    Testet, ob der API-Key funktioniert, indem ein bekannter Token abgefragt wird.
    
    Returns:
        True, wenn der API-Key funktioniert, sonst False
    """
    # Wir verwenden einen bekannten Solana-Token als Test
    test_token = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC auf Solana
    
    try:
        # Erhöhter Timeout für den Test
        timeout = 15
        
        # Verwende Session für bessere Performance
        session = requests.Session()
        
        # Setze optionale Konfiguration für eine robustere Verbindung
        adapter = requests.adapters.HTTPAdapter(
            max_retries=2,  # Bei Tests weniger Versuche
            pool_connections=5,
            pool_maxsize=5
        )
        session.mount('https://', adapter)
        
        # Headers mit API-Key
        headers = {
            "X-API-KEY": config.AXIOM_API_KEY,
            "Content-Type": "application/json"
        }
        
        # Führe die Anfrage durch
        resp = session.get(f"https://api.solanatracker.io/tokens/{test_token}", 
                          headers=headers, timeout=timeout)
        
        return resp.status_code == 200
    except Exception as e:
        print(f"API-Key Test Fehler: {e}")
        return False
    
def is_solana_address_format(address: str) -> bool:
    """
    Prüft, ob eine Adresse das Format einer Solana-Adresse hat.
    
    Args:
        address: Die zu prüfende Adresse
    
    Returns:
        True, wenn es eine gültige Solana-Adresse sein könnte, sonst False
    """
    if not address:
        return False
        
    address = address.strip()
    
    # Wenn die Adresse mit "sol:" beginnt, entferne das Präfix
    if address.lower().startswith("sol:"):
        address = address[4:]
    
    # Solana-Adressen sind Base58-Encoded und haben 32-44 Zeichen
    if len(address) < 32 or len(address) > 44:
        return False
    
    # Base58-Zeichen sind: Zahlen (ohne 0), Buchstaben (ohne O, I, l)
    base58_chars = set("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")
    return all(char in base58_chars for char in address)