import sqlite3
import os

db_path = os.path.expanduser('~/yt-cloud-data/database.db')
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("UPDATE videos SET filename = replace(filename, '/videos/', '') WHERE filename LIKE '/videos/%'")
conn.commit()
conn.close()

print("Database cleanup completed successfully!")
