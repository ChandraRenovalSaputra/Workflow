from datetime import datetime
from tkinter import *
from tkinter import Frame, Label, Button
from db import get_jadwal_pekerjaan, get_workflow_conn, search_jadwal, get_spk_details
from detail_spk import show_spk_detail
from scrollable_frame import ScrollableFrame
from backup_db import BackupManager


class LihatJadwalFrame(Frame):
    def __init__(self, parent, controller, readonly=False):
        super().__init__(parent)
        self.controller = controller
        self.backup_manager = BackupManager(
            [("workflow.db", "workflow_backup"), ("users.db", "users_backup")]
        )
        self.readonly = readonly
        self.configure(bg="#ecf0f1")

        # Judul Frame (tetap di atas)
        Label(
            self,
            text="📋 JADWAL PEKERJAAN",
            font=("Segoe UI", 26, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50",
        ).pack(pady=30)

        # 🔍 Search Bar Frame (atas)
        if not self.readonly:
            self.search_frame = Frame(self, bg="#ecf0f1")
            self.search_frame.pack(pady=10)
            
            # Frame container untuk tombol-tombol (agar bisa di-center)
            self.button_container = Frame(self.search_frame, bg="#ecf0f1")
            self.button_container.pack(expand=True)  # Ini yang membuatnya di tengah

            self.search_var = StringVar()
            Entry(
                self.button_container,
                textvariable=self.search_var,
                width=45,
                font=("Segoe UI", 13),
                bd=2,
                relief=GROOVE,
            ).pack(side=LEFT, padx=5, ipady=4)

            Button(
                self.button_container,
                text="🔍 Cari",
                font=("Segoe UI", 12, "bold"),
                bg="#27ae60",
                fg="white",
                activebackground="#2ecc71",
                command=self.search,
                padx=15,
            ).pack(side=LEFT, padx=5)

            Button(
                self.button_container,
                text="📥 Backup",
                font=("Segoe UI", 12, "bold"),
                bg="#2980b9",
                fg="white",
                activebackground="#3498db",
                command=self.backup_manager.manual_backup,
                padx=15,
            ).pack(side=LEFT, padx=5)

            Button(
                self.button_container,
                text="📷 Scan",
                font=("Segoe UI", 12, "bold"),
                bg="#2980b9",
                fg="white",
                activebackground="#3498db",
                command=self.open_scanner,
                padx=15,
            ).pack(side=LEFT, padx=5)

        # Scrollable Frame untuk Tabel (tengah)
        self.scrollable = ScrollableFrame(self)
        self.scrollable.pack(padx=30, pady=10, fill="both", expand=True)
        self.table_frame = self.scrollable.scrollable_frame

        # Filter Frame (bawah)
        if not self.readonly:
            self.filter_frame = Frame(self, bg="#ecf0f1")
            self.filter_frame.pack(pady=10)

            self.filter_var = StringVar()
            self.filter_var.set("semua")
            OptionMenu(
                self.filter_frame, 
                self.filter_var, 
                "semua", 
                "berjalan", 
                "selesai"
            ).pack(side=LEFT, padx=10)

            Button(
                self.filter_frame,
                text="📂 Terapkan Filter",
                command=self.filter_data,
                font=("Segoe UI", 12),
                bg="#7f8c8d",
                fg="white",
            ).pack(side=LEFT)

            # Tombol Kembali (bawah)
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

        self.load_table()

    def load_table(self, keyword=None, filter_status="semua"):
        print(f"[DEBUG] Mode readonly: {self.readonly}")
    
        # Dapatkan data dari database
        if keyword and keyword.strip():
            rows = search_jadwal(keyword)
        else:
            rows = get_jadwal_pekerjaan()
        
        print(f"Data dari DB: {rows}")  # Debugging
        
        if not rows:
            # Tampilkan pesan tidak ada data
            for widget in self.table_frame.winfo_children():
                widget.destroy()
            Label(
                self.table_frame,
                text="🔎 Tidak ada data ditemukan.",
                font=("Segoe UI", 12),
                bg="white",
                fg="gray",
            ).grid(row=0, column=0, columnspan=len(self.headers), pady=40)
            return
        
        # Filter berdasarkan status
        if filter_status == "berjalan":
            rows = [r for r in rows if r[3].lower() != "selesai"]
        elif filter_status == "selesai":
            rows = [r for r in rows if r[3].lower() == "selesai"]
    
        rows_with_estimasi = []
        for row in rows:
            spk_id = row[1]
            detail = get_spk_details(spk_id)
            spk_data, tahapan_data = detail

            if tahapan_data and len(tahapan_data) > 0:
                estimasi_mulai = tahapan_data[0][1] or "-"
            else:
                estimasi_mulai = "-"

            # sisipkan estimasi_mulai di index 3, geser sisa ke kanan
            new_row = row[:3] + (estimasi_mulai,) + row[3:]
            rows_with_estimasi.append(new_row)

        rows = rows_with_estimasi


        for widget in self.table_frame.winfo_children():
            widget.destroy()

        print(f"Data setelah filter status '{filter_status}': ", rows)

        # 🔁 Ambil hanya tahap terakhir per SPK
        filtered_rows = {}
        for row in rows:
            spk_id = row[1]
            if spk_id not in filtered_rows or row[5] > filtered_rows[spk_id][5]:
                filtered_rows[spk_id] = row

        rows = list(filtered_rows.values())

        if self.readonly:
            self.headers = [
                "📝 Nama Pekerjaan",
                "🆔 ID",
                "📄 PO",
                "📅 Estimasi Mulai",
                "🚧 Tahap",
                "▶️ Mulai",
                "⏹️ Selesai",
                "⏰ Deadline",
            ]
            column_widths = [22, 7, 7, 15, 15, 15, 15, 15]
        else:
            self.headers = [
                "📝 Nama Pekerjaan",
                "🆔 ID",
                "📄 PO",
                "📅 Estimasi Mulai",
                "🚧 Tahap",
                "▶️ Mulai",
                "⏹️ Selesai",
                "⏰ Deadline",
                "🔍 Aksi",
            ]
            column_widths = [22, 7, 7, 15, 15, 15, 15, 15, 8]


        # 🔶 Header
        for col, (text, width) in enumerate(zip(self.headers, column_widths)):
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
            ).grid(row=1, column=0, columnspan=len(self.headers), pady=40)
            return

        # 🔷 Baris data
        for i, row in enumerate(rows, start=1):
            row_to_display = row[:4] + row[5:]
            tag = self.get_row_tag(row[6], row[8], row[7])

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
                if j == 3:
                    cell_bg = "#33a7d4"  # kuning terang, lebih mencolok
                    font_style = ("Segoe UI", 14, "bold", "underline")
                else:
                    cell_bg = bg_color
                Label(
                    self.table_frame,
                    text=val,
                    bd=1,
                    relief=RIDGE,
                    width=column_widths[j],
                    bg=cell_bg,
                    anchor="w",
                    font=font_style,
                    height=2,
                ).grid(row=i, column=j, sticky="nsew")

            # 🔍 Aksi - hanya jika bukan readonly
            if not self.readonly:
                Button(
                    self.table_frame,
                    text="ℹ️ Detail",
                    bg="#0984e3",
                    fg="white",
                    font=("Segoe UI", 12, "bold"),
                    cursor="hand2",
                    activebackground="#74b9ff",
                    command=lambda sid=row[1]: self.lihat_detail(sid),
                ).grid(row=i, column=len(self.headers) - 1, sticky="nsew", ipadx=10, pady=2)

        # Responsif
        for col in range(len(self.headers)):
            self.table_frame.grid_columnconfigure(col, weight=1)


    def lihat_detail(self, spk_id):
        print(f"🔍 Pindah ke halaman detail untuk SPK ID: {spk_id}")
        show_spk_detail(self.controller, spk_id)

    def get_row_tag(self, mulai, target, selesai):
        """Tentukan tag warna berdasarkan status deadline"""
        if not target or target == "-":
            return "normal"
        
        try:
            target_dt = datetime.strptime(target.strip(), "%d-%m-%Y %H:%M")
            now = datetime.now()
            
            if selesai and selesai != "-":
                selesai_dt = datetime.strptime(selesai.strip(), "%d-%m-%Y %H:%M:%S")
                if selesai_dt < target_dt:
                    return "selesai"
            
            if now > target_dt:
                return "terlambat"
            elif (target_dt - now).total_seconds() < 3600:  # 1 jam
                return "warning"
            elif not mulai or mulai.strip() == "-":
                return "belum"
            else:
                return "normal"
        except Exception as e:
            print(f"[ERROR] Gagal parsing waktu: {e}")
            return "normal"

    def search(self):
        keyword = self.search_var.get().strip()  # Bersihkan whitespace
        print(f"[DEBUG] Mencari dengan keyword: '{keyword}'")
        self.load_table(keyword if keyword else None)  # Kirim None jika keyword kosong

    def refresh_table(self):
        keyword = self.search_var.get()
        filter_status = self.filter_var.get()
        self.load_table(keyword, filter_status)
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
        print("Tombol Filter diklik!")  # Debugging
        keyword = self.search_var.get()
        filter_status = self.filter_var.get()
        self.load_table(keyword, filter_status)

    def auto_refresh(self):
        try:
            # Handle kasus readonly
            keyword = self.search_var.get() if hasattr(self, 'search_var') else None
            filter_status = self.filter_var.get() if hasattr(self, 'filter_var') else "semua"
            
            self.load_table(keyword, filter_status)
            self.after(10000, self.auto_refresh)
        except Exception as e:
            print(f"Error in auto_refresh: {e}")
            # Coba lagi setelah 10 detik
            self.after(10000, self.auto_refresh)
  