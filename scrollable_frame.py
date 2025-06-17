import tkinter as tk
from tkinter import ttk
import platform

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        
        # Canvas dan Scrollbar
        self.canvas = tk.Canvas(self, borderwidth=0, background="#f0f2f5", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, background="#f0f2f5")
        
        # Konfigurasi scroll region
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        # Buat window di canvas
        self.window_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Konfigurasi canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Packing
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Binding mousewheel
        self._bind_mousewheel()
        self.bind("<Destroy>", self._on_destroy)

    def _on_canvas_configure(self, event):
        """Atur lebar scrollable frame saat canvas di-resize"""
        canvas_width = event.width
        self.canvas.itemconfig(self.window_id, width=canvas_width)

    def _bind_mousewheel(self):
        """Binding mousewheel yang spesifik untuk widget ini"""
        self.canvas.bind("<Enter>", self._bind_to_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_from_mousewheel)

    def _bind_to_mousewheel(self, event):
        """Aktifkan scroll hanya saat mouse di atas canvas"""
        os_name = platform.system()
        if os_name == 'Windows':
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        elif os_name == 'Darwin':  # macOS
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel_mac)
        else:  # Linux
            self.canvas.bind_all("<Button-4>", self._on_mousewheel_linux_up)
            self.canvas.bind_all("<Button-5>", self._on_mousewheel_linux_down)

    def _unbind_from_mousewheel(self, event):
        """Nonaktifkan scroll saat mouse meninggalkan canvas"""
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        """Handler mousewheel untuk Windows"""
        if self.winfo_exists():  # Pastikan widget masih ada
            self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def _on_mousewheel_mac(self, event):
        """Handler mousewheel untuk Mac"""
        if self.winfo_exists():
            self.canvas.yview_scroll(-1 * event.delta, "units")

    def _on_mousewheel_linux_up(self, event):
        """Handler scroll up untuk Linux"""
        if self.winfo_exists():
            self.canvas.yview_scroll(-1, "units")

    def _on_mousewheel_linux_down(self, event):
        """Handler scroll down untuk Linux"""
        if self.winfo_exists():
            self.canvas.yview_scroll(1, "units")

    def _on_destroy(self, event):
        """Cleanup saat widget dihancurkan"""
        self._unbind_from_mousewheel(None)

    def get_scrollable_frame(self):
        return self.scrollable_frame