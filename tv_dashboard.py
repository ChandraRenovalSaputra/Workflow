import tkinter as tk
from lihat_jadwal_frame import LihatJadwalFrame

class TVLihatJadwal(tk.Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.title("Lihat Jadwal SPK - TV Monitor")
        self.state("zoomed")
        self.configure(bg="#ecf0f1")
        
        # Frame utama tanpa judul tambahan
        self.main_frame = tk.Frame(self, bg="#ecf0f1")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Inisialisasi frame jadwal langsung
        self.jadwal_frame = LihatJadwalFrame(
            parent=self.main_frame, 
            controller=root, 
            readonly=True
        )
        self.jadwal_frame.pack(fill="both", expand=True)
        
        # Inisialisasi variabel yang diperlukan untuk menghindari error
        if not hasattr(self.jadwal_frame, 'search_var'):
            self.jadwal_frame.search_var = tk.StringVar()
        if not hasattr(self.jadwal_frame, 'filter_var'):
            self.jadwal_frame.filter_var = tk.StringVar()
            self.jadwal_frame.filter_var.set("semua")
        
        # Load data pertama kali
        self.load_initial_data()
        
        # Setup auto refresh dan scroll
        self.setup_auto_features()
        
        self.bind("<Escape>", self.keluar_fullscreen)

    def load_initial_data(self):
        """Memuat data pertama kali dengan error handling"""
        try:
            self.jadwal_frame.load_table()
            self.after(100, self.configure_font_sizes)  # Delay untuk render
        except Exception as e:
            print(f"Gagal memuat data awal: {e}")
            self.after(1000, self.load_initial_data)  # Coba lagi setelah 1 detik

    def setup_auto_features(self):
        """Mengatur fitur otomatis"""
        # Auto refresh yang aman
        self.after(10000, self.safe_auto_refresh)
        
        # Auto scroll
        self.scroll_direction = 1
        self.after(2000, self.auto_scroll)

    def safe_auto_refresh(self):
        """Refresh data dengan penanganan error"""
        try:
            self.jadwal_frame.load_table()
        except Exception as e:
            print(f"Error saat auto-refresh: {e}")
        finally:
            self.after(10000, self.safe_auto_refresh)

    def auto_scroll(self):
        """Scroll otomatis dengan penanganan error"""
        try:
            if hasattr(self.jadwal_frame, 'scrollable'):
                canvas = self.jadwal_frame.scrollable.canvas
                canvas.yview_scroll(self.scroll_direction, "units")
                
                # Balik arah scroll jika mencapai batas
                pos = canvas.yview()
                if pos[1] >= 1.0:
                    self.scroll_direction = -1
                elif pos[0] <= 0.0:
                    self.scroll_direction = 1
        except Exception as e:
            print(f"Error auto-scroll: {e}")
        finally:
            self.after(5000, self.auto_scroll)

    def configure_font_sizes(self):
        """Menyesuaikan ukuran font untuk TV"""
        try:
            if hasattr(self.jadwal_frame, 'table_frame'):
                for widget in self.jadwal_frame.table_frame.winfo_children():
                    if isinstance(widget, tk.Label):
                        current_font = widget.cget("font")
                        if widget.cget("text") in getattr(self.jadwal_frame, 'headers', []):
                            widget.configure(font=("Segoe UI", 18, "bold"))
                        else:
                            widget.configure(font=("Segoe UI", 16))
        except Exception as e:
            print(f"Error mengatur font: {e}")

    def keluar_fullscreen(self, event=None):
        """Keluar dari mode TV"""
        self.root.tv_window = None
        self.destroy()