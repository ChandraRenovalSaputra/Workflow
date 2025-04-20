import tkinter as tk
from tkinter import ttk
from ui_input_spk import SPKInputFrame
from lihat_jadwal_frame import LihatJadwalFrame


class DashboardFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f2f5")
        self.controller = controller

        # === Header ===
        header = tk.Frame(self, bg="#0078D7", height=60)
        header.pack(side="top", fill="x")

        title = tk.Label(header, text="📋 Dashboard Workflow Percetakan", font=("Segoe UI", 18, "bold"), bg="#0078D7", fg="white")
        title.pack(side="left", padx=20, pady=10)

        logout_btn = tk.Button(header, text="Logout", command=self.logout, bg="white", fg="#0078D7", font=("Segoe UI", 10, "bold"),
                               relief="flat", cursor="hand2", padx=10, pady=5)
        logout_btn.pack(side="right", padx=20, pady=10)

        # === Welcome Section ===
        user = getattr(controller, "current_user", (None, "User", None))  # fallback tuple
        welcome = tk.Label(self, text=f"Halo, {user[1]} 👋", font=("Segoe UI", 16), bg="#f0f2f5", fg="#333")

        welcome.pack(pady=(30, 10))

        subtitle = tk.Label(self, text="Buat pekerjaanmu lebih mudah", font=("Segoe UI", 12), bg="#f0f2f5", fg="#666")
        subtitle.pack()

       

        # === Tombol Aksi Utama ===
        button_frame = tk.Frame(self, bg="#f0f2f5")
        button_frame.pack(pady=(10, 40))

        # Tombol Buat SPK
        tk.Button(
            button_frame, 
            text="➕ Buat SPK", 
            width=20, 
            height=2, 
            command=lambda: self.controller.switch_frame(SPKInputFrame), 
            bg="#007BFF", 
            fg="white", 
            font=("Helvetica", 14), 
            relief="flat", 
            padx=10, 
            pady=10
        ).pack(pady=10)

        # Tombol Lihat Pekerjaan
        tk.Button(
            button_frame, 
            text="📄 Lihat Pekerjaan", 
            width=20, 
            height=2, 
            command=lambda: self.controller.switch_frame(LihatJadwalFrame), 
            bg="#4CAF50", 
            fg="white", 
            font=("Helvetica", 14), 
            relief="flat", 
            padx=10, 
            pady=10
        ).pack(pady=10)


        # === Placeholder for more features ===
        tk.Label(self, text="© PT Percetakan.", font=("Segoe UI", 11), bg="#f0f2f5", fg="#999").pack(pady=(50, 10))

    def create_card(self, parent, title, count, color):
        card = tk.Frame(parent, bg="white", bd=0, relief="flat", padx=20, pady=20, highlightthickness=1, highlightbackground="#ddd")
        card.pack(side="left", padx=15)

        lbl_title = tk.Label(card, text=title, font=("Segoe UI", 12), bg="white", fg="#333")
        lbl_title.pack(anchor="w")

        lbl_count = tk.Label(card, text=count, font=("Segoe UI", 24, "bold"), bg="white", fg=color)
        lbl_count.pack(anchor="w", pady=(5, 0))

    def logout(self):
        from ui_login import LoginFrame
        self.controller.switch_frame(LoginFrame)