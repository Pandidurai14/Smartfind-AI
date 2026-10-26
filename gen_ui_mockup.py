from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1380, 820
img = Image.new('RGB', (W, H), '#0a1428')
d = ImageDraw.Draw(img)

try:
    font_bold = ImageFont.truetype('arialbd.ttf', 22)
    font_norm = ImageFont.truetype('arial.ttf', 14)
    font_small = ImageFont.truetype('arial.ttf', 11)
    font_title = ImageFont.truetype('arialbd.ttf', 28)
except:
    font_bold = font_norm = font_small = font_title = ImageFont.load_default()

BG = '#0a1428'; SIDEBAR = '#0e1d38'; CARD = '#132442'; BORDER = '#1e3a5f'
ACCENT = '#2f80ed'; WHITE = '#ffffff'; MUTED = '#8a9bb5'
GREEN = '#2ecc71'; ORANGE = '#f39c12'; RED = '#e74c3c'

# Top bar
d.rectangle([0, 0, W, 62], fill=BG)
d.rounded_rectangle([16, 10, 60, 54], radius=10, fill='white')
d.text((28, 16), 'AV', fill='#0a1428', font=font_bold)
d.text((72, 12), 'SmartFind AI', fill=WHITE, font=font_bold)
d.text((72, 36), 'Find - Track - Secure', fill=MUTED, font=font_small)
d.text((W-280, 20), 'Admin', fill=WHITE, font=font_norm)
d.text((W-150, 20), 'Online - YOLO + Face', fill=GREEN, font=font_small)
d.line([(24, 62), (W-24, 62)], fill=BORDER, width=1)

# Sidebar
sb_x, sb_y, sb_w = 12, 74, 220
d.rounded_rectangle([sb_x, sb_y, sb_x+sb_w, H-12], radius=14, fill=SIDEBAR)
d.text((sb_x+20, sb_y+14), 'MENU', fill=MUTED, font=font_small)
nav_items = ['Dashboard', 'Live Cameras', 'Video Search', 'Matches', 'Report', 'Settings']
for i, txt in enumerate(nav_items):
    y = sb_y + 34 + i * 46
    if i == 0:
        d.rounded_rectangle([sb_x+10, y, sb_x+sb_w-10, y+42], radius=8, fill=ACCENT)
        d.text((sb_x+20, y+10), txt, fill=WHITE, font=font_norm)
    else:
        d.text((sb_x+20, y+10), txt, fill=MUTED, font=font_norm)
d.rounded_rectangle([sb_x+10, H-120, sb_x+sb_w-10, H-30], radius=10, outline=BORDER, width=1)
d.text((sb_x+20, H-110), 'Authorized Access Only', fill=WHITE, font=font_small)
d.text((sb_x+20, H-90), 'Security & defence use only.', fill=MUTED, font=font_small)

# Main content
mx = 252; mw = W - mx - 24
d.rounded_rectangle([mx, 74, mx+mw, 130], radius=14, fill=CARD, outline=BORDER, width=1)
d.rounded_rectangle([mx+14, 84, mx+18, 120], radius=2, fill=ACCENT)
d.text((mx+30, 88), 'Welcome to SmartFind AI', fill=WHITE, font=font_bold)
d.text((mx+30, 112), 'Search across multiple camera feeds. Track movements.', fill=MUTED, font=font_small)

stats = ['0', '0', '5']
labels = ['Cameras connected', 'Candidate matches', 'AI models']
cw = (mw - 30) // 3
for i, (num, lbl) in enumerate(zip(stats, labels)):
    x = mx + i * (cw + 10)
    d.rounded_rectangle([x, 142, x+cw, 220], radius=12, fill=CARD, outline=BORDER, width=1)
    d.rounded_rectangle([x+10, 154, x+66, 158], radius=2, fill=ACCENT)
    d.text((x+cw//2-15, 166), num, fill=ACCENT, font=font_title)
    d.text((x+10, 200), lbl, fill=MUTED, font=font_small)

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
    d.text((x+fcw//2-30, 260), ['SEARCH', 'TRACK', 'SHIELD'][i], fill=col, font=font_bold)
    d.text((x+fcw//2-20, 320), title, fill=WHITE, font=font_bold)
    d.text((x+10, 344), desc, fill=MUTED, font=font_small)
    d.rounded_rectangle([x+10, 392, x+fcw-10, 420], radius=6, fill='#1a3355')
    d.text((x+fcw//2-40, 398), btn, fill='#7fb3ff', font=font_small)

d.rounded_rectangle([mx, 432, mx+mw, 580], radius=14, fill=CARD, outline=BORDER, width=1)
d.text((mx+18, 444), 'How it works', fill=WHITE, font=font_bold)
d.text((mx+18, 472), 'Detection - tracking - face match - report', fill=MUTED, font=font_small)
steps = ['Target', 'Detect', 'Track', 'Match', 'Report']
sw = (mw - 60) // 5
for i, step in enumerate(steps):
    x = mx + 18 + i * (sw + 8)
    d.rounded_rectangle([x, 490, x+sw, 570], radius=10, outline=BORDER, width=1)
    d.text((x+sw//2-20, 510), f'Step {i+1}', fill='#38bdf8', font=font_small)
    d.text((x+sw//2-20, 536), step, fill=WHITE, font=font_bold)
    if i < 4:
        d.text((x+sw+1, 520), '>', fill=GREEN, font=font_bold)

d.text((mx, H-30), 'SmartFind AI V5.0  |  AI-Powered Multi-Camera Search', fill=ACCENT, font=font_small)

out = r'C:\Users\epand\Downloads\kaggriculture\ui_preview\ui_mockup_generated.png'
img.save(out)
print(f'Saved: {out}')
