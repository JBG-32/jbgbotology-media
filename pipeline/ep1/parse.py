import json,glob,re,sys
out={}
for f in glob.glob('/root/.claude/projects/-home-claude/f638c0ee-2db3-51e9-9fa4-4a0662295b40/tool-results/mcp-ElevenLabs-creative_get_flow_run_status-*.txt'):
    d=json.load(open(f))
    if isinstance(d,list): d=json.loads(d[0]['text']) if 'text' in d[0] else d
    for m in d.get('media',[]):
        p=m.get('prompt','')
        mm=re.match(r'Shot (\d+)\.',p)
        key=('s%02d'%int(mm.group(1))) if mm else None
        out.setdefault(key or m['generation_id'],[]).append({'gid':m['generation_id'],'kind':m['kind'],'prev':m['url'],'master':m.get('master_url'),'prompt':p[:80]})
    print(f, d.get('all_completed'), d.get('has_failures'))
json.dump(out,open('media.json','w'),indent=1)
for k,v in sorted(out.items(), key=lambda x:str(x[0])): print(k,len(v),[x['gid'] for x in v])
