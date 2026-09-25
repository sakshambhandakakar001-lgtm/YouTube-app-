import re

with open('app.py', 'r') as f:
    code = f.read()

# Fix f-string rendering issue
fixed_code = re.sub(r'f("""|\'\'\')', r'\1', code)

with open('app.py', 'w') as f:
    f.write(fixed_code)

print("✅ Original Code Successfully Restored from Backup!")
