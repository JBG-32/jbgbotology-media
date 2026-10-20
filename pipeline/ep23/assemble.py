"""Assemble Stargate Ep 2 or Ep 3.  usage: python3 assemble.py ep2|ep3 [seg ov mix mux]"""
import json, subprocess, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

EP = sys.argv[1]
W, H, FPS = 1080, 1920, 30
B = '/tmp/claude-0/ep23'
REPO = '/home/claude/jbgbotology-media'
os.chdir(B)
os.makedirs(f'build/{EP}/seg', exist_ok=True)
BD = f'build/{EP}'
FD = '/tmp/claude-0/ep1/fonts/fontsource-space-grotesk-5.3.0/files/'
FM = '/tmp/claude-0/ep1/fonts/fontsource-ibm-plex-mono-5.3.0/files/'
F_BOLD, F_MED = FD + 'space-grotesk-latin-700-normal.woff', FD + 'space-grotesk-latin-500-normal.woff'
F_MONO = FM + 'ibm-plex-mono-latin-500-normal.woff'
CHALK, GOLD, CYAN, EMBER, VIOLET = (237, 230, 214), (245, 185, 66), (63, 224, 255), (255, 74, 46), (123, 92, 255)
LAV = (164, 140, 255)

SHOTS = json.load(open(f'{REPO}/pipeline/ep23/shots.json'))[EP]
PICKS = json.load(open(f'{REPO}/pipeline/ep23/picks.json'))
N = 2 if EP == 'ep2' else 3

# ---------------- episode config ----------------
if EP == 'ep2':
    VO_END = 85.8
    END_BG = 'keys/E2S14_B.png'
    FROM_END = {'E2S07'}
    HEAD = [
        (0.25, 4.5, ['EVERY WORMHOLE', 'SLAMS SHUT'], CHALK, None, None),
        (9.5, 13.2, ['LAST WEEK:', 'A BRIDGE IN THE MATH'], CHALK, 'EP 1 RECAP', CYAN),
        (18.7, 23.9, ['WHEELER & FULLER'], CHALK, '1962', GOLD),
        (24.1, 29.5, ['OPENS... THEN', 'PINCHES SHUT'], CHALK, None, None),
        (32.9, 38.6, ['GRAVITY PULLS'], EMBER, 'MATTER · LIGHT · ENERGY', CHALK),
        (38.8, 41.3, ['SQUEEZING', 'THE THROAT CLOSED'], CHALK, None, None),
        (44.3, 48.3, ['EXOTIC MATTER'], LAV, 'NEGATIVE ENERGY', LAV),
        (48.6, 53.5, ['MORRIS & THORNE'], CHALK, '1988', GOLD),
        (53.7, 57.2, ["CARL SAGAN'S", 'CONTACT'], CHALK, 'THE NOVEL', GOLD),
        (57.4, 63.2, ['A WORMHOLE YOU', 'COULD TRAVEL THROUGH'], CHALK, None, None),
        (63.4, 68.7, ['PROPPED OPEN BY', 'EXOTIC MATTER'], LAV, 'IF IT EXISTS', CHALK),
        (68.9, 73.2, ['THE RING JUST', 'STAYS OPEN'], GOLD, None, None),
        (73.4, 79.9, ['IS NEGATIVE ENERGY', 'EVEN REAL?'], LAV, None, None),
        (80.1, 85.7, ['NEXT SUNDAY'], CHALK, "WE'VE MEASURED IT", LAV),
    ]
    RP = [(18.6, 41.4), (44.2, 68.7)]
    SF = [(68.8, 73.3)]
    NEXT = ('EP 3  ·  NEGATIVE ENERGY IS REAL', 'NEXT SUNDAY  ·  12 PM CT')
    MUSIC = 'audio/ep2_music_A.mp3'
    SFX = [('sfx_hit', 0.0, 0.55), ('sfx_slam', 3.0, 0.6), ('sfx_chalk', 18.9, 0.35), ('sfx_slam', 25.4, 0.45),
           ('sfx_fizz', 44.3, 0.35), ('sfx_hit', 68.8, 0.4), ('sfx_hit', 80.1, 0.45)]
    MUSIC_DIP = (67.8, 68.9)
    OUT = 'Stargate_Ep2_Why_Every_Wormhole_Slams_Shut.mp4'
