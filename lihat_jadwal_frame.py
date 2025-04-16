from tkinter import *
from tkinter import Frame, Label, Button
from db import get_jadwal_pekerjaan, search_jadwal
from detail_spk import DetailSPKFrame  # Impor DetailSPKFrame
from detail_spk import show_spk_detail
from detail_spk import DetailSPKFrame  # ✅ Impor DetailSPKFrame

class LihatJadwalFrame(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg='lightgray')

        Label(self, text="JADWAL", font=('Arial', 18, 'bold'), bg='lightgray').pack(pady=10)
        
        # 🔍 Input untuk Pencarian
        search_frame = Frame(self, bg='lightgray')
        search_frame.pack(pady=5)
        
        self.search_var = StringVar()
        Entry(search_frame, textvariable=self.search_var, width=30).pack(side=LEFT, padx=5)
        Button(search_frame, text="Cari", command=self.search).pack(side=LEFT)
        
        self.table_frame = Frame(self, bg='white', bd=2, relief=RIDGE)
        self.table_frame.pack(padx=20, pady=10, fill=X)

        self.load_table()

        Button(self, text="DASHBOARD", command=self.kembali_ke_dashboard, bg="white").pack(pady=10, anchor=SE, padx=20)

    def load_table(self, keyword=None):
        rows = search_jadwal(keyword) if keyword else get_jadwal_pekerjaan()

        # 🧹 Hapus semua widget lama sebelum load baru
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        headers = ["Nama Pekerjaan", "ID", "PO", "Tahap", "Mulai", "Selesai", "Deadline"]
        for col, text in enumerate(headers):
            Label(self.table_frame, text=text, font=('Arial', 10, 'bold'), bd=1, relief=RIDGE, width=15).grid(row=0, column=col)

        for i, row in enumerate(rows, start=1):
            for j, val in enumerate(row):
                Label(self.table_frame, text=val, bd=1, relief=RIDGE, width=15).grid(row=i, column=j)

            Button(self.table_frame, text="Detail", bg="red", fg="white", 
                command=lambda sid=row[1]: self.lihat_detail(sid)).grid(row=i, column=len(row))

    def lihat_detail(self, spk_id):
        """ Cek apakah fungsi ini berjalan """
        print(f"🔍 Pindah ke halaman detail untuk SPK ID: {spk_id}")  # Debugging
        
        from detail_spk import show_spk_detail  # Impor di dalam fungsi untuk mencegah error import
        show_spk_detail(self.controller, spk_id)

    def search(self):
        keyword = self.search_var.get()
        self.load_table(keyword)

    def kembali_ke_dashboard(self):
        from ui_dashboard import DashboardFrame  # Impor di dalam fungsi
        self.controller.switch_frame(DashboardFrame)
 

