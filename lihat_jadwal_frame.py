from datetime import datetime
from tkinter import *
from tkinter import Frame, Label, Button, ttk
from db import get_jadwal_pekerjaan, get_workflow_conn, search_jadwal
from detail_spk import show_spk_detail
from datetime import datetime
from scrollable_frame import ScrollableFrame


class LihatJadwalFrame(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#ecf0f1")

        Label(
            self,
            text="📋 JADWAL PEKERJAAN",
            font=("Segoe UI", 26, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50",
        ).pack(pady=30)

        # 🔍 Search Bar
        search_frame = Frame(self, bg="#ecf0f1")
        search_frame.pack(pady=10)

        self.search_var = StringVar()
        Entry(
            search_frame,
            textvariable=self.search_var,
            width=45,
            font=("Segoe UI", 13),
            bd=2,
            relief=GROOVE,
        ).pack(side=LEFT, padx=10, ipady=4)
        Button(
            search_frame,
            text="🔍 Cari",
            font=("Segoe UI", 12, "bold"),
            bg="#27ae60",
            fg="white",
            activebackground="#2ecc71",
            command=self.search,
            padx=15,
        ).pack(side=LEFT)

        # 🧾 Scrollable Tabel
        scrollable = ScrollableFrame(self)
        scrollable.pack(padx=30, pady=10, fill=BOTH, expand=True)

        self.table_frame = scrollable.scrollable_frame

        self.filter_var = StringVar()
        self.filter_var.set("semua")  # Defaultnya semua

        filter_frame = Frame(self, bg="#ecf0f1")
        filter_frame.pack()

        OptionMenu(filter_frame, self.filter_var, "semua", "berjalan", "selesai").pack(
            side=LEFT, padx=10
        )

        Button(
            filter_frame,
            text="📂 Terapkan Filter",
            command=self.filter_data,
            font=("Segoe UI", 12),
            bg="#7f8c8d",
            fg="white",
        ).pack(side=LEFT)

        self.load_table()

        # 🔙 Tombol Kembali
        Button(
            self,
            text="⬅️ Kembali ke Dashboard",
            command=self.kembali_ke_dashboard,
            bg="#ffffff",
            fg="#2c3e50",
            font=("Segoe UI", 12, "bold"),
            activebackground="#bdc3c7",
            padx=20,
            pady=8,
            relief=GROOVE,
            bd=1,
        ).pack(pady=20, anchor=SE, padx=30)

        Button(
            search_frame,
            text="📷 Scan",
            font=("Segoe UI", 12, "bold"),
            bg="#2980b9",
            fg="white",
            activebackground="#3498db",
            command=self.open_scanner,
            padx=15,
        ).pack(side=LEFT, padx=10)
        self.auto_refresh()

    def auto_refresh(self):
        self.refresh_table()
        # Refresh setiap 60 detik (60000 milidetik)
        self.after(60000, self.auto_refresh)


    def load_table(self, keyword=None, filter_status="semua"):
        if keyword is not None and keyword != "":
            rows = search_jadwal(keyword)
        else:
            rows = get_jadwal_pekerjaan()

        print("Data yang diambil: ", rows)

        for row in rows:
            print(f"ID: {row[1]}, Status: {row[3]}")  # Kolom 3 adalah status

        # 🔍 Filter berdasarkan tahap
        if filter_status == "berjalan":
            rows = [r for r in rows if r[3].lower() != "selesai"]
        elif filter_status == "selesai":
            rows = [r for r in rows if r[3].lower() == "selesai"]

        for widget in self.table_frame.winfo_children():
            widget.destroy()

        print(f"Data setelah filter status '{filter_status}': ", rows)

        # 🔁 Ambil hanya tahap terakhir per SPK (berdasarkan waktu mulai terbaru)
        filtered_rows = {}
        for row in rows:
            spk_id = row[1]  # Kolom ke-2 = SPK ID
            if spk_id not in filtered_rows or row[5] > filtered_rows[spk_id][5]:  # Kolom ke-6 = waktu mulai
                filtered_rows[spk_id] = row

        rows = list(filtered_rows.values())


        headers = [
            "📝 Nama Pekerjaan",
            "🆔 ID",
            "📄 PO",
            "🚧 Tahap",
            "▶️ Mulai",
            "⏹️ Selesai",
            "⏰ Deadline",
            "🔍 Aksi",
        ]
        column_widths = [23, 15, 15, 17, 15, 15, 15, 8]

        # 🔶 Header
        for col, (text, width) in enumerate(zip(headers, column_widths)):
            Label(
                self.table_frame,
                text=text,
                font=("Segoe UI", 14, "bold"),
                bd=1,
                relief=RIDGE,
                width=width,
                height=2,
                bg="#dfe6e9",
                fg="#2c3e50",
            ).grid(row=0, column=col, sticky="nsew")

        if not rows:
            Label(
                self.table_frame,
                text="🔎 Tidak ada data ditemukan.",
                font=("Segoe UI", 12),
                bg="white",
                fg="gray",
            ).grid(row=1, column=0, columnspan=len(headers), pady=40)
            return

        # 🔷 Baris data
        for i, row in enumerate(rows, start=1):
            row_to_display = row[:3] + row[4:]  # skip kolom ke-3 (status)
            print(row)
            tag = self.get_row_tag(row[5], row[7], row[6])  # mulai = row[5], deadline = row[7]

            if tag == "belum" or tag == "normal":
                bg_color = "#f7f9fa"  
            elif tag == "terlambat":
                bg_color = "#ff6f61"  
            elif tag == "warning":
                bg_color = "#ffeb3b"  
            elif tag == "sedang":
                bg_color = "#00e676"  
            else:
                bg_color = "#a5d6a7"  


            for j, val in enumerate(row_to_display):
                font_style = ("Segoe UI", 14, "bold") if j == 3 else ("Segoe UI", 14)
                Label(
                    self.table_frame,
                    text=val,
                    bd=1,
                    relief=RIDGE,
                    width=column_widths[j],
                    bg=bg_color,
                    anchor="w",
                    font=font_style,
                    height=2,
                ).grid(row=i, column=j, sticky="nsew")


            Button(
                self.table_frame,
                text="ℹ️ Detail",
                bg="#0984e3",
                fg="white",
                font=("Segoe UI", 12, "bold"),
                cursor="hand2",
                activebackground="#74b9ff",
                command=lambda sid=row[1]: self.lihat_detail(sid),
            ).grid(row=i, column=len(headers) - 1, sticky="nsew", ipadx=10, pady=2)



        # Responsif
        for col in range(len(headers)):
            self.table_frame.grid_columnconfigure(col, weight=1)

    def lihat_detail(self, spk_id):
        print(f"🔍 Pindah ke halaman detail untuk SPK ID: {spk_id}")
        show_spk_detail(self.controller, spk_id)

    def get_row_tag(self, mulai, target, selesai):
        """Tentukan tag warna berdasarkan status deadline"""
        print(f"[DEBUG] Mulai: {mulai}, Target: {target}")  # log


        try:

            # Coba parsing waktu deadline
            target_dt = datetime.strptime(target.strip(), "%d-%m-%Y %H:%M")
            if selesai:
                selesai_dt = datetime.strptime(selesai.strip(), "%d-%m-%Y %H:%M:%S")

                if selesai_dt < target_dt:
                    return "selesai"
            # print(f"selesai_dt: {selesai_dt}")
            now = datetime.now()

            print(f"[DEBUG] Now: {now}, Deadline: {target_dt}")  # log waktu


            if now > target_dt:
                return "terlambat"
            elif (target_dt - now).total_seconds() < 1 * 3600:
                return "warning"
            elif not mulai or mulai.strip() == "-":
                return "belum"
            else:
                return "normal"

        except Exception as e:
            print(f"[ERROR] Gagal parsing waktu: {e}")
            # return "normal"


    def search(self):
        keyword = self.search_var.get()
        self.load_table(keyword)

    def refresh_table(self):
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        self.load_table()
        self.update_idletasks()

    def open_scanner(self):
        from scanner_ui import ScannerApp

        scanner = ScannerApp(self, get_workflow_conn())
        # Set the callback to refresh the table
        scanner.set_scan_complete_callback(self.refresh_table)
        scanner.grab_set()

    def kembali_ke_dashboard(self):
        from ui_dashboard import DashboardFrame

        self.controller.switch_frame(DashboardFrame)


    def filter_data(self):
        keyword = self.search_var.get()
        filter_status = self.filter_var.get()
        self.load_table(keyword, filter_status)