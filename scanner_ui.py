from tkinter import Toplevel, Label, Entry, messagebox
from datetime import datetime
import sqlite3

class ScannerApp(Toplevel):
    def __init__(self, parent, db_connection):
        super().__init__(parent)
        self.db_conn = db_connection
        self.parent = parent
        self.title("Scanner Produksi")
        self.geometry("400x200")
        self.is_open = True
        
        # UI elements
        Label(self, text="Scan ID SPK", font=('Arial', 14)).pack(pady=10)
        
        self.entry = Entry(self, font=('Arial', 12))
        self.entry.pack(pady=10)
        self.entry.focus_set()
        
        self.status_label = Label(self, text="Silakan scan ID SPK", font=('Arial', 12))
        self.status_label.pack(pady=10)
        
        self.entry.bind('<Return>', self.process_scan)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Initialize callback
        self.scan_complete_callback = None

    def on_close(self):
        self.is_open = False
        self.destroy()

    def set_scan_complete_callback(self, callback):
        """Set callback function to be called after successful scan"""
        self.scan_complete_callback = callback

    def process_scan(self, event):
        if not self.is_open:
            return
            
        spk_id = self.entry.get().strip()
        self.entry.delete(0, 'end')
        
        try:
            if not spk_id.isdigit():
                raise ValueError("ID SPK harus angka")
                
            self.update_production_stage(spk_id)
            
        except Exception as e:
            if self.is_open:
                self.status_label.config(text=f"Error: {str(e)}", fg='red')
                self.after(2000, self.reset_status)

    def reset_status(self):
        if self.is_open:
            self.status_label.config(text="Silakan scan ID SPK", fg='black')

    def update_production_stage(self, spk_id):
        cursor = self.db_conn.cursor()
        
        # 1. Validasi SPK
        cursor.execute("SELECT id FROM spk WHERE id = ?", (spk_id,))
        if not cursor.fetchone():
            raise ValueError(f"SPK {spk_id} tidak ditemukan")
        
        # 2. Dapatkan tahapan aktif
        tahap = self.get_active_stage(spk_id)
        if not tahap:
            raise ValueError("Tidak ada tahapan yang perlu diproses")
        
        # 3. Proses update
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Cek apakah sudah ada record yang belum selesai
        cursor.execute("""
            SELECT id FROM spk_tracking 
            WHERE spk_id = ? AND tahapan = ? AND scan_selesai IS NULL
            ORDER BY id DESC 
            LIMIT 1
        """, (spk_id, tahap))
        
        record = cursor.fetchone()
        
        if not record:  # Belum mulai
            cursor.execute("""
                INSERT INTO spk_tracking 
                (spk_id, tahapan, scan_mulai)
                VALUES (?, ?, ?)
            """, (spk_id, tahap, now))
            message = f"✅ {tahap} DIMULAI\nSPK-{spk_id}"
        else:  # Sudah mulai, selesaikan
            cursor.execute("""
                UPDATE spk_tracking 
                SET scan_selesai = ?
                WHERE id = ?
            """, (now, record[0]))
            message = f"✅ {tahap} SELESAI\nSPK-{spk_id}"
        
        try:
            self.db_conn.commit()
            if self.is_open:
                self.status_label.config(text=message, fg='green')
                # Execute callback if exists
                if self.scan_complete_callback:
                    self.scan_complete_callback()
                self.after(2000, self.on_close)
        except sqlite3.Error as e:
            self.db_conn.rollback()
            raise ValueError(f"Database error: {str(e)}")

    def get_active_stage(self, spk_id):
        """Mendapatkan tahapan aktif berikutnya"""
        cursor = self.db_conn.cursor()
        
        # Cari tahapan yang sudah mulai tapi belum selesai
        cursor.execute("""
            SELECT tahapan FROM spk_tracking 
            WHERE spk_id = ? AND scan_selesai IS NULL
            LIMIT 1
        """, (spk_id,))
        tahap_berjalan = cursor.fetchone()
        
        if tahap_berjalan:
            return tahap_berjalan[0]
        
        # Jika tidak ada, cari tahapan berikutnya yang belum dimulai
        cursor.execute("""
            SELECT t.nama_tahapan 
            FROM spk_tahapan t
            LEFT JOIN spk_tracking tr ON t.spk_id = tr.spk_id AND t.nama_tahapan = tr.tahapan
            WHERE t.spk_id = ?
            GROUP BY t.nama_tahapan
            HAVING MAX(tr.scan_mulai) IS NULL
            ORDER BY t.id ASC
            LIMIT 1
        """, (spk_id,))
        
        result = cursor.fetchone()
        return result[0] if result else None