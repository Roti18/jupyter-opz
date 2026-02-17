# Panduan Pengembangan

Halaman ini menjelaskan alur kerja pengembangan dan fitur **Markdown Canvas** yang dirancang untuk mempercepat proses pembuatan konten tanpa harus berurusan dengan konfigurasi manual.

## 1. Persiapan & Konfigurasi
Kita telah menyederhanakan sistem sehingga **tidak lagi memerlukan file `.env`**. Semua konfigurasi identitas sekarang langsung disimpan ke dalam `_config.yml`.

### Mengatur Identitas Project
Jika Anda ingin mengubah Nama Penulis, Tahun, atau URL Repository, gunakan perintah:
*   **Windows:** `.\run.bat config`
*   **Linux/macOS:** `bash run.sh config`

Script ini akan secara otomatis memperbarui `_config.yml` dan memberikan opsi untuk langsung membangun ulang (rebuild) buku.

## 2. Menjalankan Dev Server & Canvas
Untuk mulai menulis materi baru dengan antarmuka web (Markdown Canvas), jalankan:

*   **Windows:** `.\run.bat dev`
*   **Linux/macOS:** `bash run.sh dev`

Server akan berjalan secara lokal di `http://127.0.0.1:5000`. 
*   **Book Preview:** `http://127.0.0.1:5000/`
*   **Markdown Canvas:** `http://127.0.0.1:5000/canvas`

## 3. Alur Kerja Markdown Canvas
Di dalam antarmuka Canvas, Anda dapat:

1.  **Paste & Edit**: Tulis atau tempel materi Markdown Anda. Pastikan setiap file memiliki **H1 Title** (`# Judul`) di baris pertama.
2.  **Simpan & Bangun**: Masukkan nama file (misal: `materi-baru`). 
    *   **Auto-Prefix**: Sistem akan otomatis mendeteksi urutan dan menambahkan prefix angka (seperti `05_materi-baru.md`).
3.  **Otomasi Total**: Setelah klik simpan, sistem akan:
    *   Menyimpan file ke folder `md/`.
    *   Membangun ulang daftar isi (`_toc.yml`) secara otomatis.
    *   Membangun ulang file HTML (`jupyter-book build`).

## 4. Keuntungan Sistem Baru
*   **Zero Config**: Tidak ada lagi urusan dengan file `.env` atau setting manual yang rumit.
*   **Auto TOC**: Daftar isi di sidebar akan selalu sinkron dengan file yang ada di folder `md/` berdasarkan urutan angka.
*   **Single Master Script**: Semua operasi (install, dev, publish, config, reset) dikelola melalui satu perintah `run.bat` atau `run.sh`.
*   **Deployment Ready**: Menjalankan `run.bat publish` akan langsung menyiapkan folder `docs/` yang siap di-push ke GitHub Pages.
