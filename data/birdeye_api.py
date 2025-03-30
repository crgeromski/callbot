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



def analyze_token_for_strategy(token_data, price_history=None):
    """
    Analysiert Token-Daten nach den Kriterien der "Second Bounce Strategy".
    Die Analyse wird um historische Preisdaten erweitert, um Muster besser zu erkennen.
    
    Args:
        token_data: Die Token-Daten aus der API
        price_history: Historische Preis- und Volumendaten (optional)
        
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
        "bounce_detected": False,
        "price_history_analysis": {}
    }
    
    # Wenn historische Preisdaten vorhanden sind, analysiere sie
    if price_history and isinstance(price_history, dict) and "data" in price_history and "candles" in price_history["data"]:
        candles = price_history["data"]["candles"]
        # Analysiere Preishistorie für Pattern-Erkennung
        result["price_history_analysis"] = analyze_price_history(candles)
        
        # 1. Muster-Analyse (40 Punkte) - Verbessert mit historischen Daten
        pattern_score, pattern_reasons = analyze_price_pattern(result["price_history_analysis"])
        result["score"]["pattern"] = pattern_score
        result["reasons"].extend(pattern_reasons)
        
        # Setze dip_detected und bounce_detected basierend auf der Analyse
        result["dip_detected"] = result["price_history_analysis"].get("dip_detected", False)
        result["bounce_detected"] = result["price_history_analysis"].get("bounce_detected", False)
    else:
        # Wenn keine historischen Daten verfügbar sind, verwende die einfachere 24h-Analyse
        simple_pattern_analysis(token_info, result)
    
    # 2. Volumen-Analyse (35 Punkte)
    volume_score, volume_reasons, volume_trend = analyze_volume_quality(token_info, result["price_history_analysis"])
    result["score"]["volume"] = volume_score
    result["reasons"].extend(volume_reasons)
    result["volume_trend"] = volume_trend
    
    # 3. Zeitrahmen-Analyse (15 Punkte)
    timeframe_score, timeframe_reasons = analyze_timeframes(token_info, result["price_history_analysis"])
    result["score"]["timeframe"] = timeframe_score
    result["reasons"].extend(timeframe_reasons)
    
    # 4. Rugpull-Sicherheit (10 Punkte)
    safety_score, safety_reasons = analyze_rugpull_safety(token_info)
    result["score"]["rugpull"] = safety_score
    result["reasons"].extend(safety_reasons)
    
    # Gesamtpunktzahl berechnen
    result["score"]["total"] = sum(result["score"].values())
    
    # Potenzial basierend auf dem Score und anderen Faktoren
    potential_factor = calculate_potential_factor(result["score"]["total"], 
                                                 result["dip_detected"], 
                                                 result["bounce_detected"],
                                                 result["volume_trend"])
    result["potential"] = potential_factor
    
    # Hauptgrund bestimmen
    result["main_reason"] = determine_main_reason(result)
    
    return result

def analyze_price_history(candles):
    """
    Analysiert historische Preisdaten, um wichtige Muster zu erkennen.
    Insbesondere wird nach dem "Dip nach initialem Pump" und dem "Second Bounce" gesucht.
    
    Args:
        candles: Liste der Kerzendaten aus der API
        
    Returns:
        Dictionary mit Analyseergebnissen
    """
    # Sicherstellen, dass die Kerzen nach Zeitstempel sortiert sind (älteste zuerst)
    sorted_candles = sorted(candles, key=lambda x: x.get("time", 0))
    
    # Wenn zu wenige Datenpunkte, können wir kein zuverlässiges Muster erkennen
    if len(sorted_candles) < 10:
        return {
            "dip_detected": False,
            "bounce_detected": False,
            "price_pattern": "insufficient_data",
            "highest_price": 0,
            "lowest_price": 0,
            "current_price": 0,
            "dip_percentage": 0,
            "recovery_percentage": 0,
            "stabilization_count": 0
        }
    
    # Extrahiere Preise für die Analyse
    prices = [float(candle.get("close", 0)) for candle in sorted_candles]
    volumes = [float(candle.get("volume", 0)) for candle in sorted_candles]
    
    # Finde höchsten und niedrigsten Preis
    highest_price = max(prices)
    highest_idx = prices.index(highest_price)
    
    current_price = prices[-1]
    
    # Prüfe, ob nach einem Höchststand ein Dip aufgetreten ist
    if highest_idx < len(prices) - 3:  # Der Höchststand war vor mindestens 3 Kerzen
        # Berechne den tiefsten Punkt nach dem Höchststand
        dip_segment = prices[highest_idx:]
        lowest_price_after_high = min(dip_segment)
        lowest_idx_after_high = highest_idx + dip_segment.index(lowest_price_after_high)
        
        # Berechne den prozentualen Rückgang vom Höchststand
        dip_percentage = (highest_price - lowest_price_after_high) / highest_price * 100
        
        # Prüfe, ob der Dip zwischen 15% und 40% liegt (typisch für einen guten Einstiegspunkt)
        dip_detected = 15 <= dip_percentage <= 40
        
        # Prüfe, ob der Preis nach dem Dip wieder angestiegen ist (Second Bounce)
        prices_after_dip = prices[lowest_idx_after_high:]
        if len(prices_after_dip) >= 3:  # Mindestens 3 Kerzen nach dem Tiefpunkt
            highest_after_dip = max(prices_after_dip)
            recovery_percentage = (highest_after_dip - lowest_price_after_high) / lowest_price_after_high * 100
            
            # Prüfe auf Stabilisierung nach dem Dip
            stabilization_count = 0
            for i in range(lowest_idx_after_high, min(lowest_idx_after_high + 5, len(prices) - 1)):
                next_price = prices[i+1]
                prev_price = prices[i]
                # Wenn die Preisänderung weniger als 5% beträgt, betrachten wir es als stabilisiert
                if abs(next_price - prev_price) / prev_price < 0.05:
                    stabilization_count += 1
            
            # Second Bounce erkannt, wenn der Preis nach dem Dip um mindestens 10% gestiegen ist
            bounce_detected = recovery_percentage >= 10 and stabilization_count >= 2
        else:
            recovery_percentage = 0
            bounce_detected = False
            stabilization_count = 0
    else:
        # Wenn der Höchststand zu nahe am aktuellen Preis liegt, wird kein Dip erkannt
        dip_detected = False
        bounce_detected = False
        lowest_price_after_high = min(prices)  # Fallback
        dip_percentage = 0
        recovery_percentage = 0
        stabilization_count = 0
    
    # Prüfe auf Volumenspitzen während des Dips
    volume_pattern = "unknown"
    if dip_detected and highest_idx < len(volumes) - 1 and lowest_idx_after_high < len(volumes):
        # Durchschnittliches Volumen vor dem Höchststand
        avg_volume_before_high = sum(volumes[:highest_idx]) / max(1, highest_idx)
        
        # Volumen während des Dips
        dip_volumes = volumes[highest_idx:lowest_idx_after_high+1]
        avg_dip_volume = sum(dip_volumes) / max(1, len(dip_volumes))
        
        # Volumen nach dem Dip
        after_dip_volumes = volumes[lowest_idx_after_high:]
        avg_after_dip_volume = sum(after_dip_volumes) / max(1, len(after_dip_volumes))
        
        # Prüfe auf erhöhtes Volumen während des Dips (gutes Zeichen)
        if avg_dip_volume > avg_volume_before_high * 1.2:
            volume_pattern = "high_dip_volume"
        elif avg_after_dip_volume > avg_dip_volume * 1.2:
            volume_pattern = "increasing_after_dip"
        else:
            volume_pattern = "normal"
    
    # Ergebnisse der Analyse
    return {
        "dip_detected": dip_detected,
        "bounce_detected": bounce_detected,
        "price_pattern": "second_bounce" if bounce_detected else "dip" if dip_detected else "other",
        "highest_price": highest_price,
        "lowest_price": lowest_price_after_high,
        "current_price": current_price,
        "dip_percentage": dip_percentage,
        "recovery_percentage": recovery_percentage,
        "stabilization_count": stabilization_count,
        "volume_pattern": volume_pattern
    }

def simple_pattern_analysis(token_info, result):
    """
    Führt eine einfache Musteranalyse basierend auf 24h-Daten durch, wenn keine
    historischen Daten verfügbar sind.
    
    Args:
        token_info: Basisinformationen zum Token
        result: Das Ergebnis-Dictionary, das aktualisiert wird
    """
    # Preis-Änderung 24h als Indikator
    price_change_24h = token_info["price_change_24h"]
    
    # Negative 24h-Änderung könnte auf einen Dip hindeuten
    if -40 <= price_change_24h <= -15:  # 15-40% Dip
        result["score"]["pattern"] += 20
        result["dip_detected"] = True
        result["reasons"].append(f"Preisdip von {abs(price_change_24h):.1f}% erkannt (optimal: 15-40%)")
    elif price_change_24h < -40:  # Zu starker Dip
        result["score"]["pattern"] += 5
        result["reasons"].append(f"Starker Preisdip von {abs(price_change_24h):.1f}% (>40%, Vorsicht)")
    elif price_change_24h > 0:  # Positiver Trend
        bounce_score = min(int(price_change_24h), 30)  # Max 30 Punkte für positiven Trend
        result["score"]["pattern"] += bounce_score
        result["bounce_detected"] = True
        result["reasons"].append(f"Positiver Preistrend ({price_change_24h:.1f}%)")

def analyze_volume_quality(token_info, price_history_analysis):
    """
    Analysiert die Volumenqualität anhand verschiedener Metriken.
    
    Args:
        token_info: Basisinformationen zum Token
        price_history_analysis: Ergebnisse der Preishistorie-Analyse
        
    Returns:
        Tuple mit (Score, Gründe, Volume-Trend)
    """
    volume_score = 0
    reasons = []
    volume_trend = "→"
    
    # Volumen im Verhältnis zur Marktkapitalisierung
    volume_to_mcap = token_info["volume_to_mcap_ratio"]
    
    # Volumen-Qualität basierend auf dem Verhältnis zum MCAP
    if volume_to_mcap >= 0.3:  # Sehr hohes Volumen
        volume_score += 35
        volume_trend = "↑↑"
        reasons.append(f"Außergewöhnlich hohes Handelsvolumen ({volume_to_mcap*100:.1f}% des MCAP)")
    elif volume_to_mcap >= 0.2:  # Hohes Volumen
        volume_score += 30
        volume_trend = "↑"
        reasons.append(f"Sehr starkes Handelsvolumen ({volume_to_mcap*100:.1f}% des MCAP)")
    elif volume_to_mcap >= 0.1:  # Gutes Volumen
        volume_score += 25
        volume_trend = "↑"
        reasons.append(f"Starkes Handelsvolumen ({volume_to_mcap*100:.1f}% des MCAP)")
    elif volume_to_mcap >= 0.05:  # Moderates Volumen
        volume_score += 20
        volume_trend = "↑"
        reasons.append(f"Gutes Handelsvolumen ({volume_to_mcap*100:.1f}% des MCAP)")
    elif volume_to_mcap >= 0.02:  # Ausreichendes Volumen
        volume_score += 15
        reasons.append(f"Moderate Handelsaktivität ({volume_to_mcap*100:.1f}% des MCAP)")
    elif volume_to_mcap > 0:
        volume_score += 10
        volume_trend = "↓"
        reasons.append(f"Niedriges Handelsvolumen ({volume_to_mcap*100:.1f}% des MCAP)")
    else:
        volume_trend = "↓↓"
        reasons.append("Kaum oder kein Handelsvolumen erkennbar")
    
    # Zusätzliche Bonus-Punkte basierend auf dem Volumen-Muster in der Preishistorie
    if price_history_analysis and "volume_pattern" in price_history_analysis:
        volume_pattern = price_history_analysis["volume_pattern"]
        if volume_pattern == "high_dip_volume":
            # Bonus für hohes Volumen während eines Dips (starkes Kaufsignal)
            bonus = min(5, 35 - volume_score)  # Maximal 5 Bonus-Punkte, aber nicht über 35 total
            if bonus > 0:
                volume_score += bonus
                reasons.append("Bonus: Erhöhtes Kaufvolumen während des Dips")
                if volume_trend == "→":
                    volume_trend = "↑"
                elif volume_trend == "↓":
                    volume_trend = "→"
        elif volume_pattern == "increasing_after_dip":
            # Bonus für zunehmendes Volumen nach einem Dip (potentieller Bounce)
            bonus = min(3, 35 - volume_score)  # Maximal 3 Bonus-Punkte
            if bonus > 0:
                volume_score += bonus
                reasons.append("Bonus: Zunehmendes Volumen nach dem Dip")
    
    return volume_score, reasons, volume_trend

def analyze_timeframes(token_info, price_history_analysis):
    """
    Analysiert die verschiedenen Zeitrahmen für eine Divergenz.
    Idealerweise: kurzfristig (5M/1H) negativ, langfristig (6H/24H) positiv.
    
    Args:
        token_info: Basisinformationen zum Token
        price_history_analysis: Ergebnisse der Preishistorie-Analyse
        
    Returns:
        Tuple mit (Score, Gründe)
    """
    timeframe_score = 0
    reasons = []
    
    # Da wir nicht direkt auf 5M/1H/6H/24H-Daten zugreifen können,
    # verwenden wir die 24h-Änderung und die Preishistorie-Analyse
    
    price_change_24h = token_info["price_change_24h"]
    
    # Wenn ein Dip erkannt wurde und der 24h-Wert trotzdem positiv ist,
    # ist das ein starkes Indiz für die gewünschte Zeitrahmen-Divergenz
    if price_history_analysis and price_history_analysis.get("dip_detected", False):
        if price_change_24h > 0:
            timeframe_score += 15
            reasons.append("Ideale Zeitrahmen-Divergenz: Kurzfristiger Dip, langfristig positiv")
        elif price_change_24h > -10 and price_change_24h <= 0:
            timeframe_score += 10
            reasons.append("Gute Zeitrahmen-Konstellation: Dip mit stabilem 24h-Trend")
        elif price_change_24h > -30 and price_change_24h <= -10:
            timeframe_score += 5
            reasons.append("Mäßige Zeitrahmen-Konstellation: Dip mit mäßigem 24h-Rückgang")
    elif price_history_analysis and price_history_analysis.get("bounce_detected", False):
        # Wenn bereits ein Bounce erkannt wurde und 24h positiv ist
        if price_change_24h > 0:
            # Bonus basierend auf der Erholungsrate
            recovery = price_history_analysis.get("recovery_percentage", 0)
            if recovery >= 20:
                timeframe_score += 15
                reasons.append(f"Hervorragender Second Bounce: {recovery:.1f}% Erholung vom Dip")
            elif recovery >= 10:
                timeframe_score += 10
                reasons.append(f"Guter Second Bounce: {recovery:.1f}% Erholung vom Dip")
            else:
                timeframe_score += 5
                reasons.append(f"Beginnender Second Bounce: {recovery:.1f}% Erholung vom Dip")
    elif price_change_24h > 0:
        # Einfach positiver 24h-Trend, ohne erkannten Dip/Bounce
        timeframe_score += 8
        reasons.append(f"Positiver 24h-Trend: +{price_change_24h:.1f}%")
    
    return timeframe_score, reasons

def analyze_rugpull_safety(token_info):
    """
    Analysiert die Sicherheit gegen Rugpulls anhand verschiedener Metriken.
    
    Args:
        token_info: Basisinformationen zum Token
        
    Returns:
        Tuple mit (Score, Gründe)
    """
    safety_score = 0
    reasons = []
    
    # Liquidität im Verhältnis zur Marktkapitalisierung
    liquidity_to_mcap = token_info["liquidity_to_mcap_ratio"]
    
    # Gesunde Liquidität im Verhältnis zur Marktkapitalisierung
    if liquidity_to_mcap >= 0.3:  # Sehr hohe Liquidität
        safety_score += 10
        reasons.append(f"Hervorragende Liquidität ({liquidity_to_mcap*100:.1f}% des MCAP)")
    elif liquidity_to_mcap >= 0.2:  # Hohe Liquidität
        safety_score += 8
        reasons.append(f"Sehr gute Liquidität ({liquidity_to_mcap*100:.1f}% des MCAP)")
    elif liquidity_to_mcap >= 0.1:  # Gute Liquidität
        safety_score += 6
        reasons.append(f"Gute Liquidität ({liquidity_to_mcap*100:.1f}% des MCAP)")
    elif liquidity_to_mcap >= 0.05:  # Ausreichende Liquidität
        safety_score += 4
        reasons.append(f"Ausreichende Liquidität ({liquidity_to_mcap*100:.1f}% des MCAP)")
    elif liquidity_to_mcap >= 0.02:  # Minimale Liquidität
        safety_score += 2
        reasons.append(f"Niedrige Liquidität ({liquidity_to_mcap*100:.1f}% des MCAP)")
    else:
        reasons.append(f"Sehr geringe Liquidität ({liquidity_to_mcap*100:.1f}% des MCAP) - Rugpull-Risiko")
    
    return safety_score, reasons

def calculate_potential_factor(total_score, dip_detected, bounce_detected, volume_trend):
    """
    Berechnet das potenzielle X-Multiple basierend auf dem Score und anderen Faktoren.
    
    Args:
        total_score: Gesamtpunktzahl des Tokens
        dip_detected: Wurde ein Dip erkannt?
        bounce_detected: Wurde ein Bounce erkannt?
        volume_trend: Volumen-Trend (↑, →, ↓)
        
    Returns:
        String mit dem potenziellen X-Multiple
    """
    # Basis-Potential basierend auf dem Score
    if total_score >= 90:
        potential = "→10X"
    elif total_score >= 85:
        potential = "→7X"
    elif total_score >= 80:
        potential = "→5X"
    elif total_score >= 75:
        potential = "→3X"
    elif total_score >= 70:
        potential = "→2X"
    elif total_score >= 60:
        potential = "→1.5X"
    else:
        potential = "→1X"
    
    # Anpassen basierend auf anderen Faktoren
    if bounce_detected and volume_trend in ["↑", "↑↑"] and total_score >= 75:
        # Wenn bereits ein Bounce erkannt wurde und das Volumen stark ist, 
        # könnte das Potential höher sein
        if potential == "→5X":
            potential = "→7X"
        elif potential == "→3X":
            potential = "→5X"
        elif potential == "→2X":
            potential = "→3X"
    elif dip_detected and not bounce_detected and volume_trend in ["↑", "↑↑"]:
        # Wenn ein Dip erkannt wurde, aber noch kein Bounce, ist das ein guter Einstiegspunkt
        # mit möglicherweise höherem Potential
        if total_score >= 70:
            if potential == "→3X":
                potential = "→5X"
            elif potential == "→2X":
                potential = "→3X"
            elif potential == "→1.5X":
                potential = "→2X"
    elif volume_trend == "↓↓" and total_score < 75:
        # Bei sehr niedrigem Volumen ist das Potential begrenzt
        if potential != "→1X":
            potential = "→1X"
    
    return potential

def determine_main_reason(result):
    """
    Bestimmt den Hauptgrund für die Bewertung basierend auf den Scores und erkannten Mustern.
    
    Args:
        result: Das Ergebnis-Dictionary mit allen Analyse-Daten
        
    Returns:
        String mit dem Hauptgrund
    """
    scores = result["score"]
    total = scores["total"]
    
    # Fälle für hohe Scores
    if total >= 85:
        if result["bounce_detected"] and result["volume_trend"] in ["↑", "↑↑"]:
            return "Second Bounce mit starkem Volumen"
        elif scores["pattern"] >= 30 and scores["volume"] >= 25:
            return "Optimales Kurs- und Volumenmuster"
        else:
            return "Hervorragende Gesamtwerte"
    
    # Fälle für mittlere Scores
    elif total >= 70:
        if result["dip_detected"] and not result["bounce_detected"]:
            return "Dip erkannt - potenzieller Einstiegspunkt"
        elif result["bounce_detected"]:
            return "Second Bounce im Gange"
        elif scores["volume"] >= 25:
            return "Starkes Handelsvolumen"
        else:
            return "Solide Gesamtwerte"
    
    # Fälle für niedrige Scores
    else:
        if scores["rugpull"] <= 2:
            return "Hohes Rugpull-Risiko"
        elif scores["volume"] < 15:
            return "Zu geringes Handelsvolumen"
        elif scores["pattern"] < 10:
            return "Kein klares Kursmuster erkennbar"
        elif result["dip_detected"] and scores["volume"] < 20:
            return "Dip mit schwachem Volumen"
        else:
            return "Unzureichende Gesamtwerte"



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