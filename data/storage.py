# Datenspeicherung
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

# Importiere Konfiguration
from config import CALLS_FILE, BACKUP_FILE, BUDGET_FILE, DEFAULT_BUDGET

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
        "Datum": datetime.now().strftime("%d.%m.%Y"),
        "Symbol": symbol,
        "MCAP_at_Call": mcap,
        "Liquidity_at_Call": liquidity,
        "Link": link,
        "Aktuelles_MCAP": mcap,  # initial gleich MCAP_at_Call
        "Live_Liquidity": liquidity,  # initial gleich Liquidity_at_Call
        "X_Factor": "",      # Platzhalter, wird später im Live-Update berechnet
        "PL_Percent": "",    # Platzhalter
        "PL_Dollar": "",     # Platzhalter
        "Invest": "10"       # Fester Investitionswert: 10$
    }

def backup_calls() -> None:
    """Erstellt ein Backup der Calls-Datei."""
    try:
        calls = load_call_data()
        with open(BACKUP_FILE, "w") as f:
            json.dump(calls, f, indent=4)
    except Exception as e:
        print(f"Backup fehlgeschlagen: {e}")

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