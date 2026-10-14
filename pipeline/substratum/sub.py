import json, subprocess, os, sys
from PIL import Image, ImageDraw, ImageFont
W,H,FPS=1080,1920,30
WORK=os.environ.get('WORK','/tmp/claude-0/subpromo'); REPO=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(WORK); os.makedirs('build',exist_ok=True); os.makedirs('out',exist_ok=True)
FD=FM=os.path.join(REPO,'fonts')+'/'
FB=FD+'space-grotesk-latin-700-normal.woff'; FMD=FD+'space-grotesk-latin-500-normal.woff'; FMO=FM+'ibm-plex-mono-latin-500-normal.woff'
CHALK=(237,230,214); GOLD=(245,185,66); CYAN=(63,224,255); EMBER=(255,74,46); VIOLET=(155,132,255); INK=(5,6,10)
f=lambda p,s: ImageFont.truetype(p,s)
F_PILL=f(FMO,30); F_BRAND=f(FMO,27); F_STRIP=f(FMO,26); F_CAP=f(FB,70); F_E1=f(FB,112); F_E2=f(FMO,36); F_E3=f(FMD,44)
F_LBL=f(FMO,34); F_LBLB=f(FB,46); F_D=f(FB,64); F_STAMP=f(FB,120)
WORDS=json.load(open('words.json'))
SFX=os.path.join(REPO,'promos','sfx')+'/'
EQ_OLD=Image.open('eq_old.png'); EQ_NEW=Image.open('eq_new.png'); SKY=Image.open('skymap.png')
def run(c): subprocess.run(c,check=True)
def dur(p): return float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',p],capture_output=True,text=True).stdout)
VF=f"fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1"

def base(src,T,slow=1.0,out=None):
    """Scale to 1080x1920, optional slow-down, hold last frame to reach T, gentle drift."""
    out=out or f'build/{os.path.basename(src)}_base.mp4'
    vf=f"setpts={slow}*PTS,{VF},tpad=stop_mode=clone:stop_duration=10,trim=0:{T},format=yuv420p"
    run(['ffmpeg','-v','error','-y','-i',src,'-vf',vf,'-an','-c:v','libx264','-crf','16','-preset','medium',out]); return out

def ease(t,a,d=0.3): return max(0,min(1,(t-a)/d))

def center(d,y,t,fnt,col,stroke=0):
    w=d.textlength(t,font=fnt); d.text(((W-w)/2,y),t,font=fnt,fill=col,stroke_width=stroke,stroke_fill=INK+(230,))

def pill(d):
    t='AI-GENERATED  ·  LOLA IS AN AI'
    tw=d.textlength(t,font=F_PILL); x,y=54,118
    d.rounded_rectangle((x,y,x+tw+78,y+60),radius=30,fill=INK+(185,),outline=CYAN+(230,),width=2)
    d.ellipse((x+22,y+21,x+40,y+39),fill=CYAN+(255,))
    d.text((x+54,y+13),t,font=F_PILL,fill=CYAN+(255,))
    b='JBGBotology'; bw=d.textlength(b,font=F_BRAND); d.text((W-54-bw,y+13),b,font=F_BRAND,fill=CHALK+(220,))
    s='SUBSTRATUM THEORY  ·  A HYPOTHESIS BY JUAN HINOJOSA'
    sw=d.textlength(s,font=F_STRIP); d.rectangle((54,200,54+sw+28,244),fill=INK+(160,))
    d.text((68,207),s,font=F_STRIP,fill=GOLD+(235,))

def chunks(words,n=3):
    out=[];cur=[]
    for w in words:
        cur.append(w)
        if len(cur)==n or w['text'].endswith(('.','?',',','...')): out.append(cur);cur=[]
    if cur: out.append(cur)
    return out

def caption(d,words,t,y=1500):
    for c in chunks(words):
        a=c[0]['start']; b=c[-1]['end']+0.12
        if a<=t<b:
            toks=[w['text'].upper() for w in c]; sp=d.textlength(' ',font=F_CAP)
            widths=[d.textlength(x,font=F_CAP) for x in toks]; x=(W-(sum(widths)+sp*(len(toks)-1)))/2
            for w,tok,wd in zip(c,toks,widths):
                col=GOLD if w['start']<=t<w['end']+0.25 else CHALK
                d.text((x,y),tok,font=F_CAP,fill=col+(255,),stroke_width=6,stroke_fill=INK+(235,)); x+=wd+sp
            return

