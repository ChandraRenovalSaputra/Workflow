import tkinter as tk
from tkinter import messagebox
from db import register_user
from scrollable_frame import ScrollableFrame

class RegisterFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller  # Simpan referensi controller (App)

        scroll = ScrollableFrame(self)
        scroll.pack(fill="both", expand=True)

        container = scroll.scrollable_frame
        
        # Frame isi yang diletakkan di tengah atas
        content_frame = tk.Frame(container)
        content_frame.pack(pady=100)  # Jarak dari atas

        tk.Label(content_frame, text="Register", font=("Arial", 18)).pack(pady=10)

        self.username_entry = self.create_labeled_entry(content_frame, "Username")
        self.password_entry = self.create_labeled_entry(content_frame, "Password", show="*")

        tk.Button(content_frame, text="Daftar", command=self.register).pack(pady=10)
        tk.Button(content_frame, text="Sudah punya akun? Login", command=self.goto_login).pack()

    def create_labeled_entry(self, parent, label, show=None):
        tk.Label(parent, text=label).pack()
        entry = tk.Entry(parent, show=show)
        entry.pack()
        return entry

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if register_user(username, password):
            messagebox.showinfo("Sukses", "Pendaftaran berhasil. Silakan login.")
            self.master.switch_frame(__import__("ui_login").LoginFrame)
        else:
            messagebox.showerror("Gagal", "Username sudah digunakan.")

    def goto_login(self):
        self.controller.switch_frame(__import__("ui_login").LoginFrame)
