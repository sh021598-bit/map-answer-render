# 2차 음원 후보 (Actions 전용): OpenGameArt CC0 효과음(총·대포·행진·함성·물·파도·양 등) + incompetech BGM 분위기별 추가 후보(수치로 거름)
# 결과: audio/out2/sfx/<q>/*.ogg · audio/out2/bgm/*.mp3 · audio/out2/list2.json
import io,json,os,re,subprocess,urllib.request,urllib.parse,zipfile,random
import numpy as np
O='audio/out2'; os.makedirs(O,exist_ok=True); UA={'User-Agent':'Mozilla/5.0 (map-answer-render audio fetch)'}
def get(u,t=60): return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=t).read()
R={'sfx':{},'bgm':[],'log':[]}
def conv(src,dst,maxs):
    subprocess.run(['ffmpeg','-v','error','-y','-i',src,'-t',str(maxs),'-ac','1','-ar','48000','-af','silenceremove=start_periods=1:start_threshold=-45dB','-c:a','libvorbis','-q:a','5',dst],check=True)
    return float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',dst],capture_output=True,text=True).stdout or 0)
Q={'gunshot':6,'rifle shot':6,'musket':6,'cannon':6,'explosion':6,'marching':8,'footsteps march':8,'war cry':6,'battle cry':6,'crowd cheer':6,
   'water splash':5,'swimming':8,'ocean waves':10,'sea waves':10,'sheep':4,'car engine':6,'ship horn':6,'wind':10,'glass clink':3}
for q,maxs in Q.items():
    got=[]; d=f'{O}/sfx/{q.replace(" ","_")}'
    try:
        h=get('https://opengameart.org/art-search-advanced?'+urllib.parse.urlencode({'keys':q,'field_art_type_tid[]':13,'sort_by':'count','sort_order':'DESC'})).decode('utf-8','replace')
        pages=list(dict.fromkeys(re.findall(r'href="(/content/[^"#?]+)"',h)))[:8]
        for pg in pages:
            if len(got)>=3: break
            try: c=get('https://opengameart.org'+pg).decode('utf-8','replace')
            except Exception as e: R['log'].append(f'{q} {pg}: {e}'); continue
            if 'publicdomain/zero' not in c: continue
            files=list(dict.fromkeys(re.findall(r'https?://opengameart\.org/sites/default/files/[^"\s<>]+\.(?:ogg|wav|mp3|flac|zip)',c,re.I)))
            for fu in files[:3]:
                if len(got)>=3: break
                try: b=get(fu,90)
                except Exception as e: R['log'].append(f'{q} {fu}: {e}'); continue
                if len(b)>25_000_000: continue
                srcs=[]
                if fu.lower().endswith('.zip'):
                    try:
                        z=zipfile.ZipFile(io.BytesIO(b)); names=[n for n in z.namelist() if n.lower().endswith(('.ogg','.wav','.mp3','.flac'))]
                        key=[n for n in names if any(w in n.lower() for w in q.split())] or names
                        for n in key[:2]: p=f'/tmp/s_{len(got)}_{len(srcs)}'+os.path.splitext(n)[1]; open(p,'wb').write(z.read(n)); srcs.append((p,n))
                    except Exception as e: R['log'].append(f'{q} zip: {e}')
                else:
                    p='/tmp/s_'+str(len(got))+os.path.splitext(fu)[1]; open(p,'wb').write(b); srcs.append((p,os.path.basename(fu)))
                for p,n in srcs:
                    if len(got)>=3: break
                    os.makedirs(d,exist_ok=True); dst=f'{d}/{len(got)}.ogg'
                    try: dur=conv(p,dst,maxs)
                    except Exception as e: R['log'].append(f'{q} conv {n}: {e}'); continue
                    got.append({'file':dst,'src_page':'https://opengameart.org'+pg,'src_file':n,'dur':round(dur,2),'license':'CC0'})
    except Exception as e: R['log'].append(f'{q}: {e}')
    R['sfx'][q]=got
# BGM 추가 후보 — 무거운 분위기엔 밝은·장난 느낌 금지(필터), 목소리 대역·기복 수치로 상위 3곡
SERIOUS_BAN=('bright','bouncy','humorous','uplifting','grooving','quirky')
FEEL={'epic':['epic','heroic'],'tense':['intense','suspenseful','driving','tense','aggressive'],'mystery':['mysterious','eerie','mystical','unnerving'],
      'somber':['somber','sad','melancholic'],'bright':['bright','uplifting','bouncy']}
def dec(p):
    raw=subprocess.run(['ffmpeg','-v','error','-ss','10','-t','30','-i',p,'-ac','1','-ar','22050','-f','f32le','-'],capture_output=True).stdout
    return np.frombuffer(raw,np.float32)
def metr(a,sr=22050,w=2048):
    fr=a[:len(a)//w*w].reshape(-1,w); sp=np.abs(np.fft.rfft(fr*np.hanning(w),axis=1))**2; f=np.fft.rfftfreq(w,1/sr)
    vb=float((sp[:,(f>300)&(f<3000)].sum(1)/(sp.sum(1)+1e-12)).mean()); r=np.sqrt((fr**2).mean(1))
    return vb,float(20*np.log10(np.percentile(r,95)/max(np.percentile(r,10),1e-6)))
try:
    P=json.loads(get('https://incompetech.com/music/royalty-free/pieces.json')); random.seed(11)
    for mood,keys in FEEL.items():
        pool=[p for p in P if any(k in str(p.get('feel','')).lower() for k in keys) and 'humorous' not in str(p.get('feel','')).lower()]
        if mood!='bright': pool=[p for p in pool if not any(b in str(p.get('feel','')).lower() for b in SERIOUS_BAN)]
        else: pool=[p for p in pool if not any(b in str(p.get('feel','')).lower() for b in ('dark','eerie','somber','unnerving'))]
        random.shuffle(pool); scored=[]
        for p in pool[:10]:
            fn=p.get('filename') or p.get('title','')+'.mp3'; url='https://incompetech.com/music/royalty-free/mp3-royaltyfree/'+urllib.parse.quote(fn)
            try: open('/tmp/b.mp3','wb').write(get(url,90))
            except Exception as e: R['log'].append(f'bgm {fn}: {e}'); continue
            vb,dy=metr(dec('/tmp/b.mp3'))
            if dy>14: continue
            out=f'{O}/bgm/{mood}_{len(scored)}.mp3'; os.makedirs(f'{O}/bgm',exist_ok=True)
            subprocess.run(['ffmpeg','-v','error','-y','-i','/tmp/b.mp3','-t','80','-ac','2','-b:a','128k',out],check=True)
            scored.append({'mood':mood,'file':out,'title':p.get('title'),'feel':p.get('feel'),'voiceband':round(vb,2),'dyn':round(dy,1),'url':url})
        scored.sort(key=lambda x:x['voiceband']+x['dyn']/40)
        for x in scored[3:]: os.remove(x['file'])
        R['bgm']+=scored[:3]
except Exception as e: R['log'].append(f'incompetech: {e}')
json.dump(R,open(f'{O}/list2.json','w'),ensure_ascii=False,indent=1)
print(json.dumps(R['log'],ensure_ascii=False)[:3000]); print({q:len(v) for q,v in R['sfx'].items()}, len(R['bgm']))
