import os
import sqlite3
import subprocess
import threading
import time
import urllib.request
from datetime import datetime
from flask import Flask, request, send_from_directory, render_template_string, redirect, session, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key_flixify_pro')

BASE_DIR = os.path.expanduser('~/yt-cloud-data')
MEDIA_DIR = os.path.join(BASE_DIR, 'media')
DB_FILE = os.path.join(BASE_DIR, 'database.db')

os.makedirs(MEDIA_DIR, exist_ok=True)

def get_db():
    conn = sqlite3.connect(DB_FILE, timeout=30.0)
    conn.row_factory = sqlite3.Row
    return conn

def init_and_migrate_db():
    conn = get_db()
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        username TEXT UNIQUE, 
        handle TEXT, 
        password TEXT,
        subscribers INTEGER DEFAULT 1250,
        age INTEGER DEFAULT 20,
        role TEXT DEFAULT 'Verified Creator',
        balance REAL DEFAULT 4200.5,
        rpm REAL DEFAULT 1.8,
        cpm REAL DEFAULT 3.5,
        bio TEXT DEFAULT 'Welcome to my official Flixify channel!',
        dark_mode INTEGER DEFAULT 1,
        data_saver INTEGER DEFAULT 0,
        country TEXT DEFAULT 'US',
        parental_control TEXT DEFAULT 'Off'
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        filename TEXT, 
        title TEXT, 
        description TEXT, 
        category TEXT DEFAULT 'All', 
        tags TEXT DEFAULT '',
        user_id INTEGER, 
        likes INTEGER DEFAULT 0, 
        dislikes INTEGER DEFAULT 0, 
        views INTEGER DEFAULT 0, 
        is_short INTEGER DEFAULT 0, 
        file_size_mb REAL DEFAULT 0.0,
        visibility TEXT DEFAULT 'Public',
        copyright_status TEXT DEFAULT 'Passed (Content ID Clean)',
        loop_enabled INTEGER DEFAULT 0,
        hdr_enabled INTEGER DEFAULT 0,
        audio_normalized INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        video_id INTEGER, 
        user_id INTEGER,
        user_name TEXT, 
        comment_text TEXT, 
        likes INTEGER DEFAULT 0,
        is_creator_heart INTEGER DEFAULT 0,
        is_pinned INTEGER DEFAULT 0,
        is_quarantined INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        channel_id INTEGER
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS downloads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        video_id INTEGER,
        quality TEXT DEFAULT '720p',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS saved_videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        video_id INTEGER,
        playlist_name TEXT DEFAULT 'Watch Later',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS community_posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        content TEXT,
        post_type TEXT DEFAULT 'text',
        poll_options TEXT DEFAULT '',
        likes INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        message TEXT,
        is_read INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS watch_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        video_id INTEGER,
        watched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS clips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        video_id INTEGER,
        user_id INTEGER,
        clip_title TEXT,
        start_time INTEGER DEFAULT 0,
        end_time INTEGER DEFAULT 15,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS live_streams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT,
        stream_key TEXT,
        is_live INTEGER DEFAULT 1,
        viewers_count INTEGER DEFAULT 42,
        multi_stream_platforms TEXT DEFAULT 'YouTube, Twitch'
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS channel_memberships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        channel_id INTEGER,
        tier_level INTEGER DEFAULT 1,
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Safe Migrations for existing DB instances
    migrations = [
        "ALTER TABLE comments ADD COLUMN user_id INTEGER",
        "ALTER TABLE comments ADD COLUMN user_name TEXT",
        "ALTER TABLE comments ADD COLUMN is_creator_heart INTEGER DEFAULT 0",
        "ALTER TABLE comments ADD COLUMN is_pinned INTEGER DEFAULT 0",
        "ALTER TABLE comments ADD COLUMN is_quarantined INTEGER DEFAULT 0",
        "ALTER TABLE users ADD COLUMN bio TEXT",
        "ALTER TABLE users ADD COLUMN dark_mode INTEGER DEFAULT 1",
        "ALTER TABLE users ADD COLUMN data_saver INTEGER DEFAULT 0",
        "ALTER TABLE users ADD COLUMN country TEXT DEFAULT 'US'",
        "ALTER TABLE users ADD COLUMN parental_control TEXT DEFAULT 'Off'",
        "ALTER TABLE videos ADD COLUMN category TEXT DEFAULT 'All'",
        "ALTER TABLE videos ADD COLUMN hdr_enabled INTEGER DEFAULT 0",
        "ALTER TABLE videos ADD COLUMN audio_normalized INTEGER DEFAULT 1"
    ]
    for m in migrations:
        try:
            c.execute(m)
        except Exception:
            pass

    conn.commit()
    conn.close()

init_and_migrate_db()

@app.after_request
def add_header(response):
    if 'static' in request.path or request.path.startswith('/videos/'):
        response.headers['Cache-Control'] = 'public, max-age=86400'
    else:
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

def self_ping():
    app_url = os.getenv('RENDER_EXTERNAL_URL', '')
    if app_url:
        while True:
            try:
                time.sleep(300)
                urllib.request.urlopen(app_url)
            except Exception:
                pass

threading.Thread(target=self_ping, daemon=True).start()

