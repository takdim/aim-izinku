# PRD: Aplikasi Pemantauan Izin Pegawai

| | |
|---|---|
| **Nama kerja** | Izin Monitor (sementara, bisa diganti) |
| **Versi dokumen** | 0.1 (draf) |
| **Tanggal** | 3 November 2026 |
| **Penulis** | Muhammad Takdim |
| **Status** | Draf untuk didiskusikan |

---

## 1. Ringkasan

Aplikasi web internal untuk mengelola dan memantau izin pegawai, termasuk izin keluar sementara pada jam kerja, dengan persetujuan atasan dan bukti kehadiran di lokasi saat pegawai kembali. Aplikasi berjalan di jaringan lokal kantor dan **tidak menangani absensi**, karena absensi sudah dilakukan melalui Unhas Ontime.

## 2. Latar Belakang dan Masalah

- Absensi masuk dan pulang sudah ditangani Unhas Ontime.
- Masalah yang muncul: pegawai absen datang lalu meninggalkan kantor, dan tidak ada catatan ke mana serta berapa lama.
- Unhas Ontime **tidak memiliki API**, sehingga integrasi otomatis tidak memungkinkan.
- Pelacakan lokasi (GPS) dinilai tidak perlu dan berisiko pada privasi. Pendekatan yang dipilih adalah **izin yang tercatat, disetujui, dan dibuktikan**.

## 3. Tujuan dan Non-Tujuan

### Tujuan
1. Semua kepergian pegawai pada jam kerja tercatat sebagai izin yang disetujui atasan.
2. Pimpinan dapat melihat secara langsung siapa yang sedang izin atau di luar kantor.
3. Setiap izin keluar diakhiri dengan bukti keberadaan di lokasi, sehingga prosesnya transparan.
4. Menyediakan rekap izin per pegawai dan per periode untuk keperluan evaluasi.

### Non-Tujuan (di luar cakupan)
- Pencatatan absensi masuk dan pulang (tetap di Unhas Ontime).
- Pelacakan lokasi real-time atau latar belakang.
- Integrasi otomatis dengan Unhas Ontime (belum ada API).
- Aplikasi mobile native.
- Penghitungan gaji atau tunjangan kinerja.

## 4. Pengguna dan Peran

| Peran | Deskripsi | Hak utama |
|---|---|---|
| **Pegawai** | Pengguna umum | Mengajukan izin, melihat status, menyelesaikan izin keluar dengan bukti, melihat riwayat sendiri |
| **Atasan / Pimpinan** | Menyetujui izin bawahan | Menyetujui atau menolak, memantau dashboard bawahan, membuka bukti, memutuskan pengecualian |
| **Admin** | Pengelola sistem | Kelola pengguna, struktur atasan, jenis izin, pengaturan, dan laporan menyeluruh |

## 5. Ruang Lingkup MVP

1. Login dan manajemen pengguna
2. Pengajuan izin (berhari-hari) dan izin keluar sementara (dalam jam kerja)
3. Persetujuan atau penolakan oleh atasan
4. Penyelesaian izin keluar: tombol "sudah kembali" + unggah bukti
5. Dashboard pemantauan untuk atasan
6. Notifikasi di dalam aplikasi
7. Rekap dan ekspor laporan
8. Jalur pengecualian bila bukti tidak dapat diunggah

## 6. Alur Utama Izin Keluar Sementara

```
Diajukan -> Disetujui -> Sedang di luar -> Selesai
    |                          |
    +-> Ditolak                +-> Terlambat kembali -> Selesai (terlambat)
```

1. **Pengajuan.** Pegawai mengisi jenis izin, alasan, jam pergi, dan jam pulang yang direncanakan.
2. **Persetujuan.** Atasan menyetujui atau menolak dengan catatan.
3. **Sedang di luar.** Status aktif otomatis pada jam pergi dan tampil di dashboard.
4. **Kembali.** Pegawai menekan "sudah kembali" dan mengunggah bukti. Tombol hanya aktif bila perangkat terhubung ke jaringan kantor dan bukti sudah terunggah.
5. **Selesai.** Izin ditutup dan tersimpan sebagai arsip.
6. **Terlambat kembali.** Bila melewati jam pulang tanpa penutupan, sistem menandai otomatis. Setelah pegawai kembali, izin ditutup dengan label "terlambat".
7. **Perpanjangan.** Selama status "sedang di luar", pegawai dapat mengajukan perpanjangan jam pulang yang perlu disetujui atasan.

## 7. Kebutuhan Fungsional

