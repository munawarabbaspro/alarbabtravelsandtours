var WAICON='<svg class="i" width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/></svg>';
(function(){
'use strict';
var $=function(s,r){return (r||document).querySelector(s)},$$=function(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s))};
var WA=(window.SITE&&SITE.wa)||'https://wa.me/923152323811';
function toast(t){var e=$('#toast');if(!e)return;e.textContent=t;e.classList.add('show');clearTimeout(toast.t);toast.t=setTimeout(function(){e.classList.remove('show')},3200)}
function waFor(dest){var S=window.SITE||{},d=(dest||'').toLowerCase(),l=S.sch||[];for(var i=0;i<l.length;i++){if(d.indexOf(l[i])>-1)return S.waS||WA}return S.waA||WA}
function openWA(msg,dest){window.open((dest?waFor(dest):WA)+'?text='+encodeURIComponent(msg),'_blank','noopener')}
/* mobile menu */
var bg=$('.burger'),menu=$('#menu');
if(bg&&menu)bg.addEventListener('click',function(){var o=menu.classList.toggle('open');bg.setAttribute('aria-expanded',o)});
/* Visas dropdown: close on outside click or Escape */
document.addEventListener('click',function(e){$$('details.dd[open]').forEach(function(d){if(!d.contains(e.target))d.removeAttribute('open')})});
document.addEventListener('keydown',function(e){if(e.key==='Escape')$$('details.dd[open]').forEach(function(d){d.removeAttribute('open');var s=$('summary',d);if(s)s.focus()})});
/* scroll reveal */
if('IntersectionObserver' in window){
var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{threshold:.1});
$$('.reveal').forEach(function(e){io.observe(e)});
}else{$$('.reveal').forEach(function(e){e.classList.add('in')})}
/* animated counters */
$$('[data-count]').forEach(function(el){
var end=+el.dataset.count,suf=el.dataset.suffix||'',t0=null;
function f(t){if(!t0)t0=t;var k=Math.min(1,(t-t0)/1600);el.textContent=Math.round(end*(1-Math.pow(1-k,3))).toLocaleString('en-US')+suf;if(k<1)requestAnimationFrame(f)}
if('IntersectionObserver' in window){var o=new IntersectionObserver(function(es){if(es[0].isIntersecting){requestAnimationFrame(f);o.disconnect()}});o.observe(el)}else el.textContent=end.toLocaleString('en-US')+suf;
});
/* hero: destinations, flight route, live weather */
var DEST=window.DEST;
if(DEST&&$('#photoA')){
var idx=0,timer,photos=[$('#photoA'),$('#photoB')],pi=0;
var wxReady=false;/* live weather is fetched only after the page has loaded, so the hero paints without a third-party request */
window.addEventListener('load',function(){setTimeout(function(){wxReady=true;weather(DEST[idx])},1500)});
var 
mq=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
var tabs=$('#dtabs');
DEST.forEach(function(d,i){var b=document.createElement('button');b.type='button';b.textContent=d.n;b.setAttribute('aria-pressed',i===0);b.onclick=function(){show(i,true)};tabs.appendChild(b)});
/* live weather: Open-Meteo (current conditions for the destination's coordinates, local time of that place), refreshed every 10 minutes */
var WXI={
sun:'<svg viewBox="0 0 64 64" aria-hidden="true"><g stroke="#ffd45e" stroke-width="4" stroke-linecap="round"><path d="M32 6v7M32 51v7M6 32h7M51 32h7M13.6 13.6l5 5M45.4 45.4l5 5M13.6 50.4l5-5M45.4 18.6l5-5"/></g><circle cx="32" cy="32" r="12" fill="#ffd45e"/></svg>',
moon:'<svg viewBox="0 0 64 64" aria-hidden="true"><path d="M44 46A20 20 0 0 1 26 10a20 20 0 1 0 28 30 20 20 0 0 1-10 6z" fill="#e8ecff"/></svg>',
pcloud:'<svg viewBox="0 0 64 64" aria-hidden="true"><g stroke="#ffd45e" stroke-width="3.5" stroke-linecap="round"><path d="M22 6v5M8 20H3M41 20h5M12 10l3.5 3.5M32 10l-3.5 3.5"/></g><circle cx="22" cy="24" r="9" fill="#ffd45e"/><path d="M20 52h26a11 11 0 0 0 1.5-21.9A15 15 0 0 0 19 34a9 9 0 0 0 1 18z" fill="#fff"/></svg>',
pmoon:'<svg viewBox="0 0 64 64" aria-hidden="true"><path d="M28 24a10 10 0 1 1-8-16 8 8 0 0 0 8 16z" fill="#e8ecff"/><path d="M20 52h26a11 11 0 0 0 1.5-21.9A15 15 0 0 0 19 34a9 9 0 0 0 1 18z" fill="#fff"/></svg>',
cloud:'<svg viewBox="0 0 64 64" aria-hidden="true"><path d="M17 50h29a12 12 0 0 0 1.6-23.9A16 16 0 0 0 16 30a10 10 0 0 0 1 20z" fill="#fff"/></svg>',
fog:'<svg viewBox="0 0 64 64" aria-hidden="true"><path d="M17 38h29a12 12 0 0 0 1.6-23.9A16 16 0 0 0 16 18a10 10 0 0 0 1 20z" fill="#fff"/><g stroke="#dfe9ee" stroke-width="4" stroke-linecap="round"><path d="M14 46h36M20 54h30"/></g></svg>',
rain:'<svg viewBox="0 0 64 64" aria-hidden="true"><path d="M17 38h29a12 12 0 0 0 1.6-23.9A16 16 0 0 0 16 18a10 10 0 0 0 1 20z" fill="#fff"/><g stroke="#7cc4ff" stroke-width="4" stroke-linecap="round"><path d="M22 46l-3 8M34 46l-3 8M46 46l-3 8"/></g></svg>',
snow:'<svg viewBox="0 0 64 64" aria-hidden="true"><path d="M17 38h29a12 12 0 0 0 1.6-23.9A16 16 0 0 0 16 18a10 10 0 0 0 1 20z" fill="#fff"/><g fill="#cfe8ff"><circle cx="22" cy="48" r="3"/><circle cx="34" cy="53" r="3"/><circle cx="46" cy="48" r="3"/></g></svg>',
storm:'<svg viewBox="0 0 64 64" aria-hidden="true"><path d="M17 36h29a12 12 0 0 0 1.6-23.9A16 16 0 0 0 16 16a10 10 0 0 0 1 20z" fill="#e3e9ee"/><path d="M34 34l-9 14h7l-3 12 12-16h-8z" fill="#ffd45e"/></svg>'};
function wxInfo(c,day){
if(c===0)return day?['Clear sky','sun']:['Clear night','moon'];
if(c===1)return day?['Mostly clear','sun']:['Mostly clear','moon'];
if(c===2)return ['Partly cloudy',day?'pcloud':'pmoon'];
if(c===3)return ['Overcast','cloud'];
if(c===45||c===48)return ['Fog','fog'];
if(c>=51&&c<=57)return ['Drizzle','rain'];
if(c>=61&&c<=67)return ['Rain','rain'];
if(c>=71&&c<=77||c===85||c===86)return ['Snow','snow'];
if(c>=80&&c<=82)return ['Rain showers','rain'];
if(c>=95)return ['Thunderstorm','storm'];
return ['Cloudy','cloud'];
}
function clock(t){var m=/T(\d\d):(\d\d)/.exec(t||'');if(!m)return '';var h=+m[1],ap=h<12?'AM':'PM';h=h%12||12;return h+':'+m[2]+' '+ap}
function weather(d,quiet){
var w=$('.weather');$('#wplace').textContent=d.city.split(' (')[0];
if(!quiet){$('#wdesc').textContent='Loading live weather…';w.classList.add('wx-load')}
fetch('https://api.open-meteo.com/v1/forecast?latitude='+d.lat+'&longitude='+d.lon+'&current=temperature_2m,apparent_temperature,relative_humidity_2m,is_day,weather_code,wind_speed_10m&daily=temperature_2m_max,temperature_2m_min&forecast_days=1&timezone=auto')
.then(function(r){if(!r.ok)throw 0;return r.json()}).then(function(j){
if(DEST[idx]!==d)return;/* the visitor already moved to another destination */
var c=j.current,x=wxInfo(c.weather_code,c.is_day===1),dl=j.daily||{};
$('#temp').textContent=Math.round(c.temperature_2m);
$('#wico').innerHTML=WXI[x[1]];$('#wdesc').textContent=x[0];
$('#wfeel').textContent=Math.round(c.apparent_temperature)+'°';
$('#wwind').textContent=Math.round(c.wind_speed_10m)+' km/h';
$('#whum').textContent=c.relative_humidity_2m+'%';
$('#whl').textContent=dl.temperature_2m_max?Math.round(dl.temperature_2m_max[0])+'° / '+Math.round(dl.temperature_2m_min[0])+'°':'--';
$('#wtime').textContent=clock(c.time)+' local';
w.classList.remove('wx-load');w.classList.remove('wx-err')})
.catch(function(){$('#wdesc').textContent='Live weather unavailable';w.classList.remove('wx-load');w.classList.add('wx-err')});
}
setInterval(function(){if(wxReady&&!document.hidden)weather(DEST[idx],true)},600000);
function draw(){var w=$('#vvw');if(!w)return;w.classList.remove('go');void w.offsetWidth;w.classList.add('go')}
function show(i,user,first){
idx=i;var d=DEST[i];
$$('#dtabs button').forEach(function(b,k){b.setAttribute('aria-pressed',k===i)});
var nxt=photos[1-pi],cur=photos[pi];
if(!first&&!window.HERO_NOPHOTO){nxt.onload=function(){nxt.classList.add('on');cur.classList.remove('on');pi=1-pi};
// srcset would override src and keep showing the first photo, so drop it before swapping
nxt.removeAttribute('srcset');nxt.removeAttribute('sizes');
nxt.alt=d.n+' – '+d.city+' travel and visa packages from Islamabad';nxt.src=innerWidth>1000?d.img:d.img.replace('-2000.webp','-1000.webp').replace('w=2000','w=1100')}/* first call: the page already shows slide 1, do not download it a second time */
$('#f3t').textContent=d.visa;if($('#gfn')){$('#gfn').textContent=d.n;$('#gfn').nextElementSibling.textContent=d.visa}
var vk=$('#vvk');if(vk){vk.textContent=d.code;$('#vvy').textContent=d.city.split(' (')[0];var vl=$('#vvl');vl.setAttribute('href',d.url);vl.textContent=d.n+' guide →'}
$('#hlink').setAttribute('href',d.url);$('#hlink').textContent=d.n+' visa guide →';
draw(d);if(wxReady)weather(d);else $('#wplace').textContent=d.city.split(' (')[0];
sched(user?6500:(first?9000:4500));
if(!first&&wxReady){var nx=DEST[(i+1)%DEST.length];(new Image()).src=innerWidth>1000?nx.img:nx.img.replace('-2000.webp','-1000.webp').replace('w=2000','w=1100')}/* the next photo is fetched only after the page has settled, so it never competes with the first one */
}
/* auto-rotation: stops on a Pause button (WCAG 2.2.2), while the pointer or keyboard focus is in the hero, and on touch */
var paused=false,hov=false,pbtn=$('#dpause'),hero=$('.hero');
function sched(ms){clearInterval(timer);if(!mq&&!paused&&!hov)timer=setInterval(function(){show((idx+1)%DEST.length)},ms||4500)}
function hold(v){hov=v;if(v)clearInterval(timer);else sched()}
show(0,false,true);
/* no pause on hover: the photos keep changing while the pointer is over the hero (the Pause button stops them) */
hero.addEventListener('focusin',function(){hold(true)});hero.addEventListener('focusout',function(){hold(false)});
hero.addEventListener('touchstart',function(){clearInterval(timer);sched(8000)},{passive:true});
if(pbtn){
if(mq){pbtn.hidden=true}
var PI=pbtn.innerHTML,PLAY='<svg class="i" width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" focusable="false"><path d="M8 4.5v15l11-7.5z"/></svg>';
pbtn.addEventListener('click',function(){paused=!paused;pbtn.setAttribute('aria-pressed',paused);
pbtn.setAttribute('aria-label',paused?'Play the destination slideshow':'Pause the destination slideshow');
pbtn.innerHTML=paused?PLAY:PI;if(paused)clearInterval(timer);else sched()});
}
}
/* forms → WhatsApp / mailto (static site, no backend) */
var sf=$('#searchForm');
if(sf)sf.addEventListener('submit',function(e){e.preventDefault();var f=new FormData(sf),q=String(f.get('to')||'').trim().toLowerCase();
var hit=(window.FIND||[]).filter(function(x){return x[0].toLowerCase()===q})[0]||((window.FIND||[]).filter(function(x){return q.length>2&&x[0].toLowerCase().indexOf(q)===0})[0]);
if(hit){location.href=hit[1];return}
openWA('Hi AL ARBAB TRAVEL AND TOURS, I want to plan a trip.\nDestination: '+(f.get('to')||'-')+'\nCheck-in: '+(f.get('in')||'-')+'\nCheck-out: '+(f.get('out')||'-')+'\nTravelers: '+f.get('pax'),f.get('to'));});
var cf=$('#contactForm');
if(cf)cf.addEventListener('submit',function(e){e.preventDefault();var f=new FormData(cf);
openWA('New inquiry from website\nName: '+f.get('name')+'\nEmail: '+f.get('email')+'\nWhatsApp: '+f.get('phone')+'\nDestination: '+f.get('dest')+'\nDetails: '+(f.get('msg')||'-'),f.get('dest'));toast('Opening WhatsApp with your inquiry…')});
var nf=$('#nlForm');
if(nf)nf.addEventListener('submit',function(e){e.preventDefault();var m=$('input',nf).value;window.location.href='mailto:'+((window.SITE&&SITE.email)||'alarbabtravels@gmail.com')+'?subject='+encodeURIComponent('Newsletter subscription')+'&body='+encodeURIComponent('Please subscribe: '+m);toast('Thanks! Confirm the email to finish subscribing.')});
/* country finder */
var fi=$('#finder');
if(fi){var out=$('#finderCount'),tiles=$$('[data-name]'),groups=$$('[data-group]');
fi.addEventListener('input',function(){var q=fi.value.trim().toLowerCase(),n=0;
tiles.forEach(function(t){var ok=!q||t.dataset.name.indexOf(q)>-1;t.hidden=!ok;if(ok)n++});
groups.forEach(function(g){g.hidden=!$$('[data-name]:not([hidden])',g).length});
out.textContent=q?n+' destination'+(n===1?'':'s')+' found':''});}
/* airline filter */
var at=$('#airTabs');
if(at)at.addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;
$$('#airTabs button').forEach(function(x){x.setAttribute('aria-pressed',x===b)});
var r=b.dataset.r;$$('.air').forEach(function(a){a.hidden=!(r==='all'||a.dataset.region===r)})});
})();
/* office open/closed status (Pakistan time, Mon–Sat 9:00–20:00) */
(function(){var els=document.querySelectorAll('[data-open-status]');if(!els.length)return;
var now=new Date(),pk=new Date(now.getTime()+now.getTimezoneOffset()*60000+5*3600000),d=pk.getDay(),h=pk.getHours()+pk.getMinutes()/60;
var open=d>=1&&d<=6&&h>=9&&h<20,txt;
if(open)txt='Office open now · until 8 PM';
else{var nd=(d===6&&h>=20)||d===0?'Monday':(h<9?'today':'tomorrow');txt='Office closed · opens 9 AM '+nd+' · WhatsApp us and we reply during office hours'}
els.forEach(function(el){el.textContent=txt;el.classList.add(open?'is-open':'is-closed')});})();
/* free eligibility check */
(function(){var f=document.getElementById('eligForm'),out=document.getElementById('eligOut');if(!f||!window.ELIG)return;
var EX={emp:['Employment letter on company letterhead (with salary and leave approval)','Last 3 months salary slips'],
biz:['Chamber of Commerce / business registration certificate','NTN and last 2–3 years income tax returns','Business bank statement (last 6 months)'],
stu:['Student ID card or enrolment letter from your institute','Sponsor’s (parent’s) bank statement, income proof and CNIC'],
dep:['Sponsor’s (spouse/child) bank statement and income proof','Relationship proof: NADRA FRC or marriage certificate']};
var P={t:'Tourism / holiday',f:'Family / friends visit',b:'Business / conference'},S={emp:'Employed',biz:'Business owner',stu:'Student',dep:'Housewife / retired / dependant'},
Hs={none:'No previous foreign travel',some:'Gulf / Asia visas',strong:'UK / USA / Schengen visas'};
var q=new URLSearchParams(location.search).get('d');if(q&&ELIG[q])f.d.value=q;
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
f.addEventListener('submit',function(e){e.preventDefault();var c=ELIG[f.d.value];if(!c){f.d.focus();return}
var docs=(f.p.value==='b'?c.b:c.t).slice(),extra=EX[f.s.value]||[];
if(f.p.value==='f')extra=extra.concat(['Invitation letter from your host abroad with their ID / residence copy']);
var tip=f.h.value==='none'?'First-time travellers: a strong cover letter and clear ties to Pakistan matter most. Our adviser helps you build both.':
f.h.value==='strong'?'Your previous UK / USA / Schengen visas strengthen the file — include copies of all of them.':'Include copies of your previous visas and travel stamps.';
var msg='Hi AL ARBAB TRAVEL AND TOURS, please check my file.\nDestination: '+c.n+'\nPurpose: '+P[f.p.value]+'\nSituation: '+S[f.s.value]+'\nTravel history: '+Hs[f.h.value];
out.innerHTML='<h2>Your '+esc(c.n)+' checklist</h2><ul class="out-docs">'+docs.map(function(x){return'<li>'+esc(x)+'</li>'}).join('')+extra.map(function(x){return'<li class="extra">'+esc(x)+' <small>(for your situation)</small></li>'}).join('')+'</ul>'+
'<p class="note">'+esc(tip)+'</p><p style="margin-top:14px;display:flex;gap:10px;flex-wrap:wrap"><a class="btn wa" target="_blank" rel="noopener" href="'+waFor(c.n)+'?text='+encodeURIComponent(msg)+'">'+WAICON+' Send my file for a free check</a><a class="btn light" href="'+c.u+'">Full '+esc(c.n)+' visa guide</a></p>';
out.hidden=false;out.scrollIntoView({behavior:'smooth',block:'start'});});})();
/* analytics: count WhatsApp and call clicks when GA4 is configured */
document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[href^="tel:"],a[href*="wa.me"]');if(!a||typeof window.gtag!=='function')return;
window.gtag('event',a.href.indexOf('tel:')===0?'phone_call_click':'whatsapp_click',{link_url:a.href,page_path:location.pathname});});
/* book cards: tap to open on touch screens (no hover) */
document.addEventListener('click',function(e){var c=e.target.closest&&e.target.closest('.book .cover');if(c)c.parentNode.classList.add('open')});
/* click-to-load Google Map */
document.addEventListener('click',function(e){var b=e.target.closest&&e.target.closest('.map-facade button');if(!b)return;var box=b.parentNode,f=document.createElement('iframe');
f.className='map';f.title=box.dataset.title||'Map';f.src=box.dataset.src;f.setAttribute('loading','lazy');box.replaceWith(f)});
/* home: fill destination suggestions from window.FIND (keeps the HTML small) */
(function(){var dl=document.getElementById('destlist');if(!dl||!window.FIND)return;var done=false;
function fill(){if(done)return;done=true;var h='';window.FIND.forEach(function(x){h+='<option value="'+x[0].replace(/"/g,'&quot;')+'">'});dl.innerHTML=h}
var inp=document.getElementById('to');if(inp){inp.addEventListener('focus',fill);inp.addEventListener('input',fill)}})();
