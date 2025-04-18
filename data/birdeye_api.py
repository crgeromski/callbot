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
# Korrekter Pfad zur API-Key-Datei
API_KEY_FILE = r"C:\Users\Gerome PC\Desktop\callbot_real\api_key.txt" 

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
        endpoint = "/defi/token_overview" # Korrigierter Endpunkt
        params = {
            "address": token_address
        }
        
        return make_api_request(endpoint, params)
    
    return get_cached_or_fetch(cache_key, fetch_token_info)

def get_filtered_tokens(
    mcap_min: float = 100000,
    mcap_max: float = 3000000,
    liquidity_min: float = 30000,
    limit: int = 20 # Dieses Limit bezieht sich auf die Anzahl der *zurückgegebenen*, gefilterten Tokens
) -> List[Dict[str, Any]]:
    """
    Holt eine Liste von Tokens von der API, filtert sie nach MCAP und gibt eine begrenzte Anzahl zurück.
    
    Args:
        mcap_min: Minimale Marktkapitalisierung
        mcap_max: Maximale Marktkapitalisierung
        liquidity_min: Minimale Liquidität (wird an API übergeben)
        limit: Maximale Anzahl der *zurückzugebenden* Tokens nach Filterung
        
    Returns:
        Eine Liste mit gefilterten Token-Daten, maximal 'limit' Elemente.
    """
    # Hole die maximal erlaubte Menge Tokens von der API (Limit ist 50)
    fetch_limit = 50 
    print(f"Rufe Top {fetch_limit} Tokens von Birdeye ab (min. Liquidität: {liquidity_min})...")
    token_list = get_token_list(limit=fetch_limit, min_liquidity=liquidity_min)
    filtered_tokens = []

    if token_list and token_list.get("success", False):
        print(f"API-Antwort erhalten, verarbeite Tokens...")
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

