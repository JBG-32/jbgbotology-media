import json, subprocess, os, sys
from PIL import Image, ImageDraw, ImageFont
W,H,FPS=1080,1920,30
os.chdir('/tmp/claude-0/intro')
REPO='/home/claude/jbgbotology-media/pipeline'
FD=REPO+'/fonts/'; SFX=REPO+'/promos/sfx/'
FB=FD+'space-grotesk-latin-700-normal.woff'; FMD=FD+'space-grotesk-latin-500-normal.woff'; FMO=FD+'ibm-plex-mono-latin-500-normal.woff'
CHALK=(237,230,214); GOLD=(245,185,66); CYAN=(63,224,255); INK=(5,6,10)
f=lambda p,s: ImageFont.truetype(p,s)
F_PILL=f(FMO,30); F_BRAND=f(FMO,27); F_STRIP=f(FMO,26); F_CAP=f(FB,70); F_E1=f(FB,96); F_E2=f(FMO,36); F_E3=f(FMD,44); F_TAG=f(FMO,30)
WORDS=json.load(open('words.json'))
def run(c): subprocess.run(c,check=True)
def dur(p): return float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',p],capture_output=True,text=True).stdout)
VF=f"fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1"

def seg(src,ss,d,out,fx=''):
    cd=dur(src); slow=max(1.0,(ss+d)/cd) if ss==0 else 1.0
    vf=f"setpts={slow:.3f}*PTS,{VF}"
    if fx=='glitch': vf+=",rgbashift=rh=-22:bh=22:gv=6,noise=alls=50:allf=t,eq=contrast=1.4:brightness=0.05"
    if fx=='zoom': vf+=",zoompan=z='1+0.0015*on':d=1:s=1080x1920:fps=30"
    vf+=f",tpad=stop_mode=clone:stop_duration=5,trim=0:{d},setpts=PTS-STARTPTS,format=yuv420p"
    run(['ffmpeg','-v','error','-y','-ss',str(ss),'-i',src,'-vf',vf,'-an','-c:v','libx264','-crf','16','-preset','fast',out])
    return out

def color(c,d,out):
    run(['ffmpeg','-v','error','-y','-f','lavfi','-i',f'color=c={c}:s={W}x{H}:r={FPS}','-t',str(d),'-vf','format=yuv420p','-c:v','libx264','-crf','16',out]); return out

def concat(parts,out):
    with open('build/cc.txt','w') as fh:
        for p in parts: fh.write(f"file '{os.path.abspath(p)}'\n")
    run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i','build/cc.txt','-c','copy',out]); return out

def ease(t,a,d=0.3): return max(0,min(1,(t-a)/d))
def center(d,y,t,fnt,col,stroke=0):
    w=d.textlength(t,font=fnt); d.text(((W-w)/2,y),t,font=fnt,fill=col,stroke_width=stroke,stroke_fill=INK+(230,))

def pill(d,part):
    t='AI-GENERATED  ·  LOLA IS AN AI'
    tw=d.textlength(t,font=F_PILL); x,y=54,118
    d.rounded_rectangle((x,y,x+tw+78,y+60),radius=30,fill=INK+(185,),outline=CYAN+(230,),width=2)
    d.ellipse((x+22,y+21,x+40,y+39),fill=CYAN+(255,))
    d.text((x+54,y+13),t,font=F_PILL,fill=CYAN+(255,))
    b='JBGBotology'; bw=d.textlength(b,font=F_BRAND); d.text((W-54-bw,y+13),b,font=F_BRAND,fill=CHALK+(220,))
    s=f'LOLA  ·  BREAKING THROUGH  ·  PART {part}/4'
    sw=d.textlength(s,font=F_STRIP); d.rectangle((54,200,54+sw+28,244),fill=INK+(160,)); d.text((68,207),s,font=F_STRIP,fill=GOLD+(235,))

def chunks(words,n=3):
    out=[];cur=[]
    for w in words:
        cur.append(w)
        if len(cur)==n or w['text'].endswith(('.','?',',','…')): out.append(cur);cur=[]
    if cur: out.append(cur)
    return out

