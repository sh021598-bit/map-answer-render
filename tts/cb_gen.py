# Chatterbox(MIT) 음성 생성: python cb_gen.py <config> <lines.json> <outdir>
# config: cb_<ref> (Chatterbox, ref/<ref>.wav 음색 복제) | cb_default | turbo_<ref>
import sys,json,os,time,torch,torchaudio as ta
_load=torch.load; torch.load=lambda *a,**k:_load(*a,**{**k,'map_location':'cpu'})
cfg,lines,out=sys.argv[1],json.load(open(sys.argv[2])),sys.argv[3]
if isinstance(lines,dict): lines=lines['lines']; os.makedirs(out,exist_ok=True)
kind,ref=cfg.split('_',1); ref=None if ref=='default' else f'ref/{ref}.wav'
if kind=='turbo':
    from chatterbox.tts_turbo import ChatterboxTurboTTS as M
else:
    from chatterbox.tts import ChatterboxTTS as M
m=M.from_pretrained(device='cpu'); t0=time.time()
for i,ln in enumerate(lines):
    sid,txt=ln[0],(ln[2] if len(ln)>2 else ln[1])   # 3번째 값 = 발음용 철자
    kw=dict(audio_prompt_path=ref) if ref else {}
    if kind=='cb': kw.update(exaggeration=0.55,cfg_weight=0.45)
    torch.manual_seed(7); w=m.generate(txt,**kw)
    ta.save(f'{out}/{i:02d}.wav',w,m.sr); print(cfg,i,round(time.time()-t0),'s',flush=True)
