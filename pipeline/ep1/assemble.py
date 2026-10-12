import json, subprocess, os, math, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
B = '/tmp/claude-0/ep1'
os.chdir(B)
FD = 'fonts/fontsource-space-grotesk-5.3.0/files/'
FM = 'fonts/fontsource-ibm-plex-mono-5.3.0/files/'
F_BOLD = FD + 'space-grotesk-latin-700-normal.woff'
F_MED = FD + 'space-grotesk-latin-500-normal.woff'
F_MONO = FM + 'ibm-plex-mono-latin-500-normal.woff'
CHALK = (237, 230, 214)
GOLD = (245, 185, 66)
CYAN = (63, 224, 255)
EMBER = (255, 74, 46)
VIOLET = (123, 92, 255)

# ---------------- timeline ----------------
# (name, source, kind, start, end, opts)
T = [
    ('s01', 'clips/s01.mp4', 'v', 0.0, 5.2, {}),
    ('s02', 'clips/s02.mp4', 'v', 5.2, 9.0, {}),
    ('s03', 'build/seg/s03.mp4', 's', 9.0, 13.0, {}),
    ('s05a', 'build/seg/s05a.mp4', 's', 13.0, 17.1, {}),
    ('s04', 'clips/s04.mp4', 'v', 17.1, 20.8, {}),
    ('s05b', 'build/seg/s05b.mp4', 's', 20.8, 25.2, {}),
    ('s06', 'clips/s06.mp4', 'v', 25.2, 30.8, {'from_end': True}),
    ('s07', 'clips/s07.mp4', 'v', 30.8, 34.6, {}),
    ('s08', 'clips/s08.mp4', 'v', 34.6, 37.9, {}),
    ('s09', 'build/seg/s09.mp4', 's', 37.9, 42.9, {}),
    ('s10', 'build/seg/s10.mp4', 's', 42.9, 49.3, {}),
    ('s11', 'build/seg/s11.mp4', 's', 49.3, 51.0, {}),
    ('s12', 'clips/s12.mp4', 'v', 51.0, 55.4, {'from_end': True}),
    ('s13', 'clips/s13.mp4', 'v', 55.4, 58.3, {}),
    ('s14', 'clips/s14.mp4', 'v', 58.3, 61.9, {}),
    ('s15', 'build/seg/s15.mp4', 's', 61.9, 66.1, {}),
    ('s16', 'clips/s16.mp4', 'v', 66.1, 68.6, {}),
    ('s17', 'clips/s17.mp4', 'v', 68.6, 71.6, {}),
    ('s18', 'clips/s18.mp4', 'v', 71.6, 75.5, {}),
    ('s19', 'clips/s19.mp4', 'v', 75.5, 79.0, {}),
    ('s20', 'clips/s20.mp4', 'v', 79.0, 85.4, {'fit': True}),
    ('end', 'build/seg/end.mp4', 's', 85.4, 91.0, {}),
]
TOTAL = 91.0


def dur(f):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f],
                                capture_output=True, text=True).stdout)


def build_segments():
    lst = []
    for name, src, kind, a, b, o in T:
        d = round((b - a) * FPS) / FPS
        n = round((b - a) * FPS)
        L = dur(src)
        ss = 0.0
        speed = 1.0
        if o.get('fit') or L < d:
            speed = L / d  # >1 speeds up, <1 slows
        elif o.get('from_end'):
            ss = max(0.0, L - d - 0.05)
        vf = (f"setpts=PTS/{speed:.5f},fps={FPS},scale={W}:{H}:flags=lanczos,"
              f"eq=contrast=1.03:saturation=1.04,format=yuv420p")
        out = f'build/seg/T_{name}.mp4'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{ss:.3f}', '-i', src, '-vf', vf, '-frames:v', str(n),
                        '-an', '-c:v', 'libx264', '-crf', '15', '-preset', 'medium', out], check=True)
        lst.append(out)
        print('seg', name, f'{a}-{b}', 'src', round(L, 2), 'speed', round(speed, 3), 'ss', round(ss, 2))
    with open('build/concat.txt', 'w') as f:
        for p in lst:
            f.write(f"file '{os.path.abspath(p)}'\n")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', 'build/concat.txt', '-c', 'copy',
                    'build/base.mp4'], check=True)
    print('base', dur('build/base.mp4'))


