import sqlite3
import os

BASE_DIR = os.path.expanduser('~/yt-cloud-data')
DB_FILE = os.path.join(BASE_DIR, 'database.db')

def seed_1000_videos():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # 10 Major Topics with sample embedded players
    topics = {
        "Gaming": [
            ("https://www.youtube.com/embed/2g811KoJBUo", "Minecraft Survival & Building"),
            ("https://www.youtube.com/embed/3JZ_D3ELwOQ", "BGMI / Free Fire Pro Gameplay"),
            ("https://www.youtube.com/embed/dQw4w9WgXcQ", "GTA 5 Mods & Missions")
        ],
        "Entertainment": [
            ("https://www.youtube.com/embed/7PIji8yy4Aw", "New Movie Trailers 2026"),
            ("https://www.youtube.com/embed/kJQP7kiw5Fk", "Best Web Series Moments")
        ],
        "Music": [
            ("https://www.youtube.com/embed/jfKfPfyJRdk", "Lofi Beats & Relaxing Songs"),
            ("https://www.youtube.com/embed/09R8_2nJtjg", "Trending DJ Remix Songs")
        ],
        "Tech": [
            ("https://www.youtube.com/embed/09R8_2nJtjg", "Python & Flask App Development"),
            ("https://www.youtube.com/embed/3JZ_D3ELwOQ", "Latest Smartphone Reviews")
        ],
        "Shorts": [
            ("https://www.youtube.com/embed/tgbNymZ7vqY", "Viral Funny Challenge Clips")
        ],
        "Vlogs": [
            ("https://www.youtube.com/embed/7PIji8yy4Aw", "Daily Lifestyle & Travel Vlog")
        ],
        "Education": [
            ("https://www.youtube.com/embed/09R8_2nJtjg", "Science Facts & Tutorials")
        ],
        "Sports": [
            ("https://www.youtube.com/embed/3JZ_D3ELwOQ", "Cricket & Football Best Moments")
        ],
        "News": [
            ("https://www.youtube.com/embed/7PIji8yy4Aw", "Trending News & Business Podcasts")
        ],
        "Fitness": [
            ("https://www.youtube.com/embed/2g811KoJBUo", "Gym Workout & Health Tips")
        ]
    }

    count = 0
    # Har ek topic ke 100 videos = Total 1000 Videos
    for cat, items in topics.items():
        for i in range(1, 101):
            url, base_title = items[i % len(items)]
            title = f"{base_title} - Video #{i}"
            desc = f"Watch high quality {cat} content on Flixify Pro."
            is_short = 1 if cat == "Shorts" else 0
            
            c.execute("""
                INSERT INTO videos (filename, title, description, category, is_short, user_id)
                VALUES (?, ?, ?, ?, ?, 1)
            """, (url, title, desc, cat, is_short))
            count += 1

    conn.commit()
    conn.close()
    print(f"Successfully added {count} videos (100 per topic) to Flixify Pro!")

if __name__ == '__main__':
    seed_1000_videos()
