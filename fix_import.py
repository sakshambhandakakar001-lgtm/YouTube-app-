with open('app.py', 'r') as f:
    code = f.read()

# Flask imports fix
import_line = "from flask import Flask, render_template, request, redirect, session, url_for"

if "from flask import" in code:
    lines = code.split('\n')
    for i, line in enumerate(lines):
        if line.startswith("from flask import"):
            lines[i] = import_line
            break
    code = '\n'.join(lines)
else:
    code = import_line + "\n" + code

with open('app.py', 'w') as f:
    f.write(code)

print("✅ Flask imports fixed successfully!")
