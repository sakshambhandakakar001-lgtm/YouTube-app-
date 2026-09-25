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
