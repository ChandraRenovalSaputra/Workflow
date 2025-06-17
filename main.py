import tkinter as tk
from tkinter import ttk
from ui_login import LoginFrame
from db import create_tables, create_spk_tables
from db import tambah_colom_db
from multi_scanner_listener import start_all_scanners
from backup_db import BackupManager
import threading
from lihat_jadwal_frame import LihatJadwalFrame
from scanner_handler import BarcodeScanner

create_tables()
create_spk_tables()


def center_window(root, width=1600, height=800):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    root.geometry(f"1000x800")
    root.minsize(width, height)
    root.configure(bg="white")


BACKUP_CONFIG = [
    ("workflow.db", "workflow_backup"),
    ("users.db", "users_backup")
]


class App(tk.Tk):
    def __init__(self):
        from ui_dashboard import DashboardFrame
        from ui_profile import ProfileFrame
        self.dashboard_frame_class = DashboardFrame
        self.profile_frame_class = ProfileFrame
        super().__init__()
        self.title("Sistem Workflow Percetakan")
        self.current_user = None
        self.tv_window = None

        center_window(self, 1600, 800)
        self.resizable(True, True)
        create_tables()
        self.state("zoomed")

        self._frame = None
        self.switch_frame(LoginFrame)

        self.backup_manager = BackupManager(databases=BACKUP_CONFIG)
        self.backup_manager.start()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Tambahkan callback global untuk refresh tampilan setelah scan
        def refresh_jadwal():
            if hasattr(self, 'tv_window') and self.tv_window:
                try:
                    self.tv_window.jadwal_frame.refresh_table()
                except Exception as e:
                    print(f"Gagal auto-refresh layar TV: {e}")
            if hasattr(self, '_frame') and isinstance(self._frame, LihatJadwalFrame):
                try:
                    self._frame.refresh_table()
                except Exception as e:
                    print(f"Gagal auto-refresh frame utama: {e}")

        BarcodeScanner.set_global_refresh_callback(refresh_jadwal)

    def _on_close(self):
        self.backup_manager.shutdown()
        self.destroy()

    def switch_frame(self, frame_class, *args):
        if self._frame is not None:
            self._frame.destroy()

        if callable(frame_class):
            self._frame = frame_class(self, self, *args)
        else:
            self._frame = frame_class(self, self, *args)

        if hasattr(self._frame, "load_table"):
            try:
                self._frame.load_table()
            except Exception as e:
                print(f"Gagal load_table: {e}")

        self._frame.pack(fill="both", expand=True)

    def show_preview_frame(self, spk_id):
        from spk_preview_frame import SPKPreviewFrame
        self.switch_frame(lambda parent, controller: SPKPreviewFrame(parent, controller, spk_id))


def run_scanner_listener():
    start_all_scanners()


def tampilkan_jadwal_di_tv(root):
    from tv_dashboard import TVLihatJadwal
    tv_window = TVLihatJadwal(root)
    root.tv_window = tv_window
    tv_window.focus_set()

if __name__ == "__main__":
    scanner_thread = threading.Thread(target=run_scanner_listener, daemon=True)
    scanner_thread.start()

    app = App()
    app.mainloop()