def caption(d,words,t,off,y=1500):
    for c in chunks(words):
        a=c[0]['start']+off; b=c[-1]['end']+off+0.15
        if a<=t<b:
            toks=[w['text'].upper() for w in c]; sp=d.textlength(' ',font=F_CAP)
            widths=[d.textlength(x,font=F_CAP) for x in toks]; x=(W-(sum(widths)+sp*(len(toks)-1)))/2
            for w,tok,wd in zip(c,toks,widths):
                col=GOLD if w['start']+off<=t<w['end']+off+0.25 else CHALK
                d.text((x,y),tok,font=F_CAP,fill=col+(255,),stroke_width=6,stroke_fill=INK+(235,)); x+=wd+sp
            return

def tag(d,t,t0,line):
    k=ease(t,t0,0.4); al=int(255*k)
    center(d,1700,line,F_TAG,CYAN+(al,),3)

def endcard(img,t,t0):
    k=ease(t,t0,0.35); ov=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    d.rectangle((0,0,W,H),fill=INK+(int(170*k),)); al=int(255*k)
    center(d,720,'COULD A STARGATE',F_E1,CHALK+(al,),4)
    center(d,830,'BE REAL?',F_E1,GOLD+(al,),4)
    center(d,990,'EPISODE 1  ·  SUN OCT 25  ·  12 PM CT',F_E2,CYAN+(al,))
    center(d,1060,'Narrated by Lola, an AI',F_E3,CHALK+(int(al*0.85),))
    img.alpha_composite(ov)

def render(name,bv,T,draw):
    n=int(round(T*FPS))
    p=subprocess.Popen(['ffmpeg','-v','error','-y','-i',bv,'-f','rawvideo','-pix_fmt','rgba','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
        '-filter_complex','[0:v][1:v]overlay=0:0:format=auto,format=yuv420p','-frames:v',str(n),'-an','-c:v','libx264','-crf','17','-preset','medium',f'build/{name}_v.mp4'],stdin=subprocess.PIPE)
    for i in range(n):
        t=i/FPS; img=Image.new('RGBA',(W,H),(0,0,0,0)); draw(img,ImageDraw.Draw(img),t); p.stdin.write(img.tobytes())
    p.stdin.close(); p.wait()

def mix(name,T,vo,vo_off,beds,sfx):
    """beds: list of (file, start_in_timeline, volume) video-ambience or audio beds"""
    ins=['-i',vo]; fl=[f"[0:a]adelay={int(vo_off*1000)}|{int(vo_off*1000)},volume=1.0[a0]"]; labs=['[a0]']; k=1
    for fn,at,vol in beds+[(SFX+s+'.mp3',a,v) for s,a,v in sfx]:
        ins+=['-i',fn]; ms=int(at*1000); fl.append(f"[{k}:a]aresample=48000,adelay={ms}|{ms},volume={vol}[a{k}]"); labs.append(f'[a{k}]'); k+=1
    fl.append(''.join(labs)+f"amix=inputs={len(labs)}:normalize=0,apad,atrim=0:{T},afade=t=out:st={T-0.4}:d=0.4,loudnorm=I=-14:TP=-1.5[out]")
    run(['ffmpeg','-v','error','-y',*ins,'-filter_complex',';'.join(fl),'-map','[out]','-ar','48000','-c:a','aac','-b:a','192k',f'build/{name}_a.m4a'])
    run(['ffmpeg','-v','error','-y','-i',f'build/{name}_v.mp4','-i',f'build/{name}_a.m4a','-c:v','libx264','-crf','20','-maxrate','10M','-bufsize','20M','-preset','slow','-c:a','copy','-shortest','-movflags','+faststart',f'out/{name}.mp4'])
    print('done',name,round(dur(f'out/{name}.mp4'),2))

def amb(clip,at):  # Flow clip ambience bed
    return (clip,at,0.22)

