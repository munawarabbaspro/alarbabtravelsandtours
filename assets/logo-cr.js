(function(){
/* 15 original AL + aeroplane marks, drawn on a 260 x 240 grid. Letters are built from strokes and cut flat at the baseline (y = 200). */
var PAL=[
 {n:'Red + Ink',   a1:'#ff4b4b',a2:'#c10012',ink:'#15171b',pl:'#15171b',acc:'#e1121f'},
 {n:'Red + Gold',  a1:'#ff4b4b',a2:'#c10012',ink:'#15171b',pl:'#f6b81f',acc:'#e1121f'},
 {n:'Red + Navy',  a1:'#ff4b4b',a2:'#c10012',ink:'#102a56',pl:'#102a56',acc:'#e1121f'},
 {n:'All Red',     a1:'#ff4b4b',a2:'#c10012',ink:'#d3000f',pl:'#d3000f',acc:'#e1121f'},
 {n:'Mono Black',  a1:'#2a2d33',a2:'#0b0c0e',ink:'#0b0c0e',pl:'#0b0c0e',acc:'#0b0c0e'},
 {n:'Brand Green', a1:'#2fd37a',a2:'#0a6b34',ink:'#0b1a14',pl:'#f2b84b',acc:'#0e7f3e'}];
var PLANE='M22,0 C22,-2 20,-3 17,-3 L4,-3 L-4,-17 L-9,-17 L-5,-3 L-14,-3 L-17,-8 L-20,-8 L-17,0 L-20,8 L-17,8 L-14,3 L-5,3 L-9,17 L-4,17 L4,3 L17,3 C20,3 22,2 22,0 Z';
var NAMES=['Plane crossbar','Aircraft window','Sunrise horizon','Paper-plane foot','Boarding ticket','Globe orbit','Speed italic','Swoosh trail','Gloss app tile','Hex badge','Wing foot','Runway A','Flight slice','Shield','Red disc + orbit'];
var P=0,BG='milky',n=0;
function plane(c,x,y,r,s){return '<g transform="translate('+x+','+y+') rotate('+r+') scale('+s+')"><path d="'+PLANE+'" fill="'+c+'"/></g>'}
function dots(c,x,y,dx,dy,k){var o='',op=[.95,.7,.45,.25];for(var i=0;i<(k||3);i++)o+='<circle cx="'+(x+dx*(i+1))+'" cy="'+(y+dy*(i+1))+'" r="'+(4-i*.9).toFixed(1)+'" fill="'+c+'" opacity="'+op[i]+'"/>';return o}
function St(d,c,w,extra){return '<path d="'+d+'" stroke="'+c+'" stroke-width="'+w+'" stroke-linejoin="miter" stroke-miterlimit="10" stroke-linecap="butt" fill="none" '+(extra||'')+'/>'}
function Aletter(c,x,w,bar,sw){x=x||40;sw=sw||26;return St('M'+x+',218 L'+(x+56)+',46 L'+(x+112)+',218',c,sw)+(bar===false?'':St('M'+(x+22)+',156 H'+(x+90),c,sw*.72))}
function Lletter(c,x,sw,foot,flat){sw=sw||26;return St('M'+x+',32 V218',c,sw)+(foot===false?'':St('M'+(x-sw/2)+',187 H'+(x+(foot||58)),c,sw))}
function mark(o,pal,dark){
  var id='c'+(++n),I=dark?'#f6f1e8':pal.ink,G='url(#'+id+'g)',H='url(#'+id+'h)',PL=dark&&pal.pl===pal.ink?'#f6f1e8':pal.pl,s='';
  var defs='<defs><linearGradient id="'+id+'g" gradientUnits="userSpaceOnUse" x1="0" y1="30" x2="0" y2="205"><stop offset="0" stop-color="'+pal.a1+'"/><stop offset="1" stop-color="'+pal.a2+'"/></linearGradient>'+
    '<linearGradient id="'+id+'h" gradientUnits="userSpaceOnUse" x1="20" y1="20" x2="240" y2="210"><stop offset="0" stop-color="'+pal.a1+'"/><stop offset="1" stop-color="'+pal.a2+'"/></linearGradient>'+
    '<linearGradient id="'+id+'s" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="130"><stop offset="0" stop-color="#fff" stop-opacity=".6"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'+
    '<clipPath id="'+id+'c"><rect x="-20" y="-20" width="320" height="220"/></clipPath>'+
    '<mask id="'+id+'m"><rect width="260" height="240" fill="#fff"/><path d="M-10,225 L275,10" stroke="#000" stroke-width="7"/></mask>'+
    '<mask id="'+id+'t"><rect width="260" height="240" fill="#fff"/><circle cx="30" cy="120" r="15"/><circle cx="230" cy="120" r="15"/></mask></defs>';
  var C='clip-path="url(#'+id+'c)"';
  if(o===0)s='<g '+C+'>'+Aletter(G,36,0,false)+Lletter(I,190,26,52)+'</g>'+plane(PL,92,146,0,2.05)+dots(PL,238,56,-18,10)+plane(PL,238,48,-36,1.2);
  else if(o===1)s='<rect x="66" y="14" width="128" height="196" rx="64" fill="'+(dark?'#101a20':'#fff')+'" stroke="'+I+'" stroke-width="11"/><rect x="76" y="24" width="108" height="176" rx="54" fill="'+H+'"/>'+
    '<g transform="translate(86,100) scale(.42)"><g '+C+'>'+Aletter('#fff',0,0,true,30)+Lletter('#fff',152,30,56)+'</g></g>'+plane(PL,226,44,-36,1.35)+dots(PL,226,44,-18,12);
  else if(o===2)s='<path d="M24,172 A106,106 0 0 1 236,172 Z" fill="'+H+'"/><g transform="translate(66,52) scale(.6)"><g '+C+'>'+Aletter('#fff',20,0,true,28)+Lletter('#fff',172,28,60)+'</g></g>'+
    '<rect x="14" y="170" width="232" height="9" rx="4.5" fill="'+I+'"/><path d="M60,196 H200" stroke="'+I+'" stroke-width="5" stroke-linecap="round" stroke-dasharray="1 14" opacity=".6"/>'+plane(PL,208,52,-30,1.4)+dots(PL,208,52,-20,10);
  else if(o===3)s='<g '+C+'>'+Aletter(G,30)+Lletter(I,178,26,0,0)+'</g><path d="M163,190 L246,150 L216,196 Z" fill="'+PL+'"/><path d="M216,196 L246,150 L232,214 Z" fill="'+G+'" opacity=".9"/>'+dots(G,246,150,-14,-10,2);
  else if(o===4)s='<g mask="url(#'+id+'t)"><rect x="12" y="50" width="236" height="140" rx="22" fill="'+H+'"/></g><path d="M196,62 V178" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-dasharray="2 9" opacity=".85"/>'+
    '<g transform="translate(34,70) scale(.6)"><g '+C+'>'+Aletter('#fff',10,0,true,30)+Lletter('#fff',160,30,60)+'</g></g>'+plane('#fff',220,120,-90,1.25);
  else if(o===5)s='<circle cx="126" cy="122" r="88" fill="none" stroke="'+I+'" stroke-width="5"/><ellipse cx="126" cy="122" rx="38" ry="88" fill="none" stroke="'+I+'" stroke-width="3" opacity=".2"/><path d="M38,122 H214 M60,70 H192 M60,174 H192" stroke="'+I+'" stroke-width="3" opacity=".14"/>'+
    '<g transform="translate(20,18) scale(.86)"><g '+C+'>'+Aletter(G,64,0,true,24)+Lletter(G,180,24,36)+'</g></g><ellipse cx="126" cy="122" rx="116" ry="34" fill="none" stroke="'+pal.acc+'" stroke-width="5" stroke-dasharray="300 70" transform="rotate(-24 126 122)"/>'+plane(PL,222,60,-52,1.5);
  else if(o===6)s='<mask id="'+id+'k"><rect width="280" height="240" fill="#fff"/><rect x="-20" y="78" width="320" height="6" fill="#000"/><rect x="-20" y="122" width="320" height="6" fill="#000"/><rect x="-20" y="166" width="320" height="6" fill="#000"/></mask>'+
    '<g mask="url(#'+id+'k)"><g transform="translate(26,0) skewX(-13) scale(.9 1)" '+C+'>'+Aletter(H,30,0,true,30)+Lletter(H,176,30,60)+'</g></g>'+plane(PL,222,34,-24,1.4)+St('M150,24 H190 M166,38 H200 M176,52 H204',G,4,'stroke-linecap="round" opacity=".7"');
  else if(o===7)s='<g '+C+'>'+Aletter(I,40)+Lletter(I,190,26,52)+'</g><path d="M14,214 C84,230 196,214 240,92 C206,172 112,198 14,214 Z" fill="'+H+'"/>'+plane(PL,242,84,-64,1.45)+dots(pal.acc,242,84,-4,16);
  else if(o===8)s='<rect x="8" y="8" width="244" height="224" rx="56" fill="'+H+'"/><ellipse cx="130" cy="44" rx="104" ry="52" fill="url(#'+id+'s)" opacity=".5"/><g transform="translate(34,38) scale(.78)"><g '+C+'>'+Aletter('#fff',18,0,true,28)+Lletter('#fff',170,28,56)+'</g></g>'+plane('#fff',204,56,-36,1.3)+dots('#fff',204,56,-18,12);
  else if(o===9)s='<path d="M130,10 L236,66 V174 L130,230 L24,174 V66 Z" fill="'+(dark?'#101a20':'#15171b')+'"/><path d="M130,22 L226,72 V168 L130,218 L34,168 V72 Z" fill="none" stroke="'+pal.acc+'" stroke-width="3"/>'+
    '<g transform="translate(60,52) scale(.62)"><g '+C+'>'+Aletter(H,10,0,true,28)+Lletter('#fff',162,28,52)+'</g></g><path d="M52,188 Q130,226 208,188" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-dasharray="1 10" opacity=".7"/>'+plane(PL,196,64,-40,1.2);
  else if(o===10)s='<g '+C+'>'+Aletter(G,30)+Lletter(I,176,26,0)+'</g><path d="M162,200 L252,156 L252,138 L258,134 L258,164 L228,200 Z" fill="'+H+'"/>'+plane(PL,222,56,-34,1.3)+dots(PL,222,56,-18,10);
  else if(o===11)s='<g '+C+'>'+Aletter(I,40,0,false)+Lletter(I,190,26,52)+'</g><rect x="82" y="168" width="28" height="10" rx="3" fill="'+pal.acc+'"/><rect x="87" y="144" width="18" height="9" rx="3" fill="'+pal.acc+'" opacity=".85"/><rect x="91" y="124" width="10" height="8" rx="2.5" fill="'+pal.acc+'" opacity=".65"/>'+
    plane(PL,134,30,-52,1.7)+dots(PL,134,30,-17,14);
  else if(o===12)s='<g mask="url(#'+id+'m)"><g '+C+'>'+Aletter(G,34)+Lletter(G,186,26,54)+'</g></g>'+plane(PL,236,36,-38,1.45)+dots(PL,236,36,-18,10);
  else if(o===13)s='<path d="M130,10 C170,26 206,28 230,26 C234,120 214,184 130,230 C46,184 26,120 30,26 C54,28 90,26 130,10 Z" fill="'+(dark?'#101a20':'#15171b')+'"/><path d="M130,26 C164,40 196,42 214,42 C216,122 198,172 130,212 C62,172 44,122 46,42 C64,42 96,40 130,26 Z" fill="'+H+'"/>'+
    '<g transform="translate(62,60) scale(.58)"><g '+C+'>'+Aletter('#fff',14,0,true,30)+Lletter('#fff',164,30,56)+'</g></g>'+plane('#fff',186,76,-36,1.15);
  else s='<circle cx="130" cy="120" r="100" fill="'+H+'"/><g transform="translate(60,60) scale(.62)"><g '+C+'>'+Aletter('#fff',16,0,true,28)+Lletter('#fff',166,28,52)+'</g></g><ellipse cx="130" cy="120" rx="124" ry="34" fill="none" stroke="'+I+'" stroke-width="6" stroke-dasharray="330 70" stroke-dashoffset="-60" transform="rotate(-22 130 120)"/>'+plane(PL,230,70,-52,1.45);
  return '<svg viewBox="0 0 260 240" role="img" aria-label="AL ARBAB mark">'+defs+s+'</svg>';
}
function pill(o,pal,dark){return '<div class="pill"><span class="pm">'+mark(o,pal,false)+'</span><span class="pn"><b>AL <i style="color:'+pal.acc+'">ARBAB</i></b><small>TRAVEL &amp; TOURS</small></span></div>'}
function $(s){return document.querySelector(s)}
function render(){
  var pal=PAL[P],dark=BG==='dark';
  $('#crGrid').innerHTML=NAMES.map(function(nm,o){return '<article class="alc"><h3>'+(o+1)+' · '+nm+'</h3><div class="big '+BG+'">'+mark(o,pal,dark||BG==='red'&&false)+'</div><div class="pw">'+pill(o,pal)+'</div><div class="sm"><span style="width:64px">'+mark(o,pal,false)+'</span><span style="width:32px">'+mark(o,pal,false)+'</span><span style="width:20px">'+mark(o,pal,false)+'</span></div></article>'}).join('');
  document.querySelectorAll('.al-pal button').forEach(function(b,i){b.setAttribute('aria-pressed',i===P)});
  document.querySelectorAll('.al-bg button').forEach(function(b){b.setAttribute('aria-pressed',b.dataset.b===BG)});
}
$('.al-pal').innerHTML='<b>Colour set:</b>'+PAL.map(function(p){return '<button type="button"><i style="background:linear-gradient(135deg,'+p.a1+','+p.a2+')"></i>'+p.n+'</button>'}).join('');
document.querySelectorAll('.al-pal button').forEach(function(b,i){b.onclick=function(){P=i;render()}});
document.querySelectorAll('.al-bg button').forEach(function(b){b.onclick=function(){BG=b.dataset.b;render()}});
var q=location.search.match(/[?&]p=(\d)/);if(q)P=Math.min(PAL.length-1,+q[1]);
render();
})();
