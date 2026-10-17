(function(){
var PAL=[['Red','#ff5144','#c4000c','#1a1a1c'],['Brand green','#2fd37a','#0a6b34','#0b1a14'],['Teal','#27e0ee','#0079a8','#0b1c26'],['Gold','#ffd84a','#d98200','#15130f'],['Violet','#9a7bff','#4a2fd0','#140f2e']];
var PLANE='M22,0 C22,-2 20,-3 17,-3 L4,-3 L-4,-17 L-9,-17 L-5,-3 L-14,-3 L-17,-8 L-20,-8 L-17,0 L-20,8 L-17,8 L-14,3 L-5,3 L-9,17 L-4,17 L4,3 L17,3 C20,3 22,2 22,0 Z';
var NAMES=['Bold AL + plane','Swoosh foot','Speed italic','Orbit ring','App tile'];
var P=0,BG='white',uid=0;
function defs(id,p){return '<defs><linearGradient id="'+id+'g" gradientUnits="userSpaceOnUse" x1="0" y1="10" x2="0" y2="190"><stop offset="0" stop-color="'+p[1]+'"/><stop offset="1" stop-color="'+p[2]+'"/></linearGradient>'+
  '<linearGradient id="'+id+'h" gradientUnits="userSpaceOnUse" x1="10" y1="10" x2="205" y2="190"><stop offset="0" stop-color="'+p[1]+'"/><stop offset="1" stop-color="'+p[2]+'"/></linearGradient>'+
  '<linearGradient id="'+id+'s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'+
  '<clipPath id="'+id+'c"><rect x="-10" y="-10" width="240" height="188"/></clipPath></defs>'}
function plane(col,x,y,r,s){return '<g transform="translate('+x+','+y+') rotate('+r+') scale('+s+')"><path d="'+PLANE+'" fill="'+col+'"/></g>'}
function dots(col,x,y,dx,dy){var o='';[.9,.62,.38].forEach(function(op,i){o+='<circle cx="'+(x+dx*(i+1))+'" cy="'+(y+dy*(i+1))+'" r="'+(3.6-i*.8)+'" fill="'+col+'" opacity="'+op+'"/>'});return o}
function AL(cA,cL,foot,flat){
  /* a full A (two legs + bar) and an L, all strokes, cut flat at the baseline by the clip path */
  var f=foot?'':'<path d="M132,165 H208" stroke="'+cL+'" stroke-width="26" fill="none"/>';
  return '<path d="M8,204 L62,28 L116,204" stroke="'+cA+'" stroke-width="29" stroke-linejoin="miter" stroke-miterlimit="8" fill="none"/><path d="M34,142 H90" stroke="'+cA+'" stroke-width="20" fill="none"/>'+
    '<path d="M148,20 V204" stroke="'+cL+'" stroke-width="29" fill="none"/>'+f;
}
function mark(o,p,dark){
  var id='m'+(++uid),ink=dark?'#f6f1e8':p[3],g='url(#'+id+'g)',s='',c='clip-path="url(#'+id+'c)"';
  if(o===0){ /* A in colour, L in ink, plane above the L */
    s=defs(id,p)+'<g '+c+'>'+AL(g,ink)+'</g><g '+c+'><path d="M8,204 L62,28" stroke="url(#'+id+'s)" stroke-width="9" fill="none" opacity=".5"/></g>'+plane(p[1],190,30,-38,1.05)+dots(p[1],190,30,-17,10);
  } else if(o===1){ /* the L foot becomes a swoosh that rises to the plane */
    s=defs(id,p)+'<g '+c+'>'+AL(g,ink,true)+'</g><path d="M148,152 C174,154 196,138 210,100 C208,150 182,180 148,180 Z" fill="url(#'+id+'h)"/>'+plane(ink,196,52,-60,.92)+dots(p[1],196,52,-10,13);
  } else if(o===2){ /* speed italic with horizontal cuts */
    s=defs(id,p)+'<mask id="'+id+'k"><rect width="260" height="200" fill="#fff"/><rect x="-20" y="72" width="280" height="6" fill="#000"/><rect x="-20" y="112" width="280" height="6" fill="#000"/><rect x="-20" y="152" width="280" height="6" fill="#000"/></mask>'+
      '<g mask="url(#'+id+'k)"><g transform="translate(34,0) skewX(-12) scale(.82 1)" '+c+'>'+AL('url(#'+id+'h)','url(#'+id+'h)')+'</g></g>'+plane(ink,190,26,-30,1)+dots(p[1],190,26,-18,8);
  } else if(o===3){ /* letters inside an open ring, the plane sits on the ring */
    s=defs(id,p)+'<circle cx="104" cy="104" r="84" fill="none" stroke="'+ink+'" stroke-width="8" stroke-dasharray="455 74" stroke-dashoffset="-70" stroke-linecap="round" transform="rotate(-30 104 104)"/>'+
      '<g transform="translate(46,54) scale(.5)"><g '+c+'>'+AL(g,g)+'</g></g>'+plane(p[1],178,42,-52,1.1)+dots(p[1],178,42,-15,10);
  } else { /* app tile, white letters */
    s=defs(id,p)+'<rect x="4" y="4" width="196" height="196" rx="46" fill="url(#'+id+'h)"/><ellipse cx="100" cy="30" rx="86" ry="46" fill="url(#'+id+'s)" opacity=".45"/>'+
      '<g transform="translate(34,48) scale(.62)"><g '+c+'>'+AL('#fff','#fff')+'</g></g>'+plane('#fff',158,50,-38,.85)+dots('#fff',158,50,-14,9);
  }
  return '<svg viewBox="0 0 215 200" role="img" aria-label="AL ARBAB mark">'+s+'</svg>';
}
function pill(o,p){return '<div class="pill"><span class="pm">'+mark(o,p,false)+'</span><span class="pn"><b>AL <i style="color:'+p[2]+'">ARBAB</i></b><small>TRAVEL &amp; TOURS</small></span></div>'}
function $(s){return document.querySelector(s)}
function render(){
  var p=PAL[P];
  $('#alGrid').innerHTML=NAMES.map(function(n,o){return '<article class="alc"><h3>'+(o+1)+' · '+n+'</h3><div class="big '+BG+'">'+mark(o,p,BG==='dark')+'</div><div class="pw">'+pill(o,p)+'</div><div class="sm"><span style="width:64px">'+mark(o,p,false)+'</span><span style="width:32px">'+mark(o,p,false)+'</span><span style="width:20px">'+mark(o,p,false)+'</span></div></article>'}).join('');
  document.querySelectorAll('.al-pal button').forEach(function(b,i){b.setAttribute('aria-pressed',i===P)});
  document.querySelectorAll('.al-bg button').forEach(function(b){b.setAttribute('aria-pressed',b.dataset.b===BG)});
}
$('.al-pal').innerHTML='<b>Colour:</b>'+PAL.map(function(p,i){return '<button type="button"><i style="background:linear-gradient(135deg,'+p[1]+','+p[2]+')"></i>'+p[0]+'</button>'}).join('');
document.querySelectorAll('.al-pal button').forEach(function(b,i){b.onclick=function(){P=i;render()}});
document.querySelectorAll('.al-bg button').forEach(function(b){b.onclick=function(){BG=b.dataset.b;render()}});
var q=location.search.match(/[?&]p=(\d)/);if(q)P=Math.min(PAL.length-1,+q[1]);
render();
})();