def extract_token_info(token_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extrahiert und berechnet die relevanten Informationen aus einem Token-Objekt
    von /defi/tokenlist oder /defi/token_stat.
    
    Args:
        token_data: Das Token-Objekt aus der API-Antwort
        
    Returns:
        Ein Dictionary mit den relevanten Token-Informationen
    """
    # Versuche, die Daten aus verschiedenen möglichen Schlüsseln zu extrahieren
    address = token_data.get("address", "")
    symbol = token_data.get("symbol", "").upper()
    name = token_data.get("name", "")
    # Felder aus /token_overview verwenden oder Fallback auf /tokenlist Felder
    mcap = token_data.get("marketCap", token_data.get("mc", 0)) 
    liquidity = token_data.get("liquidity", 0)
    price = token_data.get("price", 0)
    volume_24h = token_data.get("v24hUSD", token_data.get("v24h", 0)) # Verwende v24hUSD oder v24h
    
    # Preisänderungen für verschiedene Zeiträume (aus /token_overview oder /tokenlist)
    price_change_1h = token_data.get("priceChange1hPercent", token_data.get("priceChange1h", 0))
    price_change_4h = token_data.get("priceChange4hPercent", token_data.get("priceChange4h", 0))
    price_change_12h = token_data.get("priceChange12hPercent", token_data.get("priceChange12h", 0))
    price_change_24h = token_data.get("priceChange24hPercent", token_data.get("priceChange24h", 0))
    
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
        "price_change_1h": price_change_1h,
        "price_change_4h": price_change_4h,
        "price_change_12h": price_change_12h,
        "price_change_24h": price_change_24h,
        "volume_to_mcap_ratio": volume_to_mcap_ratio,
        "liquidity_to_mcap_ratio": liquidity_to_mcap_ratio,
        # Für UI-Anzeige formatierte Werte
        "mcap_display": formatters.format_k(mcap),
        "liquidity_display": formatters.format_k(liquidity),
        "volume_24h_display": formatters.format_k(volume_24h),
        "price_change_24h_display": f"{price_change_24h:.2f}%" # Ist bereits Prozentwert
    }

def analyze_price_pattern(price_history_analysis: Dict[str, Any], max_score: int = 40) -> Tuple[int, List[str]]:
    """
    Analysiert das Preismuster basierend auf der historischen Analyse.
    
    Args:
        price_history_analysis: Ergebnisse der Preishistorie-Analyse
        max_score: Die maximal erreichbare Punktzahl für diese Kategorie (Gewichtung)
        
    Returns:
        Tuple mit (Score, Gründe)
    """
    # Interner Maximalwert, auf den die Logik ursprünglich ausgelegt war
    internal_max_score = 40
    raw_score = 0 # Rohpunkte basierend auf der internen Logik
    reasons = []
    
    dip_detected = price_history_analysis.get("dip_detected", False)
    bounce_detected = price_history_analysis.get("bounce_detected", False)
    dip_percentage = price_history_analysis.get("dip_percentage", 0)
    stabilization_count = price_history_analysis.get("stabilization_count", 0)
    recovery_percentage = price_history_analysis.get("recovery_percentage", 0)
    
    # Punkte für korrekten Dip (15-40%)
    if dip_detected:
        raw_score += 15 # Grundpunkte für korrekten Dip
        reasons.append(f"Dip von {dip_percentage:.1f}% erkannt (Ziel: 15-40%)")
        
        # Punkte für Stabilisierung (mindestens 3 Kerzen)
        if stabilization_count >= 3:
            stabilization_bonus = min(10, (stabilization_count - 2) * 5) # Bis zu 10 Punkte für 3+ Kerzen
            raw_score += stabilization_bonus
            reasons.append(f"Preisstabilisierung über {stabilization_count} Kerzen nach Dip")
        else:
             reasons.append(f"Wenig Stabilisierung ({stabilization_count}) nach Dip (Ziel: 3-5)")

        # Punkte für Bounce nach Dip und Stabilisierung
        if bounce_detected:
            bounce_bonus = min(15, 5 + int(recovery_percentage / 5)) # Bis zu 15 Punkte für Bounce Stärke
            raw_score += bounce_bonus
            reasons.append(f"Second Bounce mit {recovery_percentage:.1f}% Erholung erkannt")
        else:
            reasons.append("Kein klarer Bounce nach Dip bisher")
            
    elif dip_percentage > 40:
         raw_score += 5 # Wenige Punkte für zu starken Dip
         reasons.append(f"Dip zu stark ({dip_percentage:.1f}%), erhöhtes Risiko")
    elif dip_percentage > 0: # Dip < 15%
         raw_score += 5 # Wenige Punkte für zu schwachen Dip
         reasons.append(f"Dip zu gering ({dip_percentage:.1f}%), schwaches Signal")
    else: # Kein Dip erkannt
        # Korrekte Einrückung hier:
        reasons.append("Kein signifikanter Dip nach Höchststand erkannt")
        # Optional: Punkte für generellen Aufwärtstrend, falls kein Dip/Bounce?
        # Hier vorerst keine Punkte, da Fokus auf Dip/Bounce liegt.

    # TODO: Kerzenmuster (Hammer/Doji) analysieren, falls OHLC-Daten verfügbar wären
    
    # Skaliere den Roh-Score auf den maximal erlaubten Score (Gewichtung)
    # Stelle sicher, dass internal_max_score nicht 0 ist, um Division durch Null zu vermeiden
    if internal_max_score > 0:
        scaled_score = round((raw_score / internal_max_score) * max_score)
    else:
        scaled_score = 0 # Wenn die interne Maximalpunktzahl 0 ist, ist der skalierte Score auch 0
        
    # Begrenze den Score auf maximal max_score Punkte
    final_score = min(scaled_score, max_score)
    
    return final_score, reasons

def analyze_token_for_strategy(
    token_data, 
    price_history=None,
    pattern_weight: int = 40,
    volume_weight: int = 35,
    timeframe_weight: int = 15,
    rugpull_weight: int = 10
):
    """
    Analysiert Token-Daten nach den Kriterien der "Second Bounce Strategy".
    Die Analyse wird um historische Preisdaten erweitert, um Muster besser zu erkennen.
    
    Args:
        token_data: Die Token-Daten aus der API
        price_history: Historische Preis- und Volumendaten (optional)
        pattern_weight: Gewichtung für Mustererkennung
        volume_weight: Gewichtung für Volumenbestätigung
        timeframe_weight: Gewichtung für Zeitrahmenübereinstimmung
        rugpull_weight: Gewichtung für Rugpull-Sicherheit
        
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
            "pattern": 0,
            "volume": 0,
            "timeframe": 0,
            "rugpull": 0,
            "total": 0
        },
        "weights": { # Speichere die verwendeten Gewichte für die UI-Anzeige
            "pattern": pattern_weight,
            "volume": volume_weight,
            "timeframe": timeframe_weight,
            "rugpull": rugpull_weight
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
    # if price_history and isinstance(price_history, dict) and "data" in price_history and "candles" in price_history["data"]:
    #     candles = price_history["data"]["candles"]
    #     # Analysiere Preishistorie für Pattern-Erkennung
    #     result["price_history_analysis"] = analyze_price_history(candles)
        
    #     # 1. Muster-Analyse (Gewichtet) - Verbessert mit historischen Daten
    #     pattern_score, pattern_reasons = analyze_price_pattern(result["price_history_analysis"], max_score=pattern_weight)
    #     result["score"]["pattern"] = pattern_score
    #     result["reasons"].extend(pattern_reasons)
        
    #     # Setze dip_detected und bounce_detected basierend auf der Analyse
    #     result["dip_detected"] = result["price_history_analysis"].get("dip_detected", False)
    #     result["bounce_detected"] = result["price_history_analysis"].get("bounce_detected", False)
    # else:
    #     # Wenn keine historischen Daten verfügbar sind oder die Analyse fehlgeschlagen ist
    #     result["reasons"].append("Keine ausreichenden historischen Preisdaten für Musteranalyse verfügbar.")
    #     # Fallback auf einfache 24h-Analyse (optional, könnte man auch weglassen und 0 Punkte geben)
    #     # simple_pattern_analysis(token_info, result) # Entfernt, da wir historische Daten priorisieren
    result["score"]["pattern"] = 0 # Keine Punkte ohne historische Daten
    result["reasons"].append("Preismuster-Analyse deaktiviert (API-Limit)")
    
    # 2. Volumen-Analyse (Gewichtet)
    volume_score, volume_reasons, volume_trend = analyze_volume_quality(token_info, result.get("price_history_analysis", {}), max_score=volume_weight)
    result["score"]["volume"] = volume_score
    result["reasons"].extend(volume_reasons)
    result["volume_trend"] = volume_trend
    
    # 3. Zeitrahmen-Analyse (Gewichtet)
    timeframe_score, timeframe_reasons = analyze_timeframes(token_info, result.get("price_history_analysis", {}), max_score=timeframe_weight)
    result["score"]["timeframe"] = timeframe_score
    result["reasons"].extend(timeframe_reasons)
    
    # 4. Rugpull-Sicherheit (Gewichtet)
    safety_score, safety_reasons = analyze_rugpull_safety(token_info, max_score=rugpull_weight)
    result["score"]["rugpull"] = safety_score
    result["reasons"].extend(safety_reasons)
    
    # Gesamtpunktzahl berechnen (Summe der gewichteten Scores)
    result["score"]["total"] = sum(result["score"].values())
    
    # Potenzial basierend auf dem Score und anderen Faktoren
    total_weight = sum(result["weights"].values())
    potential_factor = calculate_potential_factor(
        result["score"]["total"], 
        total_weight,
        result["dip_detected"], 
        result["bounce_detected"], 
        result["volume_trend"]
    )
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
        dip_percentage = (highest_price - lowest_price_after_high) / highest_price * 100 if highest_price > 0 else 0
        
        # Prüfe, ob der Dip zwischen 15% und 40% liegt (typisch für einen guten Einstiegspunkt)
        dip_detected = 15 <= dip_percentage <= 40
        
        # Prüfe, ob der Preis nach dem Dip wieder angestiegen ist (Second Bounce)
        prices_after_dip = prices[lowest_idx_after_high:]
        if len(prices_after_dip) >= 3:  # Mindestens 3 Kerzen nach dem Tiefpunkt
            highest_after_dip = max(prices_after_dip)
            recovery_percentage = (highest_after_dip - lowest_price_after_high) / lowest_price_after_high * 100 if lowest_price_after_high > 0 else 0
            
            # Prüfe auf Stabilisierung nach dem Dip (über z.B. 5 Kerzen)
            stabilization_candles = 5 # Anzahl der Kerzen für Stabilisierungsprüfung
            stabilization_threshold = 0.05 # Maximale prozentuale Änderung für Stabilisierung
            stabilization_count = 0
            
            # Stelle sicher, dass wir nicht über das Array-Ende hinausgehen
            stabilization_end_idx = min(lowest_idx_after_high + stabilization_candles, len(prices) -1)
            
            # Beginne die Prüfung ab der Kerze *nach* dem Tiefpunkt
            for i in range(lowest_idx_after_high + 1, stabilization_end_idx + 1):
                # Stelle sicher, dass der vorherige Index gültig ist
                if i > 0:
                    current_close = prices[i]
                    prev_close = prices[i-1]
                    # Vermeide Division durch Null
                    if prev_close > 0:
                        price_change_percent = abs(current_close - prev_close) / prev_close
                        if price_change_percent < stabilization_threshold:
                            stabilization_count += 1
                        else:
                            # Breche ab, wenn eine Kerze nicht stabil ist
                            break 
                    else:
                        # Wenn der vorherige Preis Null war, können wir keine prozentuale Änderung berechnen
                        # Brechen wir hier ab oder behandeln es als stabil? Vorerst Abbruch.
                        break 
            
            # Second Bounce erkannt, wenn Preis nach Dip um mind. 10% gestiegen ist UND Stabilisierung (mind. 3 Kerzen) stattfand
            # Wir prüfen auf >= 3, da die Anforderung 3-5 Kerzen war.
            bounce_detected = recovery_percentage >= 10 and stabilization_count >= 3 
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
    # Stelle sicher, dass Indizes gültig sind
    if dip_detected and highest_idx < len(volumes) and lowest_idx_after_high < len(volumes):
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

# Entfernt, da wir die Analyse auf historischen Daten basieren
# def simple_pattern_analysis(token_info, result):
#     ...

def analyze_volume_quality(token_info, price_history_analysis, max_score: int = 35):
    """
    Analysiert die Volumenqualität anhand verschiedener Metriken.
    
    Args:
        token_info: Basisinformationen zum Token
        price_history_analysis: Ergebnisse der Preishistorie-Analyse
        max_score: Die maximal erreichbare Punktzahl für diese Kategorie (Gewichtung)
        
    Returns:
        Tuple mit (Score, Gründe, Volume-Trend)
    """
    internal_max_score = 35
    raw_score = 0
    reasons = []
    volume_trend = "→"
    
    # Volumen im Verhältnis zur Marktkapitalisierung
    volume_to_mcap = token_info["volume_to_mcap_ratio"]
    
    # Volumen-Qualität basierend auf dem Verhältnis zum MCAP
    if volume_to_mcap >= 0.3:  # Sehr hohes Volumen
        raw_score += 35
        volume_trend = "↑↑"
        reasons.append(f"Außergewöhnlich hohes Handelsvolumen ({volume_to_mcap*100:.1f}% des MCAP)")
    elif volume_to_mcap >= 0.2:  # Hohes Volumen
        raw_score += 30
        volume_trend = "↑"
        reasons.append(f"Sehr starkes Handelsvolumen ({volume_to_mcap*100:.1f}% des MCAP)")
    elif volume_to_mcap >= 0.1:  # Gutes Volumen
        raw_score += 25
        volume_trend = "↑"
        reasons.append(f"Starkes Handelsvolumen ({volume_to_mcap*100:.1f}% des MCAP)")
    elif volume_to_mcap >= 0.05:  # Moderates Volumen
        raw_score += 20
        volume_trend = "↑"
        reasons.append(f"Gutes Handelsvolumen ({volume_to_mcap*100:.1f}% des MCAP)")
    elif volume_to_mcap >= 0.02:  # Ausreichendes Volumen
        raw_score += 15
        reasons.append(f"Moderate Handelsaktivität ({volume_to_mcap*100:.1f}% des MCAP)")
    elif volume_to_mcap > 0:
        raw_score += 10
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
            bonus = min(5, internal_max_score - raw_score)  # Maximal 5 Bonus-Punkte, aber nicht über internal_max_score total
            if bonus > 0:
                raw_score += bonus
                reasons.append("Bonus: Erhöhtes Kaufvolumen während des Dips")
                if volume_trend == "→":
                    volume_trend = "↑"
                elif volume_trend == "↓":
                    volume_trend = "→"
        elif volume_pattern == "increasing_after_dip":
            # Bonus für zunehmendes Volumen nach einem Dip (potentieller Bounce)
            bonus = min(3, internal_max_score - raw_score)  # Maximal 3 Bonus-Punkte
            if bonus > 0:
                raw_score += bonus
                reasons.append("Bonus: Zunehmendes Volumen nach dem Dip")

    # Skaliere und begrenze den Score
    if internal_max_score > 0:
        scaled_score = round((raw_score / internal_max_score) * max_score)
    else:
        scaled_score = 0
    final_score = min(scaled_score, max_score)
    
    return final_score, reasons, volume_trend

def analyze_timeframes(token_info, price_history_analysis, max_score: int = 15):
    """
    Analysiert die verschiedenen Zeitrahmen für eine Divergenz.
    Idealerweise: kurzfristig (5M/1H) negativ, langfristig (6H/24H) positiv.
    
    Args:
        token_info: Basisinformationen zum Token
        price_history_analysis: Ergebnisse der Preishistorie-Analyse
        max_score: Die maximal erreichbare Punktzahl für diese Kategorie (Gewichtung)
        
    Returns:
        Tuple mit (Score, Gründe)
    """
    internal_max_score = 15
    raw_score = 0
    reasons = []
    
    # Verwende spezifische Zeitrahmen-Daten aus token_info (jetzt aus /token_overview)
    # priceChange*hPercent Felder werden verwendet
    
    # Hole die verfügbaren Preisänderungen (Standardwert 0, falls nicht vorhanden)
    price_change_1h = token_info.get("price_change_1h", 0) # Bereits extrahiert als priceChange1hPercent
    price_change_12h = token_info.get("price_change_12h", 0) # Bereits extrahiert als priceChange12hPercent
    price_change_24h = token_info.get("price_change_24h", 0) # Bereits extrahiert als priceChange24hPercent
    
    # Definiere kurzfristige und langfristige Indikatoren
    # Annahme: 1H ist kurzfristig, 12H/24H sind langfristig
    short_term_negative = price_change_1h < -2 # Erlaube leichten negativen Trend (-2%)
    long_term_positive = price_change_12h > 0 or price_change_24h > 0
    
    # Ideale Divergenz: Kurzfristig negativ, Langfristig positiv
    if short_term_negative and long_term_positive:
        raw_score += 15
        reasons.append(f"Ideale Zeitrahmen-Divergenz (1H: {price_change_1h:.1f}%, 12/24H positiv)")
    # Gute Konstellation: Kurzfristig leicht negativ/neutral, Langfristig positiv
    elif price_change_1h <= 0 and long_term_positive:
        raw_score += 10
        reasons.append(f"Gute Zeitrahmen-Konstellation (1H: {price_change_1h:.1f}%, 12/24H positiv)")
    # Akzeptabel: Alles positiv (Aufwärtstrend)
    elif price_change_1h > 0 and long_term_positive:
        raw_score += 5
        reasons.append(f"Genereller Aufwärtstrend (1H: {price_change_1h:.1f}%, 12/24H positiv)")
    # Negativ: Langfristig negativ
    elif not long_term_positive:
        raw_score += 0 # Keine Punkte bei negativem Langzeittrend
        reasons.append(f"Negativer Langzeit-Trend (12H: {price_change_12h:.1f}%, 24H: {price_change_24h:.1f}%)")
    else:
        # Andere Fälle (z.B. kurz positiv, lang negativ) - weniger ideal
        raw_score += 2
        reasons.append(f"Inkonsistente Zeitrahmen (1H: {price_change_1h:.1f}%, 12H: {price_change_12h:.1f}%, 24H: {price_change_24h:.1f}%)")

    # Bonus, wenn 5M (aus price_history) positiv wird (falls Dip erkannt wurde)
    # Wir könnten es aus price_history_analysis ableiten, wenn dort die letzte Kerze positiv war.
    if price_history_analysis and price_history_analysis.get("dip_detected", False):
         current_price = price_history_analysis.get("current_price", 0)
         lowest_price = price_history_analysis.get("lowest_price", 0)
         # Prüfe, ob der aktuelle Preis über dem Tiefpunkt liegt
         if current_price > lowest_price:
             bonus = min(3, internal_max_score - raw_score) # Kleiner Bonus, max 3
             if bonus > 0:
                 raw_score += bonus
                 reasons.append("Bonus: Preis beginnt sich vom Dip-Tief zu erholen")

    # Skaliere und begrenze den Score
    if internal_max_score > 0:
        scaled_score = round((raw_score / internal_max_score) * max_score)
    else:
        scaled_score = 0
    final_score = min(scaled_score, max_score)
    
    return final_score, reasons

def analyze_rugpull_safety(token_info, max_score: int = 10):
    """
    Analysiert die Sicherheit gegen Rugpulls anhand verschiedener Metriken.
    
    Args:
        token_info: Basisinformationen zum Token
        max_score: Die maximal erreichbare Punktzahl für diese Kategorie (Gewichtung)
        
    Returns:
        Tuple mit (Score, Gründe)
    """
    internal_max_score = 10
    raw_score = 0
    reasons = []
    
    # Liquidität im Verhältnis zur Marktkapitalisierung
    liquidity_to_mcap = token_info["liquidity_to_mcap_ratio"]
    
    # Gesunde Liquidität im Verhältnis zur Marktkapitalisierung
    if liquidity_to_mcap >= 0.3:  # Sehr hohe Liquidität
        raw_score += 10
        reasons.append(f"Hervorragende Liquidität ({liquidity_to_mcap*100:.1f}% des MCAP)")
    elif liquidity_to_mcap >= 0.2:  # Hohe Liquidität
        raw_score += 8
        reasons.append(f"Sehr gute Liquidität ({liquidity_to_mcap*100:.1f}% des MCAP)")
    elif liquidity_to_mcap >= 0.1:  # Gute Liquidität
        raw_score += 6
        reasons.append(f"Gute Liquidität ({liquidity_to_mcap*100:.1f}% des MCAP)")
    elif liquidity_to_mcap >= 0.05:  # Ausreichende Liquidität
        raw_score += 4
        reasons.append(f"Ausreichende Liquidität ({liquidity_to_mcap*100:.1f}% des MCAP)")
    elif liquidity_to_mcap >= 0.02:  # Minimale Liquidität
        raw_score += 2
        reasons.append(f"Niedrige Liquidität ({liquidity_to_mcap*100:.1f}% des MCAP)")
    else:
        reasons.append(f"Sehr geringe Liquidität ({liquidity_to_mcap*100:.1f}% des MCAP) - Rugpull-Risiko")

    # Skaliere und begrenze den Score
    if internal_max_score > 0:
        scaled_score = round((raw_score / internal_max_score) * max_score)
    else:
        scaled_score = 0
    final_score = min(scaled_score, max_score)
    
    return final_score, reasons

def calculate_potential_factor(total_score, total_weight, dip_detected, bounce_detected, volume_trend):
    """
    Berechnet das potenzielle X-Multiple basierend auf dem Score und anderen Faktoren.
    
    Args:
        total_score: Gesamtpunktzahl des Tokens (Summe der gewichteten Scores)
        total_weight: Summe der Gewichtungen (normalerweise 100)
        dip_detected: Wurde ein Dip erkannt?
        bounce_detected: Wurde ein Bounce erkannt?
        volume_trend: Volumen-Trend (↑, →, ↓)
        
    Returns:
        String mit dem potenziellen X-Multiple
    """
    # Berechne den prozentualen Score relativ zur Gesamtgewichtung
    percentage_score = (total_score / total_weight * 100) if total_weight > 0 else 0
    
    # Basis-Potential basierend auf dem prozentualen Score
    if percentage_score >= 90:
        potential = "→10X"
    elif percentage_score >= 85:
        potential = "→7X"
    elif percentage_score >= 80:
        potential = "→5X"
    elif percentage_score >= 75:
        potential = "→3X"
    elif percentage_score >= 70:
        potential = "→2X"
    elif percentage_score >= 60:
        potential = "→1.5X"
    else:
        potential = "→1X"
    
    # Anpassen basierend auf anderen Faktoren
    if bounce_detected and volume_trend in ["↑", "↑↑"] and percentage_score >= 75:
        # Wenn bereits ein Bounce erkannt wurde und das Volumen stark ist,
        # könnte das Potential höher sein
        if potential == "→5X": potential = "→7X"
        elif potential == "→3X": potential = "→5X"
        elif potential == "→2X": potential = "→3X"
    elif dip_detected and not bounce_detected and volume_trend in ["↑", "↑↑"]:
        # Wenn ein Dip erkannt wurde, aber noch kein Bounce, ist das ein guter Einstiegspunkt
        # mit möglicherweise höherem Potential
        if percentage_score >= 70:
            if potential == "→3X": potential = "→5X"
            elif potential == "→2X": potential = "→3X"
            elif potential == "→1.5X": potential = "→2X"
    elif volume_trend == "↓↓" and percentage_score < 75:
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
    weights = result["weights"]
    total_score = scores["total"]
    total_weight = sum(weights.values())
    percentage_score = (total_score / total_weight * 100) if total_weight > 0 else 0

    # Berechne prozentuale Scores für jede Kategorie
    pattern_perc = (scores["pattern"] / weights["pattern"] * 100) if weights["pattern"] > 0 else 0
    volume_perc = (scores["volume"] / weights["volume"] * 100) if weights["volume"] > 0 else 0
    timeframe_perc = (scores["timeframe"] / weights["timeframe"] * 100) if weights["timeframe"] > 0 else 0
    rugpull_perc = (scores["rugpull"] / weights["rugpull"] * 100) if weights["rugpull"] > 0 else 0
    
    # Fälle für hohe Scores (>= 85%)
    if percentage_score >= 85:
        if result["bounce_detected"] and result["volume_trend"] in ["↑", "↑↑"]:
            return "Second Bounce mit starkem Volumen"
        elif pattern_perc >= 75 and volume_perc >= 70: # Hohe % in Pattern & Volume
            return "Optimales Kurs- und Volumenmuster"
        else:
            return "Hervorragende Gesamtwerte"
    
    # Fälle für mittlere Scores (70-84%)
    elif percentage_score >= 70:
        if result["dip_detected"] and not result["bounce_detected"]:
            return "Dip erkannt - potenzieller Einstiegspunkt"
        elif result["bounce_detected"]:
            return "Second Bounce im Gange"
        elif volume_perc >= 70: # Hohe % in Volume
            return "Starkes Handelsvolumen"
        else:
            return "Solide Gesamtwerte"
    
    # Fälle für niedrige Scores (< 70%)
    else:
        # Priorisiere die wichtigsten negativen Gründe
        if rugpull_perc < 20: # Sehr niedrige Rugpull-Sicherheit
            return "Hohes Rugpull-Risiko"
        elif volume_perc < 40: # Sehr niedriges Volumen
            return "Zu geringes Handelsvolumen"
        elif pattern_perc < 25: # Sehr schwaches Muster
            return "Kein klares Kursmuster erkennbar"
        elif result["dip_detected"] and volume_perc < 50: # Dip mit schwachem Volumen
            return "Dip mit schwachem Volumen"
        else:
            # Finde die Kategorie mit dem relativ niedrigsten Score
            lowest_cat = min(weights.keys(), key=lambda k: (scores[k] / weights[k]) if weights[k] > 0 else 1)
            if lowest_cat == "rugpull": return "Geringe Rugpull-Sicherheit"
            if lowest_cat == "volume": return "Schwaches Volumen"
            if lowest_cat == "pattern": return "Schwaches Muster"
            if lowest_cat == "timeframe": return "Ungünstige Zeitrahmen"
            return "Unzureichende Gesamtwerte" # Fallback


def scan_tokens_for_strategy(
    mcap_min: float = 100000,
    mcap_max: float = 3000000,
    liquidity_min: float = 30000,
    age_min: int = 0, # Hinzugefügt
    age_max: int = 5, # Hinzugefügt
    min_tx: int = 1000, # Hinzugefügt
    limit: int = 10,
    pattern_weight: int = 40,
    volume_weight: int = 35,
    timeframe_weight: int = 15,
    rugpull_weight: int = 10
) -> List[Dict[str, Any]]:
    """
    Scannt Tokens nach den Strategie-Kriterien.
    
    Args:
        mcap_min: Minimale Marktkapitalisierung
        mcap_max: Maximale Marktkapitalisierung
        liquidity_min: Minimale Liquidität
        age_min: Minimales Token-Alter in Tagen
        age_max: Maximales Token-Alter in Tagen
        min_tx: Minimale Anzahl Transaktionen in 24h
        limit: Maximale Anzahl der zu analysierenden Tokens
        pattern_weight: Gewichtung für Mustererkennung
        volume_weight: Gewichtung für Volumenbestätigung
        timeframe_weight: Gewichtung für Zeitrahmenübereinstimmung
        rugpull_weight: Gewichtung für Rugpull-Sicherheit
        
    Returns:
        Eine Liste mit analysierten Token-Daten, sortiert nach Score
    """
    # Hole gefilterte Tokens (Filterung nach Alter und TX erfolgt später)
    filtered_tokens = get_filtered_tokens(
        mcap_min=mcap_min,
        mcap_max=mcap_max,
        liquidity_min=liquidity_min,
        limit=limit * 2 # Hole mehr Tokens, da wir noch nach Alter/TX filtern
    )
    
    # Analyse jedes Tokens
    results = []
    analyzed_count = 0
    for token in filtered_tokens:
        if analyzed_count >= limit:
            break

        token_address = token.get("address")
        if not token_address:
            continue

        # Überspringe den Aufruf von get_token_info und die Filter für Alter und TX,
        # da /defi/token_overview nicht im Standard-Plan verfügbar ist.
        # und wir die 401-Fehler vermeiden wollen.
        
        # # Hole zusätzliche Token-Infos für Alter und TX (nicht im Standard-Tokenlist-Endpunkt)
        # # Nutze Cache, um API-Aufrufe zu minimieren
        # token_stat = get_token_info(token_address)
        # if not token_stat or not token_stat.get("success", False):
        # #   print(f"Konnte Token-Stat für {token_address} nicht abrufen.")
        #     continue
        
        # # token_stat_data = token_stat.get("data", {})

        # # Filter nach Alter (AUSKOMMENTIERT, da 'created_at' in /token_overview fehlt)
        # # created_at = token_stat_data.get("created_at", 0) 
        # # if created_at:
        # #     from datetime import datetime, timezone
        # #     created_dt = datetime.fromtimestamp(created_at, tz=timezone.utc)
        # #     now = datetime.now(tz=timezone.utc)
        # #     age_days = (now - created_dt).days
        # #     if not (age_min <= age_days <= age_max):
        # #       # print(f"Token {token_address} nach Alter gefiltert ({age_days} Tage)") # Debugging
        # #         continue
        # # else:
        # #   print(f"Kein Erstellungsdatum für {token_address} gefunden (Altersfilter übersprungen).")
        #     # continue # Ohne Alter können wir nicht filtern - Vorerst überspringen statt filtern

        # # Filter nach Transaktionen (verwende 'trade24h' aus /token_overview)
        # # tx_24h = token_stat_data.get("trade24h", 0) # Geändert von tx24h zu trade24h
        # # if tx_24h < min_tx:
        # #   # print(f"Token {token_address} nach TX gefiltert ({tx_24h} TX)") # Debugging
        # #     continue

        # Hole Preis-Historie (z.B. 5m Kerzen für die letzten 24 Stunden)
        # to_ts = int(time.time())
        # from_ts = to_ts - 86400 # 24 * 60 * 60
        
        # price_history = get_token_price_history(token_address, resolution="5m", from_ts=from_ts, to_ts=to_ts)
        price_history = None # Deaktiviere Price History

        # Führe die Analyse mit historischen Daten und Gewichtungen durch
        # Verwende token_stat_data, da es mehr Infos enthält als das token-Objekt aus der Liste
        analysis = analyze_token_for_strategy(
            token, 
            price_history=price_history,
            pattern_weight=pattern_weight,
            volume_weight=volume_weight,
            timeframe_weight=timeframe_weight,
            rugpull_weight=rugpull_weight
        )
        results.append(analysis)
        analyzed_count += 1
    
    # Sortiere nach Gesamt-Score (absteigend)
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
    # Zeige Score relativ zur Gesamtgewichtung an
    total_score = analysis["score"]["total"]
    total_weight = sum(analysis["weights"].values())
    score_display = f"{total_score}/{total_weight}" if total_weight > 0 else f"{total_score}"
    
    potential = calculate_potential_factor(
        total_score, 
        total_weight, 
        analysis["dip_detected"], 
        analysis["bounce_detected"], 
        analysis["volume_trend"]
    )
    volume_trend = analysis["volume_trend"]
    main_reason = analysis["main_reason"]
    
    return (symbol, mcap_str, score_display, potential, volume_trend, main_reason)

# Test-Funktion, wenn direkt ausgeführt
if __name__ == "__main__":
    print("=== Birdeye API Test - Schritt 2 ===")
    
    # API-Key testen
    api_key = get_api_key()
    if api_key:
        print(f"API-Key gefunden: {api_key[:5]}..." + "*" * (len(api_key) - 5))
    else:
        print("Kein API-Key gefunden!")
        exit() # Beenden, wenn kein Key vorhanden ist
    
    print("\n=== Token-Liste Test ===")
    token_list = get_token_list(limit=3)
    if token_list and token_list.get("success", False):
        print("Token-Liste erfolgreich abgerufen!")
        tokens = token_list.get("data", {}).get("tokens", [])
        print(f"Anzahl Tokens: {len(tokens)}")
    else:
        print("Fehler beim Abrufen der Token-Liste")
    
    print("\n=== Strategie-Scan Test ===")
    # Test mit Standard-Gewichtungen
    results = scan_tokens_for_strategy(
        mcap_min=50000,     # 50K
        mcap_max=5000000,   # 5M
        liquidity_min=10000, # 10K
        age_min=0,
        age_max=7,
        min_tx=500,
        limit=5 # Teste mit 5 Tokens
    )
    
    print(f"Anzahl analysierter Tokens: {len(results)}")
    
    for i, analysis in enumerate(results):
        token_data = extract_token_data_for_ui(analysis)
        print(f"\n--- Token {i+1}: {token_data[0]} ---")
        print(f"  MCAP: {token_data[1]}")
        print(f"  Score: {token_data[2]}")
        print(f"  Potential: {token_data[3]}")
        print(f"  Volume-Trend: {token_data[4]}")
        print(f"  Hauptgrund: {token_data[5]}")
        print(f"  Score-Details:")
        print(f"    - Muster:   {analysis['score']['pattern']}/{analysis['weights']['pattern']}")
        print(f"    - Volumen:  {analysis['score']['volume']}/{analysis['weights']['volume']}")
        print(f"    - Zeit:     {analysis['score']['timeframe']}/{analysis['weights']['timeframe']}")
        print(f"    - Sicherheit: {analysis['score']['rugpull']}/{analysis['weights']['rugpull']}")
        # print(f"  Gründe:") # Optional: Detaillierte Gründe ausgeben
        # for reason in analysis["reasons"]:
        #     print(f"    - {reason}")
