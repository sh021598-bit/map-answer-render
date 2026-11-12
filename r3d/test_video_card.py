# 영상 카드 시험 (2026-11-12): python3 test_video_card.py   — ffmpeg·node 필요, 사본(임시 폴더)에서만 돈다
# ① media.py video_dir == cards.js videoDir (이름 규칙이 어긋나면 렌더에서 프레임 404)
# ② cut_video: 가로·세로 원본 → 1080×1920 · 2.8초 = 84±1프레임 · 원음 없음 · 짧은 원본은 멈춤
# ③ precheck: 허용 출처·출처 줄·라이선스·길이 1.5~2.5초·≤3장 (정상·경계·실패)
import json,os,shutil,subprocess,sys,tempfile
sys.dont_write_bytecode=True
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE); import media
T=tempfile.mkdtemp(); ok=fail=0
def check(name,cond,info=''):
    global ok,fail
    print(('✅' if cond else '❌'),name,info); ok+=cond; fail+=not cond
# ①
srcs=[{'src':'https://upload.wikimedia.org/wikipedia/commons/a/ab/Gambia_River_(2019).webm','start':1.25},
      {'src':'https://commons.wikimedia.org/wiki/Special:FilePath/Sunrise%20at%20the%20Gambia%20River.webm?width=1280'},
      {'src':'media/Río_Gambia-é clip.mp4','start':0},{'src':'https://images-assets.nasa.gov/video/x/x~orig.mp4','start':'2'},{'src':'a.webm','start':0.125},{'src':'b.webm','start':2.345}]
js="import('"+os.path.join(HERE,'cards.js')+"').then(m=>console.log(JSON.stringify(%s.map(m.videoDir))))"%json.dumps(srcs)
out=subprocess.run(['node','--input-type=module','-e',js],capture_output=True,text=True,cwd=T)
jsd=json.loads(out.stdout or 'null') or []
pyd=['media/'+media.video_dir(c) for c in srcs]
check('videoDir py == js',jsd==pyd,f'{pyd}' if jsd==pyd else f'py {pyd} js {jsd} {out.stderr[:200]}')
# ②
def mk(p,w,h,d): subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i',f'testsrc2=size={w}x{h}:rate=25:duration={d}','-f','lavfi','-i',f'sine=d={d}','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac',p],check=True)
from PIL import Image
for w,h in((1920,1080),(720,1280),(1080,1920)):
    p=os.path.join(T,f's{w}.mp4'); mk(p,w,h,4); d=os.path.join(T,f'o{w}')
    media.cut_video({'src':p,'credit':'Video: x / CC0','start':0.5,'x':0.2},p,d)
    n=json.load(open(os.path.join(d,'clip.json')))['n']; sz=Image.open(os.path.join(d,'001.jpg')).size
    check(f'자르기 {w}x{h}',sz==(1080,1920) and 83<=n<=85,f'{sz} {n}프레임')
p=os.path.join(T,'short.mp4'); mk(p,1920,1080,1.2)
r=subprocess.run([sys.executable,'-c',f"import sys;sys.path.insert(0,{HERE!r});import media;media.cut_video({{'src':'s','credit':'Video: x / CC0'}},{p!r},{os.path.join(T,'os')!r})"],capture_output=True,text=True)
check('짧은 원본(1.2초) 멈춤',r.returncode!=0,r.stderr.strip()[-60:])
r=subprocess.run([sys.executable,os.path.join(HERE,'media.py'),'-'],input='',capture_output=True,text=True)
cfg={'cards':[{'type':'video','src':'https://upload.wikimedia.org/x.webm','scene':'a'}]}; cp=os.path.join(T,'nocredit.json'); json.dump(cfg,open(cp,'w'))
r=subprocess.run([sys.executable,os.path.join(HERE,'media.py'),cp,T,os.path.join(T,'m')],capture_output=True,text=True)
check('출처 줄 없음 → media.py 멈춤',r.returncode!=0 and 'credit' in r.stderr,r.stderr.strip()[-50:])
# ③ precheck — 감비아 시험 설정(음성 009) 위에 카드만 바꿔서
base=json.load(open(os.path.join(HERE,'..','videos','gambia_cards_test.json'))); V=os.path.join(HERE,'..','voice','009_gambia')
U='https://upload.wikimedia.org/wikipedia/commons/a/ab/Gambia_River.webm'
good={'type':'video','scene':'river','from':0.9,'to':3.1,'src':U,'credit':'Video: Someone / CC BY 4.0 (Wikimedia Commons)'}
cases=[('정상 Commons CC BY 2.2초',[good],True),
       ('정상 NASA 1.5초 경계',[{**good,'src':'https://images-assets.nasa.gov/video/a/a~orig.mp4','to':2.4,'credit':'Video: NASA'}],True),
       ('정상 3장',[good,{**good,'scene':'brit'},{**good,'scene':'strip','from':0.2,'to':2.2}],True),
       ('실패 4장',[good,{**good,'scene':'brit'},{**good,'scene':'strip'},{**good,'scene':'indep'}],False),
       ('실패 Pexels',[{**good,'src':'https://videos.pexels.com/x.mp4'}],False),
       ('실패 가짜 nasa 도메인',[{**good,'src':'https://nasa.gov.evil.com/a.mp4'}],False),
       ('실패 출처 줄 없음',[{**good,'credit':''}],False),
       ('실패 Video: 아님',[{**good,'credit':'Photo: x / CC BY 4.0'}],False),
       ('실패 CC BY-SA',[{**good,'credit':'Video: x / CC BY-SA 4.0'}],False),
       ('실패 2.6초',[{**good,'to':3.5}],False),
       ('실패 to 없음(장면 끝까지 >2.5초)',[{k:v for k,v in good.items() if k!='to'}],False)]
for name,cards,exp in cases:
    c=dict(base); c['cards']=cards; p=os.path.join(T,'c.json'); json.dump(c,open(p,'w'))
    r=subprocess.run([sys.executable,os.path.join(HERE,'precheck.py'),p,V],capture_output=True,text=True)
    line=[l for l in r.stdout.splitlines() if '카드(' in l]
    check('precheck '+name,(r.returncode==0)==exp,line[0][:110] if line else r.stderr[-120:])
shutil.rmtree(T); print(f'{ok} 통과 / {fail} 실패'); sys.exit(1 if fail else 0)
