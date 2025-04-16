import tkinter as tk
# from tkinter import ttk
from PIL import Image, ImageTk
import sqlite3
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
from tkinter import messagebox
# from reportlab.lib.utils import ImageReader
import platform
import subprocess
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
        ORDER SALES : {self.data['order_sales']}
        NO PO       : {self.data['no_po']}
        COSTUMER    : {self.data['costumer']}
        NAMA ARTIKEL: {self.data['nama_artikel']}
        QTY         : {self.data['qty']}
        TANGGAL KIRIM: {self.data['tanggal_kirim']}

        JENIS BAHAN : {self.data['jenis_bahan']}
        QTY BAHAN   : {self.data['qty_bahan']}
        UKURAN CETAK: {self.data['ukuran_cetak']}
        JUMLAH CETAK: {self.data['jumlah_cetak']}
        INSHEET     : {self.data['insheet']}
        TOTAL CETAK : {self.data['total_cetak']}
        WARNA       : {self.data['warna']}
        VARNISH     : {self.data['varnish']}
        FINISHING   : {self.data['finishing']}
        """.strip()

        tk.Label(self, text=info_text, justify="left", anchor="w").pack(padx=20, pady=10)

        # Gambar dan barcode
        img_frame = tk.Frame(self)
        img_frame.pack(pady=10)

        self.show_image(img_frame, self.data['desain_path'], "Desain")
        self.generate_and_show_barcode(img_frame)
        self.show_image(img_frame, self.data['dummy_path'], "Dummy")

        # Tombol
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=15)

        tk.Button(btn_frame, text="Cetak SPK", command=self.export_to_pdf).pack(side="left", padx=10)
        # tk.Button(btn_frame, text="Dashboard", command=self.go_dashboard, width=15).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Kembali ke Dashboard", command=lambda: self.controller.switch_frame(DashboardFrame)).pack(side="left", padx=10)


    def show_image(self, parent, path, label):
        if path and os.path.exists(path):
            img = Image.open(path)
            img.thumbnail((100, 100))
            photo = ImageTk.PhotoImage(img)
            frame = tk.Frame(parent)
            frame.pack(side="left", padx=20)
            tk.Label(frame, image=photo).pack()
            tk.Label(frame, text=label).pack()
            frame.image = photo  # prevent garbage collection
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

    def export_to_pdf(self):
        os.makedirs("spk_output", exist_ok=True)
        filename = os.path.join("spk_output", f"SPK_{self.spk_id}.pdf")
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4

        y = height - 50
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, y, "SURAT PERINTAH KERJA")

        y -= 50
        c.setFont("Helvetica", 10)
        for line in self.data_text_lines():
            c.drawString(50, y, line)
            y -= 15

        # Gambar: desain, barcode, dummy
        y -= 30
        try:
            from reportlab.lib.utils import ImageReader
            if os.path.exists(self.data['desain_path']):
                c.drawImage(self.data['desain_path'], 50, y - 100, width=100, height=100)
            if os.path.exists(self.barcode_path):
                c.drawImage(self.barcode_path, 170, y - 100, width=100, height=100)
            if os.path.exists(self.data['dummy_path']):
                c.drawImage(self.data['dummy_path'], 290, y - 100, width=100, height=100)
        except Exception as e:
                print(f"Gagal menampilkan gambar di PDF: {e}")

        c.save()
        
        # Cetak otomatis (opsional)
        self.print_pdf(filename)
        
        tk.messagebox.showinfo("Sukses", f"File PDF berhasil dibuat: {filename}")
        

    def print_pdf(self, filepath):
        try:
            if platform.system() == "Windows":
                os.startfile(filepath, "print")
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["lp", filepath])
            else:  # Linux
                subprocess.run(["lp", filepath])
        except Exception as e:
            messagebox.showerror("Gagal Print", f"Terjadi kesalahan saat mencetak PDF:\n{e}")
            
    def data_text_lines(self):
        return [
            f"ORDER SALES : {self.data['order_sales']}",
            f"NO PO       : {self.data['no_po']}",
            f"COSTUMER    : {self.data['costumer']}",
            f"NAMA ARTIKEL: {self.data['nama_artikel']}",
            f"QTY         : {self.data['qty']}",
            f"TANGGAL KIRIM: {self.data['tanggal_kirim']}",
            "",
            f"JENIS BAHAN : {self.data['jenis_bahan']}",
            f"QTY BAHAN   : {self.data['qty_bahan']}",
            f"UKURAN CETAK: {self.data['ukuran_cetak']}",
            f"JUMLAH CETAK: {self.data['jumlah_cetak']}",
            f"INSHEET     : {self.data['insheet']}",
            f"TOTAL CETAK : {self.data['total_cetak']}",
            f"WARNA       : {self.data['warna']}",
            f"VARNISH     : {self.data['varnish']}",
            f"FINISHING   : {self.data['finishing']}",
        ]
# class App(tk.Tk):
#     def __init__(self):
#         super().__init__()
#         self.switch_frame(DashboardFrame)

#     def switch_frame(self, frame_class, *args):
#         new_frame = frame_class(self, self, *args)
#         if hasattr(self, 'current_frame'):
#             self.current_frame.destroy()
#         self.current_frame = new_frame
#         self.current_frame.pack(fill="both", expand=True)

#     def show_dashboard(self):
#         self.switch_frame(DashboardFrame)