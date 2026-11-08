import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance
src, outdir = sys.argv[1], sys.argv[2]
F="/usr/share/fonts/opentype/inter/"
fnt=lambda n,s: ImageFont.truetype(F+n,s)
SAF,WHT,GRN,NAVY=(255,153,51),(255,255,255),(19,136,8),(0,0,128)
base=Image.open(src).convert("RGB")
base=ImageEnhance.Contrast(ImageEnhance.Color(base).enhance(1.15)).enhance(1.06)

def glass(img, box, r, tint=0.2):
    m=Image.new("L",img.size,0); ImageDraw.Draw(m).rounded_rectangle(box,r,fill=255)
    sh=Image.new("RGBA",img.size,(0,0,0,0)); ImageDraw.Draw(sh).rounded_rectangle((box[0],box[1]+10,box[2],box[3]+14),r,fill=(0,0,0,90))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
    g=Image.blend(img.convert("RGB").filter(ImageFilter.GaussianBlur(30)),Image.new("RGB",img.size,(255,255,255)),tint)
    img.paste(g,(0,0),m)
    ImageDraw.Draw(img).rounded_rectangle(box,r,outline=(255,255,255,140),width=2)

def flagbar(d,x,y,w,h):
    for k,c in enumerate((SAF,WHT,GRN)): d.rectangle((x+w*k/3,y,x+w*(k+1)/3,y+h),fill=c)

def stroke_text(d,xy,t,f,fill,anchor="la"):
    d.text(xy,t,font=f,fill=fill,anchor=anchor,stroke_width=max(2,f.size//22),stroke_fill=(0,0,0,150))

def gradient(size, top, bottom):
    W,H=size; g=Image.new("RGBA",size,(0,0,0,0)); d=ImageDraw.Draw(g)
    for y in range(H):
        a=int(top*(1-y/H)**2.2 + bottom*(y/H)**2.2); d.line((0,y,W,y),fill=(0,0,0,a))
    return g

# ---------- 9:16 (1080x1920) ----------
W,H=1080,1920
v=base.resize((W,H),Image.LANCZOS).filter(ImageFilter.UnsharpMask(2,80,2)).convert("RGBA")
v.alpha_composite(gradient((W,H),150,230))
glass(v,(60,90,470,170),40)
d=ImageDraw.Draw(v); flagbar(d,95,118,60,24)
d.text((180,130),"15 AUGUST",font=fnt("Inter-Bold.otf",40),fill=WHT,anchor="lm")
glass(v,(50,1440,W-50,1840),56,0.16)
d=ImageDraw.Draw(v)
d.text((100,1490),"FANCY DRESS COMPETITION",font=fnt("Inter-SemiBold.otf",36),fill=(255,255,255,230))
stroke_text(d,(96,1550),"INDEPENDENCE",fnt("Inter-Black.otf",110),SAF)
stroke_text(d,(96,1670),"DAY",fnt("Inter-Black.otf",110),WHT)
bx=96+d.textlength("DAY ",font=fnt("Inter-Black.otf",110))
d.ellipse((bx,1700,bx+70,1770),outline=NAVY,width=8,fill=WHT)  # chakra-style dot
for a in range(0,360,15):
    import math; cx,cy=bx+35,1735
    d.line((cx,cy,cx+30*math.cos(math.radians(a)),cy+30*math.sin(math.radians(a))),fill=NAVY,width=2)
flagbar(d,96,1800,300,10)
v.convert("RGB").save(outdir+"/thumbnail_9x16.jpg",quality=93)

# ---------- 16:9 (1280x720) ----------
W,H=1280,720
bg=base.resize((W,int(W*850/478)),Image.LANCZOS).crop((0,300,W,300+H)).filter(ImageFilter.GaussianBlur(28))
bg=ImageEnhance.Brightness(bg).enhance(0.6).convert("RGBA")
fg=base.resize((int(720*478/850),720),Image.LANCZOS).filter(ImageFilter.UnsharpMask(2,80,2))
fx=W-fg.width-60
sh=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(sh).rectangle((fx-6,0,fx+fg.width+6,H),fill=(0,0,0,140))
bg.alpha_composite(sh.filter(ImageFilter.GaussianBlur(20))); bg.paste(fg,(fx,0))
glass(bg,(50,150,fx-40,580),40,0.14)
d=ImageDraw.Draw(bg)
flagbar(d,90,195,90,26)
d.text((200,208),"15 AUGUST",font=fnt("Inter-Bold.otf",34),fill=WHT,anchor="lm")
stroke_text(d,(86,265),"INDEPENDENCE",fnt("Inter-Black.otf",78),SAF)
stroke_text(d,(86,355),"DAY",fnt("Inter-Black.otf",78),WHT)
d.text((90,480),"Fancy Dress Competition",font=fnt("Inter-SemiBold.otf",40),fill=(255,255,255,235))
flagbar(d,90,540,240,8)
bg.convert("RGB").save(outdir+"/thumbnail_16x9.jpg",quality=93)
