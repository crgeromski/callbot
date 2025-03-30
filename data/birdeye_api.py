# Birdeye API Integration
import requests
import json
import time
import os
from typing import Dict, Any, List, Optional
import utils.formatters as formatters

# Standard-Wartezeit zwischen API-Aufrufen (in Sekunden)
DEFAULT_WAIT_TIME = 1.2  # Etwas mehr als 1 Sekunde wegen des Rate-Limits

# Cache-Ablaufzeit (in Sekunden)
CACHE_EXPIRY = 60  # 1 Minute

# API-Konfiguration
API_BASE_URL = "https://public-api.birdeye.so"
# Ändere den Pfad zum externen API-Key
API_KEY_FILE = r"C:\Users\Gerome PC\Desktop\callbot_github\api dateien\birdeye_api_key.txt"
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "accept": "application/json"
}

# Cache für API-Antworten
api_cache = {}
# Zeitpunkt des letzten API-Aufrufs
last_api_call = 0

def get_api_key() -> str:
    """
    Liest den API-Key aus der Datei oder fordert zur Eingabe auf,
    wenn keine Datei vorhanden ist.
    """
    try:
        if os.path.exists(API_KEY_FILE):
            with open(API_KEY_FILE, "r") as f:
                return f.read().strip()
        else:
            # Im Produktionscode würde hier ein Dialog angezeigt werden
            print("Birdeye API-Key nicht gefunden. Bitte in ui/api_key.txt speichern.")
            return ""
    except Exception as e:
        print(f"Fehler beim Lesen des API-Keys: {e}")
        return ""

def rate_limit_wait():
    """
    Wartet, um das Rate-Limit einzuhalten (1 Request pro Sekunde).
    """
    global last_api_call
    current_time = time.time()
    time_since_last_call = current_time - last_api_call
    
    if time_since_last_call < DEFAULT_WAIT_TIME and last_api_call > 0:
        wait_time = DEFAULT_WAIT_TIME - time_since_last_call
        time.sleep(wait_time)
    
    last_api_call = time.time()

def get_cached_or_fetch(cache_key: str, fetch_func, cache_expiry: int = CACHE_EXPIRY) -> Any:
    """
    Versucht, Daten aus dem Cache zu holen. Falls nicht vorhanden oder abgelaufen,
    ruft die fetch_func auf und speichert das Ergebnis im Cache.
    
    Args:
        cache_key: Der Schlüssel für den Cache-Eintrag
        fetch_func: Eine Funktion ohne Parameter, die die Daten von der API holt
        cache_expiry: Ablaufzeit des Cache in Sekunden
        
    Returns:
        Die Daten aus dem Cache oder von der API
    """
    global api_cache
    
    current_time = time.time()
    
    # Prüfe, ob der Schlüssel im Cache existiert und aktuell ist
    if cache_key in api_cache:
        cache_entry = api_cache[cache_key]
        if current_time - cache_entry["timestamp"] < cache_expiry:
            return cache_entry["data"]
    
    # Daten von der API holen
    try:
        data = fetch_func()
        
        # Speichere im Cache
        api_cache[cache_key] = {
            "data": data,
            "timestamp": current_time
        }
        
        return data
    except Exception as e:
        print(f"Fehler beim Abrufen der Daten für {cache_key}: {e}")
        return None

