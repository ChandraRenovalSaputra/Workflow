import sqlite3
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from db import get_spk_details, update_keterangan_tahapan
from PIL import Image, ImageTk
import io
import qrcode
from datetime import datetime
from io import BytesIO
from tkinter import ttk
import tkinter as tk

def center_window(root, width=1600, height=800):
    """Menempatkan window di tengah layar"""
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")  # Tentukan ukuran dan posisi
    root.minsize(width, height)  # Ukuran minimal untuk window

def show_spk_detail(controller, spk_id):
    """ Fungsi untuk beralih ke halaman DetailSPKFrame """
    controller.switch_frame(DetailSPKFrame, spk_id)

class DetailSPKFrame(Frame):
    def __init__(self, parent, controller, spk_id):
        super().__init__(parent)
        self.controller = controller
        self.spk_id = spk_id
        self.configure(bg='#f0f2f5')

        # === HEADER ===
        header = Frame(self, bg="#0078D7", height=60)
        header.pack(side="top", fill="x")

        title = Label(
            header, text=f"🧾 Detail SPK - {spk_id}",
            font=("Segoe UI", 18, "bold"), bg="#0078D7", fg="white"
        )
        title.pack(side="left", padx=20, pady=10)

        # === SCROLLABLE ===
        self.canvas = Canvas(self, bg="#f0f2f5", highlightthickness=0)
        self.scrollbar = Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = Frame(self.canvas, bg="#f0f2f5")
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.bind_scroll_event()

        # === DATA SPK ===
        spk_data, tahapan_data = get_spk_details(spk_id)
        if spk_data:
            # Bungkus agar bisa center
            wrapper = Frame(self.scrollable_frame, bg='#f0f2f5')
            wrapper.pack(pady=20)

            detail_card = Frame(wrapper, bg='white', bd=2, relief='groove')
            detail_card.pack(padx=550)

            Label(
                detail_card, text="🗝️ INFORMASI SPK",
                font=('Segoe UI', 18, 'bold'), bg='white', fg='#222'
            ).grid(row=0, column=0, columnspan=3, sticky="w", padx=20, pady=(20, 10))

            labels = [
                ("ORDER SALES", spk_data[1]), ("NO PO", spk_data[2]),
                ("CUSTOMER", spk_data[3]), ("NAMA ARTIKEL", spk_data[4]),
                ("QTY", spk_data[5]), ("TANGGAL KIRIM", spk_data[6]),
                ("JENIS BAHAN", spk_data[7]), ("QTY BAHAN", spk_data[8]),
                ("UKURAN CETAK", spk_data[9]), ("JUMLAH CETAK", spk_data[10]),
                ("INSHEET", spk_data[11]), ("TOTAL CETAK", spk_data[12]),
                ("WARNA", spk_data[13]), ("VARNISH", spk_data[14]),
                ("FINISHING", spk_data[15])
            ]

            for i, (label_text, value) in enumerate(labels, start=1):
                Label(detail_card, text=label_text, font=('Segoe UI', 12, 'bold'), bg='white').grid(
                    row=i, column=0, sticky='w', padx=(20, 5), pady=6)
                Label(detail_card, text=":", font=('Segoe UI', 12), bg='white').grid(
                    row=i, column=1, sticky='w', padx=5, pady=6)
                Label(detail_card, text=value, font=('Segoe UI', 12), bg='white').grid(
                    row=i, column=2, sticky='w', padx=(5, 20), pady=6)

            # Atur lebar kolom supaya rapi
            detail_card.grid_columnconfigure(0, minsize=150)
            detail_card.grid_columnconfigure(2, minsize=550)

        else:
            Label(self.scrollable_frame, text="❌ Data tidak ditemukan.", bg='#f0f2f5').pack()


        # === GAMBAR FRAME ===
        if spk_data:
            img_container = Frame(self.scrollable_frame, bg='#f0f2f5')
            img_container.pack(padx=30, pady=10, fill='x')

            img_frame = Frame(img_container, bg='#f0f2f5')
            img_frame.pack(anchor="center")


            # Desain
            self.add_image_column(img_frame, 0, spk_data[16], "Desain")
            # Barcode
            barcode_img = self.generate_barcode_image() if not (len(spk_data) > 18 and spk_data[19]) else Image.open(io.BytesIO(spk_data[19]))
            self.add_image_column(img_frame, 1, barcode_img, "Barcode")
            # Dummy
            self.add_image_column(img_frame, 2, spk_data[17], "Dummy")

        # === WORKFLOW PRODUKSI ===
        Label(
            self.scrollable_frame, text="📋 WORKFLOW PRODUKSI",
            font=('Segoe UI', 18, 'bold'), bg='#f0f2f5', fg='#2c3e50'
        ).pack(pady=(20, 10))



        workflow_frame = Frame(self.scrollable_frame, bg='white', bd=1, relief='solid')
        workflow_frame.pack(padx=30, fill='both')

        headers = ["Tahap", "Estimasi", "Mulai", "Selesai", "Status", "Keterangan"]
        # HEADER
        for col, header in enumerate(headers):
            Label(
                workflow_frame, text=header, font=('Segoe UI', 12, 'bold'),
                bg='#0056b3', fg='white', padx=25, pady=12
            ).grid(row=0, column=col, sticky='nsew')

        # Get scan data from spk_tracking
        conn = sqlite3.connect("workflow.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                tahapan,
                MAX(scan_mulai) as mulai,
                MAX(scan_selesai) as selesai
            FROM spk_tracking 
            WHERE spk_id = ?
            GROUP BY tahapan
        """, (self.spk_id,))
        scan_data = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}
        conn.close()

        for i in range(len(headers)):
            workflow_frame.grid_columnconfigure(i, weight=1)

        # ISI
        if tahapan_data:
            
            self.keterangan_vars = []

            for row, (tahap, mulai, selesai, keterangan) in enumerate(tahapan_data, start=1):
                status, bg_color = self.tentukan_status(mulai, selesai)
                estimasi = f"{mulai[:10]} - {selesai[:10]}" if selesai else "-"

                base_font = ('Segoe UI', 12)
                status_font = ('Segoe UI', 12, 'bold')

                Label(workflow_frame, text=tahap, bg='white', font=base_font).grid(row=row, column=0, sticky='nsew', padx=5, pady=6)
                Label(workflow_frame, text=estimasi, bg='white', font=base_font).grid(row=row, column=1, sticky='nsew', padx=5, pady=6)
                Label(workflow_frame, text=mulai or "-", bg='white', font=base_font).grid(row=row, column=2, sticky='nsew', padx=5, pady=6)
                Label(workflow_frame, text=selesai or "-", bg='white', font=base_font).grid(row=row, column=3, sticky='nsew', padx=5, pady=6)

                Label(
                    workflow_frame, text=status, bg=bg_color, fg='white',
                    font=status_font, relief='ridge', bd=2
                ).grid(row=row, column=4, sticky='nsew', padx=5, pady=6)

                # Keterangan Entry
                keterangan_var = StringVar(value=keterangan if keterangan else "")
                self.keterangan_vars.append((tahap, keterangan_var))

                entry_bg = "#ffffff"
                if status == "TERLAMBAT" and not keterangan:
                    keterangan_var.set("Harap isi alasan keterlambatan")
                    entry_bg = "#ffeeba"  # kuning soft

                entry = Entry(
                    workflow_frame, textvariable=keterangan_var, font=base_font,
                    bg=entry_bg, relief='solid', bd=1, highlightthickness=1, highlightbackground='#ccc'
                )
                entry.grid(row=row, column=5, sticky='nsew', padx=5, pady=6, ipady=6)


        # === BUTTONS ===
        button_frame = Frame(self.scrollable_frame, bg='#f0f2f5')
        button_frame.pack(pady=30)

        ttk.Style().configure("Green.TButton", font=('Segoe UI', 12, 'bold'), padding=10)
        ttk.Button(button_frame, text="💾 Simpan Keterangan", command=self.simpan_keterangan, style="Green.TButton").pack(side="left", padx=10)
        ttk.Button(button_frame, text="⏪ Kembali ke Jadwal", command=self.kembali_ke_jadwal, style="Green.TButton").pack(side="left", padx=10)

    
    def bind_scroll_event(self):
        """Binding scroll agar bisa dipakai di Windows"""
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        """Fungsi scroll mouse (untuk Windows)"""
        self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")

    def generate_barcode_image(self, size=(200, 200)):
        """Generate QR Code untuk SPK"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(f"SPK-{self.spk_id}")
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img = img.resize(size)
        
        # Convert ke format yang bisa ditampilkan di Tkinter
        bio = BytesIO()
        img.save(bio, format="PNG")
        return Image.open(bio)

    def tentukan_status(self, mulai, selesai):
        """Menentukan status tahapan berdasarkan tanggal"""
        if not selesai:
            return "BELUM", "#6c757d"  # Gray
        
        try:
            mulai_date = datetime.strptime(mulai[:10], "%Y-%m-%d").date()
            selesai_date = datetime.strptime(selesai[:10], "%Y-%m-%d").date()
            today = datetime.now().date()
            
            if today < mulai_date:
                return "BELUM", "#6c757d"  # Gray
            elif mulai_date <= today <= selesai_date:
                return "SEDANG BERJALAN", "#007bff"  # Blue
            elif today > selesai_date:
                return "TERLAMBAT", "#dc3545"  # Red
            else:
                return "SELESAI", "#28a745"  # Green
        except:
            return "SELESAI", "#28a745"  # Green

    def simpan_keterangan(self):
        """Validasi dan simpan keterangan ke database"""
        # Validasi untuk tahap yang terlambat
        for tahap, var in self.keterangan_vars:
            if "TERLAMBAT" in var.get() and not var.get().strip():
                messagebox.showerror("Error", 
                    f"Keterangan wajib diisi untuk tahap {tahap} yang terlambat!")
                return
        
        # Simpan ke database
        try:
            for tahap, var in self.keterangan_vars:
                if var.get().strip():  # Hanya simpan jika ada isinya
                    success = update_keterangan_tahapan(self.spk_id, tahap, var.get())
                    if not success:
                        raise Exception(f"Gagal menyimpan keterangan untuk tahap {tahap}")
            
            messagebox.showinfo("Sukses", "Keterangan berhasil disimpan!")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan ke database: {str(e)}")
        
    def kembali_ke_jadwal(self):
        from lihat_jadwal_frame import LihatJadwalFrame
        self.controller.switch_frame(LihatJadwalFrame)

    def add_tracking_section(self):
        tracking_frame = Frame(self)
        tracking_frame.pack(pady=10)
        
        Label(tracking_frame, text="Riwayat Tracking", font=('Arial', 14)).pack()
        
        # Tabel riwayat scan
        columns = ("Tahap", "Mulai", "Selesai", "Durasi", "Operator")
        self.tracking_tree = ttk.Treeview(tracking_frame, columns=columns, show="headings")
        for col in columns:
            self.tracking_tree.heading(col, text=col)
        self.tracking_tree.pack()
        
        self.load_tracking_data()
    
    def load_tracking_data(self):
        conn = sqlite3.connect("workflow.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tahapan, scan_mulai, scan_selesai, operator 
            FROM spk_tracking 
            WHERE spk_id=?
            ORDER BY scan_mulai
        """, (self.spk_id,))
        
        for row in cursor.fetchall():
            durasi = "Sedang berjalan"
            if row[2]:  # Jika ada waktu selesai
                start = datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
                end = datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S")
                durasi = f"{(end-start).total_seconds()/60:.1f} menit"
            
            self.tracking_tree.insert("", "end", values=(row[0], row[1], row[2] or "-", durasi, row[3]))
        
        conn.close()
    def add_image_column(self, parent, col, image_source, title):
        try:
            if isinstance(image_source, Image.Image):
                img = image_source
            elif isinstance(image_source, str):
                img = Image.open(image_source)
            elif image_source:
                img = Image.open(io.BytesIO(image_source))
            else:
                return

            img.thumbnail((200, 200))
            photo = ImageTk.PhotoImage(img)
            frame = Frame(parent, bg='white')
            frame.grid(row=0, column=col, padx=15)

            label_img = Label(frame, image=photo, bg='white')
            label_img.image = photo
            label_img.pack()
            Label(frame, text=title, font=('Segoe UI', 10, 'bold'), bg='white').pack()
        except Exception as e:
            print(f"Error loading {title} image: {e}")
