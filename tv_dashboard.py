import tkinter as tk
from lihat_jadwal_frame import LihatJadwalFrame

class TVLihatJadwal(tk.Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.title("Lihat Jadwal SPK - TV Monitor")
        self.state("zoomed")
        self.configure(bg="#ecf0f1")

        # Pasang frame jadwal
        self.jadwal_frame = LihatJadwalFrame(self, controller=root, readonly=True)
        self.jadwal_frame.pack(fill="both", expand=True)
        self.jadwal_frame.auto_refresh()

        self.scroll_direction = 1  # 1 untuk scroll ke bawah, -1 ke atas
        self.after(2000, self.auto_scroll)  # Mulai auto scroll tiap 2 detik

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
            canvas = self.jadwal_frame.scrollable.canvas
            table_frame = self.jadwal_frame.table_frame

            # Hitung jumlah baris data
            total_widgets = len(table_frame.winfo_children())
            column_count = len(self.jadwal_frame.headers)
            row_count = total_widgets // column_count - 1 

            if row_count > 7:
                canvas.yview_scroll(7 * self.scroll_direction, "units")
                top, bottom = canvas.yview()
                if bottom >= 1.0:
                    self.scroll_direction = -1
                elif top <= 0.0:
                    self.scroll_direction = 1

        except Exception as e:
            print("Auto-scroll error:", e)

        self.after(10000, self.auto_scroll)
