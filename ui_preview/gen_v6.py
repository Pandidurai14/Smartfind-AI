from PIL import Image, ImageDraw, ImageFont
import os
W,H=1380,860
out=r"C:\Users\epand\Downloads\kaggriculture\ui_preview\v6_dashboard.png"
def f(s,b=False):
    try: return ImageFont.truetype("arialbd.ttf" if b else "arial.ttf",s)
    except: return ImageFont.load_default()
# live counts
import glob
mdir=r"C:\Users\epand\Downloads\kaggriculture\saved_matches"
n=len(glob.glob(os.path.join(mdir,"*.jpg")))+len(glob.glob(os.path.join(mdir,"*.png")))
img=Image.new("RGB",(W,H),"#0a1428")
d=ImageDraw.Draw(img)
# topbar + sidebar (simplified)
d.rectangle([(0,0),(W,62)],fill="#0a1428")
d.rounded_rectangle([(12,10),(56,52)],radius=10,fill="white")
d.text((34,31),"A",font=f(20,True),fill="#0a1428",anchor="mm")
d.text((65,22),"SmartFind AI",font=f(20,True),fill="white",anchor="lm")
d.text((65,42),"Find - Track - Secure",font=f(11),fill="#8a9bb5",anchor="lm")
d.text((W-20,31),"Backend Online | YOLO Face | 0 camera(s)",font=f(12),fill="#2ecc71",anchor="rm")
d.rounded_rectangle([(12,75),(232,H-12)],radius=14,fill="#0e1d38")
y=95
for txt,act in [("Dashboard",True),("Live Cameras",False),("Video Search",False),("Matches",False),("Report",False),("Settings",False)]:
    if act: d.rounded_rectangle([(22,y),(222,y+36)],radius=8,fill="#2f80ed")
    d.text((40,y+18),txt,font=f(13,act),fill="white",anchor="lm")
    y+=44
# banner with cameras right
d.rounded_rectangle([(245,75),(W-12,195)],radius=14,fill="#132442",outline="#1e3a5f")
d.text((270,100),"Welcome to SmartFind AI",font=f(22,True),fill="white",anchor="lm")
d.text((270,128),"Search across multiple camera feeds. Track movements.",font=f(11),fill="#8a9bb5",anchor="lm")
d.text((270,148),"Faster. Smarter. Safer.",font=f(11),fill="#8a9bb5",anchor="lm")
# camera sketches right
for i,x in enumerate([950,1080,1210]):
    d.rectangle([(x,95),(x+70,125)],fill="#3a3f47",outline="#9ca3af",width=2)
    d.rectangle([(x+25,125),(x+40,165)],fill="#2b2f36")
# stats live
for i,(num,lbl) in enumerate([( "0","Cameras connected"),(str(n),"Candidate matches"),("5","AI models in pipeline")]):
    x0=245+i*365
    d.rounded_rectangle([(x0,207),(x0+353,290)],radius=12,fill="#132442",outline="#1e3a5f")
    d.text((x0+176,235),num,font=f(26,True),fill="#2f80ed",anchor="mm")
    d.text((x0+176,262),lbl,font=f(10),fill="#8a9bb5",anchor="mm")
# trio with icons
for i,(t,btn) in enumerate([("Find","Start Search"),("Track","View Cameras"),("Secure","See Results")]):
    x0=245+i*365
    d.rounded_rectangle([(x0,302),(x0+353,565)],radius=12,fill="#132442",outline="#1e3a5f")
    # icon box
    d.rectangle([(x0+60,320),(x0+293,410)],outline="#223a5e")
    if t=="Find":
        d.rectangle([(x0+80,330),(x0+170,395)],outline="#38bdf8",width=2)
        d.ellipse([(x0+110,x0+110-80+330),(x0+130,x0+130-80+330)],outline="#4ade80",width=2)  # approx head
        d.ellipse([(x0+175,340),(x0+215,380)],outline="#38bdf8",width=2)
        d.line([(x0+208,373),(x0+230,395)],fill="#38bdf8",width=3)
    elif t=="Track":
        d.line([(x0+60,365),(x0+293,345)],fill="#4ade80",width=2)
        for cx,tag in [(x0+80,"C1"),(x0+160,"C2"),(x0+240,"C3")]:
            d.rectangle([(cx,350),(cx+30,368)],outline="#38bdf8",width=2)
            d.text((cx+15,382),tag,font=f(8),fill="#8a9bb5",anchor="mm")
    else:
        d.polygon([(x0+120,330),(x0+160,322),(x0+190,330),(x0+190,370),(x0+155,395),(x0+120,370)],outline="#38bdf8",width=2)
        d.line([(x0+135,360),(x0+150,372)],fill="#4ade80",width=3)
        d.line([(x0+150,372),(x0+175,345)],fill="#4ade80",width=3)
        d.rectangle([(x0+200,330),(x0+250,395)],outline="#4ade80",width=2)
    d.text((x0+176,435),t,font=f(16,True),fill="white",anchor="mm")
    d.rounded_rectangle([(x0+15,510),(x0+338,545)],radius=8,fill="#1a3355")
    d.text((x0+176,527),btn+" ->",font=f(11),fill="#7fb3ff",anchor="mm")
# how it works with arrows
d.rounded_rectangle([(245,577),(W-12,H-12)],radius=14,fill="#132442",outline="#1e3a5f")
d.text((270,600),"How it works",font=f(14,True),fill="white",anchor="lm")
d.text((270,622),"Detection -> tracking -> face + appearance match -> report.",font=f(10),fill="#8a9bb5",anchor="lm")
steps=["Target","Detect","Track","Match","Report"]
subs=["Reference photo","YOLOv11","ByteTrack","ArcFace+OSNet","GenAI summary"]
for i in range(5):
    x0=260+i*222
    d.rounded_rectangle([(x0,645),(x0+200,755)],radius=10,outline="#1e3a5f")
    d.text((x0+100,690),steps[i],font=f(12,True),fill="white",anchor="mm")
    d.text((x0+100,712),subs[i],font=f(9),fill="#8a9bb5",anchor="mm")
    if i<4:
        d.text((x0+211,700),"->",font=f(12,True),fill="#2f80ed",anchor="mm")
img.save(out)
print("saved "+out+" matches="+str(n))
