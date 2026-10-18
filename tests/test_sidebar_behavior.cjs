"use strict";
// Fast behavioral smoke test for desktop sizing, drag/pointer cancel,
// accessible keyboard controls, local settings and mobile adaptation.
const fs=require('node:fs');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const path=require('node:path');
const script=fs.readFileSync(path.join(__dirname,'../web/sidebar-layout.js'),'utf8');
const style={};
const makeNode=()=>({
  attributes:{},listeners:{},value:'',disabled:false,tabIndex:0,textContent:'',
  addEventListener(name,handler){(this.listeners[name]??=[]).push(handler);},
  setAttribute(k,v){this.attributes[k]=v;},
  setPointerCapture(id){this.capture=id;},
  releasePointerCapture(id){if(this.capture===id)delete this.capture;},
  dispatch(name,args={}){for(const fn of this.listeners[name]||[])fn({button:0,pointerId:1,clientX:0,preventDefault(){},...args});}
});
const handle=makeNode(),slider=makeNode(),output=makeNode(),reset=makeNode(),help=makeNode();
const elements={sidebarResizeHandle:handle,settingSidebarWidth:slider,sidebarWidthValue:output,
 resetSidebarWidth:reset,sidebarWidthHelp:help};
const classes=new Set(['radar-hybrid']);
const storage=new Map();
const windowListeners={};
const window={
 innerWidth:1440,
 addEventListener(name,fn){(windowListeners[name]??=[]).push(fn);},
 emit(name,details={}){for(const fn of windowListeners[name]||[])fn(details);}
};
const context={
 window,localStorage:{getItem:k=>storage.has(k)?storage.get(k):null,
  setItem:(k,v)=>storage.set(k,String(v)),removeItem:k=>storage.delete(k)},
 document:{
  body:{classList:{contains:c=>classes.has(c),add:c=>classes.add(c),remove:c=>classes.delete(c)}},
  documentElement:{style:{setProperty:(k,v)=>{style[k]=v}}},
  getElementById:id=>elements[id]
 },console
};
vm.runInNewContext(script,context,{filename:'sidebar-layout.js'});
const width=()=>style['--radar-sidebar-width'];
assert.equal(width(),'310px','initial desktop sidebar');
assert.equal(slider.disabled,false);
assert.equal(handle.attributes['aria-valuenow'],'310');
handle.dispatch('keydown',{key:'ArrowRight'});
assert.equal(width(),'326px');
assert.equal(storage.get('radar-sidebar-width'),'326');
handle.dispatch('keydown',{key:'Home'});
assert.equal(width(),'240px');
handle.dispatch('keydown',{key:'End'});
assert.equal(width(),'480px');
handle.dispatch('dblclick');
assert.equal(width(),'310px');
assert.equal(storage.has('radar-sidebar-width'),false,'double click clears override');
// Pointer drag commits, pointercancel restores.
handle.dispatch('pointerdown',{clientX:310,pointerId:1});
handle.dispatch('pointermove',{clientX:380,pointerId:1});
assert.equal(width(),'380px');
handle.dispatch('pointerup',{clientX:380,pointerId:1});
assert.equal(storage.get('radar-sidebar-width'),'380');
handle.dispatch('pointerdown',{clientX:380,pointerId:2});
handle.dispatch('pointermove',{clientX:410,pointerId:2});
assert.equal(width(),'410px');
handle.dispatch('pointercancel',{clientX:410,pointerId:2});
assert.equal(width(),'380px');
assert.equal(storage.get('radar-sidebar-width'),'380');
// Constrained desktop viewport, preserve user preference for larger screens.
window.innerWidth=960;
window.emit('resize');
assert.equal(width(),'380px'); // viewport limit 420, saved width remains 380
window.innerWidth=1000;
window.emit('resize');
slider.value='460';
slider.dispatch('input');
assert.equal(width(),'460px');
window.innerWidth=970;
window.emit('resize');
assert.equal(width(),'430px','clamp to available content width');
assert.equal(storage.get('radar-sidebar-width'),'460','keep preferred width when constrained');
// Mobile becomes one-column via CSS, no custom resizing.
window.innerWidth=700;
window.emit('resize');
assert.equal(slider.disabled,true);
assert.equal(handle.tabIndex,-1);
window.innerWidth=1440;
window.emit('resize');
assert.equal(width(),'460px','restore width on desktop');
storage.set('radar-sidebar-width','350');
window.emit('radar-sidebar-pref-sync');
assert.equal(width(),'350px','restore from imported backup');
storage.delete('radar-sidebar-width');
window.emit('radar-sidebar-pref-sync');
assert.equal(width(),'310px','reset settings synchronization');
reset.dispatch('click');
assert.equal(width(),'310px');
console.log('Sidebar behavior verified: keyboard, drag, cancel, viewport, backup, reset.');
