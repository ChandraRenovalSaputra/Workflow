import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import sqlite3
import qrcode
import os
from reportlab.pdfgen import canvas
import matplotlib
matplotlib.use('Agg')
from ui_dashboard import DashboardFrame
from scrollable_frame import ScrollableFrame

class SPKPreviewFrame(tk.Frame):
    def __init__(self, parent, controller, spk_id):
        super().__init__(parent, bg="#f7f9fb")
        self.controller = controller
        self.spk_id = spk_id
        self.data = self.get_spk_data(spk_id)
        self.build_ui()

    def get_spk_data(self, spk_id):
        conn = sqlite3.connect("workflow.db")
        c = conn.cursor()
        c.execute("SELECT * FROM spk WHERE id = ?", (spk_id,))
        row = c.fetchone()
        col = [d[0] for d in c.description]
        conn.close()
        return dict(zip(col, row)) if row else {}

    def build_ui(self):
        # Header
        header = tk.Label(self, text="📝 SURAT PERINTAH KERJA",
                        font=("Segoe UI", 24, "bold"),
                        bg="#f7f9fb", fg="#2c3e50")
        header.pack(pady=25)

        # Scrollable content
        scroll = ScrollableFrame(self)
        scroll.pack(fill="both", expand=True)
        content_frame = scroll.scrollable_frame
        content_frame.configure(bg="#f7f9fb")

        # Gunakan grid agar container bisa dipusatkan
        content_frame.grid_columnconfigure(0, weight=1)

        container = tk.Frame(content_frame, bg="white")
        container.grid(row=0, column=0, padx=60, pady=30, ipadx=20, ipady=20, sticky="n")


        # Section Title
        section_title = tk.Label(container, text="📄 Detail Informasi SPK",
                                font=("Segoe UI", 16, "bold"),
                                bg="white", fg="#34495e")
        section_title.pack(pady=(10, 15))

        # Informasi SPK
        info_frame = tk.Frame(container, bg="#ffffff")
        info_frame.pack(padx=20, pady=10, fill="x")

        for i, (label_text, key) in enumerate([
            ("ORDER SALES", "order_sales"), ("NO PO", "no_po"), ("COSTUMER", "costumer"),
            ("NAMA ARTIKEL", "nama_artikel"), ("QTY", "qty"), ("TANGGAL KIRIM", "tanggal_kirim"),
            ("JENIS BAHAN", "jenis_bahan"), ("QTY BAHAN", "qty_bahan"),
            ("UKURAN CETAK", "ukuran_cetak"), ("JUMLAH CETAK", "jumlah_cetak"),
            ("INSHEET", "insheet"), ("TOTAL CETAK", "total_cetak"),
            ("WARNA", "warna"), ("VARNISH", "varnish"), ("FINISHING", "finishing"),
        ]):
            tk.Label(info_frame, text=f"{label_text}        :", font=("Segoe UI", 11, "bold"),
                    bg="white", anchor="w", width=20).grid(row=i, column=0, sticky="w", pady=4, padx=10)
            tk.Label(info_frame, text=self.data.get(key, "-"), font=("Segoe UI", 11),
                    bg="white", anchor="w").grid(row=i, column=1, sticky="w", pady=4)

        # Gambar & Barcode
        section_images = tk.Label(container, text="🖼️ Gambar & Barcode",
                                font=("Segoe UI", 16, "bold"), 
                                bg="white", fg="#34495e")
        section_images.pack(pady=(30, 10))

        # Frame utama untuk gambar
        img_main_frame = tk.Frame(container, bg="white")
        img_main_frame.pack(pady=10)

        # Baris 1: Desain, Dummy, Potong
        row1_frame = tk.Frame(img_main_frame, bg="white")
        row1_frame.grid(row=0, column=0, sticky="nsew")

        # Baris 2: Barcode (di tengah)
        row2_frame = tk.Frame(img_main_frame, bg="white")
        row2_frame.grid(row=1, column=0, sticky="nsew")

        # Atur grid column configure
        img_main_frame.grid_columnconfigure(0, weight=1)
        row1_frame.grid_columnconfigure(0, weight=1)
        row1_frame.grid_columnconfigure(1, weight=1)
        row1_frame.grid_columnconfigure(2, weight=1)
        row2_frame.grid_columnconfigure(0, weight=1)
        row2_frame.grid_columnconfigure(1, weight=1)
        row2_frame.grid_columnconfigure(2, weight=1)

        # Baris 1: Desain, Dummy, Potong
        self.show_image(row1_frame, self.data.get('gambar_desain'), "Desain", row=0, col=0)
        self.show_image(row1_frame, self.data.get('gambar_dummy'), "Dummy", row=0, col=1)
        self.show_image(row1_frame, self.data.get('gambar_potong'), "Potong Bahan", row=0, col=2)

        # Baris 2: Barcode di tengah
        empty_frame1 = tk.Frame(row2_frame, width=180, height=180, bg="white")
        empty_frame1.grid(row=0, column=0, sticky="nsew")
        
        self.generate_and_show_barcode(row2_frame, row=0, col=1)
        
        empty_frame2 = tk.Frame(row2_frame, width=180, height=180, bg="white")
        empty_frame2.grid(row=0, column=2, sticky="nsew")


        # Tombol kembali
        btn_frame = tk.Frame(container, bg="white")
        btn_frame.pack(pady=40)

        back_button = tk.Button(btn_frame, text="⬅️ Kembali ke Dashboard",
                                font=("Segoe UI", 12, "bold"),
                                bg="#27ae60", fg="white", padx=30, pady=10,
                                relief="flat", cursor="hand2",
                                command=lambda: self.controller.switch_frame(DashboardFrame))
        back_button.pack()

    def show_image(self, parent, path, label, row=0, col=0):
        frame = tk.Frame(parent, bg="white", bd=2, relief="groove")
        frame.grid(row=row, column=col, padx=20, pady=10, sticky="nsew")
        
        try:
            if path and os.path.exists(path):
                img = Image.open(path)
                img.thumbnail((180, 180))
                photo = ImageTk.PhotoImage(img)
                
                label_img = tk.Label(frame, image=photo, bg="white")
                label_img.image = photo  # Keep reference
                label_img.pack(pady=5)
            else:
                label_img = tk.Label(frame, text="[Gambar Tidak Ada]", 
                                bg="white", fg="gray",
                                font=("Segoe UI", 10, "italic"))
                label_img.pack(pady=20)
                
            label_name = tk.Label(frame, text=label, 
                                bg="white", 
                                font=("Segoe UI", 11, "bold"))
            label_name.pack(pady=5)
            
        except Exception as e:
            print(f"Error loading image {label}: {e}")
            error_label = tk.Label(frame, text=f"[Error: {label}]", 
                                bg="white", fg="red")
            error_label.pack(pady=20)
        
        return frame

    def generate_and_show_barcode(self, parent, row=0, col=0):
        try:
            barcode_path = f"barcode_spk_{self.spk_id}.png"
            qr = qrcode.make(f"SPK-{self.spk_id}")
            qr.save(barcode_path)
            
            # Tampilkan barcode menggunakan show_image yang sudah diperbaiki
            self.show_image(parent, barcode_path, "Barcode", row, col)
            self.barcode_path = barcode_path
        except Exception as e:
            print(f"Error generating barcode: {e}")
            error_frame = tk.Frame(parent, bg="white")
            error_frame.grid(row=row, column=col)
            tk.Label(error_frame, text="[Barcode Error]", fg="red").pack()

    def destroy(self):
        if hasattr(self, 'barcode_path') and os.path.exists(self.barcode_path):
            os.remove(self.barcode_path)
        super().destroy()
