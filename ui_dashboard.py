import tkinter as tk
from tkinter import ttk
from ui_input_spk import SPKInputFrame
from lihat_jadwal_frame import LihatJadwalFrame
from ui_profile import ProfileFrame
from tv_dashboard import TVLihatJadwal


class DashboardFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f2f5")
        self.controller = controller
        
        # === Layout Utama ===
        self.sidebar = tk.Frame(self, bg="#2c3e50", width=200)
        self.sidebar.pack(side="left", fill="y")
        
        main_content = tk.Frame(self, bg="#f0f2f5")
        main_content.pack(side="right", fill="both", expand=True)
        
        # === Build Komponen ===
        self.build_sidebar()
        self.build_main_content(main_content)

    def build_sidebar(self):
        btn_style = {
            'bg': "#34495e",
            'fg': "white",
            'font': ("Segoe UI", 12),
            'relief': "flat",
            'activebackground': "#2980b9",
            'padx': 15,
            'pady': 10,
            'anchor': "w",
            'cursor': "hand2"
        }
        
        # Tombol Profil
        tk.Button(
            self.sidebar,
            text="⚙️ Pengaturan Profil",
            command=lambda: self.controller.switch_frame(ProfileFrame),
            **btn_style
        ).pack(pady=5, fill='x')

    def build_main_content(self, parent):
        # === Header ===
        header = tk.Frame(parent, bg="#0078D7", height=60)
        header.pack(side="top", fill="x")

        title = tk.Label(header, text="📋 Dashboard Workflow Percetakan", 
                    font=("Segoe UI", 18, "bold"), bg="#0078D7", fg="white")
        title.pack(side="left", padx=20, pady=10)

        logout_btn = tk.Button(header, text="Logout", command=self.logout, 
                            bg="white", fg="#0078D7", font=("Segoe UI", 10, "bold"),
                            relief="flat", cursor="hand2", padx=10, pady=5)
        logout_btn.pack(side="right", padx=20, pady=10)

        # === Konten Utama ===
        user = getattr(self.controller, "current_user", {'id': None, 'username': 'User', 'name': 'User'})
        welcome = tk.Label(parent, text=f"Halo, {user['username']} 👋", 
                        font=("Segoe UI", 16), bg="#f0f2f5", fg="#333")
        welcome.pack(pady=(30, 10))

        subtitle = tk.Label(parent, text="Buat pekerjaanmu lebih mudah", 
                        font=("Segoe UI", 12), bg="#f0f2f5", fg="#666")
        subtitle.pack()

        # === Tombol Aksi ===
        button_frame = tk.Frame(parent, bg="#f0f2f5")
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

        tk.Button(
            button_frame,
            text="🖥 Tampilkan ke TV",
            width=20,
            height=2,
            command=self.tampilkan_tv,
            bg="#8e44ad",
            fg="white",
            font=("Helvetica", 14),
            relief="flat",
            padx=10,
            pady=10
        ).pack(pady=10)

        # Footer
        tk.Label(parent, text="© PT Percetakan.", 
                font=("Segoe UI", 11), bg="#f0f2f5", fg="#999").pack(pady=(50, 10))

    def tampilkan_tv(self):
        tv = TVLihatJadwal(self.controller)
        tv.focus_set()

    def logout(self):
        from ui_login import LoginFrame
        self.controller.switch_frame(LoginFrame)