# ---------------- overlay graphics ----------------
def font(p, s):
    return ImageFont.truetype(p, s)


def text_size(d, t, f, sp=0):
    if sp:
        w = sum(d.textlength(c, font=f) for c in t) + sp * (len(t) - 1)
    else:
        w = d.textlength(t, font=f)
    return w


def draw_tracked(d, xy, t, f, fill, sp=0):
    x, y = xy
    if not sp:
        d.text((x, y), t, font=f, fill=fill)
        return
    for c in t:
        d.text((x, y), c, font=f, fill=fill)
        x += d.textlength(c, font=f) + sp


def shadowed(layer_fn, blur=10, alpha=170):
    """render with a soft dark shadow underneath"""
    fg = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    layer_fn(ImageDraw.Draw(fg))
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    a = fg.split()[3].filter(ImageFilter.GaussianBlur(blur))
    a = a.point(lambda v: min(255, int(v * alpha / 255 * 1.6)))
    sh.putalpha(a)
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    out.alpha_composite(sh, (0, 4))
    out.alpha_composite(fg)
    return out


F_LABEL = font(F_MONO, 28)
F_CAP = font(F_BOLD, 66)
F_HEAD = font(F_BOLD, 64)
F_HEAD_S = font(F_BOLD, 50)
F_BADGE = font(F_MONO, 30)
F_SUB = font(F_MONO, 34)
F_END1 = font(F_BOLD, 82)
F_END2 = font(F_MED, 44)


def persistent():
    def f(d):
        draw_tracked(d, (64, 170), 'COULD A STARGATE BE REAL?  ·  EP 1', F_LABEL, CHALK + (215,), 2)
        t = 'JBGBotology'
        w = text_size(d, t, F_LABEL)
        d.text((W - 64 - w, 170), t, font=F_LABEL, fill=CHALK + (180,))
    return shadowed(f, 6, 150)


def headline(lines, color=CHALK, y=330, sub=None, subcolor=None):
    def f(d):
        yy = y
        for ln in lines:
            fnt = F_HEAD if len(ln) <= 16 else F_HEAD_S
            w = text_size(d, ln, fnt, 3)
            draw_tracked(d, ((W - w) / 2, yy), ln, fnt, color + (255,), 3)
            yy += fnt.size + 14
        if sub:
            w = text_size(d, sub, F_SUB, 2)
            draw_tracked(d, ((W - w) / 2, yy + 10), sub, F_SUB, (subcolor or GOLD) + (255,), 2)
    return shadowed(f, 14, 200)