else:
    VO_END = 85.6
    END_BG = 'keys/E3S17_A.png'
    FROM_END = set()
    HEAD = [
        (0.2, 3.7, ['NEGATIVE ENERGY', 'SOUNDS MADE UP'], CHALK, None, None),
        (5.8, 9.7, ['LAST WEEK:', 'IT NEEDS NEGATIVE ENERGY'], CHALK, 'EP 2 RECAP', CYAN),
        (9.9, 11.9, ['DOES IT EXIST?'], LAV, None, None),
        (12.1, 16.9, ['EMPTY SPACE', "ISN'T EMPTY"], CHALK, None, None),
        (17.1, 22.7, ['QUANTUM', 'FLUCTUATIONS'], CYAN, None, None),
        (22.9, 27.0, ['HENDRIK CASIMIR'], CHALK, '1948', GOLD),
        (27.2, 30.3, ['TWO PLATES,', 'VERY CLOSE'], CHALK, None, None),
        (43.4, 46.8, ['PUSHED TOGETHER'], CHALK, None, None),
        (47.0, 50.3, ['STEVE LAMOREAUX'], CHALK, '1997', GOLD),
        (50.5, 56.5, ['PINNED DOWN TO', 'ABOUT 1%'], CHALK, 'THE CASIMIR EFFECT IS REAL', CYAN),
        (56.7, 58.8, ['THE CATCH'], EMBER, None, None),
        (59.2, 63.7, ['~1 MICROMETER', 'APART'], CHALK, 'THINNER THAN A BACTERIUM', GOLD),
        (63.9, 71.0, ['A 1-METER WORMHOLE'], CHALK, "SOME ESTIMATES: A JUPITER'S WORTH", LAV),
        (71.3, 73.5, ['FLIP A SWITCH'], GOLD, None, None),
        (73.7, 78.5, ['COULD WE EVER', 'MAKE ENOUGH?'], LAV, None, None),
        (78.7, 85.5, ['NEXT SUNDAY'], CHALK, 'WHERE WOULD IT GO?', LAV),
    ]
    RP = [(12.0, 30.4), (43.3, 71.0)]
    SF = [(71.1, 73.6)]
    NEXT = ('EP 4  ·  AN ADDRESS FOR THE UNIVERSE', 'NEXT SUNDAY  ·  12 PM CT')
    MUSIC = 'audio/ep3_music_A.mp3'
    SFX = [('sfx_hit', 0.0, 0.55), ('sfx_fizz', 12.1, 0.35), ('sfx_chalk', 23.0, 0.35), ('sfx_slam', 43.4, 0.35),
           ('sfx_hit', 56.7, 0.45), ('sfx_lever', 71.4, 0.5), ('sfx_hit', 78.7, 0.45)]
    MUSIC_DIP = (56.0, 56.8)
    OUT = 'Stargate_Ep3_Negative_Energy_Is_Real.mp4'

CLOSE_AT = round(VO_END + 0.3, 2)            # "So, real physics or pure sci-fi? Tell me in the comments"
TAG_AT = round(CLOSE_AT + 4.75, 2)           # "I'm Lola. I'm an AI. See you next Sunday."
TOTAL = round(TAG_AT + 3.6 + 0.6, 2)
HF = [tuple(s['t']) for s in SHOTS if s['type'] == 'hyperframes']


def dur(f):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f],
                                capture_output=True, text=True).stdout)


# ---------------- timeline ----------------
def timeline():
    T, zi = [], 0
    for s in SHOTS:
        sid, (a, b), k = s['id'], s['t'], s['type']
        if k == 'still':
            zi += 1
            T.append((sid, f'keys/{sid}_{PICKS[sid]}.png', 'still', a, b, {'zin': zi % 2 == 1}))
        elif k == 'reuse':
            T.append((sid, 'clips/E2S13.mp4', 'v', a, b, {'ss': 1.2}))
        elif sid == 'E2S13':
            T.append((sid, 'clips/E2S13.mp4', 'v', a, a + 6.0, {}))
            T.append(('E2S13B', 'keys/E2S13_B.png', 'still', a + 6.0, b, {'zin': True}))
        else:
            T.append((sid, f'clips/{sid}.mp4', 'v', a, b, {'from_end': sid in FROM_END}))
    T.append(('end', END_BG, 'still', T[-1][4], TOTAL, {'zin': True, 'z1': 1.04}))
    return T


