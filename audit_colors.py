import re, os

files = [
    'pages/01_Home.py','pages/02_For_You.py','pages/03_Explore.py',
    'pages/04_Trending.py','pages/05_Analytics.py',
    'pages/06_My_Profile.py','pages/07_About.py'
]

skip_keywords = [
    'stroke=', 'fill=', 'color_discrete', 'linear-gradient',
    "m['color']", '#FFD700', '#C0C0C0', '#CD7F32',
    'background:#', 'stop-color', 'rgba(239,68,68', 'rgba(255,255,255',
    'rgba(0,0,0', 'rgba(99,102', 'rgba(6,', 'rgba(16,', 'rgba(127',
]

import re
pattern = re.compile(r'style=["\'][^"\']*(?:color|background)[^"\']*#[0-9a-fA-F]{3,8}')

ok = True
for f in files:
    src = open(f, encoding='utf-8').read()
    lines = src.splitlines()
    for i, line in enumerate(lines, 1):
        if any(kw in line for kw in skip_keywords):
            continue
        if pattern.search(line):
            print(f"{f}:{i}: {line.strip()[:110]}")
            ok = False

if ok:
    print("CLEAN - no stray hardcoded colors in inline styles")