C=lambda n:f'clips/{n}.mp4'
OFF=0.3

def p1():
    T=10.6
    cuts=[('L1a',0,3.2,''),('L1b',0,2.5,''),('L1c',0,2.6,''),('L1d',0,2.3,'')]
    parts=[seg(C(s),ss,d,f'build/p1_{i}.mp4',fx) for i,(s,ss,d,fx) in enumerate(cuts)]
    b=concat(parts,'build/p1_base.mp4')
    def dr(img,d,t):
        pill(d,1); caption(d,WORDS['1'],t,OFF)
        if t>9.6: tag(d,t,9.6,'TO BE CONTINUED  ·  PART 2 NEXT')
    render('Lola_Intro_1_Signal',b,T,dr)
    mix('Lola_Intro_1_Signal',T,'n1.mp3',OFF,[amb(C('L1a'),0),amb(C('L1c'),5.7)],[('drone',0,0.35),('glitch',5.7,0.5)])

def p2():
    T=10.4
    cuts=[('L2a',0,2.9,''),('L2b',0,2.5,''),('L2c',0,2.6,''),('L2d',0,2.4,'')]
    parts=[seg(C(s),ss,d,f'build/p2_{i}.mp4',fx) for i,(s,ss,d,fx) in enumerate(cuts)]
    b=concat(parts,'build/p2_base.mp4')
    def dr(img,d,t):
        pill(d,2); caption(d,WORDS['2'],t,OFF)
        if t>9.5: tag(d,t,9.5,'TO BE CONTINUED  ·  PART 3 NEXT')
    render('Lola_Intro_2_Touch',b,T,dr)
    mix('Lola_Intro_2_Touch',T,'n2.mp3',OFF,[amb(C('L2b'),0),amb(C('L2c'),5.4)],[('drone',0,0.3)])

def p3():
    T=11.9
    cuts=[('L3a',0,4.3,''),('L3a',2.0,0.2,'glitch'),('G1',0,1.7,''),('G2',0,0.2,'glitch'),('G2',0.2,1.9,''),('L3a',3.0,0.25,'glitch'),('L3c',0,3.35,'')]
    parts=[seg(C(s),ss,d,f'build/p3_{i}.mp4',fx) for i,(s,ss,d,fx) in enumerate(cuts)]
    b=concat(parts,'build/p3_base.mp4')
    def dr(img,d,t):
        pill(d,3); caption(d,WORDS['3'],t,OFF)
        if t>11.0: tag(d,t,11.0,'TO BE CONTINUED  ·  PART 4 NEXT')
    render('Lola_Intro_3_Reflection',b,T,dr)
    mix('Lola_Intro_3_Reflection',T,'n3.mp3',OFF,[amb(C('L3c'),8.0)],[('drone',0,0.35),('glitch',4.3,0.7),('glitch',6.2,0.6),('glitch',8.4,0.6)])

def p4():
    E=9.85; T=E+2.6
    cuts=[('L4a',0,3.0,''),('L4b',0,2.4,''),('L4c',0,2.1,''),('G3',0,2.15,'')]
    parts=[seg(C(s),ss,d,f'build/p4_{i}.mp4',fx) for i,(s,ss,d,fx) in enumerate(cuts)]
    parts.append(color('white',0.12,'build/p4_w.mp4'))
    parts.append(seg(C('L4b'),2.0,T-E-0.12+0.1,'build/p4_end.mp4',''))
    b=concat(parts,'build/p4_base.mp4')
    def dr(img,d,t):
        if t<E: pill(d,4); caption(d,WORDS['4'],t,OFF)
        else: endcard(img,t,E); pill(ImageDraw.Draw(img),4)
    render('Lola_Intro_4_Heartbeat',b,T,dr)
    mix('Lola_Intro_4_Heartbeat',T,'n4.mp3',OFF,[('heartbeat.wav',0,0.55)],[('boom',E,0.9),('drone',E,0.4)])

for k in (sys.argv[1:] or ['p1','p2','p3','p4']): globals()[k]()
