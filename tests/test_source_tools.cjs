'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const file=require('node:path').join(__dirname,'../web/source-tools.js');
const tools=fs.existsSync(file)?require(file):{};
const sources=[
 {id:'one',name:'MEDIO — Ciencia Única',category:'01 - Ciencia',url:'https://example.com/rss?a=1&b=2',website:'https://example.com',is_radar:false},
 {id:'two',name:'RADAR — Mundo',category:'03 - Internacionales',url:'https://news.google.com/rss/search?q=world',website:'https://portal.test',is_radar:true},
 {id:'three',name:'Ciencia Única',category:'01 - Ciencia',url:'https://other.test/atom',website:'https://other.test',is_radar:false}
];
test('feed identity allows only public http(s) syntax and preserves significant query order',()=>{
 assert.equal(typeof tools.feedKey,'function');
 assert.equal(tools.feedKey(' HTTPS://EXAMPLE.com:443/rss?a=1&b=2#top '),sources[0].url);
 for(const url of ['javascript:alert(1)','data:text/xml,hi','https://name:secret@example.com/rss','/rss'])assert.equal(tools.feedKey(url),'');
 assert.notEqual(tools.feedKey('http://example.com/rss'),tools.feedKey('https://example.com/rss'));
 assert.notEqual(tools.feedKey('https://example.com/rss?b=2&a=1'),tools.feedKey(sources[0].url));
});
test('search finds RSS/domain/current folder without accents and combines visibility/health/type',()=>{
 assert.equal(typeof tools.filterSources,'function');
 const options={hiddenIds:new Set(['three']),healthById:new Map([['one',{state:'ok'}],['two',{state:'error'}]]),foldersById:new Map([['one',['Investigación']],['two',['Mundo']]])};
 for(const query of ['investigacion','example.com/rss','CIENCIA UNICA'])assert.deepEqual(tools.filterSources(sources,{...options,query,visibility:'visible'}).map(s=>s.id),['one']);
 assert.deepEqual(tools.filterSources(sources,{...options,type:'radar',status:'error'}).map(s=>s.id),['two']);
 assert.deepEqual(tools.filterSources(sources,{...options,visibility:'hidden',status:'unknown'}).map(s=>s.id),['three']);
 assert.deepEqual(tools.filterSources(sources,{...options,folder:'Investigación'}).map(s=>s.id),['one']);
 assert.equal(tools.healthState({state:'invented'}),'unknown');
});
test('OPML export preserves personal folder names, overlaps, safe URLs and unassigned sources',()=>{
 assert.equal(typeof tools.buildOPML,'function');
 const xml=tools.buildOPML([{name:'Mi <ciencia> & más',ids:['one','one']},{name:'Lectura',ids:['one','two']}],sources,new Set(['two']));
 assert.match(xml,/Mi &lt;ciencia&gt; &amp; más/);
 assert.equal((xml.match(/xmlUrl="https:\/\/example.com/g)||[]).length,2);
 assert.ok(!xml.includes('news.google.com'));
 assert.match(xml,/Sin carpeta/);
 assert.match(xml,/other.test\/atom/);
 assert.match(xml,/a=1&amp;b=2/);
});
test('OPML matching uses URL, counts duplicates, preserves multiple memberships, reports unknown/unsafe',()=>{
 assert.equal(typeof tools.matchOPML,'function');
 const records=[{name:'Wrong name',url:sources[0].url+'#top',folder:'A'},{name:'Duplicate',url:sources[0].url,folder:'A'},
 {url:sources[0].url,folder:'B'},{name:sources[0].name,url:'https://example.com/unregistered',folder:'A'},
 {url:'javascript:alert(1)',folder:'A'},{url:sources[1].url,folder:'A'}];
 const result=tools.matchOPML(records,sources);
 assert.deepEqual(result.matched.map(r=>[r.id,r.folder]),[['one','A'],['one','B'],['two','A']]);
 assert.equal(result.knownCount,2);assert.equal(result.duplicates,2);
 assert.equal(result.unknown.length,2);assert.equal(result.unknown[1].reason,'URL no admitida');
 assert.equal(result.total,6);
});
test('CSV export includes explicit addresses/state and neutralizes spreadsheet formulas',()=>{
 assert.equal(typeof tools.buildCSV,'function');
 const csv=tools.buildCSV([{id:'x',name:'=WEBSERVICE("bad")',rss:'https://example.com/rss',website:'https://example.com',folders:'+injected',type:'RSS directo',visible:false,status:'unknown'}]);
 assert.match(csv,/URL RSS/);assert.match(csv,/https:\/\/example.com\/rss/);
 assert.match(csv,/'=WEBSERVICE/);assert.match(csv,/'\+injected/);
 assert.match(csv,/Oculta/);assert.match(csv,/Sin diagnóstico/);
});
