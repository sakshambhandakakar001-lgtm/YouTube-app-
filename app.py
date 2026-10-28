import os
import sqlite3
import subprocess
import time
import urllib.request
from datetime import datetime, timedelta
from flask import Flask, render_template, render_template_string, request, redirect, url_for, session, jsonify, send_from_directory, get_flashed_messages
from werkzeug.security import generate_password_hash, check_password_hash

import threading

def background_save(video_file, filepath):
    try:
        video_file.save(filepath)
    except Exception as e:
        print("Error saving file:", e)


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
        username TEXT,
        email TEXT UNIQUE,
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
        channel_id INTEGER,
        UNIQUE(user_id, channel_id)
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

    c.execute('''CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 1,
        author TEXT,
        avatar TEXT,
        content TEXT,
        category TEXT,
        mood TEXT,
        language TEXT,
        reactions INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS post_likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        post_id INTEGER,
        UNIQUE(user_id, post_id)
    )''')

    c.execute("UPDATE posts SET user_id = 1 WHERE user_id IS NULL")

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
        
        .profile-header { display: flex; align-items: center; justify-content: space-between; padding: 16px; border-bottom: 1px solid #272727; }
        .profile-user-info { display: flex; align-items: center; gap: 14px; }
        .profile-avatar { width: 64px; height: 64px; border-radius: 50%; background: #3ea6ff; color: #000; display: flex; align-items: center; justify-content: center; font-size: 26px; font-weight: bold; }
        .profile-name { font-size: 18px; font-weight: bold; color: #fff; }
        .profile-handle { font-size: 12px; color: #aaa; margin-top: 2px; }

        .menu-list-item { display: flex; align-items: center; gap: 16px; padding: 12px 16px; text-decoration: none; color: #fff; font-size: 14px; font-weight: 500; border-bottom: 1px solid #1a1a1a; }
        .menu-list-item svg { width: 22px; height: 22px; fill: none; stroke: #fff; stroke-width: 2; }

        .bottom-nav { position: fixed; bottom: 0; left: 0; width: 100%; height: 56px; background: #0f0f0f; border-top: 1px solid #272727; display: flex; justify-content: space-around; align-items: center; z-index: 1000; }
        .nav-item { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; text-decoration: none; color: #aaa; font-size: 10px; gap: 3px; height: 100%; cursor: pointer; }
        .nav-item svg { width: 22px; height: 22px; fill: none; stroke: #aaa; stroke-width: 2; }
        .nav-item.active { color: #fff; font-weight: bold; }
        .nav-item.active svg { stroke: #fff; fill: #fff; }
        
        .modal-overlay { display: none; position: fixed; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.8); z-index: 1099; }
        .btn-large { background: #cc0000; color: white; border: none; padding: 12px; border-radius: 20px; width: 100%; font-size: 14px; font-weight: bold; margin-top: 10px; cursor: pointer; }
    </style>
</head>
<body>

{% if page == 'auth' %}
<div style="max-width: 400px; margin: 80px auto; background: #181818; padding: 24px; border-radius: 16px; border: 1px solid #333;">
    <h2 style="text-align: center; margin-bottom: 20px;">Flixify Login</h2>
    {% if error %}
    <p style="color: #ff0000; font-size: 14px; text-align: center; margin-bottom: 10px;">{{ error }}</p>
    {% endif %}
    <form action="/login" method="post">
        <label style="font-size: 12px; color: #aaa;">Username / Email</label>
        <input type="text" name="username" required style="width: 100%; padding: 10px; background: #222; border: 1px solid #444; color: #fff; border-radius: 6px; margin-bottom: 15px;">
        <label style="font-size: 12px; color: #aaa;">Password</label>
        <input type="password" name="password" required style="width: 100%; padding: 10px; background: #222; border: 1px solid #444; color: #fff; border-radius: 6px; margin-bottom: 20px;">
        <button type="submit" style="width: 100%; padding: 12px; background: #cc0000; color: #fff; border: none; border-radius: 6px; font-weight: bold; cursor: pointer;">Login</button>
    </form>
    <p style="text-align: center; margin-top: 15px; font-size: 14px; color: #aaa;">
        Don't have an account? <a href="/signup" style="color: #3ea6ff; text-decoration: none;">Signup</a>
    </p>
</div>

{% elif page == 'signup' %}
<div style="max-width: 400px; margin: 80px auto; background: #181818; padding: 24px; border-radius: 16px; border: 1px solid #333;">
    <h2 style="text-align: center; margin-bottom: 20px;">Create Pro Account</h2>
    {% if error %}
    <p style="color: #ff0000; font-size: 14px; text-align: center; margin-bottom: 10px;">{{ error }}</p>
    {% endif %}
    <form action="/signup" method="post">
        <label style="font-size: 12px; color: #aaa;">Username</label>
        <input type="text" name="username" required style="width: 100%; padding: 10px; background: #222; border: 1px solid #444; color: #fff; border-radius: 6px; margin-bottom: 15px;">
        <label style="font-size: 12px; color: #aaa;">Email</label>
        <input type="email" name="email" required style="width: 100%; padding: 10px; background: #222; border: 1px solid #444; color: #fff; border-radius: 6px; margin-bottom: 15px;">
        <label style="font-size: 12px; color: #aaa;">Password</label>
        <input type="password" name="password" required style="width: 100%; padding: 10px; background: #222; border: 1px solid #444; color: #fff; border-radius: 6px; margin-bottom: 20px;">
        <button type="submit" style="width: 100%; padding: 12px; background: #3ea6ff; color: #fff; border: none; border-radius: 6px; font-weight: bold; cursor: pointer;">Sign Up</button>
    </form>
    <p style="text-align: center; margin-top: 15px; font-size: 14px; color: #aaa;">
        Already have an account? <a href="/login" style="color: #3ea6ff; text-decoration: none;">Login</a>
    </p>
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

    <div id="sidebarOverlay" class="modal-overlay" onclick="closeSidebarDrawer()"></div>
    <div id="sidebarDrawer" style="display:none; position:fixed; top:0; left:0; width:280px; height:100%; background:#1f1f1f; z-index:2500; overflow-y:auto; padding:16px; border-right:1px solid #333;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; border-bottom:1px solid #333; padding-bottom:10px;">
            <h3 style="font-size:16px;">Sidebar Categories</h3>
            <div class="icon-btn" onclick="closeSidebarDrawer()"><svg viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></div>
        </div>
        <a href="/?cat=Shopping" class="menu-list-item">Shopping (Merchandise)</a>
        <a href="/?cat=Music" class="menu-list-item">Music Hub</a>
        <a href="/edit_profile" class="menu-list-item">Settings & Configurations</a>
    </div>

    <div id="searchOverlay">
        <div class="search-top-bar">
            <div class="icon-btn" onclick="closeSearchOverlay()">
                <svg viewBox="0 0 24 24"><line x1="19" y1="12" x2="5" y2="12"></line></svg>
            </div>
            <form action="/" method="get" class="search-input-box">
                <input type="text" name="q" id="searchInputField" placeholder="Search Posts...">
                <button type="submit" style="background:none; border:none; cursor:pointer;">
                    <svg class="search-icon" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                </button>
            </form>
        </div>
    </div>

    {% if page == 'home' %}
      <div class="mainFeedContainer" style="padding: 16px; max-width: 600px; margin: 0 auto;">
        
        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            {% for category, message in messages %}
              <div style="background: {% if category == 'danger' %}#cc0000{% else %}#2ba640{% endif %}; color: #fff; padding: 10px 14px; border-radius: 8px; margin-bottom: 15px; font-size: 14px; text-align: center;">
                {{ message }}
              </div>
            {% endfor %}
          {% endif %}
        {% endwith %}

        {% for p in posts %}
          <div style="background: #181818; padding: 16px; margin-bottom: 15px; border-radius: 12px; color: #fff; border: 1px solid #333;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
              <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 18px;">{{ p['avatar'] if p['avatar'] else '⚡' }}</span>
                <div>
                  <div style="font-weight: bold; font-size: 14px;">{{ p['username'] }}</div>
                  <div style="font-size: 11px; color: #aaa;">
                    {{ p['created_at'] }} | <span id="countdown_{{ p['id'] }}" style="color: #3ea6ff; font-weight: bold;">Loading timer...</span>
                  </div>
                </div>
              </div>

              <!-- Feature 2: Channel Subscription Button (Appears for other creators) -->
              {% if user and p.get('user_id') and user['id'] != p['user_id'] %}
                <form action="{{ url_for('subscribe_channel', creator_id=p['user_id']) }}" method="POST" style="margin: 0;">
                  <button type="submit" style="background: {% if p['is_subscribed'] %}#272727{% else %}#fff{% endif %}; color: {% if p['is_subscribed'] %}#fff{% else %}#000{% endif %}; border: none; padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: bold; cursor: pointer;">
                    {{ 'Subscribed ✓' if p['is_subscribed'] else 'Subscribe' }}
                  </button>
                </form>
              {% endif %}
            </div>

            <div style="font-size: 15px; margin-bottom: 12px; line-height: 1.4;">{{ p['content'] }}</div>

            <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #272727; padding-top: 10px;">
              
              <!-- Feature 1: Post Like Button -->
              <form action="{{ url_for('like_post', post_id=p['id']) }}" method="POST" style="margin: 0;">
                <button type="submit" style="background: #272727; color: #fff; border: none; padding: 6px 14px; border-radius: 20px; font-size: 13px; cursor: pointer; display: flex; align-items: center; gap: 6px;">
                  ❤️ <span style="font-weight: bold;">{{ p['likes_count'] }}</span>
                </button>
              </form>

              <!-- Feature 4: Creator Self-Deletion -->
              {% if user and p.get('user_id') and user['id'] == p['user_id'] %}
                <form action="{{ url_for('delete_post', post_id=p['id']) }}" method="POST" style="margin: 0;" onsubmit="return confirm('Kya aap apni is post ko delete karna chahte hain?');">
                  <button type="submit" style="background: rgba(255,0,0,0.15); color: #ff4444; border: 1px solid rgba(255,0,0,0.3); padding: 6px 12px; border-radius: 20px; font-size: 12px; cursor: pointer; font-weight: bold;">
                    🗑️ Delete Post
                  </button>
                </form>
              {% endif %}

            </div>

          </div>

          <script>
            (function() {
                const createdAt = "{{ p['created_at'] }}";
                // 48 hours expiry calculation
                const expiryTime = new Date(createdAt.replace(/-/g, "/")).getTime() + (48 * 60 * 60 * 1000);
                const timerElement = document.getElementById("countdown_{{ p['id'] }}");

                function updateCountdown() {
                    const now = new Date().getTime();
                    const distance = expiryTime - now;

                    if (distance < 0) {
                        timerElement.innerHTML = "Expired";
                        window.location.reload(); // Auto refresh to remove deleted post
                        return;
                    }

                    const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                    const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                    const seconds = Math.floor((distance % (1000 * 60)) / 1000);

                    timerElement.innerHTML = `Expires in: ${hours}h ${minutes}m ${seconds}s`;
                }

                updateCountdown();
                setInterval(updateCountdown, 1000);
            })();
          </script>
        {% else %}
          <div style="color: white; text-align: center; padding: 40px;">
            <h3>Database mein koi post nahi hai!</h3>
            <p style="color: #aaa; font-size: 13px; margin-top: 6px;">Neeche diye gaye '+' button par click karke nayi post banayein.</p>
          </div>
        {% endfor %}
      </div>

    {% elif page == 'notifications' %}
        <div style="padding: 16px; max-width: 600px; margin: 0 auto;">
            <h3 style="font-size: 18px; margin-bottom: 15px;">Notification Center</h3>
            {% for n in notifications %}
            <div style="background:#1a1a1a; padding: 14px; border-radius: 10px; margin-bottom: 10px; font-size: 14px; border: 1px solid #333; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div>{{ n['message'] }}</div>
                    <div style="font-size: 11px; color: #888; margin-top: 4px;">{{ n['created_at'] }}</div>
                </div>
            </div>
            {% else %}
            <div style="color: #777; text-align: center; padding: 40px;">
                <p>Koi nayi notification nahi hai.</p>
            </div>
            {% endfor %}
        </div>

    {% elif page == 'community' %}
        <div style="padding:16px;">
            <h3>Community Tab & Live Polls</h3>
        </div>
    {% elif page == 'you' %}
        <div style="padding: 20px; text-align: center;">
            <h2>{{ user['username'] }}</h2>
            <p style="color: #aaa; font-size: 13px; margin-top: 4px;">{{ user['handle'] }}</p>
            <a href="/logout" style="display: inline-block; margin-top: 20px; background: #cc0000; color: #fff; padding: 10px 20px; border-radius: 20px; text-decoration: none; font-weight: bold;">Logout</a>
        </div>
    {% endif %}

    <div class="bottom-nav">
        <a href="/" class="nav-item {% if page == 'home' %}active{% endif %}">
            <svg viewBox="0 0 24 24"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
            Home
        </a>
        <div class="nav-item" onclick="openModal()" style="display:flex; justify-content:center; align-items:center; font-size:24px; color:#ff4757; cursor:pointer;">+</div>
        <a href="/notifications" class="nav-item {% if page == 'notifications' %}active{% endif %}">
            <svg viewBox="0 0 24 24"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
            Alerts
        </a>
        <a href="/you" class="nav-item {% if page == 'you' %}active{% endif %}">
            <svg viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            You
        </a>
    </div>

    <script>
        function openSearchOverlay() { document.getElementById('searchOverlay').style.display = 'block'; document.getElementById('searchInputField').focus(); }
        function closeSearchOverlay() { document.getElementById('searchOverlay').style.display = 'none'; }
        function openSidebarDrawer() { document.getElementById('sidebarOverlay').style.display = 'block'; document.getElementById('sidebarDrawer').style.display = 'block'; }
        function closeSidebarDrawer() { document.getElementById('sidebarOverlay').style.display = 'none'; document.getElementById('sidebarDrawer').style.display = 'none'; }
    </script>
{% endif %}

<div id="writeModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); z-index:9999; justify-content:center; align-items:center;">
    <div style="background:#1e1e1e; padding:20px; border-radius:12px; width:90%; max-width:450px; color:#fff; box-shadow: 0 4px 15px rgba(0,0,0,0.5);">
        <h3 style="margin-top:0; color:#ff4757; text-align:center;">Create Post</h3>
        <form action="/add_post" method="POST">
            <textarea name="content" placeholder="Write your thoughts here..." rows="4" style="width:100%; padding:10px; margin:8px 0; background:#2f2f2f; color:#fff; border:none; border-radius:6px; resize:none;" required></textarea>
            
            <div style="display:flex; justify-content:space-between; margin-top:12px;">
                <button type="button" onclick="closeModal()" style="background:#444; color:#fff; border:none; padding:8px 16px; border-radius:6px; cursor:pointer;">Cancel</button>
                <button type="submit" style="background:#cc0000; color:#fff; border:none; padding:8px 16px; border-radius:6px; cursor:pointer;">Publish</button>
            </div>
        </form>
    </div>
</div>

<script>
function openModal() { document.getElementById('writeModal').style.display = 'flex'; }
function closeModal() { document.getElementById('writeModal').style.display = 'none'; }
</script>

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

def cleanup_expired_posts():
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM posts WHERE datetime(created_at) < datetime('now', '-48 hours')")
    conn.commit()
    conn.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username') or request.form.get('email')
        password = request.form.get('password')
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, username))
        user = c.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return redirect(url_for('home'))
        else:
            error = 'Invalid credentials!'
            
    return render_template_string(HTML_TEMPLATE, page='auth', error=error)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password)
        email = request.form.get('email')
        handle = f"@{username.lower().replace(' ', '')}"
        
        try:
            conn = get_db()
            c = conn.cursor()
            c.execute("INSERT INTO users (username, email, password, handle) VALUES (?, ?, ?, ?)", (username, email, hashed_password, handle))
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
    cleanup_expired_posts()
    
    user = get_current_user()
    current_user_id = user['id'] if user else None
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT posts.*, users.username FROM posts LEFT JOIN users ON posts.user_id = users.id ORDER BY posts.id DESC")
    raw_posts = c.fetchall()
    
    posts = []
    for p in raw_posts:
        p_dict = dict(p)
        if not p_dict.get('username'):
            p_dict['username'] = p_dict.get('author', 'Creator')
            
        c.execute("SELECT COUNT(*) as cnt FROM post_likes WHERE post_id = ?", (p['id'],))
        likes_res = c.fetchone()
        p_dict['likes_count'] = likes_res['cnt'] if likes_res else 0
        
        p_dict['is_subscribed'] = False
        if current_user_id and p_dict.get('user_id'):
            c.execute("SELECT id FROM subscriptions WHERE user_id = ? AND channel_id = ?", (current_user_id, p_dict['user_id']))
            if c.fetchone():
                p_dict['is_subscribed'] = True
                
        posts.append(p_dict)
        
    conn.close()
    return render_template_string(HTML_TEMPLATE, posts=posts, page='home', user=user)

@app.route('/like_post/<int:post_id>', methods=['POST'])
def like_post(post_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
        
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id FROM post_likes WHERE user_id = ? AND post_id = ?", (user['id'], post_id))
    existing = c.fetchone()
    if existing:
        c.execute("DELETE FROM post_likes WHERE user_id = ? AND post_id = ?", (user['id'], post_id))
    else:
        c.execute("INSERT INTO post_likes (user_id, post_id) VALUES (?, ?)", (user['id'], post_id))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/subscribe/<int:creator_id>', methods=['POST'])
def subscribe_channel(creator_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
        
    if user['id'] == creator_id:
        return redirect(url_for('home'))
        
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id FROM subscriptions WHERE user_id = ? AND channel_id = ?", (user['id'], creator_id))
    sub = c.fetchone()
    if sub:
        c.execute("DELETE FROM subscriptions WHERE user_id = ? AND channel_id = ?", (user['id'], creator_id))
    else:
        c.execute("INSERT INTO subscriptions (user_id, channel_id) VALUES (?, ?)", (user['id'], creator_id))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
        
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
    post = c.fetchone()
    
    if post and post['user_id'] == user['id']:
        c.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        c.execute("DELETE FROM post_likes WHERE post_id = ?", (post_id,))
        conn.commit()
        from flask import flash
        flash('Aapki post successfully delete ho gayi hai.', 'success')
    else:
        from flask import flash
        flash('Aap kisi aur ki post delete nahi kar sakte!', 'danger')
        
    conn.close()
    return redirect(url_for('home'))

@app.route('/add_post', methods=['POST'])
def add_post():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
        
    content = request.form.get('content')
    
    if content:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO posts (user_id, author, avatar, content, category, language, created_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """, (user['id'], user['username'], '⚡', content, 'Blog', 'English'))
        
        cursor.execute("SELECT user_id FROM subscriptions WHERE channel_id = ?", (user['id'],))
        subscribers = cursor.fetchall()
        for sub in subscribers:
            notif_msg = f"{user['username']} ne ek naya post publish kiya hai!"
            cursor.execute("INSERT INTO notifications (user_id, message) VALUES (?, ?)", (sub['user_id'], notif_msg))
            
        conn.commit()
        conn.close()
        
    return redirect(url_for('home'))

@app.route('/notifications')
def notifications_page():
    user = get_current_user()
    if not user: return redirect(url_for('login'))
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM notifications WHERE user_id = ? ORDER BY id DESC", (user['id'],))
    notifications = c.fetchall()
    conn.close()
    return render_template_string(HTML_TEMPLATE, page='notifications', notifications=notifications, user=user)

@app.route('/community')
def community_page():
    user = get_current_user()
    if not user: return redirect(url_for('login'))
    return render_template_string(HTML_TEMPLATE, page='community', user=user)

@app.route('/you')
def profile_page():
    user = get_current_user()
    if not user: return redirect(url_for('login'))
    return render_template_string(HTML_TEMPLATE, page='you', user=user)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
