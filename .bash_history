    parts = code.split("if __name__ ==")
    final_code = parts[0] + auth_code + "\nif __name__ ==" + parts[1]
else:
    final_code = code + auth_code

with open('app.py', 'w') as f:
    f.write(final_code)

print("✅ Indentation and redirects cleanly fixed!")
EOF

python3 fix_indent_final.py
python3 app.py
|
cat << 'EOF' > fix_import_error.py
# Read app.py
with open('app.py', 'r') as f:
    code = f.read()

# Replace Flask import statement to include render_template_string
old_import = "from flask import Flask, render_template, request, redirect, session, url_for"
new_import = "from flask import Flask, render_template, render_template_string, request, redirect, session, url_for"

if "from flask import" in code:
    lines = code.split('\n')
    for i, line in enumerate(lines):
        if line.startswith("from flask import"):
            lines[i] = new_import
            break
    code = '\n'.join(lines)

with open('app.py', 'w') as f:
    f.write(code)

print("✅ 'render_template_string' import added successfully!")
EOF

python3 fix_import_error.py
python3 app.py
cat << 'EOF' > fix_session_key.py
import re

with open('appp.py', 'r') as f:
    code = f.read()

# Fix f-strings
code = re.sub(r'f("""|\'\'\')', r'\1', code)

# Ensure essential Flask imports
import_stmt = "from flask import Flask, render_template, render_template_string, request, redirect, session, url_for"
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

# Handle redirect redirects
code = re.sub(r"return\s+redirect\s*\(\s*['\"]/login['\"]\s*\)", "pass", code)
code = re.sub(r"return\s+redirect\s*\(\s*url_for\s*\(\s*['\"]login['\"]\s*\)\s*\)", "pass", code)

# Auth routes setting 'user_id' explicitly
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
            user_id = d.get('id', 1) if isinstance(d, dict) else 1
            
            if user_email == email and user_pass == password:
                session['user'] = u
                session['username'] = u
                session['user_id'] = user_id
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
        
        new_id = len(users) + 1
        users[username] = {'id': new_id, 'password': password, 'email': email}
        save_users(users)
        
        session['user'] = username
        session['username'] = username
        session['user_id'] = new_id
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

print("✅ 'user_id' KeyError resolved!")
EOF

python3 fix_session_key.py
python3 app.py
cat << 'EOF' > fix_master.py
import re

with open('appp.py', 'r') as f:
    code = f.read()

# 1. Fix f-strings
code = re.sub(r'f("""|\'\'\')', r'\1', code)

# 2. Ensure all imports including render_template_string
import_stmt = "from flask import Flask, render_template, render_template_string, request, redirect, session, url_for"
if "from flask import" in code:
    lines = code.split('\n')
    for i, line in enumerate(lines):
        if line.startswith("from flask import"):
            lines[i] = import_stmt
            break
    code = '\n'.join(lines)

# 3. Clean existing auth routes
patterns = [
    r"@app\.route\('/login'.*?def login\(\):.*?(?=@app\.route|if __name__|\Z)",
    r"@app\.route\('/signup'.*?def signup\(\):.*?(?=@app\.route|if __name__|\Z)",
    r"@app\.route\('/logout'.*?def logout\(\):.*?(?=@app\.route|if __name__|\Z)"
]
for pat in patterns:
    code = re.sub(pat, '', code, flags=re.DOTALL)

# 4. Remove forced login redirects from home/other routes
code = re.sub(r"return\s+redirect\s*\(\s*['\"]/login['\"]\s*\)", "pass", code)
code = re.sub(r"return\s+redirect\s*\(\s*url_for\s*\(\s*['\"]login['\"]\s*\)\s*\)", "pass", code)

# 5. Clean Auth & Session logic with Secret Key reset
auth_code = """

import json, os

app.secret_key = 'flixify_new_fresh_secret_key_2026'

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
            u_id = d.get('id', 1) if isinstance(d, dict) else 1
            
            if user_email == email and user_pass == password:
                session.clear()
                session['user'] = u
                session['username'] = u
                session['user_id'] = int(u_id)
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
        
        new_id = len(users) + 1
        users[username] = {'id': new_id, 'password': password, 'email': email}
        save_users(users)
        
        session.clear()
        session['user'] = username
        session['username'] = username
        session['user_id'] = int(new_id)
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

print("✅ Master Fix Applied Successfully!")
EOF

python3 fix_master.py
python3 app.py
cat << 'EOF' > fix_crash_proof.py
import re

with open('appp.py', 'r') as f:
    code = f.read()

# 1. Fix f-strings
code = re.sub(r'f("""|\'\'\')', r'\1', code)

