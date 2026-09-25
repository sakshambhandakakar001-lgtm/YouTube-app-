import re

with open('appp.py', 'r') as f:
    code = f.read()

# Fix f-strings
code = re.sub(r'f("""|\'\'\')', r'\1', code)

# Ensure essential Flask imports
import_stmt = "from flask import Flask, render_template, request, redirect, session, url_for"
if "from flask import" in code:
    lines = code.split('\n')
    for i, line in enumerate(lines):
        if line.startswith("from flask import"):
            lines[i] = import_stmt
            break
    code = '\n'.join(lines)

# Remove all existing login/signup/logout routes
patterns = [
    r"@app\.route\('/login'.*?def login\(\):.*?(?=@app\.route|if __name__|\Z)",
    r"@app\.route\('/signup'.*?def signup\(\):.*?(?=@app\.route|if __name__|\Z)",
    r"@app\.route\('/logout'.*?def logout\(\):.*?(?=@app\.route|if __name__|\Z)"
]
for pat in patterns:
    code = re.sub(pat, '', code, flags=re.DOTALL)

# Disable any redirect to login anywhere in the app logic
code = re.sub(r"return\s+redirect\s*\(\s*['\"]/login['\"]\s*\)", "# return redirect('/login')", code)
code = re.sub(r"return\s+redirect\s*\(\s*url_for\s*\(\s*['\"]login['\"]\s*\)\s*\)", "# return redirect(url_for('login'))", code)

# Fresh Auth Routes
auth_code = """

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
            user_email = d.get('email', '').lower() if isinstance(d, dict) else u.lower()
            user_pass = d.get('password') if isinstance(d, dict) else d
            
            if user_email == email and user_pass == password:
                session['user'] = u
                session['username'] = u
                session['user_id'] = u
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
            if isinstance(d, dict) and d.get('email', '').lower() == email:
                return "<h3>Is Email ID se pehle se account bana hua hai!</h3><br><a href='/login'>Login Karein</a>"
                
        users[username] = {'password': password, 'email': email}
        save_users(users)
        
        session['user'] = username
        session['username'] = username
        session['user_id'] = username
        return redirect('/')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

"""

if "if __name__ ==" in code:
    parts = code.split("if __name__ ==")
    final_code = parts[0] + auth_code + "\nif __name__ ==" + parts[1]
else:
    final_code = code + auth_code

with open('app.py', 'w') as f:
    f.write(final_code)

print("✅ All forced redirects removed & app fixed!")
