# 🖨️ Tukang-Print — File Converter & Compressor Bot

> Telegram bot untuk kompres dan konversi file — PDF, Word (DOCX), Gambar — langsung dari chat tanpa install software apapun.

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python) ![python-telegram-bot](https://img.shields.io/badge/python--telegram--bot-22.6-blue) ![Pillow](https://img.shields.io/badge/Pillow-12.1.1-orange) ![Platform](https://img.shields.io/badge/Platform-Linux-lightgrey?logo=linux) ![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Fitur

### 🖼️ Gambar (JPG / PNG / WebP)
- 📉 **Kompres** ukuran file (quality 60, optimized)
- 🔄 **Convert** gambar ke PDF

### 📄 PDF
- 📉 **Kompres** PDF via Ghostscript (setting `ebook` — 150 DPI, balance size vs kualitas)

### 📝 Word (DOCX)
- 📄 **Convert** Word ke PDF via LibreOffice Headless

### General
- ✅ Tombol interaktif via **Inline Keyboard**
- 🧹 **Auto-cleanup** — semua file temp dihapus otomatis setelah diproses
- ❌ Error handling lengkap dengan notifikasi ke user

---

## 🛠️ Tech Stack

| Komponen | Detail |
|---|---|
| Bahasa | Python 3 |
| Bot Framework | `python-telegram-bot` v22.6 |
| Image Processing | `Pillow` v12.1.1 |
| PDF Compression | `Ghostscript` (system package) |
| DOCX Conversion | `LibreOffice Headless` (system package) |
| Environment | Linux Ubuntu (LXC Container di Proxmox VE) |

---

## 📦 System Dependencies

Sebelum install Python packages, pastikan ini sudah terinstall di sistem:

```bash
# Ghostscript (untuk kompres PDF)
apt install ghostscript -y

# LibreOffice (untuk convert DOCX ke PDF)
apt install libreoffice -y
```

---

## 🚀 Cara Deploy

### 1. Clone repo ini
```bash
git clone https://github.com/MrElixir1945/Tukang-Print.git
cd Tukang-Print
```

### 2. Buat virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 4. Konfigurasi token
Buka `main.py`, cari baris berikut dan ganti dengan token bot kamu:
```python
TOKEN = "GANTI_DENGAN_TOKEN_BOT_KAMU"
```

> 💡 Atau gunakan `.env` + `python-dotenv` untuk pengelolaan token yang lebih aman.

### 5. Jalankan bot
```bash
python main.py
```

---

## 📁 Struktur Project

```
Tukang-Print/
├── main.py             # Main bot
├── requirements.txt    # Python dependencies
└── temp_files/         # Folder temp (auto-dibuat, auto-dihapus setelah proses)
```

---

## ⚙️ Cara Kerja

```
User kirim file (Gambar / PDF / DOCX)
    ↓
Bot deteksi tipe file
    ↓
Bot tampilkan tombol pilihan aksi
    ↓
User pilih aksi (Kompres / Convert)
    ↓
Bot proses file di server
    ↓
Kirim hasil ke user
    ↓
Hapus semua file temp (cleanup)
```

---

## 📋 Contoh Penggunaan

```
User:  [kirim file photo.jpg]
Bot:   File diterima: photo.jpg — Mau diapain?
       [📉 Kompres JPG] [🔄 Convert to PDF]

User:  klik [📉 Kompres JPG]
Bot:   ⏳ Sedang memproses... Tunggu bentar ya server kentang.
Bot:   ✅ Nih hasilnya! [compressed_photo.jpg]
```

---

## ⚠️ Catatan

- File diproses di server dan **langsung dihapus** setelah dikirim — tidak ada data yang disimpan
- Untuk file besar, proses mungkin memakan waktu beberapa detik tergantung spesifikasi server
- Bot ini dirancang untuk berjalan di **home server / VPS Linux**

---

## 👤 Author

**Mr. Elixir** — [@MrElixir1945](https://github.com/MrElixir1945)

*Self-hosted on Proxmox VE Home Server*
