import tkinter as tk
from PIL import Image, ImageTk
import sqlite3
import qrcode
import os
from tkinter import messagebox
from ui_dashboard import DashboardFrame
from scrollable_frame import ScrollableFrame  # Pastikan path import sesuai
from reportlab.pdfgen import canvas

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
        # Header (di luar scroll)
        header = tk.Label(self, text="📝 SURAT PERINTAH KERJA", font=("Helvetica", 24, "bold"),
                          bg="#f7f9fb", fg="#2c3e50")
        header.pack(pady=25)

        # Scrollable content
        scroll = ScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=40, pady=(0, 20))
        content_frame = scroll.scrollable_frame

        # Section Title
        section_title = tk.Label(content_frame, text="📄 Detail Informasi SPK",
                                 font=("Helvetica", 14, "bold"), bg="white", fg="#34495e")
        section_title.pack(pady=(15, 0), anchor="w", padx=20)

        info_items = [
            ("ORDER SALES", "order_sales"), ("NO PO", "no_po"), ("COSTUMER", "costumer"),
            ("NAMA ARTIKEL", "nama_artikel"), ("QTY", "qty"), ("TANGGAL KIRIM", "tanggal_kirim"),
            ("JENIS BAHAN", "jenis_bahan"), ("QTY BAHAN", "qty_bahan"),
            ("UKURAN CETAK", "ukuran_cetak"), ("JUMLAH CETAK", "jumlah_cetak"),
            ("INSHEET", "insheet"), ("TOTAL CETAK", "total_cetak"),
            ("WARNA", "warna"), ("VARNISH", "varnish"), ("FINISHING", "finishing"),
        ]

        info_frame = tk.Frame(content_frame, bg="white", bd=3, relief="solid")
        info_frame.pack(padx=10, pady=10, fill="x")

        for i, (label_text, key) in enumerate(info_items):
            tk.Label(info_frame, text=f"{label_text} :", font=("Helvetica", 11, "bold"),
                     bg="white", anchor="w", width=18).grid(row=i, column=0, sticky="w", pady=3, padx=10)
            tk.Label(info_frame, text=self.data.get(key, "-"), font=("Helvetica", 11),
                     bg="white", anchor="w").grid(row=i, column=1, sticky="w", pady=3)

        # Image & Barcode Section
        section_images = tk.Label(content_frame, text="🖼️ Gambar & Barcode",
                                  font=("Helvetica", 14, "bold"), bg="white", fg="#34495e")
        section_images.pack(pady=(20, 5), anchor="w", padx=20)

        img_frame = tk.Frame(content_frame, bg="white")
        img_frame.pack(pady=10)

        self.show_image(img_frame, self.data.get('gambar_desain'), "Desain")
        self.generate_and_show_barcode(img_frame)
        self.show_image(img_frame, self.data.get('gambar_dummy'), "Dummy")

        # Back Button (masih di dalam scroll agar tetap ikut scroll ke bawah)
        btn_frame = tk.Frame(content_frame, bg="white")
        btn_frame.pack(pady=30)
        back_button = tk.Button(btn_frame, text="⬅️ Kembali ke Dashboard", font=("Helvetica", 12, "bold"),
                                bg="#27ae60", fg="white", padx=20, pady=8,
                                command=lambda: self.controller.switch_frame(DashboardFrame))
        back_button.pack()

    def show_image(self, parent, path, label):
        frame = tk.Frame(parent, bg="white")
        frame.pack(side="left", padx=30)

        if path and os.path.exists(path):
            img = Image.open(path)
            img.thumbnail((160, 160))
            photo = ImageTk.PhotoImage(img)
            label_image = tk.Label(frame, image=photo, bg="white")
            label_image.pack()
            frame.image = photo  # Keep a reference
        else:
            label_image = tk.Label(frame, text="[Gambar Tidak Ada]", bg="white", fg="gray", font=("Helvetica", 10, "italic"))
            label_image.pack()

        label_name = tk.Label(frame, text=label, bg="white", font=("Helvetica", 11, "bold"))
        label_name.pack(pady=5)

    def generate_and_show_barcode(self, parent):
        barcode_path = f"barcode_spk_{self.spk_id}.png"
        qr = qrcode.make(str(self.spk_id))
        qr.save(barcode_path)
        self.show_image(parent, barcode_path, "Barcode")
        self.barcode_path = barcode_path

    def destroy(self):
        if hasattr(self, 'barcode_path') and os.path.exists(self.barcode_path):
            os.remove(self.barcode_path)
        super().destroy()
