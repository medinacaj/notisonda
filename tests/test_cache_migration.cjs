'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');

test('activation removes legacy app caches, keeps current cache and other apps, and claims clients',async()=>{
 const handlers={},deleted=[];
 let current,claimed=0,pending;
 const context=vm.createContext({URL,Request,
  self:{addEventListener:(name,handler)=>handlers[name]=handler,clients:{claim:async()=>{claimed++;}}},
  caches:{keys:async()=>['radar-rss-v55','notisonda-v0',current,'another-app-v1'],delete:async key=>{deleted.push(key);return true;}}
 });
 vm.runInContext(fs.readFileSync(path.join(__dirname,'../web/sw.js'),'utf8'),context);
 current=vm.runInContext('CACHE',context);
 handlers.activate({waitUntil:promise=>{pending=promise;}});
 await pending;
 assert.deepEqual(deleted.sort(),['notisonda-v0','radar-rss-v55']);
 assert.equal(claimed,1);
 assert.ok(!deleted.includes(current));
 assert.ok(!deleted.includes('another-app-v1'));
});

for(const fresh of [false,true])test(fresh?'fresh manual check fails offline instead of returning stale cached news':'ordinary offline reading still returns cached news',async()=>{
 const handlers={},cached=new Response('{"generated_at":"old"}');
 let matches=0,pending;
 const context=vm.createContext({URL,Request,
  self:{location:{origin:'https://example.test'},registration:{scope:'https://example.test/notisonda/'},addEventListener:(name,fn)=>handlers[name]=fn},
  caches:{open:async()=>({match:async()=>{matches++;return cached;}})},
  fetch:async()=>{throw new Error('offline');}
 });
 vm.runInContext(fs.readFileSync(path.join(__dirname,'../web/sw.js'),'utf8'),context);
 handlers.fetch({request:new Request('https://example.test/notisonda/data/meta.json?check=123',{cache:fresh?'no-store':'no-cache'}),respondWith:promise=>{pending=promise;}});
 if(fresh){await assert.rejects(pending,/offline/);assert.equal(matches,0);}
 else{assert.equal(await pending,cached);assert.equal(matches,1);}
});
