import json, subprocess, os, math, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H,FPS=1080,1920,30
os.chdir('/tmp/claude-0/lola')
FD='/tmp/claude-0/ep1/fonts/fontsource-space-grotesk-5.3.0/files/'
FM='/tmp/claude-0/ep1/fonts/fontsource-ibm-plex-mono-5.3.0/files/'
FB=FD+'space-grotesk-latin-700-normal.woff'; FMD=FD+'space-grotesk-latin-500-normal.woff'; FMO=FM+'ibm-plex-mono-latin-500-normal.woff'
CHALK=(237,230,214); GOLD=(245,185,66); CYAN=(63,224,255); EMBER=(255,74,46); VIOLET=(123,92,255)
f=lambda p,s: ImageFont.truetype(p,s)
F_PILL=f(FMO,30); F_BRAND=f(FMO,27); F_CAP=f(FB,70); F_E1=f(FB,100); F_E2=f(FMO,40); F_E3=f(FMD,40); F_NUM=f(FB,420); F_NUMLBL=f(FB,96)
WORDS=json.load(open('words.json'))
def run(c): subprocess.run(c,check=True)
def dur(p): return float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',p],capture_output=True,text=True).stdout)
VF=f"fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,format=yuv420p"
def enc(args,out): run(['ffmpeg','-v','error','-y',*args,'-an','-c:v','libx264','-crf','16','-preset','medium',out])

# ---------- shared orb plate (animated countdown keyframe) ----------
def orb_plate():
    out='build/orb.mp4'
    if os.path.exists(out): return out
    n=8*FPS
    enc(['-loop','1','-i','k4a.png','-vf',
         f"scale=2160:3840,zoompan=z='1.0+0.10*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS},"
         "eq=brightness='0.035*sin(2*PI*t*1.1)':saturation=1.05:eval=frame,noise=alls=6:allf=t,format=yuv420p",
         '-frames:v',str(n)],out)
    return out

def glitch(src,ss,d,out):
    enc(['-ss',str(ss),'-i',src,'-vf',VF+",rgbashift=rh=-22:bh=22:gv=6,noise=alls=55:allf=t,eq=contrast=1.5:brightness=0.06,"
         "crop=iw:ih*0.92:0:'ih*0.04*mod(n,3)',scale=1080:1920",'-t',str(d)],out)

# ---------- overlay drawing ----------
def pill(d):
    t='AI-GENERATED  ·  LOLA IS AN AI'
    tw=d.textlength(t,font=F_PILL); x,y=54,118
    d.rounded_rectangle((x,y,x+tw+78,y+60),radius=30,fill=(5,6,10,185),outline=CYAN+(230,),width=2)
    d.ellipse((x+22,y+21,x+40,y+39),fill=CYAN+(255,))
    d.text((x+54,y+13),t,font=F_PILL,fill=CYAN+(255,))
    b='JBGBotology'; bw=d.textlength(b,font=F_BRAND)
    d.text((W-54-bw,y+13),b,font=F_BRAND,fill=CHALK+(220,))

def chunks(words,n=3):
    out=[];cur=[]
    for w in words:
        cur.append(w)
        if len(cur)==n or w['text'].endswith(('.','?',',','—','...')):
            out.append(cur);cur=[]
    if cur: out.append(cur)
    return out

def caption(d,words,t,off,y):
    for c in chunks(words):
        a=c[0]['start']+off; b=c[-1]['end']+off+0.12
        if a<=t<b:
            toks=[w['text'].upper() for w in c]
            sp=d.textlength(' ',font=F_CAP)
            widths=[d.textlength(x,font=F_CAP) for x in toks]
            tot=sum(widths)+sp*(len(toks)-1); x=(W-tot)/2
            for w,tok,wd in zip(c,toks,widths):
                act=(w['start']+off)<=t
                col=GOLD if act and t<(w['end']+off+0.25) else CHALK
                d.text((x,y),tok,font=F_CAP,fill=col+(255,),stroke_width=6,stroke_fill=(5,6,10,235))
                x+=wd+sp
            return

def center(d,y,t,fnt,col,stroke=0,track=0):
    if track:
        w=sum(d.textlength(c,font=fnt) for c in t)+track*(len(t)-1); x=(W-w)/2
        for c in t:
            d.text((x,y),c,font=fnt,fill=col,stroke_width=stroke,stroke_fill=(5,6,10,230)); x+=d.textlength(c,font=fnt)+track
    else:
        w=d.textlength(t,font=fnt); d.text(((W-w)/2,y),t,font=fnt,fill=col,stroke_width=stroke,stroke_fill=(5,6,10,230))

