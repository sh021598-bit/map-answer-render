// 소품 라이브러리: 영상 설정 "props" 의 type 별로 3D 클레이 소품을 만들고 매 프레임 움직인다.
// 새 소재에 필요한 연출은 여기에 type 을 추가하고, 영상 설정에서 장면·좌표·시간만 지정한다.
import {FontLoader} from 'three/addons/loaders/FontLoader.js';
import {TextGeometry} from 'three/addons/geometries/TextGeometry.js';
import {RoundedBoxGeometry} from 'three/addons/geometries/RoundedBoxGeometry.js';
const RB=(w,h,d,r)=>new RoundedBoxGeometry(w,h,d,3,Math.min(w,h,d)*r);
export async function makeProps(X){
const {ENV,THREE,scene,CFG,meta,cid,ll2w,ll2g,g2w,heightAt,groundAtW,bigRing,ease,cur}=X;
const C=c=>new THREE.Color(c);
// 재질: 무광 비닐 피규어 느낌(약한 sheen·clearcoat). 금속은 metal().
const clay=(c,o={})=>new THREE.MeshPhysicalMaterial({envMap:ENV,envMapIntensity:0.45,color:C(c),roughness:0.55,metalness:0,sheen:0.35,sheenRoughness:0.6,sheenColor:C('#ffffff'),clearcoat:0.15,clearcoatRoughness:0.5,...o});
const metal=(c,r=0.3)=>new THREE.MeshPhysicalMaterial({envMap:ENV,envMapIntensity:1,color:C(c),roughness:r,metalness:1,clearcoat:0.3});
const glow=c=>new THREE.MeshBasicMaterial({color:C(c),toneMapped:false,transparent:true});
const mesh=(g,m,o={})=>{const x=new THREE.Mesh(g,m);x.castShadow=true;x.receiveShadow=true;Object.assign(x.position,o);return x};
const clamp01=v=>v<0?0:v>1?1:v;
const popS=u=>{u=clamp01(u);return u<=0?0.0001:1+Math.sin(u*Math.PI)*0.35*(1-u)+(1-Math.pow(1-u,3))-1};
const rnd=s=>{const x=Math.sin(s*127.1+311.7)*43758.5453;return x-Math.floor(x)};
const W=([lo,la])=>{const [x,z]=ll2w(lo,la);return new THREE.Vector3(x,0,z)};
// ---- flag textures ----
function flagTex(kind){const c=document.createElement('canvas');c.width=192;c.height=128;const g=c.getContext('2d');
  const bands=(cols)=>cols.forEach((k,i)=>{g.fillStyle=k;g.fillRect(0,i*128/cols.length,192,128/cols.length+1)});
  if(kind==='chile'){g.fillStyle='#fff';g.fillRect(0,0,192,64);g.fillStyle='#d52b1e';g.fillRect(0,64,192,64);g.fillStyle='#0039a6';g.fillRect(0,0,64,64);
    g.fillStyle='#fff';g.beginPath();for(let i=0;i<10;i++){const a=-Math.PI/2+i*Math.PI/5,rr=i%2?7:17;g.lineTo(32+rr*Math.cos(a),32+rr*Math.sin(a))}g.fill()}
  else if(kind==='bolivia') bands(['#d52b1e','#f9e300','#007934']);
  else if(kind==='peru'){g.fillStyle='#d91023';g.fillRect(0,0,192,128);g.fillStyle='#fff';g.fillRect(64,0,64,128)}
  else if(kind==='argentina'){bands(['#74acdf','#fff','#74acdf']);g.fillStyle='#f6b40e';g.beginPath();g.arc(96,64,13,0,7);g.fill()}
  else if(kind==='denmark'){g.fillStyle='#c8102e';g.fillRect(0,0,192,128);g.fillStyle='#fff';g.fillRect(56,0,24,128);g.fillRect(0,52,192,24)}
  else if(kind==='russia') bands(['#ffffff','#0039a6','#d52b1e']);
  else if(kind==='ussr'){g.fillStyle='#cc0000';g.fillRect(0,0,192,128);g.fillStyle='#ffd700';g.beginPath();for(let i=0;i<10;i++){const a=-Math.PI/2+i*Math.PI/5,rr=i%2?4:10;g.lineTo(34+rr*Math.cos(a),22+rr*Math.sin(a))}g.fill();
    g.strokeStyle='#ffd700';g.lineWidth=5;g.beginPath();g.arc(36,52,12,0.3,Math.PI*1.25);g.stroke();g.beginPath();g.moveTo(26,64);g.lineTo(46,42);g.stroke()}
  else if(kind==='usa'){for(let i=0;i<13;i++){g.fillStyle=i%2?'#fff':'#b22234';g.fillRect(0,i*128/13,192,128/13+1)}g.fillStyle='#3c3b6e';g.fillRect(0,0,80,69);
    g.fillStyle='#fff';for(let y=0;y<5;y++)for(let x=0;x<6;x++){g.beginPath();g.arc(8+x*13+(y%2)*6,8+y*13,2.6,0,7);g.fill()}}
  else if(kind==='uk'){g.fillStyle='#012169';g.fillRect(0,0,192,128);g.strokeStyle='#fff';g.lineWidth=24;g.beginPath();g.moveTo(0,0);g.lineTo(192,128);g.moveTo(192,0);g.lineTo(0,128);g.stroke();
    g.strokeStyle='#c8102e';g.lineWidth=8;g.stroke();g.strokeStyle='#fff';g.lineWidth=36;g.beginPath();g.moveTo(96,0);g.lineTo(96,128);g.moveTo(0,64);g.lineTo(192,64);g.stroke();g.strokeStyle='#c8102e';g.lineWidth=20;g.stroke()}
  else {g.fillStyle=kind;g.fillRect(0,0,192,128)}
  // 천 질감: 은은한 세로 주름 음영
  const gr=g.createLinearGradient(0,0,192,0);for(let i=0;i<=6;i++)gr.addColorStop(i/6,i%2?'rgba(0,0,0,0.10)':'rgba(255,255,255,0.06)');g.fillStyle=gr;g.fillRect(0,0,192,128);
  const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;return t}
function makeFlag(kind,sz=1){const grp=new THREE.Group();
  grp.add(mesh(new THREE.CylinderGeometry(0.0045*sz,0.0055*sz,0.27*sz,12),metal('#b9b2a6',0.35),{y:0.135*sz}));
  grp.add(mesh(new THREE.SphereGeometry(0.009*sz,16,12),metal('#e8b84a',0.25),{y:0.274*sz}));
  grp.add(mesh(new THREE.CylinderGeometry(0.018*sz,0.022*sz,0.008*sz,20),clay('#3b3632'),{y:0.004*sz}));
  const fg=new THREE.PlaneGeometry(0.16*sz,0.105*sz,24,8);fg.translate(0.08*sz,0,0);
  const f=mesh(fg,new THREE.MeshPhysicalMaterial({envMap:ENV,envMapIntensity:0.5,map:flagTex(kind),side:THREE.DoubleSide,roughness:0.8,sheen:0.6,sheenRoughness:0.5,sheenColor:C('#ffffff')}),{x:0.004*sz,y:0.215*sz});
  f.userData.x0=Float32Array.from(fg.attributes.position.array);grp.add(f);grp.userData.cloth=f;grp.userData.sz=sz;return grp}
function wave(fl,t){const f=fl.userData.cloth,p=f.geometry.attributes.position,a=p.array,x0=f.userData.x0,sz=fl.userData.sz;
  for(let i=0;i<p.count;i++){const x=x0[i*3],y=x0[i*3+1],k=x/(0.16*sz);a[i*3+2]=(Math.sin(x/sz*34-t*6+y/sz*8)*0.011+Math.sin(x/sz*61-t*9)*0.004)*sz*k;a[i*3+1]=y-k*k*0.008*sz}
  p.needsUpdate=true;f.geometry.computeVertexNormals()}
// ---- soldiers: 다리·팔·벨트·모자 챙·배낭이 있는 미니어처 병사 ----
function makeSoldier(color,sz=1){const g=new THREE.Group();const m=clay(color),dark=clay('#232733'),skin=clay('#eebf98'),belt=clay('#f2ead8'),wood=clay('#5a3b25');
  const legs=[];for(const z of [-0.0085,0.0085]){const L=new THREE.Group();L.position.set(0,0.042*sz,z*sz);L.add(mesh(new THREE.CapsuleGeometry(0.0075*sz,0.028*sz,4,10),dark,{y:-0.02*sz}));
    L.add(mesh(RB(0.02*sz,0.009*sz,0.013*sz,0.4),clay('#15171c'),{x:0.004*sz,y:-0.04*sz}));g.add(L);legs.push(L)}
  g.add(mesh(new THREE.CapsuleGeometry(0.017*sz,0.026*sz,6,14),m,{y:0.066*sz}));
  const bt=mesh(new THREE.TorusGeometry(0.0172*sz,0.0028*sz,6,24),belt,{y:0.056*sz});bt.rotation.x=Math.PI/2;g.add(bt);
  g.add(mesh(RB(0.016*sz,0.026*sz,0.026*sz,0.3),clay('#6d5a3e'),{x:-0.019*sz,y:0.07*sz}));
  g.add(mesh(new THREE.SphereGeometry(0.0145*sz,20,16),skin,{y:0.104*sz}));
  g.add(mesh(new THREE.CylinderGeometry(0.0125*sz,0.0145*sz,0.017*sz,20),m,{y:0.119*sz}));
  g.add(mesh(new THREE.CylinderGeometry(0.0135*sz,0.0135*sz,0.003*sz,20),dark,{y:0.128*sz}));
  const visor=mesh(new THREE.CylinderGeometry(0.009*sz,0.009*sz,0.002*sz,16,1,false,-Math.PI/2,Math.PI),dark,{x:0.011*sz,y:0.111*sz});g.add(visor);
  const arm=new THREE.Group();arm.position.set(0.004*sz,0.083*sz,0);arm.add(mesh(new THREE.CapsuleGeometry(0.0062*sz,0.02*sz,4,8),m,{x:0.008*sz,y:-0.01*sz,z:0.016*sz}));
  const gun=new THREE.Group();gun.add(mesh(RB(0.06*sz,0.0055*sz,0.0055*sz,0.3),wood,{x:0.012*sz}));gun.add(mesh(new THREE.CylinderGeometry(0.0018*sz,0.0018*sz,0.03*sz,8),metal('#3d3f44'),{x:0.055*sz}));
  gun.children[1].rotation.z=Math.PI/2;gun.position.set(0.012*sz,-0.012*sz,0.012*sz);arm.add(gun);g.add(arm);
  g.userData.gun=arm;g.userData.legs=legs;return g}
// ---- car ----
function makeCar(color,sz=1){const g=new THREE.Group();
  g.add(mesh(RB(0.1*sz,0.03*sz,0.054*sz,0.35),clay(color,{clearcoat:0.8,clearcoatRoughness:0.15,roughness:0.35}),{y:0.03*sz}));
  g.add(mesh(RB(0.056*sz,0.026*sz,0.046*sz,0.4),clay(color,{clearcoat:0.8,clearcoatRoughness:0.15,roughness:0.35}),{x:-0.006*sz,y:0.054*sz}));
  g.add(mesh(RB(0.058*sz,0.018*sz,0.048*sz,0.4),new THREE.MeshPhysicalMaterial({color:C('#1c2a3a'),roughness:0.1,metalness:0.2,clearcoat:1}),{x:-0.006*sz,y:0.056*sz}));
  for(const z of [-0.018,0.018]){g.add(mesh(new THREE.SphereGeometry(0.0055*sz,12,8),new THREE.MeshBasicMaterial({color:C('#fff4d0'),toneMapped:false}),{x:0.05*sz,y:0.032*sz,z:z*sz}))}
  for(const [x,z] of [[0.03,0.027],[-0.03,0.027],[0.03,-0.027],[-0.03,-0.027]]){const w=new THREE.Group();w.position.set(x*sz,0.014*sz,z*sz);
    const tire=mesh(new THREE.TorusGeometry(0.0095*sz,0.005*sz,10,20),clay('#17171a',{roughness:0.9}));w.add(tire);w.add(mesh(new THREE.CylinderGeometry(0.007*sz,0.007*sz,0.008*sz,16),metal('#c9ccd2'),{}));w.children[1].rotation.x=Math.PI/2;g.add(w)}
  return g}
function trailTube(pts,color,r=0.014){const curve=new THREE.CatmullRomCurve3(pts,false,'centripetal',0.3);
  const tg=new THREE.TubeGeometry(curve,Math.max(24,pts.length*3),r,6,false);const m=new THREE.Mesh(tg,glow(color));m.userData.curve=curve;m.userData.total=tg.index.count;tg.setDrawRange(0,0);return m}
const reveal=(m,f)=>{const n=m.userData.total, seg=6*6;m.geometry.setDrawRange(0,Math.floor(clamp01(f)*n/seg)*seg)};
// spine of a country: centre line north→south
function spine(key){const id=meta.ids[key];const out=[];for(let gy=0;gy<meta.NY;gy+=8){let sx=0,c=0;for(let gx=0;gx<meta.NX;gx++){if(cid[gy*meta.NX+gx]===id){sx+=gx;c++}}
  if(c>2){const [x,z]=g2w(sx/c,gy);out.push(new THREE.Vector3(x,heightAt(sx/c,gy)+0.03,z))}}return out}
// shared border between two countries (ordered north→south)
function shared(a,b,southOf){const A=bigRing(a),Bp=bigRing(b);const out=[];
  for(const [gx,gy] of A){let best=1e9;for(const [hx,hy] of Bp){const d=(gx-hx)**2+(gy-hy)**2;if(d<best)best=d}if(best<4) out.push([gx,gy])}
  out.sort((p,q)=>p[1]-q[1]);const lim=southOf!==undefined?ll2g(-60,southOf)[1]:-1;
  const f=[];for(const p of out){if(p[1]<lim)continue;if(!f.length||Math.hypot(p[0]-f[f.length-1][0],p[1]-f[f.length-1][1])>3)f.push(p)}
  return f.map(([gx,gy])=>{const [x,z]=g2w(gx,gy);return new THREE.Vector3(x,heightAt(gx,gy),z)})}
let font=null;
const items=[];
for(const p of CFG.props){const it={p,root:new THREE.Group()};it.root.visible=false;scene.add(it.root);items.push(it);const sz=p.size||1;
  switch(p.type){
  case 'drive':{const pts=String(p.path).startsWith('spine:')?spine(p.path.split(':')[1]):p.path.map(q=>{const v=W(q);v.y=groundAtW(v.x,v.z)+0.03;return v});
    it.trail=trailTube(pts,p.color,0.016*sz);it.root.add(it.trail);it.car=makeCar(p.color,(p.car||2.2)*sz);it.root.add(it.car);break}
  case 'trace':{const pts=bigRing(p.country).filter((_,k)=>k%2==0).map(([gx,gy])=>{const [x,z]=g2w(gx,gy);return new THREE.Vector3(x,heightAt(gx,gy)+0.03,z)});
    it.trail=trailTube(pts,p.color||'#ffc83d',0.02*sz);it.root.add(it.trail);break}
  case 'qmark':{if(!font)font=await new FontLoader().loadAsync('node_modules/three/examples/fonts/helvetiker_bold.typeface.json');
    const g=new TextGeometry('?',{font,size:0.9*sz,depth:0.22*sz,bevelEnabled:true,bevelSize:0.03*sz,bevelThickness:0.04*sz,curveSegments:8});g.center();
    it.q=mesh(g,clay('#ffc83d',{emissive:C('#3a2600')}));it.q.castShadow=false;it.root.add(it.q);break}
  case 'houses':{const roofs=['#c8553d','#b84a36','#d0663f'],walls=['#f4ede0','#efe2c8','#f6efe6'];
    it.h=p.at.map((q,k)=>{const g=new THREE.Group();const s=0.05*sz;
      g.add(mesh(RB(s,s*0.75,s*0.85,0.12),clay(walls[k%3]),{y:s*0.375}));
      const sh=new THREE.Shape();sh.moveTo(-s*0.58,0);sh.lineTo(0,s*0.42);sh.lineTo(s*0.58,0);sh.lineTo(-s*0.58,0);
      const rg=new THREE.ExtrudeGeometry(sh,{depth:s*0.98,bevelEnabled:true,bevelSize:s*0.03,bevelThickness:s*0.03,bevelSegments:2});rg.translate(0,0,-s*0.49);
      g.add(mesh(rg,clay(roofs[k%3]),{y:s*0.74}));
      g.add(mesh(RB(s*0.2,s*0.34,s*0.02,0.2),clay('#6b4426'),{x:-s*0.15,y:s*0.17,z:s*0.43}));
      g.add(mesh(RB(s*0.18,s*0.16,s*0.02,0.2),new THREE.MeshPhysicalMaterial({color:C('#ffdc8a'),emissive:C('#7a4a10'),roughness:0.3}),{x:s*0.2,y:s*0.42,z:s*0.43}));
      g.add(mesh(RB(s*0.12,s*0.25,s*0.12,0.2),clay('#a89a88'),{x:s*0.25,y:s*1.0}));
      g.rotation.y=rnd(k)*1.2-0.6;const v=W(q);g.position.copy(v);g.userData.v=v;it.root.add(g);return g});break}
  case 'ship':{const g=new THREE.Group();const s=sz;
    const hs=new THREE.Shape();hs.moveTo(-0.085*s,0.045*s);hs.quadraticCurveTo(-0.08*s,0.0,-0.04*s,-0.005*s);hs.lineTo(0.05*s,-0.005*s);hs.quadraticCurveTo(0.085*s,0.005*s,0.1*s,0.04*s);hs.lineTo(-0.085*s,0.045*s);
    const hg=new THREE.ExtrudeGeometry(hs,{depth:0.05*s,bevelEnabled:true,bevelSize:0.008*s,bevelThickness:0.008*s,bevelSegments:3,curveSegments:12});hg.translate(0,0,-0.025*s);
    g.add(mesh(hg,clay('#6b4426',{roughness:0.7}),{y:0.0}));
    g.add(mesh(RB(0.17*s,0.006*s,0.052*s,0.3),clay('#c9a46a'),{x:0.005*s,y:0.046*s}));
    g.add(mesh(RB(0.04*s,0.03*s,0.054*s,0.2),clay('#5a3820'),{x:-0.065*s,y:0.062*s}));
    for(const [x,h,w] of [[0.035,0.19,0.085],[-0.02,0.16,0.07]]){g.add(mesh(new THREE.CylinderGeometry(0.0028*s,0.0035*s,h*s,10),clay('#3a2a1e'),{x:x*s,y:h*s/2+0.045*s}));
      for(const [yy,hh] of [[0.45,0.36],[0.82,0.24]]){const sg=new THREE.CylinderGeometry(w*s*0.75,w*s*0.75,hh*h*s,16,1,true,-0.55,1.1);
        const sail=mesh(sg,clay('#f3ead6',{side:THREE.DoubleSide,roughness:0.8}),{x:x*s-w*s*0.62,y:0.045*s+yy*h*s});g.add(sail)}}
    const fl=makeFlag(p.flag||'#c60b1e',0.45*s);fl.position.set(0.035*s,0.2*s,0);g.add(fl);it.fl=fl;
    it.ship=g;it.root.add(g);it.a=W(p.path[0]);it.b=W(p.path[1]);break}
  case 'crest':case 'pen':{const pts=shared(p.between[0],p.between[1],p.south_of);it.pts=pts;
    it.trail=trailTube(pts.map(v=>new THREE.Vector3(v.x,v.y,v.z)),p.color,0.016*sz);it.root.add(it.trail);
    if(p.type==='pen'){const pen=new THREE.Group();pen.add(mesh(new THREE.CylinderGeometry(0.02*sz,0.02*sz,0.3*sz,10),clay('#1d2433'),{y:0.2*sz}));
      pen.add(mesh(new THREE.ConeGeometry(0.02*sz,0.05*sz,10),clay('#ffc83d'),{y:0.025*sz}));pen.children[1].rotation.x=Math.PI;
      pen.add(mesh(new THREE.CylinderGeometry(0.021*sz,0.021*sz,0.03*sz,10),clay('#ffc83d'),{y:0.33*sz}));pen.rotation.z=-0.35;pen.traverse(o=>o.castShadow=false);it.pen=pen;it.root.add(pen)}
    break}
  case 'army':{it.men=[];const fw=W(p.from),tw=W(p.to);it.fw=fw;it.tw=tw;const dir=tw.clone().sub(fw).normalize();const side=new THREE.Vector3(-dir.z,0,dir.x);it.dir=dir;
    const sp=0.075*sz;for(let r_=0;r_<p.rows;r_++)for(let c=0;c<p.cols;c++){const m=makeSoldier(p.color,(p.man||1.15)*sz);
      m.userData.off=side.clone().multiplyScalar((c-(p.cols-1)/2)*sp).add(dir.clone().multiplyScalar(-r_*sp));m.userData.ph=rnd(r_*7+c)*6;it.men.push(m);it.root.add(m)}
    if(p.flag){it.fl=makeFlag(p.flag,1.3*sz);it.fl.userData.off=dir.clone().multiplyScalar(sp*1.1).add(side.clone().multiplyScalar(-sp*0.6));it.root.add(it.fl)}
    it.yaw=Math.atan2(-dir.z,dir.x);break}
  case 'clash':{it.c=W(p.at);it.fx=[];const smokeM=new THREE.MeshStandardMaterial({color:C('#e4ddd2'),roughness:1,transparent:true,depthWrite:false});
    for(let k=0;k<44;k++){const isF=k<16;
      const m=isF?new THREE.Mesh(new THREE.OctahedronGeometry(0.012,0),glow(k%3?'#ffe08a':'#ff8a3d')):new THREE.Mesh(new THREE.IcosahedronGeometry(0.022,2),smokeM.clone());
      m.userData={isF,k};m.castShadow=false;it.fx.push(m);it.root.add(m)}break}
  case 'flagswap':{it.lost=makeFlag(p.lost,1.6*sz);it.won=makeFlag(p.won,1.6*sz);it.v=W(p.at);it.root.add(it.lost,it.won);break}
  case 'flags':{it.f=p.at.map(q=>{const f=makeFlag(p.flag,1.5*sz);f.userData.v=W(q);it.root.add(f);return f});break}
  case 'sheep':{it.sh=[];const c=W(p.at);const wool=clay('#e9e3d6',{roughness:0.95,sheen:0.25,sheenRoughness:0.9,clearcoat:0}),face=clay('#2a2522');
    for(let k=0;k<p.n;k++){const g=new THREE.Group();const s=sz*1.2;
      for(let q=0;q<11;q++){const a=q/11*6.28;g.add(mesh(new THREE.SphereGeometry((0.012+0.004*rnd(q+k))*s,14,10),wool,{x:Math.cos(a)*0.016*s,y:(0.032+0.008*Math.sin(a*2))*s+(q%2)*0.006*s,z:Math.sin(a)*0.011*s}))}
      g.add(mesh(new THREE.SphereGeometry(0.02*s,16,12),wool,{y:0.036*s}));
      const hd=mesh(new THREE.SphereGeometry(0.0105*s,16,12),face,{x:0.03*s,y:0.042*s});hd.scale.set(1.2,1,0.85);g.add(hd);
      for(const z of [-0.008,0.008]){const e=mesh(new THREE.SphereGeometry(0.0045*s,10,8),face,{x:0.027*s,y:0.05*s,z:z*s});e.scale.set(0.6,0.5,1.4);g.add(e)}
      for(const [x,z] of [[0.012,0.008],[-0.012,0.008],[0.012,-0.008],[-0.012,-0.008]]) g.add(mesh(new THREE.CapsuleGeometry(0.003*s,0.012*s,3,8),face,{x:x*s,y:0.009*s,z:z*s}));
      const a=rnd(k)*6.28,rr=0.08+0.3*rnd(k+9);g.userData={c:new THREE.Vector3(c.x+Math.cos(a)*rr,0,c.z+Math.sin(a)*rr*0.7),ph:rnd(k+3)*6,dir:rnd(k+5)*6.28};it.sh.push(g);it.root.add(g)}break}
  case 'otters':{it.o=[];const c=W(p.at);const fur=clay('#7a5236',{roughness:0.75,sheen:0.6,sheenColor:C('#d9b48a')}),pale=clay('#e3cfae'),dark=clay('#1a1412');
    for(let k=0;k<p.n;k++){const g=new THREE.Group();const s=sz;   // 해달: 배를 위로 하고 떠 있는 자세
      const body=mesh(new THREE.SphereGeometry(0.02*s,20,14),fur);body.scale.set(1.6,0.6,0.85);g.add(body);
      const belly=mesh(new THREE.SphereGeometry(0.016*s,18,12),pale,{y:0.006*s});belly.scale.set(1.5,0.45,0.75);g.add(belly);
      const hd=mesh(new THREE.SphereGeometry(0.0125*s,18,14),pale,{x:0.036*s,y:0.01*s});g.add(hd);
      for(const z of [-0.0045,0.0045])g.add(mesh(new THREE.SphereGeometry(0.0018*s,8,6),dark,{x:0.045*s,y:0.016*s,z:z*s}));
      g.add(mesh(new THREE.SphereGeometry(0.0025*s,8,6),dark,{x:0.048*s,y:0.011*s}));
      for(const z of [-0.008,0.008])g.add(mesh(new THREE.SphereGeometry(0.005*s,10,8),fur,{x:0.018*s,y:0.014*s,z:z*s}));
      const tail=mesh(new THREE.CapsuleGeometry(0.005*s,0.022*s,4,8),fur,{x:-0.038*s,y:0.002*s});tail.rotation.z=Math.PI/2;g.add(tail);
      const a=rnd(k+1)*6.28,rr=0.05+0.4*rnd(k+7);g.userData={v:new THREE.Vector3(c.x+Math.cos(a)*rr,0,c.z+Math.sin(a)*rr*0.6),ph:rnd(k)*6,yaw:rnd(k+2)*6.28,out:p.vanish?p.vanish[0]+(p.vanish[1]-p.vanish[0])*rnd(k+11):1e9};
      it.o.push(g);it.root.add(g)}break}
  case 'coins':{it.c=[];const gold=metal('#e8b84a',0.28);const A=W(p.src),B=W(p.dst);it.A=A;it.B=B;
    for(let k=0;k<p.n;k++){const m=mesh(new THREE.CylinderGeometry(0.03*sz,0.03*sz,0.007*sz,28),gold);m.userData.k=k;it.c.push(m);it.root.add(m)}
    it.pile=new THREE.Group();for(let k=0;k<26;k++){const m=mesh(new THREE.CylinderGeometry(0.03*sz,0.03*sz,0.007*sz,28),gold,{x:(rnd(k)-0.5)*0.08*sz,y:k*0.0045*sz,z:(rnd(k+5)-0.5)*0.08*sz});m.rotation.set((rnd(k+9)-0.5)*0.5,0,(rnd(k+3)-0.5)*0.5);it.pile.add(m)}
    it.root.add(it.pile);break}
  case 'pumpjacks':{it.pj=p.at.map((q,k)=>{const g=new THREE.Group();const s=sz;const steel=clay('#2b2f36'),y=clay('#ffc83d');
      g.add(mesh(RB(0.14*s,0.012*s,0.05*s,0.3),clay('#5d5850'),{y:0.006*s}));
      for(const z of [-0.015,0.015]){const l=mesh(new THREE.CylinderGeometry(0.003*s,0.004*s,0.1*s,8),steel,{x:0,y:0.055*s,z:z*s});l.rotation.x=z>0?-0.25:0.25;g.add(l)}
      const beam=new THREE.Group();beam.position.y=0.1*s;beam.add(mesh(RB(0.16*s,0.012*s,0.012*s,0.3),y));
      const head=mesh(new THREE.CylinderGeometry(0.022*s,0.022*s,0.014*s,20,1,false,0,Math.PI),y,{x:0.08*s});head.rotation.x=Math.PI/2;head.rotation.z=-Math.PI/2;beam.add(head);g.add(beam);
      g.add(mesh(new THREE.CylinderGeometry(0.0025*s,0.0025*s,0.06*s,8),steel,{x:0.095*s,y:0.04*s}));
      g.add(mesh(RB(0.03*s,0.03*s,0.03*s,0.3),clay('#b03a2e'),{x:-0.06*s,y:0.035*s}));
      const v=W(q);g.userData={v,beam,ph:k*1.3};g.rotation.y=k*0.7;it.root.add(g);return g});break}
  case 'nuggets':{it.n=p.at.map((q,k)=>{const g=new THREE.Group();const gold=metal('#f2c14e',0.22);
      for(let j=0;j<5;j++){const m=mesh(new THREE.DodecahedronGeometry((0.012+0.008*rnd(j+k))*sz,1),gold,{x:(rnd(j*3+k)-0.5)*0.04*sz,y:0.008*sz,z:(rnd(j*5+k)-0.5)*0.04*sz});m.scale.set(1,0.7,1.1);g.add(m)}
      const sp=new THREE.Mesh(new THREE.OctahedronGeometry(0.02*sz,0),glow('#fff3b0'));sp.position.y=0.05*sz;g.add(sp);g.userData={v:W(q),sp};it.root.add(g);return g});break}

  case 'span':{const a=W(p.a),b=W(p.b);const y=(p.h||0.06);a.y=b.y=y;const pts=[];for(let i=0;i<=40;i++){const v=a.clone().lerp(b,i/40);v.y=y+Math.sin(i/40*Math.PI)*(p.arc||0.03);pts.push(v)}
    it.trail=trailTube(pts,p.color||'#ffc83d',0.008*sz);it.root.add(it.trail);it.ends=[a,b].map(v=>{const e=mesh(new THREE.CylinderGeometry(0.012*sz,0.012*sz,y+0.04,12),glow(p.color||'#ffc83d'));e.position.set(v.x,(y+0.04)/2-0.02,v.z);it.root.add(e);return e});break}
  case 'dateline':{const pts=p.path.map(q=>W(q));const H=(p.h||0.35)*sz;const pos=[],uv=[];const n=pts.length;
    for(let i=0;i<n;i++){const v=pts[i];pos.push(v.x,-0.02,v.z,v.x,H,v.z);uv.push(i/(n-1),0,i/(n-1),1)}const idx=[];for(let i=0;i<n-1;i++){const a=2*i;idx.push(a,a+1,a+2,a+1,a+3,a+2)}
    const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));g.setIndex(idx);
    const c=document.createElement('canvas');c.width=8;c.height=256;const gx=c.getContext('2d');const gr=gx.createLinearGradient(0,256,0,0);gr.addColorStop(0,'rgba(255,200,61,0.85)');gr.addColorStop(0.35,'rgba(255,200,61,0.35)');gr.addColorStop(1,'rgba(255,200,61,0)');gx.fillStyle=gr;gx.fillRect(0,0,8,256);
    const tx=new THREE.CanvasTexture(c);it.wall=new THREE.Mesh(g,new THREE.MeshBasicMaterial({map:tx,transparent:true,side:THREE.DoubleSide,depthWrite:false,toneMapped:false}));it.root.add(it.wall);
    const top=pts.map(v=>new THREE.Vector3(v.x,0.012,v.z));it.trail=trailTube(top,p.color||'#ffc83d',0.006*sz);it.root.add(it.trail);it.H=H;break}
  case 'swimmer':{const pts=p.path.map(q=>{const v=W(q);v.y=0.004;return v});it.trail=trailTube(pts,'#e8f4ff',0.006*sz);it.trail.material=glow('#cfe6ff');it.trail.material.opacity=0.8;it.root.add(it.trail);
    const g=new THREE.Group();const s=0.03*sz;const skin=clay('#eebf98'),cap=clay(p.color||'#ffc83d');g.add(mesh(new THREE.SphereGeometry(s*0.5,20,14),cap,{y:s*0.15}));
    g.add(mesh(new THREE.CapsuleGeometry(s*0.32,s*1.1,6,12),clay('#22324a'),{x:-s*0.9,y:-s*0.05}));g.children[1].rotation.z=Math.PI/2;
    it.arms=[0,1].map(k=>{const a=new THREE.Group();a.add(mesh(new THREE.CapsuleGeometry(s*0.13,s*0.9,4,8),skin,{y:s*0.5}));a.position.set(-s*0.35,0,(k?1:-1)*s*0.32);g.add(a);return a});
    it.sw=g;it.root.add(g);break}
  case 'glasses':{const c=W(p.at);it.c=c;it.g=[0,1].map(k=>{const g=new THREE.Group();const s=0.08*sz;const glass=new THREE.MeshPhysicalMaterial({color:C('#dfe8f2'),roughness:0.15,transparent:true,opacity:0.45,envMap:ENV,envMapIntensity:0.5,clearcoat:0.5});
      g.add(mesh(new THREE.CylinderGeometry(s*0.38,s*0.06,s*0.9,24,1,true),glass,{y:s*1.35}));g.add(mesh(new THREE.CylinderGeometry(s*0.33,s*0.08,s*0.55,24),clay('#e9b949',{transparent:true,opacity:0.9}),{y:s*1.2}));
      g.add(mesh(new THREE.CylinderGeometry(s*0.035,s*0.035,s*0.9,10),glass,{y:s*0.45}));g.add(mesh(new THREE.CylinderGeometry(s*0.26,s*0.28,s*0.04,24),glass,{y:s*0.02}));
      const fl=makeFlag(k?p.right:p.left,0.9*sz);fl.position.set(0,0,0);g.userData.fl=fl;it.root.add(fl);it.root.add(g);return g});
    it.sp=new THREE.Group();for(let i=0;i<10;i++){const m=mesh(new THREE.OctahedronGeometry(0.012*sz,0),glow('#fff2b0'));m.userData.k=i;it.sp.add(m)}it.root.add(it.sp);break}
  case 'ice':{it.f=[];const n=p.n||60;const A=W(p.a),B=W(p.b);const iceM=clay('#c9d6e2',{roughness:0.6,clearcoat:0.2,sheen:0.1,envMapIntensity:0.25});
    for(let i=0;i<n;i++){const u=rnd(i*3.1),v=rnd(i*7.7);const pos=new THREE.Vector3(A.x+(B.x-A.x)*u,0,A.z+(B.z-A.z)*v);const r=(0.03+rnd(i*1.3)*0.05)*sz;
      const m=mesh(new THREE.CylinderGeometry(r,r*1.05,0.008*sz,6),iceM);m.position.copy(pos);m.rotation.y=rnd(i)*3;m.userData.k=u;it.f.push(m);it.root.add(m)}break}
  case 'pricetag':{await document.fonts.load('400 120px AB');await document.fonts.load('800 44px IN');const c=document.createElement('canvas');c.width=512;c.height=256;const g2=c.getContext('2d');g2.fillStyle='#fff6df';g2.fillRect(0,0,512,256);
    g2.fillStyle='#0a0f1a';g2.font='400 116px AB';g2.textAlign='center';g2.textBaseline='middle';g2.fillText(p.text,256,120);
    g2.font='800 44px IN';g2.fillStyle='#c8553d';g2.fillText(p.sub||'',256,210);const tx=new THREE.CanvasTexture(c);tx.colorSpace=THREE.SRGBColorSpace;
    const g=new THREE.Group();const s=sz;const body=mesh(RB(0.8*s,0.4*s,0.03*s,0.15),clay('#efe4c8',{clearcoat:0,sheen:0,roughness:0.95,envMapIntensity:0.15}));g.add(body);
    const face=mesh(new THREE.PlaneGeometry(0.76*s,0.38*s),new THREE.MeshStandardMaterial({map:tx,roughness:0.95,color:C('#e6dcc4')}),{z:0.016*s});g.add(face);
    g.add(mesh(new THREE.TorusGeometry(0.03*s,0.008*s,8,20),metal('#e8b84a'),{x:-0.33*s,y:0.13*s,z:0.02*s}));
    const str=mesh(new THREE.CylinderGeometry(0.003*s,0.003*s,0.6*s,6),clay('#c8553d'),{x:-0.33*s,y:0.43*s});g.add(str);
    it.tag=g;it.root.add(g);it.v=W(p.at);break}
  }}
