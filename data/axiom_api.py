# Axiom API-Funktionen
import requests
from typing import Dict, Any, Optional
import config
import re

def fetch_axiom_data(token_address: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
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
        resp = requests.get(api_url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Axiom API-Fehler: {e}")
        return None

def fetch_top_holders(token_address: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
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
        resp = requests.get(api_url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Axiom API-Fehler (Top-Holder): {e}")
        return None

def fetch_top_traders(token_address: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
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
        resp = requests.get(api_url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Axiom API-Fehler (Top-Trader): {e}")
        return None

def extract_rugcheck_metrics(token_data: Dict[str, Any], holders_data: Optional[Dict[str, Any]] = None, 
                            traders_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Extrahiert die RugCheck-Metriken aus den Axiom API-Daten.
    
    Args:
        token_data: Die Token-Daten von der Axiom API
        holders_data: Optional, die Top-Holder-Daten
        traders_data: Optional, die Top-Trader-Daten
    
    Returns:
        Ein Dictionary mit den RugCheck-Metriken
    """
    metrics = {
        "top_10_holders_percent": 0.0,  # Prozentsatz des Supplies, das die Top 10 Holder besitzen
        "dev_holdings_percent": 0.0,    # Prozentsatz des Supplies, das der Entwickler hält
        "snipers_holdings_percent": 0.0, # Prozentsatz des Supplies, das Sniper halten (vereinfacht)
        "insiders_percent": 0.0,        # Prozentsatz des Supplies, das Insider halten
        "bundlers_percent": 0.0,        # Prozentsatz des Supplies, das Bundler halten
        "lp_burned_percent": 0.0,       # Prozentsatz der LP-Token, die verbrannt wurden
        "holders_count": 0,             # Anzahl der Holder
        "pro_traders_count": 0,         # Anzahl der Pro-Trader
        "dex_paid": False,              # Ob für den Token bezahlte Werbung geschaltet wurde
    }
    
    # 1. Top 10 Holders Prozentsatz
    if holders_data and "holders" in holders_data:
        top_10_holders = holders_data["holders"][:10] if len(holders_data["holders"]) >= 10 else holders_data["holders"]
        top_10_percent = sum(holder.get("percentage", 0) for holder in top_10_holders)
        metrics["top_10_holders_percent"] = round(top_10_percent, 2)
    
    # 2. Holders Count
    metrics["holders_count"] = token_data.get("holders", 0)
    
    # 3. LP Burned Prozentsatz
    if "pools" in token_data and token_data["pools"]:
        main_pool = token_data["pools"][0]  # Hauptpool
        metrics["lp_burned_percent"] = main_pool.get("lpBurn", 0)
    
    # 4. Deployer/Dev Holdings
    if "pools" in token_data and token_data["pools"]:
        main_pool = token_data["pools"][0]
        deployer_address = main_pool.get("deployer", "")
        
        if deployer_address and holders_data and "holders" in holders_data:
            for holder in holders_data["holders"]:
                if holder.get("address") == deployer_address:
                    metrics["dev_holdings_percent"] = round(holder.get("percentage", 0), 2)
                    break
    
    # 5. Bundlers
    if "pools" in token_data and token_data["pools"]:
        main_pool = token_data["pools"][0]
        if main_pool.get("bundleId") or main_pool.get("market") == "pumpfun":
            # Vereinfachte Annahme: Wenn es ein Pump.fun-Launch war, setzen wir einen Standardwert
            # In der Realität müsste man die tatsächlichen Bundler identifizieren
            metrics["bundlers_percent"] = round(5.0, 2)  # Platzhalter - in Realität komplexere Logik notwendig
    
    # 6. Pro Traders
    if traders_data and isinstance(traders_data, list):
        metrics["pro_traders_count"] = len(traders_data)
    
    # 7. Snipers & Insiders (vereinfachte Annahme basierend auf frühen Transaktionen)
    # Hier würden wir normalerweise eine komplexere Logik implementieren,
    # die auf Transaktionshistorie und zeitlichen Mustern basiert
    # Für jetzt setzen wir Platzhalter-Werte
    metrics["snipers_holdings_percent"] = round(0.0, 2)  # Platzhalter
    metrics["insiders_percent"] = round(10.0, 2)  # Platzhalter
    
    # 8. Dex Paid Status
    # In der API nicht direkt verfügbar, könnte aus weiteren Quellen kommen
    # Für jetzt setzen wir einen Platzhalter-Wert
    metrics["dex_paid"] = False  # Platzhalter
    
    return metrics

def extract_address_from_url(url: str) -> Optional[str]:
    """
    Extrahiert eine Solana-Token-Adresse aus einer URL oder Zeichenkette.
    
    Args:
        url: Die URL oder Zeichenkette, die eine Solana-Token-Adresse enthält
    
    Returns:
        Die extrahierte Adresse oder None, wenn keine gefunden wurde
    """
    # 1. Wenn bereits eine reine Adresse, versuche direkt zu validieren
    if is_solana_address_format(url):
        return url
    
    # 2. Versuche, Adressen aus URLs zu extrahieren
    
    # DexScreener-URLs können verschiedene Formate haben
    if "dexscreener.com" in url:
        # Format: https://dexscreener.com/solana/ANYxxxx
        parts = url.split('/')
        for part in parts:
            if is_solana_address_format(part):
                return part
    
    # Extrahiere jedes mögliche Token, das wie eine Solana-Adresse aussieht
    potential_addresses = re.findall(r'[1-9A-HJ-NP-Za-km-z]{32,44}', url)
    
    # Wenn gefunden, gib die erste zurück
    if potential_addresses:
        return potential_addresses[0]
    
    return None

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

def test_api_key() -> bool:
    """
    Testet, ob der API-Key funktioniert, indem ein bekannter Token abgefragt wird.
    
    Returns:
        True, wenn der API-Key funktioniert, sonst False
    """
    # Wir verwenden einen bekannten Solana-Token als Test
    test_token = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC auf Solana
    
    try:
        headers = {
            "X-API-KEY": config.AXIOM_API_KEY,
            "Content-Type": "application/json"
        }
        
        resp = requests.get(f"https://api.solanatracker.io/tokens/{test_token}", 
                          headers=headers, timeout=5)
        
        return resp.status_code == 200
    except Exception:
        return False