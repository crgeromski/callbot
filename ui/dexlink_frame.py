# DexLink-Eingabe Frame
import tkinter as tk

class DexLinkFrame:
    def __init__(self, parent, shared_vars, main_window):
        self.parent = parent
        self.shared_vars = shared_vars
        self.main_window = main_window
        self.create_frame()
        
    def create_frame(self):
        """Erstellt den Frame für DexLink-Eingabe"""
        self.frame = tk.Frame(
            self.parent, 
            bg="white", 
            padx=20, 
            pady=20
        )
        self.frame.pack(fill="both", expand=True)
        

        
        # Eingabefeld und Button
        entry_frame = tk.Frame(self.frame, bg="white")
        entry_frame.pack(fill="x", pady=(0,10))
        
        entry = tk.Entry(entry_frame, textvariable=self.shared_vars['entry_var'])
        entry.pack(side="left", fill="x", expand=True, padx=(0,5))
        entry.bind("<Return>", lambda event: self.main_window.fetch_data())
        # Platzhaltertext hinzufügen
        entry.insert(0, "Link oder CA einfügen")
        entry.config(fg="#888888")  # Hellgrau für bessere Transparenz-Wirkung

        # Event-Handler für Fokusgewinn und -verlust
        def on_entry_focus_in(event):
            if entry.get() == "Link oder CA einfügen":
                entry.delete(0, "end")
                entry.config(fg="black")

        def on_entry_focus_out(event):
            if not entry.get():
                entry.insert(0, "Link oder CA einfügen")
                entry.config(fg="#888888")

        entry.bind("<FocusIn>", on_entry_focus_in)
        entry.bind("<FocusOut>", on_entry_focus_out)
        
        # Paste-Button mit Icon
        def paste_from_clipboard():
            try:
                clipboard_content = self.main_window.root.clipboard_get()
                self.shared_vars['entry_var'].set(clipboard_content)
                self.main_window.fetch_data()
            except Exception as e:
                import tkinter.messagebox as messagebox
                messagebox.showerror("Fehler", f"Konnte Zwischenablage nicht verarbeiten: {e}")

        paste_btn = tk.Button(
            entry_frame, 
            text="📋", 
            width=2,
            command=paste_from_clipboard
        )
        paste_btn.pack(side="right")