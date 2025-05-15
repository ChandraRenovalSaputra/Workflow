import tkinter as tk
from lihat_jadwal_frame import LihatJadwalFrame  # sesuaikan nama file dan kelas

class TVLihatJadwal(tk.Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.title("Lihat Jadwal SPK - TV Monitor")
        self.attributes('-fullscreen', True)
        self.configure(bg="#ecf0f1")

        # Pasang frame jadwal di sini
        self.jadwal_frame = LihatJadwalFrame(self, controller=root)
        self.jadwal_frame.pack(fill="both", expand=True)

        # Bind tombol Escape untuk keluar fullscreen
        self.bind("<Escape>", lambda e: self.destroy())
