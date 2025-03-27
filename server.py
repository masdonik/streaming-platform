from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
import subprocess
from functools import wraps
from datetime import datetime
from utils import (
    download_from_google_drive,
    is_video_file,
    get_safe_filename,
    check_ffmpeg_installed,
    get_system_info,
    get_video_info,
    start_streaming,
    get_active_streams
)

app = Flask(__name__)
app.secret_key = 'rahasia123'  # Ganti dengan secret key yang lebih aman di produksi

# Direktori untuk menyimpan video
UPLOAD_FOLDER = 'videos'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Dictionary untuk menyimpan proses streaming yang aktif
active_streams = {}

# Decorator untuk mengecek login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Silakan login terlebih dahulu', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'admin' and password == '1234':
            session['logged_in'] = True
            flash('Login berhasil!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Username atau password salah!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Anda telah logout', 'info')
    return redirect(url_for('login'))

@app.route('/system-info')
@login_required
def system_info():
    return jsonify(get_system_info())

@app.route('/dashboard')
@login_required
def dashboard():
    # Ambil daftar video dari folder videos
    videos = []
    for filename in os.listdir(UPLOAD_FOLDER):
        if os.path.isfile(os.path.join(UPLOAD_FOLDER, filename)):
            video_info = get_video_info(os.path.join(UPLOAD_FOLDER, filename))
            if video_info:
                videos.append({
                    'name': filename,
                    'size': video_info['size_formatted'],
                    'created': video_info['created'].strftime('%Y-%m-%d %H:%M:%S')
                })
    
    system_info = get_system_info()
    return render_template('dashboard.html', videos=videos, system_info=system_info)

@app.route('/save-api-key', methods=['POST'])
@login_required
def save_api_key():
    api_key = request.form.get('api_key')
    if api_key:
        session['api_key'] = api_key
        flash('API Key berhasil disimpan!', 'success')
    else:
        flash('API Key tidak boleh kosong!', 'error')
    return redirect(url_for('dashboard'))

@app.route('/download', methods=['POST'])
@login_required
def download_video():
    drive_url = request.form.get('drive_url')
    api_key = session.get('api_key')
    
    if not api_key:
        flash('Silakan simpan API Key terlebih dahulu!', 'error')
        return redirect(url_for('dashboard'))
        
    if not drive_url:
        flash('URL Google Drive harus diisi!', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        # Generate nama file yang aman
        temp_filename = 'temp_download'
        save_path = os.path.join(UPLOAD_FOLDER, temp_filename)
        
        def progress_callback(progress):
            # Dalam implementasi nyata, gunakan WebSocket untuk update progress
            print(f"Download progress: {progress:.1f}%")
        
        # Download video
        download_from_google_drive(drive_url, save_path, api_key, progress_callback)
        
        # Cek apakah file yang didownload adalah video
        if not is_video_file(save_path):
            os.remove(save_path)
            flash('File yang didownload bukan video!', 'error')
            return redirect(url_for('dashboard'))
        
        # Rename file dengan nama yang aman
        original_filename = os.path.basename(drive_url)
        safe_filename = get_safe_filename(original_filename)
        if not safe_filename.endswith(('.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv')):
            safe_filename += '.mp4'
        
        new_path = os.path.join(UPLOAD_FOLDER, safe_filename)
        os.rename(save_path, new_path)
        
        flash('Video berhasil didownload!', 'success')
    except Exception as e:
        flash(f'Error saat mendownload video: {str(e)}', 'error')
        if os.path.exists(save_path):
            os.remove(save_path)
    
    return redirect(url_for('dashboard'))

@app.route('/rename', methods=['POST'])
@login_required
def rename_video():
    old_name = request.form.get('old_name')
    new_name = request.form.get('new_name')
    
    if not all([old_name, new_name]):
        flash('Nama file lama dan baru harus diisi!', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        # Pastikan ekstensi file tetap sama
        old_ext = os.path.splitext(old_name)[1]
        new_name_with_ext = new_name if new_name.endswith(old_ext) else new_name + old_ext
        
        old_path = os.path.join(UPLOAD_FOLDER, old_name)
        new_path = os.path.join(UPLOAD_FOLDER, new_name_with_ext)
        
        os.rename(old_path, new_path)
        flash('Nama video berhasil diubah!', 'success')
    except Exception as e:
        flash(f'Error saat mengubah nama video: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/delete', methods=['POST'])
@login_required
def delete_video():
    filename = request.form.get('filename')
    if not filename:
        flash('Nama file tidak boleh kosong!', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        os.remove(os.path.join(UPLOAD_FOLDER, filename))
        flash('Video berhasil dihapus!', 'success')
    except Exception as e:
        flash(f'Error saat menghapus video: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/live')
@login_required
def live():
    videos = []
    for filename in os.listdir(UPLOAD_FOLDER):
        if os.path.isfile(os.path.join(UPLOAD_FOLDER, filename)):
            video_info = get_video_info(os.path.join(UPLOAD_FOLDER, filename))
            if video_info:
                videos.append({
                    'name': filename,
                    'size': video_info['size_formatted'],
                    'created': video_info['created'].strftime('%Y-%m-%d %H:%M:%S')
                })
    
    # Get active streams
    streams = get_active_streams()
    system_info = get_system_info()
    
    return render_template('live.html', 
                         videos=videos, 
                         streams=streams,
                         system_info=system_info)

@app.route('/live/start', methods=['POST'])
@login_required
def start_live():
    # Cek apakah ffmpeg terinstall
    if not check_ffmpeg_installed():
        flash('ffmpeg tidak terinstall di sistem!', 'error')
        return redirect(url_for('live'))
    
    video_file = request.form.get('video_file')
    stream_key = request.form.get('stream_key')
    platform = request.form.get('platform')
    
    if not all([video_file, stream_key, platform]):
        flash('File video, stream key, dan platform harus diisi!', 'error')
        return redirect(url_for('live'))
    
    try:
        video_path = os.path.join(UPLOAD_FOLDER, video_file)
        if not os.path.exists(video_path):
            flash('File video tidak ditemukan!', 'error')
            return redirect(url_for('live'))
        
        # Start streaming process
        process = start_streaming(video_path, platform, stream_key)
        
        # Save stream info
        stream_id = f"{platform}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        active_streams[stream_id] = {
            'process': process,
            'video': video_file,
            'platform': platform,
            'started': datetime.now()
        }
        
        flash('Streaming berhasil dimulai!', 'success')
    except Exception as e:
        flash(f'Error saat memulai streaming: {str(e)}', 'error')
    
    return redirect(url_for('live'))

@app.route('/live/stop', methods=['POST'])
@login_required
def stop_live():
    stream_id = request.form.get('stream_id')
    
    if not stream_id or stream_id not in active_streams:
        flash('Stream ID tidak valid!', 'error')
        return redirect(url_for('live'))
    
    try:
        stream = active_streams[stream_id]
        if stream['process']:
            stream['process'].terminate()
            stream['process'].wait()
        
        del active_streams[stream_id]
        flash('Streaming berhasil dihentikan!', 'success')
    except Exception as e:
        flash(f'Error saat menghentikan streaming: {str(e)}', 'error')
    
    return redirect(url_for('live'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)