# Birdeye API Integration mit Strategie-Analyse (Schritt 2)
import requests
import json
import time
import os
from typing import Dict, Any, List, Optional, Tuple
import utils.formatters as formatters

# Standard-Wartezeit zwischen API-Aufrufen (in Sekunden)
DEFAULT_WAIT_TIME = 1.2  # Etwas mehr als 1 Sekunde wegen des Rate-Limits

# Cache-Ablaufzeit (in Sekunden)
CACHE_EXPIRY = 60  # 1 Minute

# API-Konfiguration
API_BASE_URL = "https://public-api.birdeye.so"
API_KEY_FILE = r"C:\Users\Gerome PC\Desktop\callbot_github\api dateien\birdeye_api_key.txt"

# Standard-Header für alle Anfragen
DEFAULT_HEADERS = {
    "accept": "application/json",
    "X-Chain": "solana"  # Standardmäßig Solana-Chain verwenden
}

# Cache für API-Antworten
api_cache = {}
# Zeitpunkt des letzten API-Aufrufs
last_api_call = 0

def get_api_key() -> str:
    """
    Liest den API-Key aus der Datei.
    """
    try:
        # Prüfe den angegebenen Pfad
        if os.path.exists(API_KEY_FILE):
            with open(API_KEY_FILE, "r") as f:
                api_key = f.read().strip()
                return api_key
                
        # Kein API-Key gefunden
        print(f"Birdeye API-Key nicht gefunden unter: {API_KEY_FILE}")
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

def make_api_request(endpoint: str, params: Dict = None) -> Dict[str, Any]:
    """
    Führt eine API-Anfrage durch mit korrektem Header und Rate-Limiting.
    """
    api_key = get_api_key()
    if not api_key:
        print("API-Anfrage fehlgeschlagen: Kein API-Key gefunden")
        return {"success": False, "error": "API-Key nicht gefunden"}
    
    # Warte gemäß Rate-Limit
    rate_limit_wait()
    
    # Vollständige URL
    url = f"{API_BASE_URL}{endpoint}"
    
    # Header mit API-Key
    headers = DEFAULT_HEADERS.copy()
    headers["X-API-KEY"] = api_key
    
    try:
        print(f"API-Anfrage an: {url}")
        print(f"Parameter: {params}")
        
        response = requests.get(url, headers=headers, params=params)
        
        print(f"Status-Code: {response.status_code}")
        if response.status_code != 200:
            print(f"Antwort-Inhalt: {response.text[:200]}")  # Ausgabe der ersten 200 Zeichen
        
        response.raise_for_status()  # Wirft Exception bei HTTP-Fehlern
        
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API-Anfragefehler: {e}")
        return {"success": False, "error": str(e)}
    except json.JSONDecodeError:
        print("Fehler beim Decodieren der JSON-Antwort")
        print(f"Antwort-Text: {response.text[:200]}")  # Zeige den Anfang des Antworttexts
        return {"success": False, "error": "Ungültige JSON-Antwort"}

def get_token_list(sort_by="v24hUSD", sort_type="desc", limit=50, offset=0, min_liquidity=0) -> Optional[Dict[str, Any]]:
    """
    Ruft eine sortierte Liste von Tokens ab.
    
    Args:
        sort_by: Sortierkriterium (z.B. "v24hUSD", "mc")
        sort_type: Sortierrichtung ("asc" oder "desc")
        limit: Maximale Anzahl der Ergebnisse
        offset: Offset für Paginierung
        min_liquidity: Minimale Liquidität in USD
        
    Returns:
        Ein Dictionary mit Token-Liste oder None bei Fehler
    """
    cache_key = f"token_list_{sort_by}_{sort_type}_{limit}_{offset}_{min_liquidity}"
    
    def fetch_token_list():
        endpoint = "/defi/tokenlist"
        params = {
            "sort_by": sort_by,
            "sort_type": sort_type,
            "limit": limit,
            "offset": offset,
            "min_liquidity": min_liquidity
        }
        
        return make_api_request(endpoint, params)
    
    return get_cached_or_fetch(cache_key, fetch_token_list)

