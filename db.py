# db.py
from datetime import datetime
import sqlite3
import hashlib
import os


# Untuk login/register
def get_users_conn():
    return sqlite3.connect("users.db")


# # Untuk SPK/workflow
def get_workflow_conn():
    db_path = "workflow.db"
    print("🔍 Membuka DB dari path:", os.path.abspath(db_path))  # DEBUG
    return sqlite3.connect("workflow.db")


def create_tables():
    conn = get_users_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """
    )
    conn.commit()
    conn.close()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username, password):
    try:
        conn = get_users_conn()
        cursor = conn.cursor()
        hashed = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed)
        )
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
    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed)
    )
    user = cursor.fetchone()
    conn.close()
    return user


def get_jadwal_pekerjaan():
    conn = get_workflow_conn()
    cursor = conn.cursor()

    query = """
    WITH latest_tracking AS (
        SELECT 
            spk_id,
            tahapan,
            MAX(scan_mulai) as last_scan_mulai,
            MAX(scan_selesai) as last_scan_selesai
        FROM spk_tracking
        GROUP BY spk_id, tahapan
    ),
    current_stages AS (
        SELECT
            t.spk_id,
            t.nama_tahapan,
            lt.last_scan_mulai as mulai,
            lt.last_scan_selesai as selesai,
            t.selesai as target_selesai,
            ROW_NUMBER() OVER (PARTITION BY t.spk_id ORDER BY 
                CASE 
                    WHEN lt.last_scan_mulai IS NOT NULL AND lt.last_scan_selesai IS NULL THEN 0
                    WHEN lt.last_scan_mulai IS NULL THEN 1
                    ELSE 2
                END,
                lt.last_scan_mulai DESC NULLS LAST
            ) as stage_priority
        FROM spk_tahapan t
        LEFT JOIN latest_tracking lt ON t.spk_id = lt.spk_id AND t.nama_tahapan = lt.tahapan
    ),
    spk_status AS (
        SELECT 
            s.id as spk_id,
            CASE 
                WHEN COUNT(CASE WHEN lt.last_scan_selesai IS NULL THEN 1 END) > 0 
                THEN 'berjalan' 
                ELSE 'selesai' 
            END as status
        FROM spk s
        LEFT JOIN spk_tahapan t ON s.id = t.spk_id
        LEFT JOIN latest_tracking lt ON t.spk_id = lt.spk_id AND t.nama_tahapan = lt.tahapan
        GROUP BY s.id
    )
    SELECT
        s.nama_artikel,
        s.id as spk_id,
        s.no_po,
        ss.status,
        cs.nama_tahapan,
        cs.mulai,
        cs.selesai,
        cs.target_selesai as target
    FROM spk s
    JOIN current_stages cs ON s.id = cs.spk_id AND cs.stage_priority = 1
    JOIN spk_status ss ON s.id = ss.spk_id
    ORDER BY cs.spk_id DESC
    """

    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows



def get_spk_details(spk_id):
    conn = get_workflow_conn()
    cursor = conn.cursor()

    # Get SPK basic info
    cursor.execute("""
        SELECT id, order_sales, no_po, costumer, nama_artikel, qty, tanggal_kirim,
            jenis_bahan, qty_bahan, ukuran_cetak, jumlah_cetak, insheet, total_cetak,
            warna, varnish, finishing,
            gambar_desain, gambar_dummy, gambar_potong, barcode_image
        FROM spk WHERE id = ?
    """, (spk_id,))
    spk_data = cursor.fetchone()

    # Get tahapan with scan times - modified to match your schema
    cursor.execute(
        """
        SELECT 
            t.nama_tahapan,
            t.mulai as estimasi_mulai,
            t.selesai as estimasi_selesai,
            t.keterangan,
            MAX(tr.scan_mulai) as scan_mulai,
            MAX(tr.scan_selesai) as scan_selesai
        FROM spk_tahapan t
        LEFT JOIN spk_tracking tr ON t.spk_id = tr.spk_id AND t.nama_tahapan = tr.tahapan
        WHERE t.spk_id = ?
        GROUP BY t.nama_tahapan
        ORDER BY t.mulai ASC
    """,
        (spk_id,),
    )

    tahapan_data = cursor.fetchall()
    conn.close()

    return spk_data, tahapan_data


def create_spk_tables():
    conn = get_workflow_conn()
    cursor = conn.cursor()

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS spk (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_sales TEXT,
        no_po TEXT,
        costumer TEXT,
        nama_artikel TEXT,
        qty TEXT,
        tanggal_kirim TEXT,
        jenis_bahan TEXT,
        qty_bahan TEXT,
        ukuran_cetak TEXT,
        jumlah_cetak TEXT,
        insheet TEXT,
        total_cetak TEXT,
        warna TEXT,
        varnish TEXT,
        finishing TEXT,
        barcode_data TEXT,
        barcode_image BLOB,
        gambar_desain BLOB,
        gambar_dummy BLOB,
        gambar_potong BLOB
    )
    """
    )

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS spk_tahapan (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        spk_id INTEGER,
        nama_tahapan TEXT,
        status TEXT,
        keterangan TEXT,
        mulai TEXT,
        selesai TEXT,
        FOREIGN KEY(spk_id) REFERENCES spk(id)
    )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS spk_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            spk_id INTEGER NOT NULL,
            tahapan TEXT NOT NULL,
            scan_mulai TEXT,
            scan_selesai TEXT,
            FOREIGN KEY(spk_id) REFERENCES spk(id)
        )"""
    )
    conn.commit()
    conn.close()


def update_keterangan_tahapan(spk_id, tahap, keterangan):
    conn = get_workflow_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE spk_tahapan 
            SET keterangan = ?
            WHERE spk_id = ? AND nama_tahapan = ?
        """,
            (keterangan, spk_id, tahap),
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating keterangan: {e}")
        return False
    finally:
        conn.close()


