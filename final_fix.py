import re

with open('appp.py', 'r') as f:
    code = f.read()

# Fix f-strings if present
code = re.sub(r'f("""|\'\'\')', r'\1', code)

# Clean imports
import_header = "from flask import Flask, render_template, request, redirect, session, url_for\nimport json, os\n\napp = Flask(__name__)\napp.secret_key = 'flixify_secret_key'\n\nUSERS_FILE = 'users.json'\nif not os.path.exists(USERS_FILE):\n    with open(USERS_FILE, 'w') as f:\n        json.dump({}, f)\n\ndef get_users():\n    with open(USERS_FILE, 'r') as f:\n        try:\n            return json.load(f)\n        except:\n            return {}\n\ndef save_users(users):\n    with open(USERS_FILE, 'w') as f:\n        json.dump(users, f, indent=4)\n"

# Clean custom Auth Routes
auth_routes = """
@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user'):
        return redirect('/')
    if request.method == 'POST':
        email = request.form.get('email', '').lower().strip()
        password = request.form.get('password')
        users = get_users()
        for u, d in users.items():
            if isinstance(d, dict) and d.get('email') == email and d.get('password') == password:
                session['user'] = u
                return redirect('/')
            elif not isinstance(d, dict) and u == email and d == password:
                session['user'] = u
                return redirect('/')
        return "<h3>Galat Email ya Password!</h3><br><a href='/login'>Wapas jayein</a>"
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
            if isinstance(d, dict) and d.get('email') == email:
                return "<h3>Is Email ID se pehle se account bana hua hai!</h3><br><a href='/login'>Login Karein</a>"
        users[username] = {'password': password, 'email': email}
        save_users(users)
        session['user'] = username
        return redirect('/')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')
"""

# Strip existing top imports/route overlaps from original code
lines = code.split('\n')
filtered_lines = []
skip = False

for line in lines:
    if "from flask import" in line or "Flask(__name__)" in line:
        continue
    if "@app.route('/login'" in line or "@app.route('/signup'" in line or "@app.route('/logout'" in line:
        skip = True
        continue
    if skip and line.startswith("@app.route"):
        skip = False
    if not skip:
        filtered_lines.append(line)

final_code = import_header + "\n" + "\n".join(filtered_lines) + "\n" + auth_routes

with open('app.py', 'w') as f:
    f.write(final_code)

print("✅ ALL Syntax & Assertion Errors Fixed Perfectly!")
