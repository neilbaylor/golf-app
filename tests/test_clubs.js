const { chromium } = require('playwright');
(async()=>{
 const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const pg=await b.newPage({viewport:{width:390,height:844},deviceScaleFactor:3});
 let errs=0; pg.on('pageerror',e=>{errs++;console.log('PAGEERR '+e.message)});
 await pg.route('**/three.min.js',r=>r.fulfill({path:'node_modules/three/build/three.min.js',contentType:'text/javascript'}));
 await pg.route('**/fonts.googleapis.com/**',r=>r.fulfill({path:'fonts.css',contentType:'text/css'}));
 await pg.goto('file://'+process.cwd()+'/wrapped_club.html');
 await pg.waitForFunction(()=>{ const i=document.querySelector('#intro'); return i && !i.hidden; },null,{timeout:300000}); await pg.click('#introSkip');
 await pg.waitForFunction(()=>document.querySelector('#boot.home') && !document.querySelector('#intro'),null,{timeout:30000});
 await pg.click('#playBtn'); await pg.waitForFunction(()=>!document.querySelector('#boot'),null,{timeout:60000}); await pg.waitForTimeout(1500);
 await pg.evaluate(()=>{ window.__knobOff = true; });
 for (let i=0;i<13;i++){ await pg.evaluate(i=>{ __knob(i); },i); await pg.waitForTimeout(80);
   const r=await pg.evaluate(()=>{ const k=document.querySelector('#knob').getBoundingClientRect(); return {x:k.x-14,y:k.y-14,width:k.width+28,height:k.height+28}; });
   await pg.screenshot({path:`out/club${i}.png`,clip:r}); }
 console.log('errors',errs); await b.close();
})();