def get_token_price_history(token_address: str, resolution: str = "5m", from_ts: int = None, to_ts: int = None) -> Optional[Dict[str, Any]]:
    """
    Ruft die Preishistorie eines Tokens ab.
    
    Args:
        token_address: Die Token-Adresse
        resolution: Zeitauflösung (z.B. "5m", "1h", "1d")
        from_ts: Startzeitstempel (Unix-Zeit in Sekunden)
        to_ts: Endzeitstempel (Unix-Zeit in Sekunden)
        
    Returns:
        Ein Dictionary mit der Preishistorie oder None bei Fehler
    """
    # Wenn keine Zeitstempel angegeben sind, verwende die letzten 24 Stunden
    if not from_ts:
        from_ts = int(time.time()) - 86400  # 24 Stunden zurück
    if not to_ts:
        to_ts = int(time.time())
        
    cache_key = f"price_history_{token_address}_{resolution}_{from_ts}_{to_ts}"
    
    def fetch_price_history():
        endpoint = "/defi/price_history"
        params = {
            "address": token_address,
            "resolution": resolution,
            "from_ts": from_ts,
            "to_ts": to_ts
        }
        
        return make_api_request(endpoint, params)
    
    return get_cached_or_fetch(cache_key, fetch_price_history)

def get_token_info(token_address: str) -> Optional[Dict[str, Any]]:
    """
    Ruft detaillierte Informationen zu einem Token ab.
    
    Args:
        token_address: Die Token-Adresse
        
    Returns:
        Ein Dictionary mit Token-Informationen oder None bei Fehler
    """
    cache_key = f"token_info_{token_address}"
    
    def fetch_token_info():
        endpoint = "/defi/token_stat"
        params = {
            "address": token_address
        }
        
        return make_api_request(endpoint, params)
    
    return get_cached_or_fetch(cache_key, fetch_token_info)

