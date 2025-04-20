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

def show_spk_detail(controller, spk_id):
    """ Fungsi untuk beralih ke halaman DetailSPKFrame """
    controller.switch_frame(DetailSPKFrame, spk_id)

class DetailSPKFrame(Frame):
    def __init__(self, parent, controller, spk_id):
        super().__init__(parent)
        self.controller = controller
        self.spk_id = spk_id
        self.configure(bg='white')
        
        # Scrollable Frame
        canvas = Canvas(self, bg='white', highlightthickness=0)
        scrollbar = Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = Frame(canvas, bg='white')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Header
        Label(self.scrollable_frame, text=f"Detail SPK - {spk_id}", 
              font=('Arial', 18, 'bold'), bg='blue', fg='white').pack(pady=10, fill=X)

        # Data Utama SPK
        spk_data, tahapan_data = get_spk_details(spk_id)
        if spk_data:
            detail_text = (
                f"ORDER SALES          : {spk_data[1]}\n"
                f"NO PO                         : {spk_data[2]}\n"
                f"COSTUMER               : {spk_data[3]}\n"
                f"NAMA ARTIKEL       : {spk_data[4]}\n"
                f"QTY                             : {spk_data[5]}\n"
                f"TANGGAL KIRIM      : {spk_data[6]}\n"
                f"JENIS BAHAN          : {spk_data[7]}\n"
                f"QTY BAHAN            : {spk_data[8]}\n"
                f"UKURAN CETAK       : {spk_data[9]}\n"
                f"JUMLAH CETAK      : {spk_data[10]}\n"
                f"INSHEET                   : {spk_data[11]}\n"
                f"TOTAL CETAK         : {spk_data[12]}\n"
                f"WARNA                     : {spk_data[13]}\n"
                f"VARNISH                  : {spk_data[14]}\n"
                f"FINISHING                : {spk_data[15]}"
            )
            Label(self.scrollable_frame, text=detail_text, bg='white', 
                 font=('Arial', 12), justify="left").pack(pady=5, padx=20, anchor="w")
        else:
            Label(self.scrollable_frame, text="❌ Data tidak ditemukan.", bg='white').pack()

        # ===== Gambar Desain, Barcode, dan Dummy =====
        img_frame = Frame(self.scrollable_frame, bg='white')
        img_frame.pack(pady=10)

        # Gambar Desain
        if spk_data and spk_data[16]:  # gambar_desain
            try:
                img_desain = Image.open(spk_data[16]) if isinstance(spk_data[16], str) else Image.open(io.BytesIO(spk_data[16]))
                img_desain.thumbnail((200, 200))
                self.photo_desain = ImageTk.PhotoImage(img_desain)
                desain_frame = Frame(img_frame, bg='white')
                desain_frame.grid(row=0, column=0, padx=10)
                Label(desain_frame, image=self.photo_desain, bg='white').pack()
                Label(desain_frame, text="Desain", bg='white', font=('Arial', 10, 'bold')).pack()
            except Exception as e:
                print(f"Error loading design image: {e}")
                Label(img_frame, text="Gambar desain tidak tersedia", bg='white').grid(row=0, column=0)

        # Barcode
        try:
            if spk_data and len(spk_data) > 18 and spk_data[19]:  # barcode_image
                # Jika barcode sudah ada di database
                barcode_img = Image.open(io.BytesIO(spk_data[19]))
                barcode_img.thumbnail((200, 200))
                self.photo_barcode = ImageTk.PhotoImage(barcode_img)
                barcode_text = "Barcode SPK"
            else:
                # Generate baru jika tidak ada di database
                barcode_img = self.generate_barcode_image()
                self.photo_barcode = ImageTk.PhotoImage(barcode_img)
                barcode_text = "Barcode SPK (Generated)"
            
            barcode_frame = Frame(img_frame, bg='white')
            barcode_frame.grid(row=0, column=1, padx=10)
            Label(barcode_frame, image=self.photo_barcode, bg='white').pack()
            Label(barcode_frame, text=barcode_text, bg='white', font=('Arial', 10, 'bold')).pack()
        except Exception as e:
            print(f"Error loading/generating barcode: {e}")
            Label(img_frame, text="Gagal memuat barcode", bg='white').grid(row=0, column=1)

        # Gambar Dummy
        if spk_data and spk_data[17]:  # gambar_dummy
            try:
                img_dummy = Image.open(spk_data[17]) if isinstance(spk_data[17], str) else Image.open(io.BytesIO(spk_data[17]))
                img_dummy.thumbnail((200, 200))
                self.photo_dummy = ImageTk.PhotoImage(img_dummy)
                dummy_frame = Frame(img_frame, bg='white')
                dummy_frame.grid(row=0, column=2, padx=10)
                Label(dummy_frame, image=self.photo_dummy, bg='white').pack()
                Label(dummy_frame, text="Dummy", bg='white', font=('Arial', 10, 'bold')).pack()
            except Exception as e:
                print(f"Error loading dummy image: {e}")
                Label(img_frame, text="Gambar dummy tidak tersedia", bg='white').grid(row=0, column=2)

        # ===== WORKFLOW/Tahapan Produksi =====
        Label(self.scrollable_frame, text="WORKFLOW PRODUKSI", 
            font=('Arial', 14, 'bold'), bg='white').pack(pady=10)

        # Frame untuk tabel workflow
        workflow_frame = Frame(self.scrollable_frame, bg='white')
        workflow_frame.pack(pady=10, padx=20, fill=BOTH)

        # Header tabel
        headers = ["Tahap", "Mulai", "Selesai", "Status", "Keterangan"]
        for col, header in enumerate(headers):
            Label(workflow_frame, text=header, font=('Arial', 10, 'bold'), 
                bg='#f0f0f0', relief=RAISED, padx=5, pady=5, width=15).grid(row=0, column=col, sticky='nsew')

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

        # Isi tabel
        if tahapan_data:
            self.keterangan_vars = []  # Untuk menyimpan StringVar keterangan
            
            for row, (tahap, estimasi_mulai, estimasi_selesai, keterangan) in enumerate(tahapan_data, start=1):
                # Get actual scan times
                mulai_scan, selesai_scan = scan_data.get(tahap, (None, None))
                
                # Determine status
                if selesai_scan:
                    status = "SELESAI"
                    bg_color = "#28a745"  # Green
                elif mulai_scan:
                    status = "SEDANG DIKERJAKAN"
                    bg_color = "#007bff"  # Blue
                else:
                    status = "BELUM"
                    bg_color = "#6c757d"  # Gray
                
                # Kolom 1: Tahap
                Label(workflow_frame, text=tahap, bg='white', 
                    relief=GROOVE, padx=5, pady=5).grid(row=row, column=0, sticky='nsew')
                
                # Kolom 2: Mulai (from scan data)
                Label(workflow_frame, text=mulai_scan.split(' ')[0] if mulai_scan else "-", 
                    bg='white', relief=GROOVE, padx=5, pady=5).grid(row=row, column=1, sticky='nsew')
                
                # Kolom 3: Selesai (from scan data)
                Label(workflow_frame, text=selesai_scan.split(' ')[0] if selesai_scan else "-", 
                    bg='white', relief=GROOVE, padx=5, pady=5).grid(row=row, column=2, sticky='nsew')
                
                # Kolom 4: Status
                Label(workflow_frame, text=status, bg=bg_color, fg='white',
                    relief=GROOVE, padx=5, pady=5).grid(row=row, column=3, sticky='nsew')
                
                # Kolom 5: Keterangan
                keterangan_var = StringVar(value=keterangan if keterangan else "")
                self.keterangan_vars.append((tahap, keterangan_var))
                entry = Entry(workflow_frame, textvariable=keterangan_var, 
                            relief=GROOVE)
                entry.grid(row=row, column=4, sticky='nsew')
        
        # Tombol Simpan Keterangan
        Button(self.scrollable_frame, text="Simpan Keterangan", 
              command=self.simpan_keterangan, bg='#28a745', fg='white',
              font=('Arial', 10, 'bold')).pack(pady=10)
        
        # Tombol Kembali
        Button(self.scrollable_frame, text="Kembali ke Jadwal", 
              font=('Arial', 12, 'bold'), bg='#dc3545', fg='white', 
              command=self.kembali_ke_jadwal).pack(pady=20)

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