def endcard(img,t,t0):
    k=min(1,(t-t0)/0.35)
    ov=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    for i in range(700):  # bottom gradient
        a=int(210*k*(i/700)**1.3); d.line([(0,H-700+i),(W,H-700+i)],fill=(5,6,10,a))
    al=int(255*k)
    center(d,1290,'COULD A STARGATE',F_E1,CHALK+(al,),4)
    center(d,1400,'BE REAL?',F_E1,GOLD+(al,),4)
    center(d,1545,'EPISODE 1  ·  SUNDAY 12 PM CT',F_E2,CYAN+(al,),0,2)
    center(d,1625,'Follow JBGBotology',F_E3,CHALK+(int(al*0.9),))
    img.alpha_composite(ov)

def countdown_num(d,t,t0,num,lbl):
    if t<t0: return
    k=min(1,(t-t0)/0.25); s=1+0.25*(1-k)
    fnt=f(FB,int(420*s)) if num else None
    al=int(255*k)
    if num:
        center(d,1080-int(60*(s-1)*4),num,fnt,GOLD+(al,),8)
        center(d,1520,lbl,F_NUMLBL,CHALK+(al,),5)
    else:
        center(d,1250,lbl,f(FB,int(150*s)),GOLD+(al,),7)

def render(name,base,total,draw):
    n=int(round(total*FPS))
    p=subprocess.Popen(['ffmpeg','-v','error','-y','-i',base,'-f','rawvideo','-pix_fmt','rgba','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
        '-filter_complex','[0:v][1:v]overlay=0:0:format=auto,format=yuv420p','-frames:v',str(n),'-an','-c:v','libx264','-crf','17','-preset','medium',f'build/{name}_v.mp4'],stdin=subprocess.PIPE)
    for i in range(n):
        t=i/FPS; img=Image.new('RGBA',(W,H),(0,0,0,0)); draw(img,ImageDraw.Draw(img),t)
        p.stdin.write(img.tobytes())
    p.stdin.close(); p.wait()

def mix(name,total,vo,vo_off,sfx):
    ins=['-i',vo]; fl=[f"[0:a]adelay={int(vo_off*1000)}|{int(vo_off*1000)},volume=1.0[a0]"]; labs=['[a0]']
    for i,(fn,at,vol) in enumerate(sfx,1):
        ins+=['-i',f'sfx/{fn}.mp3']; fl.append(f"[{i}:a]adelay={int(at*1000)}|{int(at*1000)},volume={vol}[a{i}]"); labs.append(f'[a{i}]')
    fl.append(''.join(labs)+f"amix=inputs={len(labs)}:normalize=0,atrim=0:{total},afade=t=out:st={total-0.3}:d=0.3,loudnorm=I=-14:TP=-1.5[out]")
    run(['ffmpeg','-v','error','-y',*ins,'-filter_complex',';'.join(fl),'-map','[out]','-ar','48000','-c:a','aac','-b:a','192k',f'build/{name}_a.m4a'])
    run(['ffmpeg','-v','error','-y','-i',f'build/{name}_v.mp4','-i',f'build/{name}_a.m4a','-c:v','copy','-c:a','copy','-shortest',f'out/{name}.mp4'])
    print('done',name,dur(f'out/{name}.mp4'))

def concat(parts,out):
    with open('build/cc.txt','w') as fh:
        for p in parts: fh.write(f"file '{os.path.abspath(p)}'\n")
    run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i','build/cc.txt','-c','copy',out])

os.makedirs('out',exist_ok=True)
orb=orb_plate()

# ---------- P1: Don't turn around ----------
def p1():
    enc(['-i','p1_talk.mp4','-vf',VF,'-t','5.30'],'build/p1a.mp4')
    glitch('p1_talk.mp4',5.0,0.35,'build/p1g.mp4')
    enc(['-i',orb,'-vf',VF,'-t','1.75'],'build/p1o.mp4')
    concat(['build/p1a.mp4','build/p1g.mp4','build/p1o.mp4'],'build/p1_base.mp4')
    T=5.30+0.35+1.75
    def dr(img,d,t):
        if t<5.65: pill(d); caption(d,WORDS['p1'],t,0,1500)
        else:
            endcard(img,t,5.65); pill(ImageDraw.Draw(img))
    render('P1_dont_turn_around','build/p1_base.mp4',T,dr)
    mix('P1_dont_turn_around',T,'v1a.mp3',0,[('ignite',3.6,0.8),('glitch',5.25,0.9),('boom',5.65,0.9),('drone',5.65,0.45)])

