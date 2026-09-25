import re

with open('app.py', 'r') as f:
    code = f.read()

# Add JSON database storage helpers
helpers = """
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
"""

if "USERS_FILE = 'users.json'" not in code:
    code = helpers + "\n" + code

login_code = """
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
"""

signup_code = """
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
"""

# Replace or append login/signup routes safely
if "@app.route('/login'" in code:
    code = re.sub(r"@app\.route\('/login'.*?def login\(\):.*?(?=@app\.route|\Z)", login_code.strip(), code, flags=re.DOTALL)
else:
    code += "\n" + login_code

if "@app.route('/signup'" in code:
    code = re.sub(r"@app\.route\('/signup'.*?def signup\(\):.*?(?=@app\.route|\Z)", signup_code.strip(), code, flags=re.DOTALL)
else:
    code += "\n" + signup_code

with open('app.py', 'w') as f:
    f.write(code)

print("✅ Original code restored successfully!")
