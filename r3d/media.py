# 카드 사진·영상 준비: python3 media.py <영상설정.json> <저장소 media 폴더> <작업폴더/media>
# 설정 cards 의 photo src 가 media/<파일> 이면 복사, https URL 이면 받아서 media/<URL 마지막 이름> 으로 (cards.js mediaPath 와 같은 이름)
# video(2026-11-12): src 를 받아(또는 media/ 에서) ffmpeg 로 start 부터 CLIP 초를 원음 없이 1080×1920(9:16 자르기, x)·30fps JPG 로 잘라
#   media/<videoDir>/001.jpg… + clip.json{n,src,credit} (cards.js videoDir 과 같은 이름). 원본 클립은 레포에 안 둔다 — 렌더 때마다 받는다
# 출처 줄(credit)이 없으면 멈춘다 — 라이선스 표기 없이 사진·영상을 쓰지 않는다
import json,math,os,re,shutil,subprocess,sys,urllib.request,urllib.parse
CLIP=2.8   # 카드 한 장 최대 2.5초(precheck) + 여유. 카드가 더 길면 마지막 프레임 유지
FPS=30
UA='map-answer-render/1.0 (https://github.com/sh021598-bit/map-answer-render; render bot)'
def fetch(s,out):
    if not os.path.exists(out):
        req=urllib.request.Request(s,headers={'User-Agent':UA})
        with urllib.request.urlopen(req,timeout=120) as r,open(out+'.part','wb') as f: shutil.copyfileobj(r,f)
        os.replace(out+'.part',out)
def name(s): return urllib.parse.unquote(s.split('?')[0].rsplit('/',1)[-1])
def video_dir(c):   # cards.js videoDir 과 같아야 한다 (시험: test_media.py)
    nm=re.sub(r'[^A-Za-z0-9]','_',re.sub(r'\.[A-Za-z0-9]+$','',name(str(c['src']))))[:60]
    return f"v_{nm}_{math.floor(float(c.get('start') or 0)*100+0.5)}"   # JS Math.round 와 같게(파이썬 round 는 짝수 반올림)
def cut_video(c,src,dst):
    x=float(c.get('x',0.5)); x=min(1,max(0,x)); os.makedirs(dst,exist_ok=True)
    for f in os.listdir(dst): os.remove(os.path.join(dst,f))
    vf=(f"scale=w='if(gt(a,9/16),-2,1080)':h='if(gt(a,9/16),1920,-2)':flags=lanczos,"
        f"crop=1080:1920:'(iw-1080)*{x}':'(ih-1920)/2',fps={FPS},setsar=1")
    subprocess.run(['ffmpeg','-v','error','-y','-ss',str(float(c.get('start') or 0)),'-t',str(CLIP),'-i',src,'-an','-vf',vf,
                    '-q:v','3','-start_number','1',os.path.join(dst,'%03d.jpg')],check=True)
    n=len([f for f in os.listdir(dst) if f.endswith('.jpg')])
    if n<int(1.5*FPS): sys.exit(f"영상 카드 클립이 짧음({n/FPS:.1f}초 < 1.5초): {c['src']} start {c.get('start',0)}")
    h=subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height','-of','csv=p=0',src],capture_output=True,text=True).stdout.strip()
    json.dump({'n':n,'src':c['src'],'start':c.get('start',0),'credit':c['credit'],'source_size':h},open(os.path.join(dst,'clip.json'),'w'),ensure_ascii=False)
    print('영상',c['src'],f'{n}프레임 (원본 {h})','→',dst)
    try:
        w_,h_=map(int,h.split(',')[:2])
        if min(w_,h_)<720: print(f'ℹ️ 원본 해상도 낮음 {h} — 9:16 자르면 흐릴 수 있음')
    except ValueError: pass
if __name__=='__main__':
    cfg=json.load(open(sys.argv[1])); SRC,DST=sys.argv[2],sys.argv[3]; os.makedirs(DST,exist_ok=True)
    CACHE=os.path.join(DST,'_src')
    for c in cfg.get('cards',[]):
        if c.get('type') not in ('photo','video'): continue
        if not (c.get('credit') or '').strip(): sys.exit(f"{'사진' if c['type']=='photo' else '영상'} 카드 출처 줄(credit) 없음: {c.get('src')}")
        s=c['src']
        if c['type']=='video':
            os.makedirs(CACHE,exist_ok=True)
            if s.startswith('http'): p=os.path.join(CACHE,name(s)); fetch(s,p)
            else: p=os.path.join(SRC,s[len('media/'):] if s.startswith('media/') else s)
            cut_video(c,p,os.path.join(DST,video_dir(c))); continue
        if s.startswith('http'): fetch(s,os.path.join(DST,name(s)))
        else:
            p=os.path.join(SRC,s[len('media/'):] if s.startswith('media/') else s)
            shutil.copy(p,os.path.join(DST,os.path.basename(p)))
        print('사진',s,'→',DST)
