with open("app.py", "r") as f:
    content = f.read()

if "reels_bp" not in content:
    new_content = "from reels_feature import reels_bp\n" + content
    new_content = new_content.replace("app = Flask(__name__)", "app = Flask(__name__)\napp.register_blueprint(reels_bp)")
    with open("app.py", "w") as f:
        f.write(new_content)
    print("✅ Reels feed attached successfully!")
else:
    print("✅ Already attached!")
