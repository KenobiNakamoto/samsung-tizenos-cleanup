// DOM/state tests, with image/font measurement mocked; no browser or TV access.
const {test}=require('node:test'), assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const {JSDOM}=require(process.env.FAMILY_HOME_TEST_JSDOM||'jsdom');
const app=path.join(__dirname,'../app');
const layout=require('../app/family-layout.js');
const ids=['livetv','rtveplay','movistarplus','primevideo','disneyplus','appletv','plex','stremio'];
async function setup(t,old){
 const dom=new JSDOM(fs.readFileSync(path.join(app,'index.html'),'utf8'),{url:'https://preview.invalid/',runScripts:'outside-only',pretendToBeVisual:true});
 t.after(()=>dom.window.close());const w=dom.window;
 w.HTMLCanvasElement.prototype.getContext=()=>({measureText:s=>({width:s.length*20})});
 Object.defineProperty(w.HTMLImageElement.prototype,'complete',{get:()=>true});
 Object.defineProperty(w.HTMLImageElement.prototype,'naturalWidth',{get:()=>1920});
 w.HTMLElement.prototype.getBoundingClientRect=function(){return {x:0,y:0,left:0,top:0,right:200,bottom:40,width:200,height:40};};
 w.HTMLElement.prototype.getClientRects=function(){return this.closest('[hidden]')?[]:[this.getBoundingClientRect()];};
 if(old)w.localStorage.setItem('family-home.settings.v1',JSON.stringify(old));
 let launches=[];w.tizen={application:{getAppsInfo:ok=>ok([
  {id:'org.tizen.tv-viewer',name:'TV',show:true},
  {id:'ubrNshqKcU.ALaCarta',name:'RTVE',show:true},
  {id:'m52SXlMi8Y.YOMVITIZEN',name:'Movistar+',show:true},
  {id:'org.tizen.netflix-app',name:'Netflix',show:true},
  {id:'rJeHak5zRg.Spotify',name:'Spotify',show:true},
  {id:'FamHome001.FamilyHome',name:'Family Home',show:true},
  {id:'abcdefghij.AdService',name:'Advertising service',show:true}
 ]),launch:(id,ok)=>{launches.push(id);ok();}}};
 ['device.js','assets/icons/metrics.js','assets/wallpapers/catalog.js','assets/adaptive-ink.js','assets/font-catalog.js','family-layout.js','main.js'].forEach(f=>w.eval(fs.readFileSync(path.join(app,f),'utf8')));
 await new Promise(r=>setTimeout(r,50));
 return {w,qa:w.ShoreQA,launches,state:()=>w.ShoreQA.state(),click:action=>{const el=w.document.querySelector('[data-action="'+action+'"]');assert.ok(el,action);el.click();}};
}
test('default geometry fits five large, three compact, square Apps and vertical + without overlaps',()=>{
 const sizes=Object.fromEntries(ids.map((id,i)=>[id,i<5?'large':'compact'])),g=layout.geometry(ids,sizes);
 assert.equal(g.cells.length,10);assert.ok(g.width<=1696);assert.equal(g.cells.filter(c=>c.small).length,3);
 assert.equal(g.cells[8].w,g.cells[8].h);assert.ok(g.cells[9].w<g.cells[9].h);
 for(const a of g.cells)for(const b of g.cells)if(a!==b)assert.ok(a.x+a.w<=b.x||b.x+b.w<=a.x||a.y+a.h<=b.y||b.y+b.h<=a.y);
});
test('D-pad reaches both compact rows and trailing Apps/+ controls',async t=>{
 const {qa,state}=await setup(t);assert.deepEqual(Array.from(state().home),ids);
 qa.nav('right','right','right','right','right');assert.equal(state().selected,'appletv');
 qa.nav('down');assert.equal(state().selected,'stremio');qa.nav('up','right');assert.equal(state().selected,'plex');
 qa.nav('right');assert.equal(qa.where().zone,'tail');qa.nav('right','ok');assert.equal(state().view,'editor');
});
test('old Family Home preferences migrate without overwriting the old rollback key',async t=>{
 const old={version:4,favorites:['org.tizen.tv-viewer','ubrNshqKcU.ALaCarta','family-home:hbo'],cardSizes:{'org.tizen.tv-viewer':'large','ubrNshqKcU.ALaCarta':'compact','family-home:hbo':'compact'},layout:'frame',background:'slate'};
 const {w,state}=await setup(t,old);assert.deepEqual(Array.from(state().home),['livetv','rtveplay']);assert.equal(state().layout,'list');assert.equal(state().sizes.rtveplay,'compact');assert.deepEqual(JSON.parse(w.localStorage.getItem('family-home.settings.v1')),old);
});
test('native Live TV/Spanish apps launch exact installed IDs and HBO is absent from Home',async t=>{
 const {qa,launches,state}=await setup(t);qa.nav('ok');assert.equal(launches[0],'org.tizen.tv-viewer');qa.nav('right','ok');assert.equal(launches[1],'ubrNshqKcU.ALaCarta');
 qa.nav('right','ok');assert.equal(launches[2],'m52SXlMi8Y.YOMVITIZEN');
 assert.ok(!state().home.includes('hbomax'));assert.equal(state().familyHomeRevision,1);assert.equal(launches.length,3);
});
test('editor size toggle, reorder, undo, remove/add and ninth app retain saved state',async t=>{
 const {qa,state,click}=await setup(t);qa.scene('editor');
 click('editor.size.livetv');assert.equal(state().sizes.livetv,'compact');click('editor.undo');assert.equal(state().sizes.livetv,'large');
 click('editor.move.livetv');qa.nav('down','ok');assert.equal(state().home[1],'livetv');click('editor.undo');assert.equal(state().home[0],'livetv');
 click('editor.remove.livetv');assert.ok(!state().home.includes('livetv'));click('editor.add.livetv');assert.equal(state().home[0],'livetv');
 click('editor.add.rJeHak5zRg.Spotify');assert.equal(state().home.length,9);assert.equal(state().sizes['rJeHak5zRg.Spotify'],'compact');
});
test('layout switch preserves sizes and catalogue omits self and services',async t=>{
 const {qa,state}=await setup(t);qa.look({layout:'list',apps:'text'});assert.equal(state().layout,'list');assert.equal(state().sizes.appletv,'compact');qa.scene('apps');
 assert.ok(state().catalog.ids.includes('org.tizen.netflix-app'));assert.ok(!state().catalog.ids.includes('FamHome001.FamilyHome'));assert.ok(!state().catalog.ids.includes('abcdefghij.AdService'));
});
