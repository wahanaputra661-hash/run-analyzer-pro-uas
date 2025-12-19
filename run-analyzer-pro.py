import tkinter as tk 
from tkinter import ttk, messagebox
from datetime import datetime, date

THEME = {
    "dark": {"bg":"#1e1e2e","frame":"#2d3047","card":"#3d405b","fg":"white"},
    "light":{"bg":"#f4f4f4","frame":"#ffffff","card":"#e6e6e6","fg":"black"}
}

class RunningApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Run Analyzer Pro")
        self.geometry("700x750")
        self.mode = "dark"
        self.vars = {x: tk.StringVar() for x in ["jarak","waktu","berat","target_jarak"]}
        self.history = {}
        self.daily_targets = {}  # Menyimpan target harian per tanggal
        self.daily_distances = {}  # Menyimpan total jarak harian per tanggal
        self.make_gui()
        self.apply_theme()

    def make_gui(self):
        self.title_lbl = tk.Label(self, text="RUN ANALYZER PRO", font=("Arial",18,"bold"))
        self.title_lbl.pack(pady=20)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both", padx=20, pady=10)
        
        self.tabs = {}
        for name in ["Input","Hasil","Gizi","Jadwal","History"]:
            self.tabs[name] = ttk.Frame(self.notebook)
            self.notebook.add(self.tabs[name], text=name)

        self.make_input_tab()
        tk.Button(self, text="Toggle Theme", command=self.toggle_theme).pack(pady=5)

    def apply_theme(self):
        t = THEME[self.mode]
        self.configure(bg=t["bg"])
        self.title_lbl.configure(bg=t["bg"], fg=t["fg"])
        for tab in self.tabs.values():
            for widget in tab.winfo_children(): 
                widget.destroy()
        self.make_input_tab()
        if hasattr(self, "pace"): 
            self.show_all()

    def toggle_theme(self):
        self.mode = "light" if self.mode=="dark" else "dark"
        self.apply_theme()

    def make_input_tab(self):
        t = THEME[self.mode]
        f = tk.Frame(self.tabs["Input"], bg=t["frame"], padx=25, pady=25)
        f.pack(expand=True, fill="both")

        labels = ["Jarak (km)", "Waktu (menit)", "Berat (kg)", "Target Jarak Harian (km)"]
        keys = ["jarak", "waktu", "berat", "target_jarak"]
        
        for label, key in zip(labels, keys):
            tk.Label(f, text=label, bg=t["frame"], fg=t["fg"]).pack(anchor="w", pady=(5,0))
            tk.Entry(f, textvariable=self.vars[key], font=("Arial",12),
                     bg=t["card"], fg=t["fg"]).pack(fill="x", pady=3)

        tk.Button(f, text="Analisis", command=self.analyze,
                  bg="#ff6b6b", fg="white", font=("Arial",11,"bold"),
                  pady=8).pack(fill="x", pady=20)

    def analyze(self):
        try:
            j = float(self.vars["jarak"].get())
            w = float(self.vars["waktu"].get())
            b = float(self.vars["berat"].get())
            t = float(self.vars["target_jarak"].get()) if self.vars["target_jarak"].get().strip() else None
            if min(j,w,b) <= 0: raise ValueError
            if t is not None and t <= 0: raise ValueError
        except:
            return messagebox.showerror("Error","Input tidak valid!")
        
        today = date.today().strftime("%Y-%m-%d")
        self.pace = w/j
        self.speed = (j/w)*60
        self.kal = j*b*1.036
        
        # Simpan target harian jika ada input target
        if t is not None:
            self.daily_targets[today] = t
            self.target_jarak = t
        else:
            # Gunakan target terakhir jika ada, atau gunakan target saat ini
            if today in self.daily_targets:
                self.target_jarak = self.daily_targets[today]
            elif hasattr(self, 'target_jarak'):
                self.daily_targets[today] = self.target_jarak
            else:
                self.target_jarak = 0
        
        # Akumulasi jarak harian
        if today not in self.daily_distances:
            self.daily_distances[today] = 0
        self.daily_distances[today] += j
        
        # Hitung total jarak hari ini
        total_jarak_hari_ini = self.daily_distances[today]
        
        if today not in self.history:
            self.history[today] = []
        
        self.history[today].append({
            "time": datetime.now().strftime("%H:%M"),
            "jarak": j,
            "waktu": w,
            "pace": self.pace,
            "speed": self.speed,
            "kal": self.kal,
            "target": self.target_jarak,
            "total_jarak_harian": total_jarak_hari_ini
        })
        
        self.show_all()
        self.notebook.select(1)

    def show_all(self):
        self.show_hasil()
        self.show_gizi()
        self.show_jadwal()
        self.show_history()

    def show_hasil(self):
        t = THEME[self.mode]
        tab = self.tabs["Hasil"]
        for w in tab.winfo_children(): w.destroy()
        
        f = tk.Frame(tab, bg=t["frame"], padx=25, pady=25)
        f.pack(fill="both", expand=True)
        
        tk.Label(f, text="HASIL ANALISIS", bg=t["frame"],
                 fg="#ffd166", font=("Arial",14,"bold")).pack(pady=(0,20))
        
        data = [
            ("Pace", f"{self.pace:.2f} menit/km"),
            ("Kecepatan", f"{self.speed:.1f} km/jam"),
            ("Kalori Terbakar", f"{self.kal:.0f} kalori")
        ]
        
        for label, value in data:
            frame = tk.Frame(f, bg=t["card"], padx=15, pady=10)
            frame.pack(fill="x", pady=5)
            tk.Label(frame, text=label, bg=t["card"], fg=t["fg"],
                     font=("Arial",11)).pack(side="left")
            tk.Label(frame, text=value, bg=t["card"], fg="#4ecdc4",
                     font=("Arial",11,"bold")).pack(side="right")

    def show_gizi(self):
        t = THEME[self.mode]
        tab = self.tabs["Gizi"]
        for w in tab.winfo_children(): w.destroy()
        
        # Buat main frame dengan scrollbar
        main_frame = tk.Frame(tab, bg=t["frame"])
        main_frame.pack(fill="both", expand=True)
        
        # Buat canvas untuk scroll dengan width yang cukup
        canvas = tk.Canvas(main_frame, bg=t["frame"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=t["frame"], width=650)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas dan scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=(25,0), pady=25)
        scrollbar.pack(side="right", fill="y", pady=25)
        
        # Bind mouse wheel untuk scroll
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Kontainer utama untuk konten di tengah
        container = tk.Frame(scrollable_frame, bg=t["frame"])
        container.pack(expand=True, fill="both", padx=20, pady=10)
        
        # Judul di tengah
        tk.Label(container, text="PROGRES & NUTRISI", bg=t["frame"],
                 fg="#ffd166", font=("Arial",14,"bold")).pack(pady=(0,25))
        
        if hasattr(self, 'target_jarak') and self.target_jarak > 0:
            today = date.today().strftime("%Y-%m-%d")
            
            # Gunakan target terbaru untuk hari ini
            current_target = self.daily_targets.get(today, self.target_jarak)
            
            # Hitung total jarak hari ini
            total_jarak_hari_ini = self.daily_distances.get(today, 0)
            
            # Ambil data dari input terbaru
            jarak_sekarang = float(self.vars["jarak"].get())
            
            # Hitung progress berdasarkan akumulasi
            sisa_jarak = current_target - total_jarak_hari_ini
            persentase = (total_jarak_hari_ini / current_target) * 100 if current_target > 0 else 0
            
            # Container untuk progres target (di tengah)
            progress_container = tk.Frame(container, bg=t["frame"])
            progress_container.pack(fill="x", pady=(0,20))
            
            # Judul progres di tengah
            tk.Label(progress_container, text="PROGRES TARGET LARI HARIAN", bg=t["frame"],
                     fg=t["fg"], font=("Arial",12,"bold")).pack(pady=(0,15))
            
            # Data progres dengan layout terpusat
            data_progres = [
                ("Target Harian", f"{current_target:.1f} km"),
                ("Jarak Hari Ini", f"{total_jarak_hari_ini:.1f} km"),
                ("Sisa Jarak", f"{abs(sisa_jarak):.2f} km"),
                ("Persentase", f"{persentase:.1f}%")
            ]
            
            # Frame untuk grid data progres
            progress_grid = tk.Frame(progress_container, bg=t["frame"])
            progress_grid.pack()
            
            for i, (label, value) in enumerate(data_progres):
                row_frame = tk.Frame(progress_grid, bg=t["card"], padx=25, pady=12)
                row_frame.grid(row=i, column=0, sticky="ew", pady=3, padx=50)
                
                # Label
                tk.Label(row_frame, text=label, bg=t["card"], fg=t["fg"],
                         font=("Arial",11), width=20, anchor="center").pack(side="left", expand=True)
                
                # Separator
                tk.Label(row_frame, text=":", bg=t["card"], fg=t["fg"],
                         font=("Arial",11), padx=10).pack(side="left")
                
                # Value
                tk.Label(row_frame, text=value, bg=t["card"], fg="#4ecdc4",
                         font=("Arial",11,"bold"), width=15, anchor="center").pack(side="left", expand=True)
            
            # Status target di tengah
            status_container = tk.Frame(container, bg=t["card"], padx=30, pady=15)
            status_container.pack(fill="x", pady=15, padx=80)
            
            if sisa_jarak <= 0:
                tk.Label(status_container, text="🎯 TARGET HARIAN TERCAPAI!", bg=t["card"], fg="#4ecdc4",
                         font=("Arial",12,"bold")).pack()
                tk.Label(status_container, text=f"Total lari hari ini: {total_jarak_hari_ini:.1f} km (Target: {current_target:.1f} km)", 
                         bg=t["card"], fg="#4ecdc4", font=("Arial",10)).pack(pady=(5,0))
                
                # Pesan khusus jika melebihi target
                if total_jarak_hari_ini > current_target:
                    excess = total_jarak_hari_ini - current_target
                    tk.Label(status_container, text=f"⭐ Anda telah melewati target harian sebesar {excess:.1f} km!",
                             bg=t["card"], fg="#ffd166", font=("Arial",10, "bold")).pack(pady=(5,0))
            else:
                tk.Label(status_container, text="📊 BELUM TERCAPAI", bg=t["card"], fg="#ff6b6b",
                         font=("Arial",12,"bold")).pack()
                tk.Label(status_container, text=f"Kurang {sisa_jarak:.2f} km untuk capai target harian", 
                         bg=t["card"], fg="#ff6b6b", font=("Arial",10)).pack(pady=(5,0))
                tk.Label(status_container, text=f"Progress: {persentase:.1f}% dari {current_target:.1f} km",
                         bg=t["card"], fg="#888", font=("Arial",9)).pack(pady=(2,0))
            
            # Kalori terbakar di tengah
            tk.Label(container, text="KALORI TERBAKAR", bg=t["frame"],
                     fg=t["fg"], font=("Arial",12,"bold")).pack(pady=(20,10))
            
            kal_container = tk.Frame(container, bg=t["card"], padx=30, pady=15)
            kal_container.pack(fill="x", pady=5, padx=150)
            tk.Label(kal_container, text=f"{self.kal:.0f} kalori", bg=t["card"], fg="#ff6b6b",
                     font=("Arial",14,"bold")).pack()
            
            # Informasi input terbaru
            info_frame = tk.Frame(container, bg=t["card"], padx=15, pady=10)
            info_frame.pack(fill="x", pady=10, padx=80)
            tk.Label(info_frame, text=f"Input terbaru: {jarak_sekarang:.1f} km pada {datetime.now().strftime('%H:%M')}",
                     bg=t["card"], fg="#888", font=("Arial",9)).pack()
            
            # Rekomendasi makanan fokus protein & karbohidrat
            tk.Label(container, text="REKOMENDASI NUTRISI", bg=t["frame"],
                     fg=t["fg"], font=("Arial",12,"bold")).pack(pady=(25,15))
            
            makanan = [
                ("Dada Ayam (100g)", "31g protein", "Protein tinggi, rendah lemak"),
                ("Telur (2 butir)", "13g protein", "Protein lengkap, mudah dicerna"),
                ("Salmon (100g)", "25g protein", "Protein + Omega-3"),
                ("Tahu (100g)", "8g protein", "Protein nabati"),
                ("Nasi Merah (100g)", "23g karbo", "Karbohidrat kompleks"),
                ("Oatmeal (50g)", "30g karbo", "Serat tinggi, energi tahan lama"),
                ("Ubi (100g)", "20g karbo", "Vitamin A, karbo sehat"),
                ("Pisang (1 buah)", "27g karbo", "Kalium, energi cepat")
            ]
            
            # Frame untuk makanan yang terpusat
            makanan_container = tk.Frame(container, bg=t["frame"])
            makanan_container.pack(fill="x", padx=50)
            
            for i, (nama, nutrisi, desc) in enumerate(makanan):
                frame = tk.Frame(makanan_container, bg=t["card"], padx=15, pady=10)
                frame.pack(fill="x", pady=4)
                
                # Container untuk konten makanan
                content_frame = tk.Frame(frame, bg=t["card"])
                content_frame.pack(expand=True)
                
                # Nama makanan (di tengah)
                tk.Label(content_frame, text=nama, bg=t["card"], fg=t["fg"],
                         font=("Arial",10,"bold"), width=25).pack(pady=(0,5))
                
                # Nutrisi dan deskripsi
                nutrisi_frame = tk.Frame(content_frame, bg=t["card"])
                nutrisi_frame.pack()
                
                tk.Label(nutrisi_frame, text=nutrisi, bg=t["card"], fg="#ff6b6b",
                         font=("Arial",9,"bold"), width=20).pack(side="left", padx=(0,10))
                
                tk.Label(nutrisi_frame, text=desc, bg=t["card"], fg="#888",
                         font=("Arial",9), wraplength=200, justify="center").pack(side="left")
            
            # Tips nutrisi singkat
            tk.Label(container, text="TIPS CEPAT", bg=t["frame"],
                     fg=t["fg"], font=("Arial",12,"bold")).pack(pady=(25,10))
            
            tips = [
                "Protein dalam 30 menit setelah lari",
                "Minum air 500ml setiap 30 menit lari",
                "Karbohidrat kompleks sebelum lari",
                "Hindari makanan berat 2 jam sebelum lari"
            ]
            
            tips_container = tk.Frame(container, bg=t["frame"])
            tips_container.pack(fill="x", padx=100)
            
            for tip in tips:
                frame = tk.Frame(tips_container, bg=t["card"], padx=15, pady=8)
                frame.pack(fill="x", pady=3)
                tk.Label(frame, text=f"✓ {tip}", bg=t["card"], fg="#4ecdc4",
                         font=("Arial",9)).pack(anchor="center")
        else:
            # Pesan jika tidak ada target
            message_frame = tk.Frame(container, bg=t["frame"], padx=20, pady=40)
            message_frame.pack(expand=True, fill="both")
            tk.Label(message_frame, text="Masukkan target jarak harian di tab Input", 
                     bg=t["frame"], fg=t["fg"], font=("Arial",11)).pack(expand=True)
            tk.Label(message_frame, text="Target akan digunakan untuk menghitung progres harian", 
                     bg=t["frame"], fg="#888", font=("Arial",9)).pack()

    def show_jadwal(self):
        t = THEME[self.mode]
        tab = self.tabs["Jadwal"]
        for w in tab.winfo_children(): w.destroy()
        
        f = tk.Frame(tab, bg=t["frame"], padx=25, pady=25)
        f.pack(fill="both", expand=True)
        
        tk.Label(f, text="JADWAL LATIHAN", bg=t["frame"],
                 fg="#ffd166", font=("Arial",14,"bold")).pack(pady=(0,20))
        
        hari = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
        jadwal = [
            ("Lari Ringan", "30 menit", "Pemanasan"),
            ("Interval Run", "45 menit", "Kecepatan"),
            ("Recovery", "20 menit", "Pemulihan"),
            ("Long Run", "60 menit", "Daya tahan"),
            ("Cross Training", "40 menit", "Variasi"),
            ("Tempo Run", "50 menit", "Konsistensi"),
            ("Rest Day", "-", "Pemulihan total")
        ]
        
        for i, (latihan, durasi, tipe) in enumerate(jadwal):
            frame = tk.Frame(f, bg=t["card"], padx=15, pady=10)
            frame.pack(fill="x", pady=4)
            
            # Hari
            tk.Label(frame, text=hari[i], bg=t["card"], fg=t["fg"],
                     font=("Arial",11,"bold"), width=8).pack(side="left", padx=(0,10))
            
            # Latihan
            tk.Label(frame, text=latihan, bg=t["card"], fg="#4ecdc4",
                     font=("Arial",11,"bold"), width=15).pack(side="left", padx=(0,10))
            
            # Durasi & Tipe
            tk.Label(frame, text=f"{durasi} | {tipe}", bg=t["card"], fg=t["fg"],
                     font=("Arial",10)).pack(side="left")
            
            # Indikator
            color = "#ff6b6b" if i % 3 == 0 else "#4ecdc4" if i % 3 == 1 else "#ffd166"
            tk.Label(frame, text="●", bg=t["card"], fg=color,
                     font=("Arial",12)).pack(side="right")

    def show_history(self):
        t = THEME[self.mode]
        tab = self.tabs["History"]
        for w in tab.winfo_children(): w.destroy()

        f = tk.Frame(tab, bg=t["frame"], padx=25, pady=25)
        f.pack(fill="both", expand=True)
        
        tk.Label(f, text="Riwayat Analisis", bg=t["frame"],
                 fg="#ffd166", font=("Arial",14,"bold")).pack(pady=(0,20))
        
        if not self.history:
            tk.Label(f, text="Belum ada riwayat", fg=t["fg"], bg=t["frame"]).pack()
            return

        dates_frame = tk.Frame(f, bg=t["frame"])
        dates_frame.pack(anchor="center")

        row_frame = None
        for i, tanggal in enumerate(sorted(self.history.keys(), reverse=True)):
            if i % 3 == 0:
                row_frame = tk.Frame(dates_frame, bg=t["frame"])
                row_frame.pack(anchor="center", pady=6)

            btn = tk.Button(
                row_frame, text=tanggal,
                command=lambda tgl=tanggal: self.show_date_detail(tgl),
                bg=t["card"], fg=t["fg"], font=("Arial",10),
                relief="flat", padx=18, pady=8, cursor="hand2"
            )
            btn.pack(side="left", padx=6)

            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#444444" if self.mode=="dark" else "#dddddd"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=t["card"]))

    def show_date_detail(self, tanggal):
        detail = tk.Toplevel(self)
        detail.title(f"Detail {tanggal}")
        detail.geometry("600x450")
        t = THEME[self.mode]
        detail.configure(bg=t["bg"])

        # Frame utama untuk center
        main_frame = tk.Frame(detail, bg=t["bg"])
        main_frame.pack(expand=True, fill="both")

        # Title di tengah
        tk.Label(main_frame, text=f"Detail Tanggal {tanggal}", bg=t["bg"], fg="#ffd166",
                 font=("Arial",14,"bold")).pack(pady=15)

        # Frame untuk konten history yang di-center
        center_frame = tk.Frame(main_frame, bg=t["bg"])
        center_frame.pack(expand=True)

        # Container untuk data history
        container = tk.Frame(center_frame, bg=t["frame"], padx=20, pady=20)
        container.pack()

        # Tampilkan target harian untuk tanggal tersebut
        target_harian = self.daily_targets.get(tanggal, "Tidak ada target")
        total_jarak = self.daily_distances.get(tanggal, 0)
        
        target_frame = tk.Frame(container, bg=t["card"], padx=10, pady=8)
        target_frame.pack(fill="x", pady=5)
        tk.Label(target_frame, text=f"Target Harian: {target_harian} km | Total Jarak: {total_jarak:.1f} km", 
                 bg=t["card"], fg=t["fg"], font=("Arial",10, "bold")).pack()
        
        for item in self.history[tanggal]:
            row_frame = tk.Frame(container, bg=t["card"], padx=10, pady=8)
            row_frame.pack(fill="x", pady=4)

            info = f"{item['time']} | {item['jarak']}km | {item['waktu']}m | Pace {item['pace']:.2f} | {item['kal']:.0f} cal"
            
            label = tk.Label(row_frame, text=info, bg=t["card"], fg=t["fg"],
                     font=("Arial",10))
            label.pack(expand=True)

RunningApp().mainloop()