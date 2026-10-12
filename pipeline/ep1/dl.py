import json,subprocess,os
from concurrent.futures import ThreadPoolExecutor
m=json.load(open('media.json'))
jobs=[]
for k,v in m.items():
    if not k.startswith('s'): continue
    for i,x in enumerate(v):
        jobs.append((x['master'],f'kf/{k}_{i+1}.png'))
def g(j):
    subprocess.run(['curl','-sS','-o',j[1],j[0]],check=True)
with ThreadPoolExecutor(8) as ex: list(ex.map(g,jobs))
from PIL import Image,ImageDraw
keys=sorted(k for k in m if k.startswith('s'))
for part in range(3):
    ks=keys[part*6:(part+1)*6]
    sheet=Image.new('RGB',(6*2*200+5*30,370),'white')
    for ci,k in enumerate(ks):
        for i in range(2):
            im=Image.open(f'kf/{k}_{i+1}.png').convert('RGB').resize((200,356))
            x=ci*(400+30)+i*200
            sheet.paste(im,(x,14))
            ImageDraw.Draw(sheet).text((x+4,0),f'{k} opt{i+1}',fill='black')
    sheet.save(f'kf/sheet{part}.png')
