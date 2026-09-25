with open('app.py', 'r') as f:
    code = f.read()

# 1. Limit database fetch query to avoid freeze on ALL category
code = code.replace("SELECT * FROM videos", "SELECT * FROM videos ORDER BY id DESC LIMIT 20")
code = code.replace("SELECT * FROM videos WHERE category=?", "SELECT * FROM videos WHERE category=? ORDER BY id DESC LIMIT 20")

# 2. Fix dynamic iframe player embed display issue
old_player = '<source src="/videos/{{ v[\'filename\'] }}" type="video/mp4">'
new_player = '''<iframe src="{{ v['filename'].replace('watch?v=', 'embed/') if 'youtube.com' in v['filename'] else v['filename'] }}" style="width:100%; height:210px; border:none; background:#000;" allowfullscreen></iframe>'''

if old_player in code:
    code = code.replace(old_player, new_player)

with open('app.py', 'w') as f:
    f.write(code)

print("App optimized for low-end devices and fast loading!")
