from PIL import Image, ImageDraw, ImageFont
import os
W,H=1380,820
out=r"C:\Users\epand\Downloads\kaggriculture\ui_preview\v5_dashboard.png"
def f(s,b=False):
    try: return ImageFont.truetype("arialbd.ttf" if b else "arial.ttf",s)
    except: return ImageFont.load_default()
img=Image.new("RGB",(W,H),"#0a1428")
d=ImageDraw.Draw(img)
# topbar
d.rectangle([(0,0),(W,62)],fill="#0a1428")
d.rounded_rectangle([(12,10),(56,52)],radius=10,fill="white")
d.text((34,31),"A",font=f(20,True),fill="#0a1428",anchor="mm")
d.text((65,22),"SmartFind AI",font=f(20,True),fill="white",anchor="lm")
d.text((65,42),"Find • Track • Secure",font=f(11),fill="#8a9bb5",anchor="lm")
d.text((W-20,31),"Admin  Backend Offline | 0 camera(s) connected",font=f(13),fill="#f0a35e",anchor="rm")
# sidebar
d.rounded_rectangle([(12,75),(232,H-12)],radius=14,fill="#0e1d38")
y=95
for txt,act in [("Dashboard",True),("Live Cameras",False),("Video Search",False),("Report",False),("Settings",False)]:
    if act: d.rounded_rectangle([(22,y),(222,y+38)],radius=8,fill="#2f80ed")
    d.text((40,y+19),txt,font=f(14,act),fill="white",anchor="lm")
    y+=46
d.rounded_rectangle([(22,H-170),(222,H-70)],radius=10,outline="#1e3a5f")
d.text((32,H-150),"Authorized Access Only",font=f(11,True),fill="white",anchor="lm")
d.text((32,H-130),"Security & defence use",font=f(10),fill="#8a9bb5",anchor="lm")
d.text((32,H-35),"SmartFind AI V5.0",font=f(11),fill="#2f80ed",anchor="lm")
# banner
d.rounded_rectangle([(245,75),(W-12,190)],radius=14,fill="#132442",outline="#1e3a5f")
d.text((270,105),"Welcome to SmartFind AI",font=f(24,True),fill="white",anchor="lm")
d.text((270,135),"Search across multiple camera feeds. Track movements. Get results.",font=f(12),fill="#8a9bb5",anchor="lm")
# stats
for i,(n,l) in enumerate([("0","Cameras connected"),("0","Candidate matches"),("5","AI models in pipeline")]):
    x0=245+i*365
    d.rounded_rectangle([(x0,202),(x0+353,285)],radius=12,fill="#132442",outline="#1e3a5f")
    d.text((x0+176,230),n,font=f(28,True),fill="#2f80ed",anchor="mm")
    d.text((x0+176,260),l,font=f(11),fill="#8a9bb5",anchor="mm")
# trio
for i,(t,btn) in enumerate([("Find","Start Search"),("Track","View Cameras"),("Secure","See Results")]):
    x0=245+i*365
    d.rounded_rectangle([(x0,297),(x0+353,560)],radius=12,fill="#132442",outline="#1e3a5f")
    d.text((x0+176,380),t,font=f(17,True),fill="white",anchor="mm")
    d.rounded_rectangle([(x0+15,505),(x0+338,540)],radius=8,fill="#1a3355")
    d.text((x0+176,522),btn+" ->",font=f(12),fill="#7fb3ff",anchor="mm")
# how
d.rounded_rectangle([(245,572),(W-12,H-12)],radius=14,fill="#132442",outline="#1e3a5f")
d.text((270,595),"How it works",font=f(15,True),fill="white",anchor="lm")
d.text((270,618),"Detection -> tracking -> face + appearance match -> report.",font=f(11),fill="#8a9bb5",anchor="lm")
for i,t in enumerate(["Target","Detect","Track","Match","Report"]):
    x0=260+i*225
    d.rounded_rectangle([(x0,640),(x0+210,750)],radius=10,outline="#1e3a5f")
    d.text((x0+105,695),t,font=f(13,True),fill="white",anchor="mm")
img.save(out)
print("saved "+out)
