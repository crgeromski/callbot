# Verbesserte Axiom API-Funktionen mit detailliertem Fehlerprotokoll
import requests
from typing import Dict, Any, Optional, List, Tuple
import config
import re
import time
import logging

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('axiom_api.log')
    ]
)
logger = logging.getLogger("axiom_api")

def fetch_axiom_data(token_address: str, timeout: int = 30) -> Optional[Dict[str, Any]]:
    """
    Ruft Daten von der Axiom API für eine Token-Adresse ab.
    
    Args:
        token_address: Die Token-Adresse (bei Solana ohne Präfix)
        timeout: Timeout in Sekunden
    
    Returns:
        Die API-Antwortdaten als Dictionary oder None bei Fehler
    """
    # Protokolliere Anfang des API-Aufrufs
    logger.info(f"Starte API-Anfrage für Token: {token_address}")
    
    # Stelle sicher, dass die Adresse kein Solana-Präfix enthält
    token_address = token_address.strip()
    if token_address.lower().startswith("sol:"):
        token_address = token_address[4:]
        logger.info(f"Entferne 'sol:'-Präfix. Neue Adresse: {token_address}")
    
    # Protokolliere API-Key (erste 4 Zeichen für Diagnose)
    api_key = config.AXIOM_API_KEY
    api_key_start = api_key[:4] + "..." if api_key else "None"
    logger.info(f"API-Key (Anfang): {api_key_start}")
    
    if not api_key:
        logger.error("Kein API-Key definiert!")
        return None
    
    # API-Endpunkt für Token-Daten
    api_url = f"https://api.solanatracker.io/tokens/{token_address}"
    logger.info(f"API-URL: {api_url}")
    
    # Headers mit API-Key
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }
    
    start_time = time.time()
    logger.info("Sende Anfrage...")
    
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
        elapsed = time.time() - start_time
        logger.info(f"Antwort erhalten in {elapsed:.2f}s mit Status: {resp.status_code}")
        
        # Überprüfe den Status
        resp.raise_for_status()
        
        # Versuche, die JSON-Daten zu parsen
        data = resp.json()
        logger.info(f"Daten erfolgreich abgerufen und geparst.")
        return data
        
    except requests.exceptions.Timeout:
        logger.error(f"Axiom API-Timeout: Die Anfrage hat die Zeitbeschränkung von {timeout} Sekunden überschritten.")
        return None
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Axiom API-Verbindungsfehler: Konnte keine Verbindung zum Server herstellen. Details: {str(e)}")
        return None
    except requests.exceptions.HTTPError as e:
        logger.error(f"Axiom API-HTTP-Fehler: {str(e)}")
        return None
    except ValueError as e:
        logger.error(f"Axiom API-JSON-Parsing-Fehler: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Axiom API-Fehler: {str(e)}", exc_info=True)
        return None
    finally:
        end_time = time.time()
        logger.info(f"API-Anfrage abgeschlossen in {end_time - start_time:.2f}s")

def fetch_top_holders(token_address: str, timeout: int = 30) -> Optional[Dict[str, Any]]:
    """
    Ruft die Top-Holder für eine Token-Adresse ab.
    
    Args:
        token_address: Die Token-Adresse (bei Solana ohne Präfix)
        timeout: Timeout in Sekunden
    
    Returns:
        Die API-Antwortdaten als Dictionary oder None bei Fehler
    """
    logger.info(f"Hole Top-Holder für Token: {token_address}")
    
    # Stelle sicher, dass die Adresse kein Solana-Präfix enthält
    token_address = token_address.strip()
    if token_address.lower().startswith("sol:"):
        token_address = token_address[4:]
    
    # API-Endpunkt für Top-Holder
    api_url = f"https://api.solanatracker.io/tokens/{token_address}/holders/top"
    logger.info(f"Top-Holder API-URL: {api_url}")
    
    # Headers mit API-Key
    headers = {
        "X-API-KEY": config.AXIOM_API_KEY,
        "Content-Type": "application/json"
    }
    
    start_time = time.time()
    try:
        # Verwende Session für bessere Performance
        session = requests.Session()
        
        # Setze optionale Konfiguration für eine robustere Verbindung
        adapter = requests.adapters.HTTPAdapter(
            max_retries=3,
            pool_connections=10,
            pool_maxsize=10
        )
        session.mount('https://', adapter)
        
        # Führe die Anfrage durch
        logger.info("Sende Anfrage für Top-Holder...")
        resp = session.get(api_url, headers=headers, timeout=timeout)
        elapsed = time.time() - start_time
        logger.info(f"Top-Holder Antwort erhalten in {elapsed:.2f}s mit Status: {resp.status_code}")
        
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.Timeout:
        logger.error(f"Axiom API-Timeout (Top-Holder): Die Anfrage hat die Zeitbeschränkung von {timeout} Sekunden überschritten.")
        return None
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Axiom API-Verbindungsfehler (Top-Holder): Konnte keine Verbindung zum Server herstellen. Details: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Axiom API-Fehler (Top-Holder): {str(e)}", exc_info=True)
        return None
    finally:
        end_time = time.time()
        logger.info(f"Top-Holder API-Anfrage abgeschlossen in {end_time - start_time:.2f}s")

