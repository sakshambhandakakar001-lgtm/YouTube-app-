import re

# Read original application code
with open('appp.py', 'r') as f:
    code = f.read()

# Fix f-string issues
code = re.sub(r'f("""|\'\'\')', r'\1', code)

# Fix imports
import_stmt = "from flask import Flask, render_template, request, redirect, session, url_for"
if "from flask import" in code:
    lines = code.split('\n')
    for i, line in enumerate(lines):
        if line.startswith("from flask import"):
            lines[i] = import_stmt
            break
    code = '\n'.join(lines)

# Remove old authentication definitions to prevent duplication
patterns = [
    r"@app\.route\('/login'.*?def login\(\):.*?(?=@app\.route|if __name__|\Z)",
    r"@app\.route\('/signup'.*?def signup\(\):.*?(?=@app\.route|if __name__|\Z)",
    r"@app\.route\('/logout'.*?def logout\(\):.*?(?=@app\.route|if __name__|\Z)"
]
for pat in patterns:
    code = re.sub(pat, '', code, flags=re.DOTALL)

# Clean and properly indented authentication module
auth_module = """

import json, os

USERS_FILE = 'users.json'
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w') as f:
        json.dump({}, f)

def get_users():
    with open(USERS_FILE, 'r') as f:
        try:
            return json.load(f)
        except:
            return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').lower().strip()
        password = request.form.get('password')
        users = get_users()
        for u, d in users.items():
            if isinstance(d, dict) and d.get('email') == email and d.get('password') == password:
                session['user'] = u
                session['username'] = u
                return redirect('/')
            elif not isinstance(d, dict) and u == email and d == password:
                session['user'] = u
                session['username'] = u
                return redirect('/')
        return "<h3>Galat Email ya Password!</h3><br><a href='/login'>Wapas jayein</a>"
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
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
        session['username'] = username
        return redirect('/')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')
"""

# Append auth code safely before app runner
if "if __name__ ==" in code:
    parts = code.split("if __name__ ==")
    final_code = parts[0] + auth_module + "\nif __name__ ==" + parts[1]
else:
    final_code = code + auth_module

with open('app.py', 'w') as f:
    f.write(final_code)

print("✅ Indentation Fixed & Original Application Cleanly Restored!")