def endcard(img,t,t0):
    k=ease(t,t0,0.35); ov=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    d.rectangle((0,0,W,H),fill=INK+(int(150*k),))
    al=int(255*k)
    center(d,700,'CAN YOU',F_E1,CHALK+(al,),4)
    center(d,820,'BREAK IT?',F_E1,GOLD+(al,),4)
    center(d,1000,'Challenge it  ·  link in bio',F_E3,CHALK+(al,))
    center(d,1075,'jbg-32.github.io/substratum-theory',F_E2,CYAN+(al,))
    center(d,1240,'A hypothesis, not established science.',F_E2,CHALK+(int(al*0.75),))
    img.alpha_composite(ov)

def paste(img,src,cx,cy,alpha,scale=1.0):
    s=src if scale==1.0 else src.resize((int(src.width*scale),int(src.height*scale)),Image.LANCZOS)
    if alpha<1:
        s=s.copy(); a=s.getchannel('A').point(lambda v:int(v*alpha)); s.putalpha(a)
    img.alpha_composite(s,(int(cx-s.width/2),int(cy-s.height/2)))

def render(name,bv,T,draw):
    n=int(round(T*FPS))
    p=subprocess.Popen(['ffmpeg','-v','error','-y','-i',bv,'-f','rawvideo','-pix_fmt','rgba','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
        '-filter_complex','[0:v][1:v]overlay=0:0:format=auto,format=yuv420p','-frames:v',str(n),'-an','-c:v','libx264','-crf','17','-preset','medium',f'build/{name}_v.mp4'],stdin=subprocess.PIPE)
    for i in range(n):
        t=i/FPS; img=Image.new('RGBA',(W,H),(0,0,0,0)); draw(img,ImageDraw.Draw(img),t); p.stdin.write(img.tobytes())
    p.stdin.close(); p.wait()

def mix(name,T,vo,sfx):
    ins=['-i',vo]; fl=["[0:a]volume=1.0[a0]"]; labs=['[a0]']
    for i,(fn,at,vol) in enumerate(sfx,1):
        ins+=['-i',SFX+fn+'.mp3']; ms=int(at*1000); fl.append(f"[{i}:a]adelay={ms}|{ms},volume={vol}[a{i}]"); labs.append(f'[a{i}]')
    fl.append(''.join(labs)+f"amix=inputs={len(labs)}:normalize=0,apad,atrim=0:{T},afade=t=out:st={T-0.4}:d=0.4,loudnorm=I=-14:TP=-1.5[out]")
    run(['ffmpeg','-v','error','-y',*ins,'-filter_complex',';'.join(fl),'-map','[out]','-ar','48000','-c:a','aac','-b:a','192k',f'build/{name}_a.m4a'])
    run(['ffmpeg','-v','error','-y','-i',f'build/{name}_v.mp4','-i',f'build/{name}_a.m4a','-c:v','libx264','-crf','20','-maxrate','10M','-bufsize','20M','-preset','slow','-c:a','copy','-shortest','-movflags','+faststart',f'out/{name}.mp4'])
    print('done',name,round(dur(f'out/{name}.mp4'),2))

END=2.4
# ---- S1: break it ----
def s1():
    w=WORDS['1']; e=w[-1]['end']+0.35; T=e+END
    b=base('c1.mp4',T)
    def dr(img,d,t):
        if t<e: pill(d); caption(d,w,t)
        else: endcard(img,t,e); pill(ImageDraw.Draw(img))
    render('S1_break_it',b,T,dr)
    mix('S1_break_it',T,'v1.mp3',[('drone',0,0.3),('glitch',e-0.1,0.6),('boom',e,0.85)])

