# backup_db.py
import os
import sqlite3
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler


class BackupManager:
    def __init__(self, databases):
        """
        databases: List of tuples (db_path, backup_dir)
        Contoh: [("workflow.db", "backups/workflow"), ("users.db", "backups/users")]
        """
        self.scheduler = BackgroundScheduler(daemon=True)
        self.databases = databases
        self._setup_jobs()

    def _setup_jobs(self):
        """Menyiapkan jadwal backup untuk semua database"""
        for db_path, backup_dir in self.databases:
            self.scheduler.add_job(
                self._perform_backup,
                "cron",
                hour=22,
                minute=0,
                args=[db_path, backup_dir],
                id=f"backup_{db_path}",
                max_instances=1,
                misfire_grace_time=60,
            )

    def _perform_backup(self, db_path, backup_dir):
        """Eksekusi backup dengan error handling"""
        src = None
        dst = None
        try:
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
            db_name = os.path.splitext(os.path.basename(db_path))[0]
            backup_path = os.path.join(backup_dir, f"{db_name}_{timestamp}.db")

            src = sqlite3.connect(db_path)
            dst = sqlite3.connect(backup_path)

            with dst:
                src.backup(dst, pages=1)

            print(f"Backup berhasil: {db_path} -> {backup_path}")
            return True

        except Exception as e:
            print(f"Backup gagal untuk {db_path}: {str(e)}")
            # Hapus temporary file jika ada error
            return False
        finally:
            if src:
                src.close()
            if dst:
                dst.close()

    def start(self):
        """Mulai jadwal backup"""
        if not self.scheduler.running:
            self.scheduler.start()
            print("Backup scheduler started")

    def shutdown(self):
        """Hentikan jadwal backup"""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            print("Backup scheduler stopped")
