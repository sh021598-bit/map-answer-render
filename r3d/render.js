const {chromium}=require('playwright');const {spawn}=require('child_process');const fs=require('fs');
const [,,out,fpsArg,only]=process.argv; const Q=process.env.LOOKQ||''; const FPS=+fpsArg||30;
(async()=>{const tl=JSON.parse(fs.readFileSync('data/timeline.json'));
const b=await chromium.launch({...(process.env.CHROME?{executablePath:process.env.CHROME}:{}),args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const p=await b.newPage({viewport:{width:1080,height:1920}}); p.on('console',m=>console.log('PAGE',m.text())); p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto(`http://localhost:${process.env.PORT||8765}/index.html${Q}`); await p.waitForFunction('window.ready',null,{timeout:120000});
if(out==='frames'){ // 이어 그리기: node render.js frames 30 <시작> <끝> → frames/00000.jpg (있는 프레임은 건너뜀)
  const N=Math.ceil(tl.total*FPS),a=+process.argv[4]||0,e=Math.min(N,+process.argv[5]||N);fs.mkdirSync('frames',{recursive:true});const t0=Date.now();
  for(let i=a;i<e;i++){const f=`frames/${String(i).padStart(5,'0')}.jpg`;if(fs.existsSync(f))continue;await p.evaluate(`frame(${i/FPS})`);
    await p.screenshot({path:f+'.tmp',type:'jpeg',quality:92,timeout:120000});fs.renameSync(f+'.tmp',f);if(i%30==0)console.log(i,'/',e,((Date.now()-t0)/1000).toFixed(0)+'s')}
  await b.close();return}
if(only){for(const t of only.split(',')){await p.evaluate(`frame(${t})`);await p.screenshot({path:`still_${t}.jpg`,type:'jpeg',quality:90,timeout:120000});}await b.close();return}
const N=Math.ceil(tl.total*FPS);
const ff=spawn('ffmpeg',['-y','-v','error','-f','image2pipe','-framerate',String(FPS),'-c:v','mjpeg','-i','-','-i','final_audio.wav','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-shortest','-movflags','+faststart',out]);
const t0=Date.now();for(let i=0;i<N;i++){await p.evaluate(`frame(${i/FPS})`);const buf=await p.screenshot({type:'jpeg',quality:92,timeout:120000});
 if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r)); if(i%60==0) console.log(i,'/',N,((Date.now()-t0)/1000).toFixed(0)+'s');}
ff.stdin.end(); await new Promise(r=>ff.on('close',r)); await b.close(); console.log('done');})();
