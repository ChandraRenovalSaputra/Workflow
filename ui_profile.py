import tkinter as tk
from tkinter import messagebox

class ProfileFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f2f5")
        self.controller = controller
        self.current_user = controller.current_user
        
        # Container utama
        container = tk.Frame(self, bg="white", bd=0, highlightthickness=2, 
                           highlightbackground="#ccc", padx=60, pady=50)
        container.place(relx=0.5, rely=0.5, anchor="center")

        # Judul
        tk.Label(container, text="Pengaturan Profil", font=("Segoe UI", 30, "bold"), 
                bg="white", fg="#333").grid(row=0, column=0, columnspan=2, pady=(0, 30))

        # Username Field
        tk.Label(container, text="Username Baru", font=("Segoe UI", 13), 
                bg="white", anchor="w").grid(row=1, column=0, sticky="w", pady=(0, 5))
        
        self.username_entry = tk.Entry(container, font=("Segoe UI", 13), 
                                    width=35, relief="solid", bd=1)
        self.username_entry.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        self.username_entry.insert(0, self.current_user['username'])

        # Password Field
        tk.Label(container, text="Password Baru", font=("Segoe UI", 13), 
                bg="white", anchor="w").grid(row=3, column=0, sticky="w", pady=(0, 5))
        
        pass_frame = tk.Frame(container, bg="white")
        pass_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 30))
        
        self.password_entry = tk.Entry(pass_frame, show="*", font=("Segoe UI", 13), 
                                     width=32, relief="solid", bd=1)
        self.password_entry.pack(side="left", fill="x", expand=True)
        
        # Tombol mata (eye) untuk toggle password visibility
        self.eye_btn = tk.Button(pass_frame, text="👁️", relief="flat", 
                                bg="white", cursor="hand2", command=self.toggle_password,
                                padx=5)
        self.eye_btn.pack(side="right")

        # Frame untuk tombol aksi
        btn_frame = tk.Frame(container, bg="white")
        btn_frame.grid(row=5, column=0, columnspan=2, pady=(10, 0))
        
        # Tombol Update
        tk.Button(btn_frame, text="Update Profil", command=self.update_profile,
                 bg="#0078D7", fg="white", font=("Segoe UI", 12, "bold"),
                 relief="flat", padx=20, pady=8, cursor="hand2").pack(side="left", padx=5)
        
        # Tombol Kembali
        tk.Button(btn_frame, text="Kembali", 
                command=lambda: self.controller.switch_frame(self.controller.dashboard_frame_class),
                bg="#6c757d", fg="white", font=("Segoe UI", 12),
                relief="flat", padx=20, pady=8, cursor="hand2").pack(side="left", padx=5)

        # Configure column weights
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, minsize=40)  # Space for eye button

    def toggle_password(self):
        if self.password_entry['show'] == "*":
            self.password_entry.config(show="")
            self.eye_btn.config(text="🙈")
        else:
            self.password_entry.config(show="*")
            self.eye_btn.config(text="👁️")

    def update_profile(self):
        from db import is_username_exists, update_user
        
        new_username = self.username_entry.get().strip()
        new_password = self.password_entry.get().strip()
        
        # Validasi input
        if not new_username or not new_password:
            messagebox.showerror("Error", "Semua field harus diisi")
            return
            
        if not new_username.isalnum() or not new_password.isalnum():
            messagebox.showerror("Error", "Hanya boleh huruf dan angka")
            return
            
        if len(new_username) < 3 or len(new_password) < 3:
            messagebox.showerror("Error", "Minimal 3 karakter")
            return
        
        # Cek jika username berubah
        if new_username != self.current_user['username'] and is_username_exists(new_username):
            messagebox.showerror("Error", "Username sudah digunakan")
            return
            
        if update_user(self.current_user['username'], new_username, new_password):
            self.controller.current_user['username'] = new_username
            messagebox.showinfo("Sukses", "Profil berhasil diupdate!")
        else:
            messagebox.showerror("Error", "Gagal mengupdate profil")