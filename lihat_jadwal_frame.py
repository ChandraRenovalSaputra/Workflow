from datetime import datetime
from tkinter import *
from tkinter import Frame, Label, Button, ttk
from db import get_jadwal_pekerjaan, get_workflow_conn
from detail_spk import show_spk_detail
from datetime import datetime


class LihatJadwalFrame(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg='lightgray')
        self.build_ui()  # Tambahkan ini untuk memanggil build_ui saat frame diinisialisasi
        
    def build_ui(self):
        # Header
        header = Label(self, text="TAHAP PRODUKSI BERJALAN", 
                    font=('Arial', 18, 'bold'), bg='lightgray')
        header.pack(pady=10)
        
        # Status Info
        self.status_info = Label(self, text="Menampilkan 0 pekerjaan aktif", 
                            bg='lightgray', font=('Arial', 10))
        self.status_info.pack()
        
        # Table Frame
        self.table_frame = Frame(self, bg='white', bd=2, relief=RIDGE)
        self.table_frame.pack(padx=20, pady=10, fill=BOTH, expand=True)
        
        # Scrollbar
        scroll_y = Scrollbar(self.table_frame)
        scroll_y.pack(side=RIGHT, fill=Y)
        
        # Treeview
        self.tree = ttk.Treeview(self.table_frame, 
                            columns=("nama", "id", "po", "tahap", "mulai", "selesai", "target", "operator", "aksi"), 
                            show="headings",
                            yscrollcommand=scroll_y.set)
        
        # Configure columns
        columns = [
            ("nama", "Nama Pekerjaan", 200),
            ("id", "ID SPK", 80),
            ("po", "No PO", 100),
            ("tahap", "Tahap Produksi", 150),
            ("mulai", "Waktu Mulai", 150),
            ("selesai", "Waktu Selesai", 150),
            ("target", "Target Selesai", 150),
            ("operator", "Operator", 120),
            ("aksi", "Aksi", 80)
        ]
        
        for col_id, col_text, width in columns:
            self.tree.heading(col_id, text=col_text)
            self.tree.column(col_id, width=width, anchor='center', stretch=NO)
        
        scroll_y.config(command=self.tree.yview)
        self.tree.pack(fill=BOTH, expand=True)
        self.tree.bind("<ButtonRelease-1>", self.on_tree_click)  # << Tambahkan baris ini
        self.tree.tag_configure('sedang', background='#fff2cc')  # Kuning muda

        # Control buttons
        btn_frame = Frame(self, bg='lightgray')
        btn_frame.pack(pady=10)
        
        Button(btn_frame, text="Refresh", command=self.load_data).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Scan", command=self.open_scanner).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Dashboard", command=self.kembali_ke_dashboard).pack(side=LEFT, padx=5)
        
        # Load initial data
        self.load_data()

    def load_data(self):
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            rows = get_jadwal_pekerjaan()
            
            if not rows:
                self.status_info.config(text="Tidak ada pekerjaan aktif")
                return
                
            for row in rows:
                try:
                    nama, spk_id, po, tahap, mulai, selesai, target, operator = row
                    
                    # Format waktu
                    mulai = self.format_waktu(mulai) if mulai else "-"
                    selesai = self.format_waktu(selesai) if selesai else "-"
                    target = self.format_waktu(target) if target else "-"
                    operator = operator if operator else "-"
                    
                    self.tree.insert("", "end", 
                                values=(nama, spk_id, po, tahap, mulai, selesai, target, operator, "📝 Detail"),
                                tags=(self.get_row_tag(mulai, target),))
                    
                except Exception as e:
                    print(f"Error processing row: {e}")
                    continue
            
            self.status_info.config(text=f"Menampilkan {len(rows)} pekerjaan aktif")
            
        except Exception as e:
            self.status_info.config(text=f"Error: {str(e)}", fg='red')
            print(f"Database error: {e}")

    def format_waktu(self, waktu_str):
        """Format waktu ke DD-MM-YYYY HH:MM dengan handling error"""
        if not waktu_str or waktu_str == "-":
            return "-"
        
        try:
            # Coba parse format database
            dt = datetime.strptime(waktu_str, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%d-%m-%Y %H:%M")
        except ValueError:
            try:
                # Jika sudah dalam format tampilan, return as-is
                datetime.strptime(waktu_str, "%d-%m-%Y %H:%M")
                return waktu_str
            except ValueError:
                return "-"  # atau return waktu_str untuk melihat data asli
            
    def on_tree_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            item = self.tree.identify_row(event.y)
            
            if column == "#9":  # Kolom aksi (kolom ke-9)
                spk_id = self.tree.item(item)['values'][1]  # Ambil ID SPK dari kolom ke-2
                self.show_detail(spk_id)

    def show_detail(self, spk_id):
        from detail_spk import show_spk_detail
        show_spk_detail(self.controller, spk_id)

    def get_row_tag(self, mulai, target):
        """Determine row color based on status"""
        if not mulai or mulai == "-":
            return 'belum'  # Abu-abu
            
        try:
            if not target or target == "-":
                return 'normal'  # Putih
                
            # Parse waktu
            mulai_dt = datetime.strptime(mulai, "%Y-%m-%d %H:%M:%S")
            target_dt = datetime.strptime(target, "%Y-%m-%d %H:%M:%S")
            
            if datetime.now() > target_dt:
                return 'terlambat'  # Merah muda
                
            if (target_dt - datetime.now()).total_seconds() < 12 * 3600:
                return 'warning'  # Kuning
                
            return 'sedang'  # Kuning muda (sedang dikerjakan)
        except:
            return 'normal'
        
    def open_scanner(self):
        from scanner_ui import ScannerApp
        from db import get_workflow_conn
        scanner = ScannerApp(self, get_workflow_conn())  # Pass self sebagai parent
        scanner.grab_set()

    def kembali_ke_dashboard(self):
        from ui_dashboard import DashboardFrame
        self.controller.switch_frame(DashboardFrame)