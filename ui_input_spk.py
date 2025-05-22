import sqlite3
import re
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import os
import shutil
import time
import io
import traceback
from PIL import Image, ImageTk
from tkcalendar import DateEntry
import qrcode
from scrollable_frame import ScrollableFrame
from db import get_workflow_conn
import platform
import subprocess
from tkinter import messagebox, filedialog
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.units import cm
from reportlab.lib import colors
import locale

# Set locale ke Indonesia
locale.setlocale(locale.LC_TIME, 'Indonesian')  # Untuk Windows


def format_angka_with_dot(value):
    raw = re.sub(r'[^\d]', '', value)
    if raw == '':
        return ''
    return f"{int(raw):,}".replace(",", ".")

def setup_ribuan_format(entry, var):
    def on_change(*args):
        current = var.get()
        new_value = format_angka_with_dot(current)
        if current != new_value:
            var.set(new_value)
    var.trace_add('write', on_change)
    
def format_dengan_titik(angka_str):
        try:
            angka = int(str(angka_str).replace('.', '').replace(',', '').strip())
            return f"{angka:,}".replace(",", ".")
        except:
            return angka_str  # fallback
        
def safe_int(value):
    try:
        return int(str(value).replace(".", "").strip())
    except:
        return 0

class SPKInputFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f2f5")
        self.controller = controller
        self.entries = {}
        self.desain_temp_path = None
        self.dummy_temp_path = None
        self.gambar_desain = None
        self.gambar_dummy = None
        self.potong_temp_path = None
        self.gambar_potong = None
        self.configure(bg="#f0f2f5")

        # ===== Scrollable Frame =====
        scroll = ScrollableFrame(self)
        scroll.pack(fill="both", expand=True)

        self.container = scroll.scrollable_frame
        self.container.configure(bg="#f0f2f5")

        # ===== Judul Halaman =====
        title = tk.Label(
            self.container,
            text="📋 Input SPK",
            font=("Segoe UI", 24, "bold"),
            bg="#f0f2f5",
            fg="#333",
            pady=20
        )
        title.pack(fill="x", anchor="center", padx=20) 

        form_fields = [
            ("ORDER SALES",),
            ("NO PO",),
            ("COSTUMER",),
            ("NAMA PRODUK",),
            ("QTY",),
            ("TANGGAL KIRIM", "date"),
            ("JENIS BAHAN",),
            ("QTY BAHAN",),
            ("UKURAN CETAK",),
            ("JUMLAH CETAK (DRUK)",),
            ("INSHEET",),
            ("TOTAL CETAK",),
            ("WARNA",),
            ("FINISHING",),
        ]

        # ===== Form Input =====
        form_frame = tk.Frame(self.container, bg="#f0f2f5")
        form_frame.pack(fill="x", padx=40, pady=20)

        for field in form_fields:
            self.add_form_row(field[0], field[1] if len(field) > 1 else None)

        # ===== Upload Gambar Section =====
        upload_frame = tk.Frame(self.container, bg="#f0f2f5")
        upload_frame.pack(fill="x", padx=40, pady=30)

        # Upload Desain
        tk.Label(upload_frame, text="Upload Gambar Desain:", bg="#f0f2f5", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(10, 2))
        self.desain_label = tk.Label(upload_frame, text="Belum ada file", fg="gray", bg="#f0f2f5", font=11)
        self.desain_label.pack(anchor="w")

        button_frame_desain = tk.Frame(upload_frame, bg="#f0f2f5")
        button_frame_desain.pack(fill="x", pady=10)

        tk.Button(button_frame_desain, text="Pilih File", command=self.upload_desain, bg="#007BFF", fg="white", font=("Segoe UI", 10, "bold"), relief="flat").pack(side="left", padx=10)  
        tk.Button(button_frame_desain, text="Hapus File", command=self.remove_desain, bg="#F44336", fg="white", font=("Segoe UI", 10, "bold"), relief="flat").pack(side="left", padx=10)  

        # Upload Dummy
        tk.Label(upload_frame, text="Upload Gambar Dummy:", bg="#f0f2f5", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(10, 2))
        self.dummy_label = tk.Label(upload_frame, text="Belum ada file", fg="gray", bg="#f0f2f5", font=11)
        self.dummy_label.pack(anchor="w")

        button_frame_dummy = tk.Frame(upload_frame, bg="#f0f2f5")
        button_frame_dummy.pack(fill="x", pady=10)

        tk.Button(button_frame_dummy, text="Pilih File", command=self.upload_dummy, bg="#007BFF", fg="white", font=("Segoe UI", 10, "bold"), relief="flat").pack(side="left", padx=10)  
        tk.Button(button_frame_dummy, text="Hapus File", command=self.remove_dummy, bg="#F44336", fg="white", font=("Segoe UI", 10, "bold"), relief="flat").pack(side="left", padx=10)  

        # Upload Gambar Potong Bahan
        tk.Label(upload_frame, text="Upload Gambar Potong Bahan:", bg="#f0f2f5", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(10, 2))
        self.potong_label = tk.Label(upload_frame, text="Belum ada file", fg="gray", bg="#f0f2f5", font=11)
        self.potong_label.pack(anchor="w")

        button_frame_potong = tk.Frame(upload_frame, bg="#f0f2f5")
        button_frame_potong.pack(fill="x", pady=10)

        tk.Button(button_frame_potong, text="Pilih File", command=self.upload_potong, bg="#007BFF", fg="white", font=("Segoe UI", 10, "bold"), relief="flat").pack(side="left", padx=10)  
        tk.Button(button_frame_potong, text="Hapus File", command=self.remove_potong, bg="#F44336", fg="white", font=("Segoe UI", 10, "bold"), relief="flat").pack(side="left", padx=10)

        # ===== Estimasi Tahapan =====
        self.build_estimasi_section()

        # ===== Tombol Navigasi =====
        button_frame = tk.Frame(self.container, bg="#f0f2f5")
        button_frame.pack(pady=30, anchor="center")  # Center the button frame

        style = {
            "width": 15,
            "font": ("Segoe UI", 10, "bold"),
            "padx": 10,
            "pady": 5,
            "relief": "flat"
        }

        # Gaya umum untuk tombol besar
        button_font = ("Arial", 14, "bold")
        button_padx = 20
        button_pady = 10

        def make_hover_button(parent, text, command, bg, hover_bg):
            btn = tk.Button(
                parent,
                text=text,
                command=command,
                bg=bg,
                fg="white",
                font=button_font,
                padx=button_padx,
                pady=button_pady,
                relief="flat",
                cursor="hand2"
            )
            btn.pack(side="left", padx=20)

            # Hover effect
            btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
            btn.bind("<Leave>", lambda e: btn.config(bg=bg))
            return btn

        # Membuat tombol navigasi di tengah
        make_hover_button(button_frame, "Dashboard", self.go_dashboard, "#2196F3", "#1976D2")
        make_hover_button(button_frame, "Hapus", self.clear_form, "#F44336", "#C62828")
        make_hover_button(button_frame, "Simpan", self.save_spk, "#4CAF50", "#2E7D32")

    # ====================================================DEF===================================================
    def add_form_row(self, label_text, input_type=None):
        frame = tk.Frame(self.container)
        frame.pack(fill="x", pady=3, padx=20)

        label = tk.Label(frame, text=label_text, width=25, anchor="w", font=("Segoe UI", 14, "bold"))
        label.pack(side="left")

        if input_type == "date":
            style = ttk.Style()
            style.theme_use("default")
            style.configure("my.DateEntry", 
                        fieldbackground="white",
                        background="#0078D7",
                        foreground="black",
                        arrowcolor="white",
                        bordercolor="#ccc",
                        lightcolor="#0078D7",
                        darkcolor="#005a9e",
                        relief="flat",
                        padding=5)

            today = datetime.today().date()
            entry = DateEntry(
                frame,
                date_pattern='dd-mm-yyyy',
                mindate=today,
                state="readonly",
                width=20,
                style="my.DateEntry",
                font=("Segoe UI", 14),
                locale='id_ID'
            )
        else:
            entry = tk.Entry(frame, font=("Segoe UI", 14))

        entry.pack(side="left", fill="x", expand=True)

        # ✅ Tambahkan auto-format jika field cocok
        if label_text in ["QTY", "QTY BAHAN", "JUMLAH CETAK (DRUK)", "INSHEET", "TOTAL CETAK"]:
            var = tk.StringVar()
            entry.config(textvariable=var)
            setup_ribuan_format(entry, var)
        else:
            var = tk.StringVar()
            entry.config(textvariable=var)

        self.entries[label_text] = entry


    def clear_form(self):
        confirm = messagebox.askokcancel("Konfirmasi", "Apakah kamu yakin ingin menghapus semua data form?")
        if confirm:
            for entry in self.entries.values():
                entry.delete(0, tk.END)
            # Kosongkan label gambar juga
            self.desain_label.config(text="Belum ada file", fg="gray")
            self.dummy_label.config(text="Belum ada file", fg="gray")
            self.gambar_desain  = None
            self.gambar_dummy = None
            # Kosongkan tabel estimasi jika ada
            for row in self.estimasi_table.get_children():
                self.estimasi_table.delete(row)
            self.estimasi_rows.clear()
        # Jika batal, tidak terjadi apa-apa

    def save_spk(self):
        # Validasi input
        for field, entry in self.entries.items():
            if field != "DUMMY" and entry.get().strip() == "":
                messagebox.showwarning("Input Kosong", f"Kolom '{field}' wajib diisi.")
                return

        if not self.estimasi_rows:
            messagebox.showwarning("Input Kosong", "Minimal 1 tahapan harus ditambahkan.")
            return

        confirm = messagebox.askquestion("Konfirmasi", "Apakah Anda yakin ingin menyimpan data SPK?", icon='question')
        if confirm != 'yes':
            return

        data = {label: entry.get().strip() for label, entry in self.entries.items()}
        images_dir = "images"
        os.makedirs(images_dir, exist_ok=True)

        # Inisialisasi path
        gambar_desain_path = None
        gambar_dummy_path = None
        gambar_potong_path = None  # ✅ BARU

        # Salin file gambar ke direktori tujuan
        try:
            if self.desain_temp_path:
                ext = os.path.splitext(self.desain_temp_path)[1]
                filename = f"desain_{int(time.time())}{ext}"
                gambar_desain_path = os.path.join(images_dir, filename)
                shutil.copy(self.desain_temp_path, gambar_desain_path)
            else:
                messagebox.showwarning("Upload Gambar", "Silakan unggah gambar desain terlebih dahulu.")
                return

            if self.dummy_temp_path:
                ext = os.path.splitext(self.dummy_temp_path)[1]
                filename = f"dummy_{int(time.time())}{ext}"
                gambar_dummy_path = os.path.join(images_dir, filename)
                shutil.copy(self.dummy_temp_path, gambar_dummy_path)

            # ✅ Tambahkan salin gambar potong bahan jika ada
            if self.potong_temp_path:
                ext = os.path.splitext(self.potong_temp_path)[1]
                filename = f"potong_{int(time.time())}{ext}"
                gambar_potong_path = os.path.join(images_dir, filename)
                shutil.copy(self.potong_temp_path, gambar_potong_path)

        except Exception as e:
            messagebox.showerror("Gagal Salin Gambar", f"Gagal menyalin file gambar: {e}")
            return

       # Simpan ke database
        try:
            conn = get_workflow_conn()
            c = conn.cursor()

            # Pastikan semua path gambar valid
            gambar_desain_path = gambar_desain_path if gambar_desain_path and os.path.exists(gambar_desain_path) else None
            gambar_dummy_path = gambar_dummy_path if gambar_dummy_path and os.path.exists(gambar_dummy_path) else None
            gambar_potong_path = gambar_potong_path if gambar_potong_path and os.path.exists(gambar_potong_path) else None

            # Insert data SPK
            c.execute('''
                INSERT INTO spk (
                    order_sales, no_po, costumer, nama_artikel, qty, tanggal_kirim,
                    jenis_bahan, qty_bahan, ukuran_cetak, jumlah_cetak, insheet,
                    total_cetak, warna, finishing,
                    gambar_desain, gambar_dummy, gambar_potong
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data["ORDER SALES"],
                data["NO PO"],
                data["COSTUMER"],
                data["NAMA PRODUK"],
                safe_int(data["QTY"]),
                data["TANGGAL KIRIM"],
                data["JENIS BAHAN"],
                safe_int(data["QTY BAHAN"]),
                data["UKURAN CETAK"],
                safe_int(data["JUMLAH CETAK (DRUK)"]),
                safe_int(data["INSHEET"]),
                safe_int(data["TOTAL CETAK"]),
                data["WARNA"],
                data["FINISHING"],
                gambar_desain_path,
                gambar_dummy_path,
                gambar_potong_path
            ))
            spk_id = c.lastrowid

            # Generate dan simpan barcode
            barcode_data = f"SPK-{spk_id}"
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(barcode_data)
            qr.make(fit=True)
            barcode_img = qr.make_image(fill_color="black", back_color="white")

            img_byte_arr = io.BytesIO()
            barcode_img.save(img_byte_arr, format='PNG')
            barcode_blob = img_byte_arr.getvalue()

            c.execute('''
                UPDATE spk 
                SET barcode_data = ?, barcode_image = ?
                WHERE id = ?
            ''', (barcode_data, barcode_blob, spk_id))

            # Simpan tahapan produksi
            for _, (tahap, mulai, selesai) in self.sort_estimasi_rows().items():
                c.execute('''
                    INSERT INTO spk_tahapan (spk_id, nama_tahapan, mulai, selesai)
                    VALUES (?, ?, ?, ?)
                ''', (spk_id, tahap, mulai, selesai))

            conn.commit()

            # Generate PDF
            costumer = data["COSTUMER"].replace(" ", "_")
            artikel = data["NAMA PRODUK"].replace(" ", "_")
            pdf_filename = f"{costumer}_{artikel}.pdf"
            
            try:
                logo_path = "img/image.png"
                self.generate_pdf(spk_id, gambar_desain_path, gambar_dummy_path, pdf_filename, logo_path)

            except Exception as e:
                print(f"Error generating PDF: {e}")
                # Lanjutkan meskipun PDF gagal dibuat

            conn.close()

            # Pastikan matplotlib menggunakan backend yang benar sebelum show_preview_frame
            import matplotlib
            matplotlib.use('Agg')
            
            self.controller.show_preview_frame(spk_id)

        except sqlite3.Error as e:
            error_msg = f"Database Error:\n{str(e)}"
            messagebox.showerror("Database Error", error_msg)
            print(traceback.format_exc())
        except Exception as e:
            error_msg = f"Gagal menyimpan SPK:\n{str(e)}\n\n"
            error_msg += "Pastikan:\n"
            error_msg += "1. Semua field wajib diisi\n"
            error_msg += "2. Gambar yang diupload valid\n"
            error_msg += "3. Database tersedia dan tidak terkunci"
            messagebox.showerror("Gagal Simpan", error_msg)
            print(traceback.format_exc())
        finally:
            if 'conn' in locals():
                conn.close()


    def generate_pdf(self, spk_id, desain_path, dummy_path, filename, logo_path=None):
        """Fungsi untuk membuat PDF SPK dengan tampilan profesional"""
        os.makedirs("spk_output", exist_ok=True)
        filepath = os.path.join("spk_output", filename)

        try:
            # Ambil data dari database
            conn = get_workflow_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM spk WHERE id = ?", (spk_id,))
            row = cursor.fetchone()
            col_names = [d[0] for d in cursor.description]
            data = dict(zip(col_names, row)) if row else {}
            conn.close()

            # Siapkan PDF
            c = canvas.Canvas(filepath, pagesize=A4)
            width, height = A4
            # Margin lebih kecil untuk naikkan posisi awal
            margin_x, margin_y = 2 * cm, 1 * cm
            y = height - margin_y

            # --- Logo Perusahaan ---
            if logo_path and os.path.exists(logo_path):
                logo_width = 5 * cm
                logo_height = 3 * cm
                c.drawImage(
                    logo_path,
                    (width - logo_width) / 2,
                    y - logo_height,
                    width=logo_width,
                    height=logo_height,
                    preserveAspectRatio=True
                )
                y -= logo_height + 1  # Jarak setelah logo diperkecil

            # --- Judul ---
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(width / 2, y, "SURAT PERINTAH KERJA (SPK)")
            y -= 15  # Jarak setelah judul diperkecil
            c.setLineWidth(1)
            c.line(margin_x, y, width - margin_x, y)
            y -= 15  # Jarak setelah garis diperkecil


            # Style untuk judul dalam tabel
            title_style = ParagraphStyle(
                name='CenterTitle',
                fontName='Helvetica-Bold',
                fontSize=12,
                textColor=colors.white,
                alignment=TA_CENTER
            )

            # --- Tabel Keterangan Produk ---
            info_umum_data = [
                [Paragraph("Keterangan Produk", title_style), ""],
                ["Nomor SPK", f"SPK-{data.get('id', '')}"],
                ["Order Sales", data.get("order_sales", "")],
                ["No PO", data.get("no_po", "")],
                ["Customer", data.get("costumer", "")],
                ["Nama Produk", data.get("nama_artikel", "")],
                ["Qty", format_dengan_titik(data.get("qty", ""))],            
                ["Tanggal Kirim", data.get("tanggal_kirim", "")]                                       
            ]


            col_widths = [5 * cm, 10 * cm]
            total_table_width = sum(col_widths)
            table_x = (width - total_table_width) / 2  # center align table

            info_umum_table = Table(info_umum_data, colWidths=col_widths)
            info_umum_table.setStyle(TableStyle([
                ('SPAN', (0, 0), (1, 0)),
                ('BACKGROUND', (0, 0), (1, 0), colors.black),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 11),
                ('GRID', (0, 1), (-1, -1), 0.5, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))

            w, h = info_umum_table.wrapOn(c, width, y)
            info_umum_table.drawOn(c, table_x, y - h)
            y -= h + 10

            # --- Tabel Spesifikasi Produk ---
            table_data = [
                [Paragraph("Spesifikasi Produk", title_style), ""],
                ["Jenis Bahan", data.get("jenis_bahan", "")],
                ["Qty Bahan", format_dengan_titik(data.get("qty_bahan", ""))],
                ["Ukuran Cetak", data.get("ukuran_cetak", "")],
                ["Jumlah Cetak", format_dengan_titik(data.get("jumlah_cetak", ""))],
                ["Insheet", format_dengan_titik(data.get("insheet", ""))],
                ["Total Cetak", format_dengan_titik(data.get("total_cetak", ""))],
                ["Warna", data.get("warna", "")],
                ["Finishing", data.get("finishing", "")]
            ]

            table = Table(table_data, colWidths=col_widths)
            table.setStyle(TableStyle([
                ('SPAN', (0, 0), (1, 0)),
                ('BACKGROUND', (0, 0), (1, 0), colors.black),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 11),
                ('GRID', (0, 1), (-1, -1), 0.5, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))

            w, h = table.wrapOn(c, width, y)
            table.drawOn(c, table_x, y - h)
            y -= h + 30

            # Gambar
            # Gambar (2x2 layout: Desain, Dummy, Potong, Barcode)
            try:
                from reportlab.lib.utils import ImageReader
                barcode_path = f"temp_barcode_{spk_id}.png"
                qr = qrcode.make(f"SPK-{spk_id}")
                qr.save(barcode_path)

                images = []

                if desain_path and os.path.exists(desain_path):
                    images.append(("Desain", desain_path))
                if dummy_path and os.path.exists(dummy_path):
                    images.append(("Dummy", dummy_path))
                if 'gambar_potong' in data and data['gambar_potong'] and os.path.exists(data['gambar_potong']):
                    images.append(("Potong Bahan", data['gambar_potong']))
                if os.path.exists(barcode_path):
                    images.append(("Barcode", barcode_path))

                img_width = 4 * cm  # dari 5 cm jadi 4 cm
                img_height = 4 * cm
                spacing_x = 1.5 * cm  # lebih rapat
                spacing_y = 1 * cm

                num_cols = 2
                x_start = (width - (num_cols * img_width + (num_cols - 1) * spacing_x)) / 2
                y_start = y - img_height

                for idx, (label, path) in enumerate(images):
                    row = idx // num_cols
                    col = idx % num_cols
                    x = x_start + col * (img_width + spacing_x)
                    y_pos = y_start - row * (img_height + spacing_y + 12)

                    c.drawImage(path, x, y_pos, width=img_width, height=img_height)
                    c.setFont("Helvetica", 9)  # Ukuran label lebih kecil
                    c.drawCentredString(x + img_width / 2, y_pos - 10, label)

                # hitung total tinggi layout gambar
                y -= ((len(images) + 1) // 2) * (img_height + spacing_y + 12)


                # Hapus barcode
                if os.path.exists(barcode_path):
                    os.remove(barcode_path)

            except Exception as e:
                print(f"Error adding images to PDF: {e}")



            # # Footer
            # footer_y = 2.5 * cm
            # c.setFont("Helvetica", 9)
            # c.drawString(margin_x, footer_y, "Dokumen ini dicetak secara otomatis. Harap digunakan sesuai prosedur perusahaan.")
            
            # Selesai halaman pertama, lanjut ke halaman kedua
            c.showPage()  # Mulai halaman baru
            y = height - margin_y  # Reset posisi Y

            if logo_path and os.path.exists(logo_path):
                logo_width = 5 * cm
                logo_height = 3 * cm
                c.drawImage(
                    logo_path,
                    (width - logo_width) / 2,
                    y - logo_height,
                    width=logo_width,
                    height=logo_height,
                    preserveAspectRatio=True
                )
                y -= logo_height + 2


            from reportlab.lib.styles import getSampleStyleSheet

            styles = getSampleStyleSheet()
            title_style = styles['Heading5']
            title_style.fontName = "Helvetica-Bold"
            title_style.fontSize = 12
            title_style.spaceAfter = 6

            info_umum_data = [
                [Paragraph("Keterangan Produk", title_style), ""],
                ["Nomor SPK", f"SPK-{data.get('id', '')}"],
                ["Order Sales", data.get("order_sales", "")],
                ["No PO", data.get("no_po", "")],
                ["Customer", data.get("costumer", "")],
                ["Nama Produk", data.get("nama_artikel", "")],
                ["Qty", format_dengan_titik(data.get("qty", ""))],
            ]

            info_table = Table(info_umum_data, colWidths=[5 * cm, 10 * cm])
            info_table.setStyle(TableStyle([
                ('GRID', (0, 1), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
                ('SPAN', (0, 0), (-1, 0)),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))

            w, h = info_table.wrapOn(c, width, y)
            if y - h < 3 * cm:
                c.showPage()
                y = height - margin_y
            info_table.drawOn(c, margin_x, y - h)
            y -= h + 25  # spasi sebelum tabel estimasi


            # Data Estimasi Tahapan Produksi
            y -= 25
            c.setFont("Helvetica-Bold", 12)
            c.drawString(margin_x, y, "Rangkuman Estimasi Tahapan Produksi:")
            y -= 15

            estimasi_data = self.sort_estimasi_rows()

            table_data = [["Tahapan", "Mulai", "Selesai"]]
            for _, (tahap, mulai, selesai) in estimasi_data.items():
                table_data.append([tahap, mulai, selesai])

            # Buat tabel estimasi
            col_widths = [6 * cm, 5.5 * cm, 5.5 * cm]  # Lebih lebar

            estimasi_table = Table(table_data, colWidths=col_widths)

            # Gaya tabel profesional
            estimasi_table.setStyle(TableStyle([
                # Border dan grid
                ('GRID', (0, 0), (-1, -1), 0.75, colors.HexColor('#555555')),

                # Header styling
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),  # biru gelap
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),

                # Isi tabel styling
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 11),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),

                # Padding supaya longgar
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))


            w, h = estimasi_table.wrapOn(c, width, y)
            if y - h < 3 * cm:  # kalau tidak cukup di halaman
                c.showPage()
                y = height - margin_y
            estimasi_table.drawOn(c, margin_x, y - h)
            y -= h + 25


            # Simpan PDF
            c.save()


            # Cetak otomatis (opsional)
            self.print_pdf(filepath)

            messagebox.showinfo("Sukses", f"SPK berhasil disimpan dan PDF telah dibuat:\n{filepath}")

        except Exception as e:
            messagebox.showerror("Gagal Buat PDF", f"Gagal membuat file PDF:\n{e}")

    def print_pdf(self, filepath):
        """Fungsi untuk mencetak PDF secara otomatis"""
        try:
            if platform.system() == "Windows":
                os.startfile(filepath, "print")
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["lp", filepath])
            else:  # Linux
                subprocess.run(["lp", filepath])
        except Exception as e:
            print(f"Gagal mencetak PDF: {e}")

    def generate_barcode_image(self, data):
        """Generate QR Code image"""
        import qrcode
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        return qr.make_image(fill_color="black", back_color="white")

    def go_dashboard(self):
        self.master.switch_frame(__import__('ui_dashboard').DashboardFrame)

    def build_estimasi_section(self):
        separator = ttk.Separator(self.container, orient="horizontal")
        separator.pack(fill="x", pady=20)

        tk.Label(
            self.container,
            text="Estimasi Tahapan Produksi",
            font=("Arial", 24, "bold"),
            padx=10,
            pady=10
        ).pack(pady=(10, 10), fill="x")

        # Frame Tambah Tahapan
        tambah_frame = tk.Frame(self.container, bg="#ffffff", relief="groove", borderwidth=2)
        tambah_frame.pack(pady=20, padx=20, fill="x", ipady=15)

        self.tahapan_options = [
            "DESAIN", "ACC DESAIN", "DUMMY", "CTP", "POTONG BAHAN", "CETAK",
            "POND", "FORMING", "LAMINATING / VARNISH", "PACKING", "POLI", "EMBOS", "SPOT UV", 
            "LEM", "SPIRAL"
        ]

        label_font = ("Arial", 14, "bold")
        entry_font = ("Arial", 14)

        # Baris input
        tk.Label(tambah_frame, text="Tahapan:", font=label_font, bg="#ffffff").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.selected_tahapan = ttk.Combobox(
            tambah_frame,
            values=self.tahapan_options,
            state="readonly",
            width=25,
            font=("Arial", 14),
            style="Big.TCombobox"  # pakai style besar
        )

        self.selected_tahapan.grid(row=0, column=1, padx=12, pady=10)

        tk.Label(tambah_frame, text="Mulai (tgl & jam):", font=label_font, bg="#ffffff").grid(row=0, column=2, padx=12, pady=10, sticky="w")
        self.mulai_tanggal = DateEntry(tambah_frame, width=12, date_pattern="dd-mm-yyyy", locale="id_ID", state="readonly", font=entry_font)
        self.mulai_tanggal.grid(row=0, column=3, padx=5, pady=10)
        self.mulai_jam = tk.Entry(tambah_frame, width=8, font=entry_font)
        self.mulai_jam.insert(0, "08:00")
        self.mulai_jam.grid(row=0, column=4, padx=5, pady=10)

        tk.Label(tambah_frame, text="Selesai (tgl & jam):", font=label_font, bg="#ffffff").grid(row=0, column=5, padx=12, pady=10, sticky="w")
        self.selesai_tanggal = DateEntry(tambah_frame, width=12, date_pattern="dd-mm-yyyy", locale="id_ID", state="readonly", font=entry_font)
        self.selesai_tanggal.grid(row=0, column=6, padx=5, pady=10)
        self.selesai_jam = tk.Entry(tambah_frame, width=8, font=entry_font)
        self.selesai_jam.insert(0, "17:00")
        self.selesai_jam.grid(row=0, column=7, padx=5, pady=10)

        # Tombol "Tambah"
        add_button = tk.Button(
            tambah_frame,
            text="➕ Tambah",
            command=self.tambah_tahapan,
            bg="#28a745",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=15,
            pady=5,
            relief="flat",
            cursor="hand2"
        )
        add_button.grid(row=0, column=8, padx=15, pady=10)
        add_button.bind("<Enter>", lambda e: add_button.config(bg="#218838"))
        add_button.bind("<Leave>", lambda e: add_button.config(bg="#28a745"))

        # Tabel Estimasi
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 16, "bold"))
        style.configure("Treeview", font=("Arial", 14), rowheight=40)

        self.estimasi_table = ttk.Treeview(self.container, columns=("Tahap", "Mulai", "Selesai", "Aksi"), show="headings", height=8)
        self.estimasi_table.heading("Tahap", text="Tahapan", anchor="center")
        self.estimasi_table.heading("Mulai", text="Mulai", anchor="center", command=self.sort_estimasi_table)
        self.estimasi_table.heading("Selesai", text="Selesai", anchor="center")
        self.estimasi_table.heading("Aksi", text="Aksi", anchor="center")

        self.estimasi_table.column("Tahap", width=300, anchor="center")
        self.estimasi_table.column("Mulai", width=300, anchor="center")
        self.estimasi_table.column("Selesai", width=300, anchor="center")
        self.estimasi_table.column("Aksi", width=300, anchor="center")

        self.estimasi_table.pack(pady=20, padx=30)
        self.estimasi_rows = {}

        self.estimasi_table.tag_configure('oddrow', background="#ffffff")
        self.estimasi_table.tag_configure('evenrow', background="#f0f0f0")

        self.estimasi_table.bind("<Button-1>", self.hapus_row_tahapan)

        self.estimasi_table.pack(pady=10)
        self.estimasi_rows = {}  # simpan tombol hapus

    def parse_datetime(self, datetime_str):
        try:
            return datetime.strptime(datetime_str, "%d-%m-%Y %H:%M")
        except ValueError:
            return None

    def validate_schedule(self, new_start, new_end):
        # Check all existing schedules
        for item in self.estimasi_table.get_children():
            start_str = self.estimasi_table.item(item, "values")[1]
            end_str = self.estimasi_table.item(item, "values")[2]
            existing_start = self.parse_datetime(start_str)
            existing_end = self.parse_datetime(end_str)

            if (new_start < existing_end) and (new_end > existing_start):
                return False, "Bentrok dengan jadwal yang sudah ada!"

        return True, ""

    def validate_tahapan(self, tahap):
        for item in self.estimasi_table.get_children():
            existing_tahap = self.estimasi_table.item(item, "values")[0]
            if existing_tahap == tahap:
                return False, "Tahapan sudah ada!"

        return True, ""

    def find_insert_position(self, new_start):
        children = self.estimasi_table.get_children()
        for pos, child in enumerate(children):
            child_start_str = self.estimasi_table.item(child, "values")[1]
            child_start = self.parse_datetime(child_start_str)
            if new_start < child_start:
                return pos
        return "end"

    def sort_estimasi_table(self):
        items = [(self.estimasi_table.item(item, "values"), item) 
                for item in self.estimasi_table.get_children()]

        items.sort(key=lambda x: datetime.strptime(x[0][1], "%Y-%m-%d %H:%M"))

        for index, (_, item) in enumerate(items):
            self.estimasi_table.move(item, "", index)

    def sort_estimasi_rows(self):
        sorted_estimasi_rows = sorted(
            self.estimasi_rows.items(), key=lambda x: x[1][1]
        )
        return {key: value for key, value in sorted_estimasi_rows}

    def tambah_tahapan(self):
        tahap = self.selected_tahapan.get()
        mulai = f"{self.mulai_tanggal.get_date().strftime('%d-%m-%Y')} {self.mulai_jam.get()}"
        selesai = f"{self.selesai_tanggal.get_date().strftime('%d-%m-%Y')} {self.selesai_jam.get()}"

        if not tahap:
            messagebox.showwarning("Input Kosong", "Pilih tahapan terlebih dahulu.")
            return

        valid, msg = self.validate_tahapan(tahap)
        if not valid:
            messagebox.showerror("Tahapan duplikat", msg)
            return

        try:
            new_start = datetime.strptime(mulai, "%d-%m-%Y %H:%M")
            new_end = datetime.strptime(selesai, "%d-%m-%Y %H:%M")
        except ValueError:
            messagebox.showwarning("Format salah", "Format waktu tidak valid! Gunakan HH:MM")
            return

        if new_start >= new_end:
            messagebox.showwarning("Kesalahan input", "Waktu mulai harus sebelum waktu selesai!")
            return

        valid, msg = self.validate_schedule(new_start, new_end)
        if not valid:
            messagebox.showerror("Bentrok jadwal", msg)
            return

        # cari posisi insert
        insert_pos = self.find_insert_position(new_start)

        row_id = self.estimasi_table.insert("", insert_pos, values=(tahap, mulai, selesai, "❌"))

        self.estimasi_rows[row_id] = (tahap, mulai, selesai)

        row_tag = "oddrow" if len(self.estimasi_rows) % 2 else "evenrow"
        self.estimasi_table.item(row_id, tags=row_tag)

    def hapus_row_tahapan(self, event):
        region = self.estimasi_table.identify("region", event.x, event.y)
        if region == "cell":
            col = self.estimasi_table.identify_column(event.x)
            if col == "#4":  # kolom aksi
                row_id = self.estimasi_table.identify_row(event.y)
                if row_id:
                    confirm = messagebox.askyesno("Hapus Tahapan", "Yakin ingin menghapus tahapan ini?")
                    if confirm:
                        self.estimasi_table.delete(row_id)
                        if row_id in self.estimasi_rows:
                            del self.estimasi_rows[row_id]

    def upload_desain(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg *.bmp")])
        if file_path:
            self.desain_temp_path = file_path
            image = Image.open(file_path)
            image = image.resize((100, 100))
            photo = ImageTk.PhotoImage(image)

            if hasattr(self, 'desain_label'):
                self.desain_label.configure(image=photo)
                self.desain_label.image = photo
            else:
                self.desain_label = tk.Label(self, image=photo)
                self.desain_label.image = photo
                self.desain_label.grid(row=15, column=2)

    def remove_desain(self):
        if self.desain_label:
            self.desain_label.configure(image="")
            self.desain_temp_path = None

    def upload_dummy(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg *.bmp")])
        if file_path:
            self.dummy_temp_path = file_path
            image = Image.open(file_path)
            image = image.resize((100, 100))
            photo = ImageTk.PhotoImage(image)

            if hasattr(self, 'dummy_label'):
                self.dummy_label.configure(image=photo)
                self.dummy_label.image = photo
            else:
                self.dummy_label = tk.Label(self, image=photo)
                self.dummy_label.image = photo
                self.dummy_label.grid(row=16, column=2)
    def remove_dummy(self):
        if self.dummy_label:
            self.dummy_label.configure(image="")
            self.dummy_temp_path = None

    def upload_potong(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg *.bmp")])
        if file_path:
            self.potong_temp_path = file_path
            image = Image.open(file_path)
            image = image.resize((100, 100))
            photo = ImageTk.PhotoImage(image)

            if hasattr(self, 'potong_label'):
                self.potong_label.configure(image=photo)
                self.potong_label.image = photo
            else:
                self.potong_label = tk.Label(self, image=photo)
                self.potong_label.image = photo
                self.potong_label.grid(row=17, column=2)

    def remove_potong(self):
        if self.potong_label:
            self.potong_label.configure(image="")
            self.potong_temp_path = None
