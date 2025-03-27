import os
import re
import requests
import subprocess
import psutil
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

def get_system_info():
    """Get system resource usage"""
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        'cpu': cpu,
        'memory': {
            'total': memory.total,
            'used': memory.used,
            'percent': memory.percent
        },
        'disk': {
            'total': disk.total,
            'used': disk.used,
            'percent': disk.percent
        }
    }

def get_video_info(video_path):
    """Get video file information"""
    if not os.path.exists(video_path):
        return None
        
    stat = os.stat(video_path)
    size = stat.st_size
    created = datetime.fromtimestamp(stat.st_ctime)
    
    return {
        'size': size,
        'created': created,
        'size_formatted': format_size(size)
    }

def format_size(size):
    """Format size in bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"

def get_file_id_from_url(url):
    """
    Extract file ID from URL Google Drive.
    Mendukung format URL:
    - https://drive.google.com/file/d/{fileId}/view
    - https://drive.google.com/open?id={fileId}
    - Langsung file ID
    """
    if not url:
        raise ValueError("URL tidak boleh kosong")
    
    # Jika input adalah ID langsung
    if not url.startswith('http'):
        return url
    
    # Parse URL
    parsed = urlparse(url)
    
    # Format /file/d/{fileId}/view
    if 'file/d/' in url:
        file_id = url.split('file/d/')[1].split('/')[0]
        return file_id
    
    # Format ?id={fileId}
    query_params = parse_qs(parsed.query)
    if 'id' in query_params:
        return query_params['id'][0]
    
    raise ValueError("Format URL Google Drive tidak valid")

def download_from_google_drive(url, save_path, api_key, progress_callback=None):
    """
    Download file dari Google Drive menggunakan API
    """
    try:
        file_id = get_file_id_from_url(url)
        
        # Buat direktori jika belum ada
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Setup Google Drive API dengan API key
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json'
        }
        
        # Get file metadata first
        metadata_url = f'https://www.googleapis.com/drive/v3/files/{file_id}?fields=size,mimeType'
        metadata_response = requests.get(metadata_url, headers=headers)
        metadata_response.raise_for_status()
        metadata = metadata_response.json()
        
        # Verify if it's a video file
        mime_type = metadata.get('mimeType', '')
        if not mime_type.startswith('video/'):
            raise ValueError("File bukan merupakan video")
        
        # Download file
        download_url = f'https://www.googleapis.com/drive/v3/files/{file_id}?alt=media'
        response = requests.get(download_url, headers=headers, stream=True)
        response.raise_for_status()
        
        # Get file size
        file_size = int(metadata.get('size', 0))
        
        # Download with progress
        downloaded = 0
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    downloaded += len(chunk)
                    f.write(chunk)
                    if progress_callback and file_size:
                        progress = (downloaded / file_size) * 100
                        progress_callback(progress)
        
        return True
        
    except requests.exceptions.RequestException as e:
        if e.response is not None:
            if e.response.status_code == 401:
                raise Exception("API Key tidak valid atau kadaluarsa")
            elif e.response.status_code == 403:
                raise Exception("Akses ditolak. Pastikan file dapat diakses publik atau API Key memiliki akses yang cukup")
            elif e.response.status_code == 404:
                raise Exception("File tidak ditemukan")
        raise Exception(f"Error saat download: {str(e)}")
    except Exception as e:
        raise Exception(f"Error: {str(e)}")

def is_video_file(filename):
    """
    Cek apakah file adalah video berdasarkan ekstensi
    """
    video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv']
    return any(filename.lower().endswith(ext) for ext in video_extensions)

def get_safe_filename(filename):
    """
    Membuat nama file aman (menghapus karakter yang tidak valid)
    """
    # Hapus karakter yang tidak diizinkan
    filename = re.sub(r'[^\w\s.-]', '', filename)
    # Ganti spasi dengan underscore
    filename = re.sub(r'\s+', '_', filename)
    return filename.strip('.-')

def check_ffmpeg_installed():
    """
    Cek apakah ffmpeg terinstall di sistem
    """
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False

def start_streaming(video_path, platform, stream_key):
    """
    Mulai streaming berdasarkan platform yang dipilih
    """
    if platform == 'youtube':
        rtmp_url = f"rtmps://a.rtmps.youtube.com/live2/{stream_key}"
    elif platform == 'facebook':
        rtmp_url = f"rtmps://live-api-s.facebook.com:443/rtmp/{stream_key}"
    else:
        raise ValueError("Platform tidak didukung")

    command = [
        'ffmpeg',
        '-stream_loop', '-1',  # Loop video
        '-re',                 # Read input at native frame rate
        '-i', video_path,      # Input file
        '-c', 'copy',         # Copy codec (no re-encode)
        '-f', 'flv',          # Force FLV format
        '-fflags', 'nobuffer',
        '-flags', 'low_delay',
        rtmp_url              # Output URL
    ]
    
    # Jalankan ffmpeg dengan logging
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    return process

def get_active_streams():
    """
    Dapatkan daftar streaming yang sedang aktif
    """
    streams = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.name() == 'ffmpeg':
                cmdline = proc.cmdline()
                if '-re' in cmdline and 'rtmp' in ' '.join(cmdline):
                    streams.append({
                        'pid': proc.pid,
                        'command': ' '.join(cmdline)
                    })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return streams