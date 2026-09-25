import re

app_code = '''from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json, os

app = Flask(__name__)
app.secret_key = 'flixify_secret_key_pro'

USERS_FILE = 'users.json'

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w') as f:
        json.dump({}, f)

def get_users():
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user'):
        return redirect('/')
    if request.method == 'POST':
        email = request.form.get('email', '').lower().strip()
        password = request.form.get('password')
        users = get_users()
        for u, d in users.items():
            if d.get('email') == email and d.get('password') == password:
                session['user'] = u
                return redirect('/')
        return "Invalid Email or Password! <a href='/login'>Try Again</a>"
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if session.get('user'):
        return redirect('/')
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password')
        email = request.form.get('email', '').lower().strip()

        users = get_users()
        for u, d in users.items():
            if d.get('email') == email:
                return "Is Email ID se pehle se account bana hua hai! <a href='/login'>Login karein</a>"

        users[username] = {'password': password, 'email': email}
        save_users(users)
        session['user'] = username
        return redirect('/')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

'''

with open('app.py', 'r') as f:
    content = f.read()

# Replace old auth routes if present
if '@app.route(\'/login\'' in content:
    print("✅ App.py is being updated with Email-based Authentication...")
    with open('app.py', 'w') as f:
        f.write(app_code + "\n" + content)
else:
    with open('app.py', 'w') as f:
        f.write(app_code + "\n" + content)

print("✅ Backend updated successfully!")
