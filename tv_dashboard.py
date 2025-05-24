import tkinter as tk
from lihat_jadwal_frame import LihatJadwalFrame

class TVLihatJadwal(tk.Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.title("Lihat Jadwal SPK - TV Monitor")
        self.state("zoomed")  # ✅ fullscreen dengan titlebar (lebih stabil)
        self.configure(bg="#ecf0f1")

        # Pasang frame jadwal
        self.jadwal_frame = LihatJadwalFrame(self, controller=root, readonly=True)
        self.jadwal_frame.pack(fill="both", expand=True)
        self.jadwal_frame.auto_refresh()

        # Tombol ESC untuk keluar dari mode TV
        self.bind("<Escape>", self.keluar_fullscreen)

    def keluar_fullscreen(self, event=None):
        self.root.tv_window = None
        self.destroy()
        self.root.state("zoomed")

    def tampilkan_tv(self):
        tv = TVLihatJadwal(self.controller)
        self.controller.tv_window = tv
        tv.focus_set()

    def auto_scroll(self):
        try:
            scrollable_frame = self.jadwal_frame.children["!scrollableframe"]
            canvas = scrollable_frame.canvas
            canvas.yview_scroll(3, "units")
        except Exception as e:
            print("Auto-scroll error:", e)
        self.after(5000, self.auto_scroll)
