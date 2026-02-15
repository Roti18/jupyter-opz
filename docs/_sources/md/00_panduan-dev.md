# Panduan Pengembangan (Dev Mode)

Halaman ini menjelaskan fitur **Development Mode** yang dirancang untuk mempercepat proses penambahan materi ke dalam Jupyter Book ini tanpa harus membuat file `.md` secara manual melalui file manager.

## 1. Aktivasi Development Mode
Fitur ini diatur melalui file `.env` di root project. Anda dapat mengaturnya saat pertama kali menjalankan script instalasi:

### Via Script Install
Saat menjalankan `install.sh` (Linux) atau `install.bat` (Windows), Anda akan diberikan pilihan mode:
*   Pilih **1) DEVELOPMENT** untuk mengaktifkan fitur canvas.

### Manofal Edit (.env)
Anda juga bisa mengubah mode secara manual dengan mengedit file `.env`:
```env
MODE=DEVELOPMENT
```

## 2. Menjalankan Dev Server
Setelah mode diatur ke `DEVELOPMENT`, jalankan script berikut untuk membuka antarmuka penulisan:

*   **Linux/macOS:** `./dev.sh`
*   **Windows:** `dev.bat`

Server akan berjalan di [http://127.0.0.1:5000](http://127.0.0.1:5000).

## 3. Menggunakan Markdown Canvas
Di dalam antarmuka web yang muncul, Anda dapat:

1.  **Paste Konten**: Tempelkan materi Markdown Anda ke dalam area teks yang disediakan.
2.  **Klik Simpan**: Tekan tombol "Simpan & Bangun".
3.  **Beri Nama**: Masukkan nama file (misal: `03_materi-baru`). Sistem akan otomatis menambahkan ekstensi `.md`.
4.  **Auto-Build**: Sistem akan secara otomatis:
    *   Menyimpan file ke folder `md/`.
    *   Memperbarui daftar isi (`_toc.yml`).
    *   Membangun ulang konten buku (`jupyter-book build`).

## 4. Keuntungan Mode Dev
*   **Akses Cepat**: Terdapat link "Dev Tool: Insert MD" di bagian bawah sidebar buku saat Anda melihat hasil build.
*   **Otomasi TOC**: Tidak perlu lagi mengedit `_toc.yml` secara manual, script akan mendeteksi file baru dan mengurutkannya.
*   **Pratinjau Instan**: Setelah build selesai, cukup refresh halaman buku untuk melihat materi baru Anda.
