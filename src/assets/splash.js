(function(){
var s=document.getElementById('splash'),d=document.documentElement,done=false,t,raf=0;
if(!s||!d.classList.contains('splash'))return;
function end(){if(done)return;done=true;clearTimeout(t);cancelAnimationFrame(raf);d.classList.remove('splash');try{sessionStorage.setItem('abSplash','1')}catch(e){}s.remove()}
function go(){if(s.classList.contains('out'))return;clearTimeout(t);s.classList.add('out');setTimeout(end,520)}
s.addEventListener('click',go);addEventListener('keydown',function(e){if(!done&&(e.key==='Escape'||e.key==='Enter'||e.key===' '))go()});
t=setTimeout(go,1350);
/* galaxy background: nebula + star flight. Canvas 2D only, runs only while the splash is on screen */
var cv=document.getElementById('spc');
if(cv&&cv.getContext){try{
var x=cv.getContext('2d'),D=Math.min(1.5,devicePixelRatio||1),W=cv.width=Math.round(innerWidth*D),H=cv.height=Math.round(innerHeight*D),
n=W<700?70:130,st=[],i,t0=0,neb=document.createElement('canvas'),nw=Math.max(48,W>>2),nh=Math.max(48,H>>2),q=neb.getContext('2d');
neb.width=nw;neb.height=nh;q.fillStyle='#04070f';q.fillRect(0,0,nw,nh);
function bl(a,b,r,c){var g=q.createRadialGradient(a*nw,b*nh,0,a*nw,b*nh,r*Math.max(nw,nh));g.addColorStop(0,c);g.addColorStop(1,'rgba(0,0,0,0)');q.fillStyle=g;q.fillRect(0,0,nw,nh)}
bl(.28,.42,.62,'rgba(28,84,214,.60)');bl(.74,.62,.55,'rgba(112,58,205,.40)');bl(.56,.24,.46,'rgba(30,170,225,.28)');bl(.5,.5,.34,'rgba(227,6,19,.14)');bl(.12,.86,.40,'rgba(20,48,130,.50)');
for(i=0;i<n;i++)st.push({x:Math.random()*2-1,y:Math.random()*2-1,z:Math.random()*.96+.04,p:0});
function ez(v){return v<0?0:v>1?1:v*v*(3-2*v)}
function fr(now){
 if(done)return;if(!t0)t0=now;var tt=(now-t0)/1000*1.75;
 var sp=tt<.25?.25+tt*2.2:tt<1.5?.8:Math.max(.04,.8*(1-ez((tt-1.5)/1.1))),dr=1.06-Math.min(1,tt/3)*.06;
 x.save();x.translate(W/2,H/2);x.scale(dr,dr);x.rotate(Math.sin(tt*.3)*.02);x.drawImage(neb,-W/2,-H/2,W,H);x.restore();
 var cx=W/2,cy=H/2,f=Math.max(W,H)*.19;x.lineCap='round';
 for(i=0;i<n;i++){var a=st[i];a.p=a.z;a.z-=sp*.012;
  if(a.z<=.03){a.x=Math.random()*2-1;a.y=Math.random()*2-1;a.z=1;a.p=1}
  var b=Math.min(1,(1-a.z)*1.4+.15);
  x.strokeStyle='rgba('+(190+(i%3)*20)+','+(215+(i%2)*20)+',255,'+b+')';x.lineWidth=(.6+(1-a.z)*1.7)*D;
  x.beginPath();x.moveTo(cx+a.x/a.p*f,cy+a.y/a.p*f);x.lineTo(cx+a.x/a.z*f,cy+a.y/a.z*f);x.stroke()}
 if(tt<3.4&&!document.hidden)raf=requestAnimationFrame(fr)}
raf=requestAnimationFrame(fr)}catch(e){}}
})();