def badge(kind):
    col = CYAN if kind == 'REAL PHYSICS' else GOLD
    sym = '●' if kind == 'REAL PHYSICS' else '◆'
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    txt = f'{kind}'
    tw = text_size(d, txt, F_BADGE, 3)
    x, y, h = 64, 236, 58
    wbox = tw + 86
    d.rounded_rectangle((x, y, x + wbox, y + h), radius=h // 2, fill=(5, 6, 10, 185), outline=col + (255,), width=3)
    d.ellipse((x + 24, y + h / 2 - 9, x + 42, y + h / 2 + 9), fill=col + (255,)) if sym == '●' else \
        d.polygon([(x + 33, y + h / 2 - 11), (x + 44, y + h / 2), (x + 33, y + h / 2 + 11), (x + 22, y + h / 2)], fill=col + (255,))
    draw_tracked(d, (x + 60, y + 11), txt, F_BADGE, col + (255,), 3)
    return img


def caption_img(words, active):
    # words: list of str ; active index highlighted gold
    def f(d):
        line = ' '.join(words)
        w = d.textlength(line, font=F_CAP)
        if w > W - 140:  # wrap into two lines
            mid = len(words) // 2 + (len(words) % 2)
            lines = [words[:mid], words[mid:]]
        else:
            lines = [words]
        y0 = 1545 - (len(lines) - 1) * 40
        idx = 0
        for li, lw in enumerate(lines):
            s = ' '.join(lw)
            lwid = d.textlength(s, font=F_CAP)
            x = (W - lwid) / 2
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
            w = text_size(d, ln, F_END1, 3)
            draw_tracked(d, ((W - w) / 2, y), ln, F_END1, col + (255,), 3)
            y += 104
        t = 'Tell me in the comments'
        w = d.textlength(t, font=F_END2)
        d.text(((W - w) / 2, y + 30), t, font=F_END2, fill=(255, 255, 255, 255))
        y2 = 1380
        t = 'EP 2  ·  HOW TO HOLD IT OPEN'
        w = text_size(d, t, F_SUB, 2)
        draw_tracked(d, ((W - w) / 2, y2), t, F_SUB, CHALK + (255,), 2)
        t = 'NEXT SUNDAY  ·  12 PM CT'
        w = text_size(d, t, F_SUB, 2)
        draw_tracked(d, ((W - w) / 2, y2 + 56), t, F_SUB, GOLD + (255,), 2)
        t = 'Follow JBGBotology'
        w = d.textlength(t, font=F_END2)
        d.text(((W - w) / 2, y2 + 140), t, font=F_END2, fill=(255, 255, 255, 255))
    img = Image.new('RGBA', (W, H), (0, 0, 0, 120))
    img.alpha_composite(shadowed(f, 14, 220))
    return img


# events: (start, end, image, fade)
def build_events():
    ev = []
    ev.append((0.0, 85.4, persistent(), 0))
    ev += [
        (0.25, 4.8, headline(['WHAT IF EINSTEIN', 'DREW A STARGATE?'], sub='1935', subcolor=GOLD, y=360), 0.25),
        (9.3, 13.0, headline(['EINSTEIN & ROSEN'], sub='1935', y=360), 0.3),
        (17.3, 20.8, headline(['MASS BENDS', 'SPACETIME'], y=360), 0.3),
        (21.0, 25.0, headline(['GOAL:', 'DESCRIBE PARTICLES'], y=360), 0.3),
        (33.6, 37.8, headline(['A BRIDGE'], sub='EINSTEIN–ROSEN BRIDGE', subcolor=CYAN, y=380), 0.3),
        (38.2, 42.8, headline(['WORMHOLE'], sub='1957  ·  JOHN WHEELER', y=380), 0.3),
        (45.4, 49.2, headline(['A TO B:', 'THE LONG WAY'], y=360), 0.3),
        (52.6, 55.3, headline(['A = B'], color=GOLD, y=380), 0.2),
        (62.2, 66.0, headline(['COULD WE', 'WALK THROUGH ONE?'], y=360), 0.3),
        (69.4, 71.5, headline(['THE CATCH'], color=EMBER, y=380), 0.15),
        (72.0, 75.4, headline(['IT CLOSES FASTER', 'THAN LIGHT CAN CROSS'], y=360), 0.3),
        (77.8, 78.9, headline(['NOT SO FAST.'], color=VIOLET, y=380), 0.2),
        (79.2, 85.3, headline(['NEXT SUNDAY'], sub='HOW TO HOLD ONE OPEN', subcolor=VIOLET, y=380), 0.3),
        (85.5, 91.0, end_card(), 0.4),
    ]
    rp, sf = badge('REAL PHYSICS'), badge('SCI-FI')
    for a, b in ((9.2, 25.0), (30.9, 42.8), (71.8, 75.4)):
        ev.append((a, b, rp, 0.2))
    ev.append((55.5, 61.8, sf, 0.2))
    # captions
    words = [w for w in json.load(open('audio/words.json'))['words'] if w['type'] == 'word']
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= 3 or w['text'][-1] in '.,?!:':
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    for ci, ch in enumerate(chunks):
        a = ch[0]['start']
        nxt = chunks[ci + 1][0]['start'] if ci + 1 < len(chunks) else ch[-1]['end'] + 0.4
        b = min(nxt, ch[-1]['end'] + 0.6)
        if a < 0.2:
            a = 0.0
        texts = [x['text'] for x in ch]
        for wi, w in enumerate(ch):
            ws = w['start'] if wi else a
            we = ch[wi + 1]['start'] if wi + 1 < len(ch) else b
            ev.append((ws, we, ('cap', tuple(texts), wi), 0))
    return ev


def render_overlay(ev):
    cache = {}
    n = round(TOTAL * FPS)
    blank = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-i', 'build/base.mp4', '-f', 'rawvideo', '-pix_fmt', 'rgba',
                          '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-filter_complex', '[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]', '-map', '[v]',
                          '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-r', str(FPS), '-frames:v', str(n),
                          'build/video_overlay.mp4'], stdin=subprocess.PIPE)
    last_key, last_bytes = None, None
    for i in range(n):
        t = i / FPS
        active = []
        for (a, b, img, fd) in ev:
            if a <= t < b:
                alpha = 1.0
                if fd:
                    alpha = min(1.0, (t - a) / fd, (b - t) / fd)
                alpha = max(0.0, alpha)
                active.append((img, round(alpha, 2)))
        key = tuple((id(x) if not isinstance(x, tuple) else x, al) for x, al in active)
        if key != last_key:
            frame = blank.copy()
            for img, al in active:
                if isinstance(img, tuple):
                    k = img
                    if k not in cache:
                        cache[k] = caption_img(list(k[1]), k[2])
                    img = cache[k]
                if al < 1:
                    a = img.split()[3].point(lambda v, al=al: int(v * al))
                    im2 = img.copy()
                    im2.putalpha(a)
                    img = im2
                frame.alpha_composite(img)
            last_bytes = frame.tobytes()
            last_key = key
        p.stdin.write(last_bytes)
    p.stdin.close()
    p.wait()
    print('overlay done')


