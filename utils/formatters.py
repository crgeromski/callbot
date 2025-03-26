# Formatierungsfunktionen

def format_k(num):
    """Zahl in K/M-Format."""
    try:
        val = float(num)
    except:
        return str(num)
    if abs(val) >= 1_000_000:
        return f"{val/1_000_000:.1f}M"
    elif abs(val) >= 1_000:
        return f"{val/1_000:.0f}K"
    else:
        return f"{val:.0f}"

def format_percentage(num):
    """
    Zahl mit %-Suffix, gerundet auf sinnvolle Werte.
    Für kleine Werte: 1 Dezimalstelle (z.B. 2.5%)
    Für mittlere Werte: Ohne Dezimalstellen (z.B. 25%)
    Für große Werte: Ohne Dezimalstellen (z.B. 250%)
    """
    try:
        value = float(num)
        abs_value = abs(value)
        
        if abs_value < 10:
            # Kleine Werte: Eine Dezimalstelle
            return f"{value:.1f}%"
        elif abs_value < 100:
            # Mittlere Werte: Keine Dezimalstellen
            return f"{int(value)}%"
        else:
            # Große Werte: Keine Dezimalstellen
            return f"{int(value)}%"
    except:
        return str(num)

def parse_km(value: str) -> float:
    """
    Wandelt Strings wie '5K', '2.3K', '1.2M', 'N/A' in einen float-Wert um.
    Gibt 0.0 zurück, wenn der Wert ungültig ist.
    """
    if not value or value == "N/A":
        return 0.0
    value = value.strip().upper()
    try:
        if value.endswith("K"):
            return float(value[:-1]) * 1_000
        elif value.endswith("M"):
            return float(value[:-1]) * 1_000_000
        else:
            return float(value)
    except:
        return 0.0