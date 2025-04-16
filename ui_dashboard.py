# ui_dashboard.py
import tkinter as tk
from ui_input_spk import SPKInputFrame
from lihat_jadwal_frame import LihatJadwalFrame
from lihat_jadwal_frame import LihatJadwalFrame


class DashboardFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        tk.Label(self, text="Dashboard", font=("Arial", 18)).pack(pady=10)

        tk.Button(self, text="Buat SPK", width=20, command=lambda: self.controller.switch_frame(SPKInputFrame)).pack(pady=5)
        tk.Button(self, text="Lihat Pekerjaan", width=20, command=lambda: self.controller.switch_frame(LihatJadwalFrame)).pack(pady=5)
        tk.Button(self, text="Logout", width=20, command=lambda: self.controller.switch_frame(__import__("ui_login").LoginFrame)).pack(pady=5)