def fetch_top_traders(token_address: str, timeout: int = 30) -> Optional[Dict[str, Any]]:
    """
    Ruft die Top-Trader für eine Token-Adresse ab.
    
    Args:
        token_address: Die Token-Adresse (bei Solana ohne Präfix)
        timeout: Timeout in Sekunden
    
    Returns:
        Die API-Antwortdaten als Dictionary oder None bei Fehler
    """
    logger.info(f"Hole Top-Trader für Token: {token_address}")
    
    # Stelle sicher, dass die Adresse kein Solana-Präfix enthält
    token_address = token_address.strip()
    if token_address.lower().startswith("sol:"):
        token_address = token_address[4:]
    
    # API-Endpunkt für Top-Trader
    api_url = f"https://api.solanatracker.io/top-traders/{token_address}"
    logger.info(f"Top-Trader API-URL: {api_url}")
    
    # Headers mit API-Key
    headers = {
        "X-API-KEY": config.AXIOM_API_KEY,
        "Content-Type": "application/json"
    }
    
    start_time = time.time()
    try:
        # Verwende Session für bessere Performance
        session = requests.Session()
        
        # Setze optionale Konfiguration für eine robustere Verbindung
        adapter = requests.adapters.HTTPAdapter(
            max_retries=3,
            pool_connections=10,
            pool_maxsize=10
        )
        session.mount('https://', adapter)
        
        # Führe die Anfrage durch
        logger.info("Sende Anfrage für Top-Trader...")
        resp = session.get(api_url, headers=headers, timeout=timeout)
        elapsed = time.time() - start_time
        logger.info(f"Top-Trader Antwort erhalten in {elapsed:.2f}s mit Status: {resp.status_code}")
        
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.Timeout:
        logger.error(f"Axiom API-Timeout (Top-Trader): Die Anfrage hat die Zeitbeschränkung von {timeout} Sekunden überschritten.")
        return None
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Axiom API-Verbindungsfehler (Top-Trader): Konnte keine Verbindung zum Server herstellen. Details: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Axiom API-Fehler (Top-Trader): {str(e)}", exc_info=True)
        return None
    finally:
        end_time = time.time()
        logger.info(f"Top-Trader API-Anfrage abgeschlossen in {end_time - start_time:.2f}s")

def test_api_key() -> bool:
    """
    Testet, ob der API-Key funktioniert, indem ein bekannter Token abgefragt wird.
    
    Returns:
        True, wenn der API-Key funktioniert, sonst False
    """
    logger.info("Teste API-Key...")
    
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
        logger.info(f"Sende API-Key Test-Anfrage für Token: {test_token}")
        start_time = time.time()
        resp = session.get(f"https://api.solanatracker.io/tokens/{test_token}", 
                          headers=headers, timeout=timeout)
        elapsed = time.time() - start_time
        
        logger.info(f"API-Key Test-Antwort erhalten in {elapsed:.2f}s mit Status: {resp.status_code}")
        result = resp.status_code == 200
        logger.info(f"API-Key Test Ergebnis: {'Erfolg' if result else 'Fehlgeschlagen'}")
        return result
    except Exception as e:
        logger.error(f"API-Key Test Fehler: {str(e)}", exc_info=True)
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

