import serial
import threading
from scanner_handler import BarcodeScanner
from db import get_workflow_conn

SCANNER_MAP = {
    "COM6": "DESAIN",
    "COM7": "ACC DESAIN",
    "COM8": "CTP",
    "COM9": "POTONG BAHAN",
    "COM10": "CETAK",
    "COM11": "POND",
    "COM12": "FORMING",
    "COM13": "LAMINATING / VARNISH",
    "COM14": "POLI",
    "COM15": "EMBOS",
    "COM16": "SPOT UV",
    "COM17": "LEM",
    "COM18": "SPIRAL",
}


def listen_scanner(port_name, tahapan):
    try:
        conn = get_workflow_conn()
        scanner = BarcodeScanner(conn)
        ser = serial.Serial(port_name, baudrate=9600, timeout=1)

        print(f"[{tahapan}] ✅ Listener aktif di {port_name}...")

        while True:
            if ser.in_waiting:
                try:
                    data = ser.readline().decode('utf-8').strip()
                    print(f"[{tahapan}] 🔍 Data diterima: {data}")

                    if data.startswith("SPK-"):
                        spk_id = data.replace("SPK-", "")
                        result = scanner.handle_scan(spk_id, tahapan, "AutoScanner")

                        if result["status"] == "success":
                            print(f"[{tahapan}] ✅ {result['message']}")
                        else:
                            print(f"[{tahapan}] ⚠️ {result['message']}")
                    else:
                        print(f"[{tahapan}] ❌ Format tidak dikenali: {data}")

                except Exception as e:
                    print(f"[{tahapan}] ❌ Error saat membaca data: {e}")

    except Exception as e:
        print(f"[{port_name}] ❌ Gagal membuka port: {e}")

# ✅ Tambahkan fungsi ini agar bisa dipanggil dari main.py
def start_all_scanners():
    for port, tahapan in SCANNER_MAP.items():
        thread = threading.Thread(target=listen_scanner, args=(port, tahapan), daemon=True)
        thread.start()
    print("✅ Semua scanner listener aktif (dipanggil dari main.py)")

# Bisa juga dijalankan langsung
if __name__ == "__main__":
    start_all_scanners()
    print("ini merge chandra yang baru")
    import time
    while True:
        time.sleep(1)
