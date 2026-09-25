<!-- ==========================================
     FILE: templates/my_channel.html
     FEATURE: Creator Dashboard & Uploaded Videos List
     ================================---------- -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>My Channel</title>
</head>
<body>
    <h1>Welcome to My Channel</h1>
    <a href="/logout">Logout</a>
    
    <h3>Your Videos</h3>
    <ul>
        {% for v in videos %}
        <li>
            <b>{{ v.title }}</b> - {{ v.likes }} Likes
            <a href="/video/edit/{{ v.id }}">Edit</a>
            <form action="/video/delete/{{ v.id }}" method="POST" style="display:inline;">
                <button type="submit">Delete</button>
            </form>
        </li>
        {% else %}
        <p>No videos uploaded yet.</p>
        {% endfor %}
    </ul>
</body>
</html>
