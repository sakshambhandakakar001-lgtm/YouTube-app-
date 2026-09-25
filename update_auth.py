import os

# 1. Update templates/login.html
login_html = '''<!DOCTYPE html>
<html lang="hi">
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flixify Pro - Authentication</title>
    <style>
        body { background:#0f0f0f; color:#fff; font-family:sans-serif; margin:0; display:flex; justify-content:center; align-items:center; min-height:100vh; padding:20px; box-sizing:border-box; }
        .auth-card { background:#181818; border:1px solid #282828; border-radius:16px; padding:24px; width:100%; max-width:380px; box-shadow:0 8px 24px rgba(0,0,0,0.5); }
        h2 { margin-top:0; color:#f1f1f1; font-size:22px; text-align:center; }
        .input-group { margin-bottom:14px; }
        label { font-size:12px; color:#aaa; display:block; margin-bottom:6px; }
        input { width:100%; padding:12px; background:#0f0f0f; border:1px solid #333; color:#fff; border-radius:8px; box-sizing:border-box; font-size:14px; outline:none; }
        input:focus { border-color:#3ea6ff; }
        button { width:100%; padding:12px; background:#e50914; color:#fff; font-weight:bold; border:none; border-radius:20px; font-size:15px; cursor:pointer; margin-top:10px; }
        .toggle-btn { text-align:center; margin-top:16px; font-size:13px; color:#aaa; cursor:pointer; }
        .toggle-btn span { color:#3ea6ff; text-decoration:underline; }
        .error-msg { color:#ff4e4e; font-size:12px; margin-bottom:10px; display:none; text-align:center; }
    </style>
</head>
<body>

<div class="auth-card">
    <h2 id="form-title">Create Account</h2>
    <div id="err-box" class="error-msg"></div>

    <!-- SIGN UP FORM (Naye Users Ke Liye) -->
    <form id="signup-form" action="/signup" method="POST">
        <div class="input-group">
            <label>Username</label>
            <input type="text" name="username" placeholder="Apna Username dalein" required>
        </div>
        <div class="input-group">
            <label>Password</label>
            <input type="password" name="password" placeholder="Password create karein" required>
        </div>
        <div class="input-group">
            <label>Email ID (Ek Email se ek hi account banega)</label>
            <input type="email" name="email" placeholder="example@gmail.com" required>
        </div>
        <button type="submit" style="background:#3ea6ff; color:#000;">Sign Up & Continue</button>
    </form>

    <!-- LOGIN FORM (Purane Users Ke Liye) -->
    <form id="login-form" action="/login" method="POST" style="display:none;">
        <div class="input-group">
            <label>Email ID</label>
            <input type="email" name="email" placeholder="Apni Email ID dalein" required>
        </div>
        <div class="input-group">
            <label>Password</label>
            <input type="password" name="password" placeholder="Password dalein" required>
        </div>
        <button type="submit">Log In</button>
    </form>

    <div class="toggle-btn" id="toggle-link" onclick="toggleAuth()">
        Pehle se account hai? <span>Log In Karein</span>
    </div>
</div>

<script>
    var isLogin = false;
    function toggleAuth() {
        isLogin = !isLogin;
        var title = document.getElementById('form-title');
        var suForm = document.getElementById('signup-form');
        var lgForm = document.getElementById('login-form');
        var toggleLink = document.getElementById('toggle-link');

        if (isLogin) {
            title.innerText = 'Welcome Back (Log In)';
            suForm.style.display = 'none';
            lgForm.style.display = 'block';
            toggleLink.innerHTML = 'Naye user ho? <span>Sign Up Karein</span>';
        } else {
            title.innerText = 'Create Account';
            suForm.style.display = 'block';
            lgForm.style.display = 'none';
            toggleLink.innerHTML = 'Pehle se account hai? <span>Log In Karein</span>';
        }
    }
</script>

</body>
</html>
'''

os.makedirs('templates', exist_ok=True)
with open('templates/login.html', 'w') as f:
    f.write(login_html)

with open('templates/signup.html', 'w') as f:
    f.write(login_html)

print("✅ Sign Up & Email Registration UI updated successfully!")
