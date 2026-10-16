# 지형 격자 생성: python3 prep3d.py <영상설정.json>   (작업 폴더에서 실행)
# 높이 = AWS Terrain Tiles(terrarium, z5; SRTM·ETOPO1 등 공개 데이터) → data/height.bin (float32, 계단 줄무늬 방지)
# 나라 ID·육지 마스크 = Natural Earth 50m → data/grid.png (G=ID*40, B=육지), data/coast.png, data/meta.json
import json,math,sys,io,os,urllib.request,numpy as np
from PIL import Image,ImageDraw,ImageFilter
cfg=json.load(open(sys.argv[1])); R=cfg['region']
LON0,LON1=R['lon']; LAT0,LAT1=R['lat']; NX=R.get('nx',560)
def my(lat): return math.degrees(math.log(math.tan(math.pi/4+math.radians(lat)/2)))
Y0,Y1=my(LAT0),my(LAT1); NY=int(NX*(Y1-Y0)/(LON1-LON0))
os.makedirs('data',exist_ok=True); os.makedirs('cache',exist_ok=True)
# ---- elevation mosaic (web mercator tiles) ----
Z=R.get('z',5); n=2**Z   # 작은 지역(섬 등)은 region.z 를 8~10 으로
tx=lambda lon:(lon+180)/360*n
ty=lambda lat:(1-math.log(math.tan(math.radians(lat))+1/math.cos(math.radians(lat)))/math.pi)/2*n
x0,x1=int(tx(LON0)),int(tx(LON1)); y0,y1=int(ty(LAT1)),int(ty(LAT0))
mos=np.zeros(((y1-y0+1)*256,(x1-x0+1)*256),np.float32)
for X in range(x0,x1+1):
    for Y in range(y0,y1+1):
        f=f'cache/t{Z}_{X}_{Y}.png'
        if not os.path.exists(f): urllib.request.urlretrieve(f'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{Z}/{X}/{Y}.png',f)
        a=np.asarray(Image.open(f).convert('RGB')).astype(np.float32)
        mos[(Y-y0)*256:(Y-y0+1)*256,(X-x0)*256:(X-x0+1)*256]=a[...,0]*256+a[...,1]+a[...,2]/256-32768
xs=np.linspace(LON0,LON1,NX); ys=np.linspace(Y1,Y0,NY)
lats=np.degrees(2*np.arctan(np.exp(np.radians(ys)))-math.pi/2)
U=np.broadcast_to(((xs+180)/360*n-x0)*256,(NY,NX)); V=np.broadcast_to(np.array([(ty(l)-y0)*256 for l in lats])[:,None],(NY,NX))
u0=np.clip(np.floor(U).astype(int),0,mos.shape[1]-2); v0=np.clip(np.floor(V).astype(int),0,mos.shape[0]-2); fu=U-u0; fv=V-v0
elev=(mos[v0,u0]*(1-fu)*(1-fv)+mos[v0,u0+1]*fu*(1-fv)+mos[v0+1,u0]*(1-fu)*fv+mos[v0+1,u0+1]*fu*fv)
def blur(a,s):  # separable gaussian in float
    r=int(3*s); k=np.exp(-np.arange(-r,r+1)**2/(2*s*s)); k/=k.sum()
    a=np.apply_along_axis(lambda v:np.convolve(np.pad(v,r,mode='edge'),k,'valid'),1,a)
    return np.apply_along_axis(lambda v:np.convolve(np.pad(v,r,mode='edge'),k,'valid'),0,a)
h=blur(np.clip(elev,0,None)/7000,R.get('smooth',1.0)).astype(np.float32)
h.tofile('data/height.bin')
# ---- countries ----
G={}
for f in json.load(open('world50.json'))['features']: G[f['properties']['ADMIN']]=f['geometry']
def P(lon,lat): return ((lon-LON0)/(LON1-LON0)*(NX-1),(Y1-my(lat))/(Y1-Y0)*(NY-1))
def polys(g): return [g['coordinates']] if g['type']=='Polygon' else g['coordinates']
IDS={};OWN={}
for i,(k,c) in enumerate(cfg['countries'].items(),1):
    for a in ([c['admin']] if isinstance(c['admin'],str) else c['admin']): IDS[a]=i; OWN[a]=k
idm=Image.new('L',(NX,NY),0); land=Image.new('L',(NX,NY),0); di=ImageDraw.Draw(idm); dl=ImageDraw.Draw(land)
for nm,g in G.items():
    for p in polys(g):
        pts=[P(*c) for c in p[0]]
        if max(x for x,_ in pts)<-5 or min(x for x,_ in pts)>NX+5: continue
        dl.polygon(pts,fill=255)
        if nm in IDS: di.polygon(pts,fill=IDS[nm]*40)
