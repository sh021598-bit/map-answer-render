# 3차 효과음 후보 (Actions 전용): BigSoundBank (Joseph SARDIN, CC0 — 실제 녹음) 검색 상위 3개씩
# 결과: audio/out3/<q>/<n>.ogg · audio/out3/list3.json (원본 페이지·제목·길이)
import json,os,re,subprocess,urllib.request,urllib.parse
O='audio/out3'; os.makedirs(O,exist_ok=True); UA={'User-Agent':'Mozilla/5.0 (map-answer-render audio fetch)'}
def get(u,t=60): return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=t).read()
Q={'gunshot':('gunshot rifle',4),'musket':('musket',4),'cannon':('cannon',5),'explosion':('explosion',5),'march':('marching soldiers',8),'footsteps':('footsteps gravel',6),
   'crowd':('crowd shouting',6),'cheer':('crowd cheering',6),'splash':('splash water',3),'swim':('swimming',6),'waves':('waves sea',10),'sheep':('sheep',3),
   'car':('car engine',6),'horn':('ship horn',5),'wind':('wind',10),'glass':('glass clink',2),'horse':('horse gallop',6),'bell':('church bell',5),'drum':('military drum',6)}
R={'sfx':{},'log':[]}
for key,(q,maxs) in Q.items():
    got=[]
    try:
        h=get('https://bigsoundbank.com/search?q='+urllib.parse.quote(q)).decode('utf-8','replace')
        pages=list(dict.fromkeys(re.findall(r'href="(?:https://bigsoundbank\.com)?/?([a-z0-9\-_]+-s\d{4}\.html)"',h)))[:6]
        if not pages: R['log'].append(f'{q}: 결과 없음 '+h[:200].replace('\n',' '))
        for pg in pages:
            if len(got)>=3: break
            c=get('https://bigsoundbank.com/'+pg).decode('utf-8','replace')
            if 'CC0' not in c and 'publicdomain/zero' not in c: R['log'].append(f'{pg}: CC0 표기 없음'); continue
            fl=list(dict.fromkeys(re.findall(r'''["'](https?://[^"']*?\.(?:mp3|ogg|wav|flac)|/?UPLOAD/[^"']+?\.(?:mp3|ogg|wav|flac))["']''',c,re.I)))
            fl=[f if f.startswith('http') else 'https://bigsoundbank.com/'+f.lstrip('/') for f in fl]
            fl.sort(key=lambda f:(0 if f.lower().endswith(('.wav','.flac')) else 1 if f.lower().endswith('.ogg') else 2))
            if not fl: R['log'].append(f'{pg}: 파일 링크 없음'); continue
            src='/tmp/x'+os.path.splitext(fl[0])[1]
            try: open(src,'wb').write(get(fl[0],120))
            except Exception as e: R['log'].append(f'{pg} {fl[0]}: {e}'); continue
            os.makedirs(f'{O}/{key}',exist_ok=True); dst=f'{O}/{key}/{len(got)}.ogg'
            subprocess.run(['ffmpeg','-v','error','-y','-i',src,'-t',str(maxs),'-ac','1','-ar','48000','-af','silenceremove=start_periods=1:start_threshold=-45dB,afade=t=out:st=%s:d=0.3'%max(0,maxs-0.3),'-c:a','libvorbis','-q:a','5',dst],check=True)
            dur=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',dst],capture_output=True,text=True).stdout or 0)
            title=re.search(r'<title>([^<]+)',c); got.append({'file':dst,'page':'https://bigsoundbank.com/'+pg,'title':title.group(1).strip() if title else pg,'dur':round(dur,2),'license':'CC0'})
    except Exception as e: R['log'].append(f'{q}: {e}')
    R['sfx'][key]=got
json.dump(R,open(f'{O}/list3.json','w'),ensure_ascii=False,indent=1)
print(json.dumps(R['log'],ensure_ascii=False)[:3000]); print({k:len(v) for k,v in R['sfx'].items()})
