import tkinter as tk
from tkinter import messagebox
from db import register_user


class RegisterFrame(tk.Frame):
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
            text="Buat Akun Baru",
            font=("Segoe UI", 30, "bold"),
            bg="white",
            fg="#333"
        ).grid(row=0, column=0, columnspan=2, pady=(0, 10))

        tk.Label(
            container,
            text="Silakan isi data untuk mendaftar",
            font=("Segoe UI", 14),
            bg="white",
            fg="#666"
        ).grid(row=1, column=0, columnspan=2, pady=(0, 30))

        # Input fields
        self.username_entry = self.create_labeled_entry(container, "Username", 2)
        self.password_entry = self.create_labeled_entry(container, "Password", 4, show="*")

        # Tombol daftar
        register_btn = tk.Button(
            container,
            text="Daftar",
            command=self.register,
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
        register_btn.grid(row=6, column=0, columnspan=2, pady=(30, 15))

        # Tombol kembali ke login
        login_btn = tk.Button(
            container,
            text="Sudah punya akun? Login di sini",
            command=self.goto_login,
            bg="white",
            fg="#0078D7",
            relief="flat",
            font=("Segoe UI", 12, "underline"),
            cursor="hand2",
            activeforeground="#005a9e"
        )
        login_btn.grid(row=7, column=0, columnspan=2)

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

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if register_user(username, password):
            messagebox.showinfo("Sukses", "Pendaftaran berhasil. Silakan login.")
            self.controller.switch_frame(self.load_login_frame())
        else:
            messagebox.showerror("Gagal", "Username sudah digunakan.")

    def goto_login(self):
        self.controller.switch_frame(self.load_login_frame())

    def load_login_frame(self):
        from ui_login import LoginFrame
        return LoginFrame
