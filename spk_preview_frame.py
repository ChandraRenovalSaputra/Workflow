import tkinter as tk
from PIL import Image, ImageTk
import sqlite3
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
from tkinter import messagebox
from ui_dashboard import DashboardFrame

class SPKPreviewFrame(tk.Frame):
    def __init__(self, parent, controller, spk_id):
        super().__init__(parent, bg="#f0f0f0")  # Soft background
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
        tk.Label(self, text="SURAT PERINTAH KERJA", font=("Helvetica", 20, "bold"), bg="#f0f0f0", fg="#333").pack(pady=15)

        content_frame = tk.Frame(self, bg="white", bd=2, relief="groove")
        content_frame.pack(padx=30, pady=10, fill="both", expand=True)

        # Informasi SPK dalam grid
        info_items = [
            ("ORDER SALES", "order_sales"), ("NO PO", "no_po"), ("COSTUMER", "costumer"),
            ("NAMA ARTIKEL", "nama_artikel"), ("QTY", "qty"), ("TANGGAL KIRIM", "tanggal_kirim"),
            ("JENIS BAHAN", "jenis_bahan"), ("QTY BAHAN", "qty_bahan"),
            ("UKURAN CETAK", "ukuran_cetak"), ("JUMLAH CETAK", "jumlah_cetak"),
            ("INSHEET", "insheet"), ("TOTAL CETAK", "total_cetak"),
            ("WARNA", "warna"), ("VARNISH", "varnish"), ("FINISHING", "finishing"),
        ]

        info_frame = tk.Frame(content_frame, bg="white")
        info_frame.pack(padx=20, pady=15, anchor="w")

        for i, (label_text, key) in enumerate(info_items):
            tk.Label(info_frame, text=f"{label_text} :", font=("Helvetica", 10, "bold"), bg="white", anchor="w", width=15).grid(row=i, column=0, sticky="w", pady=2)
            tk.Label(info_frame, text=self.data.get(key, ""), font=("Helvetica", 10), bg="white", anchor="w").grid(row=i, column=1, sticky="w", pady=2)

        # Gambar dan barcode
        img_frame = tk.Frame(content_frame, bg="white")
        img_frame.pack(pady=10)

        self.show_image(img_frame, self.data.get('gambar_desain'), "Desain")
        self.generate_and_show_barcode(img_frame)
        self.show_image(img_frame, self.data.get('gambar_dummy'), "Dummy")

        # Tombol kembali
        btn_frame = tk.Frame(self, bg="#f0f0f0")
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="Kembali ke Dashboard", font=("Helvetica", 10, "bold"),
                  bg="#4CAF50", fg="white", padx=15, pady=5,
                  command=lambda: self.controller.switch_frame(DashboardFrame)).pack()

    def show_image(self, parent, path, label):
        frame = tk.Frame(parent, bg="white")
        frame.pack(side="left", padx=20)

        if path and os.path.exists(path):
            img = Image.open(path)
            img.thumbnail((120, 120))
            photo = ImageTk.PhotoImage(img)
            tk.Label(frame, image=photo, bg="white").pack()
            frame.image = photo  # Keep reference
        else:
            tk.Label(frame, text="[No Image]", bg="white", fg="gray", font=("Helvetica", 10, "italic")).pack()

        tk.Label(frame, text=label, bg="white", font=("Helvetica", 10, "bold")).pack(pady=5)

    def generate_and_show_barcode(self, parent):
        barcode_path = f"barcode_spk_{self.spk_id}.png"
        qr = qrcode.make(str(self.spk_id))
        qr.save(barcode_path)
        self.show_image(parent, barcode_path, "Barcode")
        self.barcode_path = barcode_path