### 7.1 Autentikasi dan Pengguna
- **FR-01** Pengguna login dengan akun (NIP/username dan kata sandi).
- **FR-02** Admin mengelola akun, peran, dan relasi atasan-bawahan.
- **FR-03** Kata sandi disimpan dalam bentuk hash.

### 7.2 Pengajuan Izin
- **FR-04** Pegawai dapat mengajukan izin dengan jenis: sakit, cuti, dinas luar, keperluan pribadi.
- **FR-05** Izin harian memuat tanggal mulai, tanggal selesai, alasan, dan lampiran opsional (mis. surat dokter).
- **FR-06** Izin keluar sementara memuat tanggal, jam pergi, jam pulang rencana, tujuan, dan alasan.
- **FR-07** Pegawai dapat membatalkan pengajuan yang belum disetujui.
- **FR-08** Sistem menolak pengajuan yang jam pulangnya lebih awal dari jam pergi atau di luar jam kerja.

### 7.3 Persetujuan
- **FR-09** Atasan melihat daftar pengajuan yang menunggu, dengan filter dan pencarian.
- **FR-10** Atasan menyetujui atau menolak, dengan catatan (wajib saat menolak).
- **FR-11** Pegawai menerima notifikasi perubahan status.
- **FR-12** Seluruh keputusan tercatat beserta waktu dan pelakunya.

### 7.4 Penyelesaian Izin Keluar dan Bukti
- **FR-13** Status "sedang di luar" aktif otomatis pada jam pergi untuk izin yang disetujui.
- **FR-14** Tombol "sudah kembali" hanya aktif bila: (a) perangkat berada di jaringan kantor (cek rentang IP), dan (b) bukti sudah diunggah.
- **FR-15** Bukti **wajib untuk semua jenis izin keluar**.
- **FR-16** Jenis bukti yang diterima ditampilkan sesuai jenis izin (foto di lokasi, surat tugas/undangan, kuitansi/nomor antrean, surat keterangan).
- **FR-17** Foto sebaiknya diambil langsung dari kamera browser. Waktu bukti memakai **waktu server saat unggah**, bukan metadata berkas.
- **FR-18** Bukti dikompres otomatis (target sekitar 500 KB per berkas) dengan batas ukuran dan tipe berkas yang jelas.
- **FR-19** Pegawai dapat mengajukan perpanjangan jam pulang selama status "sedang di luar".
- **FR-20** Sistem menandai izin "terlambat kembali" secara otomatis saat jam pulang terlewati.

### 7.5 Jalur Pengecualian
- **FR-21** Bila bukti tidak dapat diunggah, pegawai dapat menutup izin dengan menulis alasan.
- **FR-22** Pengecualian harus diputuskan atasan (diterima atau ditolak). Hasilnya tercatat dan tampil di rekap.

### 7.6 Dashboard Pemantauan
- **FR-23** Atasan melihat ringkasan real-time: sedang izin, sedang di luar kantor, terlambat kembali, menunggu persetujuan.
- **FR-24** Atasan dapat membuka detail izin dan bukti (arsip), tanpa kewajiban memeriksa semuanya.
- **FR-25** Admin melihat dashboard seluruh unit.

### 7.7 Laporan
- **FR-26** Rekap bulanan per pegawai: jumlah izin per jenis, total jam di luar, jumlah keterlambatan, jumlah pengecualian.
- **FR-27** Ekspor laporan ke Excel/CSV dan PDF.
- **FR-28** Fitur impor rekap Unhas Ontime (CSV/Excel) untuk pencocokan ditempatkan di **fase 2** (lihat bagian 13).

### 7.8 Notifikasi
- **FR-29** Notifikasi dalam aplikasi untuk: pengajuan baru, keputusan atasan, pengingat jam pulang mendekat, dan keterlambatan.

## 8. Aturan Bisnis

1. Setiap keluar kantor pada jam kerja wajib punya izin keluar yang disetujui sebelum jam pergi.
2. Bukti wajib untuk seluruh izin keluar demi transparansi.
3. Izin yang tidak ditutup melewati jam pulang otomatis berstatus "terlambat kembali".
4. Bukti disimpan selama periode yang ditentukan (usulan: 1 tahun), lalu dihapus otomatis. Rekap tetap tersimpan.
5. Atasan hanya dapat melihat dan memutuskan izin bawahannya.
6. Atasan tidak wajib memeriksa seluruh bukti. Pemeriksaan dilakukan bila ada kecurigaan atau lewat sampel periodik.
7. Pegawai tidak dapat menyetujui izinnya sendiri.

