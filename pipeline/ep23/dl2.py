import json,sys,os,subprocess
d=json.load(open(sys.argv[1]))
sfxname={'Cinematic heavy':'sfx_slam','Deep cinematic':'sfx_hit','Low electric':'sfx_fizz','Heavy mechanical':'sfx_lever','Soft quick':'sfx_chalk'}
n_ai=0
for m in d.get('media',[]):
    p=m.get('prompt','') or ''
    if m['kind']=='video':
        f='/tmp/claude-0/ep23/clips/%s.mp4'%p.split()[0]
    elif 'Lola' in p:
        n_ai+=1; f='/tmp/claude-0/ep23/audio/ai_tag_%d.mp3'%n_ai
    else:
        k=[v for kk,v in sfxname.items() if p.startswith(kk)]
        if not k: print('skip',p[:40]); continue
        f='/tmp/claude-0/ep23/audio/%s.mp3'%k[0]
    if os.path.exists(f) and os.path.getsize(f)>5000: continue
    subprocess.run(['curl','-sS','-o',f,m['master_url']]); print('got',os.path.basename(f))
print({g['prompt'].split()[0] if g.get('prompt') else g['id']:g['status'] for g in d['generations'] if g['status']!='completed'})
print('all',d['all_completed'],'fail',d['has_failures'])
