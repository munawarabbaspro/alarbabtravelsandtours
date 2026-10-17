(function(){
var PAL=[['Red','#e0150f','#1a1a1c'],['Brand green','#0e7f3e','#091413'],['Teal','#00a3b4','#0b1c26'],['Gold','#d99a1e','#141311'],['Royal blue','#1767b3','#101828'],['Orange','#f26a2e','#14352c'],['Maroon','#a31545','#2a0f18'],['Violet','#6a4bd8','#1a1033']];
var PLANE='M22,0 C22,-2 20,-3 17,-3 L4,-3 L-4,-17 L-9,-17 L-5,-3 L-14,-3 L-17,-8 L-20,-8 L-17,0 L-20,8 L-17,8 L-14,3 L-5,3 L-9,17 L-4,17 L4,3 L17,3 C20,3 22,2 22,0 Z';
var BLADE='M170,30 C146,38 120,58 102,84 C84,110 70,134 54,148 C42,158 30,152 30,138 C30,126 36,116 44,110 C34,120 24,134 28,152 C31,172 60,178 86,160 C114,140 140,106 158,76 C165,63 169,46 170,30 Z';
var F='font-family="Archivo,Arial Black,sans-serif"';
var st={p:0,plane:'tip',wall:'night'};
function mk(a,ink,plane,sh){
  /* sh = offset copy for the 3D sign look */
  var b='<path d="'+BLADE+'" fill="'+a+'"/>';
  if(plane==='tip')b+='<g transform="translate(184,20) rotate(-38) scale(.95)"><path d="'+PLANE+'" fill="'+ink+'"/></g><g fill="'+a+'"><circle cx="150" cy="22" r="3.4" opacity=".9"/><circle cx="136" cy="30" r="2.6" opacity=".65"/><circle cx="124" cy="38" r="1.9" opacity=".4"/></g>';
  if(plane==='in')b+='<g transform="translate(98,96) rotate(-52) scale(.78)"><path d="'+PLANE+'" fill="#fff"/></g>';
  return b;
}
function logo(a,ink,plane,opt){
  opt=opt||{};var sub=opt.sub||ink,d=opt.depth;
  var inner=function(dx,dy,aa,ii,ss){return '<g transform="translate('+dx+','+dy+')">'+'<g transform="translate(0,6)">'+mk(aa,ii,plane)+'</g>'+
    '<text x="194" y="86" '+F+' font-size="82" font-weight="900" letter-spacing="-1"><tspan fill="'+aa+'">AL</tspan><tspan fill="'+ii+'" dx="12">ARBAB</tspan></text>'+
    '<text x="198" y="126" '+F+' font-size="21" font-weight="800" letter-spacing="9.5" fill="'+ss+'">TRAVEL &amp; TOURS</text></g>'};
  var s='<svg viewBox="-6 -4 748 190" role="img" aria-label="AL ARBAB Travel and Tours">';
  if(d)s+=inner(5,5,opt.back,opt.back,opt.back);
  s+=inner(0,0,a,ink,sub)+'</svg>';
  return s;
}
function tile(a,plane){return '<svg viewBox="0 0 200 200"><rect width="200" height="200" rx="46" fill="'+a+'"/><g transform="translate(10,6) scale(.9)">'+mk('#fff','#fff',plane==='in'?'in':plane)+'</g></svg>'}
function $(s){return document.querySelector(s)}
function scene(a,ink,plane,light){
  var wall=light?'light':'night';
  return '<div class="sc '+wall+'"><div class="led"></div><div class="slats"></div><div class="glass"></div><div class="sign">'+logo(a,light?ink:'#f3eee6',plane,{depth:true,back:light?'rgba(0,0,0,.55)':'rgba(0,0,0,.7)',sub:light?ink:'#f3eee6'})+'</div><div class="plants"></div></div>';
}
function render(){
  var p=PAL[st.p],a=p[1],ink=p[2],pl=st.plane;
  $('#lsMain').innerHTML=scene(a,ink,pl,st.wall==='light');
  $('#lsMain').style.setProperty('--glow',a);
  $('#lsAll').innerHTML=PAL.map(function(q,i){return '<button type="button" class="ac" data-p="'+i+'" aria-pressed="'+(i===st.p)+'">'+scene(q[1],q[2],pl,true)+'<b>'+q[0]+'</b></button>'}).join('');
  document.querySelectorAll('#lsAll .ac').forEach(function(b){b.onclick=function(){st.p=+b.dataset.p;render();$('#lsMain').scrollIntoView({block:'center',behavior:'smooth'})}});
  /* fit on the site */
  $('#fHead').innerHTML='<div class="hd"><span class="hm">'+'<svg viewBox="0 0 200 200">'+mk(a,ink,pl)+'</svg></span><span class="hn"><b>AL <i style="color:'+a+'">ARBAB</i></b><small>TRAVEL &amp; TOURS</small></span></div>';
  $('#fHero').innerHTML='<div class="hero"><div class="chip">'+logo('#fff','#fff',pl,{sub:'#e8f3ef'}).replace('<tspan fill="#fff">AL</tspan>','<tspan fill="'+a+'">AL</tspan>')+'</div></div>';
  $('#fFoot').innerHTML='<div class="foot">'+logo(a,'#f6f1e8',pl,{sub:'#a9b8b2'})+'</div>';
  $('#fFav').innerHTML=[96,48,32,16].map(function(n){return '<span style="width:'+n+'px;height:'+n+'px">'+tile(a,pl)+'</span>'}).join('');
  $('#fSplash').innerHTML='<div class="spl"><div class="lg">'+logo(a,'#fff',pl,{sub:'#9fb0ab'})+'</div></div>';
  document.querySelectorAll('.ls-pal button').forEach(function(b,i){b.setAttribute('aria-pressed',i===st.p)});
  document.querySelectorAll('.ls-pl button').forEach(function(b){b.setAttribute('aria-pressed',b.dataset.v===st.plane)});
  document.querySelectorAll('.ls-wall button').forEach(function(b){b.setAttribute('aria-pressed',b.dataset.v===st.wall)});
  $('#lsName').textContent=p[0]+' · plane: '+({tip:'flying off the tip',in:'inside the swoosh',off:'none'})[pl];
}
$('.ls-pal').innerHTML='<b>Colour:</b>'+PAL.map(function(p,i){return '<button type="button" data-p="'+i+'"><i style="background:'+p[1]+'"></i>'+p[0]+'</button>'}).join('');
document.querySelectorAll('.ls-pal button').forEach(function(b,i){b.onclick=function(){st.p=i;render()}});
document.querySelectorAll('.ls-pl button').forEach(function(b){b.onclick=function(){st.plane=b.dataset.v;render()}});
document.querySelectorAll('.ls-wall button').forEach(function(b){b.onclick=function(){st.wall=b.dataset.v;render()}});
var q=location.search,mp=q.match(/[?&]p=(\d)/),mv=q.match(/[?&]plane=(tip|in|off)/);if(mp)st.p=Math.min(PAL.length-1,+mp[1]);if(mv)st.plane=mv[1];
render();
})();
