import sqlite3

# Yeh wahi database file hai jo aapki app.py use kar rahi hogi (agar instance folder mein hai toh path check kar lein)
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE videos ADD COLUMN tags TEXT;")
    conn.commit()
    print("SUCCESS: 'tags' column add ho gaya!")
except sqlite3.OperationalError as e:
    print("NOTE:", e)

conn.close()
