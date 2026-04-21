import re

def strip_iframe(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    text = re.sub(r'<!-- JavaScript executor via Iframe bypass -->[\s\S]*?\"></iframe>\n?', '', text)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)

strip_iframe('auth/login.py')
strip_iframe('auth/signup.py')
print("Successfully stripped iframes from both files.")
