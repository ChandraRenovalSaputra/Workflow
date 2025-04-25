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
            return {"status": "error", "message": f"❌ SPK {spk_id} tidak ditemukan"}

        now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        # Cek apakah sudah mulai dan selesai
        cursor.execute("""
            SELECT id, scan_mulai, scan_selesai FROM spk_tracking
            WHERE spk_id = ? AND tahapan = ?
            ORDER BY id DESC LIMIT 1
        """, (spk_id, tahapan))
        record = cursor.fetchone()

        if not record:
            # Belum ada tracking → catat waktu mulai
            cursor.execute("""
                INSERT INTO spk_tracking (spk_id, tahapan, scan_mulai)
                VALUES (?, ?, ?)
            """, (spk_id, tahapan, now))
            message = f"{tahapan} DIMULAI\nSPK-{spk_id}"
        elif record[1] and not record[2]:
            # Sudah mulai tapi belum selesai → catat waktu selesai
            cursor.execute("""
                UPDATE spk_tracking
                SET scan_selesai = ? WHERE id = ?
            """, (now, record[0]))
            message = f"{tahapan} SELESAI\nSPK-{spk_id}"
        elif record[1] and record[2]:
            # Sudah selesai → scan diabaikan
            return {"status": "info", "message": f"🔒 {tahapan} sudah selesai untuk SPK-{spk_id}. Scan diabaikan."}
        else:
            # Tidak valid (harusnya tidak terjadi)
            return {"status": "error", "message": "❌ Data tidak valid."}

        try:
            self.conn.commit()
            return {"status": "success", "message": f"✅ {message}"}
        except Exception as e:
            self.conn.rollback()
            return {"status": "error", "message": f"DB Error: {e}"}
