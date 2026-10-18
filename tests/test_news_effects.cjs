"use strict";
const fs=require('node:fs');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../web/news-effects.js'),'utf8');
function node(data={}){
  const classes=new Set(),styles={};
  return {dataset:data,classes,
    classList:{add:k=>classes.add(k),remove:k=>classes.delete(k),contains:k=>classes.has(k)},
    style:{setProperty:(k,v)=>{styles[k]=v}},get offsetWidth(){return 12;}};
}
const defaultRow=node({radarSourceIds:JSON.stringify(['a','b'])});
const customRow=node({radarSourceIds:JSON.stringify(['c'])});
const untouchedRow=node({radarSourceIds:JSON.stringify(['z'])});
const card=node({articleId:'new-1'});
const oldCard=node({articleId:'old-1'});
const all=node(),header=node();
const timerCallbacks=[];
let onNew=null,reduceMotion=false;
const window={
 addEventListener:(key,fn)=>{if(key==='radar:news-added')onNew=fn;},
 setTimeout:(fn)=>{timerCallbacks.push(fn);return timerCallbacks.length;},
 clearTimeout:(id)=>{timerCallbacks[id-1]=()=>{};},
 matchMedia:()=>({matches:reduceMotion})
};
const document={
 querySelectorAll:selector=>{
  if(selector==='#libraryFolderNav .folder-entry')return [defaultRow,customRow,untouchedRow];
  if(selector==='.article-card[data-article-id]')return [card,oldCard];
  return [];
 },
 querySelector:selector=>selector.includes('nth-child(2)')?all:null,
 getElementById:()=>header
};
vm.runInNewContext(source,{window,document,console});
assert.equal(typeof onNew,'function');
const newArticle={id:'new-1',source_ids:['b','c']};
onNew({detail:{items:[newArticle]}});
assert(defaultRow.classList.contains('radar-folder-arrived'));
assert(customRow.classList.contains('radar-folder-arrived'));
assert(!untouchedRow.classList.contains('radar-folder-arrived'));
assert.equal(defaultRow.dataset.radarNew,'+1');
assert(card.classList.contains('radar-news-arrived'));
assert(!oldCard.classList.contains('radar-news-arrived'));
assert(all.classList.contains('radar-all-arrived'));
assert(header.classList.contains('radar-refresh-arrived'));
assert(!defaultRow.classList.contains('radar-news-arrived'));
for(const fn of timerCallbacks.splice(0))fn();
assert(!defaultRow.classList.contains('radar-folder-arrived'));
assert(!card.classList.contains('radar-news-arrived'));
reduceMotion=true;
onNew({detail:{items:[newArticle]}});
assert(!defaultRow.classList.contains('radar-folder-arrived'));
assert(!card.classList.contains('radar-news-arrived'));
console.log('New RSS effects: changed folders, cards, reset and reduced motion verified.');
