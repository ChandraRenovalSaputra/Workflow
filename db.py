# db.py
import sqlite3
import hashlib
import os

# Untuk login/register
def get_users_conn():
    return sqlite3.connect("users.db")

# # Untuk SPK/workflow
def get_workflow_conn():
    db_path = 'workflow.db'
    print("🔍 Membuka DB dari path:", os.path.abspath(db_path))  # DEBUG
    return sqlite3.connect("workflow.db")

def create_tables():
    conn = get_users_conn()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    try:
        conn = get_users_conn()
        cursor = conn.cursor()
        hashed = hash_password(password)
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def check_login(username, password):
    conn = get_users_conn()
    cursor = conn.cursor()
    hashed = hash_password(password)
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed))
    user = cursor.fetchone()
    conn.close()
    return user

def get_jadwal_pekerjaan():
    conn = get_workflow_conn()
    cursor = conn.cursor()

    query = """
    WITH current_stages AS (
        SELECT 
            t.spk_id,
            t.nama_tahapan,
            t.mulai,
            t.selesai,
            s.tanggal_kirim,
            s.nama_artikel,
            s.no_po,
            s.id,
            -- Menentukan tahap yang sedang berjalan (current stage)
            ROW_NUMBER() OVER (
                PARTITION BY t.spk_id 
                ORDER BY 
                    CASE 
                        WHEN date(t.mulai) <= date('now') AND date(t.selesai) >= date('now') THEN 0  -- Tahap sedang berjalan
                        WHEN date(t.mulai) > date('now') THEN 1  -- Tahap belum dimulai
                        ELSE 2  -- Tahap sudah selesai
                    END,
                    date(t.mulai) ASC
            ) as priority
        FROM spk_tahapan t
        JOIN spk s ON t.spk_id = s.id
    )
    SELECT 
        nama_artikel AS Nama_Pekerjaan,
        id AS ID,  
        no_po AS PO,
        nama_tahapan AS Tahap,
        mulai AS Mulai,
        selesai AS Selesai,
        tanggal_kirim AS Deadline
    FROM current_stages
    WHERE priority = 1;  -- Hanya ambil yang prioritas tertinggi (current stage)
    """

    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows

def search_jadwal(keyword):
    conn = get_workflow_conn()
    cursor = conn.cursor()
    query = """
    WITH current_stages AS (
        SELECT 
            t.spk_id,
            t.nama_tahapan,
            t.mulai,
            t.selesai,
            s.tanggal_kirim,
            s.nama_artikel,
            s.no_po,
            s.id,
            ROW_NUMBER() OVER (
                PARTITION BY t.spk_id 
                ORDER BY 
                    CASE 
                        WHEN date(t.mulai) <= date('now') AND date(t.selesai) >= date('now') THEN 0
                        WHEN date(t.mulai) > date('now') THEN 1
                        ELSE 2
                    END,
                    date(t.mulai) ASC
            ) as priority
        FROM spk_tahapan t
        JOIN spk s ON t.spk_id = s.id
        WHERE 
            s.nama_artikel LIKE ? OR 
            s.id LIKE ? OR 
            s.no_po LIKE ?
    )
    SELECT 
        nama_artikel AS Nama_Pekerjaan,
        id AS ID,  
        no_po AS PO,
        nama_tahapan AS Tahap,
        mulai AS Mulai,
        selesai AS Selesai,
        tanggal_kirim AS Deadline
    FROM current_stages
    WHERE priority = 1;
    """
    cursor.execute(query, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_spk_details(spk_id):
    conn = get_workflow_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM spk WHERE id = ?", (spk_id,))
    spk_data = cursor.fetchone()

    cursor.execute('''
        SELECT nama_tahapan, mulai, selesai, keterangan 
        FROM spk_tahapan 
        WHERE spk_id = ?
        ORDER BY date(mulai) ASC
    ''', (spk_id,))
    tahapan_data = cursor.fetchall()

    conn.close()
    return spk_data, tahapan_data

def create_spk_tables():
    conn = get_workflow_conn()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS spk (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_sales TEXT,
        no_po TEXT,
        costumer TEXT,
        nama_artikel TEXT,
        qty INTEGER,
        tanggal_kirim TEXT,
        jenis_bahan TEXT,
        qty_bahan INTEGER,
        ukuran_cetak TEXT,
        jumlah_cetak INTEGER,
        insheet INTEGER,
        total_cetak INTEGER,
        warna TEXT,
        varnish TEXT,
        finishing TEXT,
        gambar_desain BLOB,
        gambar_dummy BLOB
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS spk_tahapan (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        spk_id INTEGER,
        nama_tahapan TEXT,
        status TEXT,
        mulai TEXT,
        selesai TEXT,
        FOREIGN KEY(spk_id) REFERENCES spk(id)
    )
    """)
    conn.commit()
    conn.close()

def update_keterangan_tahapan(spk_id, tahap, keterangan):
    conn = get_workflow_conn()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE spk_tahapan 
            SET keterangan = ?
            WHERE spk_id = ? AND nama_tahapan = ?
        ''', (keterangan, spk_id, tahap))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating keterangan: {e}")
        return False
    finally:
        conn.close()