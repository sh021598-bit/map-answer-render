# 대본 → 음성 + 합성 배경음·효과음 + 덕킹 + -14 LUFS → final_audio.wav, data/timeline.json(단어 타이밍)
# python3 audio3d.py <영상설정.json> [음성폴더]   음성폴더(NN.wav, 대본 줄 순서)가 있으면 그걸 쓰고(Chatterbox 등), 없으면 Kokoro am_michael
import json,re,subprocess,sys,os,numpy as np,soundfile as sf
cfg=json.load(open(sys.argv[1])); VD=sys.argv[2] if len(sys.argv)>2 else None
SR=48000
def load(i,txt):
    if VD:
        a,sr=sf.read(f'{VD}/{i:02d}.wav',dtype='float32')
    else:
        from kokoro_onnx import Kokoro
        global K
        if 'K' not in globals(): K=Kokoro('models/kokoro-v1.0.onnx','models/voices-v1.0.bin')
        a,sr=K.create(txt,voice='am_michael',speed=1.04,lang='en-us')
    if a.ndim>1: a=a.mean(1)
    if sr!=SR: a=np.interp(np.arange(int(len(a)*SR/sr))*sr/SR,np.arange(len(a)),a).astype(np.float32)
    nz=np.where(np.abs(a)>0.02*np.abs(a).max())[0]; s0=max(0,nz[0]-480); return a[s0:nz[-1]+960],s0/SR
def syl(w): return max(1,len(re.findall(r'[aeiouy]+',w.lower())))+(3 if re.search(r'\d',w) else 0)
WH=json.load(open(f'{VD}/words.json')) if VD and os.path.exists(f'{VD}/words.json') else None
chunks=[];t=0.0;lines=[]
for i,ln in enumerate(cfg['lines']):
    sid,txt=ln[0],ln[1]; a,off=load(i,ln[2] if len(ln)>2 else txt); dur=len(a)/SR; words=txt.split(); wts=[syl(w)+0.3 for w in words]; tot=sum(wts); acc=t; ws=[]
    WJ=WH[i] if WH and len(WH[i])==len(words) else None   # Whisper 단어 타이밍(단어 수 일치할 때만)
    for k,(w,x) in enumerate(zip(words,wts)):
        if WJ: ws.append([w,round(t+max(0,WJ[k][1]-off),3),round(t+max(0,min(dur,WJ[k][2]-off)),3)]); continue
        d=dur*x/tot; ws.append([w,round(acc,3),round(acc+d,3)]); acc+=d
    lines.append(dict(scene=sid,text=txt,t0=round(t,3),t1=round(t+dur,3),words=ws))
    gap=0.12 if txt.endswith(',') else (0.35 if sid in('ask','end') else 0.22)
    nxt=cfg['lines'][i+1][0] if i+1<len(cfg['lines']) else None
    if nxt!=sid: gap+=cfg.get('hold',{}).get(sid,0)   # 장면 끝 여유(소품 연출 시간)
    chunks+=[a,np.zeros(int(gap*SR),np.float32)]; t+=dur+gap