## 9. Kebutuhan Non-Fungsional

- **Keamanan:** akses berbasis peran, hash kata sandi, perlindungan CSRF, validasi tipe dan ukuran unggahan, berkas bukti tidak dapat diakses tanpa login.
- **Privasi:** tidak ada pelacakan lokasi. Bukti hanya dapat dibuka pegawai terkait, atasannya, dan admin.
- **Kinerja:** halaman utama dimuat di bawah 2 detik pada jaringan lokal untuk sekitar 100 pengguna aktif (angka usulan, perlu dikonfirmasi).
- **Ketersediaan:** berjalan di satu server lokal, dengan cadangan basis data dan berkas bukti secara terjadwal.
- **Kompatibilitas:** responsif untuk browser desktop dan HP (pegawai mengunggah bukti dari HP).
- **Jejak audit:** pengajuan, keputusan, penutupan, dan pengecualian tercatat dengan waktu dan pelaku.
- **HTTPS:** disarankan memakai sertifikat internal agar kamera browser dapat diakses dengan andal.

## 10. Model Data (tingkat tinggi)

| Tabel | Isi utama |
|---|---|
| `users` | id, nip, nama, jabatan, unit, peran, atasan_id, password_hash, aktif |
| `leave_types` | id, nama, perlu_lampiran, jenis_bukti_diterima |
| `leave_requests` | id, user_id, leave_type_id, kategori (harian/keluar_sementara), tanggal_mulai, tanggal_selesai, jam_pergi, jam_pulang_rencana, jam_kembali_aktual, alasan, tujuan, status, ditutup_terlambat |
| `approvals` | id, request_id, approver_id, keputusan, catatan, waktu |
| `evidences` | id, request_id, path_berkas, tipe, waktu_unggah_server, catatan |
| `extensions` | id, request_id, jam_pulang_baru, alasan, status, approver_id |
| `exceptions` | id, request_id, alasan, keputusan, approver_id, catatan, waktu |
| `notifications` | id, user_id, pesan, dibaca, waktu |
| `audit_logs` | id, user_id, aksi, objek, waktu |
| `settings` | rentang_ip_kantor, jam_kerja, masa_simpan_bukti, dll. |

Status `leave_requests`: `diajukan`, `disetujui`, `ditolak`, `dibatalkan`, `sedang_di_luar`, `terlambat_kembali`, `selesai`, `selesai_terlambat`, `selesai_pengecualian`.

## 11. Daftar Layar (acuan untuk desain)

**Pegawai**
1. Login
2. Beranda pegawai (status izin aktif, tombol ajukan, tombol "sudah kembali" bila sedang di luar)
3. Form pengajuan izin (harian dan keluar sementara)
4. Detail izin dan riwayat status
5. Layar penyelesaian: unggah bukti + tombol "sudah kembali"
6. Form pengecualian
7. Riwayat izin saya

**Atasan**
8. Dashboard pemantauan (kartu ringkasan + daftar "sedang di luar" + "terlambat")
9. Daftar persetujuan (menunggu)
10. Detail pengajuan + aksi setuju/tolak
11. Penampil bukti
12. Daftar pengecualian dan perpanjangan menunggu keputusan
13. Rekap bawahan

**Admin**
14. Manajemen pengguna dan relasi atasan
15. Pengaturan (jenis izin, jam kerja, IP kantor, masa simpan bukti)
16. Laporan dan ekspor
17. Audit log

## 12. Arahan Desain (untuk Google Stitch)

- **Karakter:** bersih, formal, terpercaya, cocok untuk lingkungan kampus/perkantoran. Informasi utama mudah dipindai.
- **Platform:** *mobile-first* untuk layar pegawai (unggah bukti dari HP), *desktop-first* untuk dashboard atasan dan admin.
- **Palet warna:** warna utama bernuansa merah Unhas atau biru tua (pilih salah satu), dengan warna status yang konsisten:
  - Hijau: selesai/disetujui
  - Kuning/oranye: menunggu, sedang di luar
  - Merah: ditolak, terlambat
  - Abu-abu: dibatalkan
- **Komponen kunci:** kartu ringkasan angka, lencana status (badge), tabel dengan filter, stepper alur status, area unggah foto dengan pratinjau, kamera langsung.
- **Dashboard atasan:** empat kartu ringkasan di atas (sedang izin, sedang di luar, terlambat, menunggu persetujuan), lalu daftar "sedang di luar" dengan hitung mundur ke jam pulang.
- **Bahasa antarmuka:** Indonesia, nada ringkas dan sopan.
- **Aksesibilitas:** kontras teks memadai, tombol utama berukuran besar di layar HP.