def build_segments():
    lst = []
    for name, src, kind, a, b, o in timeline():
        n = round((b - a) * FPS)
        out = f'{BD}/seg/{name}.mp4'
        if kind == 'still':
            z0, z1 = (1.0, o.get('z1', 1.10)) if o['zin'] else (1.10, 1.0)
            z = f"{z0}+({z1}-{z0})*on/{n - 1}"
            vf = (f"scale=2160:3840,zoompan=z='{z}':x='(iw-iw/zoom)*0.5':y='(ih-ih/zoom)*0.42':d={n}:s={W}x{H}:fps={FPS},"
                  f"eq=contrast=1.03:saturation=1.04,format=yuv420p")
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-i', src, '-vf', vf, '-frames:v', str(n),
                            '-c:v', 'libx264', '-crf', '15', '-preset', 'medium', out], check=True)
            print('still', name, a, b)
        else:
            L, d = dur(src), n / FPS
            ss, speed = o.get('ss', 0.0), 1.0
            if L - ss < d:
                speed = (L - ss) / d
            elif o.get('from_end'):
                ss = max(0.0, L - d - 0.05)
            vf = (f"setpts=PTS/{speed:.5f},fps={FPS},scale={W}:{H}:flags=lanczos,"
                  f"eq=contrast=1.03:saturation=1.04,format=yuv420p")
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{ss:.3f}', '-i', src, '-vf', vf, '-frames:v', str(n),
                            '-an', '-c:v', 'libx264', '-crf', '15', '-preset', 'medium', out], check=True)
            print('vid', name, a, b, 'src', round(L, 2), 'speed', round(speed, 3), 'ss', round(ss, 2))
        lst.append(out)
    with open(f'{BD}/concat.txt', 'w') as f:
        for p in lst:
            f.write(f"file '{os.path.abspath(p)}'\n")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{BD}/concat.txt', '-c', 'copy',
                    f'{BD}/base.mp4'], check=True)
    print('base', dur(f'{BD}/base.mp4'), 'target', TOTAL)


# ---------------- overlay graphics ----------------
def font(p, s):
    return ImageFont.truetype(p, s)


def tw(d, t, f, sp=0):
    return sum(d.textlength(c, font=f) for c in t) + sp * (len(t) - 1) if sp else d.textlength(t, font=f)


def tracked(d, xy, t, f, fill, sp=0):
    x, y = xy
    if not sp:
        d.text((x, y), t, font=f, fill=fill)
        return
    for c in t:
        d.text((x, y), c, font=f, fill=fill)
        x += d.textlength(c, font=f) + sp


def shadowed(fn, blur=10, alpha=170):
    fg = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    fn(ImageDraw.Draw(fg))
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    a = fg.split()[3].filter(ImageFilter.GaussianBlur(blur)).point(lambda v: min(255, int(v * alpha / 255 * 1.6)))
    sh.putalpha(a)
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    out.alpha_composite(sh, (0, 4))
    out.alpha_composite(fg)
    return out


F_LABEL, F_CAP, F_HEAD, F_HEAD_S = font(F_MONO, 28), font(F_BOLD, 66), font(F_BOLD, 64), font(F_BOLD, 50)
F_BADGE, F_SUB, F_END1, F_END2, F_END3 = font(F_MONO, 30), font(F_MONO, 34), font(F_BOLD, 82), font(F_MED, 44), font(F_MONO, 26)


def persistent():
    def f(d):
        tracked(d, (64, 170), f'COULD A STARGATE BE REAL?  ·  EP {N}', F_LABEL, CHALK + (215,), 2)
        t = 'JBGBotology'
        d.text((W - 64 - tw(d, t, F_LABEL), 170), t, font=F_LABEL, fill=CHALK + (180,))
    return shadowed(f, 6, 150)


def headline(lines, color=CHALK, sub=None, subcolor=None, y=360):
    def f(d):
        yy = y
        for ln in lines:
            fnt = F_HEAD if len(ln) <= 16 else F_HEAD_S
            tracked(d, ((W - tw(d, ln, fnt, 3)) / 2, yy), ln, fnt, color + (255,), 3)
            yy += fnt.size + 14
        if sub:
            tracked(d, ((W - tw(d, sub, F_SUB, 2)) / 2, yy + 10), sub, F_SUB, (subcolor or GOLD) + (255,), 2)
    return shadowed(f, 14, 200)


