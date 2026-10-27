# 렌더 전 점검: 대본 줄 시간을 audio3d.py 와 같은 식으로 계산해 전략 회의 기준(길이·0초 훅·4초 전환·5초 첫 답·끝 처리)을 본다
# python3 precheck.py <영상설정.json> [음성폴더]   → 줄별 시각 + ✅/❌, ❌ 가 있으면 exit 1
# 낯선 고유명사(결재함 74③): 대본의 대문자 단어가 사전·r3d/known_names.txt·그 줄의 발음 철자(3번째 값)에 없으면 ❌ — Pituffik/Moshoeshoe 오독 재발 방지
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
import os
CAT=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','audio','bgm','catalog.json'))) if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','audio','bgm','catalog.json')) else {}
BGN=cfg.get('bgm') or cfg.get('mood','epic'); BGI=CAT.get(BGN) if CAT else {'tone':None}; TONE=(BGI or {}).get('tone')
SERIOUS=re.findall(r"\b(wars?|battles?|invad\w*|invasion|army|armies|troops|soldiers|killed|kill|died|deaths?|dead|massacres?|genocide|bombs?|bombed|nuclear|attacks?|threat\w*|famine|disasters?|earthquakes?|tsunamis?|occup\w+|conflicts?|enemy|fought|weapons?|missiles?|refugees|executed|slaves?|slavery|plague|terror\w*)\b",' '.join(r[1] for r in rows).lower())
SW=lambda t:re.search(r"\b(wars?|battles?|invad\w*|army|troops|soldiers|killed|died|dead|massacres?|genocide|bomb\w*|attacks?|famine|disasters?|occup\w+|fought|refugees|executed|slave\w*|plague)\b",t.lower())
BADCUE=[f"{c[2]}@{c[0]}" for c in cfg.get('sfx',[]) if c[2] in ('applause','glass') and SW(' '.join(r[1] for r in rows if r[0]==c[0]))]   # 전쟁 장면에 박수·건배 = 에바 (2026-10-27 Jacob)

# 낯선 고유명사 발음 점검 — 대본 줄 [장면, 화면 글, (TTS 가 읽을 발음 철자)]: channel/tts/cb_gen.py 가 3번째 값이 있으면 그걸 읽는다.
# 대문자 단어 후보(문장 첫 단어는 사전에 없을 때만)가 ① 영어 보통 단어(/usr/share/dict/words, 없으면 사전 없음) ② known_names.txt
# ③ 그 줄 3번째 값에서 철자가 바뀐 단어 — 셋 다 아니면 ❌. 사전이 없으면 문장 첫 단어는 판정 못 해 건너뛴다(대문자 단어 = 후보로 단순화).
HERE=os.path.dirname(os.path.abspath(__file__)); DICT=os.environ.get('PRECHECK_DICT','/usr/share/dict/words')
COMMON={x.strip() for x in open(DICT,errors='ignore') if x.strip().islower()} if os.path.exists(DICT) else None
KN=os.path.join(HERE,'known_names.txt'); KNOWN={x.split('#')[0].strip().lower() for x in open(KN,encoding='utf-8')} if os.path.exists(KN) else set()
TOK=re.compile(r"(?:[A-Za-z]\.){2,}|[A-Za-z][A-Za-z'’-]*")
def toks(s):   # [(단어, 문장 첫 단어인가)] — 소유격 's 는 뗀다
    out=[]; pend=True; last=0
    for m in TOK.finditer(s):
        if re.search(r'[.!?]',s[last:m.start()]): pend=True
        out.append((re.sub(r"['’]s$","",m.group()),pend)); pend=False; last=m.end()
    return out
def cand(w,first):
    if not w[0].isupper() or (len(w)<2 and '.' not in w) or re.fullmatch(r"I(['’](m|ll|d|ve))?",w): return False
    lw=w.lower()
    if lw in KNOWN: return False
    return (lw not in COMMON) if COMMON is not None else not first
BADNAME=[]
for nsid,ntxt,*nr in cfg['lines']:
    said={w.lower() for w,_ in toks(nr[0])} if nr and nr[0] else None   # 발음 철자 칸이 있으면 거기 남은 단어 = 철자가 안 바뀐 단어
    for w,fw in toks(ntxt):
        if cand(w,fw) and (said is None or w.lower() in said) and f'{w}({nsid})' not in BADNAME: BADNAME.append(f'{w}({nsid})')
chk=[('길이 35~40초',35<=TOT<=40,f'{TOT:.1f}s'),
     ('0초 큰 글자(big 첫 장면)',first in cfg.get('big',{}),' / '.join(cfg.get('big',{}).get(first,['없음']))),
     ('4초 안 장면 전환',cut<=4,f'{cut:.1f}s'),
     ('5초 안 첫 답',ans<=5,f'{ans:.1f}s'),
     ('끝: 맺음말 없음·꼬리 ≤0.5초',"map answer" not in rows[-1][1].lower() and cfg.get('tail',1.2)<=0.5,f"tail {cfg.get('tail',1.2)}s"),
     ('BGM: 무거운 소재에 밝은 곡 금지',not (SERIOUS and TONE=='light') and BGI is not None,f"{BGN} ({TONE or '목록에 없음'})"+(f" · 무거운 말: {', '.join(sorted(set(SERIOUS))[:4])}" if SERIOUS else '')),
     ('효과음: 무거운 장면에 박수·잔 소리 금지',not BADCUE,', '.join(BADCUE) or '없음'),
     ('낯선 고유명사',not BADNAME,('발음 철자 칸 필요 또는 이름 빼기: '+', '.join(BADNAME)) if BADNAME else '모두 확인됨(사전·known_names·발음 칸)'+('' if COMMON is not None else ' · 사전 없음: 문장 첫 단어는 건너뜀')),
     ('단어 타이밍(words.json 줄 수)',not VD or len(json.load(open(f'{VD}/words.json')))==len(rows),'' if VD else '(음성 없음 — 추정)')]
for name,ok,v in chk: print(('✅' if ok else '❌'),name,v)
if BGI and BGI.get('title'): print(f'ℹ️ 설명란에 넣을 줄: Music: "{BGI["title"]}" Kevin MacLeod (incompetech.com) · Licensed under Creative Commons: By Attribution 4.0 · http://creativecommons.org/licenses/by/4.0/')
sys.exit(0 if all(ok for _,ok,_ in chk) else 1)
