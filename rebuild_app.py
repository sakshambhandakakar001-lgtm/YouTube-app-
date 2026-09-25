import re

with open('appp.py', 'r') as f:
    code = f.read()

# Fix f-string format issues in template strings
code = re.sub(r'f("""|\'\'\')', r'\1', code)

# Clean out existing auth routes if present to avoid duplication
clean_lines = []
skip = False

for line in code.split('\n'):
    if line.strip().startswith("from flask import") or "Flask(__name__)" in line:
        continue
    if any(route in line for route in ["@app.route('/login'", "@app.route('/signup'", "@app.route('/logout'"]):
        skip = True
        continue
    if skip and line.strip().startswith("@app.route"):
        skip = False
    if not skip:
        clean_lines.append(line)

base_code = "\n".join(clean_lines)

# Complete Python structure
full_app = f"""from flask import Flask, render_template, request, redirect, session, url_for
import json, os

app = Flask(__name__)
app.secret_key = 'flixify_secret_key'

USERS_FILE = 'users.json'

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w') as f:
        json.dump({{}}, f)

def get_users():
    with open(USERS_FILE, 'r') as f:
        try:
            return json.load(f)
        except:
            return {{}}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

{base_code}

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
        users[username] = {{'password': password, 'email': email}}
        save_users(users)
        session['user'] = username
        return redirect('/')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
"""

with open('app.py', 'w') as f:
    f.write(full_app)

print("✅ App structure rebuilt with /login, /signup and original code!")
