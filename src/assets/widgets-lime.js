/* lime widget set (preview only) */
(function () {
  var $ = function (s) { return document.querySelector(s); };
  var all = function (s) { return [].slice.call(document.querySelectorAll(s)); };
  function pk() {
    var o = {}; new Intl.DateTimeFormat("en-GB", { timeZone: "Asia/Karachi", weekday: "short", hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false }).formatToParts(new Date()).forEach(function (x) { o[x.type] = x.value; });
    return o;
  }
  var DN = { Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6, Sun: 0 };
  function clock() {
    var t = pk(), m = +t.hour * 60 + +t.minute, d = DN[t.weekday], open = d !== 0 && m >= 540 && m < 1200;
    all(".lm-time").forEach(function (e) { e.innerHTML = t.hour + ":" + t.minute + "<sup>" + t.second + "</sup>"; });
    all(".lm-st").forEach(function (e) { e.textContent = open ? "OPEN" : "CLOSED"; e.classList.toggle("off", !open); });
    var pct = Math.max(0, Math.min(100, (m - 540) / 660 * 100));
    all(".lm-now").forEach(function (e) { e.style.left = pct + "%"; e.style.opacity = d === 0 ? 0 : 1; });
  }
  clock(); setInterval(clock, 1000);

  var D = [["Thailand", "Phuket", "HKT"], ["Malaysia", "Kuala Lumpur", "KUL"], ["Indonesia", "Bali", "DPS"], ["Singapore", "Singapore", "SIN"], ["Nepal", "Kathmandu", "KTM"], ["Vietnam", "Ho Chi Minh City", "SGN"]], di = 0;
  function dest() { var d = D[di]; all(".lm-code").forEach(function (e) { e.textContent = d[2]; }); all(".lm-city").forEach(function (e) { e.textContent = d[1]; }); di = (di + 1) % D.length; }
  dest(); setInterval(dest, 3600);

  function count(el, to, dec, ms) { var t0 = null; (function st(t) { if (!t0) t0 = t; var k = Math.min(1, (t - t0) / ms), e = 1 - Math.pow(1 - k, 3); el.textContent = (to * e).toFixed(dec); if (k < 1) requestAnimationFrame(st); })(performance.now()); }
  all(".lm-88").forEach(function (e) { count(e, 88, 0, 1400); });
  all(".lm-50").forEach(function (e) { count(e, 5, 1, 1300); });

  var ring = $(".lm-ring"); if (ring) setTimeout(function () { ring.style.setProperty("--p", 100); }, 300);

  all(".lm-wave").forEach(function (w) {
    var bars = []; for (var i = 0; i < 40; i++) { var b = document.createElement("i"); w.appendChild(b); bars.push(b); }
    setInterval(function () { bars.forEach(function (b, k) { b.style.height = (12 + Math.abs(Math.sin(Date.now() / 250 + k * .6)) * 38 * (.5 + Math.random() * .6)) + "px"; }); }, 120);
  });

  all(".lm-tabs").forEach(function (box) {
    var tabs = [].slice.call(box.querySelectorAll(".lm-tab")), rows = [].slice.call(box.querySelectorAll(".lm-rows"));
    tabs.forEach(function (t, i) { t.addEventListener("click", function () { tabs.forEach(function (x, k) { x.classList.toggle("on", k === i); }); rows.forEach(function (r, k) { r.hidden = k !== i; }); }); });
  });
  var nd = $(".lm-needle"); if (nd) { var x = 10, dir = 1; setInterval(function () { x += dir * .35; if (x > 88 || x < 10) dir = -dir; nd.style.left = x + "%"; }, 60); }
  all(".lmc a").forEach(function (a) { a.addEventListener("click", function (e) { e.preventDefault(); }); });
})();
