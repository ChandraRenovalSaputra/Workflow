import serial
import threading
from scanner_handler import BarcodeScanner
from db import get_workflow_conn

SCANNER_MAP = {
    "COM6": "DESAIN",
    "COM7": "ACC DESAIN",

    # Tambahkan COM port lain jika perlu
}

def listen_scanner(port_name, tahapan):
    try:
        conn = get_workflow_conn()
        scanner = BarcodeScanner(conn)
        ser = serial.Serial(port_name, baudrate=9600, timeout=1)

        print(f"[{tahapan}] Mendengarkan {port_name}...")

        while True:
            if ser.in_waiting:
                data = ser.readline().decode('utf-8').strip()
                print(f"[{tahapan}] Data diterima: {data}")  # 🧪 Tambahkan ini
                if data.startswith("SPK-"):
                    spk_id = data.replace("SPK-", "")
                    result = scanner.handle_scan(spk_id, tahapan, "AutoScanner")
                    print(f"[{tahapan}] {result['message']}")

    except Exception as e:
        print(f"[{port_name}] ERROR: {e}")

# ✅ Tambahkan fungsi ini agar bisa dipanggil dari main.py
def start_all_scanners():
    for port, tahapan in SCANNER_MAP.items():
        thread = threading.Thread(target=listen_scanner, args=(port, tahapan), daemon=True)
        thread.start()
    print("Semua scanner listener aktif dari main.py")



# Untuk testing standalone, tetap bisa pakai python multi_scanner_listener.py
if __name__ == "__main__":
    start_all_scanners()
    import time
    while True:
        time.sleep(1)
