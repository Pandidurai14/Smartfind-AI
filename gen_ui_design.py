from PIL import Image, ImageDraw, ImageFont
import os

# ===== PAGE 1: DASHBOARD =====
W, H = 1380, 820
img = Image.new('RGB', (W, H), '#0a1428')
d = ImageDraw.Draw(img)

try:
    fb = ImageFont.truetype('arialbd.ttf', 22)
    fn = ImageFont.truetype('arial.ttf', 14)
    fs = ImageFont.truetype('arial.ttf', 11)
    ft = ImageFont.truetype('arialbd.ttf', 28)
    fbig = ImageFont.truetype('arialbd.ttf', 36)
except:
    fb = fn = fs = ft = fbig = ImageFont.load_default()

# Colors
BG = '#0a1428'; SIDEBAR = '#0e1d38'; CARD = '#132442'; BORDER = '#1e3a5f'
ACCENT = '#2f80ed'; WHITE = '#ffffff'; MUTED = '#8a9bb5'
GREEN = '#2ecc71'; ORANGE = '#f39c12'; RED = '#e74c3c'

# Top bar
d.rectangle([0, 0, W, 62], fill=BG)
d.rounded_rectangle([16, 10, 60, 54], radius=10, fill='white')
d.text((28, 16), 'AV', fill='#0a1428', font=fb)
d.text((72, 12), 'SmartFind AI', fill=WHITE, font=fb)
d.text((72, 36), 'Find - Track - Secure', fill=MUTED, font=fs)
d.text((W-280, 20), 'Admin', fill=WHITE, font=fn)
d.text((W-150, 20), 'Online - YOLO + Face', fill=GREEN, font=fs)
d.line([(24, 62), (W-24, 62)], fill=BORDER, width=1)

# Sidebar
sb_x, sb_y, sb_w = 12, 74, 220
d.rounded_rectangle([sb_x, sb_y, sb_x+sb_w, H-12], radius=14, fill=SIDEBAR)
d.text((sb_x+20, sb_y+14), 'MENU', fill=MUTED, font=fs)
nav_items = ['Dashboard', 'Live Cameras', 'Video Search', 'Matches', 'Report', 'Settings']
for i, txt in enumerate(nav_items):
    y = sb_y + 34 + i * 46
    if i == 0:
        d.rounded_rectangle([sb_x+10, y, sb_x+sb_w-10, y+42], radius=8, fill=ACCENT)
        d.text((sb_x+20, y+10), txt, fill=WHITE, font=fn)
    else:
        d.text((sb_x+20, y+10), txt, fill=MUTED, font=fn)
d.rounded_rectangle([sb_x+10, H-120, sb_x+sb_w-10, H-30], radius=10, outline=BORDER, width=1)
d.text((sb_x+20, H-110), 'Authorized Access Only', fill=WHITE, font=fs)
d.text((sb_x+20, H-90), 'Security & defence use only.', fill=MUTED, font=fs)

# Main content
mx = 252; mw = W - mx - 24

# Welcome banner
d.rounded_rectangle([mx, 74, mx+mw, 130], radius=14, fill=CARD, outline=BORDER, width=1)
d.rounded_rectangle([mx+14, 84, mx+18, 120], radius=2, fill=ACCENT)
d.text((mx+30, 88), 'Welcome to SmartFind AI', fill=WHITE, font=fb)
d.text((mx+30, 112), 'Search across multiple camera feeds. Track movements.', fill=MUTED, font=fs)

