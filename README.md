# Streaming Platform

Aplikasi streaming video dengan fitur download dari Google Drive dan live streaming ke platform YouTube dan Facebook.

## Fitur

- Monitoring sistem (CPU, Memory, Disk Usage)
- Download video dari Google Drive
- Manajemen video (rename, delete)
- Live streaming ke YouTube dan Facebook
- Daftar video dengan informasi ukuran dan tanggal download
- Daftar live streaming yang sedang aktif

## Persyaratan Sistem

- Python 3.8+
- FFmpeg
- Dependensi Python (lihat requirements.txt)

## Instalasi

1. Clone repository:
```bash
git clone https://github.com/masdonik/streaming-platform.git
cd streaming-platform
```

2. Install dependensi:
```bash
pip install -r requirements.txt
```

3. Install FFmpeg:
```bash
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install -y ffmpeg

# Windows
# Download dari https://ffmpeg.org/download.html
```

4. Buat direktori videos:
```bash
mkdir videos
```

## Konfigurasi

1. Google Drive API:
   - Buat project di Google Cloud Console
   - Aktifkan Google Drive API
   - Buat kredensial dan dapatkan API Key
   - Masukkan API Key saat mendownload video

2. Platform Streaming:
   - YouTube: Dapatkan Stream Key dari YouTube Studio
   - Facebook: Dapatkan Stream Key dari Facebook Creator Studio

## Penggunaan

1. Jalankan aplikasi:
```bash
python server.py
```

2. Buka browser dan akses:
```
http://localhost:8000
```

3. Login dengan kredensial default:
```
Username: admin
Password: 1234
```

## Fitur Detail

### Download Video
- Mendukung download video dari Google Drive
- Progress bar saat download
- Validasi format video
- Penyimpanan otomatis di folder videos

### Live Streaming
- Support multi-platform (YouTube, Facebook)
- Kontrol streaming (start/stop)
- Monitor status streaming
- Loop video otomatis

### Manajemen Video
- Rename video
- Delete video
- Informasi ukuran dan tanggal
- Tabel daftar video

### Monitoring Sistem
- CPU Usage
- Memory Usage (Used/Total)
- Disk Usage (Used/Total)
- Update otomatis setiap 5 detik

## Struktur Direktori

```
streaming-platform/
├── static/
│   └── css/
│       └── style.css
├── templates/
│   ├── login.html
│   ├── dashboard.html
│   └── live.html
├── videos/           # Direktori penyimpanan video
├── server.py        # File utama aplikasi
├── utils.py         # Fungsi-fungsi pembantu
└── requirements.txt # Dependensi Python
```

## Keamanan

- Autentikasi wajib untuk akses fitur
- Validasi input untuk semua form
- Sanitasi nama file
- Proteksi terhadap akses langsung ke file

## Pengembangan

Untuk menambahkan fitur atau melaporkan bug, silakan buat issue atau pull request.

## Lisensi

MIT License - Lihat file LICENSE untuk detail.
