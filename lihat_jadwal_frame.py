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
        self.configure(bg='#f4f6f8')

        Label(self, text="📋 JADWAL PEKERJAAN", font=('Helvetica', 24, 'bold'), bg='#f4f6f8', fg='#2c3e50').pack(pady=20)

        # Search Bar
        search_frame = Frame(self, bg='#f4f6f8')
        search_frame.pack(pady=10)

        self.search_var = StringVar()
        Entry(search_frame, textvariable=self.search_var, width=45, font=('Arial', 14)).pack(side=LEFT, padx=10)
        Button(search_frame, text="🔍 Cari", font=('Arial', 12, 'bold'), bg='#2ecc71', fg='white', command=self.search).pack(side=LEFT)

        # Frame untuk Tabel dengan Scrollbar
        outer_frame = Frame(self, bg='white', bd=2, relief=GROOVE)
        outer_frame.pack(padx=20, pady=10, fill=BOTH, expand=True)

        canvas = Canvas(outer_frame, bg='white')
        canvas.pack(side=LEFT, fill=BOTH, expand=True)

        scrollbar = Scrollbar(outer_frame, orient=VERTICAL, command=canvas.yview)
        scrollbar.pack(side=RIGHT, fill=Y)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        self.table_frame = Frame(canvas, bg='white')
        canvas.create_window((0, 0), window=self.table_frame, anchor='nw')

        self.load_table()

        Button(self, text="⬅️ Kembali ke Dashboard", command=self.kembali_ke_dashboard,
               bg="#ffffff", fg='#34495e', font=('Arial', 12, 'bold')).pack(pady=15, anchor=SE, padx=20)

    def load_table(self, keyword=None):
        rows = search_jadwal(keyword) if keyword else get_jadwal_pekerjaan()

        for widget in self.table_frame.winfo_children():
            widget.destroy()

        headers = ["Nama Pekerjaan", "ID", "PO", "Tahap", "Mulai", "Selesai", "Deadline", "Aksi"]
        column_widths = [25, 10, 15, 15, 18, 18, 18, 12]

        for col, (text, width) in enumerate(zip(headers, column_widths)):
            Label(self.table_frame, text=text, font=('Arial', 14, 'bold'), bd=1, relief=RIDGE,
                  width=width, bg='#dfe6e9', fg='#2c3e50', pady=10).grid(row=0, column=col, sticky='nsew')

        for i, row in enumerate(rows, start=1):
            bg_color = '#f8f9fa' if i % 2 == 0 else 'white'
            for j, val in enumerate(row):
                if j == 3:  # Highlight kolom "Tahap"
                    Label(self.table_frame, text=val, bd=1, relief=RIDGE, width=column_widths[j],
                          bg='#ffeaa7', fg='black', font=('Arial', 13, 'bold')).grid(row=i, column=j, sticky='nsew')
                else:
                    Label(self.table_frame, text=val, bd=1, relief=RIDGE, width=column_widths[j],
                          bg=bg_color, anchor='w', font=('Arial', 13)).grid(row=i, column=j, sticky='nsew')

            Button(self.table_frame, text="Detail", bg="#0984e3", fg="white",
                   font=('Arial', 12, 'bold'),
                   command=lambda sid=row[1]: self.lihat_detail(sid)).grid(row=i, column=len(headers)-1, sticky='nsew', ipadx=5)

        for col in range(len(headers)):
            self.table_frame.grid_columnconfigure(col, weight=1)

    def lihat_detail(self, spk_id):
        print(f"🔍 Pindah ke halaman detail untuk SPK ID: {spk_id}")
        show_spk_detail(self.controller, spk_id)

    def search(self):
        keyword = self.search_var.get()
        self.load_table(keyword)

    def kembali_ke_dashboard(self):
        from ui_dashboard import DashboardFrame
        self.controller.switch_frame(DashboardFrame)