# Stats cards
stats = ['3', '12', '5']
labels = ['Cameras connected', 'Candidate matches', 'AI models']
cw = (mw - 30) // 3
for i, (num, lbl) in enumerate(zip(stats, labels)):
    x = mx + i * (cw + 10)
    d.rounded_rectangle([x, 142, x+cw, 220], radius=12, fill=CARD, outline=BORDER, width=1)
    d.rounded_rectangle([x+10, 154, x+66, 158], radius=2, fill=ACCENT)
    d.text((x+cw//2-15, 166), num, fill=ACCENT, font=ft)
    d.text((x+10, 200), lbl, fill=MUTED, font=fs)

# Feature cards
features = [
    ('Find', 'One photo searches every camera.', 'Start Search', ACCENT),
    ('Track', 'Candidates linked to timeline.', 'View Cameras', GREEN),
    ('Secure', 'Evidence snapshots + report.', 'See Results', ORANGE),
]
fcw = (mw - 30) // 3
for i, (title, desc, btn, col) in enumerate(features):
    x = mx + i * (fcw + 10)
    d.rounded_rectangle([x, 232, x+fcw, 420], radius=12, fill=CARD, outline=BORDER, width=1)
    d.rounded_rectangle([x+10, 244, x+fcw-10, 310], radius=8, fill='#0b1a33')
    d.text((x+fcw//2-30, 260), ['SEARCH', 'TRACK', 'SHIELD'][i], fill=col, font=fb)
    d.text((x+fcw//2-20, 320), title, fill=WHITE, font=fb)
    d.text((x+10, 344), desc, fill=MUTED, font=fs)
    d.rounded_rectangle([x+10, 392, x+fcw-10, 420], radius=6, fill='#1a3355')
    d.text((x+fcw//2-40, 398), btn, fill='#7fb3ff', font=fs)

# How it works
d.rounded_rectangle([mx, 432, mx+mw, 580], radius=14, fill=CARD, outline=BORDER, width=1)
d.text((mx+18, 444), 'How it works', fill=WHITE, font=fb)
d.text((mx+18, 472), 'Detection - tracking - face match - report', fill=MUTED, font=fs)
steps = ['Target', 'Detect', 'Track', 'Match', 'Report']
sw = (mw - 60) // 5
for i, step in enumerate(steps):
    x = mx + 18 + i * (sw + 8)
    d.rounded_rectangle([x, 490, x+sw, 570], radius=10, outline=BORDER, width=1)
    d.text((x+sw//2-20, 510), f'Step {i+1}', fill='#38bdf8', font=fs)
    d.text((x+sw//2-20, 536), step, fill=WHITE, font=fb)
    if i < 4:
        d.text((x+sw+1, 520), '>', fill=GREEN, font=fb)

d.text((mx, H-30), 'SmartFind AI V5.0  |  AI-Powered Multi-Camera Search', fill=ACCENT, font=fs)

img.save(r'C:\Users\epand\Downloads\kaggriculture\ui_preview\design_dashboard.png')
print('Dashboard saved!')

# ===== PAGE 2: LIVE CAMERA =====
img2 = Image.new('RGB', (W, H), '#0a1428')
d2 = ImageDraw.Draw(img2)

# Top bar
d2.rectangle([0, 0, W, 62], fill=BG)
d2.rounded_rectangle([16, 10, 60, 54], radius=10, fill='white')
d2.text((28, 16), 'AV', fill='#0a1428', font=fb)
d2.text((72, 12), 'SmartFind AI', fill=WHITE, font=fb)
d2.text((72, 36), 'Find - Track - Secure', fill=MUTED, font=fs)
d2.text((W-280, 20), 'Admin', fill=WHITE, font=fn)
d2.text((W-150, 20), 'Online - YOLO + Face', fill=GREEN, font=fs)
d2.line([(24, 62), (W-24, 62)], fill=BORDER, width=1)

# Sidebar
d2.rounded_rectangle([sb_x, sb_y, sb_x+sb_w, H-12], radius=14, fill=SIDEBAR)
d2.text((sb_x+20, sb_y+14), 'MENU', fill=MUTED, font=fs)
for i, txt in enumerate(nav_items):
    y = sb_y + 34 + i * 46
    if i == 1:
        d2.rounded_rectangle([sb_x+10, y, sb_x+sb_w-10, y+42], radius=8, fill=ACCENT)
        d2.text((sb_x+20, y+10), txt, fill=WHITE, font=fn)
    else:
        d2.text((sb_x+20, y+10), txt, fill=MUTED, font=fn)
d2.rounded_rectangle([sb_x+10, H-120, sb_x+sb_w-10, H-30], radius=10, outline=BORDER, width=1)
d2.text((sb_x+20, H-110), 'Authorized Access Only', fill=WHITE, font=fs)
d2.text((sb_x+20, H-90), 'Security & defence use only.', fill=MUTED, font=fs)

# Main content
mx = 252; mw = W - mx - 24

# Top controls
d2.rounded_rectangle([mx, 74, mx+mw, 120], radius=12, fill=CARD, outline=BORDER, width=1)
d2.rounded_rectangle([mx+10, 84, mx+140, 110], radius=6, fill=ACCENT)
d2.text((mx+25, 90), 'Upload Target', fill=WHITE, font=fn)
d2.rounded_rectangle([mx+150, 84, mx+280, 110], radius=6, fill=RED)
d2.text((mx+175, 90), 'Stop Camera', fill=WHITE, font=fn)
d2.text((mx+300, 90), 'Live Camera Search', fill=WHITE, font=fb)

# Video feed area
d2.rounded_rectangle([mx, 130, mx+mw-320, H-40], radius=12, fill='#000000', outline=BORDER, width=1)
# Simulated detection box
d2.rectangle([mx+200, 250, mx+440, 490], outline=GREEN, width=3)
d2.text((mx+200, 230), 'ID:1 | MATCH 87.50%', fill=GREEN, font=fn)
d2.text((mx+mw//2-100, H-60), '[ LIVE VIDEO FEED 640x480 ]', fill=MUTED, font=fs)

# Right panel
rx = mx+mw-300
d2.rounded_rectangle([rx, 130, rx+280, H-40], radius=12, fill=CARD, outline=BORDER, width=1)
d2.text((rx+60, 150), 'Live Similarity', fill=WHITE, font=fn)
d2.text((rx+40, 180), '87.50%', fill=GREEN, font=fbig)
d2.text((rx+70, 230), 'Match Graph', fill=MUTED, font=fn)
# Graph area
d2.rounded_rectangle([rx+20, 260, rx+260, 400], radius=8, fill='#0b1a33')
# Draw graph line
for i in range(19):
    x1 = rx+30 + i*12
    y1 = 330 - (i % 5) * 15
    x2 = rx+30 + (i+1)*12
    y2 = 330 - ((i+1) % 5) * 15
    d2.line([(x1, y1), (x2, y2)], fill=GREEN, width=2)

d2.text((rx+40, 420), 'Enhanced Match Capture', fill=WHITE, font=fn)
d2.rounded_rectangle([rx+70, 450, rx+210, 590], radius=10, fill='#1a2f52')
d2.text((rx+100, 500), '> photo', fill=MUTED, font=fn)
d2.text((rx+20, 620), 'Green = Match | Orange = Hidden | Red = No Match', fill=MUTED, font=fs)

img2.save(r'C:\Users\epand\Downloads\kaggriculture\ui_preview\design_live_camera.png')
print('Live Camera saved!')

# ===== PAGE 3: VIDEO SEARCH =====
img3 = Image.new('RGB', (W, H), '#0a1428')
d3 = ImageDraw.Draw(img3)

# Top bar
d3.rectangle([0, 0, W, 62], fill=BG)
d3.rounded_rectangle([16, 10, 60, 54], radius=10, fill='white')
d3.text((28, 16), 'AV', fill='#0a1428', font=fb)
d3.text((72, 12), 'SmartFind AI', fill=WHITE, font=fb)
d3.text((72, 36), 'Find - Track - Secure', fill=MUTED, font=fs)
d3.text((W-280, 20), 'Admin', fill=WHITE, font=fn)
d3.text((W-150, 20), 'Online - YOLO + Face', fill=GREEN, font=fs)
d3.line([(24, 62), (W-24, 62)], fill=BORDER, width=1)

# Sidebar
d3.rounded_rectangle([sb_x, sb_y, sb_x+sb_w, H-12], radius=14, fill=SIDEBAR)
d3.text((sb_x+20, sb_y+14), 'MENU', fill=MUTED, font=fs)
for i, txt in enumerate(nav_items):
    y = sb_y + 34 + i * 46
    if i == 2:
        d3.rounded_rectangle([sb_x+10, y, sb_x+sb_w-10, y+42], radius=8, fill=ACCENT)
        d3.text((sb_x+20, y+10), txt, fill=WHITE, font=fn)
    else:
        d3.text((sb_x+20, y+10), txt, fill=MUTED, font=fn)
d3.rounded_rectangle([sb_x+10, H-120, sb_x+sb_w-10, H-30], radius=10, outline=BORDER, width=1)
d3.text((sb_x+20, H-110), 'Authorized Access Only', fill=WHITE, font=fs)
d3.text((sb_x+20, H-90), 'Security & defence use only.', fill=MUTED, font=fs)

# Main content
mx = 252; mw = W - mx - 24

# Top controls
d3.rounded_rectangle([mx, 74, mx+mw, 120], radius=12, fill=CARD, outline=BORDER, width=1)
d3.rounded_rectangle([mx+10, 84, mx+160, 110], radius=6, fill=ACCENT)
d3.text((mx+25, 90), '1. Target Image', fill=WHITE, font=fn)
d3.rounded_rectangle([mx+170, 84, mx+320, 110], radius=6, fill=ACCENT)
d3.text((mx+195, 90), '2. Select Video', fill=WHITE, font=fn)
d3.rounded_rectangle([mx+330, 84, mx+460, 110], radius=6, fill=RED)
d3.text((mx+355, 90), 'Stop Video', fill=WHITE, font=fn)
d3.text((mx+480, 90), 'Video File Search', fill=WHITE, font=fb)

# Video feed area
d3.rounded_rectangle([mx, 130, mx+mw-320, H-40], radius=12, fill='#000000', outline=BORDER, width=1)
# Simulated detection box
d3.rectangle([mx+200, 250, mx+440, 490], outline=GREEN, width=3)
d3.text((mx+200, 230), 'ID:1 | MATCH 87.50%', fill=GREEN, font=fn)
d3.text((mx+mw//2-100, H-60), '[ VIDEO FILE PLAYBACK 640x480 ]', fill=MUTED, font=fs)

# Right panel
rx = mx+mw-300
d3.rounded_rectangle([rx, 130, rx+280, H-40], radius=12, fill=CARD, outline=BORDER, width=1)
d3.text((rx+60, 150), 'Live Similarity', fill=WHITE, font=fn)
d3.text((rx+40, 180), '87.50%', fill=GREEN, font=fbig)
d3.text((rx+70, 230), 'Match Graph', fill=MUTED, font=fn)
d3.rounded_rectangle([rx+20, 260, rx+260, 400], radius=8, fill='#0b1a33')
for i in range(19):
    x1 = rx+30 + i*12
    y1 = 330 - (i % 5) * 15
    x2 = rx+30 + (i+1)*12
    y2 = 330 - ((i+1) % 5) * 15
    d3.line([(x1, y1), (x2, y2)], fill=GREEN, width=2)

d3.text((rx+40, 420), 'Enhanced Match Capture', fill=WHITE, font=fn)
d3.rounded_rectangle([rx+70, 450, rx+210, 590], radius=10, fill='#1a2f52')
d3.text((rx+100, 500), '> photo', fill=MUTED, font=fn)
d3.text((rx+20, 620), 'Green = Match | Orange = Hidden | Red = No Match', fill=MUTED, font=fs)

img3.save(r'C:\Users\epand\Downloads\kaggriculture\ui_preview\design_video_search.png')
print('Video Search saved!')

# ===== PAGE 4: SETTINGS =====
img4 = Image.new('RGB', (W, H), '#0a1428')
d4 = ImageDraw.Draw(img4)

# Top bar
d4.rectangle([0, 0, W, 62], fill=BG)
d4.rounded_rectangle([16, 10, 60, 54], radius=10, fill='white')
d4.text((28, 16), 'AV', fill='#0a1428', font=fb)
d4.text((72, 12), 'SmartFind AI', fill=WHITE, font=fb)
d4.text((72, 36), 'Find - Track - Secure', fill=MUTED, font=fs)
d4.text((W-280, 20), 'Admin', fill=WHITE, font=fn)
d4.text((W-150, 20), 'Online - YOLO + Face', fill=GREEN, font=fs)
d4.line([(24, 62), (W-24, 62)], fill=BORDER, width=1)

# Sidebar
d4.rounded_rectangle([sb_x, sb_y, sb_x+sb_w, H-12], radius=14, fill=SIDEBAR)
d4.text((sb_x+20, sb_y+14), 'MENU', fill=MUTED, font=fs)
for i, txt in enumerate(nav_items):
    y = sb_y + 34 + i * 46
    if i == 5:
        d4.rounded_rectangle([sb_x+10, y, sb_x+sb_w-10, y+42], radius=8, fill=ACCENT)
        d4.text((sb_x+20, y+10), txt, fill=WHITE, font=fn)
    else:
        d4.text((sb_x+20, y+10), txt, fill=MUTED, font=fn)
d4.rounded_rectangle([sb_x+10, H-120, sb_x+sb_w-10, H-30], radius=10, outline=BORDER, width=1)
d4.text((sb_x+20, H-110), 'Authorized Access Only', fill=WHITE, font=fs)
d4.text((sb_x+20, H-90), 'Security & defence use only.', fill=MUTED, font=fs)

# Main content
mx = 252; mw = W - mx - 24

# Settings title
d4.rounded_rectangle([mx, 74, mx+mw, 130], radius=14, fill=CARD, outline=BORDER, width=1)
d4.text((mx+20, 90), 'Settings', fill=WHITE, font=ft)

# Appearance section
d4.rounded_rectangle([mx, 150, mx+mw, 280], radius=12, fill=CARD, outline=BORDER, width=1)
d4.text((mx+20, 170), 'Appearance', fill=WHITE, font=fb)
d4.text((mx+20, 200), 'Dark Mode', fill=MUTED, font=fn)
d4.rounded_rectangle([mx+150, 195, mx+200, 225], radius=15, fill=ACCENT)
d4.ellipse([mx+178, 198, mx+197, 222], fill=WHITE)
d4.text((mx+220, 200), 'Light Mode', fill=MUTED, font=fn)
d4.rounded_rectangle([mx+320, 195, mx+370, 225], radius=15, fill='#1a2f52')

# AI Thresholds section
d4.rounded_rectangle([mx, 300, mx+mw, 480], radius=12, fill=CARD, outline=BORDER, width=1)
d4.text((mx+20, 320), 'AI Thresholds', fill=WHITE, font=fb)
d4.text((mx+20, 360), 'Face Match Threshold:', fill=MUTED, font=fn)
d4.rounded_rectangle([mx+220, 355, mx+320, 385], radius=6, fill='#1a2f52')
d4.text((mx+240, 362), '0.6', fill=WHITE, font=fn)
d4.text((mx+20, 400), 'ReID Match Threshold:', fill=MUTED, font=fn)
d4.rounded_rectangle([mx+220, 395, mx+320, 425], radius=6, fill='#1a2f52')
d4.text((mx+240, 402), '0.7', fill=WHITE, font=fn)
d4.text((mx+20, 440), 'Blur Threshold:', fill=MUTED, font=fn)
d4.rounded_rectangle([mx+220, 435, mx+320, 465], radius=6, fill='#1a2f52')
d4.text((mx+240, 442), '100.0', fill=WHITE, font=fn)

# Notifications section
d4.rounded_rectangle([mx, 500, mx+mw, 620], radius=12, fill=CARD, outline=BORDER, width=1)
d4.text((mx+20, 520), 'Notifications', fill=WHITE, font=fb)
d4.text((mx+20, 560), 'Sound Alert', fill=MUTED, font=fn)
d4.rounded_rectangle([mx+150, 555, mx+200, 585], radius=15, fill=GREEN)
d4.ellipse([mx+178, 558, mx+197, 582], fill=WHITE)
d4.text((mx+220, 560), 'Auto PDF Report', fill=MUTED, font=fn)
d4.rounded_rectangle([mx+370, 555, mx+420, 585], radius=15, fill='#1a2f52')

# Save button
d4.rounded_rectangle([mx+mw-150, 640, mx+mw-20, 680], radius=8, fill=ACCENT)
d4.text((mx+mw-120, 650), 'Save', fill=WHITE, font=fb)

d4.text((mx, H-30), 'SmartFind AI V5.0  |  AI-Powered Multi-Camera Search', fill=ACCENT, font=fs)

img4.save(r'C:\Users\epand\Downloads\kaggriculture\ui_preview\design_settings.png')
print('Settings saved!')

print('\nAll 4 UI designs generated successfully!')
print('Files saved in: ui_preview/')
print('  - design_dashboard.png')
print('  - design_live_camera.png')
print('  - design_video_search.png')
print('  - design_settings.png')