def get_filtered_tokens(
    mcap_min: float = 100000,
    mcap_max: float = 3000000,
    liquidity_min: float = 30000,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Holt eine gefilterte Liste von Tokens basierend auf MCAP und Liquidität.
    
    Args:
        mcap_min: Minimale Marktkapitalisierung
        mcap_max: Maximale Marktkapitalisierung
        liquidity_min: Minimale Liquidität
        limit: Maximale Anzahl der Ergebnisse
        
    Returns:
        Eine Liste mit gefilterten Token-Daten
    """
    # Versuche mehr Tokens zu holen als wir benötigen (50), da einige gefiltert werden könnten
    token_list = get_token_list(limit=50, min_liquidity=liquidity_min)
    filtered_tokens = []
    
    if token_list and token_list.get("success", False):
        tokens = token_list.get("data", {}).get("tokens", [])
        
        for token in tokens:
            # MCAP-Filter
            mcap = token.get("mc", 0)
            if mcap_min <= mcap <= mcap_max:
                # Liquiditäts-Filter (bereits durch API-Parameter gesetzt, aber zur Sicherheit)
                liquidity = token.get("liquidity", 0)
                if liquidity >= liquidity_min:
                    filtered_tokens.append(token)
                    
                    # Begrenze die Anzahl der Tokens
                    if len(filtered_tokens) >= limit:
                        break
    
    return filtered_tokens

def extract_token_info(token: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extrahiert die relevanten Informationen aus einem Token-Objekt.
    
    Args:
        token: Das Token-Objekt aus der API-Antwort
        
    Returns:
        Ein Dictionary mit den relevanten Token-Informationen
    """
    address = token.get("address", "")
    symbol = token.get("symbol", "").upper()
    name = token.get("name", "")
    mcap = token.get("mc", 0)
    liquidity = token.get("liquidity", 0)
    price = token.get("price", 0)
    volume_24h = token.get("v24h", 0)
    price_change_24h = token.get("priceChange24h", 0)
    
    # Berechne zusätzliche Daten für die Strategie
    volume_to_mcap_ratio = volume_24h / mcap if mcap > 0 else 0
    liquidity_to_mcap_ratio = liquidity / mcap if mcap > 0 else 0
    
    return {
        "address": address,
        "symbol": symbol,
        "name": name,
        "mcap": mcap,
        "liquidity": liquidity,
        "price": price,
        "volume_24h": volume_24h,
        "price_change_24h": price_change_24h,
        "volume_to_mcap_ratio": volume_to_mcap_ratio,
        "liquidity_to_mcap_ratio": liquidity_to_mcap_ratio,
        # Für UI-Anzeige formatierte Werte
        "mcap_display": formatters.format_k(mcap),
        "liquidity_display": formatters.format_k(liquidity),
        "volume_24h_display": formatters.format_k(volume_24h),
        "price_change_24h_display": f"{price_change_24h:.2f}%"
    }

def analyze_token_for_strategy(token_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analysiert Token-Daten nach den Kriterien der "Second Bounce Strategy".
    
    Args:
        token_data: Die Token-Daten aus der API
        
    Returns:
        Ein Dictionary mit der Analyse und dem Score
    """
    token_info = extract_token_info(token_data)
    token_address = token_info["address"]
    
    # Initialisiere das Ergebnis-Dictionary
    result = {
        "token_address": token_address,
        "token_info": token_info,
        "score": {
            "pattern": 0,  # Max 40 Punkte
            "volume": 0,   # Max 35 Punkte
            "timeframe": 0,  # Max 15 Punkte
            "rugpull": 0,    # Max 10 Punkte
            "total": 0
        },
        "reasons": [],
        "potential": "→1X",
        "main_reason": "",
        "volume_trend": "→",
        "dip_detected": False,
        "bounce_detected": False
    }
    
    # 1. Muster-Analyse (40 Punkte)
    # Hier würden wir normalerweise die Preishistorie analysieren
    # Da wir nur begrenzte Daten haben, basieren wir dies auf den verfügbaren Daten
    
    # Preis-Änderung 24h als Indikator
    price_change_24h = token_info["price_change_24h"]
    
    # Negative 24h-Änderung könnte auf einen Dip hindeuten
    if -40 <= price_change_24h <= -15:  # 15-40% Dip
        result["score"]["pattern"] += 20
        result["dip_detected"] = True
        result["reasons"].append("Preisdip von 15-40% erkannt")
    elif price_change_24h < -40:  # Zu starker Dip
        result["score"]["pattern"] += 5
        result["reasons"].append("Zu starker Preisdip (> 40%)")
    elif price_change_24h > 0:  # Positiver Trend
        bounce_score = min(int(price_change_24h), 30)  # Max 30 Punkte für positiven Trend
        result["score"]["pattern"] += bounce_score
        result["bounce_detected"] = True
        result["reasons"].append(f"Positiver Preistrend ({price_change_24h:.1f}%)")
    
    # 2. Volumen-Analyse (35 Punkte)
    volume_to_mcap = token_info["volume_to_mcap_ratio"]
    
    # Gesundes Volumen im Verhältnis zur Marktkapitalisierung
    if volume_to_mcap >= 0.2:  # 20% des MCAP als Volumen
        result["score"]["volume"] += 30
        result["volume_trend"] = "↑"
        result["reasons"].append("Starkes Handelsvolumen")
    elif volume_to_mcap >= 0.05:  # 5% des MCAP als Volumen
        result["score"]["volume"] += 20
        result["volume_trend"] = "↑"
        result["reasons"].append("Moderates Handelsvolumen")
    elif volume_to_mcap > 0:
        result["score"]["volume"] += 10
        result["reasons"].append("Niedriges Handelsvolumen")
    
    # 3. Zeitrahmen-Analyse (15 Punkte)
    # Dies würde normalerweise verschiedene Zeitrahmen vergleichen
    # Als Vereinfachung verwenden wir die 24h-Änderung
    if price_change_24h > 0 and result["dip_detected"]:
        result["score"]["timeframe"] += 15
        result["reasons"].append("Positive Entwicklung nach Dip")
    elif price_change_24h > 0:
        result["score"]["timeframe"] += 10
        result["reasons"].append("Positiver 24h-Trend")
    
    # 4. Rugpull-Sicherheit (10 Punkte)
    liquidity_to_mcap = token_info["liquidity_to_mcap_ratio"]
    
    # Gesunde Liquidität im Verhältnis zur Marktkapitalisierung
    if liquidity_to_mcap >= 0.2:  # 20% des MCAP als Liquidität
        result["score"]["rugpull"] += 10
        result["reasons"].append("Hohe Liquidität im Verhältnis zum MCAP")
    elif liquidity_to_mcap >= 0.1:  # 10% des MCAP als Liquidität
        result["score"]["rugpull"] += 5
        result["reasons"].append("Moderate Liquidität im Verhältnis zum MCAP")
    
    # Gesamtpunktzahl berechnen
    result["score"]["total"] = sum(result["score"].values())
    
    # Potenzial basierend auf dem Score
    if result["score"]["total"] >= 85:
        result["potential"] = "→5X"
    elif result["score"]["total"] >= 75:
        result["potential"] = "→3X"
    elif result["score"]["total"] >= 70:
        result["potential"] = "→2X"
    else:
        result["potential"] = "→1X"
    
    # Hauptgrund bestimmen
    if result["dip_detected"] and result["bounce_detected"]:
        result["main_reason"] = "Second Bounce nach Dip"
    elif result["bounce_detected"]:
        result["main_reason"] = "Positiver Preistrend"
    elif result["dip_detected"]:
        result["main_reason"] = "Potenzieller Einstiegspunkt (Dip)"
    elif result["score"]["volume"] > 20:
        result["main_reason"] = "Hohes Handelsvolumen"
    else:
        result["main_reason"] = "Kein klares Signal"
    
    return result

def scan_tokens_for_strategy(
    mcap_min: float = 100000,
    mcap_max: float = 3000000,
    liquidity_min: float = 30000,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Scannt Tokens nach den Strategie-Kriterien.
    
    Args:
        mcap_min: Minimale Marktkapitalisierung
        mcap_max: Maximale Marktkapitalisierung
        liquidity_min: Minimale Liquidität
        limit: Maximale Anzahl der zu analysierenden Tokens
        
    Returns:
        Eine Liste mit analysierten Token-Daten, sortiert nach Score
    """
    # Hole gefilterte Tokens
    filtered_tokens = get_filtered_tokens(
        mcap_min=mcap_min,
        mcap_max=mcap_max,
        liquidity_min=liquidity_min,
        limit=limit
    )
    
    # Analyse jedes Tokens
    results = []
    for token in filtered_tokens:
        analysis = analyze_token_for_strategy(token)
        results.append(analysis)
    
    # Sortiere nach Score (absteigend)
    results.sort(key=lambda x: x["score"]["total"], reverse=True)
    
    return results

def extract_token_data_for_ui(analysis: Dict[str, Any]) -> tuple:
    """
    Extrahiert die wichtigsten Daten aus der Token-Analyse für die UI.
    
    Args:
        analysis: Die vollständige Token-Analyse
        
    Returns:
        Ein Tuple mit (Symbol, MCAP, Score, Potential, Volume-Trend, Hauptgrund)
    """
    token_info = analysis["token_info"]
    symbol = f"${token_info['symbol']}"
    mcap_str = token_info["mcap_display"]
    score = str(analysis["score"]["total"])
    potential = analysis["potential"]
    volume_trend = analysis["volume_trend"]
    main_reason = analysis["main_reason"]
    
    return (symbol, mcap_str, score, potential, volume_trend, main_reason)

# Test-Funktion, wenn direkt ausgeführt
if __name__ == "__main__":
    print("=== Birdeye API Test - Schritt 2 ===")
    
    # API-Key testen
    api_key = get_api_key()
    if api_key:
        print(f"API-Key gefunden: {api_key[:5]}..." + "*" * (len(api_key) - 5))
    else:
        print("Kein API-Key gefunden!")
    
    print("\n=== Token-Liste Test ===")
    token_list = get_token_list(limit=3)
    if token_list and token_list.get("success", False):
        print("Token-Liste erfolgreich abgerufen!")
        tokens = token_list.get("data", {}).get("tokens", [])
        print(f"Anzahl Tokens: {len(tokens)}")
    else:
        print("Fehler beim Abrufen der Token-Liste")
    
    print("\n=== Strategie-Scan Test ===")
    results = scan_tokens_for_strategy(
        mcap_min=50000,     # 50K
        mcap_max=5000000,   # 5M
        liquidity_min=10000, # 10K
        limit=3
    )
    
    print(f"Anzahl analysierter Tokens: {len(results)}")
    
    for i, analysis in enumerate(results):
        token_data = extract_token_data_for_ui(analysis)
        print(f"\nToken {i+1}: {token_data[0]}")
        print(f"MCAP: {token_data[1]}")
        print(f"Score: {token_data[2]}/100")
        print(f"Potential: {token_data[3]}")
        print(f"Volume-Trend: {token_data[4]}")
        print(f"Hauptgrund: {token_data[5]}")
        print(f"Gründe:")
        for reason in analysis["reasons"]:
            print(f"  - {reason}")