def extract_address_from_url(url: str) -> Optional[str]:
    """
    Extrahiert eine Solana-Adresse aus einer URL.
    
    Args:
        url: Die URL, aus der die Adresse extrahiert werden soll
    
    Returns:
        Die extrahierte Adresse oder None, wenn keine gefunden wurde
    """
    if not url:
        return None
        
    # Versuche zuerst, einen Solana-Token aus der URL zu extrahieren
    sol_patterns = [
        r'solana/([a-zA-Z0-9]{32,44})',  # Für dexscreener.com/solana/ADDRESS
        r'solana/([a-zA-Z0-9]{32,44})/',  # Mit Schrägstrich am Ende
        r'/([a-zA-Z0-9]{32,44})$'  # Für Adressen am Ende der URL
    ]

    for pattern in sol_patterns:
        match = re.search(pattern, url)
        if match:
            address = match.group(1)
            if is_solana_address_format(address):
                return address
    
    return None

def extract_rugcheck_metrics(token_data: Optional[Dict], holders_data: Optional[Dict], traders_data: Optional[Dict]) -> Dict[str, Any]:
    """
    Extrahiert Metriken für den RugCheck aus den API-Antworten.
    
    Args:
        token_data: Token-Basis-Daten
        holders_data: Daten über Token-Holder
        traders_data: Daten über Token-Trader
    
    Returns:
        Dictionary mit extrahierten Metriken
    """
    result = {
        "top_10_holders_percent": 0.0,  # Prozentsatz der Token, die von den Top 10 gehalten werden
        "dev_holdings_percent": 0.0,     # Prozentsatz der Token, die vom Entwickler gehalten werden
        "snipers_holdings_percent": 0.0,  # Prozentsatz der Token, die von Snipern gehalten werden
        "insiders_percent": 0.0,          # Prozentsatz der Insider
        "bundlers_percent": 0.0,          # Prozentsatz der Bundler
        "lp_burned_percent": 0.0,         # Prozentsatz der verbrannten LP-Token
        "holders_count": 0,               # Anzahl der Token-Holder
        "pro_traders_count": 0,           # Anzahl der Pro-Trader
        "dex_paid": False                 # Wurde die Dex-Gebühr bezahlt?
    }
    
    # Token-Basisdaten verarbeiten
    if token_data and isinstance(token_data, dict):
        # Holder-Anzahl 
        result["holders_count"] = token_data.get("holdersCount", 0)
        
        # LP Burned
        lp_data = token_data.get("liquidityPool", {})
        if isinstance(lp_data, dict):
            result["lp_burned_percent"] = lp_data.get("burnedPercent", 0.0)
            
        # Dex Paid
        result["dex_paid"] = token_data.get("isDexVerified", False)
    
    # Holder-Daten verarbeiten
    if holders_data and isinstance(holders_data, dict):
        top_holders = holders_data.get("data", [])
        
        if top_holders and len(top_holders) > 0:
            # Top 10 Holder Anteil
            top_10_percent = sum(h.get("percentage", 0.0) for h in top_holders[:10])
            result["top_10_holders_percent"] = top_10_percent
            
            # Entwickler-Anteile (vereinfacht)
            for holder in top_holders:
                if holder.get("isTeam", False) or holder.get("isDeveloper", False):
                    result["dev_holdings_percent"] += holder.get("percentage", 0.0)
                    
            # Sniper-Anteile (vereinfacht) 
            for holder in top_holders:
                if holder.get("isBot", False) or holder.get("isSniper", False):
                    result["snipers_holdings_percent"] += holder.get("percentage", 0.0)
            
            # Insider & Bundler (fiktiv)
            result["insiders_percent"] = 5.0  # Beispielwert
            result["bundlers_percent"] = 2.5  # Beispielwert
    
    # Trader-Daten verarbeiten
    if traders_data and isinstance(traders_data, dict):
        traders_list = traders_data.get("data", [])
        
        if traders_list and len(traders_list) > 0:
            # Pro-Trader zählen
            result["pro_traders_count"] = sum(1 for t in traders_list if t.get("isPro", False))
    
    return result

if __name__ == "__main__":
    # Direkter Aufruf zum Testen
    print("=== Axiom API Test ===")
    print("Test API-Key:", test_api_key())
    
    # Test mit einem bekannten Token (USDC)
    test_token = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    print(f"Teste fetch_axiom_data für {test_token}:")
    result = fetch_axiom_data(test_token)
    print("Ergebnis:", "Daten erhalten" if result else "Keine Daten")