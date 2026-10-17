(function(){
var PAL=[
 ['red','Red & Charcoal','#e0150f','#1a1a1c'],
 ['green','Brand Green & Ink','#0e7f3e','#091413'],
 ['teal','Teal & Navy','#00a3b4','#0b1c26'],
 ['gold','Gold & Black','#d99a1e','#111111'],
 ['blue','Royal Blue & Slate','#1767b3','#101828'],
 ['orange','Orange & Deep Green','#f26a2e','#14352c']];
var CON=['Blade + wordmark','Monogram tile','Stacked arc'];
var st={c:0,p:0,wall:'light'};
var F='font-family="Archivo,Arial Black,sans-serif"';
/* the blade/wing mark: original curved shape with a small arrow cut-out, drawn in a 130 x 150 box */
function blade(a,x,y,s){return '<g transform="translate('+x+','+y+') scale('+s+')"><path d="M14,140 C4,94 30,50 74,25 C92,14 112,9 128,11 C106,22 92,37 84,57 C76,77 74,105 82,136 C60,118 36,122 14,140 Z" fill="'+a+'"/><path d="M38,98 L72,72 L66,98 L58,92 Z" fill="#fff"/></g>'}
function logo(c,a,ink,sub){
  sub=sub||ink;
  if(c===0)return '<svg viewBox="0 0 700 160" role="img" aria-label="AL ARBAB Travel and Tours">'+blade(a,0,4,1)+
    '<text x="150" y="92" '+F+' font-size="82" font-weight="900" letter-spacing="-1"><tspan fill="'+a+'">AL</tspan><tspan fill="'+ink+'" dx="14">ARBAB</tspan></text>'+
    '<text x="154" y="132" '+F+' font-size="21" font-weight="800" letter-spacing="9.5" fill="'+sub+'">TRAVEL &amp; TOURS</text></svg>';
  if(c===1)return '<svg viewBox="0 0 700 160" role="img" aria-label="AL ARBAB Travel and Tours">'+
    '<rect x="4" y="12" width="136" height="136" rx="30" fill="'+a+'"/><text x="72" y="104" text-anchor="middle" '+F+' font-size="68" font-weight="900" fill="#fff" letter-spacing="-2">AL</text>'+
    '<path d="M26,128 C54,116 86,116 118,128" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" opacity=".85"/><path d="M110,118 L124,128 L106,130 Z" fill="#fff"/>'+
    '<text x="166" y="92" '+F+' font-size="82" font-weight="900" letter-spacing="-1" fill="'+ink+'">ARBAB</text>'+
    '<text x="170" y="132" '+F+' font-size="21" font-weight="800" letter-spacing="9.5" fill="'+sub+'">TRAVEL &amp; TOURS</text></svg>';
  return '<svg viewBox="0 0 400 300" role="img" aria-label="AL ARBAB Travel and Tours">'+
    '<path d="M70,112 C130,18 270,10 336,86" fill="none" stroke="'+a+'" stroke-width="9" stroke-linecap="round"/><path d="M322,60 L352,96 L308,98 Z" fill="'+a+'"/>'+
    '<text x="200" y="168" text-anchor="middle" '+F+' font-size="132" font-weight="900" letter-spacing="-3" fill="'+a+'">AL</text>'+
    '<text x="200" y="232" text-anchor="middle" '+F+' font-size="68" font-weight="900" letter-spacing="2" fill="'+ink+'">ARBAB</text>'+
    '<text x="204" y="272" text-anchor="middle" '+F+' font-size="20" font-weight="800" letter-spacing="10" fill="'+sub+'">TRAVEL &amp; TOURS</text></svg>';
}
function mark(c,a,ink){
  if(c===1)return '<svg viewBox="0 0 150 150"><rect x="4" y="4" width="142" height="142" rx="32" fill="'+a+'"/><text x="75" y="102" text-anchor="middle" '+F+' font-size="72" font-weight="900" fill="#fff" letter-spacing="-2">AL</text></svg>';
  if(c===2)return '<svg viewBox="0 0 150 150"><text x="75" y="112" text-anchor="middle" '+F+' font-size="108" font-weight="900" fill="'+a+'" letter-spacing="-3">AL</text><path d="M20,52 C50,14 100,10 128,40" fill="none" stroke="'+ink+'" stroke-width="8" stroke-linecap="round"/><path d="M118,22 L134,46 L108,46 Z" fill="'+ink+'"/></svg>';
  return '<svg viewBox="0 0 150 150">'+blade(a,10,0,1)+'</svg>';
}
function $(s,r){return (r||document).querySelector(s)}
function render(){
  var p=PAL[st.p],a=p[2],ink=p[3],dark=st.wall==='dark',wInk=dark?'#f6f1e8':ink;
  $('#lpWall').className='wall '+st.wall;$('#lpWall').style.setProperty('--halo',dark?'rgba(255,200,130,.55)':'rgba(255,184,96,.75)');
  $('#lpWallLogo').innerHTML=logo(st.c,a,wInk,wInk);
  $('#lpWhite').innerHTML=logo(st.c,a,ink);
  $('#lpDark').innerHTML=logo(st.c,a,'#f6f1e8');
  $('#lpHead').innerHTML='<span class="mk">'+mark(st.c,a,ink)+'</span><span class="nm"><b>AL ARBAB</b><small>TRAVEL &amp; TOURS</small></span>';
  $('#lpFav').innerHTML=[16,32,64].map(function(n){return '<span style="width:'+n+'px;height:'+n+'px">'+mark(st.c,a,ink)+'</span>'}).join('');
  $('#lpGrid').innerHTML=PAL.map(function(q,i){return '<button type="button" class="pc" data-p="'+i+'" aria-pressed="'+(i===st.p)+'"><span>'+logo(st.c,q[2],q[3])+'</span><b>'+q[1]+'</b><i><u style="background:'+q[2]+'"></u><u style="background:'+q[3]+'"></u></i></button>'}).join('');
  document.querySelectorAll('#lpGrid .pc').forEach(function(b){b.onclick=function(){st.p=+b.dataset.p;render()}});
  document.querySelectorAll('.lp-con button').forEach(function(b,i){b.setAttribute('aria-pressed',i===st.c)});
  document.querySelectorAll('.lp-wall button').forEach(function(b){b.setAttribute('aria-pressed',b.dataset.w===st.wall)});
  $('#lpName').textContent=CON[st.c]+' · '+p[1];
}
document.querySelectorAll('.lp-con button').forEach(function(b,i){b.onclick=function(){st.c=i;render()}});
document.querySelectorAll('.lp-wall button').forEach(function(b){b.onclick=function(){st.wall=b.dataset.w;render()}});
var q=location.search,mc=q.match(/[?&]c=(\d)/),mp=q.match(/[?&]p=(\d)/);if(mc)st.c=Math.min(2,+mc[1]);if(mp)st.p=Math.min(PAL.length-1,+mp[1]);
render();
})();
