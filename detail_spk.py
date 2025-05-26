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
from scrollable_frame import ScrollableFrame

def center_window(root, width=1600, height=800):
    """Menempatkan window di tengah layar"""
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")  # Tentukan ukuran dan posisi
    root.minsize(width, height)  # Ukuran minimal untuk window


def show_spk_detail(controller, spk_id):
    """Fungsi untuk beralih ke halaman DetailSPKFrame"""
    controller.switch_frame(DetailSPKFrame, spk_id)


class DetailSPKFrame(Frame):
    def __init__(self, parent, controller, spk_id):
        super().__init__(parent)
        self.controller = controller
        self.spk_id = spk_id
        self.configure(bg="#f0f2f5")

        # === HEADER ===
        header = Frame(self, bg="#0078D7", height=60)
        header.pack(side="top", fill="x")

        title = Label(
            header,
            text=f"🧾 Detail SPK - {spk_id}",
            font=("Segoe UI", 18, "bold"),
            bg="#0078D7",
            fg="white",
        )
        title.pack(side="left", padx=20, pady=10)

        # === SCROLLABLE FRAME ===
        scrollable_frame_widget = ScrollableFrame(self)
        scrollable_frame_widget.pack(fill="both", expand=True)

        self.scrollable_frame = scrollable_frame_widget.get_scrollable_frame()

        # === DATA SPK ===
        spk_data, tahapan_data = get_spk_details(spk_id)
        if spk_data:
            # Bungkus agar bisa center
            wrapper = Frame(self.scrollable_frame, bg="#f0f2f5")
            wrapper.pack(pady=20)

            detail_card = Frame(wrapper, bg="white", bd=2, relief="groove")
            detail_card.pack(padx=550)

            Label(
                detail_card,
                text="🗝️ INFORMASI SPK",
                font=("Segoe UI", 18, "bold"),
                bg="white",
                fg="#222",
            ).grid(row=0, column=0, columnspan=3, sticky="w", padx=20, pady=(20, 10))

            labels = [
                ("ORDER SALES", spk_data[1]),
                ("NO PO", spk_data[2]),
                ("CUSTOMER", spk_data[3]),
                ("NAMA ARTIKEL", spk_data[4]),
                ("QTY", spk_data[5]),
                ("TANGGAL KIRIM", spk_data[6]),
                ("JENIS BAHAN", spk_data[7]),
                ("QTY BAHAN", spk_data[8]),
                ("UKURAN CETAK", spk_data[9]),
                ("JUMLAH CETAK", spk_data[10]),
                ("INSHEET", spk_data[11]),
                ("TOTAL CETAK", spk_data[12]),
                ("WARNA", spk_data[13]),
                ("VARNISH", spk_data[14]),
                ("FINISHING", spk_data[15]),
            ]

            for i, (label_text, value) in enumerate(labels, start=1):
                Label(
                    detail_card,
                    text=label_text,
                    font=("Segoe UI", 12, "bold"),
                    bg="white",
                ).grid(row=i, column=0, sticky="w", padx=(20, 5), pady=6)
                Label(detail_card, text=":", font=("Segoe UI", 12), bg="white").grid(
                    row=i, column=1, sticky="w", padx=5, pady=6
                )
                Label(detail_card, text=value, font=("Segoe UI", 12), bg="white").grid(
                    row=i, column=2, sticky="w", padx=(5, 20), pady=6
                )

            detail_card.grid_columnconfigure(0, minsize=150)
            detail_card.grid_columnconfigure(2, minsize=550)
        else:
            Label(
                self.scrollable_frame, text="❌ Data tidak ditemukan.", bg="#f0f2f5"
            ).pack()

        # === GAMBAR FRAME ===
        if spk_data:
            # Main image container
            img_container = Frame(self.scrollable_frame, bg="#f0f2f5")
            img_container.pack(padx=30, pady=10, fill="x")

            # First row frame (desain, dummy, potong)
            row1_frame = Frame(img_container, bg="#f0f2f5")
            row1_frame.pack()

            # Second row frame (empty, barcode, empty)
            row2_frame = Frame(img_container, bg="#f0f2f5")
            row2_frame.pack()

            # Row 1: Desain, Dummy, Potong
            self.add_image_column(row1_frame, 0, spk_data[16], "Desain")
            self.add_image_column(row1_frame, 1, spk_data[17], "Dummy")
            self.add_image_column(row1_frame, 2, spk_data[18], "Potong Bahan")

            # Row 2: Empty, Barcode, Empty
            barcode_img = (
                self.generate_barcode_image()
                if not (len(spk_data) > 19 and spk_data[19])
                else Image.open(io.BytesIO(spk_data[19]))
            )
            
            # Add empty placeholder in column 0
            empty_frame1 = Frame(row2_frame, width=200, height=200, bg="#f0f2f5")
            empty_frame1.grid(row=0, column=0, padx=15)
            
            # Add barcode in column 1
            if barcode_img:
                barcode_img.thumbnail((200, 200))
                barcode_photo = ImageTk.PhotoImage(barcode_img)
                barcode_frame = Frame(row2_frame, bg="white")
                barcode_frame.grid(row=0, column=1, padx=15)
                
                label_barcode = Label(barcode_frame, image=barcode_photo, bg="white")
                label_barcode.image = barcode_photo
                label_barcode.pack()
                Label(barcode_frame, text="Barcode", font=("Segoe UI", 10, "bold"), bg="white").pack()
            
            # Add empty placeholder in column 2
            empty_frame2 = Frame(row2_frame, width=200, height=200, bg="#f0f2f5")
            empty_frame2.grid(row=0, column=2, padx=15)


        # === WORKFLOW PRODUKSI ===
        Label(
            self.scrollable_frame,
            text="📋 WORKFLOW PRODUKSI",
            font=("Segoe UI", 18, "bold"),
            bg="#f0f2f5",
            fg="#2c3e50",
        ).pack(pady=(20, 10))

        workflow_frame = Frame(self.scrollable_frame, bg="white", bd=1, relief="solid")
        workflow_frame.pack(padx=30, fill="both")

        headers = [
            "Tahap",
            "Estimasi",
            "Scan Mulai",
            "Scan Selesai",
            "Status",
            "Keterangan",
        ]
        for col, header in enumerate(headers):
            Label(
                workflow_frame,
                text=header,
                font=("Segoe UI", 12, "bold"),
                bg="#0056b3",
                fg="white",
                padx=25,
                pady=12,
            ).grid(row=0, column=col, sticky="nsew")

        for i in range(len(headers)):
            workflow_frame.grid_columnconfigure(i, weight=1)

        # ISI
        if tahapan_data:
            print(tahapan_data)
            self.keterangan_vars = []

            for row, (
                tahap,
                estimasi_mulai,
                estimasi_selesai,
                keterangan,
                scan_mulai,
                scan_selesai,
            ) in enumerate(tahapan_data, start=1):

                status, bg_color = self.tentukan_status(
                    scan_mulai,
                    scan_selesai,
                    estimasi_selesai
                )

                estimasi = (
                    f"{estimasi_mulai} - {estimasi_selesai}"
                    if estimasi_selesai
                    else "-"
                )

                # Format scan times to show only date if they exist
                display_mulai = scan_mulai if scan_mulai else "-"
                display_selesai = scan_selesai if scan_selesai else "-"

                base_font = ("Segoe UI", 12)
                status_font = ("Segoe UI", 12, "bold")

                Label(workflow_frame, text=tahap, bg="white", font=base_font).grid(
                    row=row, column=0, sticky="nsew", padx=5, pady=6
                )
                Label(workflow_frame, text=estimasi, bg="white", font=base_font).grid(
                    row=row, column=1, sticky="nsew", padx=5, pady=6
                )
                Label(
                    workflow_frame, text=display_mulai, bg="white", font=base_font
                ).grid(row=row, column=2, sticky="nsew", padx=5, pady=6)
                Label(
                    workflow_frame, text=display_selesai, bg="white", font=base_font
                ).grid(row=row, column=3, sticky="nsew", padx=5, pady=6)

                Label(
                    workflow_frame,
                    text=status,
                    bg=bg_color,
                    fg="white",
                    font=status_font,
                    relief="ridge",
                    bd=2,
                ).grid(row=row, column=4, sticky="nsew", padx=5, pady=6)

                # Keterangan Entry
                entry_bg = "#ffffff"
                text_value = keterangan if keterangan else ""
                if status == "TERLAMBAT" and not keterangan:
                    text_value = "Harap isi alasan keterlambatan"
                    entry_bg = "#ffeeba"

                text_widget = Text(
                    workflow_frame,
                    height=3,
                    font=base_font,
                    bg=entry_bg,
                    relief="solid",
                    bd=1,
                    width=60,
                    wrap="word",
                )
                text_widget.insert("1.0", text_value)
                text_widget.grid(row=row, column=5, sticky="nsew", padx=5, pady=6)

                # Simpan tahap dan widget-nya
                self.keterangan_vars.append((tahap, text_widget))


        # === BUTTONS ===
        button_frame = Frame(self.scrollable_frame, bg="#f0f2f5")
        button_frame.pack(pady=30)

        ttk.Style().configure(
            "Green.TButton", font=("Segoe UI", 12, "bold"), padding=10
        )
        ttk.Button(
            button_frame,
            text="💾 Simpan Keterangan",
            command=self.simpan_keterangan,
            style="Green.TButton",
        ).pack(side="left", padx=10)
        ttk.Button(
            button_frame,
            text="⏪ Kembali ke Jadwal",
            command=self.kembali_ke_jadwal,
            style="Green.TButton",
        ).pack(side="left", padx=10)

    @staticmethod
    def parse_datetime(dt_str):
        """Static method untuk parsing tanggal dari berbagai format"""
        if not dt_str or str(dt_str).strip() in ("", "-"):
            return None

        dt_str = str(dt_str).strip()

        # Daftar format yang didukung (termasuk format Indonesia dan ISO)
        formats = [
            "%d-%m-%Y %H:%M",  # 21-04-2025 17:00
            "%d-%m-%Y %H:%M:%S",  # 21-04-2025 15:59:48
        ]

        for fmt in formats:
            try:
                return datetime.strptime(dt_str, fmt)
            except ValueError:
                continue
        print(f"Format waktu tidak dikenali: {dt_str}")
        return None

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

    def simpan_keterangan(self):
        """Validasi dan simpan keterangan ke database"""
        # Validasi untuk tahap yang terlambat
        for tahap, widget in self.keterangan_vars:
            value = widget.get("1.0", "end").strip()
            if "TERLAMBAT" in widget.get("1.0", "end") and not value:
                messagebox.showerror(
                    "Error",
                    f"Keterangan wajib diisi untuk tahap {tahap} yang terlambat!",
                )
                return

        # Simpan ke database
        try:
            conn = sqlite3.connect("workflow.db")
            cursor = conn.cursor()

            for tahap, widget in self.keterangan_vars:
                value = widget.get("1.0", "end").strip()
                if value:  # Hanya simpan jika ada isinya
                    cursor.execute(
                        """
                        UPDATE spk_tahapan 
                        SET keterangan = ?
                        WHERE spk_id = ? AND nama_tahapan = ?
                        """,
                        (value, self.spk_id, tahap),
                    )

            conn.commit()
            conn.close()
            messagebox.showinfo("Sukses", "Keterangan berhasil disimpan!")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan ke database: {str(e)}")


    def kembali_ke_jadwal(self):
        from lihat_jadwal_frame import LihatJadwalFrame

        self.controller.switch_frame(LihatJadwalFrame)

    def add_tracking_section(self):
        tracking_frame = Frame(self)
        tracking_frame.pack(pady=10)

        Label(tracking_frame, text="Riwayat Tracking", font=("Arial", 14)).pack()

        # Tabel riwayat scan
        columns = ("Tahap", "Mulai", "Selesai", "Durasi", "Operator")
        self.tracking_tree = ttk.Treeview(
            tracking_frame, columns=columns, show="headings"
        )
        for col in columns:
            self.tracking_tree.heading(col, text=col)
        self.tracking_tree.pack()

        self.load_tracking_data()

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
            frame = Frame(parent, bg="white")
            frame.grid(row=0, column=col, padx=15)

            label_img = Label(frame, image=photo, bg="white")
            label_img.image = photo
            label_img.pack()
            Label(frame, text=title, font=("Segoe UI", 10, "bold"), bg="white").pack()
        except Exception as e:
            print(f"Error loading {title} image: {e}")

    def tentukan_status(self, scan_mulai, scan_selesai, estimasi_selesai):
        """Menentukan status tahapan dengan format tanggal fleksibel"""
        try:

            scan_mulai = DetailSPKFrame.parse_datetime(scan_mulai) if scan_mulai else None
            scan_selesai = DetailSPKFrame.parse_datetime(scan_selesai) if scan_selesai else None
            estimasi_selesai = DetailSPKFrame.parse_datetime(estimasi_selesai)

            if scan_selesai and scan_selesai <= estimasi_selesai:
                return "SELESAI", "#28a745"
            elif scan_selesai and scan_selesai > estimasi_selesai:
                return "TERLAMBAT", "#dc3545"
            elif scan_mulai:
                return "SEDANG BERJALAN", "#007bff"
            else:
                return "BELUM MULAI", "#6c757d"
        except Exception as e:
            # print(f"Error menentukan status: {e}\nMulai: {mulai}\nSelesai: {selesai}")
            print(f"Error menentukan status: {e}")
            return "UNKNOWN", "#6c757d"

    def load_tracking_data(self):
        conn = sqlite3.connect("workflow.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT tahapan, scan_mulai, scan_selesai, operator 
            FROM spk_tracking 
            WHERE spk_id=?
            ORDER BY scan_mulai
        """,
            (self.spk_id,),
        )

        for row in cursor.fetchall():
            durasi = "Sedang berjalan"
            try:
                if row[2]:  # Jika ada waktu selesai
                    start = DetailSPKFrame.parse_datetime(row[1])
                    end = DetailSPKFrame.parse_datetime(row[2])
                    if start and end:
                        durasi = f"{(end-start).total_seconds()/60:.1f} menit"
                    else:
                        durasi = "Data tidak valid"
            except Exception as e:
                durasi = "Format Error"
                print(f"Error parsing waktu: {e}")

            self.tracking_tree.insert(
                "",
                "end",
                values=(row[0], row[1] or "-", row[2] or "-", durasi, row[3] or "-"),
            )

        conn.close()