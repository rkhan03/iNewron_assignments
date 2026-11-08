import subprocess, sys, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
src, out = sys.argv[1], sys.argv[2]
W, H, FPS, DUR = 478, 850, 30, 102.93
N = int(DUR*FPS)
CH = [(0.0, "Warm-Up & Intro"), (28.77, "Batting Drills"), (57.15, "Coach's Tips")]
F = "/usr/share/fonts/opentype/inter/"
fb = lambda s: ImageFont.truetype(F+"Inter-SemiBold.otf", s)
fr = lambda s: ImageFont.truetype(F+"Inter-Medium.otf", s)
def mask(box, r):
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).rounded_rectangle(box, r, fill=255); return m
PILL = (16, 18, 196, 54); CARD = (16, H-138, W-16, H-18)
widgets = [(PILL, 18), (CARD, 22)]
masks = [mask(b, r) for b, r in widgets]
# shadow + border layers (static)
shadow = Image.new("RGBA", (W, H), (0,0,0,0)); sd = ImageDraw.Draw(shadow)
for b, r in widgets: sd.rounded_rectangle((b[0], b[1]+4, b[2], b[3]+6), r, fill=(0,0,0,70))
shadow = shadow.filter(ImageFilter.GaussianBlur(8))
border = Image.new("RGBA", (W, H), (0,0,0,0)); bd = ImageDraw.Draw(border)
for b, r in widgets:
    bd.rounded_rectangle(b, r, outline=(255,255,255,110), width=1)
    bd.line((b[0]+r, b[1]+1, b[2]-r, b[1]+1), fill=(255,255,255,170))  # top highlight
def fmt(t): return f"{int(t)//60}:{int(t)%60:02d}"
dec = subprocess.Popen(["ffmpeg","-v","error","-i",src,"-f","rawvideo","-pix_fmt","rgb24","-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
    "-i",src,"-map","0:v","-map","1:a","-c:v","libx264","-crf","18","-preset","medium","-pix_fmt","yuv420p","-c:a","copy","-shortest","-movflags","+faststart",out], stdin=subprocess.PIPE)
tint = Image.new("RGB", (W, H), (255,255,255))
i = 0
while True:
    raw = dec.stdout.read(W*H*3)
    if len(raw) < W*H*3: break
    t = i/FPS; i += 1
    fr_img = Image.frombytes("RGB", (W, H), raw)
    blur = fr_img.filter(ImageFilter.GaussianBlur(14))
    glass = Image.blend(blur, tint, 0.18)
    img = Image.alpha_composite(fr_img.convert("RGBA"), shadow)
    for m in masks: img.paste(glass, (0,0), m)
    img = Image.alpha_composite(img, border)
    ci = max(k for k,(s,_) in enumerate(CH) if t >= s)
    a = min(1.0, (t-CH[ci][0])/0.5)  # text fade-in on chapter change
    ov = Image.new("RGBA", (W, H), (0,0,0,0)); d = ImageDraw.Draw(ov)
    A = lambda base: int(base*a)
    # pill: chapter counter + dots
    d.ellipse((30, 30, 42, 42), fill=(255,90,90,255))
    d.text((52, 36), f"CHAPTER {ci+1:02d} / {len(CH)}", font=fb(14), fill=(255,255,255,A(255)), anchor="lm")
    # card
    x0, y0, x1, y1 = CARD
    d.text((x0+20, y0+18), "CRICKET NETS SESSION", font=fr(11), fill=(255,255,255,190), anchor="lt")
    d.text((x0+20, y0+38), CH[ci][1], font=fb(26), fill=(255,255,255,A(255)), anchor="lt")
    # segmented progress bar
    bx0, bx1, by = x0+20, x1-20, y0+86
    gap = 6; segs = [s for s,_ in CH] + [DUR]
    total = bx1-bx0-gap*(len(CH)-1); x = bx0
    for k in range(len(CH)):
        w = total*(segs[k+1]-segs[k])/DUR
        d.rounded_rectangle((x, by, x+w, by+5), 3, fill=(255,255,255,70))
        p = min(1, max(0, (t-segs[k])/(segs[k+1]-segs[k])))
        if p > 0: d.rounded_rectangle((x, by, x+max(5, w*p), by+5), 3, fill=(255,255,255,235))
        x += w+gap
    d.text((bx0, by+12), fmt(t), font=fr(11), fill=(255,255,255,200), anchor="lt")
    d.text((bx1, by+12), fmt(DUR), font=fr(11), fill=(255,255,255,200), anchor="rt")
    img = Image.alpha_composite(img, ov).convert("RGB")
    enc.stdin.write(img.tobytes())
enc.stdin.close(); enc.wait(); print("frames", i)
