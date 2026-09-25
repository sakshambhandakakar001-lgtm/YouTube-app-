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
