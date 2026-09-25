with open('app.py', 'r') as f:
    code = f.read()

# Incorrect local source tag replacement with smart YouTube embed / direct video handling
old_source = '<source src="/videos/{{ v[\'filename\'] }}" type="video/mp4">'
new_source = '''{% if 'youtube.com/embed' in v['filename'] %}
<iframe src="{{ v['filename'] }}" style="width:100%; height:100%; border:none;" allowfullscreen></iframe>
{% else %}
<source src="/videos/{{ v['filename'] }}" type="video/mp4">
{% endif %}'''

if old_source in code:
    code = code.replace(old_source, new_source)
    with open('app.py', 'w') as f:
        f.write(code)
    print("app.py template successfully updated!")
else:
    print("Source tag format alternate / already modified.")
