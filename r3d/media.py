# 카드 사진 준비: python3 media.py <영상설정.json> <저장소 media 폴더> <작업폴더/media>
# 설정 cards 의 photo src 가 media/<파일> 이면 복사, https URL 이면 받아서 media/<URL 마지막 이름> 으로 (cards.js mediaPath 와 같은 이름)
# 출처 줄(credit)이 없으면 멈춘다 — 라이선스 표기 없이 사진을 쓰지 않는다
import json,os,shutil,sys,urllib.request,urllib.parse
cfg=json.load(open(sys.argv[1])); SRC,DST=sys.argv[2],sys.argv[3]; os.makedirs(DST,exist_ok=True)
for c in cfg.get('cards',[]):
    if c.get('type')!='photo': continue
    if not (c.get('credit') or '').strip(): sys.exit(f"사진 카드 출처 줄(credit) 없음: {c.get('src')}")
    s=c['src']
    if s.startswith('http'):
        out=os.path.join(DST,urllib.parse.unquote(s.split('?')[0].rsplit('/',1)[-1]))
        if not os.path.exists(out):
            req=urllib.request.Request(s,headers={'User-Agent':'map-answer-render/1.0 (render bot)'})
            with urllib.request.urlopen(req,timeout=60) as r,open(out,'wb') as f: f.write(r.read())
    else:
        p=os.path.join(SRC,s[len('media/'):] if s.startswith('media/') else s)
        shutil.copy(p,os.path.join(DST,os.path.basename(p)))
    print('사진',s,'→',DST)
