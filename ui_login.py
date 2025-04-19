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

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        user = check_login(username, password)
        if user:
            self.controller.current_user = user
            self.controller.switch_frame(DashboardFrame)
        else:
            messagebox.showerror("Login Gagal", "Username atau password salah.")
