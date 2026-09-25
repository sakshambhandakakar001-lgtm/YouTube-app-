import os
import sqlite3
from datetime import timedelta
from flask import Flask, request, render_template_string, redirect, session, url_for

app = Flask(__name__)
app.secret_key = 'simple_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365) # Feature 1: Ek baar login karne ke baad baar-baar login nahi maangega

DB_FILE = 'database.db'

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        username TEXT, 
        password TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        title TEXT, 
        filename TEXT, 
        user_id INTEGER, 
        likes INTEGER DEFAULT 0, 
        dislikes INTEGER DEFAULT 0
    )''')
    conn.commit()
    conn.close()

init_db()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        if not user:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            c.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = c.fetchone()
        conn.close()
        
        session.permanent = True
        session['user_id'] = user['id']
        return redirect(url_for('home'))
    return '''
        <h2>Login / Signup</h2>
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required><br><br>
            <input type="password" name="password" placeholder="Password" required><br><br>
            <button type="submit">Login</button>
        </form>
    '''

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT videos.*, users.username FROM videos JOIN users ON videos.user_id = users.id")
    videos = c.fetchall()
    
    c.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
    current_user = c.fetchone()
    conn.close()
    
    html = f'''
        <h2>Welcome, {current_user['username']} | <a href="/logout">Logout</a></h2>
        <hr>
        <h3>All Videos</h3>
        {% for v in videos %}
            <div style="border:1px solid #ccc; padding:10px; margin-bottom:10px;">
                <h4>{{ v['title'] }} (Uploaded by: {{ v['username'] }})</h4>
                <p>Likes: {{ v['likes'] }} | Dislikes: {{ v['dislikes'] }}</p>
                <a href="/like/{{ v['id'] }}"><button>👍 Like</button></a>
                <a href="/dislike/{{ v['id'] }}"><button>👎 Dislike</button></a>
                {% if v['user_id'] == current_user['id'] %}
                    <form action="/delete-video/{{ v['id'] }}" method="POST" style="display:inline;">
                        <button type="submit" style="color:red;">🗑️ Delete</button>
                    </form>
                {% endif %}
            </div>
        {% endfor %}
    '''
    return render_template_string(html, videos=videos, current_user=current_user)

@app.route('/like/<int:video_id>')
def like_video(video_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE videos SET likes = likes + 1 WHERE id = ?", (video_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/dislike/<int:video_id>')
def dislike_video(video_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE videos SET dislikes = dislikes + 1 WHERE id = ?", (video_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/delete-video/<int:video_id>', methods=['POST'])
def delete_video(video_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM videos WHERE id = ? AND user_id = ?", (video_id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