const placeY=(o,v,dy=0)=>{o.position.set(v.x,groundAtW(v.x,v.z)+dy,v.z)};
function update(t,s,ls,EX){
  for(const it of items){const p=it.p;const on=s===p.scene;it.root.visible=on;if(!on)continue;
    switch(p.type){
    case 'drive':{const f=clamp01((ls-(p.from||0))/p.dur);const e=f<1?f*f*(3-2*f):1;reveal(it.trail,e);
      it.trail.position.y=s===CFG.lines[0][0]?(cur.chile?.lift||0)*0.09:(cur.chile?.lift||0)*0.09;
      const c=it.trail.userData.curve, q=c.getPointAt(Math.min(0.999,e)), q2=c.getPointAt(Math.min(1,e+0.002));
      it.car.position.set(q.x,groundAtW(q.x,q.z)+0.004,q.z);it.car.rotation.y=Math.atan2(-(q2.z-q.z),q2.x-q.x);
      it.car.scale.setScalar(popS((ls-(p.from||0)+0.3)/0.35));it.car.position.y+=Math.abs(Math.sin(ls*30))*0.004;break}
    case 'trace':{reveal(it.trail,ease(clamp01((ls-0.2)/p.dur)));it.trail.position.y=(cur[p.country]?.lift||0)*0.09;break}
    case 'qmark':{const v=W(p.at);it.q.position.set(v.x,0.3+0.5*(p.size||1)+Math.sin(ls*2.2)*0.06,v.z);it.q.lookAt(X.cam.position.x,it.q.position.y,X.cam.position.z);it.q.rotation.y+=Math.sin(ls*1.6)*0.35;it.q.scale.setScalar(popS((ls-0.5)/0.45));break}
    case 'houses':{it.h.forEach((g,k)=>{placeY(g,g.userData.v,-0.004);let sc=popS((ls-(p.from??1.2)-k*0.28)/0.35);if(p.vanish){const v=clamp01((ls-p.vanish[0]-k*0.2)/(p.vanish[1]-p.vanish[0]));sc*=Math.max(0.0001,1-ease(v))}g.scale.setScalar(sc)});break}
    case 'ship':{const f=clamp01(ls/p.dur);const v=it.a.clone().lerp(it.b,f);it.ship.position.set(v.x,-0.05+Math.sin(ls*3)*0.006,v.z);
      it.ship.rotation.y=Math.atan2(-(it.b.z-it.a.z),it.b.x-it.a.x);it.ship.rotation.x=Math.sin(ls*2.4)*0.06;it.ship.scale.setScalar(1.6*popS(ls/0.4));wave(it.fl,ls);break}
    case 'crest':{reveal(it.trail,ease(clamp01((ls-1.0)/2.2)));it.trail.scale.y=EX;it.trail.position.y=0.035;
      it.trail.material.opacity=0.65+0.35*Math.sin(ls*5);break}
    case 'pen':{const f=ease(clamp01((ls-p.from)/p.dur));reveal(it.trail,f);const lift=0.09*Math.max(cur[p.between[0]]?.lift||0,cur[p.between[1]]?.lift||0);
      it.trail.position.y=lift+0.03;const q=it.trail.userData.curve.getPointAt(Math.max(0.0001,Math.min(0.999,f)));
      it.pen.position.set(q.x,q.y+lift+0.03,q.z);it.pen.visible=ls>p.from-0.4&&f<0.995;it.pen.scale.setScalar(popS((ls-p.from+0.4)/0.4));break}
    case 'army':{const [m0,m1]=p.march;let f=ease(clamp01((ls-m0)/(m1-m0)));let rf=0,fade=1;
      if(p.retreat){rf=ease(clamp01((ls-p.retreat[0])/(p.retreat[1]-p.retreat[0])));fade=1-rf}
      const at=it.fw.clone().lerp(it.tw,f).lerp(it.fw,rf*0.6);const marching=(ls>m0&&ls<m1)||(rf>0&&rf<1);const fight=ls>=m1&&!(rf>0);
      it.men.forEach((m,k)=>{const v=at.clone().add(m.userData.off);placeY(m,v);const ph=m.userData.ph;
        if(marching)m.position.y+=Math.abs(Math.sin(ls*11+ph))*0.012;
        m.rotation.y=Math.atan2(-(rf>0?-it.dir.z:it.dir.z),(rf>0?-it.dir.x:it.dir.x));
        m.userData.gun.rotation.z=fight?0.08+Math.max(0,Math.sin(ls*9+ph))*0.25:1.15+(marching?Math.sin(ls*11+ph)*0.08:0);
        m.userData.legs.forEach((L,q)=>L.rotation.z=marching?Math.sin(ls*11+ph+q*Math.PI)*0.5:0);
        if(fight)m.position.y+=Math.max(0,Math.sin(ls*9+ph))*0.006;
        m.scale.setScalar(popS((ls-m0+0.25-k*0.015)/0.3)*Math.max(0.0001,fade))});
      if(it.fl){const v=at.clone().add(it.fl.userData.off);placeY(it.fl,v);it.fl.scale.setScalar(popS((ls-m0+0.2)/0.3)*Math.max(0.0001,fade));wave(it.fl,ls)}break}
    case 'clash':{const act=ls>p.from&&ls<p.to;it.fx.forEach(m=>{const {isF,k}=m.userData;
      if(!act){m.visible=false;return}m.visible=true;const per=isF?0.5:1.6;const ph=rnd(k)*per;const lt=((ls-p.from+ph)%per)/per;const cyc=Math.floor((ls-p.from+ph)/per);
      const a=rnd(k*13+cyc)*6.28,rr=0.04+0.2*rnd(k*7+cyc*3);const x=it.c.x+Math.cos(a)*rr,z=it.c.z+Math.sin(a)*rr*0.8;
      if(isF){m.position.set(x,groundAtW(x,z)+0.07,z);m.rotation.set(a,a*2,0);m.scale.setScalar(lt<0.18?0.6+lt*8:0.0001)}
      else{m.position.set(x+lt*0.04,groundAtW(x,z)+0.06+lt*0.1,z);m.scale.setScalar(0.5+lt*1.3);m.material.opacity=0.42*Math.sin(Math.min(1,lt*1.3)*Math.PI)}});break}
    case 'flagswap':{const T=p.t;placeY(it.lost,it.v);placeY(it.won,it.v.clone().add(new THREE.Vector3(0.02,0,0)));
      const fall=ease(clamp01((ls-T)/0.5));it.lost.rotation.z=fall*1.45;it.lost.position.y-=fall*0.03;it.lost.scale.setScalar(popS(ls/0.3)*(1-ease(clamp01((ls-T-0.6)/0.4)))+0.0001);
      it.won.scale.setScalar(popS((ls-T-0.5)/0.4));wave(it.lost,ls);wave(it.won,ls);break}
    case 'flags':{it.f.forEach((f,k)=>{placeY(f,f.userData.v);f.scale.setScalar(popS((ls-p.from-k*0.35)/0.35));wave(f,ls+k)});break}
    case 'sheep':{it.sh.forEach((g,k)=>{const d=g.userData;const v=d.c.clone().add(new THREE.Vector3(Math.cos(d.dir)*Math.sin(ls*0.6+d.ph)*0.05,0,Math.sin(d.dir)*Math.sin(ls*0.6+d.ph)*0.05));
      placeY(g,v);g.position.y+=Math.max(0,Math.sin(ls*7+d.ph))*0.012;g.rotation.y=-d.dir+(Math.cos(ls*0.6+d.ph)<0?Math.PI:0);g.scale.setScalar(popS((ls-p.from-k*0.08)/0.3))});break}
    case 'otters':{it.o.forEach((g,k)=>{const d=g.userData;g.position.set(d.v.x,-0.045+Math.sin(ls*2.5+d.ph)*0.004,d.v.z);g.rotation.y=d.yaw+Math.sin(ls*0.7+d.ph)*0.3;
      const gone=ease(clamp01((ls-d.out)/0.4));g.scale.setScalar(popS((ls-(p.from||0)-k*0.06)/0.3)*(1-gone)+0.0001);g.position.y-=gone*0.03});break}
    case 'coins':{const T=p.start||0,du=p.dur||3;it.c.forEach(m=>{const k=m.userData.k;const f=(ls-T-k*du/it.c.length*0.7)/(du*0.45);
        if(f<0||f>1){m.visible=false;return}m.visible=true;const v=it.A.clone().lerp(it.B,f);v.y=0.2+Math.sin(f*Math.PI)*1.2;m.position.copy(v);m.rotation.set(ls*6+k,0,ls*4);m.scale.setScalar(1)});
      it.pile.position.copy(it.B);it.pile.position.y=groundAtW(it.B.x,it.B.z);const pf=clamp01((ls-T-du*0.45)/(du*0.7));it.pile.children.forEach((m,k)=>m.visible=k<pf*it.pile.children.length);break}
    case 'pumpjacks':{it.pj.forEach((g,k)=>{placeY(g,g.userData.v);g.userData.beam.rotation.z=Math.sin(ls*3+g.userData.ph)*0.28;g.scale.setScalar(popS((ls-(p.from||0)-k*0.25)/0.35))});break}
    case 'nuggets':{it.n.forEach((g,k)=>{placeY(g,g.userData.v);const u=ls-(p.from||0)-k*0.35;g.scale.setScalar(popS(u/0.35));const sp=g.userData.sp;sp.rotation.y=ls*3;sp.scale.setScalar(Math.max(0.0001,Math.sin(clamp01(u/0.8)*Math.PI)*1.6+0.3*Math.max(0,Math.sin(ls*5+k))))});break}

    case 'span':{const f=ease(clamp01((ls-(p.from||0))/(p.dur||1.2)));reveal(it.trail,f);it.ends.forEach((e,k)=>e.scale.setScalar(popS((ls-(p.from||0)-(k?p.dur||1.2:0))/0.3)));break}
    case 'dateline':{const f=ease(clamp01((ls-(p.from||0))/(p.dur||1.2)));reveal(it.trail,f);it.wall.scale.y=Math.max(0.0001,ease(clamp01((ls-(p.from||0)-0.3)/0.9)));it.wall.material.opacity=0.75+0.25*Math.sin(ls*3);break}
    case 'swimmer':{const f=clamp01((ls-(p.from||0))/p.dur);reveal(it.trail,f);const c=it.trail.userData.curve,q=c.getPointAt(Math.min(0.999,f)),q2=c.getPointAt(Math.min(1,f+0.003));
      it.sw.position.set(q.x,0.002+Math.sin(ls*8)*0.002,q.z);it.sw.rotation.y=Math.atan2(-(q2.z-q.z),q2.x-q.x);it.arms.forEach((a,k)=>a.rotation.z=ls*7+k*Math.PI);it.sw.scale.setScalar(popS((ls-(p.from||0)+0.2)/0.3));break}
    case 'glasses':{const T=p.t||1.2;const u=ease(clamp01((ls-0.2)/T));const d=0.18*(p.size||1)*(1-u)+0.035*(p.size||1);
      const ZA=p.axis==='z';it.g.forEach((g,k)=>{const sgn=(k?1:-1)*(p.flip?-1:1);const ox=ZA?0:sgn*d,oz=ZA?sgn*d:0;g.position.set(it.c.x+ox,(p.h||0.25),it.c.z+oz);if(ZA)g.rotation.x=sgn*0.35*u;else g.rotation.z=-sgn*0.35*u;g.scale.setScalar(popS(ls/0.4));const fl=g.userData.fl;const fo=sgn*(p.flagoff||0.32)*(p.size||1);const fx=it.c.x+(ZA?0.06:fo),fz=it.c.z+(ZA?fo:0.05);fl.position.set(fx,groundAtW(fx,fz),fz);fl.scale.setScalar(popS((ls-0.1)/0.4));wave(fl,ls+k)});
      const b=ls-0.2-T;it.sp.children.forEach(m=>{const k=m.userData.k,a=k/10*Math.PI*2;const r=b>0?b*0.35:0;m.position.set(it.c.x+Math.cos(a)*r,(p.h||0.25)+0.12*(p.size||1)+Math.sin(a)*r*0.6,it.c.z);m.scale.setScalar(b>0&&b<0.9?1-b/0.9:0.0001);m.rotation.y=ls*4})
      break}
    case 'ice':{const f=clamp01((ls-(p.from||0))/(p.dur||2));it.f.forEach(m=>{const k=m.userData.k;const g=Math.abs(k-0.5)*2;m.scale.setScalar(popS((f*1.3-(1-g))/0.25));m.position.y=-0.003})
      break}
    case 'pricetag':{const u=ls-(p.from||0);it.tag.position.set(it.v.x,(p.h||1.2)+Math.sin(ls*1.8)*0.03,it.v.z);it.tag.lookAt(X.cam.position);it.tag.rotation.z+=Math.sin(ls*2.2)*0.08;it.tag.scale.setScalar(popS(u/0.45));break}
    }}}
return {update,driveOf:s=>CFG.props.find(p=>p.type==='drive'&&p.scene===s)};
}
