import tkinter as tk
# from tkinter import ttk
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
        super().__init__(parent)
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
        tk.Label(self, text="SURAT PERINTAH KERJA", font=("Helvetica", 18, "bold")).pack(pady=10)

        info_text = f"""
        ORDER SALES : {self.data.get('order_sales', '')}
        NO PO       : {self.data.get('no_po', '')}
        COSTUMER    : {self.data.get('costumer', '')}
        NAMA ARTIKEL: {self.data.get('nama_artikel', '')}
        QTY         : {self.data.get('qty', '')}
        TANGGAL KIRIM: {self.data.get('tanggal_kirim', '')}

        JENIS BAHAN : {self.data.get('jenis_bahan', '')}
        QTY BAHAN   : {self.data.get('qty_bahan', '')}
        UKURAN CETAK: {self.data.get('ukuran_cetak', '')}
        JUMLAH CETAK: {self.data.get('jumlah_cetak', '')}
        INSHEET     : {self.data.get('insheet', '')}
        TOTAL CETAK : {self.data.get('total_cetak', '')}
        WARNA       : {self.data.get('warna', '')}
        VARNISH     : {self.data.get('varnish', '')}
        FINISHING   : {self.data.get('finishing', '')}
        """.strip()

        tk.Label(self, text=info_text, justify="left", anchor="w").pack(padx=20, pady=10)

        # Gambar dan barcode
        img_frame = tk.Frame(self)
        img_frame.pack(pady=10)

        self.show_image(img_frame, self.data.get('gambar_desain'), "Desain")
        self.generate_and_show_barcode(img_frame)
        self.show_image(img_frame, self.data.get('gambar_dummy'), "Dummy")

        # Tombol hanya kembali ke dashboard
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=15)
        tk.Button(btn_frame, text="Kembali ke Dashboard", 
                 command=lambda: self.controller.switch_frame(DashboardFrame)).pack()

    def show_image(self, parent, path, label):
        if path and os.path.exists(path):
            img = Image.open(path)
            img.thumbnail((100, 100))
            photo = ImageTk.PhotoImage(img)
            frame = tk.Frame(parent)
            frame.pack(side="left", padx=20)
            tk.Label(frame, image=photo).pack()
            tk.Label(frame, text=label).pack()
            frame.image = photo
        else:
            frame = tk.Frame(parent)
            frame.pack(side="left", padx=20)
            tk.Label(frame, text="[No Image]").pack()
            tk.Label(frame, text=label).pack()

    def generate_and_show_barcode(self, parent):
        barcode_path = f"barcode_spk_{self.spk_id}.png"
        qr = qrcode.make(str(self.spk_id))
        qr.save(barcode_path)
        self.show_image(parent, barcode_path, "Barcode")
        self.barcode_path = barcode_path