(function(){
var PAL=[['Red','#e61e2b','#ff6a5f'],['Brand green','#0e7f3e','#5fd48a'],['Teal','#00a3b4','#4fe3f0'],['Gold','#e39a00','#ffd23a'],['Royal blue','#1767b3','#5cb0ff']];
var PLANE='M22,0 C22,-2 20,-3 17,-3 L4,-3 L-4,-17 L-9,-17 L-5,-3 L-14,-3 L-17,-8 L-20,-8 L-17,0 L-20,8 L-17,8 L-14,3 L-5,3 L-9,17 L-4,17 L4,3 L17,3 C20,3 22,2 22,0 Z';
var P=0,BG='milky',uid=0;
function rot(x,y,a,cx,cy){var r=a*Math.PI/180,dx=x-cx,dy=y-cy;return [cx+dx*Math.cos(r)-dy*Math.sin(r),cy+dx*Math.sin(r)+dy*Math.cos(r)]}
/* an orbit ellipse (with a gap), and a plane sitting on it pointing along the path */
function orbit(cx,cy,rx,ry,tilt,col,w,planeT,gap){
  var t0=planeT*Math.PI/180,pp=rot(cx+rx*Math.cos(t0),cy+ry*Math.sin(t0),tilt,cx,cy);
  var dx=-rx*Math.sin(t0),dy=ry*Math.cos(t0),ang=Math.atan2(dy,dx)*180/Math.PI+tilt;
  var L=Math.PI*(3*(rx+ry)-Math.sqrt((3*rx+ry)*(rx+3*ry)));
  return '<ellipse cx="'+cx+'" cy="'+cy+'" rx="'+rx+'" ry="'+ry+'" fill="none" stroke="'+col+'" stroke-width="'+w+'" stroke-linecap="round" stroke-dasharray="'+(L-gap)+' '+gap+'" stroke-dashoffset="'+(-((planeT/360)*L+gap*.5+18))+'" transform="rotate('+tilt+' '+cx+' '+cy+')"/>'+
    '<g transform="translate('+pp[0].toFixed(1)+','+pp[1].toFixed(1)+') rotate('+ang.toFixed(1)+') scale(2.1)"><path d="'+PLANE+'" fill="'+col+'"/></g>';
}
function letters(c1,c2,sk){
  return '<g clip-path="url(#pkc)"'+(sk?' transform="translate(34,0) skewX(-12)"':'')+'><path d="M40,190 L84,40 L128,190" stroke="'+c1+'" stroke-width="26" stroke-linejoin="miter" stroke-miterlimit="8" fill="none"/><path d="M58,140 H110" stroke="'+c1+'" stroke-width="18" fill="none"/>'+
    '<path d="M150,32 V190" stroke="'+c2+'" stroke-width="26" fill="none"/><path d="M137,163 H212" stroke="'+c2+'" stroke-width="26" fill="none"/></g>';
}
var CLIP='<defs><clipPath id="pkc"><rect x="-20" y="-20" width="300" height="196"/></clipPath></defs>';
function mark(o,p,dark){
  var ink=dark?'#fff':'#17181a',red=p[1],s='';
  if(o===0)s='<use href="#alpk" width="215" height="200" style="--lt:'+ink+';--rd:'+red+'"/>';
  else if(o===1)s=CLIP+letters(ink,ink)+orbit(112,150,100,30,-14,red,7,40,40);
  else if(o===2)s=CLIP+'<circle cx="107" cy="100" r="96" fill="'+(dark?'#101a20':'#15191c')+'"/><g transform="translate(26,14) scale(.76)">'+letters('#fff','#fff')+'</g>'+orbit(107,116,92,26,-16,red,6,35,36);
  else if(o===3)s=CLIP+letters(ink,red,true)+orbit(108,150,98,24,-8,red,6,28,34);
  else s=CLIP+'<rect x="4" y="4" width="207" height="192" rx="44" fill="'+red+'"/><g transform="translate(26,14) scale(.76)">'+letters('#fff','#fff')+'</g>'+orbit(107,142,90,26,-12,'#fff',6,38,34);
  return '<svg viewBox="0 0 215 200" role="img" aria-label="AL ARBAB mark">'+s+'</svg>';
}
function exact(dark){return '<svg viewBox="4400 4000 6200 5000" role="img" aria-label="AL ARBAB mark"><use href="#alpk" width="6200" height="5000" x="4400" y="4000" style="--lt:'+(dark?'#fff':'#17181a')+'"/></svg>'}
var NAMES=['Your mark from alarbabtravel.pk, as is','Bold AL, orbit and plane','Dark disc emblem','Italic AL with red L','Red app tile'];
function pill(o,p,dark){var m=o===0?exact(dark):mark(o,p,dark);return '<div class="pill"><span class="pm">'+m+'</span><span class="pn"><b>AL <i style="color:'+p[1]+'">ARBAB</i></b><small>TRAVEL &amp; TOURS</small></span></div>'}
function $(s){return document.querySelector(s)}
function render(){
  var p=PAL[P],dark=BG==='dark';
  $('#pkGrid').innerHTML=NAMES.map(function(n,o){
    var big=o===0?exact(dark||o===2):mark(o,p,dark);
    return '<article class="alc"><h3>'+(o+1)+' · '+n+'</h3><div class="big '+BG+'">'+big+'</div><div class="pw">'+pill(o,p,false)+'</div><div class="sm"><span style="width:64px">'+(o===0?exact(false):mark(o,p,false))+'</span><span style="width:32px">'+(o===0?exact(false):mark(o,p,false))+'</span><span style="width:20px">'+(o===0?exact(false):mark(o,p,false))+'</span></div></article>'}).join('');
  document.querySelectorAll('.al-pal button').forEach(function(b,i){b.setAttribute('aria-pressed',i===P)});
  document.querySelectorAll('.al-bg button').forEach(function(b){b.setAttribute('aria-pressed',b.dataset.b===BG)});
}
$('.al-pal').innerHTML='<b>Accent colour:</b>'+PAL.map(function(p,i){return '<button type="button"><i style="background:'+p[1]+'"></i>'+p[0]+'</button>'}).join('');
document.querySelectorAll('.al-pal button').forEach(function(b,i){b.onclick=function(){P=i;render()}});
document.querySelectorAll('.al-bg button').forEach(function(b){b.onclick=function(){BG=b.dataset.b;render()}});
var q=location.search.match(/[?&]p=(\d)/);if(q)P=Math.min(PAL.length-1,+q[1]);
render();
})();
