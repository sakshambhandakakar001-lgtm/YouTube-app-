cat << 'EOF' > reels_feature.py
from flask import Blueprint, render_template_string, request
import subprocess
import json

reels_bp = Blueprint('reels_bp', __name__)

APP_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flixify Videos & Reels</title>
    <style>
        body { margin: 0; background-color: #0f0f0f; color: #fff; font-family: Arial, sans-serif; }
        .header { position: fixed; top: 0; width: 100%; background: #121212; padding: 10px; z-index: 100; border-bottom: 1px solid #222; text-align: center; }
        .search-box input { width: 55%; padding: 8px; border: 1px solid #333; background: #000; color: #fff; border-radius: 20px 0 0 20px; outline: none; }
        .search-box button { padding: 8px 15px; border: none; background: #ff0000; color: white; border-radius: 0 20px 20px 0; cursor: pointer; }
        .categories { margin-top: 10px; display: flex; gap: 8px; justify-content: center; flex-wrap: wrap; }
        .cat-btn { background: #272727; color: white; padding: 6px 12px; border-radius: 15px; text-decoration: none; font-size: 12px; }
        .main-container { margin-top: 110px; padding: 10px; }
        
        .video-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 15px; }
        .video-card { background: #181818; border-radius: 10px; overflow: hidden; }
        iframe { width: 100%; height: 200px; border: none; }
        .video-title { padding: 10px; font-size: 13px; color: #fff; }

        .shorts-container { scroll-snap-type: y mandatory; overflow-y: scroll; height: calc(100vh - 120px); }
        .short-card { height: calc(100vh - 120px); scroll-snap-align: start; display: flex; justify-content: center; align-items: center; }
        .short-card iframe { width: 100%; height: 95%; border-radius: 10px; }
    </style>
</head>
<body>

    <div class="header">
        <form class="search-box" action="/app-feed" method="GET">
            <input type="text" name="q" placeholder="Search videos, songs, gaming..." value="{{ query }}">
            <button type="submit">🔍 Search</button>
        </form>
        <div class="categories">
            <a href="/app-feed?q=trending&type=videos" class="cat-btn">🏠 Home Videos</a>
            <a href="/app-feed?q=trending&type=shorts" class="cat-btn">⚡ Reels / Shorts</a>
            <a href="/app-feed?q=gaming&type=videos" class="cat-btn">🎮 Gaming</a>
            <a href="/app-feed?q=music&type=videos" class="cat-btn">🎵 Music</a>
            <a href="/" class="cat-btn">↩️ Main App</a>
        </div>
    </div>

    <div class="main-container">
        {% if feed_type == 'shorts' %}
            <div class="shorts-container">
                {% for item in videos %}
                <div class="short-card">
                    <iframe src="https://www.youtube.com/embed/{{ item.id }}" allowfullscreen></iframe>
                </div>
                {% else %}
                <p style="text-align:center;">No Reels loaded.</p>
                {% endfor %}
            </div>
        {% else %}
            <div class="video-grid">
                {% for item in videos %}
                <div class="video-card">
                    <iframe src="https://www.youtube.com/embed/{{ item.id }}" allowfullscreen></iframe>
                    <div class="video-title">{{ item.title }}</div>
                </div>
                {% else %}
                <p style="text-align:center;">No Videos found.</p>
                {% endfor %}
            </div>
        {% endif %}
    </div>

</body>
</html>
"""

@reels_bp.route('/app-feed')
def app_feed():
    query = request.args.get('q', 'trending')
    feed_type = request.args.get('type', 'videos')
    
    search_term = f"{query} shorts" if feed_type == 'shorts' else query
    
    videos = []
    try:
        cmd = ["yt-dlp", f"ytsearch12:{search_term}", "--dump-json", "--flat-playlist", "--skip-download"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        for line in result.stdout.strip().split("\n"):
            if line:
                data = json.loads(line)
                videos.append({'id': data.get('id'), 'title': data.get('title')})
    except Exception as e:
        print(f"yt-dlp fetch error: {e}")

    return render_template_string(APP_HTML, videos=videos, query=query, feed_type=feed_type)
EOF
