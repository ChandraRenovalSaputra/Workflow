from datetime import datetime
from tkinter import *
from tkinter import Frame, Label, Button, filedialog, messagebox
import pandas as pd
from db import get_jadwal_pekerjaan, get_workflow_conn, search_jadwal, get_spk_details
from detail_spk import show_spk_detail
from scrollable_frame import ScrollableFrame
from backup_db import BackupManager

import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
from datetime import datetime, timedelta
from openpyxl import load_workbook
from openpyxl.styles import Border, Side, Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

# Add import for calendar date picker
try:
    from tkcalendar import DateEntry
except ImportError:
    messagebox.showerror("Import Error", "Module 'tkcalendar' not found. Please install it with 'pip install tkcalendar'.")


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
            self.button_container.pack(expand=True)

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

            # New Export to Excel button
            Button(
                self.button_container,
                text="📤 Export to Excel",
                font=("Segoe UI", 12, "bold"),
                bg="#8e44ad",
                fg="white",
                activebackground="#9b59b6",
                command=self.prompt_export_with_date_filter,
                padx=15,
            ).pack(side=LEFT, padx=5)

        # Scrollable Frame untuk Tabel (tengah)
        self.scrollable = ScrollableFrame(self)
        self.scrollable.pack(padx=30, pady=10, fill="both", expand=True)
        self.table_frame = self.scrollable.scrollable_frame

        # Filter Frame (SELALU tampil, baik readonly maupun tidak)
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

        # Tombol Kembali (hanya saat bukan readonly)
        if not self.readonly:
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

            # Ambil estimasi_mulai dari tahapan "sedang", atau tahap berikutnya yang aktif
            estimasi_mulai = "-"
            if tahapan_data and len(tahapan_data) > 0:
                # Urutkan berdasarkan estimasi_mulai
                from datetime import datetime

                def safe_datetime(val):
                    try:
                        return datetime.strptime(val, "%d-%m-%Y %H:%M")
                    except:
                        return datetime.max

                # Urutkan berdasarkan estimasi mulai
                tahapan_data_sorted = sorted(tahapan_data, key=lambda x: safe_datetime(x[1]))

                # Tahapan sedang = tanggal_mulai terisi, tanggal_selesai kosong
                tahapan_sedang = next((t for t in tahapan_data_sorted if t[4] and not t[5]), None)

                # Kalau tidak ada, cari tahapan berikutnya yang belum dimulai
                if not tahapan_sedang:
                    tahapan_sedang = next((t for t in tahapan_data_sorted if not t[4] and not t[5]), None)

                # Kalau semua sudah selesai, ambil tahap terakhir
                if not tahapan_sedang:
                    tahapan_sedang = tahapan_data_sorted[-1]

                # Ambil estimasi_mulai
                estimasi_mulai = tahapan_sedang[1] or "-"


            # Sisipkan estimasi_mulai di index 3, geser sisa ke kanan
            new_row = row[:3] + (estimasi_mulai,) + row[3:]
            rows_with_estimasi.append(new_row)

        rows = rows_with_estimasi


        for widget in self.table_frame.winfo_children():
            widget.destroy()

        print(f"Data setelah filter status '{filter_status}': ", rows)

        # Ambil hanya tahap terakhir per SPK
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
            column_widths = [22, 7, 9, 13, 15, 15, 15, 15, 8]

        # Header
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

        # Baris data
        for i, row in enumerate(rows, start=1):
            row_to_display = row[:4] + row[5:]  # Buang index ke-4 (status SPK), karena estimasi_mulai sudah ditambah sebelumnya
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
                    cell_bg = "#39E08F"
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

            # Aksi detail (jika bukan readonly)
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

    def show_export_date_filter_dialog(self):
        """Popup dialog to select date filter before export."""
        dialog = tk.Toplevel(self)
        dialog.title("Pilih Filter Tanggal Export")
        dialog.geometry("320x280")
        dialog.grab_set()

        tk.Label(dialog, text="Pilih filter tanggal untuk export:", font=("Segoe UI", 12, "bold")).pack(pady=10)

        filter_var = tk.StringVar(value="hari_ini")

        options = [
            ("Hari Ini", "hari_ini"),
            ("Minggu Ini", "minggu_ini"),
            ("Bulan Ini", "bulan_ini"),
            ("Custom Tanggal", "custom"),
        ]

        for text, value in options:
            tk.Radiobutton(dialog, text=text, variable=filter_var, value=value, font=("Segoe UI", 11)).pack(anchor="w", padx=20)

        start_date_var = tk.StringVar()
        end_date_var = tk.StringVar()

        def show_date_entries():
            if filter_var.get() == "custom":
                start_label.pack(pady=(10,0))
                start_entry.pack()
                end_label.pack(pady=(10,0))
                end_entry.pack()
            else:
                start_label.pack_forget()
                start_entry.pack_forget()
                end_label.pack_forget()
                end_entry.pack_forget()

        filter_var.trace("w", lambda *args: show_date_entries())

        start_label = tk.Label(dialog, text="Tanggal Mulai (dd-mm-yyyy):", font=("Segoe UI", 10))
        start_entry = tk.Entry(dialog, textvariable=start_date_var, font=("Segoe UI", 10))
        end_label = tk.Label(dialog, text="Tanggal Akhir (dd-mm-yyyy):", font=("Segoe UI", 10))
        end_entry = tk.Entry(dialog, textvariable=end_date_var, font=("Segoe UI", 10))

        def on_confirm():
            selected_filter = filter_var.get()
            start_date = None
            end_date = None

            today = datetime.now().date()

            if selected_filter == "hari_ini":
                start_date = today
                end_date = today
            elif selected_filter == "minggu_ini":
                start_date = today - timedelta(days=today.weekday())  # Monday
                end_date = start_date + timedelta(days=6)  # Sunday
            elif selected_filter == "bulan_ini":
                start_date = today.replace(day=1)
                # Calculate last day of month
                if start_date.month == 12:
                    end_date = start_date.replace(year=start_date.year+1, month=1, day=1) - timedelta(days=1)
                else:
                    end_date = start_date.replace(month=start_date.month+1, day=1) - timedelta(days=1)
            elif selected_filter == "custom":
                try:
                    start_date = datetime.strptime(start_date_var.get(), "%d-%m-%Y").date()
                    end_date = datetime.strptime(end_date_var.get(), "%d-%m-%Y").date()
                    if start_date > end_date:
                        messagebox.showerror("Error", "Tanggal Mulai harus sebelum Tanggal Akhir.")
                        return
                except Exception as e:
                    messagebox.showerror("Error", "Format tanggal salah. Gunakan dd-mm-yyyy.")
                    return

            dialog.destroy()
            self.export_to_excel(date_filter=(start_date, end_date), selected_filter=selected_filter)

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=15)
        tk.Button(btn_frame, text="Export", command=on_confirm, font=("Segoe UI", 11, "bold"), bg="#27ae60", fg="white").pack(side="left", padx=10)
        tk.Button(btn_frame, text="Batal", command=dialog.destroy, font=("Segoe UI", 11), bg="#c0392b", fg="white").pack(side="left", padx=10)

    def prompt_export_with_date_filter(self):
        """Show popup to select date filter and then export."""
        dialog = tk.Toplevel(self)
        dialog.title("Pilih Filter Tanggal Export")
        dialog.geometry("400x350")  # Increased size to avoid cutoff
        dialog.grab_set()

        tk.Label(dialog, text="Pilih filter tanggal untuk export:", font=("Segoe UI", 12, "bold")).pack(pady=10)

        filter_var = tk.StringVar(value="hari_ini")

        options = [
            ("Hari Ini", "hari_ini"),
            ("Minggu Ini", "minggu_ini"),
            ("Bulan Ini", "bulan_ini"),
            ("Custom Tanggal", "custom"),
        ]

        for text, value in options:
            tk.Radiobutton(dialog, text=text, variable=filter_var, value=value, font=("Segoe UI", 11)).pack(anchor="w", padx=20)

        # Use DateEntry widgets for date selection instead of manual entry
        start_label = tk.Label(dialog, text="Tanggal Mulai:", font=("Segoe UI", 10))
        start_date_entry = DateEntry(dialog, date_pattern='dd-mm-yyyy', font=("Segoe UI", 10))
        end_label = tk.Label(dialog, text="Tanggal Akhir:", font=("Segoe UI", 10))
        end_date_entry = DateEntry(dialog, date_pattern='dd-mm-yyyy', font=("Segoe UI", 10))

        def show_date_entries():
            if filter_var.get() == "custom":
                start_label.pack(pady=(10, 0))
                start_date_entry.pack()
                end_label.pack(pady=(10, 0))
                end_date_entry.pack()
            else:
                start_label.pack_forget()
                start_date_entry.pack_forget()
                end_label.pack_forget()
                end_date_entry.pack_forget()

        filter_var.trace("w", lambda *args: show_date_entries())

        def on_confirm():
            selected_filter = filter_var.get()
            start_date = None
            end_date = None

            today = datetime.now().date()

            if selected_filter == "hari_ini":
                start_date = today
                end_date = today
            elif selected_filter == "minggu_ini":
                start_date = today - timedelta(days=today.weekday())  # Monday
                end_date = start_date + timedelta(days=6)  # Sunday
            elif selected_filter == "bulan_ini":
                start_date = today.replace(day=1)
                # Calculate last day of month
                if start_date.month == 12:
                    end_date = start_date.replace(year=start_date.year+1, month=1, day=1) - timedelta(days=1)
                else:
                    end_date = start_date.replace(month=start_date.month+1, day=1) - timedelta(days=1)
            elif selected_filter == "custom":
                try:
                    start_date = start_date_entry.get_date()
                    end_date = end_date_entry.get_date()
                    if start_date > end_date:
                        messagebox.showerror("Error", "Tanggal Mulai harus sebelum Tanggal Akhir.")
                        return
                except Exception as e:
                    messagebox.showerror("Error", "Format tanggal salah.")
                    return

            dialog.destroy()
            self.export_to_excel(date_filter=(start_date, end_date), selected_filter=filter_var.get())

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=15)
        tk.Button(btn_frame, text="Export", command=on_confirm, font=("Segoe UI", 11, "bold"), bg="#27ae60", fg="white").pack(side="left", padx=10)
        tk.Button(btn_frame, text="Batal", command=dialog.destroy, font=("Segoe UI", 11), bg="#c0392b", fg="white").pack(side="left", padx=10)

    def export_to_excel(self, date_filter=None, selected_filter=None):
        try:
            import pandas as pd
            from tkinter import filedialog, messagebox
            from openpyxl import load_workbook
            from openpyxl.styles import Border, Side, Alignment, Font, PatternFill
            from openpyxl.utils import get_column_letter

            keyword = self.search_var.get() if hasattr(self, 'search_var') else None
            filter_status = self.filter_var.get() if hasattr(self, 'filter_var') else "semua"

            if keyword and keyword.strip():
                rows = search_jadwal(keyword)
            else:
                rows = get_jadwal_pekerjaan()

            if filter_status == "berjalan":
                rows = [r for r in rows if r[3].lower() != "selesai"]
            elif filter_status == "selesai":
                rows = [r for r in rows if r[3].lower() == "selesai"]

            export_data = []
            no_counter = 1

            for row in rows:
                spk_id = row[1]
                spk_data, tahapan_data = get_spk_details(spk_id)

                if not spk_data:
                    continue

                # Filter by date_filter if provided
                if date_filter and tahapan_data and len(tahapan_data) > 0:
                    estimasi_mulai_str = tahapan_data[0][1]  # estimasi mulai tahap pertama
                    if estimasi_mulai_str and estimasi_mulai_str != "-":
                        estimasi_mulai_date = datetime.strptime(estimasi_mulai_str.split()[0], "%d-%m-%Y").date()
                        start_date, end_date = date_filter
                        if estimasi_mulai_date < start_date or estimasi_mulai_date > end_date:
                            continue
                    else:
                        continue  # Skip if no estimasi mulai

                order_sales = spk_data[1]
                no_po = spk_data[2]
                costumer = spk_data[3]
                nama_artikel = spk_data[4]
                qty = spk_data[5]
                tanggal_kirim = spk_data[6]
                jenis_bahan = spk_data[7]
                qty_bahan = spk_data[8]
                ukuran_cetak = spk_data[9]
                jumlah_cetak = spk_data[10]
                insheet = spk_data[11]
                total_cetak = spk_data[12]
                warna = spk_data[13]
                varnish = spk_data[14]
                finishing = spk_data[15]

                status = row[3] if len(row) > 3 else "-"

                if tahapan_data and len(tahapan_data) > 0:
                    first_stage = True
                    for tahap in tahapan_data:
                        tahap_nama = tahap[0]
                        estimasi_mulai = tahap[1] or "-"
                        mulai = tahap[4] or "-"
                        selesai = tahap[5] or "-"
                        deadline = tahap[2] or "-"
                        keterangan = tahap[3] or ""

                        if first_stage:
                            export_data.append({
                                "No": no_counter,
                                "Order Sales": order_sales,
                                "No PO": no_po,
                                "Costumer": costumer,
                                "Nama Artikel": nama_artikel,
                                "Qty": qty,
                                "Tanggal Kirim": tanggal_kirim,
                                "Jenis Bahan": jenis_bahan,
                                "Qty Bahan": qty_bahan,
                                "Ukuran Cetak": ukuran_cetak,
                                "Jumlah Cetak": jumlah_cetak,
                                "Insheet": insheet,
                                "Total Cetak": total_cetak,
                                "Warna": warna,
                                "Varnish": varnish,
                                "Finishing": finishing,
                                "Estimasi Mulai": estimasi_mulai,
                                "Tahap": tahap_nama,
                                "Mulai": mulai,
                                "Selesai": selesai,
                                "Deadline": deadline,
                                "Status": status,
                                "Keterangan": keterangan,
                            })
                            first_stage = False
                            no_counter += 1
                        else:
                            export_data.append({
                                "No": "",
                                "Order Sales": "",
                                "No PO": "",
                                "Costumer": "",
                                "Nama Artikel": "",
                                "Qty": "",
                                "Tanggal Kirim": "",
                                "Jenis Bahan": "",
                                "Qty Bahan": "",
                                "Ukuran Cetak": "",
                                "Jumlah Cetak": "",
                                "Insheet": "",
                                "Total Cetak": "",
                                "Warna": "",
                                "Varnish": "",
                                "Finishing": "",
                                "Estimasi Mulai": estimasi_mulai,
                                "Tahap": tahap_nama,
                                "Mulai": mulai,
                                "Selesai": selesai,
                                "Deadline": deadline,
                                "Status": status,
                                "Keterangan": keterangan,
                            })
                else:
                    export_data.append({
                        "No": no_counter,
                        "Order Sales": order_sales,
                        "No PO": no_po,
                        "Costumer": costumer,
                        "Nama Artikel": nama_artikel,
                        "Qty": qty,
                        "Tanggal Kirim": tanggal_kirim,
                        "Jenis Bahan": jenis_bahan,
                        "Qty Bahan": qty_bahan,
                        "Ukuran Cetak": ukuran_cetak,
                        "Jumlah Cetak": jumlah_cetak,
                        "Insheet": insheet,
                        "Total Cetak": total_cetak,
                        "Warna": warna,
                        "Varnish": varnish,
                        "Finishing": finishing,
                        "Estimasi Mulai": "-",
                        "Tahap": "-",
                        "Mulai": "-",
                        "Selesai": "-",
                        "Deadline": "-",
                        "Status": status,
                        "Keterangan": "",
                    })
                    no_counter += 1

            if not export_data:
                messagebox.showinfo("Export", "Tidak ada data untuk diekspor.")
                return

            df = pd.DataFrame(export_data)

            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Save as"
            )
            if not file_path:
                return

            # Simpan DataFrame ke Excel tanpa header, mulai dari baris 6 (startrow=5)
            df.to_excel(file_path, index=False, header=False, startrow=5)

            wb = load_workbook(file_path)
            ws = wb.active

            # 🧹 Bersihkan sel-sel atas yang pernah digunakan
            for cell in ['A1', 'A2', 'B1', 'C1', 'D1']:
                ws[cell] = ""

            # Hitung teks periode
            period_text = ""
            print(f"[DEBUG] selected_filter: {selected_filter}, date_filter: {date_filter}")
            if selected_filter == "hari_ini":
                period_text = date_filter[0].strftime("%d-%m-%Y")
            elif selected_filter == "minggu_ini":
                start_date, end_date = date_filter
                period_text = f"{start_date.strftime('%d-%m-%Y')} - {end_date.strftime('%d-%m-%Y')}"
            elif selected_filter == "bulan_ini":
                month_names = {
                    1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
                    5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
                    9: "September", 10: "Oktober", 11: "November", 12: "Desember"
                }
                month_num = date_filter[0].month
                year = date_filter[0].year
                period_text = f"{month_names.get(month_num, '')} {year}"
            elif selected_filter == "custom":
                start_date, end_date = date_filter
                period_text = f"{start_date.strftime('%d-%m-%Y')} - {end_date.strftime('%d-%m-%Y')}"

            # ✅ Tulis label dan nilai ke A3 & B3
            ws['A3'] = "Periode :"
            ws['A3'].font = Font(bold=True)
            ws['A3'].alignment = Alignment(horizontal='left')

            ws['B3'] = period_text
            ws['B3'].font = Font(bold=True)
            ws['B3'].alignment = Alignment(horizontal='left')
            # Add "Periode :" label and period text combined in merged cells A1:B1
            period_text = ""
            print(f"[DEBUG] selected_filter: {selected_filter}, date_filter: {date_filter}")  # Debugging
            if selected_filter == "hari_ini":
                period_text = date_filter[0].strftime("%d-%m-%Y")
            elif selected_filter == "minggu_ini":
                # Format as "dd-mm-yyyy - dd-mm-yyyy"
                start_date = date_filter[0]
                end_date = date_filter[1]
                period_text = f"{start_date.strftime('%d-%m-%Y')} - {end_date.strftime('%d-%m-%Y')}"
            elif selected_filter == "bulan_ini":
                # Format as "month name" in Indonesian
                month_names = {
                    1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
                    5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
                    9: "September", 10: "Oktober", 11: "November", 12: "Desember"
                }
                month_num = date_filter[0].month
                month_name = month_names.get(month_num, "")
                year = date_filter[0].year
                period_text = f"{month_name} {year}"
            elif selected_filter == "custom":
                period_text = f"{date_filter[0].strftime('%d-%m-%Y')} - {date_filter[1].strftime('%d-%m-%Y')}"

            # Place period text in cell B3 as requested
            if selected_filter == "hari_ini":
                period_text = date_filter[0].strftime("%d-%m-%Y")
            elif selected_filter == "minggu_ini":
                start_date = date_filter[0]
                end_date = date_filter[1]
                period_text = f"{start_date.strftime('%d-%m-%Y')} - {end_date.strftime('%d-%m-%Y')}"
            elif selected_filter == "bulan_ini":
                month_names = {
                    1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
                    5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
                    9: "September", 10: "Oktober", 11: "November", 12: "Desember"
                }
                month_num = date_filter[0].month
                month_name = month_names.get(month_num, "")
                year = date_filter[0].year
                period_text = f"{month_name} {year}"
            elif selected_filter == "custom":
                period_text = f"{date_filter[0].strftime('%d-%m-%Y')} - {date_filter[1].strftime('%d-%m-%Y')}"

            # Merge dan styling judul serta header seperti sebelumnya
            ws.merge_cells('J1:N1')
            title_cell = ws['J1']
            title_cell.value = "JADWAL PEKERJAAN"
            title_cell.alignment = Alignment(horizontal='center', vertical='center')
            title_cell.font = Font(size=14, bold=True)

            # Define header rows content (rows 4 and 5)
            header_row_4 = [
                "No", "Order Sales", "No PO", "Costumer", "Nama Artikel", "Qty", "Tanggal Kirim",
                "Jenis Bahan", "Qty Bahan", "Ukuran Cetak", "Jumlah Cetak", "Insheet", "Total Cetak",
                "Warna", "Varnish", "Finishing", "Estimasi Mulai", "Tahap", "Mulai", "Selesai",
                "Deadline", "Status", "Keterangan"
            ]
            header_row_5 = [
                "", "", "", "", "", "", "",
                "", "", "", "", "", "",
                "", "", "", "", "", "", "",
                "", "", "", ""
            ]

            max_col = len(header_row_4)

            # Write header rows manually with merged cells vertically (rows 4 and 5)
            for col in range(1, max_col + 1):
                col_letter = get_column_letter(col)
                # Merge header cells vertically (rows 4 and 5)
                ws.merge_cells(f'{col_letter}4:{col_letter}5')
                # Set value and style on merged cell (row 4)
                cell_4 = ws.cell(row=4, column=col)
                cell_4.value = header_row_4[col - 1]
                cell_4.fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")  # Bright yellow
                cell_4.alignment = Alignment(horizontal='center', vertical='center')
                cell_4.font = Font(bold=True, color="000000")

            # Apply borders to header and data cells
            thin = Side(border_style="thin", color="000000")
            thick = Side(border_style="thick", color="000000")

            for row in range(4, ws.max_row + 1):
                for col in range(1, max_col + 1):
                    cell = ws.cell(row=row, column=col)
                    cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)

            # Thick border for outside edges
            for col in range(1, max_col + 1):
                ws.cell(row=4, column=col).border = Border(
                    top=thick,
                    left=ws.cell(row=4, column=col).border.left,
                    right=ws.cell(row=4, column=col).border.right,
                    bottom=ws.cell(row=4, column=col).border.bottom
                )
                ws.cell(row=ws.max_row, column=col).border = Border(
                    bottom=thick,
                    left=ws.cell(row=ws.max_row, column=col).border.left,
                    right=ws.cell(row=ws.max_row, column=col).border.right,
                    top=ws.cell(row=ws.max_row, column=col).border.top
                )
            for row in range(4, ws.max_row + 1):
                ws.cell(row=row, column=1).border = Border(
                    left=thick,
                    top=ws.cell(row=row, column=1).border.top,
                    bottom=ws.cell(row=row, column=1).border.bottom,
                    right=ws.cell(row=row, column=1).border.right
                )
                ws.cell(row=row, column=max_col).border = Border(
                    right=thick,
                    top=ws.cell(row=row, column=max_col).border.top,
                    bottom=ws.cell(row=row, column=max_col).border.bottom,
                    left=ws.cell(row=row, column=max_col).border.left
                )

            # Adjust row heights for title and header rows
            ws.row_dimensions[1].height = 30
            ws.row_dimensions[3].height = 20
            ws.row_dimensions[4].height = 25
            ws.row_dimensions[5].height = 25

            wb.save(file_path)

            messagebox.showinfo("Export Successful", f"Data berhasil diekspor ke {file_path}")

        except ImportError:
            messagebox.showerror("Export Failed", "Modul 'pandas' atau 'openpyxl' tidak ditemukan. Silakan instal dengan 'pip install pandas openpyxl'.")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Gagal mengekspor data: {e}")