"""Builds the four Ep 2 / Ep 3 HyperFrames graphics (index.html per folder)."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))

HEAD = """<!doctype html>
<html lang="en" data-resolution="portrait">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
@font-face{font-family:SG;src:url(fonts/space-grotesk-latin-500-normal.woff2);font-weight:500}
@font-face{font-family:SG;src:url(fonts/space-grotesk-latin-700-normal.woff2);font-weight:700}
@font-face{font-family:PM;src:url(fonts/ibm-plex-mono-latin-500-normal.woff2);font-weight:500}
:root{--void:#05060A;--navy:#0B1426;--chalk:#EDE6D6;--gold:#F5B942;--cyan:#3FE0FF;--ember:#FF4A2E;--violet:#7B5CFF}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;overflow:hidden;background:var(--void)}
#root{position:relative;width:1080px;height:1920px;background:radial-gradient(ellipse at 50% 45%,#0B1426 0%,#05060A 70%);font-family:SG,sans-serif;color:var(--chalk)}
.star{position:absolute;border-radius:50%;background:#cfe8ff}
#badge{position:absolute;top:150px;left:50%;transform:translateX(-50%);font-family:PM;font-size:30px;letter-spacing:.18em;color:var(--cyan);border:2px solid rgba(63,224,255,.6);padding:12px 26px;border-radius:40px;background:rgba(5,6,10,.6);white-space:nowrap}
#title{position:absolute;top:240px;width:100%;text-align:center;font-weight:700;font-size:96px;letter-spacing:-.02em;line-height:1}
#title span{color:var(--ember)}
.lbl{font-family:PM;font-size:30px;letter-spacing:.14em;color:rgba(237,230,214,.75)}
.big{font-weight:700;font-size:56px;line-height:1.1}
svg{position:absolute;left:0;top:0}
%CSS%
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="%DUR%" data-width="1080" data-height="1920">
  <div id="stars"></div>
  <div id="badge">&#9679; REAL PHYSICS</div>
  <div id="title">%TITLE%</div>
%BODY%
</div>
<script>
let s=7;const r=()=>{s=(s*16807)%2147483647;return s/2147483647};
const st=document.getElementById('stars');
for(let i=0;i<140;i++){const d=document.createElement('div');d.className='star';const z=r()*2.6+0.8;Object.assign(d.style,{left:r()*1080+'px',top:r()*1920+'px',width:z+'px',height:z+'px',opacity:(0.25+r()*0.6).toFixed(2)});st.appendChild(d)}
const tl=gsap.timeline({paused:true});
tl.from('#stars',{opacity:0,duration:.5},0).from('#badge',{opacity:0,y:-20,duration:.4},0.05).from('#title',{opacity:0,y:30,duration:.5},0.15);
%JS%
window.__timelines=window.__timelines||{};window.__timelines['main']=tl;tl.seek(0);
</script>
</body>
</html>
"""

FUNNEL_JS = """
const N=13, rings={top:[],bot:[]};
for(const side of ['top','bot']){
  const host=document.getElementById(side);
  for(let i=0;i<N;i++){
    const t=i/(N-1), y=Math.pow(t,0.75)*360, w=%W0%+880*t*t, h=w*0.2;
    const e=document.createElement('div');e.className='ring';
    Object.assign(e.style,{width:w+'px',height:h+'px',left:(-w/2)+'px',top:((side==='top'?-y:y)-h/2)+'px',opacity:(1-0.45*t).toFixed(2)});
    host.appendChild(e);rings[side].push(e);
  }
}
['top','bot'].forEach(side=>rings[side].slice().reverse().forEach((e,j)=>tl.from(e,{opacity:0,scaleX:.6,scaleY:.6,duration:.4},0.1+j*0.035)));
"""
FUNNEL_CSS = """#hole{position:absolute;left:540px;top:%Y%px;width:0;height:0}
.half{position:absolute;left:0;top:0;width:0;height:0}
.ring{position:absolute;border:2.5px solid var(--cyan);border-radius:50%;box-shadow:0 0 14px rgba(63,224,255,.55),inset 0 0 10px rgba(63,224,255,.25)}"""

shots = {}

# ---------- E2S04: the throat (5.3 s) ----------
shots['E2S04'] = dict(dur=5.3, title='THE <span>THROAT</span>',
 css=FUNNEL_CSS.replace('%Y%','880') + """
#tag{position:absolute;left:640px;top:850px;display:flex;align-items:center;gap:18px}
#tag .line{width:150px;height:3px;background:var(--gold);box-shadow:0 0 12px rgba(245,185,66,.7)}
#tag .t{font-family:PM;font-size:44px;letter-spacing:.16em;color:var(--gold);text-shadow:0 0 18px rgba(245,185,66,.6)}
#glow{position:absolute;left:-70px;top:-22px;width:140px;height:44px;border-radius:50%;background:radial-gradient(ellipse,rgba(245,185,66,.75),rgba(245,185,66,0) 70%);opacity:0}
#mA,#mB{position:absolute;font-family:PM;font-size:28px;letter-spacing:.14em;color:rgba(63,224,255,.85);width:100%;text-align:center}
#mA{top:440px}#mB{top:1300px}
#panel{position:absolute;left:90px;right:90px;top:1420px}
#p2{margin-top:14px}""",
 body="""  <div id="mA">MOUTH A</div>
  <div id="hole"><div class="half" id="top"></div><div class="half" id="bot"></div><div id="glow"></div></div>
  <div id="mB">MOUTH B</div>
  <div id="tag"><div class="line"></div><div class="t">THROAT</div></div>
  <div id="panel"><div class="lbl" id="p1">THE NARROWEST POINT</div><div class="big" id="p2">Where the two ends of the tunnel meet.</div></div>""",
 js=FUNNEL_JS.replace('%W0%','70') + """
tl.from('#mA',{opacity:0,duration:.4},0.5).from('#mB',{opacity:0,duration:.4},0.6)
  .fromTo('#tag',{opacity:0,x:40},{opacity:1,x:0,duration:.5},1.1)
  .fromTo('#glow',{opacity:0},{opacity:1,duration:.4},1.1)
  .from('#p1',{opacity:0,x:-30,duration:.4},1.6).from('#p2',{opacity:0,y:20,duration:.5},1.8);
// throat breathes tighter
[0,1,2,3].forEach(i=>{['top','bot'].forEach(sd=>tl.to(rings[sd][i],{scaleX:.55,scaleY:.55,duration:.9,ease:'sine.inOut',yoyo:true,repeat:1},2.4+i*0.05));});
tl.to('#glow',{scale:1.4,duration:.9,yoyo:true,repeat:1,ease:'sine.inOut'},2.4);
""")

# ---------- E2S09: pull vs push (2.8 s) ----------
arrows = []
for k in range(8):
    import math
    a = k * math.pi / 4 + math.pi / 8
    arrows.append(a)
shots['E2S09'] = dict(dur=2.8, title='PULL <span>vs</span> PUSH',
 css="""#c{position:absolute;left:540px;top:900px;width:0;height:0}
#throat{position:absolute;left:-150px;top:-150px;width:300px;height:300px;border-radius:50%;border:3px solid var(--cyan);box-shadow:0 0 30px rgba(63,224,255,.6),inset 0 0 30px rgba(63,224,255,.3)}
.arr{position:absolute;left:0;top:0;height:0;transform-origin:0 0}
.arr i{position:absolute;top:-5px;height:10px;border-radius:5px}
.arr b{position:absolute;top:-17px;width:0;height:0;border-top:17px solid transparent;border-bottom:17px solid transparent}
.in i{left:250px;width:150px;background:var(--ember);box-shadow:0 0 16px rgba(255,74,46,.7)}
.in b{left:222px;border-right:30px solid var(--ember)}
.out i{left:170px;width:150px;background:var(--violet);box-shadow:0 0 16px rgba(123,92,255,.8)}
.out b{left:318px;border-left:30px solid var(--violet)}
#leg{position:absolute;left:90px;right:90px;top:1370px}
.row{display:flex;align-items:center;gap:26px;margin-bottom:34px}
.sw{width:70px;height:12px;border-radius:6px}
.row .big{font-size:52px}""",
 body="""  <div id="c"><div id="throat"></div>""" + ''.join(
   f'<div class="arr in" style="transform:rotate({a:.3f}rad)"><i></i><b></b></div>' for a in arrows[0::2]) + ''.join(
   f'<div class="arr out" style="transform:rotate({a:.3f}rad)"><i></i><b></b></div>' for a in arrows[1::2]) + """</div>
  <div id="leg">
    <div class="row" id="r1"><div class="sw" style="background:var(--ember)"></div><div><div class="lbl">PULLS IT SHUT</div><div class="big">Gravity</div></div></div>
    <div class="row" id="r2"><div class="sw" style="background:var(--violet)"></div><div><div class="lbl">PUSHES IT OPEN</div><div class="big" style="color:#a48cff">Negative energy</div></div></div>
  </div>""",
 js="""
tl.from('#throat',{opacity:0,scale:.7,duration:.4},0.1)
  .from('.in',{opacity:0,duration:.25,stagger:.05},0.35)
  .from('.in i, .in b',{x:120,duration:.5,ease:'power2.out',stagger:.02},0.35)
  .from('#r1',{opacity:0,x:-30,duration:.35},0.5)
  .to('#throat',{scale:.8,duration:.4,ease:'power2.in'},0.6)
  .from('.out',{opacity:0,duration:.25,stagger:.05},1.2)
  .from('.out i, .out b',{x:-120,duration:.5,ease:'power2.out',stagger:.02},1.2)
  .from('#r2',{opacity:0,x:-30,duration:.35},1.35)
  .to('#throat',{scale:1.05,duration:.6,ease:'power2.out'},1.5);
""")

# ---------- E3S08: Casimir plates (5.7 s) ----------
shots['E3S08'] = dict(dur=5.7, title='ONLY SOME <span>WAVES FIT</span>',
 css="""#plA,#plB{position:absolute;top:560px;width:26px;height:700px;border-radius:6px;background:linear-gradient(90deg,#b8862c,var(--gold),#b8862c);box-shadow:0 0 26px rgba(245,185,66,.55)}
#plA{left:400px}#plB{left:654px}
#lo,#li{position:absolute;font-family:PM;font-size:28px;letter-spacing:.12em;text-align:center}
#lo{top:1290px;left:0;width:390px;color:var(--cyan)}
#li{top:1290px;left:426px;width:228px;color:var(--gold)}
#lo2{position:absolute;top:1290px;right:0;width:400px;text-align:center;font-family:PM;font-size:28px;letter-spacing:.12em;color:var(--cyan)}
#panel{position:absolute;left:90px;right:90px;top:1440px}
#p2{margin-top:14px}""",
 body="""  <svg width="1080" height="1920" id="sv"></svg>
  <div id="plA"></div><div id="plB"></div>
  <div id="lo">ALL WAVES</div><div id="li">ONLY<br>FITTING</div><div id="lo2">ALL WAVES</div>
  <div id="panel"><div class="lbl" id="p1">TWO METAL PLATES, A HAIR APART</div><div class="big" id="p2">Fewer waves inside means less energy than empty space.</div></div>""",
 js="""
const NS='http://www.w3.org/2000/svg', sv=document.getElementById('sv');
const outside=[], inside=[];
const cols=['#3FE0FF','#7fd8ff','#5aa8ff','#3FE0FF','#9be8ff','#4fc0ff','#3FE0FF','#7fd8ff','#5aa8ff','#9be8ff'];
function mk(c,w,o){const p=document.createElementNS(NS,'path');p.setAttribute('fill','none');p.setAttribute('stroke',c);p.setAttribute('stroke-width',w);p.setAttribute('opacity',o);p.setAttribute('stroke-linecap','round');sv.appendChild(p);return p}
// outside: many wavelengths, both sides
for(let i=0;i<10;i++){const k=0.012+i*0.0075, y=600+i*64;
  outside.push({p:mk(cols[i],3,.75),x0:40,x1:385,y,k,a:22,sp:2+i*.35});
  outside.push({p:mk(cols[i],3,.75),x0:695,x1:1040,y,k,a:22,sp:2+i*.35});}
// inside: standing waves that fit (n = 1..4) between x=426..654
for(let n=1;n<=4;n++){inside.push({p:mk('#F5B942',3.5,.9),y:640+(n-1)*160,n});}
const ph={t:0};
function draw(){const t=ph.t;
  outside.forEach(o=>{let d='';for(let x=o.x0;x<=o.x1;x+=6){const y=o.y+o.a*Math.sin(o.k*x*6-t*o.sp);d+=(x===o.x0?'M':'L')+x+' '+y.toFixed(1)}o.p.setAttribute('d',d)});
  inside.forEach(o=>{let d='';const L=228;for(let x=0;x<=L;x+=4){const y=o.y+40*Math.sin(o.n*Math.PI*x/L)*Math.cos(t*1.6*o.n);d+=(x===0?'M':'L')+(426+x)+' '+y.toFixed(1)}o.p.setAttribute('d',d)});}
draw();
tl.to(ph,{t:12,duration:5.7,ease:'none',onUpdate:draw},0);
tl.from('#plA',{opacity:0,y:-60,duration:.5},0.3).from('#plB',{opacity:0,y:-60,duration:.5},0.4)
  .from(outside.map(o=>o.p),{opacity:0,duration:.6,stagger:.02},0.5)
  .from('#lo,#lo2',{opacity:0,duration:.4},1.0)
  .from(inside.map(o=>o.p),{opacity:0,duration:.5,stagger:.15},1.6)
  .from('#li',{opacity:0,duration:.4},2.0)
  .from('#p1',{opacity:0,x:-30,duration:.4},2.6).from('#p2',{opacity:0,y:20,duration:.5},2.9);
""")

# ---------- E3S09: energy meter (7.2 s) ----------
shots['E3S09'] = dict(dur=7.2, title='BELOW <span>ZERO</span>',
 css="""#meter{position:absolute;left:390px;top:520px;width:300px;height:860px}
#tube{position:absolute;left:110px;top:0;width:80px;height:860px;border-radius:40px;border:3px solid rgba(237,230,214,.5);background:rgba(237,230,214,.06)}
#zline{position:absolute;left:40px;top:430px;width:220px;height:4px;background:var(--chalk);box-shadow:0 0 12px rgba(237,230,214,.6)}
#pos{position:absolute;left:116px;bottom:430px;width:68px;height:330px;border-radius:34px 34px 0 0;background:linear-gradient(var(--cyan),rgba(63,224,255,.3));transform-origin:50% 100%}
#negf{position:absolute;left:116px;top:434px;width:68px;height:330px;border-radius:0 0 34px 34px;background:linear-gradient(#a48cff,var(--violet));box-shadow:0 0 30px rgba(123,92,255,.8);transform-origin:50% 0}
.mk{position:absolute;font-family:PM;font-size:28px;letter-spacing:.1em;white-space:nowrap}
#m0{left:280px;top:412px;color:var(--chalk)}
#mE{right:280px;top:412px;color:var(--cyan);text-align:right}
#mN{right:280px;top:700px;color:#a48cff;text-align:right}
#neg{position:absolute;top:1460px;width:100%;text-align:center;font-weight:700;font-size:96px;color:var(--violet);text-shadow:0 0 34px rgba(123,92,255,.7)}
#sub{position:absolute;top:1590px;width:100%;text-align:center}""",
 body="""  <div id="meter"><div id="tube"></div><div id="pos"></div><div id="negf"></div><div id="zline"></div>
    <div class="mk" id="m0">0</div><div class="mk" id="mE">EMPTY SPACE</div><div class="mk" id="mN">BETWEEN<br>THE PLATES</div></div>
  <div id="neg">NEGATIVE ENERGY</div>
  <div class="lbl" id="sub">MEASURED IN THE LAB SINCE 1997</div>""",
 js="""
gsap.set('#pos',{scaleY:0});gsap.set('#negf',{scaleY:0});
tl.from('#tube',{opacity:0,duration:.5},0.3).from('#zline',{scaleX:0,duration:.5},0.5)
  .from('#m0',{opacity:0,duration:.3},0.8)
  .to('#pos',{scaleY:.02,duration:.4},0.9)
  .from('#mE',{opacity:0,x:30,duration:.4},1.0)
  .to('#mE',{opacity:.55,duration:.3},2.4)
  .to('#negf',{scaleY:1,duration:1.6,ease:'power2.inOut'},2.4)
  .from('#mN',{opacity:0,x:30,duration:.4},3.0)
  .from('#neg',{opacity:0,scale:.9,duration:.5},4.0)
  .from('#sub',{opacity:0,y:15,duration:.4},4.6)
  .to('#negf',{opacity:.75,duration:.5,yoyo:true,repeat:3,ease:'sine.inOut'},5.0);
""")

for sid, d in shots.items():
    html = (HEAD.replace('%CSS%', d['css']).replace('%DUR%', str(d['dur']))
            .replace('%TITLE%', d['title']).replace('%BODY%', d['body']).replace('%JS%', d['js']))
    open(os.path.join(HERE, sid, 'index.html'), 'w').write(html)
    print('wrote', sid)
