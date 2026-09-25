import re

with open('app.py', 'r') as f:
    code = f.read()

# Replace app.py rendering logic safely
new_helper = '''
def get_yt_id(url):
    if not url: return ""
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return url
app.jinja_env.globals.update(get_yt_id=get_yt_id)
'''

if 'def get_yt_id' not in code:
    code = code.replace("app = Flask(__name__)", "app = Flask(__name__)\n" + new_helper)

with open('app.py', 'w') as f:
    f.write(code)

print("App helper function added!")
