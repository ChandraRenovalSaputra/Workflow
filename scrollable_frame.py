import tkinter as tk
from tkinter import ttk
import platform

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)

        self.canvas = tk.Canvas(self, borderwidth=0, background="#f0f2f5")
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, background="#f0f2f5")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.bind_mousewheel()

    def bind_mousewheel(self):
        os_name = platform.system()
        if os_name == 'Windows':
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        elif os_name == 'Darwin':  # macOS
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel_mac)
        else:  # Linux
            self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
            self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def _on_mousewheel_mac(self, event):
        self.canvas.yview_scroll(-1 * (event.delta), "units")
