import sqlite3
import os
import urllib.request
import xml.etree.ElementTree as ET

BASE_DIR = os.path.expanduser('~/yt-cloud-data')
DB_FILE = os.path.join(BASE_DIR, 'database.db')

# YouTube RSS Feeds for Trending Content
FEEDS = {
    "Gaming": "https://www.youtube.com/feeds/videos.xml?channel_id=UC4R8DWoMoI7CAwX8_LjQHig",
    "Entertainment": "https://www.youtube.com/feeds/videos.xml?channel_id=UCq-Fj5jknLsUf-MWSy4_brA",
    "Music": "https://www.youtube.com/feeds/videos.xml?channel_id=UC-9-kyTW8ZkZNDHQJ6FzuwA"
}

def fetch_latest():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    added_count = 0

    for cat, feed_url in FEEDS.items():
        try:
            req = urllib.request.Request(feed_url, headers={'User-Agent': 'Mozilla/5.0'})
            xml_data = urllib.request.urlopen(req).read()
            root = ET.fromstring(xml_data)

            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                video_id = entry.find('{http://www.youtube.com/xml/schemas/2015}videoId').text
                title = entry.find('{http://www.w3.org/2005/Atom}title').text
                embed_url = f"https://www.youtube.com/embed/{video_id}"

                # Check if video already exists to avoid duplicates
                c.execute("SELECT id FROM videos WHERE filename = ?", (embed_url,))
                if not c.fetchone():
                    c.execute("""
                        INSERT INTO videos (filename, title, description, category, is_short, user_id)
                        VALUES (?, ?, 'Freshly updated video', ?, 0, 1)
                    """, (embed_url, title, cat))
                    added_count += 1
        except Exception as e:
            continue

    conn.commit()
    conn.close()
    print(f"Purana content safe hai! {added_count} nayi videos add ho gayi hain.")

if __name__ == '__main__':
    fetch_latest()
