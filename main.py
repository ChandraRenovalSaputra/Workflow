import tkinter as tk
from tkinter import ttk
from ui_login import LoginFrame
from db import create_tables, create_spk_tables  
# from db import tambah_colom_db

create_tables()
create_spk_tables()

def center_window(root, width=1600, height=800):
    """Menempatkan window di tengah layar"""
    # Ambil ukuran layar
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Hitung posisi x dan y untuk menempatkan window di tengah
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    
    # root.geometry(f"{width}x{height}+{x}+{y}")  # Tentukan ukuran dan posisi
    root.geometry(f"1000x800")  
    root.minsize(width, height)  # Set ukuran minimal
    root.configure(bg='white')  # Background putih jika diperlukan

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistem Workflow Percetakan")
        
        # Atur ukuran window dan posisikan di tengah layar
        center_window(self, 1600, 800)
        
        self.resizable(True, True)
        
        create_tables()
        
        self.state("zoomed")  # Untuk fullscreen pada awalnya
        
        self._frame = None
        self.switch_frame(lambda parent, controller: LoginFrame(parent, controller))

    def switch_frame(self, frame_class, *args):
        """Berpindah antar frame"""
        if self._frame is not None:
            self._frame.destroy()

        if args:
            self._frame = frame_class(self, self, *args)
        else:
            self._frame = frame_class(self, self)

        # 🆕 Cek dan panggil load_table jika ada
        if hasattr(self._frame, "load_table"):
            try:
                self._frame.load_table()
            except Exception as e:
                print(f"Gagal load_table: {e}")

        self._frame.pack(fill="both", expand=True)


    def show_preview_frame(self, spk_id):
        """Menampilkan preview SPK"""
        from spk_preview_frame import SPKPreviewFrame
        self.switch_frame(lambda parent, controller: SPKPreviewFrame(parent, controller, spk_id))
        

if __name__ == "__main__":
    # tambah_colom_db()
    app = App()
    app.mainloop()