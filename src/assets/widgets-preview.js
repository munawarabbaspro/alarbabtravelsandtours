/* neon widget board (preview only): live clock, rotating destination, count-up, waveform, tuner */
(function () {
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var all = function (s, r) { return [].slice.call((r || document).querySelectorAll(s)); };

  // accent colours per card
  var COL = { g: "#35ff4a", y: "#e8ff1a", o: "#ff5a12", p: "#ff1f5c", b: "#2fb6ff" };
  all(".wd").forEach(function (c) {
    function set(k) { c.style.setProperty("--a", COL[k]); c.setAttribute("data-c", k); all(".wd-cd button", c).forEach(function (b) { b.classList.toggle("on", b.getAttribute("data-k") === k); }); }
    all(".wd-cd button", c).forEach(function (b) { b.addEventListener("click", function () { set(b.getAttribute("data-k")); }); });
    set(c.getAttribute("data-c"));
  });
  var bar = $(".wd-all");
  if (bar) all("[data-all]", bar).forEach(function (b) { b.addEventListener("click", function () { all(".wd").forEach(function (c) { all('.wd-cd button[data-k="' + b.getAttribute("data-all") + '"]', c).forEach(function (x) { x.click(); }); }); }); });

  /* 1 · clock + office hours (Mon-Sat 9 AM - 8 PM, Islamabad) */
  function pk() {
    var p = new Intl.DateTimeFormat("en-GB", { timeZone: "Asia/Karachi", weekday: "long", day: "numeric", hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false }).formatToParts(new Date()), o = {};
    p.forEach(function (x) { o[x.type] = x.value; }); return o;
  }
  var DAY = { Monday: 1, Tuesday: 2, Wednesday: 3, Thursday: 4, Friday: 5, Saturday: 6, Sunday: 0 };
  function clock() {
    var t = pk(), h = +t.hour, m = +t.minute, dn = DAY[t.weekday];
    if ($("#wd-day")) {
      $("#wd-day").innerHTML = t.weekday + " <sup>" + t.day + "</sup>";
      $("#wd-time").innerHTML = t.hour + ":" + t.minute + "<sup>" + t.second + "</sup>";
      var mins = h * 60 + m, open = dn !== 0 && mins >= 540 && mins < 1200;
      $("#wd-st").textContent = open ? "OPEN" : "CLOSED";
      $("#wd-st").classList.toggle("off", !open);
      var pct = Math.max(0, Math.min(100, (mins - 540) / (1200 - 540) * 100));
      $("#wd-now").style.left = pct + "%";
      $("#wd-now").style.opacity = dn === 0 ? 0 : 1;
    }
  }
  clock(); setInterval(clock, 1000);

  /* 2 · route card cycles through the destinations */
  var D = [["Thailand", "Phuket", "HKT"], ["Malaysia", "Kuala Lumpur", "KUL"], ["Indonesia", "Bali", "DPS"], ["Singapore", "Singapore", "SIN"], ["Nepal", "Kathmandu", "KTM"], ["Vietnam", "Ho Chi Minh City", "SGN"]];
  var di = 0;
  function dest() {
    var d = D[di]; if (!$("#wd-code")) return;
    $("#wd-code").textContent = d[2]; $("#wd-city").textContent = d[1]; $("#wd-ctry").textContent = d[0] + " visit visa";
    di = (di + 1) % D.length;
  }
  dest(); setInterval(dest, 3600);

  /* 3 · count-up for the number of guides and the rating */
  function count(el, to, dec, ms) {
    var t0 = null;
    function st(t) { if (!t0) t0 = t; var k = Math.min(1, (t - t0) / ms), e = 1 - Math.pow(1 - k, 3); el.textContent = (to * e).toFixed(dec); if (k < 1) requestAnimationFrame(st); }
    requestAnimationFrame(st);
  }
  if ($("#wd-88")) count($("#wd-88"), 88, 0, 1400);
  if ($("#wd-50")) count($("#wd-50"), 5, 1, 1300);

  /* 5 · waveform bars */
  var wv = $(".wd-wave");
  if (wv) {
    var bars = []; for (var i = 0; i < 44; i++) { var b = document.createElement("i"); wv.appendChild(b); bars.push(b); }
    setInterval(function () { bars.forEach(function (b, k) { b.style.height = (14 + Math.abs(Math.sin(Date.now() / 260 + k * .6)) * 40 * (.5 + Math.random() * .6)) + "px"; }); }, 120);
  }

  /* 6 · tuner needle sweeps slowly */
  var nd = $(".wd-needle");
  if (nd) { var x = 10, dir = 1; setInterval(function () { x += dir * .35; if (x > 88 || x < 10) dir = -dir; nd.style.left = x + "%"; }, 60); }

  all(".wd a").forEach(function (a) { a.addEventListener("click", function (e) { e.preventDefault(); }); });
})();
