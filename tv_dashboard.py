import tkinter as tk
from lihat_jadwal_frame import LihatJadwalFrame

class TVLihatJadwal(tk.Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.root = root  # simpan referensi ke root utama
        self.title("Lihat Jadwal SPK - TV Monitor")
        self.attributes('-fullscreen', True)
        self.configure(bg="#ecf0f1")

        # Pasang frame jadwal
        self.jadwal_frame = LihatJadwalFrame(self, controller=root)
        self.jadwal_frame.pack(fill="both", expand=True)
        self.jadwal_frame.auto_refresh()

        # Bind tombol ESC untuk keluar fullscreen
        self.bind("<Escape>", self.keluar_fullscreen)  # ✅ panggil method pakai self

    def keluar_fullscreen(self, event=None):  # ✅ method class yang benar
        self.root.tv_window = None  # bersihkan referensi TV
        self.destroy()
        self.root.state("zoomed")  # kembali ke fullscreen


    def tampilkan_tv(self):
        tv = TVLihatJadwal(self.controller)
        self.controller.tv_window = tv  # 🆕 simpan referensi
        tv.focus_set()