/* hero ideas that do a job (preview only): twin live clocks, destination wheel, ticket printer */
(function () {
  var D = [
    { n: "Thailand", city: "Phuket", code: "HKT", tz: "Asia/Bangkok", f: "th" },
    { n: "Malaysia", city: "Kuala Lumpur", code: "KUL", tz: "Asia/Kuala_Lumpur", f: "my" },
    { n: "Indonesia", city: "Bali", code: "DPS", tz: "Asia/Makassar", f: "id" },
    { n: "Singapore", city: "Singapore", code: "SIN", tz: "Asia/Singapore", f: "sg" },
    { n: "Nepal", city: "Kathmandu", code: "KTM", tz: "Asia/Kathmandu", f: "np" },
    { n: "Vietnam", city: "Ho Chi Minh City", code: "SGN", tz: "Asia/Ho_Chi_Minh", f: "vn" }
  ];
  var PL = "M22,0 C22,-2 20,-3 17,-3 L4,-3 L-4,-17 L-9,-17 L-5,-3 L-14,-3 L-17,-8 L-20,-8 L-17,0 L-20,8 L-17,8 L-14,3 L-5,3 L-9,17 L-4,17 L4,3 L17,3 C20,3 22,2 22,0 Z";
  var PLANE = '<svg viewBox="-24 -20 48 40" aria-hidden="true"><path d="' + PL + '"/></svg>';
  function off(tz, d) { return (Date.parse(d.toLocaleString("en-US", { timeZone: tz })) - Date.parse(d.toLocaleString("en-US", { timeZone: "UTC" }))) / 60000; }
  function hm(tz, d) { return new Intl.DateTimeFormat("en-GB", { hour: "2-digit", minute: "2-digit", hour12: false, timeZone: tz }).format(d); }
  function diff(tz, d) {
    var m = Math.round(off(tz, d) - off("Asia/Karachi", d)), s = m < 0 ? "-" : "+", a = Math.abs(m), h = Math.floor(a / 60), r = a % 60;
    return s + h + " h" + (r ? " " + r + " min" : "");
  }
  function tiles(str) { return str.split("").map(function (c) { return c === ":" ? '<i class="hx-c">:</i>' : '<b>' + c + '</b>'; }).join(""); }

  function chips(box, on, cb) {
    var h = '<div class="hx-chips">' + D.map(function (x, i) { return '<button type="button" class="' + (i === on ? "on" : "") + '"><img src="/assets/flags/w80/' + x.f + '.png" alt="" width="20" height="14">' + x.n + "</button>"; }).join("") + "</div>";
    box.insertAdjacentHTML("beforeend", h);
    box.querySelectorAll(".hx-chips button").forEach(function (b, i) {
      b.addEventListener("click", function () { box.querySelectorAll(".hx-chips button").forEach(function (x, k) { x.classList.toggle("on", k === i); }); cb(i); });
    });
  }

  /* 1 · twin clocks */
  document.querySelectorAll('.hx-s[data-m="clock"]').forEach(function (box) {
    box.insertAdjacentHTML("afterbegin",
      '<div class="hx-twin"><div class="hx-cl"><small>ISLAMABAD</small><span class="hx-fl" id="c1">' + tiles("00:00") + '</span><em>Local time</em></div>' +
      '<div class="hx-mid"><i class="hx-ln"></i><span class="hx-pl">' + PLANE + '</span><strong id="cd">+0 h</strong></div>' +
      '<div class="hx-cl"><small id="cn">PHUKET</small><span class="hx-fl" id="c2">' + tiles("00:00") + '</span><em>Local time</em></div></div>');
    var cur = 0;
    function tick() {
      var d = new Date(), x = D[cur];
      box.querySelector("#c1").innerHTML = tiles(hm("Asia/Karachi", d));
      box.querySelector("#c2").innerHTML = tiles(hm(x.tz, d));
      box.querySelector("#cn").textContent = x.city.toUpperCase();
      box.querySelector("#cd").textContent = diff(x.tz, d) + " ahead";
    }
    chips(box, 0, function (i) { cur = i; tick(); box.classList.remove("flip"); void box.offsetWidth; box.classList.add("flip"); });
    tick(); setInterval(tick, 10000);
  });

  /* 2 · destination wheel */
  document.querySelectorAll('.hx-s[data-m="wheel"]').forEach(function (box) {
    var n = D.length, cur = 0;
    var dots = D.map(function (x, i) { return '<button type="button" class="hx-dot" data-i="' + i + '"><img src="/assets/flags/w80/' + x.f + '.png" alt="' + x.n + '" width="56" height="56"></button>'; }).join("");
    box.insertAdjacentHTML("afterbegin",
      '<div class="hx-wh"><div class="hx-arc">' + dots + '</div><div class="hx-info"><small>FROM ISLAMABAD</small><b id="wn">Thailand</b><span id="wc">Phuket &middot; HKT</span><a href="#">Ask about this visa on WhatsApp &rarr;</a></div>' +
      '<button class="hx-ar l" type="button" aria-label="Previous">&lsaquo;</button><button class="hx-ar r" type="button" aria-label="Next">&rsaquo;</button></div>');
    var ds = box.querySelectorAll(".hx-dot");
    function lay() {
      ds.forEach(function (d, i) {
        var k = ((i - cur + n + n / 2) % n) - n / 2;                // -3..2
        var a = k * 30 * Math.PI / 180, R = 150;
        d.style.transform = "translate(" + Math.round(Math.sin(a) * R) + "px," + Math.round((1 - Math.cos(a)) * R * .7) + "px) scale(" + (k === 0 ? 1.45 : 1 - Math.min(.35, Math.abs(k) * .12)) + ")";
        d.style.opacity = Math.abs(k) > 2.1 ? 0 : (k === 0 ? 1 : .75);
        d.style.zIndex = k === 0 ? 5 : 1;
        d.classList.toggle("on", k === 0);
      });
      var x = D[cur];
      box.querySelector("#wn").textContent = x.n; box.querySelector("#wc").innerHTML = x.city + " &middot; " + x.code;
    }
    function go(i) { cur = (i + n) % n; lay(); }
    ds.forEach(function (d) { d.addEventListener("click", function () { go(+d.getAttribute("data-i")); }); });
    box.querySelector(".hx-ar.l").addEventListener("click", function () { go(cur - 1); });
    box.querySelector(".hx-ar.r").addEventListener("click", function () { go(cur + 1); });
    box.addEventListener("wheel", function (e) { e.preventDefault(); go(cur + (e.deltaY > 0 ? 1 : -1)); }, { passive: false });
    lay();
  });

  /* 3 · ticket printer */
  document.querySelectorAll('.hx-s[data-m="ticket"]').forEach(function (box) {
    box.insertAdjacentHTML("afterbegin",
      '<div class="hx-pr"><div class="hx-slot"><span>AL ARBAB &middot; TRIP TICKET</span></div><div class="hx-tkw"><div class="hx-tk" id="tk">' +
      '<div class="hx-t1"><small>FROM</small><b>ISB</b><span>Islamabad</span></div><div class="hx-t2"><i class="hx-ln2"></i><span class="hx-pl2">' + PLANE + '</span></div>' +
      '<div class="hx-t3"><small>TO</small><b id="tc">HKT</b><span id="tn">Phuket</span></div>' +
      '<div class="hx-t4"><i class="hx-bc"></i><em>Send your documents on WhatsApp</em></div></div></div>' +
      '<button class="hx-print" type="button">Print my trip ticket</button></div>');
    var cur = 0, tk = box.querySelector("#tk");
    function fill() { box.querySelector("#tc").textContent = D[cur].code; box.querySelector("#tn").textContent = D[cur].city; }
    function print() { tk.classList.remove("out"); void tk.offsetWidth; fill(); tk.classList.add("out"); }
    box.querySelector(".hx-print").addEventListener("click", print);
    chips(box, 0, function (i) { cur = i; print(); });
    setTimeout(print, 500);
  });

  document.querySelectorAll(".hx-s a").forEach(function (a) { a.addEventListener("click", function (e) { e.preventDefault(); }); });
})();
