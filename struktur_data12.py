import heapq
from collections import deque

class Pasien:
    def __init__(self, pid, nama, usia, keluhan=""):
        self.pid = pid
        self.nama = nama
        self.usia = int(usia)
        self.keluhan = keluhan
        self.darurat = False
        self.id_antrean = ""
        self.riwayat = []     # STACK: Catatan rekam medis pasien (Poin 4 Laporan)

class Klinik:
    def __init__(self):
        self.pasien_dict = {}            # HASH TABLE: Data Master Pasien (O(1)) [Poin 1]
        self.antrian_reguler = deque()    # QUEUE: Antrean Reguler (O(1)) [Poin 2]
        self.antrian_prioritas = []       # HEAP: Antrean Prioritas (O(log n)) [Poin 3]

        self.pasien_sekarang = None      # Pasien aktif di ruang dokter

        # COUNTER & BATAS KUOTA HARIAN
        self.nomor_reguler = 1
        self.nomor_prioritas = 1
        self.MAX_KUOTA_REGULER = 30
        self.MAX_KUOTA_PRIORITAS = 10
        self.counter_pid = 1              # COUNTER PID: Agar ID tidak duplikat meski data diubah
        self.total_pasien_dilayani = 0    # COUNTER: Total pasien yang sudah selesai diperiksa hari ini
        self.log_transaksi = deque()      # QUEUE: Log riwayat transaksi pembayaran (O(1) append) [Poin 3.4]


    # FITUR OPERASIONAL KLINIK (MURNI MEMORI RAM)

    # MENU 1: DAFTAR PASIEN BARU + LANGSUNG MASUK ANTREAN
    def daftar_dan_antre(self, nama, usia):
        pid = f"P{self.counter_pid:03d}"  # Pakai counter tersendiri agar ID tidak pernah duplikat
        self.counter_pid += 1
        pasien = Pasien(pid, nama, usia)

        print(f"\n--- Keluhan & Status Urgensi ---")

        # VALIDASI KELUHAN (ANTI KOSONG & ANTI ANGKA MURNI)
        while True:
            keluhan = input(f"Masukkan keluhan untuk {nama}: ").strip()
            if not keluhan:
                print("[X] Input salah! Keluhan tidak boleh kosong.")
            elif keluhan.isdigit():
                print("[X] Input salah! Keluhan medis tidak boleh hanya berupa angka murni.")
            else:
                pasien.keluhan = keluhan
                break

        # Validasi Pilihan Gawat/Darurat (Wajib y/n)
        while True:
            is_darurat_input = input("Apakah kondisi pasien Gawat/Darurat? (y/n): ").lower().strip()
            if is_darurat_input == 'y':
                pasien.darurat = True
                break
            elif is_darurat_input == 'n':
                pasien.darurat = False
                break
            else:
                print("[X] Input salah! Masukkan 'y' untuk Ya, atau 'n' untuk Tidak.")

        # Logika Pengurutan Prioritas (Heap) vs Reguler (Queue) [Poin 2 & 3]
        if pasien.darurat or pasien.usia > 60:
            if self.nomor_prioritas > self.MAX_KUOTA_PRIORITAS:
                print("\n[X] Kuota Antrean Prioritas Penuh!")
                return
            pasien.id_antrean = f"B{self.nomor_prioritas:02d}"

            # Tuple Sorting: (level_prioritas, -usia, nomor_antrean, objek)
            level_prioritas = 0 if pasien.darurat else 1
            heapq.heappush(self.antrian_prioritas, (level_prioritas, -pasien.usia, self.nomor_prioritas, pasien))
            self.nomor_prioritas += 1
        else:
            if self.nomor_reguler > self.MAX_KUOTA_REGULER:
                print("\n[X] Kuota Antrean Reguler Penuh!")
                return
            pasien.id_antrean = f"A{self.nomor_reguler:02d}"
            self.antrian_reguler.append(pasien)
            self.nomor_reguler += 1

        # Simpan ke Master Data (Hash Table) [Poin 1]
        self.pasien_dict[pid] = pasien
        print(f"\n[✓] Sukses! Pasien terdaftar dengan ID: {pid} dan No Antrean: {pasien.id_antrean}")

    # MENU 2: PANGGIL PASIEN BERIKUTNYA
    def panggil_pasien(self):
        if self.pasien_sekarang:
            print(f"\n[!] Peringatan: Selesaikan dulu tindakan untuk pasien saat ini ({self.pasien_sekarang.nama}) sebelum memanggil pasien berikutnya.")
            return

        # Dahulukan heap prioritas baru kemudian reguler queue [Poin 2 & 3]
        if self.antrian_prioritas:
            item = heapq.heappop(self.antrian_prioritas)
            self.pasien_sekarang = item[3]
        elif self.antrian_reguler:
            self.pasien_sekarang = self.antrian_reguler.popleft()
        else:
            print("\n[i] Info: Tidak ada pasien yang sedang mengantre saat ini.")
            return

        print(f"\n>>> PANGGILAN PASIEN NO: {self.pasien_sekarang.id_antrean} <<<")
        print(f"Nama: {self.pasien_sekarang.nama} | Usia: {self.pasien_sekarang.usia} Tahun")
        print(f"Keluhan   : {self.pasien_sekarang.keluhan}")
        print(f"--------------------------------------------------")
        print(f"Silakan pasien masuk ke ruang dokter. Pilih Menu [4] untuk mencatatkan tindakan.")

    # MENU 3: CARI DATA PASIEN + INTEGRASI FITUR UPDATE DATA (Poin 1 Laporan Progres)
    def cari_dan_update_pasien(self, pid):
        if pid in self.pasien_dict:
            pasien = self.pasien_dict[pid]
            print(f"\n=== DATA MASTER PASIEN ===")
            print(f"ID Pasien : {pasien.pid}")
            print(f"Nama      : {pasien.nama}")
            print(f"Usia      : {pasien.usia} Tahun")
            print(f"Status    : Di Ruang Dokter" if self.pasien_sekarang == pasien else f"Status    : Antrean ({pasien.id_antrean})" if pasien.id_antrean else "Status    : Tidak Mengantre")
            print(f"\n--- Riwayat Rekam Medis (Terbaru di atas) ---")
            if not pasien.riwayat:
                print("- Belum ada catatan tindakan -")
            else:
                for i, catatan in enumerate(reversed(pasien.riwayat), 1):
                    print(f" {i}. {catatan}")

            # FITUR UPDATE DATA (MEMENUHI JANJI DI LAPORAN)
            print("\n--------------------------------------------------")
            pilihan_update = input("Apakah Anda ingin memperbarui (update) profil pasien ini? (y/n): ").lower().strip()
            if pilihan_update == 'y':
                # Validasi Nama Baru
                while True:
                    nama_baru = input("Masukkan Nama Baru: ").strip()
                    if not nama_baru:
                        print("[X] Input salah! Nama tidak boleh kosong.")
                    elif not all(char.isalpha() or char.isspace() for char in nama_baru):
                        print("[X] Input salah! Nama hanya boleh berisi huruf dan spasi.")
                    else:
                        pasien.nama = nama_baru
                        break
                # Validasi Usia Baru
                while True:
                    try:
                        usia_baru = int(input("Masukkan Usia Baru: "))
                        if usia_baru <= 0 or usia_baru > 120:
                            print("[X] Input salah! Usia harus berkisar antara 1 sampai 120 tahun.")
                            continue
                        pasien.usia = usia_baru
                        break
                    except ValueError:
                        print("[X] Input salah! Usia harus berupa angka bulat.")

                print(f"\n[✓] Sukses! Data Pasien {pasien.pid} berhasil diperbarui di Hash Table.")
        else:
            print("\n[X] Eror: ID Pasien tidak ditemukan di dalam database.")

    # MENU 4: CATAT TINDAKAN MEDIS [Poin 4]
    def catat_tindakan(self):
        if not self.pasien_sekarang:
            print("\n[X] Eror: Tidak ada pasien aktif di ruang dokter. Panggil pasien dahulu di Menu [2].")
            return

        print(f"\n=== MENCATAT TINDAKAN: {self.pasien_sekarang.nama} ({self.pasien_sekarang.id_antrean}) ===")

        # VALIDASI INPUT TINDAKAN (ANTI KOSONG & ANTI ANGKA MURNI)
        while True:
            tindakan = input("Masukkan tindakan medis / resep obat: ").strip()
            if not tindakan:
                print("[X] Input salah! Catatan tindakan tidak boleh kosong.")
            elif tindakan.isdigit():
                print("[X] Input salah! Tindakan medis tidak boleh hanya berupa angka murni.")
            else:
                break

        # STACK IMPLEMENTATION: Menambahkan data rekam medis dari belakang (O(1)) [Poin 4]
        self.pasien_sekarang.riwayat.append(f"Keluhan: {self.pasien_sekarang.keluhan} -> Tindakan: {tindakan}")
        print(f"\n[✓] Sukses mencatatkan tindakan medis.")

        # Selesai diperiksa, tambah counter & minta input biaya
        self.total_pasien_dilayani += 1

        # INPUT BIAYA & CATAT LOG TRANSAKSI (Poin 3.4)
        while True:
            try:
                biaya = int(input("Masukkan biaya konsultasi (Rp): "))
                if biaya < 0:
                    print("[X] Input salah! Biaya tidak boleh negatif.")
                    continue
                break
            except ValueError:
                print("[X] Input salah! Biaya harus berupa angka.")

        # QUEUE APPEND: Simpan log transaksi ke deque (O(1)) [Poin 3.4]
        log = (f"ID: {self.pasien_sekarang.pid} | Nama: {self.pasien_sekarang.nama} "
               f"| No Antrean: {self.pasien_sekarang.id_antrean} | Biaya: Rp{biaya:,}")
        self.log_transaksi.append(log)
        print(f"[✓] Transaksi dicatat. Total pasien dilayani hari ini: {self.total_pasien_dilayani}")

        # Selesai diperiksa, lepaskan dari ruang dokter
        self.pasien_sekarang.id_antrean = ""
        self.pasien_sekarang = None

    # MENU 5: BATALKAN TINDAKAN TERAKHIR (UNDO) [Poin 4]
    def undo_tindakan(self, pid):
        if pid not in self.pasien_dict:
            print("\n[X] Eror: ID Pasien tidak ditemukan!")
            return

        pasien = self.pasien_dict[pid]
        print(f"\n=== UNDO REKAM MEDIS: {pasien.nama} ===")

        if not pasien.riwayat:
            print("[X] Peringatan: Pasien ini belum memiliki riwayat tindakan untuk dibatalkan.")
        else:
            # STACK POP IMPLEMENTATION: Menghapus data paling atas/terakhir (O(1)) [Poin 4]
            tindakan_dihapus = pasien.riwayat.pop()
            print(f"[✓] Berhasil Membatalkan Tindakan: \n    \"{tindakan_dihapus}\"")

    # MENU 6: TAMPILKAN ANTRIAN SAAT INI [Poin 2 & 3]
    def tampilkan_antrean(self):
        print("\n=== DAFTAR ANTREAN KLINIK SAAT INI ===")

        print("\n[1] ANTREAN PRIORITAS (Min-Heap):")
        if not self.antrian_prioritas:
            print("    - Kosong -")
        else:
            temp_heap = list(self.antrian_prioritas)
            no = 1
            while temp_heap:
                item = heapq.heappop(temp_heap)
                p = item[3]
                print(f"    {no}. No: {p.id_antrean} | {p.nama} ({p.usia} Thn) | Keluhan: {p.keluhan}")
                no += 1

        print("\n[2] ANTREAN REGULER (Queue/Deque):")
        if not self.antrian_reguler:
            print("    - Kosong -")
        else:
            for idx, p in enumerate(self.antrian_reguler, 1):
                print(f"    {idx}. No: {p.id_antrean} | {p.nama} ({p.usia} Thn) | Keluhan: {p.keluhan}")

    # MENU 7: LAPORAN HARIAN [Poin 3.4]
    def laporan_harian(self):
        print("\n=== LAPORAN HARIAN ===")
        print(f"  Total Pasien Dilayani Hari Ini: {self.total_pasien_dilayani} orang")
        print("--------------------------------------------------")
        print("  [1] Daftar Pasien Urutan Alfabetis")
        print("  [2] Daftar Pasien Urutan Nomor ID")
        print("  [3] Riwayat Log Transaksi Pembayaran")
        print("  [0] Kembali ke Menu Utama")
        print("--------------------------------------------------")

        sub = input("Pilih submenu (0-3): ").strip()

        if sub == '1' or sub == '2':
            if not self.pasien_dict:
                print("- Belum ada data pasien hari ini -")
                return
            daftar_laporan = list(self.pasien_dict.values())
            if sub == '1':
                # Timsort O(n log n) berdasarkan nama
                daftar_laporan.sort(key=lambda x: x.nama)
                judul = "URUTAN ALFABETIS"
            else:
                # Timsort O(n log n) berdasarkan nomor ID
                daftar_laporan.sort(key=lambda x: x.pid)
                judul = "URUTAN NOMOR ID"
            print(f"\n=== DAFTAR PASIEN ({judul}) ===")
            print(f"{'ID':<6} | {'Nama Pasien':<20} | {'Usia':<8} | {'Total Tindakan':<15}")
            print("-" * 60)
            for p in daftar_laporan:
                print(f"{p.pid:<6} | {p.nama:<20} | {p.usia:<8} | {len(p.riwayat)} Tindakan")

        elif sub == '3':
            print(f"\n=== LOG TRANSAKSI PEMBAYARAN (Total: {len(self.log_transaksi)}) ===")
            if not self.log_transaksi:
                print("- Belum ada transaksi hari ini -")
            else:
                # Iterasi deque dari depan (urutan masuk pertama)
                for idx, log in enumerate(self.log_transaksi, 1):
                    print(f"  {idx}. {log}")

        elif sub == '0':
            return
        else:
            print("\n[X] Submenu tidak valid!")


