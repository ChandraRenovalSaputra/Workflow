from tkinter import *
from tkinter import messagebox
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
        self.canvas = Canvas(self, bg='white', highlightthickness=0)
        self.scrollbar = Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = Frame(canvas, bg='white')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        
        self.canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
                                                                                
        self.bind_scroll_event()

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
        headers = ["Tahap", "Estimasi", "Mulai", "Selesai", "Status", "Keterangan"]
        for col, header in enumerate(headers):
            Label(workflow_frame, text=header, font=('Arial', 10, 'bold'), 
                 bg='#f0f0f0', relief=RAISED, padx=5, pady=5, width=15).grid(row=0, column=col, sticky='nsew')
        
        # Isi tabel
        if tahapan_data:
            self.keterangan_vars = []  # Untuk menyimpan StringVar keterangan
            
            for row, (tahap, mulai, selesai, keterangan) in enumerate(tahapan_data, start=1):
                # Tentukan status
                status, bg_color = self.tentukan_status(mulai, selesai)
                
                # Kolom 1: Tahap
                Label(workflow_frame, text=tahap, bg='white', 
                     relief=GROOVE, padx=5, pady=5).grid(row=row, column=0, sticky='nsew')
                
                # Kolom 2: Estimasi
                estimasi = f"{mulai[:10]} - {selesai[:10]}" if selesai else "-"
                Label(workflow_frame, text=estimasi, bg='white', 
                     relief=GROOVE, padx=5, pady=5).grid(row=row, column=1, sticky='nsew')
                
                # Kolom 3 & 4: Waktu Mulai & Selesai
                Label(workflow_frame, text=mulai if mulai else "-", bg='white', 
                     relief=GROOVE, padx=5, pady=5).grid(row=row, column=2, sticky='nsew')
                Label(workflow_frame, text=selesai if selesai else "-", bg='white', 
                     relief=GROOVE, padx=5, pady=5).grid(row=row, column=3, sticky='nsew')
                
                # Kolom 5: Status
                Label(workflow_frame, text=status, bg=bg_color, fg='white',
                     relief=GROOVE, padx=5, pady=5).grid(row=row, column=4, sticky='nsew')
                
                # Kolom 6: Keterangan
                keterangan_var = StringVar(value=keterangan if keterangan else "")
                self.keterangan_vars.append((tahap, keterangan_var))
                entry = Entry(workflow_frame, textvariable=keterangan_var, 
                            relief=GROOVE)
                entry.grid(row=row, column=5, sticky='nsew')
                
                # Jika status "TERLAMBAT", set wajib isi keterangan
                if status == "TERLAMBAT" and not keterangan:
                    keterangan_var.set("Harap isi alasan keterlambatan")
                    entry.config(bg="#FFF3CD")  # Warna kuning untuk highlight
        
        # Tombol Simpan Keterangan
        Button(self.scrollable_frame, text="Simpan Keterangan", 
              command=self.simpan_keterangan, bg='#28a745', fg='white',
              font=('Arial', 10, 'bold')).pack(pady=10)
        
        # Tombol Kembali
        Button(self.scrollable_frame, text="Kembali ke Jadwal", 
              font=('Arial', 12, 'bold'), bg='#dc3545', fg='white', 
              command=self.kembali_ke_jadwal).pack(pady=20)
    
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