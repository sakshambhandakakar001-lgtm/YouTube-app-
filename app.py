from flask import Flask, render_template, render_template_string
import sqlite3
import os
import advanced_brain

app = Flask(__name__)

# Register missing Jinja filter to prevent UndefinedError
@app.template_filter('get_yt_id')
def jinja_get_yt_id(filename):
    return advanced_brain.extract_yt_id(filename)

app.jinja_env.globals.update(get_yt_id=jinja_get_yt_id)

def fetch_videos():
    videos = []
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT title, author, views, category, video_url, thumbnail, filename FROM videos")
        rows = cursor.fetchall()
        for r in rows:
            videos.append({
                "title": r[0],
                "author": r[1],
                "views": r[2],
                "category": r[3],
                "video_url": r[4],
                "thumbnail": r[5],
                "filename": r[6] if len(r) > 6 else r[4]
            })
        conn.close()
    except Exception as e:
        print(f"[App Error] {e}")
    return videos

@app.route('/')
def home():
    videos = fetch_videos()
    if os.path.exists("templates/index.html"):
        return render_template("index.html", videos=videos)
    return "Template index.html not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
