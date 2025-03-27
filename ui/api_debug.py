# api_debug.py
import requests
import sys
import os
import config
import time

def check_environment():
    """Überprüft die Umgebungsvariablen und den API-Key"""
    print("=== Umgebungsprüfung ===")
    print(f"Python-Version: {sys.version}")
    print(f"API-Key vorhanden: {'Ja' if config.AXIOM_API_KEY else 'Nein'}")
    print(f"API-Key-Länge: {len(config.AXIOM_API_KEY) if config.AXIOM_API_KEY else 0}")
    print(f"API_KEY_FILE existiert: {os.path.exists(config.API_KEY_FILE)}")
    if os.path.exists(config.API_KEY_FILE):
        try:
            with open(config.API_KEY_FILE, "r") as f:
                file_key = f.read().strip()
                print(f"API-Key aus Datei (erste 5 Zeichen): {file_key[:5]}...")
        except Exception as e:
            print(f"Fehler beim Lesen der API-Key-Datei: {e}")

def test_basic_connection():
    """Testet die grundlegende Verbindung zu bekannten Servern"""
    print("\n=== Grundlegende Verbindungstests ===")
    
    # Bekannte Dienste testen
    test_urls = [
        "https://www.google.com",
        "https://api.solanatracker.io",  # Überprüfe nur, ob die Domain erreichbar ist
    ]
    
    for url in test_urls:
        try:
            print(f"Teste Verbindung zu {url}...")
            start_time = time.time()
            response = requests.get(url, timeout=5)
            elapsed = time.time() - start_time
            print(f"  Erfolg! Statuscode: {response.status_code}, Zeit: {elapsed:.2f}s")
        except requests.exceptions.Timeout:
            print(f"  Timeout bei der Verbindung zu {url}")
        except requests.exceptions.ConnectionError:
            print(f"  Verbindungsfehler bei {url}")
        except Exception as e:
            print(f"  Fehler bei {url}: {e}")

def test_axiom_api():
    """Testet die Axiom API mit einem bekannten Token"""
    print("\n=== Axiom API Test ===")
    
    # Bekannter Solana-Token (USDC)
    test_token = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    
    # API-Endpunkt
    api_url = f"https://api.solanatracker.io/tokens/{test_token}"
    
    # Headers mit API-Key
    headers = {
        "X-API-KEY": config.AXIOM_API_KEY,
        "Content-Type": "application/json"
    }
    
    print(f"API-URL: {api_url}")
    print(f"API-Key (erste 5 Zeichen): {config.AXIOM_API_KEY[:5] if config.AXIOM_API_KEY else 'Kein Key'}")
    
    try:
        print("Sende Anfrage an Axiom API...")
        start_time = time.time()
        response = requests.get(api_url, headers=headers, timeout=15)
        elapsed = time.time() - start_time
        
        print(f"Antwort erhalten in {elapsed:.2f}s mit Statuscode: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Daten erhalten! Enthält {len(data)} Felder")
            print("Einige Schlüssel der Antwort:", list(data.keys()) if isinstance(data, dict) else "Keine Schlüssel (kein Dict)")
        else:
            print(f"Fehler-Antwort: {response.text}")
    except requests.exceptions.Timeout:
        print("Timeout bei der Anfrage an die Axiom API")
    except requests.exceptions.ConnectionError:
        print("Verbindungsfehler bei der Anfrage an die Axiom API")
    except requests.exceptions.RequestException as e:
        print(f"Request-Fehler: {e}")
    except Exception as e:
        print(f"Unerwarteter Fehler: {e}")

def test_axiom_token_data(token_address):
    """Testet die Abfrage von Token-Daten mit deiner eigenen Implementierung"""
    print(f"\n=== Test axiom_api.fetch_axiom_data für {token_address} ===")
    
    # Importiere deine eigene Implementierung
    import data.axiom_api as axiom_api
    
    try:
        print("Rufe fetch_axiom_data auf...")
        start_time = time.time()
        result = axiom_api.fetch_axiom_data(token_address, timeout=10)
        elapsed = time.time() - start_time
        
        print(f"Antwort erhalten in {elapsed:.2f}s")
        if result:
            print(f"Erfolg! Daten enthalten {len(result)} Felder")
            print("Einige Schlüssel:", list(result.keys()) if isinstance(result, dict) else "Keine Schlüssel")
        else:
            print("Keine Daten erhalten (None)")
    except Exception as e:
        print(f"Fehler: {e}")

if __name__ == "__main__":
    print("=== Axiom API Debug-Tool ===")
    check_environment()
    test_basic_connection()
    test_axiom_api()
    
    # Test mit einem bekannten Token (USDC)
    test_axiom_token_data("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")