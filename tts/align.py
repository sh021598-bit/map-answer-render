# Whisper(faster-whisper) 받아쓰기로 음성 검수 + 단어 타이밍: python align.py <음성폴더> <lines.json|영상설정.json>
# → <음성폴더>/words.json [[단어,시작,끝],...] 줄별, check.txt (대본 대조: 일치율)
import sys,json,glob,re,difflib
from faster_whisper import WhisperModel
d=sys.argv[1]; L=json.load(open(sys.argv[2])); L=L['lines'] if isinstance(L,dict) else L
m=WhisperModel('small.en',device='cpu',compute_type='int8'); out=[]; rep=[]
norm=lambda s:re.sub(r'[^a-z0-9 ]','',s.lower().replace('-',' ')).split()
for i,ln in enumerate(L):
    sid,txt=ln[0],ln[1]
    segs,_=m.transcribe(f'{d}/{i:02d}.wav',word_timestamps=True,language='en')
    ws=[[w.word.strip(),round(w.start,3),round(w.end,3)] for s in segs for w in s.words]; out.append(ws)
    heard=' '.join(w[0] for w in ws); r=difflib.SequenceMatcher(None,norm(txt),norm(heard)).ratio()
    rep.append(f'{i:02d} {r:.2f} | {txt} | {heard}')
json.dump(out,open(f'{d}/words.json','w')); open(f'{d}/check.txt','w').write('\n'.join(rep)); print('\n'.join(rep))