# RUNNER SYSTEM (INTERFACE TERPROTEKSI SECARA TOTAL)
if __name__ == '__main__':
    klinik = Klinik()

    # PROTEKSI DARI CONTROL + C (KEYBOARD INTERRUPT)
    try:
        while True:
            # VARIABEL UNTUK REAL-TIME MINI DASHBOARD
            total_prio = len(klinik.antrian_prioritas)
            total_reg = len(klinik.antrian_reguler)
            dokter_aktif = klinik.pasien_sekarang.nama if klinik.pasien_sekarang else "Kosong (Tidak Ada Pasien)"

            # TAMPILAN INTERFACE SESUAI GAMBAR + REAL TIME DASHBOARD STATUS
            print("\n==================================================")
            print("      SISTEM MANAJEMEN KLINIK SEHAT BERSAMA       ")
            print("==================================================")
            print(f" Status Ruangan -> Di Periksa: [{dokter_aktif}]")
            print(f"                   Sisa Antrean: Prioritas ({total_prio}) | Reguler ({total_reg})")
            print("--------------------------------------------------")
            print("   [1] Daftarkan Pasien Baru")
            print("   [2] Panggil Pasien Berikutnya")
            print("   [3] Cari Data Pasien")
            print("   [4] Catat Tindakan Medis")
            print("   [5] Batalkan Tindakan Terakhir (Undo)")
            print("   [6] Tampilkan Antrian Saat Ini")
            print("   [7] Laporan Harian")
            print("   [0] Keluar")
            print("==================================================")

            pilihan = input("Pilih menu (0-7): ").strip()

            if pilihan == '1':
                # VALIDASI DATA NAMA (HANYA BOLEH HURUF & SPASI)
                while True:
                    nama = input("Masukkan nama pasien baru: ").strip()
                    if not nama:
                        print("[X] Input salah! Nama tidak boleh kosong.")
                    elif not all(char.isalpha() or char.isspace() for char in nama):
                        print("[X] Input salah! Nama hanya boleh berisi huruf dan spasi (tanpa angka/simbol).")
                    else:
                        break

                # VALIDASI DATA USIA (ANTI HURUF, MINUS, ATAU UMUR DI LUAR LOGIKA)
                while True:
                    try:
                        usia = int(input("Masukkan usia pasien: "))
                        if usia <= 0 or usia > 120:
                            print("[X] Input salah! Usia harus berkisar antara 1 sampai 120 tahun.")
                            continue
                        break
                    except ValueError:
                        print("[X] Input salah! Usia harus berupa angka bulat.")

                klinik.daftar_dan_antre(nama, usia)

            elif pilihan == '2':
                klinik.panggil_pasien()

            elif pilihan == '3':
                pid = input("Masukkan ID Pasien yang dicari (contoh: P001): ").upper().strip()
                if not pid.startswith('P') or len(pid) != 4 or not pid[1:].isdigit():
                    print("[X] Format salah! ID Pasien harus diawali huruf 'P' dan diikuti 3 angka (Contoh: P001).")
                else:
                    klinik.cari_dan_update_pasien(pid)

            elif pilihan == '4':
                klinik.catat_tindakan()

            elif pilihan == '5':
                pid = input("Masukkan ID Pasien yang akan di-Undo tindakannya: ").upper().strip()
                if not pid.startswith('P') or len(pid) != 4 or not pid[1:].isdigit():
                    print("[X] Format salah! ID Pasien harus diawali huruf 'P' dan diikuti 3 angka (Contoh: P001).")
                else:
                    klinik.undo_tindakan(pid)

            elif pilihan == '6':
                klinik.tampilkan_antrean()

            elif pilihan == '7':
                klinik.laporan_harian()

            elif pilihan == '0':
                # PROTEKSI KELUAR APLIKASI SAAT ANTREAN MASIH ADA
                if klinik.antrian_prioritas or klinik.antrian_reguler or klinik.pasien_sekarang:
                    konfirmasi = input("[!] Peringatan: Masih ada pasien di dalam antrean atau ruang periksa. Yakin ingin keluar? (y/n): ").lower().strip()
                    if konfirmasi != 'y':
                        print("[i] Pembatalan keluar. Kembali ke menu utama.")
                        continue
                print("\nProgram ditutup. Terima kasih!")
                break
            else:
                print("\n[X] Menu tidak valid! Masukkan angka sesuai pilihan (0-7).")

    except KeyboardInterrupt:
        print("\n\n[!] Peringatan: Program ditutup paksa melalui Terminal via shortcut (Ctrl+C). Keluar sistem dengan aman...")