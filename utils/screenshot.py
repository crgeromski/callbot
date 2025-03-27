# Screenshot-Funktionen
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
from datetime import datetime
from tkinter import messagebox

def take_chart_screenshot(url, save_dir="screenshots"):
    """
    Nimmt einen Screenshot vom Chart-Bereich auf Dexscreener auf.
    
    Args:
        url: Der Dexscreener-Link
        save_dir: Das Verzeichnis zum Speichern der Screenshots
    
    Returns:
        Der Pfad zum gespeicherten Screenshot oder None bei Fehler
    """
    if "dexscreener.com" not in url:
        print(f"Ungültiger Dexscreener-Link: {url}")
        return None
    
    # Erstelle das Verzeichnis, falls es nicht existiert
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # Setze Chrome-Optionen
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Unsichtbarer Modus
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    
    try:
        # Browser initialisieren
        print("Browser wird initialisiert...")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        # Seite laden
        print(f"Lade Seite: {url}")
        driver.get(url)
        
        # Warte bis die Seite vollständig geladen ist
        time.sleep(5)  # Erhöhte Wartezeit für vollständiges Laden
        
        # Mache einen Screenshot der ganzen Seite als Fallback
        full_screenshot_path = os.path.join(save_dir, f"full_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        driver.save_screenshot(full_screenshot_path)
        print(f"Vollständiger Screenshot gespeichert: {full_screenshot_path}")
        
        # Warte auf Chart-Element
        print("Suche nach Chart-Element...")
        wait = WebDriverWait(driver, 20)
        
        # Aktualisierte Selektoren für den Chart (basierend auf neuer Dexscreener-Struktur)
        selectors = [
            "div.card-body",  # Container-Element für Chart
            "div.chart-container",
            "div[data-testid='price-chart']",
            "div.tradingview-chart",
            "canvas",  # Manchmal ist das Canvas-Element direkt verfügbar
            "svg",     # Manchmal ist ein SVG-Element statt Canvas verwendet
            "div.chart",
            "div.relative div.w-full" # Breiterer Ansatz
        ]
        
        chart_element = None
        for selector in selectors:
            try:
                print(f"Versuche Selektor: {selector}")
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    # Nehme das erste gefundene Element
                    chart_element = elements[0]
                    print(f"Chart-Element gefunden mit Selektor: {selector}")
                    break
            except Exception as e:
                print(f"Fehler bei Selektor {selector}: {e}")
                continue
        
        if not chart_element:
            print("Chart-Element konnte nicht gefunden werden. Verwende vollständigen Screenshot.")
            return full_screenshot_path
        
        # Scrolle zum Chart-Element
        driver.execute_script("arguments[0].scrollIntoView();", chart_element)
        time.sleep(2)  # Warte kurz nach dem Scrollen
        
        # Timestamp für den Dateinamen
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Token-Symbol aus URL extrahieren
        token_parts = url.split("/")
        token_identifier = token_parts[-1][:10]  # Nimm die ersten 10 Zeichen
        
        # Pfad für den Screenshot
        screenshot_path = os.path.join(save_dir, f"chart_{token_identifier}_{timestamp}.png")
        
        # Screenshot des Elements
        print("Erstelle Screenshot...")
        chart_element.screenshot(screenshot_path)
        
        # Falls element.screenshot nicht funktioniert, versuche alternative Methode
        if not os.path.exists(screenshot_path) or os.path.getsize(screenshot_path) == 0:
            print("Element-Screenshot fehlgeschlagen, verwende Standard-Screenshot...")
            driver.save_screenshot(screenshot_path)
        
        # Browser schließen
        driver.quit()
        
        print(f"Screenshot gespeichert unter: {screenshot_path}")
        return screenshot_path
    
    except Exception as e:
        print(f"Fehler beim Erstellen des Screenshots: {e}")
        if 'driver' in locals():
            driver.quit()
        return None