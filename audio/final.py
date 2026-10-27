# 채널성장팀이 고른 음원만 정리 (Actions 전용): audio/bgm/<mood>.mp3 (앞 80초) · audio/sfx/*.ogg · audio/CREDITS.md
import os,shutil,subprocess,urllib.request,urllib.parse
BGM={'epic':'Impact Lento','tense':'Constance','mystery':'Thunder Dreams','bright':'Rollin at 5 - electronic'}
SFX={'coins':'rpg-audio/handleCoins.ogg','cloth':'rpg-audio/cloth1.ogg','pluck':'interface-sounds/pluck_001.ogg','scratch':'interface-sounds/scratch_001.ogg','impact':'impact-sounds/impactSoft_heavy_000.ogg'}
os.makedirs('audio/bgm',exist_ok=True); os.makedirs('audio/sfx',exist_ok=True)
for m,t in BGM.items():
    u='https://incompetech.com/music/royalty-free/mp3-royaltyfree/'+urllib.parse.quote(t+'.mp3')
    open('/tmp/x.mp3','wb').write(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=60).read())
    subprocess.run(['ffmpeg','-v','error','-y','-i','/tmp/x.mp3','-t','80','-ac','2','-b:a','128k',f'audio/bgm/{m}.mp3'],check=True)
for k,p in SFX.items(): shutil.copy(f'audio/out/kenney/{p}',f'audio/sfx/{k}.ogg')
open('audio/CREDITS.md','w').write('# 음원 출처\n\n## BGM — Kevin MacLeod (incompetech.com), CC BY 4.0\n영상 설명란에 이 줄을 넣는다(곡 이름만 바꿈):\n`Music: "<곡>" Kevin MacLeod (incompetech.com) · Licensed under Creative Commons: By Attribution 4.0 · http://creativecommons.org/licenses/by/4.0/`\n\n| mood | 곡 |\n|---|---|\n'+''.join(f'| {m} | {t} |\n' for m,t in BGM.items())+'\n## 효과음 — Kenney (kenney.nl), CC0 (출처 표기 불필요)\n'+''.join(f'- {k}.ogg ← {p}\n' for k,p in SFX.items()))
print(os.listdir('audio/bgm'),os.listdir('audio/sfx'))
