# 렌더 전 점검: 대본 줄 시간을 audio3d.py 와 같은 식으로 계산해 전략 회의 기준(길이·0초 훅·4초 전환·5초 첫 답·끝 처리)을 본다
# python3 precheck.py <영상설정.json> [음성폴더]   → 줄별 시각 + ✅/❌, ❌ 가 있으면 exit 1
# 음성폴더 없이 = TTS 전 추정(음절 ÷ 4.5/초, 002~006 실측 중앙값, 줄마다 ±20%) — 대본 단계에서 먼저 고친다
import json,re,struct,sys,numpy as np
if len(sys.argv)<2: sys.exit('사용: python3 precheck.py <영상설정.json> [음성폴더]')
cfg=json.load(open(sys.argv[1])); VD=sys.argv[2] if len(sys.argv)>2 else None
def read(p):   # wav(PCM16·float32) → (float 배열, sr) — soundfile 없이
    b=open(p,'rb').read(); i=12; fmt=sr=None
    while i<len(b):
        cid,n=b[i:i+4],struct.unpack('<I',b[i+4:i+8])[0]
        if cid==b'fmt ': fmt,ch,sr=struct.unpack('<HHI',b[i+8:i+16]); bits=struct.unpack('<H',b[i+22:i+24])[0]
        if cid==b'data':
            a=np.frombuffer(b[i+8:i+8+n],'<f4' if fmt==3 else '<i2' if bits==16 else '<i4').astype(np.float32)
            return a.reshape(-1,ch).mean(1),sr
        i+=8+n+(n&1)
def dur(i,txt):    # audio3d.load 과 같은 앞뒤 무음 자르기 (음성 없으면 audio3d.syl 로 추정)
    if not VD: return sum(max(1,len(re.findall(r'[aeiouy]+',w.lower())))+(3 if re.search(r'\d',w) else 0) for w in txt.split())/4.5
    a,sr=read(f'{VD}/{i:02d}.wav'); nz=np.where(np.abs(a)>0.02*np.abs(a).max())[0]
    return (min(len(a),nz[-1]+sr//50)-max(0,nz[0]-sr//100))/sr
t=0.0; rows=[]
for i,(sid,txt,*_) in enumerate(cfg['lines']):
    d=dur(i,txt); rows.append((sid,txt,t,t+d))
    gap=0.12 if txt.endswith(',') else (0.35 if sid in('ask','end') else 0.22)
    nxt=cfg['lines'][i+1][0] if i+1<len(cfg['lines']) else None
    if nxt!=sid: gap+=cfg.get('hold',{}).get(sid,0)
    t+=d+gap
TOT=t+cfg.get('tail',1.2)
for sid,txt,a,b in rows: print(f'{a:5.1f}-{b:5.1f}s  {sid:8} {txt[:60]}')
first=rows[0][0]; cut=next((a for s,_,a,_ in rows if s!=first),TOT)
ans=next((a for s,x,a,_ in rows[1:] if not x.rstrip().endswith('?')),TOT)   # 첫 답 = 질문 아닌 둘째 줄부터의 첫 줄
chk=[('길이 35~40초',35<=TOT<=40,f'{TOT:.1f}s'),
     ('0초 큰 글자(big 첫 장면)',first in cfg.get('big',{}),' / '.join(cfg.get('big',{}).get(first,['없음']))),
     ('4초 안 장면 전환',cut<=4,f'{cut:.1f}s'),
     ('5초 안 첫 답',ans<=5,f'{ans:.1f}s'),
     ('끝: 맺음말 없음·꼬리 ≤0.5초',"map answer" not in rows[-1][1].lower() and cfg.get('tail',1.2)<=0.5,f"tail {cfg.get('tail',1.2)}s"),
     ('단어 타이밍(words.json 줄 수)',not VD or len(json.load(open(f'{VD}/words.json')))==len(rows),'' if VD else '(음성 없음 — 추정)')]
for name,ok,v in chk: print(('✅' if ok else '❌'),name,v)
sys.exit(0 if all(ok for _,ok,_ in chk) else 1)