chunks.append(np.zeros(int(1.2*SR),np.float32)); TOT=t+1.2
sf.write('voice_raw.wav',np.concatenate(chunks),SR)
# ---- music: synthesized cinematic pad (no licensing) ----
n=int(TOT*SR); tt=np.arange(n)/SR; mus=np.zeros(n)
def note(f): return 440*2**((f-69)/12)
prog=[[45,52,57,60,64],[41,48,53,57,60],[48,55,60,64,67],[43,50,55,59,62]]  # Am F C G
bar=4.0
for i in range(int(TOT/bar)+1):
    s=int(i*bar*SR); e=min(n,int((i+1)*bar*SR)+SR//2); seg=tt[s:e]-i*bar
    env=np.clip(seg/1.2,0,1)*np.clip((bar+0.5-seg)/0.8,0,1)
    for m in prog[i%4]:
        f=note(m); mus[s:e]+=env*(0.5*np.sin(2*np.pi*f*seg)+0.18*np.sin(2*np.pi*2*f*seg+0.3)+0.08*np.sin(2*np.pi*f*1.003*seg))/5
    for j in range(8):
        ps=s+int(j*0.5*SR); pe=min(n,ps+int(0.35*SR)); pt=(np.arange(max(0,pe-ps)))/SR
        mus[ps:pe]+=0.25*np.sin(2*np.pi*note(33+(0 if i%4!=1 else -4))*pt)*np.exp(-pt*9)
# ---- sfx: whoosh+impact at scene changes, plus prop cues (cfg 'sfx': [[scene, sec, kind]]) ----
sfx=np.zeros(n); rng=np.random.default_rng(3); T0={}
for L in lines: T0.setdefault(L['scene'],L['t0'])
def whoosh(st,g=0.5):
    a0=int(max(0,st-0.45)*SR); ln=min(int(0.55*SR),n-a0); x=rng.standard_normal(ln)
    for _ in range(3): x=np.convolve(x,np.ones(8)/8,'same')
    sfx[a0:a0+ln]+=x*np.sin(np.linspace(0,np.pi,ln))**2*g
def boom(st,f=55,g=0.6,dec=10):
    b0=int(st*SR); bl=min(int(0.5*SR),n-b0); bt=np.arange(bl)/SR; sfx[b0:b0+bl]+=g*np.sin(2*np.pi*f*bt)*np.exp(-bt*dec)
def pop(st,g=0.25):
    b0=int(st*SR); bl=min(int(0.12*SR),n-b0); bt=np.arange(bl)/SR; sfx[b0:b0+bl]+=g*np.sin(2*np.pi*(900-3000*bt)*bt)*np.exp(-bt*40)
def shot(st,g=0.3):
    b0=int(st*SR); bl=min(int(0.18*SR),n-b0); bt=np.arange(bl)/SR; x=rng.standard_normal(bl)
    sfx[b0:b0+bl]+=g*x*np.exp(-bt*35); boom(st,80,g*0.8,25)
for s in list(T0)[1:]: whoosh(T0[s]); boom(T0[s])
for sid,sec,kind in cfg.get('sfx',[]):
    st=T0[sid]+sec
    if kind=='pop': pop(st)
    elif kind=='boom': boom(st,45,0.7,6)
    elif kind=='volley':
        for q in range(6): shot(st+q*0.33+rng.uniform(0,0.12),0.22+0.08*rng.random())
    elif kind=='whoosh': whoosh(st,0.35)
sf.write('music.wav',(mus/np.max(np.abs(mus))*0.5).astype(np.float32),SR)
sf.write('sfx.wav',(sfx/max(1e-6,np.max(np.abs(sfx)))*0.5).astype(np.float32),SR)
VF=cfg.get('voice_fx',"highpass=f=75,equalizer=f=140:t=q:w=1:g=2,equalizer=f=3200:t=q:w=1.4:g=2,equalizer=f=7600:t=q:w=2:g=-2,acompressor=threshold=-20dB:ratio=3:attack=4:release=90:makeup=2,aecho=0.85:0.4:22|41:0.06|0.03")
fc=(f"[0:a]{VF},asplit=2[v][sc];[1:a]volume=0.32[m];[m][sc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=300[md];"
    f"[2:a]volume=0.35[s];[v][md][s]amix=inputs=3:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000,aformat=channel_layouts=stereo[out]")
subprocess.run(['ffmpeg','-y','-v','error','-i','voice_raw.wav','-i','music.wav','-i','sfx.wav','-filter_complex',fc,'-map','[out]','-ar','48000','final_audio.wav'],check=True)
json.dump(dict(total=round(TOT,3),lines=lines),open('data/timeline.json','w'),indent=0)
print('total',round(TOT,1))