def get_token_info(token_address: str) -> Optional[Dict[str, Any]]:
    """
    Ruft Informationen zu einem Token ab.
    
    Args:
        token_address: Die Adresse des Tokens
        
    Returns:
        Ein Dictionary mit Token-Informationen oder None bei Fehler
    """
    api_key = get_api_key()
    if not api_key:
        return None
    
    cache_key = f"token_info_{token_address}"
    
    def fetch_token_info():
        rate_limit_wait()
        url = f"{API_BASE_URL}/public/tokenlist"
        headers = DEFAULT_HEADERS.copy()
        headers["X-API-KEY"] = api_key
        
        params = {
            "address": token_address
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data
    
    return get_cached_or_fetch(cache_key, fetch_token_info)

def get_token_price(token_address: str) -> Optional[Dict[str, Any]]:
    """
    Ruft den aktuellen Preis und andere Preisdaten eines Tokens ab.
    
    Args:
        token_address: Die Adresse des Tokens
        
    Returns:
        Ein Dictionary mit Preisdaten oder None bei Fehler
    """
    api_key = get_api_key()
    if not api_key:
        return None
    
    cache_key = f"token_price_{token_address}"
    
    def fetch_token_price():
        rate_limit_wait()
        url = f"{API_BASE_URL}/public/price"
        headers = DEFAULT_HEADERS.copy()
        headers["X-API-KEY"] = api_key
        
        params = {
            "address": token_address
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data
    
    return get_cached_or_fetch(cache_key, fetch_token_price)

def get_token_holders(token_address: str) -> Optional[Dict[str, Any]]:
    """
    Ruft Informationen zu den Token-Inhabern ab.
    
    Args:
        token_address: Die Adresse des Tokens
        
    Returns:
        Ein Dictionary mit Holder-Informationen oder None bei Fehler
    """
    api_key = get_api_key()
    if not api_key:
        return None
    
    cache_key = f"token_holders_{token_address}"
    
    def fetch_token_holders():
        rate_limit_wait()
        url = f"{API_BASE_URL}/public/holder_list"
        headers = DEFAULT_HEADERS.copy()
        headers["X-API-KEY"] = api_key
        
        params = {
            "token": token_address
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data
    
    return get_cached_or_fetch(cache_key, fetch_token_holders)

def get_token_historical_trades(token_address: str, limit: int = 100) -> Optional[Dict[str, Any]]:
    """
    Ruft die letzten Trades für einen Token ab.
    
    Args:
        token_address: Die Adresse des Tokens
        limit: Maximale Anzahl der abzurufenden Trades
        
    Returns:
        Ein Dictionary mit Trade-Informationen oder None bei Fehler
    """
    api_key = get_api_key()
    if not api_key:
        return None
    
    cache_key = f"token_trades_{token_address}_{limit}"
    
    def fetch_token_trades():
        rate_limit_wait()
        url = f"{API_BASE_URL}/defi/trades_token"
        headers = DEFAULT_HEADERS.copy()
        headers["X-API-KEY"] = api_key
        
        params = {
            "token_address": token_address,
            "limit": limit,
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data
    
    return get_cached_or_fetch(cache_key, fetch_token_trades, cache_expiry=30)  # Kürzere Ablaufzeit für Trades

def get_trending_tokens(limit: int = 100) -> Optional[Dict[str, Any]]:
    """
    Ruft eine Liste der aktuell trendenden Tokens ab.
    
    Args:
        limit: Maximale Anzahl der abzurufenden Tokens
        
    Returns:
        Ein Dictionary mit trendenden Tokens oder None bei Fehler
    """
    api_key = get_api_key()
    if not api_key:
        return None
    
    cache_key = f"trending_tokens_{limit}"
    
    def fetch_trending_tokens():
        rate_limit_wait()
        url = f"{API_BASE_URL}/public/trending_list"
        headers = DEFAULT_HEADERS.copy()
        headers["X-API-KEY"] = api_key
        
        params = {
            "limit": limit,
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data
    
    return get_cached_or_fetch(cache_key, fetch_trending_tokens, cache_expiry=300)  # 5 Minuten Ablaufzeit

def get_newly_added_tokens(limit: int = 100) -> Optional[Dict[str, Any]]:
    """
    Ruft eine Liste der zuletzt hinzugefügten Tokens ab.
    
    Args:
        limit: Maximale Anzahl der abzurufenden Tokens
        
    Returns:
        Ein Dictionary mit neuen Tokens oder None bei Fehler
    """
    api_key = get_api_key()
    if not api_key:
        return None
    
    cache_key = f"new_tokens_{limit}"
    
    def fetch_new_tokens():
        rate_limit_wait()
        url = f"{API_BASE_URL}/public/newly_added_list"
        headers = DEFAULT_HEADERS.copy()
        headers["X-API-KEY"] = api_key
        
        params = {
            "limit": limit,
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data
    
    return get_cached_or_fetch(cache_key, fetch_new_tokens, cache_expiry=300)  # 5 Minuten Ablaufzeit

def analyze_token_for_strategy(token_address: str) -> Dict[str, Any]:
    """
    Analysiert einen Token nach den Kriterien der "Second Bounce Strategy".
    
    Args:
        token_address: Die Adresse des Tokens
        
    Returns:
        Ein Dictionary mit der Analyse und dem Score
    """
    result = {
        "token_address": token_address,
        "success": False,
        "token_info": None,
        "price_info": None,
        "volume_info": None,
        "holder_info": None,
        "trade_info": None,
        "score": {
            "pattern": 0,
            "volume": 0,
            "timeframe": 0,
            "rugpull": 0,
            "total": 0
        },
        "reasons": [],
        "potential": "→1X",
        "main_reason": "",
        "volume_trend": "→",
        "dip_detected": False,
        "bounce_detected": False
    }
    
    # Token-Infos abrufen
    token_info = get_token_info(token_address)
    if not token_info or "success" not in token_info or not token_info["success"]:
        result["reasons"].append("Token-Informationen nicht abrufbar")
        return result
    
    result["token_info"] = token_info
    
    # Preis-Infos abrufen
    price_info = get_token_price(token_address)
    if not price_info or "success" not in price_info or not price_info["success"]:
        result["reasons"].append("Preisinformationen nicht abrufbar")
        return result
    
    result["price_info"] = price_info
    
    # Holder-Infos abrufen
    holder_info = get_token_holders(token_address)
    if holder_info and "success" in holder_info and holder_info["success"]:
        result["holder_info"] = holder_info
    
    # Trade-Infos abrufen
    trade_info = get_token_historical_trades(token_address)
    if trade_info and "success" in trade_info and trade_info["success"]:
        result["trade_info"] = trade_info
    
    # Jetzt können wir mit der Analyse beginnen
    result["success"] = True
    
    # In einer vollständigen Implementierung würden hier die komplexen Analysen
    # und die Score-Berechnung für die vier Hauptkategorien stattfinden.
    # Für den Moment stellen wir einfache Platzhalter-Ergebnisse bereit.
    
    # Beispiel-Score (in einer realen Implementierung würde dies berechnet werden)
    pattern_score = 32  # Beispielwert, max 40
    volume_score = 25   # Beispielwert, max 35
    timeframe_score = 10  # Beispielwert, max 15
    rugpull_score = 8   # Beispielwert, max 10
    
    total_score = pattern_score + volume_score + timeframe_score + rugpull_score
    
    result["score"]["pattern"] = pattern_score
    result["score"]["volume"] = volume_score
    result["score"]["timeframe"] = timeframe_score
    result["score"]["rugpull"] = rugpull_score
    result["score"]["total"] = total_score
    
    # Potenzial basierend auf dem Score
    if total_score >= 85:
        result["potential"] = "→5X"
        result["volume_trend"] = "↑"
    elif total_score >= 75:
        result["potential"] = "→3X"
        result["volume_trend"] = "↑"
    elif total_score >= 70:
        result["potential"] = "→2X"
        result["volume_trend"] = "→"
    else:
        result["potential"] = "→1X"
        result["volume_trend"] = "↓"
    
    # Beispiel-Grund
    if pattern_score >= 30:
        result["main_reason"] = "Starkes Buy-Volumen im Dip"
        result["dip_detected"] = True
        result["bounce_detected"] = True
    elif volume_score >= 25:
        result["main_reason"] = "Stabilisierung nach Dip"
        result["dip_detected"] = True
    elif timeframe_score >= 10:
        result["main_reason"] = "Positiver 6H/24H Trend"
    else:
        result["main_reason"] = "Schwache Buy/Sell Ratio"
    
    return result

def scan_tokens_for_strategy(
    mcap_min: float = 100000,
    mcap_max: float = 3000000,
    liquidity_min: float = 30000,
    age_min: int = 0,
    age_max: int = 5,
    min_tx: int = 1000,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Scannt neue und trendende Tokens nach den Strategie-Kriterien.
    
    Args:
        mcap_min: Minimale Marktkapitalisierung
        mcap_max: Maximale Marktkapitalisierung
        liquidity_min: Minimale Liquidität
        age_min: Minimales Alter in Tagen
        age_max: Maximales Alter in Tagen
        min_tx: Minimale Anzahl an Transaktionen (24h)
        limit: Maximale Anzahl der zu analysierenden Tokens
        
    Returns:
        Eine Liste mit analysierten Token-Daten, sortiert nach Score
    """
    results = []
    
    # Neue Tokens abrufen
    new_tokens_data = get_newly_added_tokens(limit)
    if new_tokens_data and "success" in new_tokens_data and new_tokens_data["success"]:
        new_tokens = new_tokens_data.get("data", [])
        
        # Limitiere auf die angegebene Anzahl
        new_tokens = new_tokens[:limit]
        
        # Analysiere jeden Token
        for token in new_tokens:
            token_address = token.get("address")
            if not token_address:
                continue
                
            # Hier würden wir die vollständigen Kriterien prüfen,
            # für jetzt führen wir einfach eine grundlegende Analyse durch
            analysis = analyze_token_for_strategy(token_address)
            
            if analysis["success"]:
                results.append(analysis)
    
    # Trendende Tokens abrufen und analysieren (wenn noch Platz ist)
    if len(results) < limit:
        trending_tokens_data = get_trending_tokens(limit - len(results))
        if trending_tokens_data and "success" in trending_tokens_data and trending_tokens_data["success"]:
            trending_tokens = trending_tokens_data.get("data", [])
            
            # Analysiere jeden Token
            for token in trending_tokens:
                token_address = token.get("address")
                if not token_address:
                    continue
                    
                # Prüfe, ob der Token bereits analysiert wurde
                if any(result["token_address"] == token_address for result in results):
                    continue
                
                # Hier würden wir die vollständigen Kriterien prüfen
                analysis = analyze_token_for_strategy(token_address)
                
                if analysis["success"]:
                    results.append(analysis)
                    
                # Breche ab, wenn wir das Limit erreicht haben
                if len(results) >= limit:
                    break
    
    # Sortiere nach Score (absteigend)
    results.sort(key=lambda x: x["score"]["total"], reverse=True)
    
    return results

# Helfer-Funktion zum Extrahieren von Token-Daten für die UI
def extract_token_data_for_ui(token_analysis: Dict[str, Any]) -> tuple:
    """
    Extrahiert die wichtigsten Daten aus der Token-Analyse für die UI.
    
    Args:
        token_analysis: Die vollständige Token-Analyse
        
    Returns:
        Ein Tupel mit (Symbol, MCAP, Score, Potential, Volume-Trend, Hauptgrund)
    """
    token_info = token_analysis.get("token_info", {}).get("data", {})
    price_info = token_analysis.get("price_info", {}).get("data", {})
    
    symbol = token_info.get("symbol", "N/A")
    symbol = f"${symbol}" if symbol != "N/A" else symbol
    
    mcap = price_info.get("mcap", 0)
    mcap_str = formatters.format_k(mcap)
    
    score = token_analysis["score"]["total"]
    potential = token_analysis["potential"]
    volume_trend = token_analysis["volume_trend"]
    main_reason = token_analysis["main_reason"]
    
    return (symbol, mcap_str, str(score), potential, volume_trend, main_reason)