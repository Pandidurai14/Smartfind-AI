from PIL import Image, ImageDraw, ImageFont
import os
W,H = 1200,750
out_dir = r"C:\Users\epand\Downloads\kaggriculture\ui_preview"
os.makedirs(out_dir, exist_ok=True)

def get_font(size, bold=False):
    # try arial, fallback default
    try:
        name = "arialbd.ttf" if bold else "arial.ttf"
        return ImageFont.truetype(name, size)
    except:
        return ImageFont.load_default()

def rounded_rect(d, xy, r, fill):
    d.rounded_rectangle(xy, radius=r, fill=fill)

# 1. HOME
img = Image.new("RGB",(W,H),"#242424")
d = ImageDraw.Draw(img)
d.text((W//2,180),"Home Dashboard", font=get_font(42,True), fill="white", anchor="mm")
for i,(txt,y) in enumerate([("Live Camera",320),("Video Search",410)]):
    rounded_rect(d, [(W//2-125,y-25),(W//2+125,y+25)], 10, "#1f538d")
    d.text((W//2,y),txt, font=get_font(20,True), fill="white", anchor="mm")
d.text((W//2,700),"SMARTFIND AI V4 - main.py + gui/main_window.py:HomeDashboard", font=get_font(14), fill="#888888", anchor="mm")
img.save(os.path.join(out_dir,"1_home_dashboard.png"))
print("saved home")

# 2. LIVE CAMERA
img2 = Image.new("RGB",(W,H),"#242424")
d2 = ImageDraw.Draw(img2)
# top bar
d2.rectangle([(10,10),(W-10,70)], fill="#2f2f2f")
rounded_rect(d2, [(20,22),(140,58)], 8, "#555555")
d2.text((80,40),"< Back", font=get_font(14,True), fill="white", anchor="mm")
d2.text((200,40),"Live Camera Search", font=get_font(22,True), fill="white", anchor="lm")
# left panel
d2.rectangle([(10,80),(860,740)], fill="#333333")
rounded_rect(d2, [(40,100),(240,140)], 8, "#1f538d")
d2.text((140,120),"Upload Target Image", font=get_font(13,True), fill="white", anchor="mm")
rounded_rect(d2, [(260,100),(390,140)], 8, "#e74c3c")
d2.text((325,120),"Stop Camera", font=get_font(13,True), fill="white", anchor="mm")
# video area
d2.rectangle([(40,160),(830,720)], fill="black")
d2.rectangle([(300,280),(570,550)], outline=(0,255,0), width=3)
d2.text((435,260),"ID:1 | MATCH 87.50%", font=get_font(14,True), fill=(0,255,0), anchor="mm")
d2.text((435,580),"[ LIVE VIDEO FEED 640x480 ]", font=get_font(14), fill="#777777", anchor="mm")
# right panel
# left panel end, right panel start
d2.rectangle([(870,80),(W-10,740)], fill="#2f2f2f")
d2.text((1030,120),"Live Similarity", font=get_font(16), fill="white", anchor="mm")
d2.text((1030,165),"87.50%", font=get_font(44,True), fill="#2ecc71", anchor="mm")
d2.text((1030,230),"Match Graph", font=get_font(14), fill="white", anchor="mm")
d2.rectangle([(890,250),(1170,350)], fill="#1e1e1e")
# fake graph line
pts=[(890+i*14,320-((i*13)%60)) for i in range(20)]
d2.line(pts, fill="#2ecc71", width=2)
d2.text((1030,390),"Enhanced Match Capture", font=get_font(14), fill="white", anchor="mm")
d2.rectangle([(955,410),(1105,560)], fill="#333333")
d2.text((1030,485),"> photo", font=get_font(30), fill="white", anchor="mm")
d2.text((1030,600),"Green = Match  |  Orange = Hidden | Red = No Match", font=get_font(11), fill="#aaaaaa", anchor="mm")
img2.save(os.path.join(out_dir,"2_live_camera.png"))
print("saved live")

# 3. VIDEO SEARCH (variant)
img3 = img2.copy()
d3 = ImageDraw.Draw(img3)
d3.rectangle([(10,10),(W-10,70)], fill="#2f2f2f")
d3.text((200,40),"Video File Search", font=get_font(22,True), fill="white", anchor="lm")
d3.rectangle([(40,100),(830,145)], fill="#333333")
for txt,x in [("1. Target Image",140),("2. Select Video",340),("Stop Video",530)]:
    col="#1f538d" if "Stop" not in txt else "#e74c3c"
    rounded_rect(d3, [(x-70,105),(x+70,138)], 8, col)
    d3.text((x,121),txt, font=get_font(12,True), fill="white", anchor="mm")
img3.save(os.path.join(out_dir,"3_video_search.png"))
print("saved video")