# ---------- P2: The eye ----------
def p2():
    enc(['-i','p2_eye.mp4','-vf',VF+',trim=0:0.04,setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration=0.9','-t','0.9'],'build/p2h.mp4')
    enc(['-i','p2_eye.mp4','-vf',VF,'-t','2.0'],'build/p2a.mp4')
    enc(['-ss','2.0','-i','p2_eye.mp4','-vf','setpts=PTS/2,'+VF,'-t','0.875'],'build/p2b.mp4')
    enc(['-ss','3.75','-i','p2_eye.mp4','-vf',VF,'-t','2.25'],'build/p2c.mp4')
    enc(['-i',orb,'-vf',VF,'-t','1.6'],'build/p2o.mp4')
    concat(['build/p2h.mp4','build/p2a.mp4','build/p2b.mp4','build/p2c.mp4','build/p2o.mp4'],'build/p2_base.mp4')
    T=0.9+2.0+0.875+2.25+1.6; e=T-1.6
    def dr(img,d,t):
        if t<e: pill(d); caption(d,WORDS['p2'],t,0,1500)
        else: endcard(img,t,e); pill(ImageDraw.Draw(img))
    render('P2_the_eye','build/p2_base.mp4',T,dr)
    mix('P2_the_eye',T,'v2a.mp3',0,[('drone',0,0.35),('glitch',e-0.1,0.6),('boom',e,0.9)])

# ---------- P3: The glitch ----------
def p3():
    enc(['-i','p3_talk.mp4','-vf',VF,'-t','4.15'],'build/p3a.mp4')
    glitch('p3_talk.mp4',4.0,0.40,'build/p3g.mp4')
    enc(['-f','lavfi','-i','color=c=0x05060A:s=1080x1920:r=30','-vf','format=yuv420p','-t','0.25'],'build/p3k.mp4')
    enc(['-i',orb,'-vf',VF,'-t','1.6'],'build/p3o.mp4')
    concat(['build/p3a.mp4','build/p3g.mp4','build/p3k.mp4','build/p3o.mp4'],'build/p3_base.mp4')
    T=4.15+0.40+0.25+1.6; e=4.8
    def dr(img,d,t):
        if t<4.55: pill(d); caption(d,WORDS['p3'],t,0,1500)
        elif t<e: pill(d)
        else: endcard(img,t,e); pill(ImageDraw.Draw(img))
    render('P3_the_glitch','build/p3_base.mp4',T,dr)
    # cut VO at the glitch
    run(['ffmpeg','-v','error','-y','-i','v3a.mp3','-af','atrim=0:4.2,afade=t=out:st=4.12:d=0.08','build/v3cut.wav'])
    mix('P3_the_glitch',T,'build/v3cut.wav',0,[('glitch',4.12,1.0),('boom',4.8,0.9),('drone',4.8,0.4)])

# ---------- Countdowns ----------
def cd(key,vo,num,lbl,trig_word):
    w=[x for x in WORDS[key] if x['text'].lower().startswith(trig_word)][0]
    t0=w['start']
    T=6.0
    enc(['-i',orb,'-vf',VF,'-t',str(T)],f'build/{key}_base.mp4')
    def dr(img,d,t):
        pill(d)
        if t<4.9: caption(d,WORDS[key],t,0,1700)
        countdown_num(d,t,t0,num,lbl)
        if t>4.9:
            k=min(1,(t-4.9)/0.3); al=int(255*k)
            center(d,1700,'COULD A STARGATE BE REAL?',F_E2,CHALK+(al,),3,1)
            center(d,1765,'EPISODE 1  ·  SUN OCT 25  ·  12 PM CT',F_E2,CYAN+(al,),3,1)
    nm={'c3':'C3_three_days','c2':'C2_two_days','c1':'C1_tomorrow'}[key]
    render(nm,f'build/{key}_base.mp4',T,dr)
    mix(nm,T,vo,0,[('drone',0,0.4),('boom',t0,0.85)])

which=sys.argv[1:] or ['p1','p2','p3','c3','c2','c1']
if 'p1' in which: p1()
if 'p2' in which: p2()
if 'p3' in which: p3()
if 'c3' in which: cd('c3','c3a.mp3','3','DAYS','three')
if 'c2' in which: cd('c2','c2a.mp3','2','DAYS','two')
if 'c1' in which: cd('c1','c1a.mp3',None,'TOMORROW','tomorrow')
