// 지도 밖 장면 (결재함 101, 2026-11-08) — 3D 지도 위를 덮는 2D 카드. 설정 "cards": [ {...}, ... ]
// 공통: type · scene(대본 장면 이름) · from(장면 시작 뒤 초, 기본 0) · to(장면 시작 뒤 초, 기본 장면 끝)
//       in / out = 들어오고 나가는 전환 시간(초, 기본 0.3 · 0 이면 컷) — 화면 변화 ≤2.5초 리듬에 맞춰 짧게
//       title(위 제목, 선택)
// type "bars"  : 비교 막대 — items [[이름, 값, 색(선택)], ...] · unit(값 뒤 글자) · step(막대 사이 초, 기본 0.35) · grow(막대가 자라는 초, 기본 0.6)
// type "stat"  : 큰 숫자 하나 — value · prefix · suffix · label(아래 글) · count(숫자가 0→값으로 오르는 초, 기본 0.8, 0 이면 바로)
// type "photo" : 사진 카드 — src(media/ 아래 파일 또는 https URL — 렌더 Actions 가 media/ 로 받아 둠) · credit(출처 줄, 필수: "Photo: 작가 / 라이선스")
//                zoom(천천히 다가가는 배율, 기본 1.08) — 사진 설명은 title 로
// 카드가 화면을 다 덮은 동안은 3D 렌더를 건너뛴다(렌더 시간 절약). 자막·진행 막대·로고는 카드 위에 그대로.
export const CARD_CSS=`
.card{position:absolute;left:0;right:0;top:0;bottom:0;background:radial-gradient(120% 80% at 50% 30%,#1b2a44 0%,#0a0f1a 70%)}
.card .ttl{position:absolute;left:70px;right:70px;top:210px;font:400 76px AB;color:#fff;text-align:left;letter-spacing:1px}
.card .ttl:after{content:'';display:block;width:120px;height:10px;background:#FFC83D;margin-top:18px;border-radius:5px}
.card .bars{position:absolute;left:70px;right:70px;top:420px}
.card .row{margin-bottom:46px}
.card .row .nm{font:800 46px IN;color:#fff;letter-spacing:2px;margin-bottom:12px}
.card .row .tr{position:relative;height:96px}
.card .row .fl{position:absolute;left:0;top:0;bottom:0;border-radius:20px;box-shadow:0 10px 30px rgba(0,0,0,.45)}
.card .row .v{position:absolute;top:0;bottom:0;display:flex;align-items:center;font:400 60px AB;color:#fff;white-space:nowrap;padding-left:22px}
.card .stat{position:absolute;left:0;right:0;top:560px;text-align:center}
.card .stat .num{font:400 230px AB;color:#FFC83D;line-height:1;text-shadow:0 14px 50px rgba(0,0,0,.6)}
.card .stat .lab{font:800 56px IN;color:#fff;letter-spacing:4px;margin-top:26px;padding:0 70px}
.card .ph{position:absolute;left:60px;right:60px;top:380px;height:820px;border-radius:36px;overflow:hidden;border:4px solid #FFC83D;box-shadow:0 20px 60px rgba(0,0,0,.6);background:#111}
.card .ph img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transform-origin:50% 45%}
.card .cr{position:absolute;right:66px;top:1214px;font:600 26px IN;color:#c9d3e6;opacity:.9;text-align:right;max-width:950px}
`;
const cl=x=>Math.max(0,Math.min(1,x)), out3=u=>1-Math.pow(1-cl(u),3);
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const fmt=(v,dec)=>(+v).toLocaleString('en-US',{minimumFractionDigits:dec,maximumFractionDigits:dec});
const decs=v=>{const m=String(v).match(/\.(\d+)/);return m?m[1].length:0};
// 카드 사진 파일 경로: 언제나 media/<마지막 이름> (URL·로컬 둘 다) (render.yml·make.sh 가 같은 이름으로 받음)
export const mediaPath=src=>'media/'+decodeURIComponent(String(src).split('?')[0].split('/').pop());

export async function makeCards(CFG,T0,T1){
  const list=(CFG.cards||[]).filter(c=>T0[c.scene]!==undefined).map(c=>{
    const a=T0[c.scene]+(c.from||0), b=c.to!=null?T0[c.scene]+c.to:T1[c.scene];
    return {...c,a,b,in:c.in??0.3,out:c.out??0.3}});
  for(const c of list) if(c.type==='photo'){const im=new Image();im.src=mediaPath(c.src);try{await im.decode()}catch(e){console.log('card photo missing',c.src)}}
  // 지금 보일 카드와 덮는 정도(0~1)
  function at(t){for(const c of list){if(t<c.a||t>=c.b)continue;
      const vi=c.in>0?cl((t-c.a)/c.in):1, vo=c.out>0?cl((c.b-t)/c.out):1; return {c,v:Math.min(vi,vo),lt:t-c.a}}
    return null}
  function html(t){const k=at(t);if(!k)return {html:'',cover:0};const {c,v,lt}=k;
    const e=out3(v), slide=((1-e)*120).toFixed(0);   // 들어올 때 아래에서 살짝 올라오며 나타남, 나갈 때 반대
    let h=`<div class="card" style="opacity:${e.toFixed(3)};transform:translateY(${slide}px)">`;
    if(c.title) h+=`<div class="ttl">${esc(c.title)}</div>`;
    if(c.type==='bars'){const its=c.items||[], mx=Math.max(...its.map(x=>+x[1]),1e-9), st=c.step??0.35, gr=c.grow??0.6;
      h+=`<div class="bars">`;
      its.forEach(([nm,val,col],j)=>{const u=out3((lt-0.15-j*st)/gr), w=Math.max(0.04,(+val)/mx)*620*u;   // 막대 최대 620px, 값 글자는 막대 끝 옆
        h+=`<div class="row" style="opacity:${cl((lt-0.15-j*st)/0.2).toFixed(2)}"><div class="nm">${esc(nm)}</div><div class="tr">
          <div class="fl" style="width:${w.toFixed(0)}px;background:${col||(j?'#8fa3c4':'#FFC83D')}"></div>
          <div class="v" style="left:${w.toFixed(0)}px">${fmt(val*u,decs(val))}${esc(c.unit?' '+c.unit:'')}</div></div></div>`});
      h+=`</div>`}
    else if(c.type==='stat'){const cn=c.count??0.8, u=cn>0?out3((lt-0.1)/cn):1, val=+c.value;
      h+=`<div class="stat"><div class="num">${esc(c.prefix||'')}${fmt(val*u,decs(c.value))}${esc(c.suffix||'')}</div>${c.label?`<div class="lab">${esc(c.label)}</div>`:''}</div>`}
    else if(c.type==='photo'){const z=1+((c.zoom??1.08)-1)*cl(lt/Math.max(0.5,c.b-c.a));
      h+=`<div class="ph"><img src="${esc(mediaPath(c.src))}" style="transform:scale(${z.toFixed(4)})"></div><div class="cr">${esc(c.credit||'')}</div>`}
    return {html:h+`</div>`,cover:e}}
  return {list,at,html};
}
