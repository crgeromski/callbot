# Datenspeicherung
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

# Importiere Konfiguration
from config import CALLS_FILE, BUDGET_FILE, DEFAULT_BUDGET

def load_call_data() -> List[Dict[str, Any]]:
    """Lädt die gespeicherten Call-Daten aus der JSON-Datei."""
    if os.path.exists(CALLS_FILE):
        with open(CALLS_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_call_data(calls: List[Dict[str, Any]]) -> None:
    """Speichert die Call-Daten in der JSON-Datei."""
    with open(CALLS_FILE, "w") as f:
        json.dump(calls, f, indent=4)

def save_new_call(call_data: Dict[str, Any]) -> None:
    """Speichert einen neuen Call in der JSON-Datei."""
    calls = load_call_data()
    calls.append(call_data)
    save_call_data(calls)

def create_new_call(symbol: str, mcap: str, liquidity: str, link: str) -> Dict[str, Any]:
    """Erstellt einen neuen Call mit den notwendigen Daten."""
    return {
        "Datum": datetime.now().strftime("%d.%m."),
        "Symbol": symbol,
        "MCAP_at_Call": mcap,
        "Link": link,
        "Aktuelles_MCAP": mcap,  # initial gleich MCAP_at_Call
        "X_Factor": "",      # Platzhalter, wird später im Live-Update berechnet
        "PL_Percent": "",    # Platzhalter
        "PL_Dollar": "",     # Platzhalter
        "Invest": "10"       # Fester Investitionswert: 10$
    }


def load_budget() -> float:
    """Lädt den gespeicherten Kontostand."""
    try:
        if os.path.exists(BUDGET_FILE):
            with open(BUDGET_FILE, "r") as f:
                return float(f.read().strip())
    except Exception:
        pass
    return DEFAULT_BUDGET

def save_budget(budget: float) -> None:
    """Speichert den aktuellen Kontostand."""
    try:
        with open(BUDGET_FILE, "w") as f:
            f.write(str(budget))
    except Exception as e:
        print(f"Budget-Backup fehlgeschlagen: {e}")

def calculate_total_profit() -> tuple:
    """
    Berechnet den Gesamtgewinn/Verlust aller aktiven (nicht abgeschlossenen) Calls.
    
    Returns:
        Tuple mit (total_profit, profit_percentage)
    """
    total_profit = 0.0
    calls = load_call_data()
    for call in calls:
        # Falls der Call abgeschlossen ist, überspringe diesen Call
        if call.get("abgeschlossen", False):
            continue

        try:
            # Entfernt das Dollarzeichen und wandelt in float um
            profit = float(call.get("PL_Dollar", "0").rstrip("$"))
        except Exception:
            profit = 0.0
        total_profit += profit
    profit_percentage = (total_profit / DEFAULT_BUDGET) * 100
    return total_profit, profit_percentage

def find_call_by_symbol(symbol: str, data=None):
    """
    Findet einen Call anhand des Symbols.
    
    Args:
        symbol: Token-Symbol zum Suchen (z.B. '$MUPPET')
        data: Optional. Vorhandene Daten von der API, falls bereits abgerufen.
    
    Returns:
        Dictionary mit Call-Daten oder None, wenn kein Eintrag gefunden wurde.
    """
    if not data:
        from data.api import fetch_dexscreener_data
        from utils.formatters import parse_km
        import json

    # Hole aktuellste Calls
    calls = load_call_data()
    target_call = next((call for call in calls if call.get("Symbol", "") == symbol), None)
    
    if not target_call:
        return None
    
    # Wenn kein Datenparameter übergeben wurde, rufe Daten von API ab
    if not data:
        link = target_call.get("Link", "")
        if not link:
            return None
        
        data = fetch_dexscreener_data(link)
    
    if not data or 'pairs' not in data or not data['pairs']:
        return None
    
    pair_info = data['pairs'][0]
    
    return pair_info