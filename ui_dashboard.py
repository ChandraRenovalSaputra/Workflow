import tkinter as tk
from tkinter import ttk
from ui_input_spk import SPKInputFrame
from lihat_jadwal_frame import LihatJadwalFrame
from ui_profile import ProfileFrame
from tv_dashboard import TVLihatJadwal

class DashboardFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f4f6f9")
        self.controller = controller
        self.build_main_content()
        self.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        # Cetak ukuran baru ke terminal (debugging)
        print(f"Resize: {event.width} x {event.height}")

    def build_main_content(self):
        # === Header ===
        header = tk.Frame(self, bg="#1e3a8a", height=80)
        header.pack(side="top", fill="x")

        title = tk.Label(header, text="📋 Dashboard Workflow Percetakan",
                         font=("Segoe UI", 22, "bold"), bg="#1e3a8a", fg="white")
        title.pack(side="left", padx=20, pady=20)

        # === Frame tombol kanan atas ===
        top_button_frame = tk.Frame(header, bg="#1e3a8a")
        top_button_frame.pack(side="right", padx=20, pady=20)

        self.create_top_button(top_button_frame, "⚙ Profil", "#ffffff", "#1e3a8a", lambda: self.controller.switch_frame(ProfileFrame))
        self.create_top_button(top_button_frame, "🔒 Logout", "#ffffff", "#dc3545", self.logout)

        # === Welcome Text ===
        user = getattr(self.controller, "current_user", {'username': 'User'})
        welcome = tk.Label(self, text=f"Halo, {user['username']} 👋",
                           font=("Segoe UI", 20, "bold"), bg="#f4f6f9", fg="#2c3e50")
        welcome.pack(pady=(40, 10))

        subtitle = tk.Label(self, text="Silakan pilih aksi yang ingin dilakukan:",
                            font=("Segoe UI", 14), bg="#f4f6f9", fg="#6b7280")
        subtitle.pack()

        # === Tombol Navigasi Tengah ===
        button_frame = tk.Frame(self, bg="#f4f6f9")
        button_frame.pack(pady=40)

        self.create_nav_button(button_frame, "➕ Buat SPK", "#2563eb", lambda: self.controller.switch_frame(SPKInputFrame))
        self.create_nav_button(button_frame, "📄 Lihat Jadwal", "#16a34a", lambda: self.controller.switch_frame(LihatJadwalFrame))
        self.create_nav_button(button_frame, "🖥 Tampilkan ke TV", "#9333ea", self.tampilkan_tv)

        # === Footer ===
        footer = tk.Label(self, text="© 2025 CV Multi Karya Indonesia", font=("Segoe UI", 10),
                          bg="#f4f6f9", fg="#9ca3af")
        footer.pack(side="bottom", pady=20)

    def create_nav_button(self, parent, text, color, command):
        button = tk.Button(
            parent,
            text=text,
            width=25,
            height=2,
            command=command,
            bg=color,
            fg="white",
            font=("Segoe UI", 14, "bold"),
            relief="flat",
            activebackground=color,
            activeforeground="white",
            cursor="hand2",
            bd=0,
            highlightthickness=0
        )
        button.pack(pady=10)
        button.configure(highlightbackground=color)

    def create_top_button(self, parent, text, fg_color, bg_color, command):
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=fg_color,
            fg=bg_color,
            font=("Segoe UI", 10, "bold"),
            relief="groove",
            cursor="hand2",
            padx=10,
            pady=5,
            bd=1
        )
        button.pack(side="left", padx=5)

    def tampilkan_tv(self):
        tv = TVLihatJadwal(self.controller)
        tv.focus_set()

    def logout(self):
        from ui_login import LoginFrame
        self.controller.switch_frame(LoginFrame)
