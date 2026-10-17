// SEO/link sanity check for dist/
const fs=require('fs'),path=require('path');const D=path.join(__dirname,'..','dist');
const files=[];(function w(d){for(const f of fs.readdirSync(d)){const p=path.join(d,f);if(fs.statSync(p).isDirectory())w(p);else if(f.endsWith('.html'))files.push(p)}})(D);
const exists=u=>{u=u.split('#')[0].split('?')[0];if(u==='/')return true;const p=path.join(D,u);return fs.existsSync(path.join(p,'index.html'))||fs.existsSync(p)};
const titles={},descs={},bad=[],broken=new Set();let ld=0;
for(const f of files){const h=fs.readFileSync(f,'utf8'),rel='/'+path.relative(D,f).split(path.sep).join('/');
 const t=(h.match(/<title>([^<]*)<\/title>/)||[])[1]||'',d=((h.match(/<meta name="description" content="([^"]*)"/)||[])[1]||'').replace(/&amp;/g,'&').replace(/&quot;/g,'"');
 const noindex=/noindex/.test(h);
 (titles[t]=titles[t]||[]).push(rel);(descs[d]=descs[d]||[]).push(rel);
 const h1=(h.match(/<h1[\s>]/g)||[]).length;
 const tl=t.replace(/&amp;/g,'&').length;
 if(!noindex&&(tl>65||tl<25))bad.push(`title ${tl}: ${rel} :: ${t}`);
 if(!noindex&&(d.length>165||d.length<70))bad.push(`desc ${d.length}: ${rel}`);
 if(h1!==1)bad.push(`h1=${h1}: ${rel}`);
 for(const m of h.matchAll(/<script type="application\/ld\+json">(.*?)<\/script>/g)){try{JSON.parse(m[1]);ld++}catch(e){bad.push('ld-json: '+rel)}}
 for(const m of h.matchAll(/<img\b[^>]*>/g))if(!/\salt="/.test(m[0]))bad.push('img no alt: '+rel);
 for(const m of h.matchAll(/href="(\/[^"]*)"/g))if(!m[1].startsWith('//')&&!exists(m[1]))broken.add(m[1]+'  <- '+rel);
}
const dupT=Object.entries(titles).filter(([t,a])=>a.length>1).map(([t,a])=>t+' x'+a.length);
const dupD=Object.entries(descs).filter(([t,a])=>a.length>1).map(([t,a])=>t.slice(0,60)+' x'+a.length);
console.log(JSON.stringify({pages:files.length,ldBlocks:ld,issues:bad.slice(0,40),issueCount:bad.length,broken:[...broken].slice(0,20),brokenCount:broken.size,dupTitles:dupT,dupDescs:dupD.slice(0,10)},null,1));