def process_video_with_ffmpeg(input_path, filename):
    try:
        base_name = os.path.splitext(filename)[0]
        thumb_filename = f"{base_name}_thumb.jpg"
        thumb_path = os.path.join(MEDIA_DIR, thumb_filename)
        subprocess.run(['ffmpeg', '-i', input_path, '-ss', '00:00:01.000', '-vframes', '1', thumb_path], 
                       check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print("FFmpeg processing note:", e)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Flixify Master Ultimate Studio Pro + Advanced Features</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #0f0f0f; color: #f1f1f1; padding-bottom: 70px; }

        header { display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: #0f0f0f; position: sticky; top: 0; z-index: 100; border-bottom: 1px solid #272727; gap: 8px; }
        .logo-container { display: flex; flex-direction: column; align-items: center; text-decoration: none; gap: 2px; flex-shrink: 0; }

        .search-box-container { display: flex; align-items: center; background: #121212; border: 1.5px solid #3f3f3f; border-radius: 20px; padding: 6px 12px; flex: 1; max-width: 220px; gap: 6px; cursor: pointer; }
        .search-box-container input { background: transparent; border: none; color: #fff; width: 100%; outline: none; font-size: 13px; cursor: pointer; pointer-events: none; }
        .search-icon { width: 18px; height: 18px; fill: none; stroke: #aaa; stroke-width: 2; flex-shrink: 0; }

        .header-icons { display: flex; gap: 10px; align-items: center; flex-shrink: 0; }
        .icon-btn { background: none; border: none; cursor: pointer; position: relative; color: #fff; text-decoration: none; display: flex; align-items: center; padding: 4px; }
        .icon-btn svg { width: 20px; height: 20px; fill: none; stroke: #fff; stroke-width: 2; }
        .notif-badge { position: absolute; top: -2px; right: -2px; background: #ff0000; color: #fff; font-size: 8px; padding: 2px 4px; border-radius: 10px; font-weight: bold; }

        #searchOverlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: #0f0f0f; z-index: 2000; padding: 10px 14px; overflow-y: auto; }
        .search-top-bar { display: flex; align-items: center; gap: 10px; border-bottom: 1px solid #272727; padding-bottom: 10px; }
        .search-input-box { display: flex; align-items: center; background: #121212; border: 1px solid #3f3f3f; border-radius: 20px; padding: 6px 14px; flex: 1; gap: 8px; }
        .search-input-box input { background: transparent; border: none; color: #fff; width: 100%; outline: none; font-size: 15px; }

        .chips-wrapper { display: flex; gap: 8px; padding: 8px 16px; overflow-x: auto; background: #0f0f0f; position: sticky; top: 48px; z-index: 99; border-bottom: 1px solid #272727; scrollbar-width: none; }
        .chips-wrapper::-webkit-scrollbar { display: none; }
        .chip { background: #272727; color: #fff; padding: 6px 12px; border-radius: 8px; font-size: 13px; text-decoration: none; font-weight: 500; white-space: nowrap; border: 1px solid #3f3f3f; }
        .chip.active { background: #fff; color: #0f0f0f; border-color: #fff; }

        .feed { display: flex; flex-direction: column; gap: 16px; margin-top: 8px; }
        .video-card { width: 100%; text-decoration: none; color: inherit; display: block; }
        .thumb-box { width: 100%; aspect-ratio: 16/9; background: #000; position: relative; display: block; cursor: pointer; }
        .thumb-box video { width: 100%; height: 100%; object-fit: cover; pointer-events: none; }
        
        .shorts-feed-container { scroll-snap-type: y mandatory; overflow-y: scroll; height: calc(100vh - 105px); width: 100%; position: absolute; top: 48px; left: 0; }
        .short-card-item { scroll-snap-align: start; height: calc(100vh - 105px); width: 100%; position: relative; background: #000; display: flex; align-items: center; justify-content: center; }
        .short-card-item video { width: 100%; height: 100%; object-fit: cover; cursor: pointer; }
        
        .short-sidebar { position: absolute; right: 12px; bottom: 80px; display: flex; flex-direction: column; align-items: center; gap: 16px; z-index: 10; }
        .short-side-btn { background: none; border: none; color: #fff; display: flex; flex-direction: column; align-items: center; gap: 4px; cursor: pointer; text-decoration: none; font-size: 11px; font-weight: 600; }
        .short-side-btn svg { width: 26px; height: 26px; fill: none; stroke: #fff; stroke-width: 2; }
        
        .short-bottom-info { position: absolute; bottom: 16px; left: 16px; right: 70px; z-index: 10; color: #fff; }
        .short-ch-row { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
        .short-avatar { width: 34px; height: 34px; border-radius: 50%; background: #555; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; text-decoration: none; color: #fff; }
        
        .v-info-box { display: flex; padding: 12px; gap: 12px; }
        .channel-avatar { width: 38px; height: 38px; border-radius: 50%; background: #272727; color: #fff; display: flex; align-items: center; justify-content: center; font-weight: bold; text-decoration: none; flex-shrink: 0; }
        .v-details { flex: 1; }
        .v-title { font-size: 15px; font-weight: 600; color: #f1f1f1; margin-bottom: 4px; }
        .v-meta { font-size: 12px; color: #aaa; display: flex; gap: 6px; flex-wrap: wrap; }

        .player-container { width: 100%; aspect-ratio: 16/9; background: #000; position: sticky; top: 48px; z-index: 98; transition: box-shadow 0.3s; }
        .player-container.ambient { box-shadow: 0 0 35px rgba(62, 166, 255, 0.4); }
        .main-video { width: 100%; height: 100%; object-fit: contain; }

        .video-details-container { padding: 12px 16px; color: #ffffff; background-color: #0f0f0f; }
        .video-title { font-size: 18px; font-weight: bold; margin-bottom: 4px; }
        .video-stats { font-size: 12px; color: #aaa; margin-bottom: 12px; }
        .channel-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
        .channel-info { display: flex; align-items: center; gap: 12px; text-decoration: none; color: inherit; }
        .channel-img { width: 40px; height: 40px; border-radius: 50%; object-fit: cover; background: #555; display: flex; align-items: center; justify-content: center; font-weight: bold; }
        .channel-name-sub { display: flex; flex-direction: column; }
        .channel-title { font-size: 14px; font-weight: bold; }
        .sub-count { font-size: 11px; color: #aaa; }
        .subscribe-btn { background-color: #ffffff; color: #000000; border: none; padding: 8px 16px; border-radius: 20px; font-weight: bold; cursor: pointer; text-decoration: none; }
        
        .action-buttons { display: flex; gap: 8px; overflow-x: auto; padding-bottom: 8px; margin-bottom: 12px; scrollbar-width: none; }
        .action-buttons::-webkit-scrollbar { display: none; }
        .action-btn { background-color: #272727; color: #ffffff; border: none; padding: 8px 12px; border-radius: 20px; display: flex; align-items: center; gap: 6px; font-size: 13px; cursor: pointer; white-space: nowrap; text-decoration: none; }
        .like-dislike-group { display: flex; background-color: #272727; border-radius: 20px; overflow: hidden; }
        .like-dislike-group .action-btn { background-color: transparent; border-radius: 0; }
        .divider { width: 1px; background-color: #3f3f3f; margin: 6px 0; }
        .description-box { background-color: #272727; padding: 10px; border-radius: 8px; font-size: 13px; color: #ddd; margin-bottom: 16px; }

        .comments-section { background: #1a1a1a; border-radius: 12px; padding: 12px; border: 1px solid #333; margin-top: 12px; }
        .comments-header { font-size: 15px; font-weight: bold; margin-bottom: 10px; }
        .comment-input-box { display: flex; gap: 8px; margin-bottom: 14px; }
        .comment-input-box input { flex: 1; background: #272727; border: 1px solid #444; color: #fff; padding: 8px 12px; border-radius: 20px; outline: none; font-size: 13px; }
        .comment-submit-btn { background: #3ea6ff; color: #000; border: none; padding: 0 14px; border-radius: 20px; font-weight: bold; cursor: pointer; font-size: 13px; }
        .comment-item { display: flex; gap: 10px; margin-bottom: 12px; font-size: 13px; }
        .comment-avatar { width: 30px; height: 30px; border-radius: 50%; background: #555; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 12px; flex-shrink: 0; }
        .comment-content { flex: 1; }
        .comment-user { font-weight: bold; font-size: 12px; color: #aaa; margin-bottom: 2px; }
        .comment-text { color: #f1f1f1; }

        .profile-header { display: flex; align-items: center; justify-content: space-between; padding: 16px; border-bottom: 1px solid #272727; }
        .profile-user-info { display: flex; align-items: center; gap: 14px; }
        .profile-avatar { width: 64px; height: 64px; border-radius: 50%; background: #3ea6ff; color: #000; display: flex; align-items: center; justify-content: center; font-size: 26px; font-weight: bold; }
        .profile-name { font-size: 18px; font-weight: bold; color: #fff; }
        .profile-handle { font-size: 12px; color: #aaa; margin-top: 2px; }
        .view-channel-link { font-size: 13px; color: #3ea6ff; text-decoration: none; font-weight: 500; }

        .menu-list-item { display: flex; align-items: center; gap: 16px; padding: 12px 16px; text-decoration: none; color: #fff; font-size: 14px; font-weight: 500; border-bottom: 1px solid #1a1a1a; }
        .menu-list-item svg { width: 22px; height: 22px; fill: none; stroke: #fff; stroke-width: 2; }

        .analytics-card { background: #1a1a1a; border-radius: 12px; padding: 16px; margin: 16px; border: 1px solid #333; }
        .analytics-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 12px; }
        .analytic-box { background: #262626; padding: 12px; border-radius: 8px; border: 1px solid #3f3f3f; }
        .analytic-label { font-size: 11px; color: #aaa; }
        .analytic-val { font-size: 18px; font-weight: bold; color: #fff; margin-top: 4px; }

        .bottom-nav { position: fixed; bottom: 0; left: 0; width: 100%; height: 56px; background: #0f0f0f; border-top: 1px solid #272727; display: flex; justify-content: space-around; align-items: center; z-index: 1000; }
        .nav-item { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; text-decoration: none; color: #aaa; font-size: 10px; gap: 3px; height: 100%; cursor: pointer; }
        .nav-item svg { width: 22px; height: 22px; fill: none; stroke: #aaa; stroke-width: 2; }
        .nav-item.active { color: #fff; font-weight: bold; }
        .nav-item.active svg { stroke: #fff; fill: #fff; }
        
        .upload-plus-btn { background: #272727; width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 1px solid #3f3f3f; }
        .upload-plus-btn svg { width: 20px; height: 20px; fill: none; stroke: #fff; stroke-width: 2; }

        .modal-overlay { display: none; position: fixed; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.8); z-index: 1099; }
        .modal { display: none; position: fixed; bottom: 0; left: 0; width: 100%; background: #1f1f1f; border-top-left-radius: 16px; border-top-right-radius: 16px; padding: 20px; z-index: 1100; max-height: 85vh; overflow-y: auto; color: #fff; border-top: 1px solid #333; }
        .btn-large { background: #cc0000; color: white; border: none; padding: 12px; border-radius: 20px; width: 100%; font-size: 14px; font-weight: bold; margin-top: 10px; cursor: pointer; }
        .create-menu-item { display: flex; align-items: center; gap: 14px; padding: 14px; background: #262626; border-radius: 12px; margin-bottom: 10px; text-decoration: none; color: #fff; font-weight: 600; font-size: 14px; cursor: pointer; border: 1px solid #333; }
        .create-menu-item svg { width: 22px; height: 22px; fill: none; stroke: #ff0000; stroke-width: 2; }
    </style>
</head>
<body>

    {% if page == 'auth' %}
        <div style="max-width: 400px; margin: 80px auto; background: #1f1f1f; padding: 24px; border-radius: 12px; border: 1px solid #333;">
            <h2 style="text-align: center; margin-bottom: 20px;">Flixify Pro Login</h2>
            {% if error %}<p style="color: #ff4444; font-size: 13px; text-align: center; margin-bottom: 10px;">{{ error }}</p>{% endif %}
            <form action="/login" method="post">
                <label style="font-size: 12px; color: #aaa;">Username</label>
                <input type="text" name="username" required style="width:100%; padding:10px; background:#333; border:1px solid #444; color:#fff; border-radius:6px; margin-bottom:12px; margin-top:4px;">
                <label style="font-size: 12px; color: #aaa;">Password</label>
                <input type="password" name="password" required style="width:100%; padding:10px; background:#333; border:1px solid #444; color:#fff; border-radius:6px; margin-bottom:16px; margin-top:4px;">
                <button type="submit" class="btn-large">Login</button>
            </form>
            <p style="text-align: center; margin-top: 16px; font-size: 13px; color: #aaa;">
                Don't have an account? <a href="/signup" style="color: #3ea6ff; text-decoration: none;">Sign Up</a>
            </p>
        </div>
    {% elif page == 'signup' %}
        <div style="max-width: 400px; margin: 80px auto; background: #1f1f1f; padding: 24px; border-radius: 12px; border: 1px solid #333;">
            <h2 style="text-align: center; margin-bottom: 20px;">Create Pro Account</h2>
            {% if error %}<p style="color: #ff4444; font-size: 13px; text-align: center; margin-bottom: 10px;">{{ error }}</p>{% endif %}
            <form action="/signup" method="post">
                <label style="font-size: 12px; color: #aaa;">Username</label>
                <input type="text" name="username" required style="width:100%; padding:10px; background:#333; border:1px solid #444; color:#fff; border-radius:6px; margin-bottom:12px; margin-top:4px;">
                <label style="font-size: 12px; color: #aaa;">Password</label>
                <input type="password" name="password" required style="width:100%; padding:10px; background:#333; border:1px solid #444; color:#fff; border-radius:6px; margin-bottom:16px; margin-top:4px;">
                <button type="submit" class="btn-large" style="background: #3ea6ff; color: #000;">Sign Up</button>
            </form>
            <p style="text-align: center; margin-top: 16px; font-size: 13px; color: #aaa;">
                Already have an account? <a href="/login" style="color: #3ea6ff; text-decoration: none;">Login</a>
            </p>
        </div>
    {% elif page == 'creator_studio' %}
        <div class="max-w-5xl mx-auto my-8 p-6 bg-gray-800 rounded-xl shadow-lg border border-gray-700 space-y-8 text-white">
            <div class="flex justify-between items-center border-b border-gray-700 pb-4">
                <h1 class="text-3xl font-bold">Creator Studio - Unified Publishing</h1>
                <a href="/" class="text-blue-400 hover:underline text-sm">&larr; Back to Home</a>
            </div>

            <form action="/creator-studio" method="POST" enctype="multipart/form-data" class="space-y-8">
                <!-- SECTION 1: AUDIO SELECTION & SOUNDS LIBRARY -->
                <div class="bg-gray-900 p-6 rounded-lg border border-gray-700 space-y-4">
                    <h2 class="text-xl font-semibold flex items-center justify-between">
                        <span>🎵 Audio Selection & Sounds Library</span>
                        <button type="button" class="text-xs bg-purple-600 hover:bg-purple-700 px-3 py-1.5 rounded-lg font-medium transition">✨ Create Music (AI)</button>
                    </h2>

                    <div class="flex flex-col md:flex-row gap-3">
                        <input type="text" placeholder="Search background tracks or songs..." 
                            class="flex-1 bg-gray-800 border border-gray-700 rounded-lg p-2.5 text-sm focus:outline-none focus:border-blue-500 text-white">
                        <div class="flex gap-2 overflow-x-auto pb-1">
                            <span class="px-3 py-1 bg-blue-600 text-xs rounded-full cursor-pointer flex items-center">All</span>
                            <span class="px-3 py-1 bg-gray-800 hover:bg-gray-700 text-xs rounded-full cursor-pointer flex items-center border border-gray-700">Hindi</span>
                            <span class="px-3 py-1 bg-gray-800 hover:bg-gray-700 text-xs rounded-full cursor-pointer flex items-center border border-gray-700">Punjabi</span>
                        </div>
                    </div>

                    <div class="space-y-2 pt-2">
                        <div class="flex space-x-4 border-b border-gray-700 pb-2 text-sm">
                            <button type="button" class="text-blue-400 font-semibold border-b-2 border-blue-400 pb-1">Browse</button>
                            <button type="button" class="text-gray-400 hover:text-white pb-1">Saved (Favorites)</button>
                        </div>

                        <div class="flex items-center justify-between bg-gray-800 p-3 rounded-lg border border-gray-700">
                            <div class="flex items-center space-x-3">
                                <div class="w-10 h-10 bg-blue-600 rounded flex items-center justify-center font-bold text-sm">▶</div>
                                <div>
                                    <p class="font-medium text-sm">Electric Summer Vibe</p>
                                    <p class="text-xs text-gray-400">Artist: SoundWave • 1:00 • 4.4 lakh Shorts</p>
                                </div>
                            </div>
                            <div class="flex items-center space-x-2">
                                <input type="radio" name="selected_audio_track" value="track_1" class="w-4 h-4 text-blue-600" required>
                                <span class="text-xs text-gray-400">Use Sound</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- SECTION 2: UPLOAD & METADATA DETAILS SCREEN -->
                <div class="space-y-6">
                    <h2 class="text-xl font-semibold border-b border-gray-700 pb-2">📤 Short Metadata & Publishing</h2>

                    <div class="flex items-center space-x-4">
                        <div class="w-12 h-12 bg-gray-700 rounded-full flex items-center justify-center font-bold text-lg">
                            {{ user['username'][0]|upper if user else 'M' }}
                        </div>
                        <div>
                            <p class="font-semibold">{{ user['username'] if user else 'Creator' }}</p>
                            <p class="text-sm text-gray-400">{{ user['handle'] if user else '@creator' }}</p>
                        </div>
                    </div>

                    <div>
                        <label class="block text-sm font-medium mb-2">Caption your Short</label>
                        <input type="text" name="title" required placeholder="Add a catchy title or caption..." 
                            class="w-full bg-gray-900 border border-gray-700 rounded-lg p-3 text-sm focus:outline-none focus:border-blue-500 text-white">
                    </div>

                    <div>
                        <label class="block text-sm font-medium mb-2">Description & Hashtags</label>
                        <textarea name="description" rows="3" placeholder="Tell viewers about your short (#shorts, #trending)..."
                            class="w-full bg-gray-900 border border-gray-700 rounded-lg p-3 text-sm focus:outline-none focus:border-blue-500 text-white"></textarea>
                    </div>

                    <div>
                        <label class="block text-sm font-medium mb-2">Thumbnail Selector</label>
                        <input type="file" name="thumbnail" accept="image/*" class="block w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700">
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label class="block text-sm font-medium mb-2">Visibility</label>
                            <select name="visibility" class="w-full bg-gray-900 border border-gray-700 rounded-lg p-3 text-sm focus:outline-none text-white">
                                <option value="Public">Public</option>
                                <option value="Unlisted">Unlisted</option>
                                <option value="Private">Private</option>
                                <option value="Schedule">Schedule</option>
                            </select>
                        </div>

                        <div>
                            <label class="block text-sm font-medium mb-2">Audience (COPPA Compliance)</label>
                            <select name="audience" class="w-full bg-gray-900 border border-gray-700 rounded-lg p-3 text-sm focus:outline-none text-white">
                                <option value="not_made_for_kids">No, not made for kids</option>
                                <option value="made_for_kids">Yes, made for kids</option>
                            </select>
                        </div>
                    </div>

                    <div class="space-y-3 bg-gray-900 p-4 rounded-lg border border-gray-700">
                        <div class="flex items-center justify-between">
                            <span class="text-sm">Paid Promotion Disclosure</span>
                            <input type="checkbox" name="paid_promotion" class="w-4 h-4 text-blue-600 bg-gray-800 border-gray-700 rounded">
                        </div>
                        <div class="flex items-center justify-between">
                            <span class="text-sm">Allow Video & Audio Remixing</span>
                            <input type="checkbox" name="allow_remix" checked class="w-4 h-4 text-blue-600 bg-gray-800 border-gray-700 rounded">
                        </div>
                    </div>

                    <div class="flex items-center justify-end space-x-4 pt-4 border-t border-gray-700">
                        <button type="submit" name="action" value="draft" class="px-5 py-2.5 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm font-medium transition">Save Draft</button>
                        <button type="submit" name="action" value="publish" class="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-semibold transition">Upload Short</button>
                    </div>
                </div>
            </form>
        </div>
    {% else %}

    <header>
        <div style="display:flex; align-items:center; gap:8px;">
            <div class="icon-btn" onclick="openSidebarDrawer()">
                <svg viewBox="0 0 24 24"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
            </div>
            <a href="/" class="logo-container">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="background: #000; border-radius: 4px; padding: 2px;">
                    <path d="M5 3V21H8V14H16V11H8V6H19V3H5Z" fill="#E50914"/>
                </svg>
                <span style="font-size: 9px; font-weight: 600; color: #f1f1f1; letter-spacing: 0.5px;">Flixify Pro</span>
            </a>
        </div>
        
        <div class="search-box-container" onclick="openSearchOverlay()">
            <svg class="search-icon" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            <input type="text" placeholder="Search Master & AI" readonly>
        </div>

        <div class="header-icons">
            <a href="/notifications" class="icon-btn">
                <svg viewBox="0 0 24 24"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
                <span class="notif-badge">3</span>
            </a>
            <a href="/logout" class="icon-btn" title="Logout" style="color:#ff4444;">
                <svg viewBox="0 0 24 24" style="stroke:#ff4444;"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
            </a>
        </div>
    </header>

    <!-- Sidebar Drawer Categories Overlay & Menu -->
    <div id="sidebarOverlay" class="modal-overlay" onclick="closeSidebarDrawer()"></div>
    <div id="sidebarDrawer" style="display:none; position:fixed; top:0; left:0; width:280px; height:100%; background:#1f1f1f; z-index:2500; overflow-y:auto; padding:16px; border-right:1px solid #333;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; border-bottom:1px solid #333; padding-bottom:10px;">
            <h3 style="font-size:16px;">Sidebar Categories</h3>
            <div class="icon-btn" onclick="closeSidebarDrawer()"><svg viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></div>
        </div>
        <a href="/?cat=Shopping" class="menu-list-item"><svg viewBox="0 0 24 24"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>Shopping (Merchandise)</a>
        <a href="/?cat=Music" class="menu-list-item"><svg viewBox="0 0 24 24"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>Music Hub</a>
        <a href="/?cat=Movies" class="menu-list-item"><svg viewBox="0 0 24 24"><rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"/><line x1="7" y1="2" x2="7" y2="22"/><line x1="17" y1="2" x2="17" y2="22"/><line x1="2" y1="12" x2="22" y2="12"/></svg>Movies & TV Shows</a>
        <a href="/?cat=Hype" class="menu-list-item"><svg viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>Hype (Trending Creator Support)</a>
        <a href="/live" class="menu-list-item"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="3"/></svg>Live Broadcasting Streams</a>
        <a href="/?cat=Gaming" class="menu-list-item"><svg viewBox="0 0 24 24"><rect x="2" y="6" width="20" height="12" rx="2"/><path d="M6 12h4m-2-2v4m8-2h.01m2 0h.01"/></svg>Gaming</a>
        <a href="/?cat=Podcasts" class="menu-list-item"><svg viewBox="0 0 24 24"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v1a7 7 0 0 1-14 0v-1"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>Podcasts & Playables</a>
        <a href="/creator-studio" class="menu-list-item" style="color:#3ea6ff;"><svg viewBox="0 0 24 24" style="stroke:#3ea6ff;"><polygon points="5 3 19 12 5 21 5 3"/></svg>Creator Studio & Audio Library</a>
        <hr style="border:0; border-top:1px solid #333; margin:12px 0;">
        <a href="/edit_profile" class="menu-list-item"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>Settings & Configurations</a>
    </div>

    <div id="searchOverlay">
        <div class="search-top-bar">
            <div class="icon-btn" onclick="closeSearchOverlay()">
                <svg viewBox="0 0 24 24"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
            </div>
            <form action="/" method="get" class="search-input-box">
                <input type="text" name="q" id="searchInputField" placeholder="Search Videos, 360/VR, HDR, Podcasts..." value="{{ search_q }}" autocomplete="off" autofocus>
                <button type="submit" style="background:none; border:none; cursor:pointer; display:flex;">
                    <svg class="search-icon" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                </button>
            </form>
        </div>
        <div style="padding: 16px;">
            <h4 style="font-size: 13px; color: #aaa; margin-bottom: 8px;">AI & Pro Ecosystem Filters</h4>
            <div style="display:flex; gap: 8px; flex-wrap: wrap;">
                <a href="/?filter=new_to_you" class="chip">✨ New to you</a>
                <a href="/?filter=hdr" class="chip">HDR10 / Dolby Vision</a>
                <a href="/?filter=vr" class="chip">360° & VR</a>
                <a href="/?filter=live" class="chip" style="background:#cc0000; color:#fff;">Live Ultra-Low Latency</a>
            </div>
        </div>
    </div>

    {% if page == 'home' %}
        <div class="chips-wrapper">
            <a href="/" class="chip {% if not current_cat %}active{% endif %}">All</a>
            <a href="/?cat=Subscriptions" class="chip {% if current_cat == 'Subscriptions' %}active{% endif %}">Subscriptions</a>
            <a href="/?cat=Gaming" class="chip {% if current_cat == 'Gaming' %}active{% endif %}">Gaming</a>
            <a href="/?cat=Music" class="chip {% if current_cat == 'Music' %}active{% endif %}">Music</a>
            <a href="/?cat=Podcasts" class="chip {% if current_cat == 'Podcasts' %}active{% endif %}">Podcasts</a>
            <a href="/shorts" class="chip">Shorts</a>
            <a href="/community" class="chip">Community</a>
            <a href="/live" class="chip" style="background:#cc0000; color:#fff;">Live Studio</a>
        </div>

        <div class="feed" id="mainFeedContainer">
            {% for v in videos %}
            <div class="video-card">
                <a href="/watch/{{ v['id'] }}" class="thumb-box">
                    <video preload="metadata" muted><source src="/videos/{{ v['filename'] }}" type="video/mp4"></video>
                </a>
                <div class="v-info-box">
                    <a href="/channel/{{ v['user_id'] }}" class="channel-avatar">{{ v['username'][0]|upper if v['username'] else 'F' }}</a>
                    <div class="v-details">
                        <a href="/watch/{{ v['id'] }}" style="text-decoration:none; color:inherit;">
                            <div class="v-title">{{ v['title'] }}</div>
                        </a>
                        <div class="v-meta">
                            <span>{{ v['username'] if v['username'] else 'Creator' }}</span> • <span>{{ v['views'] }} views</span> • <span>{{ v['category'] }}</span>
                            {% if v['hdr_enabled'] %} • <span style="color:#3ea6ff;">HDR</span>{% endif %}
                        </div>
                    </div>
                </div>
            </div>
            {% else %}
            <p style="padding:40px; text-align:center; color:#aaa;">No long videos found. Upload via '+' button with advanced pro controls!</p>
            {% endfor %}
        </div>

    {% elif page == 'shorts_feed' %}
        <div class="shorts-feed-container">
            {% for v in shorts %}
            <div class="short-card-item">
                <video id="short_vid_{{ v['id'] }}" loop preload="auto" onclick="location.href='/watch/{{ v['id'] }}'" style="width:100%; height:100%; object-fit:cover;"><source src="/videos/{{ v['filename'] }}" type="video/mp4"></video>
                
                <div class="short-sidebar">
                    <button onclick="likeShortAjax({{ v['id'] }})" class="short-side-btn">
                        <svg viewBox="0 0 24 24"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/></svg>
                        <span id="shortLikeCount_{{ v['id'] }}">{{ v['likes'] }}</span>
                    </button>
                    <a href="/watch/{{ v['id'] }}" class="short-side-btn">
                        <svg viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                        <span>Watch</span>
                    </a>
                </div>

                <div class="short-bottom-info">
                    <div class="short-ch-row">
                        <a href="/channel/{{ v['user_id'] }}" class="short-avatar">{{ v['username'][0]|upper if v['username'] else 'F' }}</a>
                        <b style="font-size:14px;">@{{ v['username'] if v['username'] else 'Creator' }}</b>
                    </div>
                    <a href="/watch/{{ v['id'] }}" style="text-decoration:none; color:inherit;">
                        <p style="font-size:13px; margin-bottom:6px;">{{ v['title'] }}</p>
                    </a>
                </div>
            </div>
            {% else %}
            <div style="padding:100px 20px; text-align:center; color:#aaa;">No Shorts available yet.</div>
            {% endfor %}
        </div>
        <script>
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    const vid = entry.target;
                    if (entry.isIntersecting) { vid.play().catch(e => {}); } else { vid.pause(); }
                });
            }, { threshold: 0.6 });
            document.querySelectorAll('.short-card-item video').forEach(v => observer.observe(v));
            function likeShortAjax(vidId) {
                fetch('/api/like/' + vidId).then(res => res.json()).then(data => {
                    document.getElementById('shortLikeCount_' + vidId).innerText = data.likes;
                });
            }
        </script>

    {% elif page == 'channel' %}
        <div style="padding:16px;">
            <div style="display:flex; align-items:center; gap:14px; margin-bottom:16px;">
                <div style="width:60px; height:60px; border-radius:50%; background:#cc0000; display:flex; align-items:center; justify-content:center; font-size:24px; font-weight:bold; color:#fff;">{{ channel['username'][0]|upper }}</div>
                <div>
                    <h2 style="font-size:18px;">{{ channel['username'] }}</h2>
                    <p style="font-size:12px; color:#aaa;">{{ channel['handle'] }} • {{ channel['subscribers'] }} subscribers</p>
                </div>
            </div>
            <p style="font-size:13px; color:#ddd; margin-bottom:16px;">{{ channel['bio'] }}</p>
            <div style="display:flex; gap:10px;">
                <button onclick="toggleSubscribeAjax({{ channel['id'] }})" id="subscribeBtnEl" class="action-btn" style="background:#fff; color:#000; font-weight:bold; flex:1; justify-content:center; border:none; padding:10px;">
                    {% if is_subscribed %}Subscribed ✓{% else %}Subscribe{% endif %}
                </button>
                <a href="/membership/{{ channel['id'] }}" class="action-btn" style="background:#cc0000; color:#fff; font-weight:bold; justify-content:center; padding:10px; text-decoration:none;">Join Memberships</a>
            </div>
        </div>
        <script>
            function toggleSubscribeAjax(channelId) {
                fetch('/api/subscribe/' + channelId).then(res => res.json()).then(data => {
                    const btn = document.getElementById('subscribeBtnEl');
                    if (data.subscribed) { btn.innerText = "Subscribed ✓"; } else { btn.innerText = "Subscribe"; }
                });
            }
        </script>

    {% elif page == 'membership' %}
        <div style="padding:16px; text-align:center;">
            <h2>Channel Memberships & Tiers</h2>
            <p style="font-size:13px; color:#aaa; margin-top:4px;">Custom loyalty badges, exclusive member chat rooms, and perks.</p>
            <div style="background:#1a1a1a; border:1px solid #333; padding:16px; border-radius:12px; margin-top:20px;">
                <h3>Tier 1: VIP Supporter</h3>
                <p style="font-size:12px; color:#3ea6ff; margin:6px 0;">$4.99 / month</p>
                <p style="font-size:13px; color:#ddd;">Custom emojis, loyalty badges, exclusive member-only live chat streams.</p>
                <form action="/join_membership/{{ channel_id }}" method="post" style="margin-top:12px;">
                    <button type="submit" class="btn-large">Join Tier 1 Membership</button>
                </form>
            </div>
        </div>

    {% elif page == 'community' %}
        <div style="padding:16px;">
            <h3>Community Tab & Live Polls</h3>
            <form action="/add_community_post" method="post" style="margin:12px 0;">
                <textarea name="content" placeholder="Share updates, polls or announcements with your fans..." style="width:100%; padding:10px; background:#222; border:1px solid #444; color:#fff; border-radius:8px;" required></textarea>
                <button type="submit" class="btn-large" style="margin-top:6px;">Post to Community</button>
            </form>
            {% for p in posts %}
                <div style="background:#1a1a1a; padding:12px; border-radius:8px; margin-bottom:12px; border:1px solid #333;">
                    <b>Creator Post</b>
                    <p style="margin-top:6px; font-size:14px;">{{ p['content'] }}</p>
                </div>
            {% endfor %}
        </div>

    {% elif page == 'notifications' %}
        <div style="padding:16px;">
            <h3>Notification Center</h3>
            {% for n in notifications %}
            <div style="background:#1a1a1a; padding:12px; border-radius:8px; margin-bottom:10px; font-size:13px; border:1px solid #333;">
                <div>{{ n['message'] }}</div>
            </div>
            {% endfor %}
        </div>

    {% elif page == 'you' %}
        <div class="profile-header">
            <div class="profile-user-info">
                <div class="profile-avatar">{{ user['username'][0]|upper }}</div>
                <div>
                    <div class="profile-name">{{ user['username'] }}</div>
                    <div class="profile-handle">{{ user['handle'] }} • <a href="/channel/{{ user['id'] }}" class="view-channel-link">View channel ></a></div>
                </div>
            </div>
        </div>

        <a href="/edit_profile" class="menu-list-item">
            <svg viewBox="0 0 24 24"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            Settings, Account, Privacy & Parental Controls
        </a>

        <div class="analytics-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h4 style="font-size:15px; font-weight:bold;">Studio Analytics & Fintech Payouts</h4>
                <a href="/studio" style="font-size:12px; color:#3ea6ff; text-decoration:none; font-weight:600;">Advanced mode ></a>
            </div>
            <div class="analytics-grid">
                <div class="analytic-box">
                    <div class="analytic-label">Channel Balance & Payouts</div>
                    <div class="analytic-val" style="color:#2ba640;">${{ user['balance'] }}</div>
                </div>
                <div class="analytic-box">
                    <div class="analytic-label">Subscribers</div>
                    <div class="analytic-val">{{ user['subscribers'] }}</div>
                </div>
            </div>
        </div>

        <a href="/my_videos" class="menu-list-item">
            <svg viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"/></svg>
            Your videos & AI Thumbnail Studio / A/B Testing
        </a>
        <a href="/downloads" class="menu-list-item">
            <svg viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            Offline Downloads & Encrypted Storage
        </a>
        <a href="/history" class="menu-list-item">
            <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            Watch History & Device Remote Sign-Out
        </a>

    {% elif page == 'history' %}
        <div style="padding:16px;">
            <h2>Watch History & Device Security</h2>
            <div style="margin:10px 0; display:flex; gap:10px;">
                <a href="/clear_history" class="action-btn" style="background:#cc0000; color:#fff; text-decoration:none;">Clear All History</a>
                <button onclick="alert('All active remote sessions signed out successfully except current device.')" class="action-btn" style="background:#272727; color:#fff;">Remote Device Sign-Out</button>
            </div>
            <div class="feed" style="margin-top:16px;">
                {% for v in history_videos %}
                <div class="video-card">
                    <a href="/watch/{{ v['id'] }}" class="thumb-box"><video preload="metadata"><source src="/videos/{{ v['filename'] }}" type="video/mp4"></video></a>
                    <div class="v-info-box"><div class="v-details"><div class="v-title">{{ v['title'] }}</div><div class="v-meta"><span>Watched recently</span></div></div></div>
                </div>
                {% else %}
                <p style="color:#aaa; padding:20px 0;">No watch history recorded yet.</p>
                {% endfor %}
            </div>
        </div>

    {% elif page == 'edit_profile' %}
        <div style="padding:16px;">
            <h2>Settings, Account & Configuration Hub</h2>
            <form action="/edit_profile" method="post" style="margin-top:16px;">
                <label style="font-size:12px; color:#aaa;">Username / Handle</label>
                <input type="text" name="username" value="{{ user['username'] }}" required style="width:100%; padding:10px; background:#222; border:1px solid #444; color:#fff; border-radius:6px; margin-top:4px; margin-bottom:12px;">
                
                <label style="font-size:12px; color:#aaa;">Channel Bio</label>
                <textarea name="bio" rows="3" style="width:100%; padding:10px; background:#222; border:1px solid #444; color:#fff; border-radius:6px; margin-top:4px; margin-bottom:12px;">{{ user['bio'] }}</textarea>

                <h4 style="font-size:14px; margin:14px 0 6px 0; color:#3ea6ff;">General & Playback Settings</h4>
                <div style="display:flex; justify-content:space-between; align-items:center; background:#1a1a1a; padding:10px; border-radius:6px; margin-bottom:8px;">
                    <span style="font-size:13px;">Dark Mode Theme</span>
                    <input type="checkbox" checked disabled>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; background:#1a1a1a; padding:10px; border-radius:6px; margin-bottom:8px;">
                    <span style="font-size:13px;">Data Saver / Cellular Limits</span>
                    <input type="checkbox" name="data_saver" value="1" {% if user['data_saver'] %}checked{% endif %}>
                </div>

                <label style="font-size:12px; color:#aaa; margin-top:8px; display:block;">Restricted Mode / Parental Controls (Family Centre)</label>
                <select name="parental_control" style="width:100%; padding:10px; background:#222; border:1px solid #444; color:#fff; border-radius:6px; margin-top:4px; margin-bottom:16px;">
                    <option value="Off" {% if user['parental_control'] == 'Off' %}selected{% endif %}>Off</option>
                    <option value="Strict" {% if user['parental_control'] == 'Strict' %}selected{% endif %}>Strict (YouTube Kids / Restricted Mode)</option>
                </select>

                <button type="submit" class="btn-large">Save All Configurations</button>
            </form>
        </div>

    {% elif page == 'studio' %}
        <div style="padding:16px;">
            <h2>Creator Studio & Fintech Payout Dashboard</h2>
            <p style="font-size:13px; color:#aaa; margin-top:4px;">Manage analytics, multi-currency payouts, tax compliance & BrandConnect</p>
            
            <div class="analytics-card" style="margin:16px 0;">
                <h4>Monetization & Tax Eligibility (W-8BEN / W-9)</h4>
                <div style="font-size:13px; color:#2ba640; margin-top:6px;">✓ Tax Form Verified & Approved</div>
                <div style="font-size:13px; color:#aaa; margin-top:4px;">Subscribers: {{ user['subscribers'] }} / 1,000 required</div>
            </div>

            <div class="analytics-card" style="margin:16px 0;">
                <h4>Channel Overview & Multi-Currency Payouts</h4>
                <div class="analytics-grid">
                    <div class="analytic-box"><div class="analytic-label">Total Views</div><div class="analytic-val">{{ total_views }}</div></div>
                    <div class="analytic-box"><div class="analytic-label">Multi-Currency Balance</div><div class="analytic-val" style="color:#2ba640;">${{ user['balance'] }} USD</div></div>
                </div>
                <button onclick="alert('Initiated secure bank wire / crypto digital wallet transfer payout!')" class="btn-large" style="background:#3ea6ff; color:#000; margin-top:12px;">Request Instant Payout</button>
            </div>

            <div class="analytics-card" style="margin:16px 0;">
                <h4>BrandConnect Sponsorship Marketplace</h4>
                <p style="font-size:13px; color:#ddd; margin-top:4px;">Direct portal connecting verified creators with global brand deals.</p>
                <button onclick="alert('Matched with 2 brand sponsorship campaigns! Check notifications.')" class="action-btn" style="background:#272727; color:#fff; margin-top:10px;">Browse Brand Deals</button>
            </div>

            <div class="analytics-card" style="margin:16px 0;">
                <h4>Views Growth Graph</h4>
                <div style="height: 200px; margin-top: 10px;">
                    <canvas id="studioAnalyticsChart"></canvas>
                </div>
            </div>
        </div>
        <script>
            const ctx = document.getElementById('studioAnalyticsChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                    datasets: [{
                        label: 'Views Growth',
                        data: [120, 300, 250, 450, 600, 850, {{ total_views if total_views > 0 else 100 }}],
                        borderColor: '#3ea6ff',
                        backgroundColor: 'rgba(62, 166, 255, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.3
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { grid: { color: '#333' }, ticks: { color: '#aaa' } },
                        y: { grid: { color: '#333' }, ticks: { color: '#aaa' } }
                    }
                }
            });
        </script>

    {% elif page == 'live' %}
        <div style="padding:16px;">
            <h2>Enterprise Live Streaming Control Room</h2>
            <p style="font-size:13px; color:#aaa; margin-top:4px;">4K 60FPS Ultra-Low Latency & Multi-Stream Simulcasting</p>
            <div class="analytics-card" style="margin:16px 0;">
                <label style="font-size:12px; color:#aaa;">Server RTMP URL</label>
                <input type="text" value="rtmp://live.flixifycloud.io/app" readonly style="width:100%; padding:8px; background:#222; border:1px solid #444; color:#fff; border-radius:6px; margin:4px 0 12px 0;">
                <label style="font-size:12px; color:#aaa;">Stream Key (Keep Secret)</label>
                <input type="text" value="live_sec_{{ user['id'] }}_983210" readonly style="width:100%; padding:8px; background:#222; border:1px solid #444; color:#fff; border-radius:6px; margin:4px 0 12px 0;">
                <label style="font-size:12px; color:#aaa;">Simulcast Output Destinations</label>
                <input type="text" value="YouTube Live, Twitch, Kick, Custom RTMP" readonly style="width:100%; padding:8px; background:#222; border:1px solid #444; color:#fff; border-radius:6px; margin:4px 0 12px 0;">
                <div style="font-size:13px; color:#2ba640;">● Ultra-Low Latency Stream Status: Healthy (42 Live Viewers)</div>
            </div>
        </div>

    {% elif page == 'downloads' %}
        <div style="padding:16px;">
            <h2>Offline Downloads & Audio-Only Mode</h2>
            <p style="font-size:13px; color:#aaa; margin-top:4px;">Encrypted local storage with podcast audio-only bandwidth saver</p>
            <div class="feed" style="margin-top:16px;">
                {% for v in downloaded_videos %}
                <div class="video-card">
                    <a href="/watch/{{ v['id'] }}" class="thumb-box">
                        <video preload="metadata"><source src="/videos/{{ v['filename'] }}" type="video/mp4"></video>
                    </a>
                    <div class="v-info-box">
                        <div class="v-details">
                            <div class="v-title">{{ v['title'] }}</div>
                            <div class="v-meta"><span>Quality: {{ v['quality'] }} • Downloaded ✓</span></div>
                        </div>
                    </div>
                </div>
                {% else %}
                <p style="color:#aaa; padding:20px 0;">No offline downloads yet.</p>
                {% endfor %}
            </div>
        </div>

    {% elif page == 'watch' %}
        <div class="player-container" id="playerWrapper">
            <video id="mainVideoPlayer" class="main-video" controls playsinline autoplay {% if video['loop_enabled'] %}loop{% endif %}><source src="/videos/{{ video['filename'] }}" type="video/mp4"></video>
        </div>
        
        <div class="video-details-container">
            <h2 class="video-title">{{ video['title'] }}</h2>
            <div class="video-stats">{{ video['views'] }} views • Category: {{ video['category'] }} {% if video['hdr_enabled'] %}• HDR10+{% endif %}</div>

            <div class="channel-row">
                <a href="/channel/{{ video['user_id'] }}" class="channel-info">
                    <div class="channel-img">{{ video['username'][0]|upper if video['username'] else 'F' }}</div>
                    <div class="channel-name-sub">
                        <span class="channel-title">{{ video['username'] if video['username'] else 'Flixify Official' }}</span>
                        <span class="sub-count">1.2K subscribers</span>
                    </div>
                </a>
                <a href="/api/subscribe/{{ video['user_id'] }}" class="subscribe-btn" onclick="event.preventDefault(); fetch(this.href).then(r=>r.json()).then(d=>{location.reload();});">Subscribe</a>
            </div>

            <div class="action-buttons">
                <div class="like-dislike-group">
                    <a href="/api/like/{{ video['id'] }}" class="action-btn" onclick="event.preventDefault(); fetch(this.href).then(r=>r.json()).then(d=>{location.reload();});">
                        <i class="fas fa-thumbs-up"></i> {{ video['likes'] }}
                    </a>
                    <span class="divider"></span>
                    <button class="action-btn"><i class="fas fa-thumbs-down"></i></button>
                </div>
                <button class="action-btn" onclick="navigator.clipboard.writeText(window.location.href); alert('Link copied to clipboard!');"><i class="fas fa-share"></i> Share</button>
                <a href="/download_video/{{ video['id'] }}" class="action-btn"><i class="fas fa-download"></i> Download</a>
                <button class="action-btn" onclick="toggleAmbient()"><i class="fas fa-lightbulb"></i> Ambient</button>
                <button class="action-btn" onclick="triggerClip({{ video['id'] }})"><i class="fas fa-cut"></i> Clip</button>
                <a href="/super_thanks/{{ video['id'] }}" class="action-btn" style="background:#cc0000; color:#fff;"><i class="fas fa-heart"></i> Super Thanks</a>
            </div>

            <div class="description-box">
                <p><b>✨ AI Key Takeaways Summary:</b> Master video stream optimized with HDR pipeline and auto volume compressor.</p>
                <p style="margin-top:6px;">{{ video['description'] if video['description'] else 'Enjoy watching this pro master video.' }}</p>
                {% if video['tags'] %}<p style="font-size:11px; color:#3ea6ff; margin-top:6px;">Tags: {{ video['tags'] }}</p>{% endif %}
            </div>

            <div class="comments-section">
                <div class="comments-header">Comments & Timed Comments ({{ comments|length }})</div>
                <form action="/add_comment/{{ video['id'] }}" method="post" class="comment-input-box">
                    <input type="text" name="comment_text" placeholder="Add a comment (NLP auto-quarantine enabled)..." required>
                    <button type="submit" class="comment-submit-btn">Comment</button>
                </form>
                
                <div style="margin-top: 10px;">
                    {% for c in comments %}
                    <div class="comment-item">
                        <div class="comment-avatar">{{ c['user_name'][0]|upper if c['user_name'] else 'U' }}</div>
                        <div class="comment-content">
                            <div class="comment-user">{{ c['user_name'] }} {% if c['is_creator_heart'] %}❤️{% endif %}</div>
                            <div class="comment-text">{{ c['comment_text'] }}</div>
                        </div>
                    </div>
                    {% else %}
                    <p style="font-size:12px; color:#aaa; text-align:center; padding:10px;">No comments yet.</p>
                    {% endfor %}
                </div>
            </div>
        </div>
        <script>
            function toggleAmbient() {
                document.getElementById('playerWrapper').classList.toggle('ambient');
            }
            function triggerClip(vidId) {
                fetch('/api/clip/' + vidId).then(r=>r.json()).then(d => {
                    alert('Successfully created 15-second instant clip!');
                });
            }
        </script>
    {% endif %}

    <div class="bottom-nav">
        <a href="/" class="nav-item {% if page == 'home' %}active{% endif %}">
            <svg viewBox="0 0 24 24"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
            Home
        </a>
        <a href="/shorts" class="nav-item {% if page == 'shorts_feed' %}active{% endif %}">
            <svg viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"/></svg>
            Shorts
        </a>
        <div class="nav-item" onclick="openCreateMenu()"><div class="upload-plus-btn"><svg viewBox="0 0 24 24"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg></div></div>
        <a href="/community" class="nav-item {% if page == 'community' %}active{% endif %}">
            <svg viewBox="0 0 24 24"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>
            Community
        </a>
        <a href="/you" class="nav-item {% if page == 'you' %}active{% endif %}">
            <svg viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            You
        </a>
    </div>

    <div id="modalOverlay" class="modal-overlay" onclick="closeModals()"></div>
    <div id="createMenuModal" class="modal">
        <h3>Create & Short-Form Video Creation Suite</h3>
        <div class="create-menu-item" onclick="openUploadModal(0)">
            <svg viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"/></svg>
            Upload Long Video (AI Chapters, HDR, Thumbnails A/B)
        </div>
        <div class="create-menu-item" onclick="openUploadModal(1)">
            <svg viewBox="0 0 24 24"><rect x="2" y="2" width="20" height="20" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/></svg>
            Upload Short Video (With Gallery Grid & Trimmer)
        </div>
        <a href="/creator-studio" class="create-menu-item" style="text-decoration:none;">
            <svg viewBox="0 0 24 24"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
            Shorts & Audio Creator Studio (Unified)
        </a>
        <a href="/live" class="create-menu-item" style="text-decoration:none;">
            <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="3"/></svg>
            Go Live (4K 60FPS Ultra-Low Latency RTMP)
        </a>
    </div>
    
    <div id="uploadModal" class="modal">
        <h3>Upload Video Spec (AI & Pro Pipeline)</h3>
        <form action="/upload_video" method="post" enctype="multipart/form-data">
            <input type="hidden" name="is_short" id="isShortInput" value="0">
            
            <label style="font-size:12px; color:#aaa; display:block; margin-bottom:4px;">Select Video File (Gallery Grid & Trimmer Support)</label>
            <input type="file" name="video" accept="video/*" required style="margin-bottom:10px; width:100%;">
            
            <input type="text" name="title" placeholder="Title" required style="width:100%; padding:8px; background:#333; border:1px solid #444; color:#fff; border-radius:6px; margin-bottom:8px;">
            <textarea name="description" placeholder="Description with rich text and audio overlay settings..." style="width:100%; padding:8px; background:#333; border:1px solid #444; color:#fff; border-radius:6px; margin-bottom:8px;"></textarea>
            
            <label style="font-size:12px; color:#aaa;">Category</label>
            <select name="category" style="width:100%; padding:8px; background:#333; border:1px solid #444; color:#fff; border-radius:6px; margin-bottom:8px;">
                <option value="Gaming">Gaming</option>
                <option value="Music">Music</option>
                <option value="Podcasts">Podcasts</option>
                <option value="Tech">Tech</option>
                <option value="Shopping">Shopping</option>
                <option value="Movies">Movies & TV</option>
            </select>

            <label style="font-size:12px; color:#aaa;">Tags & Keywords</label>
            <input type="text" name="tags" placeholder="python, flask, 4k, shorts" style="width:100%; padding:8px; background:#333; border:1px solid #444; color:#fff; border-radius:6px; margin-bottom:8px;">

            <label style="font-size:12px; color:#aaa;">Visibility</label>
            <select name="visibility" style="width:100%; padding:8px; background:#333; border:1px solid #444; color:#fff; border-radius:6px; margin-bottom:12px;">
                <option value="Public">Public</option>
                <option value="Unlisted">Unlisted</option>
                <option value="Private">Private</option>
            </select>

            <button type="submit" class="btn-large">Publish / Save</button>
        </form>
    </div>

    <script>
        function openSearchOverlay() { document.getElementById('searchOverlay').style.display = 'block'; document.getElementById('searchInputField').focus(); }
        function closeSearchOverlay() { document.getElementById('searchOverlay').style.display = 'none'; }
        
        function openSidebarDrawer() { document.getElementById('sidebarOverlay').style.display = 'block'; document.getElementById('sidebarDrawer').style.display = 'block'; }
        function closeSidebarDrawer() { document.getElementById('sidebarOverlay').style.display = 'none'; document.getElementById('sidebarDrawer').style.display = 'none'; }

        function openCreateMenu() { document.getElementById('modalOverlay').style.display = 'block'; document.getElementById('createMenuModal').style.display = 'block'; }
        function openUploadModal(isShort) { document.getElementById('createMenuModal').style.display = 'none'; document.getElementById('uploadModal').style.display = 'block'; document.getElementById('isShortInput').value = isShort; }
        function closeModals() { document.getElementById('modalOverlay').style.display = 'none'; document.getElementById('createMenuModal').style.display = 'none'; document.getElementById('uploadModal').style.display = 'none'; closeSidebarDrawer(); }

        // Added script for upload button state handling
        document.addEventListener('submit', function(e) {
            var submitBtn = e.target.querySelector('button[type="submit"], input[type="submit"]');
            if(submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerText = "Uploading & Processing... Please Wait...";
                submitBtn.style.opacity = "0.7";
            }
        });
    </script>
    {% endif %}
</body>
</html>
"""

def get_current_user():
    if 'user_id' not in session:
        return None
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
    user_row = c.fetchone()
    conn.close()
    return user_row

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return redirect(url_for('home'))
        else:
            error = 'Invalid username or password!'
    return render_template_string(HTML_TEMPLATE, page='auth', error=error)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password)
        handle = f"@{username.lower().replace(' ', '')}"
        
        try:
            conn = get_db()
            c = conn.cursor()
            c.execute("INSERT INTO users (username, handle, password) VALUES (?, ?, ?)", (username, handle, hashed_password))
            conn.commit()
            user_id = c.lastrowid
            conn.close()
            
            session['user_id'] = user_id
            return redirect(url_for('home'))
        except sqlite3.IntegrityError:
            error = 'Username already taken. Choose another.'
    return render_template_string(HTML_TEMPLATE, page='signup', error=error)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/')
def home():
    user = get_current_user()
    if not user: return redirect(url_for('login'))
        
    cat_f = request.args.get('cat', '')
    q = request.args.get('q', '')
    filter_type = request.args.get('filter', '')
    
    conn = get_db()
    c = conn.cursor()
    
    if cat_f == 'Subscriptions':
        query = """SELECT videos.*, users.username FROM videos 
                   LEFT JOIN users ON videos.user_id = users.id 
                   JOIN subscriptions ON videos.user_id = subscriptions.channel_id 
                   WHERE subscriptions.user_id = ? AND videos.is_short = 0"""
        params = [user['id']]
    else:
        query = "SELECT videos.*, users.username FROM videos LEFT JOIN users ON videos.user_id = users.id WHERE videos.is_short = 0"
        params = []
        if q:
            query += " AND (videos.title LIKE ? OR videos.tags LIKE ?)"
            params.extend(['%'+q+'%', '%'+q+'%'])
        if cat_f:
            query += " AND videos.category = ?"
            params.append(cat_f)
        if filter_type == 'hdr':
            query += " AND videos.hdr_enabled = 1"
        elif filter_type == 'new_to_you':
            query += " ORDER BY RANDOM()"
            
    if filter_type != 'new_to_you':
        query += " ORDER BY videos.id DESC"
        
    c.execute(query, params)
    videos = c.fetchall()
    conn.close()
    return render_template_string(HTML_TEMPLATE, videos=videos, current_cat=cat_f, search_q=q, page='home', user=user)

@app.route('/shorts')
def shorts_feed():
    user = get_current_user()
    if not user: return redirect(url_for('login'))
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT videos.*, users.username FROM videos LEFT JOIN users ON videos.user_id = users.id WHERE videos.is_short = 1 ORDER BY videos.id DESC")
    shorts = c.fetchall()
    conn.close()
    return render_template_string(HTML_TEMPLATE, page='shorts_feed', shorts=shorts, user=user, search_q='')

@app.route('/notifications')
def notifications_page():
    user = get_current_user()
    if not user: return redirect(url_for('login'))
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM notifications WHERE user_id = ? ORDER BY id DESC", (user['id'],))
    notifications = c.fetchall()
    conn.close()
    return render_template_string(HTML_TEMPLATE, page='notifications', notifications=notifications, user=user, search_q='')

@app.route('/channel/<int:channel_id>')
def channel_profile(channel_id):
    user = get_current_user()
    if not user: return redirect(url_for('login'))
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (channel_id,))
    channel = c.fetchone()
    c.execute("SELECT * FROM subscriptions WHERE user_id = ? AND channel_id = ?", (user['id'], channel_id))
    is_subscribed = True if c.fetchone() else False
    conn.close()
    return render_template_string(HTML_TEMPLATE, page='channel', channel=channel, user=user, is_subscribed=is_subscribed, search_q='')

@app.route('/membership/<int:channel_id>')
def channel_membership(channel_id):
    user = get_current_user()
    if not user: return redirect(url_for('login'))
    return render_template_string(HTML_TEMPLATE, page='membership', user=user, channel_id=channel_id, search_q='')

@app.route('/join_membership/<int:channel_id>', methods=['POST'])
def join_membership(channel_id):
    user = get_current_user()
    if not user: return redirect(url_for('login'))
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO channel_memberships (user_id, channel_id, tier_level) VALUES (?, ?, 1)", (user['id'], channel_id))
    conn.commit()
    conn.close()
    return redirect(f'/channel/{channel_id}')

@app.route('/community')
def community_page():
    user = get_current_user()
    if not user: return redirect(url_for('login'))
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM community_posts ORDER BY id DESC")
    posts = c.fetchall()
    conn.close()
    return render_template_string(HTML_TEMPLATE, page='community', posts=posts, user=user, search_q='')

@app.route('/add_community_post', methods=['POST'])
def add_community_post():
    user = get_current_user()
    if not user: return redirect(url_for('login'))
    content = request.form.get('content', '')
    if content:
        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO community_posts (user_id, content, likes) VALUES (?, ?, 15)", (user['id'], content))
        conn.commit()
        conn.close()
    return redirect('/community')

@app.route('/you')
def profile_page():
    user = get_current_user()
    if not user: return redirect(url_for('login'))
    return render_template_string(HTML_TEMPLATE, page='you', user=user, search_q='')

@app.route('/history')
def watch_history():
    user = get_current_user()
    if not user: return redirect(url_for('login'))
    conn = get_db()
    c = conn.cursor()
    c.execute("""SELECT videos.* FROM watch_history 
                 JOIN videos ON watch_history.video_id = videos.id 
                 WHERE watch_history.user_id = ? ORDER BY watch_history.id DESC""", (user['id'],))
    history_videos = c.fetchall()
    conn.close()
    return render_template_string(HTML_TEMPLATE, page='history', history_videos=history_videos, user=user, search_q='')

@app.route('/clear_history')
def clear_history():
    user = get_current_user()
    if not user: return redirect(url_for('login'))
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM watch_history WHERE user_id = ?", (user['id'],))
    conn.commit()
    conn.close()
    return redirect('/you')

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    user = get_current_user()
    if not user: return redirect(url_for('login'))
    if request.method == 'POST':
        new_username = request.form.get('username')
        new_bio = request.form.get('bio')
        data_saver = 1 if request.form.get('data_saver') == '1' else 0
        parental_control = request.form.get('parental_control', 'Off')
        conn = get_db()
        c = conn.cursor()
        c.execute("UPDATE users SET username = ?, bio = ?, data_saver = ?, parental_control = ? WHERE id = ?", 
                  (new_username, new_bio, data_saver, parental_control, user['id']))
        conn.commit()
        conn.close()
        return redirect('/you')
    return render_template_string(HTML_TEMPLATE, page='edit_profile', user=user, search_q='')

@app.route('/studio')
def studio_dashboard():
    user = get_current_user()
    if not user: return redirect(url_for('login'))
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT SUM(views) as total_views FROM videos WHERE user_id = ?", (user['id'],))
    tv_res = c.fetchone()
    total_views = tv_res['total_views'] if tv_res and tv_res['total_views'] else 0
    conn.close()
    return render_template_string(HTML_TEMPLATE, page='studio', user=user, total_views=total_views, search_q='')

@app.route('/live')
def live_studio():
    user = get_current_user()
    if not user: return redirect(url_for('login'))
    return render_template_string(HTML_TEMPLATE, page='live', user=user, search_q='')

@app.route('/downloads')
def downloads_page():
    user = get_current_user()
    if not user: return redirect(url_for('login'))
    conn = get_db()
    c = conn.cursor()
    c.execute("""SELECT videos.*, downloads.quality FROM downloads 
                 JOIN videos ON downloads.video_id = videos.id 
                 WHERE downloads.user_id = ? ORDER BY downloads.id DESC""", (user['id'],))
    downloaded_videos = c.fetchall()
    conn.close()
    return render_template_string(HTML_TEMPLATE, page='downloads', downloaded_videos=downloaded_videos, user=user, search_q='')

@app.route('/download_video/<int:vid_id>')
def download_video(vid_id):
    user = get_current_user()
    if not user: return redirect(url_for('login'))
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO downloads (user_id, video_id, quality) VALUES (?, ?, '720p')", (user['id'], vid_id))
    conn.commit()
    conn.close()
    return redirect('/downloads')

@app.route('/super_thanks/<int:vid_id>')
def super_thanks(vid_id):
    user = get_current_user()
    if not user: return redirect(url_for('login'))
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance + 5.0 WHERE id = (SELECT user_id FROM videos WHERE id = ?)", (vid_id,))
    conn.commit()
    conn.close()
    return redirect(f'/watch/{vid_id}')

@app.route('/watch/<int:vid_id>')
def watch_page(vid_id):
    user = get_current_user()
    if not user: return redirect(url_for('login'))
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE videos SET views = views + 1 WHERE id = ?", (vid_id,))
    c.execute("INSERT INTO watch_history (user_id, video_id) VALUES (?, ?)", (user['id'], vid_id))
    conn.commit()
    c.execute("SELECT videos.*, users.username FROM videos LEFT JOIN users ON videos.user_id = users.id WHERE videos.id = ?", (vid_id,))
    video = c.fetchone()
    c.execute("SELECT * FROM comments WHERE video_id = ? ORDER BY id DESC", (vid_id,))
    comments = c.fetchall()
    conn.close()
    if not video: return redirect('/')
    return render_template_string(HTML_TEMPLATE, page='watch', video=video, comments=comments, user=user, search_q='')

@app.route('/add_comment/<int:vid_id>', methods=['POST'])
def add_comment(vid_id):
    user = get_current_user()
    if not user: return redirect(url_for('login'))
    comment_text = request.form.get('comment_text', '')
    if comment_text:
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT user_name FROM users WHERE id = ?", (user['id'],))
        u_data = c.fetchone()
        u_name = u_data['username'] if u_data else 'User'
        c.execute("INSERT INTO comments (video_id, user_id, user_name, comment_text) VALUES (?, ?, ?, ?)",
                  (vid_id, user['id'], u_name, comment_text))
        conn.commit()
        conn.close()
    return redirect(f'/watch/{vid_id}')

@app.route('/api/like/<int:vid_id>')
def api_like(vid_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE videos SET likes = likes + 1 WHERE id = ?", (vid_id,))
    conn.commit()
    c.execute("SELECT likes FROM videos WHERE id = ?", (vid_id,))
    res = c.fetchone()
    conn.close()
    return jsonify({'likes': res['likes'] if res else 0})

@app.route('/api/clip/<int:vid_id>')
def api_clip(vid_id):
    user = get_current_user()
    if not user: return jsonify({'status': 'unauthorized'})
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO clips (video_id, user_id, clip_title) VALUES (?, ?, 'Master Short Clip')", (vid_id, user['id']))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/api/subscribe/<int:channel_id>')
def api_subscribe(channel_id):
    user = get_current_user()
    if not user: return jsonify({'subscribed': False})
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM subscriptions WHERE user_id = ? AND channel_id = ?", (user['id'], channel_id))
    sub = c.fetchone()
    if sub:
        c.execute("DELETE FROM subscriptions WHERE user_id = ? AND channel_id = ?", (user['id'], channel_id))
        subscribed = False
    else:
        c.execute("INSERT INTO subscriptions (user_id, channel_id) VALUES (?, ?)", (user['id'], channel_id))
        subscribed = True
    conn.commit()
    conn.close()
    return jsonify({'subscribed': subscribed})

@app.route('/upload_video', methods=['POST'])
def upload_video():
    user = get_current_user()
    if not user: return redirect(url_for('login'))
    is_short = int(request.form.get('is_short', 0))
    category = request.form.get('category', 'Tech')
    tags = request.form.get('tags', '')
    visibility = request.form.get('visibility', 'Public')
    
    if 'video' in request.files:
        file = request.files['video']
        if file.filename != '':
            filepath = os.path.join(MEDIA_DIR, file.filename)
            file.save(filepath)
            process_video_with_ffmpeg(filepath, file.filename)
            file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
            title = request.form.get('title', file.filename)
            description = request.form.get('description', '')
            
            conn = get_db()
            c = conn.cursor()
            c.execute('INSERT INTO videos (filename, title, description, category, tags, visibility, user_id, is_short, file_size_mb, hdr_enabled) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)',
                      (file.filename, title, description, category, tags, visibility, user['id'], is_short, file_size_mb))
            conn.commit()
            conn.close()
    return redirect('/shorts' if is_short else '/')

@app.route('/creator-studio', methods=['GET', 'POST'])
def creator_studio():
    user = get_current_user()
    if not user: return redirect(url_for('login'))
    
    if request.method == 'POST':
        selected_audio = request.form.get('selected_audio_track')
        title = request.form.get('title')
        description = request.form.get('description')
        visibility = request.form.get('visibility')
        audience = request.form.get('audience')
        paid_promotion = True if request.form.get('paid_promotion') else False
        allow_remix = True if request.form.get('allow_remix') else False
        action_type = request.form.get('action')
        
        print("\n" + "="*40)
        print("--- UNIFIED PUBLISHING LOG ---")
        print(f"Selected Audio ID : {selected_audio}")
        print(f"Short Title       : {title}")
        print(f"Description       : {description}")
        print(get_current_user() and f"Visibility        : {visibility}")
        print(f"Audience          : {audience}")
        print(f"Paid Promotion    : {paid_promotion}")
        print(f"Allow Remix       : {allow_remix}")
        print(f"Action Type       : {action_type.upper() if action_type else 'UNKNOWN'}")
        print("="*40 + "\n")

        return redirect(url_for('creator_studio'))

    return render_template_string(HTML_TEMPLATE, page='creator_studio', user=user, search_q='')

@app.route('/videos/<filename>')
def serve_video(filename):
    return send_from_directory(MEDIA_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
