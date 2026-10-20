import json,sys,os,subprocess
d=json.load(open(sys.argv[1]))
out='/tmp/claude-0/ep23/clips'
for m in d.get('media',[]):
    sid=m['prompt'].split()[0]
    f=f'{out}/{sid}.mp4'
    if os.path.exists(f) and os.path.getsize(f)>10000: continue
    subprocess.run(['curl','-sS','-o',f,m['master_url']])
    print('got',sid,m.get('duration_secs'))
st={}
for g in d['generations']: st[g['prompt'].split()[0]]=g['status']
print({k:v for k,v in st.items() if v!='completed'})
print('all_completed',d['all_completed'],'fail',d['has_failures'])
