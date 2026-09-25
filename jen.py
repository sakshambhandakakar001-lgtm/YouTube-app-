cd ~/minecraft-generator
cat << 'EOF' > generate.py
import os
import sys
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def generate_animation():
    prompt = """
    Write a complete, single standalone HTML file with embedded CSS and JavaScript.
    Create a 2D Minecraft-style animation using HTML5 Canvas:
    - Scene: Steve running automatically from left to right in a pixelated world.
    - He encounters Lava pits and jumps smoothly over them.
    - Clean pixel-art blocks (grass, dirt, lava, sky, Steve character).
    - Canvas size set to 1080x1920 (Vertical Shorts format).
    - Continuous smooth loop using requestAnimationFrame.
    Return ONLY raw valid HTML code without markdown codeblocks or explanation.
    """
    
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=prompt
    )
    
    clean_code = response.text.replace('```html', '').replace('```', '').strip()
    
    with open("animation.html", "w") as f:
        f.write(clean_code)
    
    print("HTML Animation generated successfully!")

if __name__ == "__main__":
    generate_animation()
EOF
