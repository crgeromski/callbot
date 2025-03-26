# Hauptanwendung
import tkinter as tk
from ui.main_window import MainWindow
from ui.token_frame import TokenFrame
from ui.stats_frame import StatsFrame
from ui.social_frame import SocialFrame
from ui.xpost_frame import XPostFrame
from ui.call_frame import CallFrame
from ui.calls_tree import CallsTreeView
from ui.archived_calls_tree import ArchivedCallsTreeView
from ui.main_bot import MainBot
#from ui.future_function_frame_1 import FutureFunctionFrame1
#from ui.future_function_frame_2 import FutureFunctionFrame2

def main():
    # Erstelle das Root-Fenster
    root = tk.Tk()
    
    # Erstelle die Hauptfenster-Instanz
    main_window = MainWindow(root)
    
    # Erstelle die UI-Komponenten für den Main Bot Tab
    token_frame = TokenFrame(main_window.tabs['main'], main_window.shared_vars)
    stats_frame = StatsFrame(main_window.tabs['main'], main_window.shared_vars, 
                            main_window.time_price_vars, main_window.time_buys_vars, main_window.time_sells_vars)
    social_frame = SocialFrame(main_window.tabs['main'], main_window.shared_vars)
    xpost_frame = XPostFrame(main_window.tabs['main'], main_window.shared_vars)
    call_frame = CallFrame(main_window.tabs['main'], main_window.shared_vars, main_window)
    
    # Speichere Referenzen für den späteren Zugriff
    main_window.stats_frame = stats_frame
    main_window.xpost_frame = xpost_frame
    
    # Erstelle die Treeviews für die Call-Tabs
    calls_tree = CallsTreeView(main_window.tabs['calls'], main_window)
    archived_calls_tree = ArchivedCallsTreeView(main_window.tabs['archived'], main_window)
    
    # Speichere Referenzen für den späteren Zugriff
    main_window.calls_tree = calls_tree
    main_window.archived_calls_tree = archived_calls_tree
    main_window.update_calls_tree = calls_tree.update_tree
    main_window.update_archived_calls_tree = archived_calls_tree.update_tree
    
    # Initialisiere den Main Bot (Hauptfunktionalität)
    main_bot = MainBot(main_window)
    
    # Aktualisiere die Treeviews beim Start
    calls_tree.update_tree()
    archived_calls_tree.update_tree()
    
    # Starte das Live-Update, wenn es aktiv ist
    if main_window.shared_vars['live_update_active'].get():
        main_bot.auto_refresh_calls()
    
    # Starte die Hauptschleife
    root.mainloop()

if __name__ == "__main__":
    main()