import tkinter as tk
from tkinter import ttk
from ui_login import LoginFrame
from db import create_tables, create_spk_tables  
create_tables()
create_spk_tables()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistem Workflow Percetakan")
        self.geometry("1600x800")
        self.resizable(True, True)

        create_tables()

        # Set full screen on start
        self.attributes("-fullscreen", True)

        # Create frame for custom buttons
        self.top_frame = tk.Frame(self)
        self.top_frame.pack(fill="x", side="top", padx=5, pady=5)

        # Add close button
        self.close_button = tk.Button(self.top_frame, text="Close", command=self.on_close)
        self.close_button.pack(side="right", padx=5)

        # Add minimize button
        self.minimize_button = tk.Button(self.top_frame, text="Minimize", command=self.minimize_window)
        self.minimize_button.pack(side="right", padx=5)

        self._frame = None
        self.switch_frame(lambda parent, controller: LoginFrame(parent, controller))

    def switch_frame(self, frame_class, *args):
        if self._frame is not None:
            self._frame.destroy()

        # ✅ Perbaiki agar bisa menerima parameter tambahan
        if args:
            self._frame = frame_class(self, self, *args)
        else:
            self._frame = frame_class(self, self)
        
        self._frame.pack(fill="both", expand=True)

    def show_preview_frame(self, spk_id):
        from spk_preview_frame import SPKPreviewFrame
        self.switch_frame(lambda parent, controller: SPKPreviewFrame(parent, controller, spk_id))

    def on_close(self):
        self.quit()  # Properly exit the application

    def minimize_window(self):
        self.iconify()  # Minimize the window

if __name__ == "__main__":
    app = App()
    app.mainloop()
