from flask import Blueprint, render_template_string, request, Response
import subprocess
import json

reels_bp = Blueprint('reels_bp', __name__)

# Complete Native UI preserving your original bottom navigation & design
APP_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flixify Pro</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background-color: #0f0f0f; color: #fff; font-family: sans-serif; padding-bottom: 70px; }
        
        /* Top Header */
        .top-header { position: fixed; top: 0; width: 100%; background: #000; padding: 10px 15px; display: flex; align-items: center; justify-content: space-between; z-index: 1000; border-bottom: 1px solid #1a1a1a; }
        .logo-text { color: #ff0000; font-weight: bold; font-size: 20px; }
        .search-form { display: flex; flex: 1; margin: 0 15px; max-width: 400px; }
        .search-form input { width: 100%; background: #121212; border: 1px solid #333; padding: 6px 12px; color: #fff; border-radius: 20px 0 0 20px; outline: none; }
        .search-form button { background: #222; border: 1px solid #333; border-left: none; padding: 6px 12px; color: #fff; border-radius: 0 20px 20px 0; cursor: pointer; }

        /* Filter Chips */
        .chips-bar { margin-top: 55px; padding: 10px; display: flex; gap: 8px; overflow-x: auto; background: #0f0f0f; }
        .chip { background: #272727; color: #fff; padding: 6px 14px; border-radius: 16px; text-decoration: none; font-size: 13px; white-space: nowrap; }
        .chip.active { background: #fff; color: #000; font-weight: bold; }

        /* Video Feed (Home) */
        .feed-container { padding: 5px 0; }
        .video-card { margin-bottom: 20px; background: #0f0f0f; }
        .video-player { width: 100%; height: 220px; background: #000; border: none; }
        .video-info { display: flex; padding: 10px; gap: 12px; }
        .avatar { width: 38px; height: 38px; border-radius: 50%; background: #ff0000; color: #fff; display: flex; align-items: center; justify-content: center; font-weight: bold; flex-shrink: 0; }
        .meta { display: flex; flex-direction: column; justify-content: center; }
        .title { font-size: 14px; font-weight: 500; line-height: 1.3; color: #f1f1f1; margin-bottom: 4px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
        .sub-text { font-size: 12px; color: #aaa; }

        /* Shorts View */
        .shorts-wrapper { scroll-snap-type: y mandatory; overflow-y: scroll; height: calc(100vh - 120px); }
        .short-item { height: calc(100vh - 120px); scroll-snap-align: start; position: relative; background: #000; display: flex; justify-content: center; align-items: center; }
        .short-player { width: 100%; height: 100%; max-width: 450px; object-fit: cover; }

        /* Bottom Navigation Bar (Original App Design preserved) */
        .bottom-nav { position: fixed; bottom: 0; width: 100%; background: #000; display: flex; justify-content: space-around; align-items: center; padding: 8px 0; border-top: 1px solid #1f1f1f; z-index: 1000; }
        .nav-btn { text-decoration: none; color: #888; display: flex; flex-direction: column; align-items: center; font-size: 11px; }
        .nav-btn.active { color: #fff; font-weight: bold; }
        .nav-icon { font-size: 18px; margin-bottom: 2px; }
        .plus-btn { background: #222; border: 1px solid #444; width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #fff; font-size: 20px; }
    </style>
</head>
<body>

    <!-- Header -->
    <div class="top-header">
        <span class="logo-text">Flixify Pro</span>
        <form class="search-form" action="/" method="GET">
            <input type="text" name="q" placeholder="Search Master & AI" value="{{ query }}">
            <button type="submit">🔍</button>
        </form>
    </div>

    {% if not is_shorts %}
    <!-- Category Chips -->
    <div class="chips-bar">
        <a href="/?q=all" class="chip active">All</a>
        <a href="/?q=subscriptions" class="chip">Subscriptions</a>
        <a href="/?q=gaming" class="chip">Gaming</a>
        <a href="/?q=music" class="chip">Music</a>
        <a href="/?q=podcasts" class="chip">Podcasts</a>
    </div>
    {% endif %}

    <!-- Main Content Area -->
    <div class="feed-container" style="{% if is_shorts %}margin-top: 50px;{% endif %}">
        {% if is_shorts %}
            <div class="shorts-wrapper">
                {% for video in videos %}
                <div class="short-item">
                    <iframe class="short-player" src="https://www.youtube-nocookie.com/embed/{{ video.id }}?autoplay=1&controls=1&rel=0&modestbranding=1" allow="autoplay; encrypted-media" allowfullscreen></iframe>
                </div>
                {% else %}
                <p style="text-align:center; padding: 40px;">Shorts Load Ho Rahe Hain...</p>
                {% endfor %}
            </div>
        {% else %}
            {% for video in videos %}
            <div class="video-card">
                <iframe class="video-player" src="https://www.youtube-nocookie.com/embed/{{ video.id }}?rel=0&modestbranding=1" allow="autoplay; encrypted-media" allowfullscreen></iframe>
                <div class="video-info">
                    <div class="avatar">F</div>
                    <div class="meta">
                        <div class="title">{{ video.title }}</div>
                        <div class="sub-text">Flixify Creator • {{ video.views }} views</div>
                    </div>
                </div>
            </div>
            {% else %}
            <p style="text-align:center; padding: 40px;">Videos Load Ho Rahe Hain...</p>
            {% endfor %}
        {% endif %}
    </div>

    <!-- Original Bottom Nav Layout -->
    <div class="bottom-nav">
        <a href="/" class="nav-btn {% if not is_shorts %}active{% endif %}">
            <span class="nav-icon">🏠</span>
            <span>Home</span>
        </a>
        <a href="/shorts" class="nav-btn {% if is_shorts %}active{% endif %}">
            <span class="nav-icon">⚡</span>
            <span>Shorts</span>
        </a>
        <div class="plus-btn">+</div>
        <div class="nav-btn">
            <span class="nav-icon">👤</span>
            <span>Community</span>
        </div>
        <div class="nav-btn">
            <span class="nav-icon">👤</span>
            <span>You</span>
        </div>
    </div>

</body>
</html>
"""

def fetch_videos(search_term, is_short=False):
    videos = []
    try:
        # Search parameters filtering long videos vs shorts
        query = f"{search_term} shorts" if is_short else f"{search_term} full video"
        cmd = ["yt-dlp", f"ytsearch10:{query}", "--dump-json", "--flat-playlist", "--skip-download"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        for line in result.stdout.strip().split("\n"):
            if line:
                data = json.loads(line)
                videos.append({
                    'id': data.get('id'),
                    'title': data.get('title', 'Trending Video'),
                    'views': '10K'
                })
    except Exception as e:
        print(f"Fetch Error: {e}")
    return videos

@reels_bp.route('/')
def home_feed():
    query = request.args.get('q', 'trending indian music videos')
    videos = fetch_videos(query, is_short=False)
    return render_template_string(APP_HTML, videos=videos, query=query, is_shorts=False)

@reels_bp.route('/shorts')
def shorts_feed():
    query = request.args.get('q', 'trending shorts')
    videos = fetch_videos(query, is_short=True)
    return render_template_string(APP_HTML, videos=videos, query=query, is_shorts=True)
