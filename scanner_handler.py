import sqlite3
from datetime import datetime

class BarcodeScanner:
    global_refresh_callback = None

    @classmethod
    def set_global_refresh_callback(cls, callback):
        cls.global_refresh_callback = callback

    def __init__(self, db_connection):
        self.conn = db_connection

    def handle_scan(self, spk_id, tahapan, operator):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM spk WHERE id = ?", (spk_id,))
        if not cursor.fetchone():
            return {"status": "error", "message": f"❌ SPK {spk_id} tidak ditemukan"}

        # 🔒 Cek apakah tahapan sebelumnya sudah selesai
        cursor.execute("""
            SELECT nama_tahapan FROM spk_tahapan 
            WHERE spk_id = ? ORDER BY id ASC
        """, (spk_id,))
        semua_tahapan = [row[0] for row in cursor.fetchall()]

        if tahapan in semua_tahapan:
            idx = semua_tahapan.index(tahapan)
            if idx > 0:
                tahapan_sebelumnya = semua_tahapan[idx - 1]
                cursor.execute("""
                    SELECT scan_selesai FROM spk_tracking 
                    WHERE spk_id = ? AND tahapan = ? 
                    ORDER BY id DESC LIMIT 1
                """, (spk_id, tahapan_sebelumnya))
                hasil = cursor.fetchone()
                if not hasil or not hasil[0]:
                    return {"status": "warning", "message": f"🚫 Tahapan sebelumnya '{tahapan_sebelumnya}' belum selesai.\nTidak bisa melanjutkan ke '{tahapan}'."}

        now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        # Lanjutkan seperti biasa
        cursor.execute("""
            SELECT id, scan_mulai, scan_selesai FROM spk_tracking
            WHERE spk_id = ? AND tahapan = ?
            ORDER BY id DESC LIMIT 1
        """, (spk_id, tahapan))
        record = cursor.fetchone()

        if not record:
            cursor.execute("""
                INSERT INTO spk_tracking (spk_id, tahapan, scan_mulai)
                VALUES (?, ?, ?)
            """, (spk_id, tahapan, now))
            message = f"{tahapan} DIMULAI\nSPK-{spk_id}"
        elif record[1] and not record[2]:
            cursor.execute("""
                UPDATE spk_tracking
                SET scan_selesai = ? WHERE id = ?
            """, (now, record[0]))
            message = f"{tahapan} SELESAI\nSPK-{spk_id}"
        elif record[1] and record[2]:
            return {"status": "info", "message": f"🔒 {tahapan} sudah selesai untuk SPK-{spk_id}. Scan diabaikan."}
        else:
            return {"status": "error", "message": "❌ Data tidak valid."}

        try:
            self.conn.commit()

            # 🔁 Panggil callback jika ada
            if BarcodeScanner.global_refresh_callback:
                try:
                    BarcodeScanner.global_refresh_callback()
                except Exception as e:
                    print(f"Gagal memanggil callback refresh: {e}")

            return {"status": "success", "message": f"✅ {message}"}
        except Exception as e:
            self.conn.rollback()
            return {"status": "error", "message": f"DB Error: {e}"}
