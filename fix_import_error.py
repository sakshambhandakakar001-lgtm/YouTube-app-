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