def badge(kind):
    col = CYAN if kind == 'REAL PHYSICS' else GOLD
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x, y, h = 64, 236, 58
    d.rounded_rectangle((x, y, x + tw(d, kind, F_BADGE, 3) + 86, y + h), radius=h // 2, fill=(5, 6, 10, 185),
                        outline=col + (255,), width=3)
    if kind == 'REAL PHYSICS':
        d.ellipse((x + 24, y + h / 2 - 9, x + 42, y + h / 2 + 9), fill=col + (255,))
    else:
        d.polygon([(x + 33, y + h / 2 - 11), (x + 44, y + h / 2), (x + 33, y + h / 2 + 11), (x + 22, y + h / 2)], fill=col + (255,))
    tracked(d, (x + 60, y + 11), kind, F_BADGE, col + (255,), 3)
    return img


def caption_img(words, active, low):
    def f(d):
        if d.textlength(' '.join(words), font=F_CAP) > W - 140:
            mid = len(words) // 2 + (len(words) % 2)
            lines = [words[:mid], words[mid:]]
        else:
            lines = [words]
        y0 = (1690 if low else 1545) - (len(lines) - 1) * 40
        idx = 0
        for li, lw in enumerate(lines):
            x = (W - d.textlength(' '.join(lw), font=F_CAP)) / 2
            for wd in lw:
                col = GOLD if idx == active else (255, 255, 255)
                d.text((x, y0 + li * 82), wd, font=F_CAP, fill=col + (255,), stroke_width=3, stroke_fill=(0, 0, 0, 230))
                x += d.textlength(wd + ' ', font=F_CAP)
                idx += 1
    return shadowed(f, 10, 190)


def end_card():
    def f(d):
        y = 470
        for ln, col in (('REAL PHYSICS', CYAN), ('OR PURE SCI-FI?', GOLD)):
            tracked(d, ((W - tw(d, ln, F_END1, 3)) / 2, y), ln, F_END1, col + (255,), 3)
            y += 104
        t = 'Tell me in the comments'
        d.text(((W - d.textlength(t, font=F_END2)) / 2, y + 30), t, font=F_END2, fill=(255, 255, 255, 255))
        y2 = 1340
        for t, col in ((NEXT[0], CHALK), (NEXT[1], GOLD)):
            tracked(d, ((W - tw(d, t, F_SUB, 2)) / 2, y2), t, F_SUB, col + (255,), 2)
            y2 += 56
        t = 'Follow JBGBotology'
        d.text(((W - d.textlength(t, font=F_END2)) / 2, y2 + 28), t, font=F_END2, fill=(255, 255, 255, 255))
        t = "NARRATED BY LOLA, AN AI NARRATOR"
        tracked(d, ((W - tw(d, t, F_END3, 2)) / 2, y2 + 120), t, F_END3, CHALK + (200,), 2)
    img = Image.new('RGBA', (W, H), (0, 0, 0, 120))
    img.alpha_composite(shadowed(f, 14, 220))
    return img


def in_hf(t):
    return any(a <= t < b for a, b in HF)


def build_events():
    ev = []
    # persistent strip, hidden while the HyperFrames graphics (which carry their own badge/title) are up
    cuts = [0.0] + [x for ab in HF for x in ab] + [VO_END]
    strip = persistent()
    for a, b in zip(cuts[0::2], cuts[1::2]):
        ev.append((a, b, strip, 0))
    for a, b, lines, col, sub, subcol in HEAD:
        ev.append((a, b, headline(lines, col, sub, subcol, 380 if len(lines) == 1 else 360), 0.25))
    ev.append((VO_END, TOTAL, end_card(), 0.4))
    rp, sf = badge('REAL PHYSICS'), badge('SCI-FI')
    for a, b in RP:
        ev.append((a, b, rp, 0.2))
    for a, b in SF:
        ev.append((a, b, sf, 0.2))
    words = [w for w in json.load(open(f'audio/{EP}_words.json'))['words']
             if w['type'] == 'word' and not w['text'].startswith('[')]
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= 3 or w['text'][-1] in '.,?!:':
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    for ci, ch in enumerate(chunks):
        a = 0.0 if ch[0]['start'] < 0.2 else ch[0]['start']
        nxt = chunks[ci + 1][0]['start'] if ci + 1 < len(chunks) else ch[-1]['end'] + 0.4
        b = min(nxt, ch[-1]['end'] + 0.6, VO_END)
        texts = tuple(x['text'] for x in ch)
        for wi, w in enumerate(ch):
            ws = w['start'] if wi else a
            we = ch[wi + 1]['start'] if wi + 1 < len(ch) else b
            ev.append((ws, we, ('cap', texts, wi, in_hf(ws)), 0))
    return ev


