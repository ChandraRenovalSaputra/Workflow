import sqlite3
from datetime import datetime

class BarcodeScanner:
    def __init__(self, db_connection):
        self.conn = db_connection
        
    def handle_scan(self, spk_id, tahapan, operator):
        cursor = self.conn.cursor()

        # Cek apakah SPK tersedia
        cursor.execute("SELECT id FROM spk WHERE id = ?", (spk_id,))
        if not cursor.fetchone():
            return {"status": "error", "message": f"SPK {spk_id} tidak ditemukan"}

        now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        # Cek apakah sudah mulai dan selesai
        cursor.execute("""
            SELECT id, scan_mulai, scan_selesai FROM spk_tracking
            WHERE spk_id = ? AND tahapan = ?
            ORDER BY id DESC LIMIT 1
        """, (spk_id, tahapan))
        record = cursor.fetchone()

        if not record:
            # Belum ada tracking, mulai tahapan baru
            cursor.execute("""
                INSERT INTO spk_tracking (spk_id, tahapan, scan_mulai)
                VALUES (?, ?, ?)
            """, (spk_id, tahapan, now))
            message = f"✅ {tahapan} DIMULAI\nSPK-{spk_id}"
        elif record[2] is None:
            # Sudah mulai tapi belum selesai, update waktu selesai
            cursor.execute("""
                UPDATE spk_tracking
                SET scan_selesai = ? WHERE id = ?
            """, (now, record[0]))
            message = f"✅ {tahapan} SELESAI\nSPK-{spk_id}"
        else:
            # Sudah selesai dan tidak ada perubahan (scan ke-3 atau seterusnya diabaikan)
            return {"status": "success", "message": f"✅ {tahapan} sudah selesai, tidak ada perubahan lebih lanjut."}

        try:
            self.conn.commit()
            return {"status": "success", "message": message}
        except Exception as e:
            self.conn.rollback()
            return {"status": "error", "message": f"DB Error: {e}"}
