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
        self.configure(bg='#ecf0f1')

        Label(self, text="📋 JADWAL PEKERJAAN", font=('Segoe UI', 26, 'bold'),
              bg='#ecf0f1', fg='#2c3e50').pack(pady=30)

        # 🔍 Search Bar
        search_frame = Frame(self, bg='#ecf0f1')
        search_frame.pack(pady=10)

        self.search_var = StringVar()
        Entry(search_frame, textvariable=self.search_var, width=45,
              font=('Segoe UI', 13), bd=2, relief=GROOVE).pack(side=LEFT, padx=10, ipady=4)
        Button(search_frame, text="🔍 Cari", font=('Segoe UI', 12, 'bold'),
               bg='#27ae60', fg='white', activebackground='#2ecc71',
               command=self.search, padx=15).pack(side=LEFT)

        # 🧾 Scrollable Tabel
        outer_frame = Frame(self, bg='white', bd=1, relief=GROOVE)
        outer_frame.pack(padx=30, pady=10, fill=BOTH, expand=True)

        canvas = Canvas(outer_frame, bg='white', highlightthickness=0)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)

        scrollbar = Scrollbar(outer_frame, orient=VERTICAL, command=canvas.yview)
        scrollbar.pack(side=RIGHT, fill=Y)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        self.table_frame = Frame(canvas, bg='white')
        canvas.create_window((0, 0), window=self.table_frame, anchor='nw')

        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))  # Windows & MacOS
        canvas.bind_all("<Button-4>", lambda event: canvas.yview_scroll(-1, "units"))  # Linux scroll up
        canvas.bind_all("<Button-5>", lambda event: canvas.yview_scroll(1, "units"))   # Linux scroll down


        self.load_table()

        # 🔙 Tombol Kembali
        Button(self, text="⬅️ Kembali ke Dashboard", command=self.kembali_ke_dashboard,
               bg="#ffffff", fg='#2c3e50', font=('Segoe UI', 12, 'bold'),
               activebackground='#bdc3c7', padx=20, pady=8, relief=GROOVE, bd=1).pack(pady=20, anchor=SE, padx=30)

    def load_table(self, keyword=None):
        rows = search_jadwal(keyword) if keyword else get_jadwal_pekerjaan()

        for widget in self.table_frame.winfo_children():
            widget.destroy()

        headers = ["📝 Nama Pekerjaan", "🆔 ID", "📄 PO", "🚧 Tahap", "▶️ Mulai", "⏹️ Selesai", "⏰ Deadline", "🔍 Aksi"]
        column_widths = [25, 18, 18, 19, 18, 18, 18, 14]  # ❗️Diperbesar

        # 🔶 Header
        for col, (text, width) in enumerate(zip(headers, column_widths)):
            Label(self.table_frame, text=text, font=('Segoe UI', 14, 'bold'), bd=1, relief=RIDGE,
                  width=width, height=2, bg='#dfe6e9', fg='#2c3e50').grid(row=0, column=col, sticky='nsew')

        if not rows:
            Label(self.table_frame, text="🔎 Tidak ada data ditemukan.", font=('Segoe UI', 14),
                  bg='white', fg='gray').grid(row=1, column=0, columnspan=len(headers), pady=40)
            return

        # 🔷 Baris data
        for i, row in enumerate(rows, start=1):
            bg_color = '#f8f9fa' if i % 2 == 0 else 'white'
            for j, val in enumerate(row):
                font_style = ('Segoe UI', 14)
                if j == 3:  # Kolom Tahap
                    Label(self.table_frame, text=val, bd=1, relief=RIDGE, width=column_widths[j],
                          bg='#ffeaa7', fg='black', font=('Segoe UI', 14, 'bold'), height=2).grid(row=i, column=j, sticky='nsew')
                else:
                    Label(self.table_frame, text=val, bd=1, relief=RIDGE, width=column_widths[j],
                          bg=bg_color, anchor='w', font=font_style, height=2).grid(row=i, column=j, sticky='nsew')

            # 🔘 Tombol Detail
            Button(self.table_frame, text="ℹ️ Detail", bg="#0984e3", fg="white",
                   font=('Segoe UI', 12, 'bold'), cursor='hand2',
                   activebackground='#74b9ff',
                   command=lambda sid=row[1]: self.lihat_detail(sid)).grid(
                       row=i, column=len(headers)-1, sticky='nsew', ipadx=10, pady=2)

        # Responsif
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