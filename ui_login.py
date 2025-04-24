# ui_login.py
from doctest import master
import tkinter as tk
from tkinter import messagebox
from db import check_login
from ui_dashboard import DashboardFrame
from ui_register import RegisterFrame


class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f2f5")
        self.controller = controller

        # Container besar
        container = tk.Frame(
            self,
            bg="white",
            bd=0,
            highlightthickness=2,
            highlightbackground="#ccc",
            padx=60,
            pady=50
        )
        container.place(relx=0.5, rely=0.5, anchor="center")

        # Judul
        tk.Label(
            container,
            text="Selamat Datang",
            font=("Segoe UI", 30, "bold"),
            bg="white",
            fg="#333"
        ).grid(row=0, column=0, columnspan=2, pady=(0, 10))

        tk.Label(
            container,
            text="Silakan login untuk melanjutkan",
            font=("Segoe UI", 14),
            bg="white",
            fg="#666"
        ).grid(row=1, column=0, columnspan=2, pady=(0, 30))

        # Input field
        self.username_entry = self.create_labeled_entry(container, "Username", 2)
        self.password_entry = self.create_labeled_entry(container, "Password", 4, show="*")

        # Tombol Login
        login_btn = tk.Button(
            container,
            text="Masuk",
            command=self.login,
            bg="#0078D7",
            fg="white",
            font=("Segoe UI", 14, "bold"),
            relief="flat",
            padx=12,
            pady=10,
            width=30,
            cursor="hand2",
            activebackground="#005a9e"
        )
        login_btn.grid(row=6, column=0, columnspan=2, pady=(30, 15))

        # Tombol Register
        register_btn = tk.Button(
            container,
            text="Belum punya akun? Daftar di sini",
            command=lambda: self.controller.switch_frame(RegisterFrame),
            bg="white",
            fg="#0078D7",
            relief="flat",
            font=("Segoe UI", 12, "underline"),
            cursor="hand2",
            activeforeground="#005a9e"
        )
        register_btn.grid(row=7, column=0, columnspan=2)

        self.bind_all("<Return>", lambda event: self.login())


    def create_labeled_entry(self, parent, label, row, show=None):
        tk.Label(
            parent,
            text=label,
            font=("Segoe UI", 13),
            bg="white",
            anchor="w"
        ).grid(row=row, column=0, sticky="w", columnspan=2, pady=(0, 8))

        entry = tk.Entry(
            parent,
            show=show,
            font=("Segoe UI", 13),
            width=35,
            relief="solid",
            bd=1
        )
        entry.grid(row=row + 1, column=0, columnspan=2, pady=(0, 20))
        return entry
    
    def custom_messagebox(parent, title, message, type="error"):
        top = tk.Toplevel(parent)
        top.title(title)
        top.transient(parent)
        top.grab_set()
        top.configure(bg="white")

        # Ukuran dan posisi (diperbesar)
        w, h = 600, 400
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (w // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (h // 2)
        top.geometry(f"{w}x{h}+{x}+{y}")
        top.resizable(False, False)

        # Warna dan ikon
        if type == "error":
            icon_text = "❌"
            icon_color = "#e74c3c"
        else:
            icon_text = "ℹ️"
            icon_color = "#3498db"

        # Container Frame dengan padding
        container = tk.Frame(top, bg="white", padx=20, pady=20)
        container.pack(expand=True, fill="both")

        # Icon
        icon_label = tk.Label(container, text=icon_text, font=("Segoe UI", 60), bg="white", fg=icon_color)
        icon_label.pack(pady=(10, 10))

        # Message
        msg_label = tk.Label(container, text=message, font=("Segoe UI", 16), bg="white", fg="#2c3e50", wraplength=w-80, justify="center")
        msg_label.pack(pady=(0, 20))

        # OK Button
        ok_button = tk.Button(container, text="OK", command=top.destroy,
                            bg="#0078D7", fg="white", font=("Segoe UI", 16, "bold"),
                            relief="flat", padx=40, pady=10, activebackground="#005a9e", cursor="hand2")
        ok_button.pack(pady=(0, 10))

        # Tambah efek hover
        def on_enter(e):
            ok_button['bg'] = "#005a9e"
        def on_leave(e):
            ok_button['bg'] = "#0078D7"
        
        ok_button.bind("<Enter>", on_enter)
        ok_button.bind("<Leave>", on_leave)

        top.wait_window()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        user = check_login(username, password)
        if user:
            self.controller.current_user = user
            self.unbind_all("<Return>")
            self.controller.switch_frame(DashboardFrame)
        else:
            self.custom_messagebox("Login Gagal", "Username atau password salah.")
