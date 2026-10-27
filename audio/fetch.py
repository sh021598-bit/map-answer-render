# 무료 음원 후보 받기 (Actions 전용 — 세션 네트워크는 이 사이트들을 막음). 결과: audio/out/ + audio/out/list.json
# 효과음 = Kenney (CC0, 출처 표기 불필요) · BGM 후보 = Kevin MacLeod incompetech (CC BY 4.0, 설명란 출처 필수)
# Pixabay 는 Content ID 오탐 사례가 있어 뺐다. YouTube 오디오 보관함은 공개 레포에 파일을 둘 수 없어(단독 배포 금지) 여기서 안 받음.
import io,json,os,re,subprocess,urllib.request,urllib.parse,zipfile,random
O='audio/out'; os.makedirs(O,exist_ok=True); UA={'User-Agent':'Mozilla/5.0 (map-answer-render audio fetch)'}
def get(u): return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60).read()
res={'sfx':{},'bgm':[],'log':[]}
for slug in ['rpg-audio','casino-audio','impact-sounds','interface-sounds','ui-audio']:
    try:
        h=get(f'https://kenney.nl/assets/{slug}').decode('utf-8','replace')
        z=re.findall(r'href="([^"]+\.zip)"',h)
        if not z: res['log'].append(f'{slug}: zip 링크 없음'); continue
        url=z[0] if z[0].startswith('http') else 'https://kenney.nl'+z[0]
        zf=zipfile.ZipFile(io.BytesIO(get(url))); d=f'{O}/kenney/{slug}'; os.makedirs(d,exist_ok=True); names=[]
        for n in zf.namelist():
            if n.lower().endswith(('.ogg','.wav')):
                b=os.path.basename(n); open(f'{d}/{b}','wb').write(zf.read(n)); names.append(b)
            if 'license' in n.lower(): open(f'{d}/LICENSE.txt','wb').write(zf.read(n))
        res['sfx'][slug]={'url':url,'files':sorted(names)}
    except Exception as e: res['log'].append(f'{slug}: {e}')
FEEL={'epic':['Epic','Heroic'],'tense':['Intense','Suspenseful','Driving','Tense'],'mystery':['Mysterious','Eerie','Mystical'],'bright':['Bright','Uplifting','Bouncy']}
try:
    P=json.loads(get('https://incompetech.com/music/royalty-free/pieces.json'))
    res['log'].append('pieces keys: '+', '.join(P[0].keys()) if isinstance(P,list) else 'pieces 형식: '+str(type(P)))
    random.seed(7)
    for mood,keys in FEEL.items():
        pick=[p for p in P if any(k.lower() in str(p.get('feel','')).lower() for k in keys)]
        pick=[p for p in pick if 'piano' not in str(p.get('instruments','')).lower()] or pick
        random.shuffle(pick)
        n=0
        for p in pick:
            if n>=4: break
            fn=p.get('filename') or (p.get('title','')+'.mp3')
            url='https://incompetech.com/music/royalty-free/mp3-royaltyfree/'+urllib.parse.quote(fn)
            try: b=get(url)
            except Exception as e: res['log'].append(f'{fn}: {e}'); continue
            src=f'/tmp/{n}_{mood}.mp3'; open(src,'wb').write(b); out=f'{O}/bgm/{mood}_{n}.mp3'; os.makedirs(f'{O}/bgm',exist_ok=True)
            subprocess.run(['ffmpeg','-v','error','-y','-ss','8','-t','22','-i',src,'-af','afade=t=in:d=1,afade=t=out:st=20:d=2','-b:a','96k',out],check=True)
            res['bgm'].append({'mood':mood,'file':out,'title':p.get('title'),'feel':p.get('feel'),'genre':p.get('genre'),'url':url}); n+=1
except Exception as e: res['log'].append(f'incompetech: {e}')
json.dump(res,open(f'{O}/list.json','w'),ensure_ascii=False,indent=1)
print(json.dumps(res['log'],ensure_ascii=False)); print(len(res['bgm']),'bgm', {k:len(v['files']) for k,v in res['sfx'].items()})