def fix_datetime_format():
    """Function to standardize datetime formats in the database"""
    conn = get_workflow_conn()
    cursor = conn.cursor()

    try:
        print("Memperbaiki format waktu di database...")

        # Perbaiki format di spk_tracking
        cursor.execute(
            """
            UPDATE spk_tracking 
            SET scan_mulai = scan_mulai || ':00' 
            WHERE scan_mulai LIKE '%-% %H:%M' AND scan_mulai NOT LIKE '%:%:%'
        """
        )

        cursor.execute(
            """
            UPDATE spk_tracking 
            SET scan_selesai = scan_selesai || ':00' 
            WHERE scan_selesai LIKE '%-% %H:%M' AND scan_selesai NOT LIKE '%:%:%'
        """
        )

        # Perbaiki format di spk_tahapan
        cursor.execute(
            """
            UPDATE spk_tahapan 
            SET mulai = mulai || ':00' 
            WHERE mulai LIKE '%-% %H:%M' AND mulai NOT LIKE '%:%:%'
        """
        )

        cursor.execute(
            """
            UPDATE spk_tahapan 
            SET selesai = selesai || ':00' 
            WHERE selesai LIKE '%-% %H:%M' AND selesai NOT LIKE '%:%:%'
        """
        )

        conn.commit()
        print("Format waktu di database telah distandardisasi")
        return True
    except Exception as e:
        conn.rollback()
        print(f"Gagal memperbaiki format waktu: {e}")
        return False
    finally:
        conn.close()


