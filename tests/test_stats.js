const { chromium } = require('playwright');
(async()=>{
 const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const pg=await b.newPage({viewport:{width:390,height:844},deviceScaleFactor:2});
 await pg.route('**/three.min.js',r=>r.fulfill({path:'node_modules/three/build/three.min.js',contentType:'text/javascript'}));
 await pg.route('**/fonts.googleapis.com/**',r=>r.fulfill({path:'fonts.css',contentType:'text/css'}));
 await pg.goto('file://'+process.cwd()+'/wrapped.html');
 await pg.waitForFunction(()=>{ const i=document.querySelector('#intro'); return i && !i.hidden; },null,{timeout:300000}); await pg.click('#introSkip');
 await pg.waitForFunction(()=>document.querySelector('#boot.home') && !document.querySelector('#intro'),null,{timeout:30000});
 const shots=[]; for (const w of ['neil','hunter','sean']) { await pg.click(`.face[data-who="${w}"]`); await pg.waitForTimeout(500);
   const r=await pg.evaluate(()=>{const e=document.querySelector('#stats').getBoundingClientRect();return {x:e.x-6,y:e.y-6,width:e.width+12,height:e.height+12};}); console.log(w, Math.round(r.width-12));
   await pg.screenshot({path:`out/st_${w}.png`,clip:r}); }
 await b.close();
})();
