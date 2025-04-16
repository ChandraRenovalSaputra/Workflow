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
    SELECT 
        s.nama_artikel AS Nama_Pekerjaan,
        s.id AS ID,  
        s.no_po AS PO,
        t.nama_tahapan AS Tahap,
        t.mulai AS Mulai,
        t.selesai AS Selesai,
        s.tanggal_kirim AS Deadline
    FROM spk s
    LEFT JOIN spk_tahapan t ON s.id = t.spk_id
    WHERE t.selesai IS NOT NULL;
    """

    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows

def search_jadwal(keyword):
    conn = get_workflow_conn()
    cursor = conn.cursor()
    query = """
    SELECT 
        s.nama_artikel AS Nama_Pekerjaan,
        s.id AS ID,  
        s.no_po AS PO,
        t.nama_tahapan AS Tahap,
        t.mulai AS Mulai,
        t.selesai AS Selesai,
        s.tanggal_kirim AS Deadline
    FROM spk s
    LEFT JOIN spk_tahapan t ON s.id = t.spk_id
    WHERE 
        s.nama_artikel LIKE ? OR 
        s.id LIKE ? OR 
        s.no_po LIKE ?;
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

    cursor.execute("SELECT nama_tahapan, mulai, selesai FROM spk_tahapan WHERE spk_id = ?", (spk_id,))
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