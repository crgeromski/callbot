# Datenspeicherung
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

# Importiere Konfiguration
from config import CALLS_FILE, BUDGET_FILE, DEFAULT_BUDGET, WATCHLIST_FILE, BACKUP_FILE

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
    # Nach dem Speichern der Calls auch das Backup aktualisieren
    create_backup()

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
        "X_Factor": "1.0X",      # Initialer X-Factor: 1.0
        "PL_Percent": "0%",      # Initialer Wert
        "PL_Dollar": "0.00$",    # Initialer Wert
        "Invest": "10"           # Fester Investitionswert: 10$
    }

def load_watchlist_data() -> List[Dict[str, Any]]:
    """Lädt die gespeicherten Beobachtungsliste-Daten aus der JSON-Datei."""
    if os.path.exists(WATCHLIST_FILE):
        with open(WATCHLIST_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_watchlist_data(watchlist: List[Dict[str, Any]]) -> None:
    """Speichert die Beobachtungsliste-Daten in der JSON-Datei."""
    with open(WATCHLIST_FILE, "w") as f:
        json.dump(watchlist, f, indent=4)
    # Nach dem Speichern der Watchlist auch das Backup aktualisieren
    create_backup()

def save_new_watchlist_item(item_data: Dict[str, Any]) -> None:
    """Speichert einen neuen Beobachtungsliste-Eintrag in der JSON-Datei."""
    watchlist = load_watchlist_data()
    watchlist.append(item_data)
    save_watchlist_data(watchlist)

def create_new_watchlist_item(symbol: str, mcap: str, link: str) -> Dict[str, Any]:
    """Erstellt einen neuen Beobachtungsliste-Eintrag mit den notwendigen Daten."""
    return {
        "Datum": datetime.now().strftime("%d.%m."),
        "Symbol": symbol,
        "MCAP_at_Call": mcap,
        "Link": link,
        "Aktuelles_MCAP": mcap,  # initial gleich MCAP_at_Call
        "X_Factor": "1.0X",      # initialer X-Factor: 1.0
        "PL_Percent": "0%",      # initial 0%
        "PL_Dollar": "0.00$",    # initial 0.00$
        "Invest": "10"           # fiktiver Invest-Wert für Anzeige
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
        # Nach dem Speichern des Budgets auch das Backup aktualisieren
        create_backup()
    except Exception as e:
        print(f"Budget-Backup fehlgeschlagen: {e}")

def create_backup() -> None:
    """
    Erstellt ein umfassendes Backup aller wichtigen Daten.
    Enthält: Kontostand, aktive Calls, Beobachtungsliste und Timestamp.
    """
    try:
        # Lade alle benötigten Daten
        budget = load_budget()
        calls = load_call_data()
        watchlist = load_watchlist_data()
        
        # Erstelle Backup-Struktur
        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "budget": budget,
            "calls": calls,
            "watchlist": watchlist
        }
        
        # Speichere Backup-Daten
        with open(BACKUP_FILE, "w") as f:
            json.dump(backup_data, f, indent=4)
    except Exception as e:
        print(f"Vollständiges Backup fehlgeschlagen: {e}")

def restore_from_backup() -> bool:
    """
    Stellt Daten aus dem Backup wieder her.
    
    Returns:
        bool: True bei erfolgreicher Wiederherstellung, sonst False
    """
    try:
        if not os.path.exists(BACKUP_FILE):
            return False
            
        # Lade Backup-Daten
        with open(BACKUP_FILE, "r") as f:
            backup_data = json.load(f)
            
        # Prüfe, ob alle erforderlichen Daten vorhanden sind
        if not all(key in backup_data for key in ["budget", "calls", "watchlist"]):
            return False
            
        # Stelle Daten wieder her
        save_budget(backup_data["budget"])
        save_call_data(backup_data["calls"])
        save_watchlist_data(backup_data["watchlist"])
        
        return True
    except Exception as e:
        print(f"Wiederherstellung aus Backup fehlgeschlagen: {e}")
        return False

def calculate_total_profit() -> float:
    """
    Berechnet den Gesamtgewinn/Verlust aller aktiven Calls.
    
    Returns:
        Float mit dem Gesamtgewinn/Verlust in Dollar
    """
    total_profit = 0.0
    calls = load_call_data()
    
    # Summe aller PL_Dollar-Werte (nur von aktiven Calls)
    for call in calls:
        # Ignoriere abgeschlossene Calls
        if call.get("abgeschlossen", False):
            continue
            
        try:
            # Entfernt das Dollarzeichen und wandelt in float um
            profit = float(call.get("PL_Dollar", "0").rstrip("$"))
            total_profit += profit
        except Exception:
            continue
            
    return total_profit

def calculate_today_profit() -> float:
    """
    Berechnet den Gewinn/Verlust aller Calls vom heutigen Tag.
    
    Returns:
        Float mit dem heutigen Gewinn/Verlust in Dollar
    """
    today_profit = 0.0
    calls = load_call_data()
    
    # Aktuelles Datum im Format "DD.MM."
    today = datetime.now().strftime("%d.%m.")
    
    # Nur Calls vom heutigen Tag berücksichtigen (nur aktive)
    for call in calls:
        # Ignoriere abgeschlossene Calls
        if call.get("abgeschlossen", False):
            continue
            
        if call.get("Datum") != today:
            continue
            
        try:
            # Entfernt das Dollarzeichen und wandelt in float um
            profit = float(call.get("PL_Dollar", "0").rstrip("$"))
            today_profit += profit
        except Exception:
            continue
            
    return today_profit

def count_active_calls() -> int:
    """Zählt die aktiven (nicht abgeschlossenen) Calls."""
    calls = load_call_data()
    return sum(1 for call in calls if not call.get("abgeschlossen", False))

def calculate_current_balance() -> float:
    """
    Berechnet den aktuellen Kontostand als:
    DEFAULT_BUDGET (500$) + Gesamt-Profit aller aktiven und abgeschlossenen Calls
    
    Returns:
        Float mit dem aktuellen Kontostand in Dollar
    """
    # Lade das Start-Budget
    base_budget = DEFAULT_BUDGET
    
    # Berechne den Gesamt-P/L aller Calls (aktiv und abgeschlossen)
    total_profit = 0.0
    calls = load_call_data()
    
    for call in calls:
        try:
            profit = float(call.get("PL_Dollar", "0").rstrip("$"))
            total_profit += profit
        except Exception:
            continue
    
    # Aktueller Kontostand
    current_balance = base_budget + total_profit
    
    # Speichere den aktuellen Kontostand
    save_budget(current_balance)
    
    return current_balance

def calculate_total_investment() -> float:
    """
    Berechnet den aktuell investierten Betrag (10$ pro aktiven Call).
    
    Returns:
        Float mit dem investierten Betrag in Dollar
    """
    active_calls_count = count_active_calls()
    return active_calls_count * 10.0  # 10$ pro aktivem Call

def calculate_average_profit_per_call() -> float:
    """
    Berechnet den durchschnittlichen Gewinn/Verlust pro Call.
    
    Returns:
        Float mit dem durchschnittlichen Gewinn/Verlust pro Call
    """
    total_profit = calculate_total_profit()
    active_calls_count = count_active_calls()
    
    if active_calls_count > 0:
        return total_profit / active_calls_count
    else:
        return 0.0

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
        # Wenn nicht in den Calls gefunden, suche in der Watchlist
        watchlist = load_watchlist_data()
        target_call = next((item for item in watchlist if item.get("Symbol", "") == symbol), None)
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