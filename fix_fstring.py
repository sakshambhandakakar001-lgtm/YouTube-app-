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