def mix_audio():
    sfx = [('sfx_hook', 0.0, 0.55), ('sfx_dive', 27.7, 0.6), ('sfx_type', 38.3, 0.45), ('sfx_punch', 51.2, 0.6),
           ('sfx_boom', 55.4, 0.8), ('sfx_collapse', 71.8, 0.6)]
    inputs = ['-i', 'audio/lola_take2.mp3', '-i', 'audio/closing.mp3', '-i', 'audio/music2.mp3']
    for s, _, _ in sfx:
        inputs += ['-i', f'audio/{s}.mp3']
    fc = []
    fc.append('[0:a]aresample=48000,volume=1.0[n0]')
    fc.append('[1:a]aresample=48000,adelay=85700|85700,volume=1.0[n1]')
    fc.append('[n0][n1]amix=inputs=2:normalize=0,apad=whole_dur=91[narr]')
    fc.append('[narr]asplit=2[narrA][narrSC]')
    # music: base level, dip for the catch, fade out end
    fc.append("[2:a]aresample=48000,atrim=0:91,volume='if(between(t,68.7,71.7),0.08,1)':eval=frame,"
              "afade=t=in:st=0:d=1.5,afade=t=out:st=88.5:d=2.5,volume=0.34[mus]")
    fc.append('[mus][narrSC]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[musd]')
    labels = []
    for i, (s, at, vol) in enumerate(sfx):
        ms = int(at * 1000)
        fc.append(f'[{3 + i}:a]aresample=48000,volume={vol},adelay={ms}|{ms}[x{i}]')
        labels.append(f'[x{i}]')
    fc.append(f"[narrA][musd]{''.join(labels)}amix=inputs={2 + len(sfx)}:normalize=0,atrim=0:91,"
              "loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inputs + ['-filter_complex', ';'.join(fc), '-map', '[aout]',
                                                               '-ar', '48000', '-c:a', 'aac', '-b:a', '192k',
                                                               'build/mix.m4a'], check=True)
    print('mix', dur('build/mix.m4a'))


def mux():
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'build/video_overlay.mp4', '-i', 'build/mix.m4a', '-map', '0:v',
                    '-map', '1:a', '-c:v', 'copy', '-c:a', 'copy', '-shortest', '-movflags', '+faststart',
                    'Stargate_Ep1_Einstein_Drew_A_Stargate.mp4'], check=True)
    print('final', dur('Stargate_Ep1_Einstein_Drew_A_Stargate.mp4'))


if __name__ == '__main__':
    steps = sys.argv[1:] or ['seg', 'ov', 'mix', 'mux']
    if 'seg' in steps: build_segments()
    if 'ov' in steps: render_overlay(build_events())
    if 'mix' in steps: mix_audio()
    if 'mux' in steps: mux()