def render_overlay(ev):
    cache, n = {}, round(TOTAL * FPS)
    blank = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-i', f'{BD}/base.mp4', '-f', 'rawvideo', '-pix_fmt', 'rgba',
                          '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-filter_complex', '[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]', '-map', '[v]',
                          '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-r', str(FPS), '-frames:v', str(n),
                          f'{BD}/video_overlay.mp4'], stdin=subprocess.PIPE)
    last_key = last_bytes = None
    for i in range(n):
        t = i / FPS
        active = []
        for a, b, img, fd in ev:
            if a <= t < b:
                al = max(0.0, min(1.0, (t - a) / fd, (b - t) / fd)) if fd else 1.0
                active.append((img, round(al, 2)))
        key = tuple((x if isinstance(x, tuple) else id(x), al) for x, al in active)
        if key != last_key:
            frame = blank.copy()
            for img, al in active:
                if isinstance(img, tuple):
                    if img not in cache:
                        cache[img] = caption_img(list(img[1]), img[2], img[3])
                    img = cache[img]
                if al < 1:
                    im2 = img.copy()
                    im2.putalpha(img.split()[3].point(lambda v, al=al: int(v * al)))
                    img = im2
                frame.alpha_composite(img)
            last_bytes, last_key = frame.tobytes(), key
        p.stdin.write(last_bytes)
    p.stdin.close()
    p.wait()
    print('overlay done')


def mix_audio():
    inputs = ['-i', f'audio/{EP}_take1.mp3', '-i', 'audio/closing.mp3', '-i', 'audio/ai_tag_1.mp3', '-i', MUSIC]
    for s, _, _ in SFX:
        inputs += ['-i', f'audio/{s}.mp3']
    c, t = int(CLOSE_AT * 1000), int(TAG_AT * 1000)
    fc = ['[0:a]aresample=48000[n0]',
          f'[1:a]aresample=48000,adelay={c}|{c}[n1]',
          f'[2:a]aresample=48000,adelay={t}|{t}[n2]',
          f'[n0][n1][n2]amix=inputs=3:normalize=0,apad=whole_dur={TOTAL}[narr]',
          '[narr]asplit=2[narrA][narrSC]',
          f"[3:a]aresample=48000,atrim=0:{TOTAL},volume='if(between(t,{MUSIC_DIP[0]},{MUSIC_DIP[1]}),0.15,1)':eval=frame,"
          f"afade=t=in:st=0:d=1.5,afade=t=out:st={TOTAL - 2.5}:d=2.5,volume=0.34[mus]",
          '[mus][narrSC]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[musd]']
    labels = []
    for i, (s, at, vol) in enumerate(SFX):
        ms = int(at * 1000)
        fc.append(f'[{4 + i}:a]aresample=48000,volume={vol},adelay={ms}|{ms}[x{i}]')
        labels.append(f'[x{i}]')
    fc.append(f"[narrA][musd]{''.join(labels)}amix=inputs={2 + len(SFX)}:normalize=0,atrim=0:{TOTAL},"
              "loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inputs + ['-filter_complex', ';'.join(fc), '-map', '[aout]',
                    '-ar', '48000', '-c:a', 'aac', '-b:a', '192k', f'{BD}/mix.m4a'], check=True)
    print('mix', dur(f'{BD}/mix.m4a'))


def mux():
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{BD}/video_overlay.mp4', '-i', f'{BD}/mix.m4a', '-map', '0:v',
                    '-map', '1:a', '-c:v', 'copy', '-c:a', 'copy', '-shortest', '-movflags', '+faststart', OUT], check=True)
    print('final', OUT, dur(OUT))


if __name__ == '__main__':
    steps = sys.argv[2:] or ['seg', 'ov', 'mix', 'mux']
    if 'seg' in steps: build_segments()
    if 'ov' in steps: render_overlay(build_events())
    if 'mix' in steps: mix_audio()
    if 'mux' in steps: mux()
