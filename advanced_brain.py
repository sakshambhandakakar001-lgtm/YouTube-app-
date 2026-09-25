import sqlite3
import re

# YouTube ID Exporter Function for Jinja Template
def extract_yt_id(url_or_filename):
    if not url_or_filename:
        return "dQw4w9WgXcQ"
    match = re.search(r'(?:v=|\/|embed\/)([0-9A-Za-z_-]{11})', str(url_or_filename))
    if match:
        return match.group(1)
    return "dQw4w9WgXcQ"

# Autonomous Database Auto-Fix
def fix_database_content():
    try:
        conn = sqlite3.connect('database.db', timeout=5)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                author TEXT,
                views TEXT,
                category TEXT,
                video_url TEXT,
                thumbnail TEXT,
                filename TEXT
            )
        ''')
        
        cursor.execute("SELECT COUNT(*) FROM videos")
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO videos (title, author, views, category, video_url, thumbnail, filename)
                VALUES 
                ('Hum Rahein Na Rahein (Full Video)', 'Saksham', '5 views', 'Entertainment', 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4', 'https://picsum.photos/800/450?random=1', 'BigBuckBunny.mp4'),
                ('HOLD UP (Official Video)', 'Saksham', '10 views', 'Music', 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4', 'https://picsum.photos/800/450?random=2', 'ElephantsDream.mp4')
            ''')
            conn.commit()
        conn.close()
        print("[Brain] All Extractors & Database Rows Active!")
    except Exception as e:
        print(f"[Brain Warning] {e}")

if __name__ == '__main__':
    fix_database_content()
