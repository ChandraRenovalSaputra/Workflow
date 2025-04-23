import sqlite3
from datetime import datetime

class BarcodeScanner:
    def __init__(self, db_connection):
        self.conn = db_connection
        
def handle_scan(self, spk_id, tahapan, operator):
    try:
        cursor = self.conn.cursor()
<<<<<<< HEAD
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
=======
        now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
>>>>>>> 4a0cafa991840edf09b92b03c4629b02f790b674
        
        # 1. Cek tahapan yang sedang aktif untuk SPK ini
        cursor.execute("""
            SELECT nama_tahapan 
            FROM spk_tahapan 
            WHERE spk_id = ? 
            AND mulai IS NOT NULL 
            AND selesai IS NULL
            LIMIT 1
        """, (spk_id,))
        current_tahap = cursor.fetchone()
        
        # 2. Validasi tahapan
        if current_tahap and tahapan != current_tahap[0]:
            return {
                'success': False,
                'message': f"Tahapan salah! Tahap aktif: {current_tahap[0]}"
            }
        
        # 3. Proses scan masuk/selesai
        cursor.execute("""
            SELECT id, scan_selesai 
            FROM spk_tracking 
            WHERE spk_id = ? AND tahapan = ?
            ORDER BY id DESC LIMIT 1
        """, (spk_id, tahapan))
        record = cursor.fetchone()
        
        if not record or record[1]:  # Scan masuk
            # Insert tracking
            cursor.execute("""
                INSERT INTO spk_tracking (spk_id, tahapan, scan_mulai, operator)
                VALUES (?, ?, ?, ?)
            """, (spk_id, tahapan, now, operator))
            
            # Update tahapan jika belum dimulai
            cursor.execute("""
                UPDATE spk_tahapan 
                SET mulai = ?
                WHERE spk_id = ? AND nama_tahapan = ? AND mulai IS NULL
            """, (now, spk_id, tahapan))
            
            status = 'start'
            message = f"✅ {tahapan} DIMULAI\nSPK-{spk_id}"
        else:  # Scan selesai
            # Update tracking
            cursor.execute("""
                UPDATE spk_tracking 
                SET scan_selesai = ?
                WHERE id = ?
            """, (now, record[0]))
            
            # Update tahapan
            cursor.execute("""
                UPDATE spk_tahapan 
                SET selesai = ?
                WHERE spk_id = ? AND nama_tahapan = ?
            """, (now, spk_id, tahapan))
            
            # Aktifkan tahap berikutnya
            cursor.execute("""
                UPDATE spk_tahapan 
                SET mulai = ?
                WHERE spk_id = ? AND nama_tahapan = (
                    SELECT nama_tahapan 
                    FROM spk_tahapan 
                    WHERE spk_id = ? AND mulai IS NULL 
                    ORDER BY id ASC LIMIT 1
                )
            """, (now, spk_id, spk_id))
            
            status = 'complete'
            message = f"✅ {tahapan} SELESAI\nSPK-{spk_id}"
        
        self.conn.commit()
        return {
            'success': True,
            'status': status,
            'message': message,
            'timestamp': now
        }
        
    except Exception as e:
        self.conn.rollback()
        return {
            'success': False,
            'message': f"⚠️ Error: {str(e)}"
        }