**Contoh prompt awal untuk Stitch:**
> Desain aplikasi web responsif berbahasa Indonesia bernama "Izin Monitor" untuk pemantauan izin pegawai instansi pendidikan. Tampilan bersih dan formal dengan warna utama biru tua, lencana status berwarna (hijau selesai, oranye sedang di luar, merah terlambat). Layar yang dibutuhkan: login, beranda pegawai dengan tombol ajukan izin, form izin keluar sementara (jam pergi, jam pulang, alasan), layar penyelesaian dengan unggah foto bukti dan tombol "Sudah kembali", serta dashboard atasan dengan empat kartu ringkasan dan daftar pegawai yang sedang di luar.

## 13. Integrasi dengan Unhas Ontime

- **Fase 1:** tanpa integrasi. Pencocokan manual oleh atasan atau kepegawaian memakai laporan izin dari aplikasi.
- **Fase 2 (bersyarat):** impor berkala rekap Unhas Ontime melalui berkas (CSV/Excel). Sistem menandai pegawai yang tampak keluar atau tidak absen pulang tanpa izin yang sesuai. Fase ini bergantung pada ketersediaan dan format ekspor Ontime (**belum dikonfirmasi**).

## 14. Teknologi (usulan)

- **Backend:** Python Flask
- **Basis data:** MySQL
- **Frontend:** HTML/CSS/JS dengan templat sesuai desain dari Stitch
- **Penyimpanan bukti:** sistem berkas server lokal di luar direktori publik, diakses lewat rute yang dilindungi login
- **Penjadwal:** tugas terjadwal untuk menandai keterlambatan, pengingat, dan penghapusan bukti kedaluwarsa
- **Deployment:** satu server lokal dalam jaringan kantor

## 15. Risiko dan Mitigasi

| Risiko | Dampak | Mitigasi |
|---|---|---|
| Bukti dipalsukan (foto lama, foto dari internet) | Transparansi berkurang | Kamera langsung, waktu server, sampel pemeriksaan oleh atasan |
| Pegawai tidak mengajukan izin sebelum pergi | Celah pada pemantauan | Pencocokan dengan Ontime (fase 2), pengecekan manual atasan |
| Beban atasan tinggi (banyak bukti dan persetujuan) | Persetujuan tertunda | Tidak wajib periksa semua bukti, notifikasi, kemungkinan pendelegasian |
| Ruang penyimpanan penuh | Layanan terganggu | Kompresi, masa simpan, pemantauan kapasitas |
| Penolakan pegawai terhadap kewajiban bukti | Adopsi rendah | Sosialisasi, bukti beragam, jalur pengecualian |
| Server tunggal bermasalah | Layanan berhenti | Cadangan terjadwal |
| Kamera browser butuh HTTPS | Fitur kamera gagal | Sertifikat internal atau jalur unggah dari galeri sebagai cadangan |

## 16. Metrik Keberhasilan

- Persentase izin keluar yang ditutup dengan bukti (target usulan: di atas 95%)
- Jumlah izin yang berstatus "terlambat kembali" per bulan (diharapkan menurun)
- Rata-rata waktu persetujuan atasan
- Tingkat penggunaan aplikasi oleh pegawai

## 17. Rencana Rilis (usulan)

| Fase | Cakupan |
|---|---|
| **0. Desain** | Tema dan layar di Google Stitch, validasi alur dengan atasan |
| **1. MVP** | Login, pengajuan, persetujuan, penyelesaian dengan bukti, dashboard, rekap dasar |
| **2. Penguatan** | Perpanjangan, pengecualian, notifikasi lengkap, ekspor PDF |
| **3. Integrasi** | Impor rekap Ontime dan pencocokan (bila format tersedia) |

## 18. Pertanyaan Terbuka

1. Apakah Unhas Ontime dapat mengekspor rekap ke berkas, dan apa saja kolomnya?
2. Berapa jumlah pegawai dan berapa tingkat persetujuan (satu tingkat atau berjenjang)?
3. Berapa lama masa simpan bukti yang diinginkan?
4. Apakah ada batas durasi maksimal izin keluar sementara dalam sehari?
5. Siapa yang berwenang memutuskan pengecualian bila atasan langsung berhalangan?
6. Apakah jam kerja dan hari libur perlu dikelola di aplikasi (kalender libur)?
7. Apakah sertifikat HTTPS internal dapat disediakan?
