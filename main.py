# Hauptanwendung mit korrekter RugCheck-Referenzierung
import tkinter as tk
from ui.main_window import MainWindow
from ui.token_frame import TokenFrame
from ui.stats_frame import StatsFrame
from ui.social_frame import SocialFrame
from ui.recommendation_frame import RecommendationFrame
from ui.calls_tree import CallsTreeView
from ui.watchlist_tree import WatchlistTreeView
from ui.archived_calls_tree import ArchivedCallsTreeView
from ui.main_bot import MainBot

def main():
    # Erstelle das Root-Fenster
    root = tk.Tk()
    
    # Erstelle die Hauptfenster-Instanz
    main_window = MainWindow(root)
    
    # Erstelle die UI-Komponenten für den Main Bot Tab in den neuen Containern
    token_frame = TokenFrame(main_window.main_containers['top_left'], main_window.shared_vars, main_window)
    stats_frame = StatsFrame(main_window.main_containers['middle_left'], main_window.shared_vars, 
                            main_window.time_price_vars, main_window.time_buys_vars, main_window.time_sells_vars)
    social_frame = SocialFrame(main_window.main_containers['middle_right'], main_window.shared_vars, main_window)
    
    # RugCheck und Recommendation-Frames
    recommendation_frame = RecommendationFrame(main_window.main_containers['bottom_right'], main_window.shared_vars, main_window)
    
    # Speichere Referenzen für den späteren Zugriff - WICHTIG!
    main_window.stats_frame = stats_frame
    main_window.social_frame = social_frame
    main_window.recommendation_frame = recommendation_frame
    
    # Erstelle die Treeviews für die Call-Tabs
    calls_tree = CallsTreeView(main_window.tabs['calls'], main_window)
    watchlist_tree = WatchlistTreeView(main_window.tabs['watchlist'], main_window)
    archived_calls_tree = ArchivedCallsTreeView(main_window.tabs['archived'], main_window)
    
    # Speichere Referenzen für den späteren Zugriff
    main_window.calls_tree = calls_tree
    main_window.watchlist_tree = watchlist_tree
    main_window.archived_calls_tree = archived_calls_tree
    main_window.update_calls_tree = calls_tree.update_tree
    main_window.update_watchlist_tree = watchlist_tree.update_tree
    main_window.update_archived_calls_tree = archived_calls_tree.update_tree
    
    # Initialisiere den Main Bot (Hauptfunktionalität)
    main_bot = MainBot(main_window)
    
    # Aktualisiere die Treeviews beim Start
    calls_tree.update_tree()
    watchlist_tree.update_tree()
    archived_calls_tree.update_tree()
    
    # Auto-Refresh starten
    main_bot.auto_refresh_calls()
    
    # Starte die Hauptschleife
    root.mainloop()

if __name__ == "__main__":
    main()