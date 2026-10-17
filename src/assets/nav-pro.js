/* pro-level nav concepts on bar D (preview only) */
(function () {
  var reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  document.querySelectorAll(".np-tg button").forEach(function (b) {
    b.addEventListener("click", function () {
      var s = b.closest(".np-s"); s.classList.toggle("lt");
      b.textContent = s.classList.contains("lt") ? "Dark" : "Light";
    });
  });
  document.querySelectorAll(".np-x a").forEach(function (a) { a.addEventListener("click", function (e) { e.preventDefault(); }); });

  /* tiny spring solver, one per animated value */
  function Spring(v, k, c) { this.x = v; this.t = v; this.v = 0; this.k = k || 220; this.c = c || 21; }
  Spring.prototype.step = function (dt) {
    var a = this.k * (this.t - this.x) - this.c * this.v;
    this.v += a * dt; this.x += this.v * dt;
  };
  Spring.prototype.rest = function () { return Math.abs(this.t - this.x) < .15 && Math.abs(this.v) < .15; };
  function loop(fn) {
    var raf = 0, last = 0;
    function tick(now) {
      var dt = Math.min(.033, (now - last) / 1000 || .016); last = now;
      var busy = fn(dt);
      raf = busy ? requestAnimationFrame(tick) : 0;
    }
    return function wake() { if (!raf) { last = performance.now(); raf = requestAnimationFrame(tick); } };
  }

  /* A · liquid glass lens: position and width are springs, the lens stretches with speed */
  document.querySelectorAll(".np-A").forEach(function (A) {
    var trk = A.querySelector(".np-trk"), lens = A.querySelector(".np-lens"), top = A.querySelector(".np-top");
    var items = [].slice.call(trk.querySelectorAll(".np-base .np-l")), cur = 0;
    var X = new Spring(0, 260, 22), Wd = new Spring(60, 260, 24);
    var wake = loop(function (dt) {
      X.step(dt); Wd.step(dt);
      var w = trk.offsetWidth, sx = 1 + Math.min(.28, Math.abs(X.v) / 2600), sy = 1 - Math.min(.1, Math.abs(X.v) / 9000);
      lens.style.left = X.x + "px"; lens.style.width = Wd.x + "px"; lens.style.transform = "scale(" + sx + "," + sy + ")";
      top.style.clipPath = "inset(0 " + Math.max(0, w - X.x - Wd.x) + "px 0 " + Math.max(0, X.x) + "px round 99px)";
      return !(X.rest() && Wd.rest());
    });
    function go(i, snap) {
      var el = items[i]; X.t = el.offsetLeft; Wd.t = el.offsetWidth;
      if (snap || reduce) { X.x = X.t; Wd.x = Wd.t; X.v = 0; Wd.v = 0; }
      wake();
    }
    items.forEach(function (el, i) {
      el.addEventListener("mouseenter", function () { go(i); });
      el.addEventListener("click", function () { cur = i; go(i); });
    });
    trk.addEventListener("mouseleave", function () { go(cur); });
    addEventListener("resize", function () { go(cur, true); });
    setTimeout(function () { go(0, true); }, 80);
  });

  /* B · mercury: the red liquid rises to the page, a head and two droplets follow on a lag */
  document.querySelectorAll(".np-th").forEach(function (T) {
    var lay = T.querySelector(".np-lay"), items = [].slice.call(lay.querySelectorAll(".np-l")),
        fill = T.querySelector(".np-fill"), head = T.querySelector(".np-head"), b1 = T.querySelector(".np-b1"), b2 = T.querySelector(".np-b2"), liq = T.querySelector(".np-liq");
    var S = [new Spring(0, 200, 19), new Spring(0, 130, 15), new Spring(0, 90, 13), new Spring(0, 60, 12)], cur = 0;
    var wake = loop(function (dt) {
      var busy = false;
      S.forEach(function (s) { s.step(dt); if (!s.rest()) busy = true; });
      var off = 5;
      fill.style.width = Math.max(0, S[1].x - off) + "px";
      head.style.transform = "translateX(" + (S[0].x - 19 - off) + "px)";
      b1.style.transform = "translateX(" + (S[2].x - 12 - off) + "px)";
      b2.style.transform = "translateX(" + (S[3].x - 7.5 - off) + "px)";
      return busy;
    });
    function go(i, snap, hover) {
      var el = items[i], c = el.offsetLeft + el.offsetWidth / 2 + 14;   // 14 = tube padding
      S.forEach(function (s) { s.t = c; if (snap || reduce) { s.x = c; s.v = 0; } });
      if (!hover) { items.forEach(function (x) { x.classList.remove("on"); }); el.classList.add("on"); }
      wake();
    }
    items.forEach(function (el, i) {
      el.addEventListener("mouseenter", function () { go(i, false, true); });
      el.addEventListener("click", function () { cur = i; go(i); });
    });
    lay.addEventListener("mouseleave", function () { go(cur, false, true); });
    addEventListener("resize", function () { go(cur, true); });
    setTimeout(function () { go(0, true); }, 80);
  });

  /* C · scroll morph: the full bar condenses into a crystal capsule with a progress ring */
  document.querySelectorAll(".np-sc").forEach(function (sc) {
    var bar = sc.querySelector(".np-bar"), cur = sc.querySelector(".np-curname"), ring = sc.querySelector(".np-ring");
    var names = ["Home", "Visas", "Destinations", "Flights", "Umrah", "Packages"];
    function upd() {
      var max = sc.scrollHeight - sc.clientHeight, p = max > 0 ? sc.scrollTop / max : 0;
      bar.classList.toggle("cond", sc.scrollTop > 24);
      var i = Math.min(names.length - 1, Math.floor(p * names.length));
      cur.textContent = "0" + (i + 1) + "  " + names[i];
      ring.style.setProperty("--p", Math.round(p * 100));
    }
    sc.addEventListener("scroll", upd, { passive: true });
    upd();
  });

  /* D · loupe: a glass lens follows the pointer and magnifies the page names under it */
  document.querySelectorAll(".np-D").forEach(function (D) {
    var trk = D.querySelector(".np-trk"), top = D.querySelector(".np-top"), lp = D.querySelector(".np-loupe");
    var items = [].slice.call(trk.querySelectorAll(".np-base .np-l")), cur = 0, R = 46;
    var X = new Spring(0, 170, 19), Y = new Spring(0, 170, 19), over = false;
    var wake = loop(function (dt) {
      X.step(dt); Y.step(dt);
      lp.style.transform = "translate(" + X.x + "px," + Y.x + "px)";
      top.style.clipPath = "circle(" + R + "px at " + X.x + "px " + Y.x + "px)";
      top.style.transformOrigin = X.x + "px " + Y.x + "px"; top.style.transform = "scale(1.22)";
      return !(X.rest() && Y.rest());
    });
    function rest(snap) {
      var el = items[cur]; X.t = el.offsetLeft + el.offsetWidth / 2; Y.t = el.offsetTop + el.offsetHeight / 2;
      if (snap || reduce) { X.x = X.t; Y.x = Y.t; X.v = Y.v = 0; }
      wake();
    }
    trk.addEventListener("mousemove", function (e) {
      var r = trk.getBoundingClientRect(); over = true;
      X.t = e.clientX - r.left; Y.t = r.height / 2 + Math.max(-6, Math.min(6, (e.clientY - r.top - r.height / 2) * .3));
      if (reduce) { X.x = X.t; Y.x = Y.t; }
      wake();
    });
    trk.addEventListener("mouseleave", function () { over = false; rest(); });
    items.forEach(function (el, i) { el.addEventListener("click", function () { cur = i; items.forEach(function (x) { x.classList.remove("on"); }); el.classList.add("on"); }); });
    addEventListener("resize", function () { rest(true); });
    setTimeout(function () { rest(true); }, 80);
  });
})();