if R.get('land')=='elev':   # Natural Earth 에 없는 작은 섬: 고도>0 을 육지로, 나라는 경도 split 으로 나눔
    lm_=(elev>R.get('sea',1.0)).astype(np.uint8)*255; land=Image.fromarray(lm_)
    sp=R.get('split'); ida=np.zeros((NY,NX),np.uint8)
    if sp:
        ki={k:i for i,k in enumerate(cfg['countries'],1)}; west=(xs[None,:]<sp['lon']).repeat(NY,0)
        ida[(lm_>0)&west]=ki[sp['west']]*40; ida[(lm_>0)&~west]=ki[sp['east']]*40
    idm=Image.fromarray(ida)
landf=np.asarray(land.filter(ImageFilter.GaussianBlur(1.2))).astype(np.float32)/255
coast=np.asarray(land.filter(ImageFilter.GaussianBlur(10))).astype(np.float32)/255
out=np.stack([np.zeros_like(landf),np.asarray(idm),landf*255],-1).astype(np.uint8)
Image.fromarray(out).save('data/grid.png')
Image.fromarray((coast*255).astype(np.uint8)).save('data/coast.png')
outl={}
for nm,k in OWN.items():
    if R.get('land')=='elev': outl.setdefault(k,[]); continue
    outl.setdefault(k,[]).extend([[list(map(lambda v:round(v,2),P(*c))) for c in p[0]] for p in polys(G[nm]) if len(p[0])>8])
json.dump(dict(NX=NX,NY=NY,LON0=LON0,LON1=LON1,Y0=Y0,Y1=Y1,ids={k:i for i,k in enumerate(cfg['countries'],1)},outlines=outl),open('data/meta.json','w'))
print(NX,NY,float(h.max())*7000)
# ---- 세계 배경 (지역 바깥 전체, 메르카토르, 경도는 지역 중심 ±180°): 지역 지형과 같은 색 + 음영. 지구본으로 말았다 펴는 데 쓴다 ----
LC=(LON0+LON1)/2; WW=4096; YM=208.6; WH=int(WW*2*YM/360)        # 위도 ±87°
Z3=3; n3=2**Z3; m3=np.zeros((n3*256,n3*256),np.float32)
for X in range(n3):
    for Y in range(n3):
        f=f'cache/t{Z3}_{X}_{Y}.png'
        if not os.path.exists(f): urllib.request.urlretrieve(f'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{Z3}/{X}/{Y}.png',f)
        a=np.asarray(Image.open(f).convert('RGB')).astype(np.float32); m3[Y*256:(Y+1)*256,X*256:(X+1)*256]=a[...,0]*256+a[...,1]+a[...,2]/256-32768
wl=(LC-180+np.arange(WW)/WW*360+180)%360-180; wy=YM-np.arange(WH)/WH*2*YM
ci=((wl+180)/360*m3.shape[1]).astype(int)%m3.shape[1]; ri=np.clip(((1-np.radians(wy)/math.pi)/2*m3.shape[0]).astype(int),0,m3.shape[0]-1)
we=m3[ri[:,None],ci[None,:]]
def wpt(lon,lat): return ((lon-(LC-180))/360*WW,(YM-my(lat))/(2*YM)*WH)
lm=Image.new('L',(WW,WH),0); ld=ImageDraw.Draw(lm); mk=Image.new('RGB',(WW,WH),(0,0,0)); md=ImageDraw.Draw(mk)
keys=list(cfg['countries'].keys())[:3]
for nm,g in G.items():
    for p in polys(g):
        for sh in (-360,0,360):
            pts=[wpt(lo+sh,max(-87,min(87,la))) for lo,la in p[0]]
            if max(x for x,_ in pts)<0 or min(x for x,_ in pts)>WW: continue
            ld.polygon(pts,fill=255)
            if nm in OWN and OWN[nm] in keys: md.polygon(pts,fill=tuple(255 if keys.index(OWN[nm])==c else 0 for c in range(3)))
landw=np.asarray(lm).astype(np.float32)/255
cw=np.asarray(lm.filter(ImageFilter.GaussianBlur(12))).astype(np.float32)/255
hw=np.clip(we,0,None)/7000; gyy,gxx=np.gradient(hw); shade=np.clip(1+(-gxx-gyy)*60,0.75,1.25)
hx=lambda h:np.array([int(h[i:i+2],16) for i in (1,3,5)],np.float32)
L1,L2,L3,SD,SS=hx('#d8cdb8'),hx('#c2b49a'),hx('#efe9df'),hx('#0b1b33'),hx('#1d4f7a')
hh=np.clip(hw*1.3,0,1)[...,None]
landc=(L1+(L2-L1)*np.clip(hh*2,0,1)); landc=landc+(L3-landc)*np.clip((hh-0.45)*2,0,1); landc=landc*shade[...,None]
seac=SD+(SS-SD)*(cw[...,None]*0.9)
img=seac*(1-landw[...,None])+landc*landw[...,None]
Image.fromarray(np.clip(img,0,255).astype(np.uint8)).save('data/world.jpg',quality=92)
mk.save('data/worldmask.png'); lm.filter(ImageFilter.GaussianBlur(2)).save('data/worldland.png')
mm=json.load(open('data/meta.json')); mm.update(LC=LC,WYM=YM,wkeys=keys); json.dump(mm,open('data/meta.json','w'))
