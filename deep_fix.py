import re

with open('appp.py', 'r') as f:
    content = f.read()

# Remove 'f' prefix before triple quotes or single quotes containing HTML/Jinja
# Replaces f""" with """ and f''' with '''
content = re.sub(r'f("""|\'\'\')', r'\1', content)

# Save fixed code to app.py
with open('app.py', 'w') as f:
    f.write(content)

print("✅ F-string issue fixed successfully!")
