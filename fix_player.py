with open('app.py', 'r') as f:
    code = f.read()

# Replace hardcoded local video tag with dynamic YouTube embed player logic
old_video_tag = '<video controls style="width:100%; height:220px;">'
new_player_logic = '''{% if 'youtube.com' in v['filename'] or 'youtu.be' in v['filename'] %}
    {% set video_id = v['filename'].split('v=')[-1].split('&')[0].split('/')[-1] %}
    <iframe src="https://www.youtube.com/embed/{{ video_id }}" style="width:100%; height:220px; border:none;" allowfullscreen></iframe>
{% else %}
    <video controls style="width:100%; height:220px;">
{% endif %}'''

if old_video_tag in code and 'youtube.com' not in code:
    code = code.replace(old_video_tag, new_player_logic)
    with open('app.py', 'w') as f:
        f.write(code)
    print("Player safely updated in app.py!")
else:
    print("app.py is already up to date or structurally custom.")
