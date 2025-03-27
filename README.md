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

## Konfigurasi Google Drive API

1. Buka [Google Cloud Console](https://console.cloud.google.com/)
2. Buat Project baru atau pilih project yang sudah ada
3. Aktifkan Google Drive API:
   - Buka "APIs & Services" > "Library"
   - Cari "Google Drive API"
   - Klik "Enable"

4. Buat OAuth2 Credentials:
   - Buka "APIs & Services" > "Credentials"
   - Klik "Create Credentials" > "OAuth client ID"
   - Pilih "Desktop Application"
   - Isi nama aplikasi
   - Klik "Create"
   - Download file JSON credentials

5. Dapatkan OAuth2 Token:
   - Buka [Google OAuth 2.0 Playground](https://developers.google.com/oauthplayground)
   - Klik gear icon (Settings) di kanan atas
   - Centang "Use your own OAuth credentials"
   - Masukkan Client ID dan Client Secret dari file credentials JSON
   - Di panel kiri, expand "Drive API v3"
   - Pilih scope:
     - https://www.googleapis.com/auth/drive.readonly
     - https://www.googleapis.com/auth/drive.metadata.readonly
   - Klik "Authorize APIs"
   - Login dengan Google Account yang memiliki akses ke file
   - Klik "Exchange authorization code for tokens"
   - Copy "Access token" yang muncul

6. Gunakan Access Token:
   - Paste token ke form "Google Drive API Key" di aplikasi
   - Klik "Simpan API Key"
   - Token akan tersimpan selama session aktif

Note: Access token biasanya berlaku 1 jam. Jika expired, ulangi langkah 5 untuk mendapatkan token baru.

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

## Download Video dari Google Drive

1. Masukkan OAuth2 Access Token:
   - Copy Access Token dari Google OAuth Playground
   - Paste ke field "Google Drive API Key"
   - Klik "Simpan API Key"

2. Download Video:
   - Masukkan URL Google Drive video
   - Format URL yang didukung:
     - https://drive.google.com/file/d/{fileId}/view
     - https://drive.google.com/open?id={fileId}
     - Langsung file ID
   - Klik "Download Video"

Note: 
- Pastikan file video di Google Drive diset "Anyone with the link can view"
- Hanya file video yang dapat didownload (mp4, mkv, avi, mov, flv, wmv)

## Live Streaming

### YouTube Live
1. Buka YouTube Studio dan masuk ke menu "Go Live"
2. Pilih opsi "Stream" untuk mendapatkan Stream Key
3. Copy Stream Key dari YouTube Studio
4. Paste Stream Key ke form di aplikasi
5. Pilih video yang akan di-streaming
6. Klik "Mulai Live Streaming"

### Facebook Live
1. Buka Facebook Creator Studio
2. Pilih "Create Post" > "Live Video"
3. Copy Stream Key yang diberikan
4. Paste Stream Key ke form di aplikasi
5. Pilih video yang akan di-streaming
6. Klik "Mulai Live Streaming"

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
- OAuth2 untuk akses Google Drive API

## Pengembangan

Untuk menambahkan fitur atau melaporkan bug, silakan buat issue atau pull request.

## Lisensi

MIT License - Lihat file LICENSE untuk detail.