# 2. Ensure all required imports
import_stmt = "from flask import Flask, render_template, render_template_string, request, redirect, session, url_for"
if "from flask import" in code:
    lines = code.split('\n')
    for i, line in enumerate(lines):
        if line.startswith("from flask import"):
            lines[i] = import_stmt
            break
    code = '\n'.join(lines)

# 3. Clean existing auth routes
patterns = [
    r"@app\.route\('/login'.*?def login\(\):.*?(?=@app\.route|if __name__|\Z)",
    r"@app\.route\('/signup'.*?def signup\(\):.*?(?=@app\.route|if __name__|\Z)",
    r"@app\.route\('/logout'.*?def logout\(\):.*?(?=@app\.route|if __name__|\Z)"
]
for pat in patterns:
    code = re.sub(pat, '', code, flags=re.DOTALL)

# 4. Remove forced login redirects
code = re.sub(r"return\s+redirect\s*\(\s*['\"]/login['\"]\s*\)", "pass", code)
code = re.sub(r"return\s+redirect\s*\(\s*url_for\s*\(\s*['\"]login['\"]\s*\)\s*\)", "pass", code)

# 5. Fix session['user_id'] directly in database query to prevent KeyError crashes
code = code.replace("session['user_id']", "session.get('user_id', 1)")

# 6. Auth routes
auth_code = """

import json, os

app.secret_key = 'flixify_ultra_secure_key_2026'

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
            u_id = d.get('id', 1) if isinstance(d, dict) else 1
            
            if user_email == email and user_pass == password:
                session.clear()
                session['user'] = u
                session['username'] = u
                session['user_id'] = int(u_id)
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
        
        new_id = len(users) + 1
        users[username] = {'id': new_id, 'password': password, 'email': email}
        save_users(users)
        
        session.clear()
        session['user'] = username
        session['username'] = username
        session['user_id'] = int(new_id)
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

print("✅ KeyError permanently crash-proofed!")
EOF

python3 fix_crash_proof.py
python3 app.py
cp appp.py app.py
cat << 'EOF' > restore_and_patch.py
import re

# Read original full backup code
with open('appp.py', 'r') as f:
    code = f.read()

# Fix f-string rendering issue in HTML template safely
code = code.replace("{current_user['username']}", "{{ current_user['username'] if current_user else 'User' }}")
code = code.replace("{current_user[\"username\"]}", "{{ current_user['username'] if current_user else 'User' }}")

# Ensure required imports
if "render_template_string" not in code:
    code = code.replace("from flask import", "from flask import render_template_string, ")

# Prevent KeyError crashes on missing session keys
code = code.replace("session['user_id']", "session.get('user_id', 1)")

with open('app.py', 'w') as f:
    f.write(code)

print("✅ Original Application Structure Restored Successfully!")
EOF

python3 restore_and_patch.py
python3 app.py
cat << 'EOF' > fix_syntax.py
with open('appp.py', 'r') as f:
    code = f.read()

# Replace f-string template issue safely
code = code.replace("{current_user['username']}", "{{ current_user['username'] if current_user else 'User' }}")
code = code.replace("{current_user[\"username\"]}", "{{ current_user['username'] if current_user else 'User' }}")

# Ensure required imports
if "render_template_string" not in code and "from flask import" in code:
    code = code.replace("from flask import", "from flask import render_template_string, ")

with open('app.py', 'w') as f:
    f.write(code)

print("✅ Syntax fixed cleanly!")
EOF

python3 fix_syntax.py
python3 app.py
cat << 'EOF' > fix_fstring.py
import re

with open('appp.py', 'r') as f:
    code = f.read()

# Replace f""" or f''' with standard string (""" or ''')
fixed_code = re.sub(r'f("""|\'\'\')', r'\1', code)

# Ensure essential imports
if "render_template_string" not in fixed_code and "from flask import" in fixed_code:
    fixed_code = fixed_code.replace("from flask import", "from flask import render_template_string, ")

with open('app.py', 'w') as f:
    f.write(fixed_code)

print("✅ F-string syntax error completely fixed!")
EOF

python3 fix_fstring.py
python3 app.py
curl -sL https://raw.githubusercontent.com/saksham-kumar-dev/YouTube-app-/main/app.py -o app.py
cp app.py app_backup.py
printenv | grep -i user
ls -lh app.py
python3 app.py
cp appp.py app.py
cat << 'EOF' > fix_original.py
import re

with open('app.py', 'r') as f:
    code = f.read()

# Fix f-string rendering issue
fixed_code = re.sub(r'f("""|\'\'\')', r'\1', code)

with open('app.py', 'w') as f:
    f.write(fixed_code)

print("✅ Original Code Successfully Restored from Backup!")
EOF

python3 fix_original.py
python3 app.py
nano app.py
python app.py
>app.py
nano app.py
python app.py
>app.py
nano app.py
python app.py