def get_active_tahapan(spk_id):
    """Mendapatkan tahapan aktif berikutnya untuk SPK"""
    conn = get_workflow_conn()
    cursor = conn.cursor()

    # 1. Cek tahapan yang sudah mulai tapi belum selesai
    cursor.execute(
        """
        SELECT nama_tahapan FROM spk_tahapan 
        WHERE spk_id = ? AND mulai IS NOT NULL AND selesai IS NULL
        LIMIT 1
    """,
        (spk_id,),
    )
    tahap_berjalan = cursor.fetchone()

    if tahap_berjalan:
        return tahap_berjalan[0]  # Kembalikan tahapan yang sedang berjalan

    # 2. Jika tidak ada, ambil tahapan berikutnya yang belum dimulai
    cursor.execute(
        """
        SELECT nama_tahapan FROM spk_tahapan 
        WHERE spk_id = ? AND mulai IS NULL
        ORDER BY id ASC
        LIMIT 1
    """,
        (spk_id,),
    )
    tahap_berikutnya = cursor.fetchone()

    conn.close()
    return tahap_berikutnya[0] if tahap_berikutnya else None


def search_jadwal(keyword):
    if not keyword:  # kalau None atau string kosong, fallback ke get_jadwal_pekerjaan
        return get_jadwal_pekerjaan()

    conn = get_workflow_conn()
    cursor = conn.cursor()
    query = """
    WITH latest_tracking AS (
        SELECT 
            spk_id,
            tahapan,
            MAX(scan_mulai) as last_scan_mulai,
            MAX(scan_selesai) as last_scan_selesai
        FROM spk_tracking
        GROUP BY spk_id, tahapan
    ),
    current_stages AS (
        SELECT
            t.spk_id,
            t.nama_tahapan,
            lt.last_scan_mulai as mulai,
            lt.last_scan_selesai as selesai,
            t.selesai as target_selesai,
            ROW_NUMBER() OVER (PARTITION BY t.spk_id ORDER BY 
                CASE 
                    WHEN lt.last_scan_selesai IS NULL AND lt.last_scan_mulai IS NOT NULL THEN 0
                    WHEN lt.last_scan_mulai IS NULL THEN 1
                    ELSE 2
                END) as stage_priority
        FROM spk_tahapan t
        LEFT JOIN latest_tracking lt ON t.spk_id = lt.spk_id AND t.nama_tahapan = lt.tahapan
    )
    SELECT
        s.nama_artikel,
        s.id as spk_id,
        s.no_po,
        cs.nama_tahapan,
        cs.mulai,
        cs.selesai,
        cs.target_selesai as target
    FROM spk s
    JOIN current_stages cs ON s.id = cs.spk_id AND cs.stage_priority = 1
    WHERE cs.selesai IS NULL
    AND s.nama_artikel LIKE ?
    ORDER BY cs.target_selesai ASC
    """
    cursor.execute(query, ("%" + keyword + "%",))
    rows = cursor.fetchall()
    conn.close()
    return rows


def tambah_colom_db():
    conn = get_workflow_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE spk ADD COLUMN barcode_data TEXT")
        conn.commit()
        print("✅ Kolom barcode_data berhasil ditambahkan.")

        cursor.execute("ALTER TABLE spk ADD COLUMN barcode_image TEXT")
        conn.commit()
        print("✅ Kolom barcode_data dan image berhasil ditambahkan.")

        cursor.execute("ALTER TABLE spk_tahapan ADD COLUMN keterangan TEXT")
        conn.commit()
        print("✅ Kolom keterangan berhasil ditambahkan.")
    except sqlite3.OperationalError as e:
        print("ℹ️ Kolom sudah ada atau error lain:", e)
    finally:
        conn.close()

def get_user_count():
    """Mendapatkan jumlah user terdaftar"""
    conn = get_users_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    count = c.fetchone()[0]
    conn.close()
    return count

def is_username_exists(username):
    """Cek apakah username sudah ada"""
    conn = get_users_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def get_all_usernames():
    """Mendapatkan semua username yang terdaftar"""
    conn = get_users_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users")
    usernames = [row[0] for row in cursor.fetchall()]
    conn.close()
    return usernames

def update_user(old_username, new_username, new_password):
    """Update username dan password"""
    conn = get_users_conn()
    c = conn.cursor()
    try:
        hashed = hash_password(new_password)
        c.execute("UPDATE users SET username=?, password=? WHERE username=?", 
                (new_username, hashed, old_username))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()