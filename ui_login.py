# ui_login.py
from doctest import master
import tkinter as tk
from tkinter import messagebox
from db import check_login
from ui_dashboard import DashboardFrame
from ui_register import RegisterFrame


class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        tk.Label(self, text="Login", font=("Arial", 18)).pack(pady=10)

        self.username_entry = self.create_labeled_entry("Username")
        self.password_entry = self.create_labeled_entry("Password", show="*")

        tk.Button(self, text="Login", command=self.login).pack(pady=10)
        tk.Button(self, text="Belum punya akun? Register", command=lambda: self.controller.switch_frame(__import__("ui_register").RegisterFrame)).pack(pady=5)


    def create_labeled_entry(self, label, show=None):
        tk.Label(self, text=label).pack()
        entry = tk.Entry(self, show=show)
        entry.pack()
        return entry

    def login(self):
        print("Tombol login ditekan")  # debug
        username = self.username_entry.get()
        password = self.password_entry.get()
        user = check_login(username, password)
        if user:
            self.controller.current_user = user
            self.controller.switch_frame(DashboardFrame)
        else:
            messagebox.showerror("Login Gagal", "Username atau password salah.")