# ---- S2: twelve dimensions ----
def s2():
    w=WORDS['2']; e=w[-1]['end']+0.45; T=e+END
    b=base('c2.mp4',T,slow=1.08)
    def dr(img,d,t):
        if t<e:
            pill(d); caption(d,w,t)
            # D1-D12 ticker as the orb dives: D1-4 by "four", D5-12 by "twelve"
            for i in range(12):
                a=2.96+i*0.08 if i<4 else 4.3+(i-4)*0.15
                k=ease(t,a,0.2)
                if k<=0: continue
                col=(GOLD if i<4 else VIOLET)+(int(255*k),)
                x=120+(i%6)*150; y=1100+(i//6)*90
                d.text((x,y),f'D{i+1}',font=F_D,fill=col,stroke_width=4,stroke_fill=INK+(220,))
            if t>3.2: center(d,1010,'D1-D4  WHAT YOU SEE',F_LBL,GOLD+(int(255*ease(t,3.2)),),3)
            if t>5.5: center(d,1290,'D5-D12  OUR HYPOTHESIS',F_LBL,VIOLET+(int(255*ease(t,5.5)),),3)
        else: endcard(img,t,e); pill(ImageDraw.Draw(img))
    render('S2_twelve_dimensions',b,T,dr)
    mix('S2_twelve_dimensions',T,'v2.mp3',[('drone',0,0.4),('ignite',4.3,0.6),('boom',e,0.85)])

# ---- S3: we deleted it ----
def s3():
    w=WORDS['3']; e=w[-1]['end']+0.6; T=e+END
    b=base('c3.mp4',T,slow=1.9)
    def dr(img,d,t):
        if t<e:
            pk=ease(t,2.3)
            if pk>0:
                ov=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(ov).rounded_rectangle((50,640,W-50,940),radius=24,fill=INK+(int(200*pk),))
                img.alpha_composite(ov)
            pill(d); caption(d,w,t)
            if 2.3<=t<5.6:
                al=ease(t,2.3)*(1-ease(t,5.3,0.3))
                paste(img,EQ_OLD,W/2,760,al)
                if t>=3.68:
                    k=ease(t,3.68,0.25); x0,x1=90,90+int(900*k)
                    d.line((x0,760,x1,760),fill=EMBER+(int(255*al),),width=8)
                    center(d,870,'v2.1: REMOVED, indices don\'t match',F_LBL,EMBER+(int(255*al),),3)
            if t>=6.0:
                k=ease(t,6.0,0.35); paste(img,EQ_NEW,W/2,760,k,1.15)
                center(d,890,'v3.0: KEPT (standard Kaluza-Klein result)',F_LBL,CYAN+(int(255*k),),3)
        else: endcard(img,t,e); pill(ImageDraw.Draw(img))
    render('S3_we_deleted_it',b,T,dr)
    mix('S3_we_deleted_it',T,'v3.mp3',[('drone',0,0.3),('glitch',5.24,0.7),('ignite',6.0,0.5),('boom',e,0.85)])

# ---- S4: cosmic ray test ----
def s4():
    w=WORDS['4']; e=w[-1]['end']+0.45; T=e+END
    b=base('c4.mp4',T,slow=1.35)
    def dr(img,d,t):
        if t<e:
            pill(d); caption(d,w,t)
            if t>=3.44:
                k=ease(t,3.44,0.4); ov=Image.new('RGBA',(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
                od.rounded_rectangle((60,500,W-60,1180),radius=24,fill=INK+(int(170*k),))
                img.alpha_composite(ov); paste(img,SKY,W/2,800,k,1.08)
                center(d,530,'ILLUSTRATIVE: CUBIC (l=4) SKY PATTERN',F_LBL,CYAN+(int(255*k),))
                if t>=5.76:
                    k2=ease(t,5.76)
                    center(d,1060,'Real data (Auger 2017): a dipole,',F_LBL,CHALK+(int(255*k2),))
                    center(d,1105,'not this pattern. The test is open.',F_LBL,CHALK+(int(255*k2),))
        else: endcard(img,t,e); pill(ImageDraw.Draw(img))
    render('S4_cosmic_ray_test',b,T,dr)
    mix('S4_cosmic_ray_test',T,'v4.mp3',[('drone',0,0.4),('ignite',3.44,0.5),('boom',e,0.85)])

# ---- S5: antenna ----
def s5():
    w=WORDS['5']; e=w[-1]['end']+0.35; T=e+END
    b=base('c5.mp4',T)
    def dr(img,d,t):
        if t<e:
            pill(d); caption(d,w,t)
            if t>=5.72:
                k=ease(t,5.72,0.15); s=1+0.4*(1-k)
                st=Image.new('RGBA',(820,200),(0,0,0,0)); sd=ImageDraw.Draw(st)
                sd.rounded_rectangle((6,6,814,194),radius=18,outline=EMBER+(255,),width=10)
                fn=F_STAMP; tw=sd.textlength('SPECULATIVE',font=fn)
                if tw>760: fn=f(FB,int(120*760/tw)); tw=sd.textlength('SPECULATIVE',font=fn)
                sd.text(((820-tw)/2,28),'SPECULATIVE',font=fn,fill=EMBER+(255,))
                st=st.rotate(-8,expand=True,resample=Image.BICUBIC)
                paste(img,st,W/2,1330,k,s)
        else: endcard(img,t,e); pill(ImageDraw.Draw(img))
    render('S5_antenna',b,T,dr)
    mix('S5_antenna',T,'v5.mp3',[('drone',0,0.3),('boom',5.72,0.7),('glitch',e-0.1,0.5),('boom',e,0.8)])

for k in (sys.argv[1:] or ['s1','s2','s3','s4','s5']): globals()[k]()
