import tkinter as tk
from ui_input_spk import SPKInputFrame
from lihat_jadwal_frame import LihatJadwalFrame
from ui_profile import ProfileFrame

class DashboardFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f4f6f9")
        self.controller = controller
        
        # === Layout Utama ===
        self.sidebar = tk.Frame(self, bg="#2c3e50", width=200)
        self.sidebar.pack(side="left", fill="y")
        
        main_content = tk.Frame(self, bg="#f0f2f5")
        main_content.pack(side="right", fill="both", expand=True)
        
        # === Build Komponen ===
        self.build_sidebar()
        self.build_main_content(main_content)

        self.build_main_content()

    def build_main_content(self):
        # === Header ===
        header = tk.Frame(self, bg="#0078D7", height=80)
        header.pack(side="top", fill="x")

        title = tk.Label(header, text="📋 Dashboard Workflow Percetakan",
                         font=("Segoe UI", 22, "bold"), bg="#0078D7", fg="white")
        title.pack(side="left", padx=20, pady=20)

        # === Frame tombol kanan atas ===
        top_button_frame = tk.Frame(header, bg="#0078D7")
        top_button_frame.pack(side="right", padx=20, pady=20)

        # Tombol Profil
        profile_btn = tk.Button(top_button_frame, text="⚙️ Profil",
                                command=lambda: self.controller.switch_frame(ProfileFrame),
                                bg="white", fg="#0078D7", font=("Segoe UI", 10, "bold"),
                                relief="flat", cursor="hand2", padx=10, pady=5)
        profile_btn.pack(side="left", padx=5)

        # Tombol Logout
        logout_btn = tk.Button(top_button_frame, text="🔒 Logout",
                               command=self.logout,
                               bg="white", fg="#e74c3c", font=("Segoe UI", 10, "bold"),
                               relief="flat", cursor="hand2", padx=10, pady=5)
        logout_btn.pack(side="left", padx=5)

        # === Welcome Text ===
        user = getattr(self.controller, "current_user", {'username': 'User'})
        welcome = tk.Label(self, text=f"Halo, {user['username']} 👋",
                           font=("Segoe UI", 20, "bold"), bg="#f4f6f9", fg="#2c3e50")
        welcome.pack(pady=(40, 10))

        subtitle = tk.Label(self, text="Silakan pilih aksi yang ingin dilakukan:",
                            font=("Segoe UI", 14), bg="#f4f6f9", fg="#555")
        subtitle.pack()

        # === Tombol Navigasi Tengah ===
        button_frame = tk.Frame(self, bg="#f4f6f9")
        button_frame.pack(pady=40)

        self.create_nav_button(button_frame, "➕ Buat SPK", "#3498db", lambda: self.controller.switch_frame(SPKInputFrame))
        self.create_nav_button(button_frame, "📄 Lihat Jadwal", "#2ecc71", lambda: self.controller.switch_frame(LihatJadwalFrame))

        # === Footer ===
        footer = tk.Label(self, text="© 2025 PT Percetakan", font=("Segoe UI", 10),
                          bg="#f4f6f9", fg="#aaa")
        footer.pack(side="bottom", pady=20)

    def create_nav_button(self, parent, text, color, command):
        tk.Button(
            parent, text=text, width=25, height=2, command=command,
            bg=color, fg="white", font=("Segoe UI", 14, "bold"),
            relief="flat", padx=10, pady=10, cursor="hand2"
        ).pack(pady=10)

    def logout(self):
        from ui_login import LoginFrame
        self.controller.switch_frame(LoginFrame)
