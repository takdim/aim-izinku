# Izin Monitor Unhas (Aplikasi Pemantauan Izin Pegawai)

Aplikasi web internal untuk mengelola dan memantau izin pegawai, termasuk izin keluar sementara pada jam kerja, dengan persetujuan atasan dan bukti kehadiran di lokasi saat pegawai kembali. Berjalan di jaringan lokal kampus pendamping **Unhas Ontime** (non-API).

---

## 🚀 Fitur Utama Sesuai PRD & Desain

1. **Autentikasi & Multi-Peran**:
   - Pegawai (mengajukan izin, konfirmasi kepulangan dengan bukti foto, melihat riwayat).
   - Atasan / Pimpinan (dashboard pemantauan real-time, menyetujui/menolak izin dengan catatan, audit bukti, putusan pengecualian).
   - Admin (kelola akun & struktur atasan, konfigurasi subnet IP kantor, audit log, ekspor rekap).

2. **Alur Izin Keluar Sementara**:
   - `Diajukan` &rarr; `Disetujui` &rarr; `Sedang di Luar` &rarr; `Selesai`.
   - Otomatis berpindah status `sedang_di_luar` saat jam berangkat tiba.
   - Otomatis menandai `terlambat_kembali` jika melewati jam pulang tanpa konfirmasi.

3. **Verifikasi Kehadiran Fisik (Kamera & Subnet IP)**:
   - Validasi subnet IP jaringan kantor (FR-14a).
   - Pengambilan bukti langsung lewat kamera browser (WebRTC) dengan watermark terkunci (waktu server, IP, no. tiket).
   - Kompresi gambar otomatis target &le; 500 KB (FR-18).

4. **Jalur Pengecualian & Perpanjangan**:
   - Jalur penutupan izin tanpa bukti fisik bila terjadi kendala khusus (FR-21, FR-22).
   - Pengajuan perpanjangan jam pulang saat sedang di luar (FR-19).

5. **Dashboard Pemantauan & Rekap**:
   - 4 Kartu KPI: Sedang Izin Harian, Sedang di Luar, Terlambat Kembali, Menunggu Persetujuan.
   - Tabel pemantauan pegawai real-time dengan sinkronisasi auto-refresh 30 detik.
   - Ekspor rekap bulanan ke format CSV (FR-27).

---

## 🛠️ Teknologi & Stack

- **Backend**: Python 3 (Flask, SQLAlchemy, Flask-Login, PyMySQL, Werkzeug, Pillow, APScheduler)
- **Basis Data**: MySQL (Database: `aim_izinku`)
- **Frontend**: HTML5, Tailwind CSS, Google Fonts (*Plus Jakarta Sans* & *Inter*), Material Symbols Outlined
- **Lingkungan**: Virtual Environment (`venv`), `.env`

---

## ⚙️ Persiapan & Menjalankan Aplikasi

### 1. Aktifkan Virtual Environment
```bash
source venv/bin/activate
```

### 2. Konfigurasi `.env`
Salin template `.env.example` ke `.env` dan sesuaikan kredensial MySQL Anda:
```env
SECRET_KEY=change-this-to-a-secure-random-key
DATABASE_URL=mysql+pymysql://<user>:<password>@localhost:3306/aim_izinku
PORT=5002
OFFICE_SUBNETS=10.15.22.0/24,127.0.0.1,::1,192.168.0.0/16,10.0.0.0/8
DEV_BYPASS_IP_CHECK=true
```

### 3. Migrasi & Seeding Data Awal
Untuk membuat tabel dan mengisi data awal akun & jenis izin:
```bash
python seed.py
```

### 4. Jalankan Server
```bash
python run.py
```
Buka browser pada: `http://127.0.0.1:5002`

---

## 🔑 Daftar Akun Pengguna

| Peran | Nama | NIP / Username | Password | Keterangan |
|---|---|---|---|---|
| **Pegawai** | Faisal Basri, A.Md. | `199402282020121004` | `password123` | Teknisi Jaringan FT (punya izin aktif di luar) |
| **Pegawai 2** | Nurul Fadhilah, S.T. | `199605142022032008` | `password123` | Staf TU (pengajuan menunggu persetujuan) |
| **Pegawai 3** | Andi Muhammad Ilham, S.Kom. | `199108172019031005` | `password123` | Staf Lab Komputasi (status terlambat kembali) |
| **Atasan** | Prof. Dr. Ir. H. Mursalim, M.T. | `196510121991031002` | `password123` | Dekan Fakultas Teknik (Pimpinan) |
| **Admin** | Admin Kepegawaian FT | `198801012010121001` | `admin123` | Administrator Sistem Presensi & TI |