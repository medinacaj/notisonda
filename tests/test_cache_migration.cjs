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
