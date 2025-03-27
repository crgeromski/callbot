# Konfigurationsvariablen
import os

# Dateipfade
CALLS_FILE = "calls.json"
BUDGET_FILE = "budget_backup.txt"
API_KEY_FILE = "api_key.txt"  # Datei für den Axiom API-Key

# Standardwerte
DEFAULT_BUDGET = 500.0
DEFAULT_WINDOW_SIZE = "630x1127+1913+0"
DEFAULT_WINDOW_TITLE = "Dexscreener Bot"

# API Konfiguration
API_TIMEOUT = 10  # Sekunden
UPDATE_INTERVAL = 30000  # Millisekunden (30 Sekunden)

# Axiom API Konfiguration
AXIOM_API_KEY = os.environ.get('AXIOM_API_KEY', '')  # Zuerst nach Umgebungsvariable suchen

# Versuche, den API-Key aus der Datei zu laden, wenn Umgebungsvariable leer ist
if not AXIOM_API_KEY:
    try:
        if os.path.exists(API_KEY_FILE):
            with open(API_KEY_FILE, "r") as f:
                AXIOM_API_KEY = f.read().strip()
    except Exception as e:
        print(f"Fehler beim Laden des API-Keys: {e}") 