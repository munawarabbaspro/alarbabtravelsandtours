(function(){
var M='/assets/brand/orbit-mark.png',W=343,H=284,F='font-family:Archivo,Arial Black,sans-serif';
var INK='#0b0a09',GOLD='#f2a900';
function img(h){return '<img src="'+M+'" alt="AL ARBAB mark" height="'+h+'" width="'+Math.round(h*W/H)+'" style="height:'+h+'px;width:auto;display:block">'}
function name(sz,col,sub,gold){return '<span style="display:grid;line-height:1;'+F+'"><b style="font-weight:900;font-size:'+sz+'px;letter-spacing:-.01em;color:'+col+'">'+(gold?'<span style="color:'+GOLD+'">AL</span> ':'AL ')+'ARBAB</b><small style="font:800 '+Math.round(sz*.3)+'px/1 Archivo,sans-serif;letter-spacing:.42em;margin-top:'+Math.round(sz*.18)+'px;color:'+sub+'">TRAVEL &amp; TOURS</small></span>'}
var CARDS=[
 ['1 · As supplied, on white','<div class="bx w">'+img(150)+'</div>'],
 ['2 · On the milky site background','<div class="bx milky">'+img(150)+'</div>'],
 ['3 · Horizontal lockup','<div class="bx w row">'+img(84)+name(46,INK,'#5b6a66',true)+'</div>'],
 ['4 · Stacked lockup','<div class="bx w col">'+img(110)+name(44,INK,'#5b6a66',true)+'</div>'],
 ['5 · Lockup on milky glass','<div class="bx milky row">'+img(84)+name(46,INK,'#506661',true)+'</div>'],
 ['6 · In the website header','<div class="bx milky"><div class="hd">'+img(40)+'<span style="display:grid;line-height:1.05;'+F+'"><b style="font-weight:900;font-size:18px">AL ARBAB</b><small style="font:700 10px Inter,sans-serif;letter-spacing:.22em;color:#506661">TRAVEL &amp; TOURS</small></span></div></div>'],
 ['7 · App icon and favicon','<div class="bx milky tiles"><span class="t" style="width:112px;height:112px;border-radius:26px">'+img(72)+'</span><span class="t" style="width:64px;height:64px;border-radius:15px">'+img(40)+'</span><span class="t" style="width:32px;height:32px;border-radius:8px">'+img(20)+'</span><span class="t" style="width:16px;height:16px;border-radius:4px">'+img(10)+'</span></div>'],
 ['8 · Welcome screen (navy)','<div class="bx navy col"><span class="badge">'+img(88)+'</span>'+name(40,'#fff','#8fb3c2',false)+'</div>'],
 ['9 · Signage wall (mock-up)','<div class="bx wall row">'+img(84)+name(46,'#1b1a18','#3a3733',false)+'</div>']
];
var GR=[['Gold','linear-gradient(135deg,#ffd23a,#f0a000)','#17181a'],['Sunset','linear-gradient(135deg,#ff9f43,#ff3d71 60%,#8e2de2)','#fff'],['Brand green','linear-gradient(135deg,#17a354,#073d22)','#fff'],
  ['Teal','linear-gradient(135deg,#00c8ff,#0b4a5c)','#fff'],['Navy','linear-gradient(135deg,#25407f,#0a1226)','#fff'],['Violet to sky','linear-gradient(135deg,#7b5cff,#00c8ff)','#fff'],
  ['Charcoal','linear-gradient(135deg,#3a3a3e,#0d0d0f)','#fff'],['Aurora','radial-gradient(60% 55% at 15% 10%,#7fe3a2,transparent 62%),radial-gradient(55% 50% at 90% 15%,#80d0ff,transparent 62%),radial-gradient(60% 55% at 70% 100%,#ff9f7a,transparent 62%),#a9cfc2','#0b1220']];
document.getElementById('l2Cards').innerHTML=CARDS.map(function(c){return '<article class="l2c"><div class="stg">'+c[1]+'</div><h3>'+c[0]+'</h3></article>'}).join('');
document.getElementById('l2Grad').innerHTML=GR.map(function(g,i){return '<article class="l2c"><div class="stg gr" style="background:'+g[1]+';color:'+g[2]+'"><span class="badge">'+img(70)+'</span>'+name(34,g[2],g[2],false)+'</div><h3>G'+(i+1)+' · '+g[0]+'</h3></article>'}).join('');
})();
