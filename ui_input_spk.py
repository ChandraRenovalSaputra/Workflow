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

class SPKInputFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f2f5")
        self.controller = controller
        self.entries = {}
        self.desain_temp_path = None
        self.dummy_temp_path = None
        self.gambar_desain = None
        self.gambar_dummy = None

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
            ("NAMA ARTIKEL",),
            ("QTY",),
            ("TANGGAL KIRIM", "date"),
            ("JENIS BAHAN",),
            ("QTY BAHAN",),
            ("UKURAN CETAK",),
            ("JUMLAH CETAK (DRUK)",),
            ("INSHEET",),
            ("TOTAL CETAK",),
            ("WARNA",),
            ("VARNISH",),
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
            # Custom style for DateEntry
            style = ttk.Style()
            style.theme_use("default")

            style.configure(
                "my.DateEntry",
                fieldbackground="white",
                background="#0078D7",
                foreground="black",
                arrowcolor="white",
                bordercolor="#ccc",
                lightcolor="#0078D7",
                darkcolor="#005a9e",
                relief="flat",
                padding=5
            )

            today = datetime.today().date()
            entry = DateEntry(
                frame,
                date_pattern='yyyy-mm-dd',
                mindate=today,
                state="readonly",
                width=20,
                style="my.DateEntry",
                font=("Segoe UI", 14)
            )

        else:
            entry = tk.Entry(frame, font=("Segoe UI", 14)) 
        entry.pack(side="left", fill="x", expand=True)

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

        except Exception as e:
            messagebox.showerror("Gagal Salin Gambar", f"Gagal menyalin file gambar: {e}")
            return

        # Simpan ke database
        try:
            conn = get_workflow_conn()
            c = conn.cursor()

            # Insert data SPK tanpa barcode dulu
            c.execute('''
                INSERT INTO spk (
                    order_sales, no_po, costumer, nama_artikel, qty, tanggal_kirim,
                    jenis_bahan, qty_bahan, ukuran_cetak, jumlah_cetak, insheet,
                    total_cetak, warna, varnish, finishing, gambar_desain, gambar_dummy
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data["ORDER SALES"],
                data["NO PO"],
                data["COSTUMER"],
                data["NAMA ARTIKEL"],
                int(data["QTY"]),
                data["TANGGAL KIRIM"],
                data["JENIS BAHAN"],
                data["QTY BAHAN"],
                data["UKURAN CETAK"],
                data["JUMLAH CETAK (DRUK)"],
                data["INSHEET"],
                data["TOTAL CETAK"],
                data["WARNA"],
                data["VARNISH"],
                data["FINISHING"],
                gambar_desain_path,
                gambar_dummy_path
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

            # Convert image to BLOB
            img_byte_arr = io.BytesIO()
            barcode_img.save(img_byte_arr, format='PNG')
            barcode_blob = img_byte_arr.getvalue()

            # Update SPK dengan data barcode
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

            # Generate nama file PDF berdasarkan costumer dan nama artikel
            costumer = data["COSTUMER"].replace(" ", "_")
            artikel = data["NAMA ARTIKEL"].replace(" ", "_")
            pdf_filename = f"{costumer}_{artikel}.pdf"

            # Buat PDF otomatis
            self.generate_pdf(spk_id, gambar_desain_path, gambar_dummy_path, pdf_filename)

            conn.close()

            self.controller.show_preview_frame(spk_id)

        except Exception as e:
            tb = traceback.format_exc()
            messagebox.showerror("Gagal Simpan", f"Gagal menyimpan data SPK:\n{e}\n\n{tb}")

    def generate_pdf(self, spk_id, desain_path, dummy_path, filename):
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
            margin_x, margin_y = 2 * cm, 2 * cm
            y = height - margin_y

            # Judul utama
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(width / 2, y, "SURAT PERINTAH KERJA (SPK)")
            y -= 20
            c.setLineWidth(1)
            c.line(margin_x, y, width - margin_x, y)
            y -= 30

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
                ["Tanggal Kirim", data.get("tanggal_kirim", "")],
                ["Customer", data.get("costumer", "")],
                ["Order Sales", data.get("order_sales", "")],
                ["No PO", data.get("no_po", "")],
                ["Nama Artikel", data.get("nama_artikel", "")]
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
            y -= h + 30

            # --- Tabel Spesifikasi Produk ---
            table_data = [
                [Paragraph("Spesifikasi Produk", title_style), ""],
                ["Jenis Bahan", data.get("jenis_bahan", "")],
                ["Qty Bahan", data.get("qty_bahan", "")],
                ["Ukuran Cetak", data.get("ukuran_cetak", "")],
                ["Jumlah Cetak", data.get("jumlah_cetak", "")],
                ["Insheet", data.get("insheet", "")],
                ["Total Cetak", data.get("total_cetak", "")],
                ["Warna", data.get("warna", "")],
                ["Varnish", data.get("varnish", "")],
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
            try:
                from reportlab.lib.utils import ImageReader
                barcode_path = f"temp_barcode_{spk_id}.png"
                qr = qrcode.make(f"SPK-{spk_id}")
                qr.save(barcode_path)

                img_width = 4 * cm
                spacing_img = 2 * cm  # bisa diatur sesuai selera
                images = []

                if desain_path and os.path.exists(desain_path):
                    images.append(("Desain", desain_path))
                if os.path.exists(barcode_path):
                    images.append(("Barcode", barcode_path))
                if dummy_path and os.path.exists(dummy_path):
                    images.append(("Dummy", dummy_path))

                total_width = len(images) * img_width + (len(images) - 1) * spacing_img
                img_x = (width - total_width) / 2  # Mulai dari tengah
                img_y = y - img_width

                for label, path in images:
                    c.drawImage(path, img_x, img_y, width=img_width, height=img_width)
                    c.drawCentredString(img_x + img_width / 2, img_y - 12, label)
                    img_x += img_width + spacing_img

                # Hapus barcode setelah selesai dipakai
                if os.path.exists(barcode_path):
                    os.remove(barcode_path)

            except Exception as e:
                print(f"Error adding images to PDF: {e}")


            # Footer
            footer_y = 2.5 * cm
            c.setFont("Helvetica", 9)
            c.drawString(margin_x, footer_y, "Dokumen ini dicetak secara otomatis. Harap digunakan sesuai prosedur perusahaan.")

            # Selesai
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
            "POND", "FORMING", "LAMINATING", "PACKING", "PENGIRIMAN", "DITERIMA COSTUMER"
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

    def potong_bahan(self):
        if self.dummy_label:
            self.dummy_label.configure(image="")
            self.dummy_temp_path = None

    def memek(self):
        if self.dummy_label:
            self.dummy_label.configure(image="")
            self.dummy_temp_path = None