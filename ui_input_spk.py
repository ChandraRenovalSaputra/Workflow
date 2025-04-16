import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
from tkinter import filedialog
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

class SPKInputFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.entries = {}
        self.desain_temp_path = None
        self.dummy_temp_path = None
        self.gambar_desain = None
        self.gambar_dummy = None

        scroll = ScrollableFrame(self)
        scroll.pack(fill="both", expand=True)

        self.container = scroll.scrollable_frame

        # ===== Judul Halaman =====
        title = tk.Label(self.container, text="Input SPK", font=("Arial", 20, "bold"))
        title.pack(pady=10)

        self.entries = {}
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

        for field in form_fields:
            self.add_form_row(field[0], field[1] if len(field) > 1 else None)

       # ===== Upload Gambar Desain & Dummy =====
        tk.Label(self.container, text="Upload Gambar Desain:").pack(anchor="w", padx=20)
        self.desain_label = tk.Label(self.container, text="Belum ada file", fg="gray")
        self.desain_label.pack(anchor="w", padx=20)
        tk.Button(self.container, text="Pilih File", command=self.upload_desain).pack(pady=(0,10), padx=20, anchor="w")
        tk.Button(self.container, text="Hapus File", command=self.remove_desain).pack(pady=(0,10), padx=20, anchor="w")

        tk.Label(self.container, text="Upload Gambar Dummy:").pack(anchor="w", padx=20)
        self.dummy_label = tk.Label(self.container, text="Belum ada file", fg="gray")
        self.dummy_label.pack(anchor="w", padx=20)
        tk.Button(self.container, text="Pilih File", command=self.upload_dummy).pack(pady=(0,10), anchor="w", padx=20)
        tk.Button(self.container, text="Hapus File", command=self.remove_dummy  ).pack(pady=(0,10), anchor="w", padx=20)

        # ===== Estimasi Tahapan =====
        self.build_estimasi_section()

        # ===== Tombol Navigasi Paling Bawah =====
        button_frame = tk.Frame(self.container)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Dashboard", command=self.go_dashboard, width=15).pack(side="left", padx=10)
        tk.Button(button_frame, text="Hapus", command=self.clear_form, width=15).pack(side="left", padx=10)
        tk.Button(button_frame, text="Simpan", command=self.save_spk, width=15).pack(side="left", padx=10)



# ====================================================DEF===================================================
    def add_form_row(self, label_text, input_type=None):
        frame = tk.Frame(self.container)
        frame.pack(fill="x", pady=3, padx=20)

        label = tk.Label(frame, text=label_text, width=25, anchor="w")
        label.pack(side="left")

        if input_type == "date":
            today = datetime.today().date()
            entry = DateEntry(frame, date_pattern='yyyy-mm-dd', mindate=today)
        else:
            entry = tk.Entry(frame)
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
            else:
                messagebox.showwarning("Upload Gambar", "Silakan unggah gambar dummy terlebih dahulu.")
                return

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
            img_byte_arr = io.BytesIO()  # Perbaikan: gunakan BytesIO dengan huruf besar
            barcode_img.save(img_byte_arr, format='PNG')
            barcode_blob = img_byte_arr.getvalue()

            # Update SPK dengan data barcode
            c.execute('''
                UPDATE spk 
                SET barcode_data = ?, barcode_image = ?
                WHERE id = ?
            ''', (barcode_data, barcode_blob, spk_id))

            # Simpan tahapan produksi
            for row_id, (tahap, mulai, selesai) in self.estimasi_rows.items():
                c.execute('''
                    INSERT INTO spk_tahapan (spk_id, nama_tahapan, mulai, selesai)
                    VALUES (?, ?, ?, ?)
                ''', (spk_id, tahap, mulai, selesai))

            conn.commit()
            conn.close()

            self.controller.show_preview_frame(spk_id)

        except Exception as e:
            tb = traceback.format_exc()
            messagebox.showerror("Gagal Simpan", f"Gagal menyimpan data SPK:\n{e}\n\n{tb}")

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
        separator.pack(fill="x", pady=10)

        tk.Label(self.container, text="Estimasi Tahapan Produksi", font=("Arial", 14, "bold")).pack(pady=(10, 5))

        # Frame Tambah Tahapan
        tambah_frame = tk.Frame(self.container)
        tambah_frame.pack(pady=5)

        self.tahapan_options = [
            "DESAIN", "ACC DESAIN", "DUMMY", "CTP", "POTONG BAHAN", "CETAK",
            "POND", "FORMING", "LAMINATING", "PACKING", "PENGIRIMAN", "DITERIMA COSTUMER"
        ]

        tk.Label(tambah_frame, text="Tahapan:").grid(row=0, column=0)
        self.selected_tahapan = ttk.Combobox(tambah_frame, values=self.tahapan_options, state="readonly")
        self.selected_tahapan.grid(row=0, column=1, padx=5)

        tk.Label(tambah_frame, text="Mulai (tgl & jam):").grid(row=0, column=2)
        self.mulai_tanggal = DateEntry(tambah_frame, width=10, date_pattern="yyyy-mm-dd", locale="id_ID")
        self.mulai_tanggal.grid(row=0, column=3)
        self.mulai_jam = tk.Entry(tambah_frame, width=5)
        self.mulai_jam.insert(0, "08:00")
        self.mulai_jam.grid(row=0, column=4, padx=(0, 5))

        tk.Label(tambah_frame, text="Selesai (tgl & jam):").grid(row=0, column=5)
        self.selesai_tanggal = DateEntry(tambah_frame, width=10, date_pattern="yyyy-mm-dd", locale="id_ID")
        self.selesai_tanggal.grid(row=0, column=6)
        self.selesai_jam = tk.Entry(tambah_frame, width=5)
        self.selesai_jam.insert(0, "17:00")
        self.selesai_jam.grid(row=0, column=7, padx=(0, 5))

        tk.Button(tambah_frame, text="Tambah", command=self.tambah_tahapan).grid(row=0, column=8, padx=5)

        # Tabel Estimasi
        self.estimasi_table = ttk.Treeview(self.container, columns=("Tahap", "Mulai", "Selesai", "Aksi"), show="headings")
        self.estimasi_table.heading("Tahap", text="Tahapan")
        self.estimasi_table.heading("Mulai", text="Mulai")
        self.estimasi_table.heading("Selesai", text="Selesai")
        self.estimasi_table.heading("Aksi", text="Aksi")

        self.estimasi_table.column("Tahap", width=120)
        self.estimasi_table.column("Mulai", width=150)
        self.estimasi_table.column("Selesai", width=150)
        self.estimasi_table.column("Aksi", width=80)

        self.estimasi_table.pack(pady=10)
        self.estimasi_rows = {}  # simpan tombol hapus

    def tambah_tahapan(self):
        tahap = self.selected_tahapan.get()
        mulai = f"{self.mulai_tanggal.get_date().strftime('%Y-%m-%d')} {self.mulai_jam.get()}"
        selesai = f"{self.selesai_tanggal.get_date().strftime('%Y-%m-%d')} {self.selesai_jam.get()}"

        if not tahap:
            messagebox.showwarning("Input Kosong", "Pilih tahapan terlebih dahulu.")
            return

        # Tambah ke tabel
        row_id = self.estimasi_table.insert("", "end", values=(tahap, mulai, selesai, "❌"))

        # Simpan referensi tombol hapus
        self.estimasi_rows[row_id] = (tahap, mulai, selesai)
        self.estimasi_table.bind("<Button-1>", self.hapus_row_tahapan)

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
