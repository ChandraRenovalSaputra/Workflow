from tkinter import *
from db import get_spk_details  # ✅ Pastikan fungsi ini ada
from PIL import Image, ImageTk
import io

def show_spk_detail(controller, spk_id):
    """ Fungsi ini mengganti halaman ke DetailSPKFrame """
    controller.switch_frame(DetailSPKFrame, spk_id)

class DetailSPKFrame(Frame):
    def __init__(self, parent, controller, spk_id):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg='white')

        Label(self, text=f"Detail SPK - {spk_id}", font=('Arial', 18, 'bold'), bg='blue').pack(pady=10)  

        # 🔹 Ambil data SPK
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
        else:
            detail_text = "❌ Data tidak ditemukan."        

        Label(self, text=detail_text, bg='white', font=('Arial', 12), justify="left").pack(pady=5, padx=20, anchor="w")

        # 🔹 Tampilkan Gambar Desain dan Dummy
        frame_gambar = Frame(self, bg='white')
        frame_gambar.pack(pady=10)

        try:
            # Ambil kolom gambar_desain dan gambar_dummy
            gambar_desain_blob = spk_data[16]
            gambar_dummy_blob = spk_data[17]

            # Tampilkan masing-masing gambar
            if gambar_desain_blob:
                img1 = Image.open(io.BytesIO(gambar_desain_blob))
                img1.thumbnail((200, 200))
                self.photo1 = ImageTk.PhotoImage(img1)
                Label(frame_gambar, text="Gambar Desain", bg='white', font=('Arial', 10, 'bold')).pack()
                Label(frame_gambar, image=self.photo1, bg='white').pack(pady=5)

            if gambar_dummy_blob:
                img2 = Image.open(io.BytesIO(gambar_dummy_blob))
                img2.thumbnail((200, 200))
                self.photo2 = ImageTk.PhotoImage(img2)
                Label(frame_gambar, text="Gambar Dummy", bg='white', font=('Arial', 10, 'bold')).pack()
                Label(frame_gambar, image=self.photo2, bg='white').pack(pady=5)

        except Exception as e:
            Label(frame_gambar, text=f"⚠️ Gagal memuat gambar: {e}", fg='red', bg='white').pack()

        # 🔹 Estimasi Pekerjaan
        Label(self, text="Estimasi Pekerjaan:", font=('Arial', 14, 'bold'), bg='white').pack(pady=10)

        if tahapan_data:
            frame_tahapan = Frame(self, bg='white')
            frame_tahapan.pack(pady=5)

            for tahap, mulai, selesai in tahapan_data:
                Label(frame_tahapan, text=f"{tahap}: {mulai} - {selesai}", bg='white', font=('Arial', 10)).pack(anchor="w", padx=20)
        else:
            Label(self, text="⚠️ Tidak ada data tahapan.", bg='white', font=('Arial', 10)).pack()

        # 🔹 Tombol Kembali
        Button(self, text="Kembali", font=('Arial', 12, 'bold'), bg='red', fg='white',
            command=self.kembali_ke_jadwal).pack(pady=20)

    def kembali_ke_jadwal(self):
        from lihat_jadwal_frame import LihatJadwalFrame
        self.controller.switch_frame(LihatJadwalFrame) 
    
    def show_spk_detail(controller, spk_id):
        """ Fungsi ini mengganti halaman ke DetailSPKFrame """
        print(f"✅ Memanggil switch_frame ke DetailSPKFrame dengan SPK ID: {spk_id}")  # Debugging
        controller.switch_frame(DetailSPKFrame, spk_id)

