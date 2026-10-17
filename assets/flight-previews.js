/* flight route animation concepts for the hero (preview only) */
(function () {
  var NS = "http://www.w3.org/2000/svg";
  var reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  var PLANE = "M22,0 C22,-2 20,-3 17,-3 L4,-3 L-4,-17 L-9,-17 L-5,-3 L-14,-3 L-17,-8 L-20,-8 L-17,0 L-20,8 L-17,8 L-14,3 L-5,3 L-9,17 L-4,17 L4,3 L17,3 C20,3 22,2 22,0 Z";
  var PAPER = "M24,0 L-16,-13 L-8,0 L-16,13 Z M-8,0 L2,6 L-2,0 Z";
  var S = [110, 360], E = [650, 120];
  var LOOP = "M110,360 C300,390 400,270 345,200 C300,145 225,200 285,245 C345,290 470,90 650,120";
  var ARC = "M110,360 Q330,40 650,120";

  function el(n, a, p) { var e = document.createElementNS(NS, n); for (var k in a) e.setAttribute(k, a[k]); if (p) p.appendChild(e); return e; }
  function ease(t) { return t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2; }

  function Stage(box) {
    var mode = box.getAttribute("data-m");
    var svg = box.querySelector("svg"), raf = 0, t0 = 0, DUR = 3200, HOLD = 1300;
    svg.innerHTML = "";
    var defs = el("defs", {}, svg);
    var glow = el("filter", { id: "g" + mode, x: "-30%", y: "-30%", width: "160%", height: "160%" }, defs);
    el("feGaussianBlur", { stdDeviation: "4" }, glow);
    var d = mode === "paper" ? LOOP : ARC;
    var path = el("path", { d: d, fill: "none", stroke: "none" }, svg);
    var L = path.getTotalLength();
    function at(len) { return path.getPointAtLength(Math.max(0, Math.min(L, len))); }
    var plane, shadow, parts = {};

    // destination marker
    function dest(label) {
      var g = el("g", {}, svg);
      var r = el("circle", { cx: E[0], cy: E[1], r: 7, fill: "#fff" }, g);
      var ring = el("circle", { cx: E[0], cy: E[1], r: 7, fill: "none", stroke: "#fff", "stroke-width": 2, opacity: 0 }, g);
      var t = el("text", { x: E[0], y: E[1] - 20, "text-anchor": "middle", fill: "#fff", "font-size": 22, "font-weight": 800, "font-family": "Archivo,sans-serif" }, g); t.textContent = label || "HKT";
      return { g: g, ring: ring, t: t };
    }
    var org = el("g", {}, svg);
    el("circle", { cx: S[0], cy: S[1], r: 8, fill: "#fff" }, org);
    el("circle", { cx: S[0], cy: S[1], r: 3.5, fill: "#0b0e14" }, org);
    var dst = dest(mode === "ticket" ? "" : "HKT");

    if (mode === "contrail") {
      parts.glow = el("path", { d: d, fill: "none", stroke: "#bfe1ff", "stroke-width": 12, "stroke-linecap": "round", filter: "url(#g" + mode + ")", opacity: .55 }, svg);
      parts.core = el("path", { d: d, fill: "none", stroke: "#fff", "stroke-width": 3.5, "stroke-linecap": "round" }, svg);
      plane = el("path", { d: PLANE, fill: "#fff" }, svg);
    } else if (mode === "dots") {
      parts.dots = [];
      for (var l = 0; l < L; l += 20) { var p = at(l); parts.dots.push({ l: l, c: el("circle", { cx: p.x, cy: p.y, r: 3.2, fill: "#fff", opacity: 0 }, svg) }); }
      plane = el("path", { d: PLANE, fill: "#fff" }, svg);
    } else if (mode === "ticket") {
      el("path", { d: d, fill: "none", stroke: "rgba(255,255,255,.35)", "stroke-width": 2 }, svg);
      parts.prog = el("path", { d: d, fill: "none", stroke: "#fff", "stroke-width": 3, "stroke-dasharray": "0 " + L }, svg);
      var mid = at(L * .5); parts.mid = el("circle", { cx: mid.x, cy: mid.y, r: 6, fill: "#0b0e14", stroke: "#fff", "stroke-width": 3 }, svg);
      parts.chip = el("g", {}, svg);
      el("rect", { x: S[0] - 28, y: S[1] + 18, width: 56, height: 26, rx: 13, fill: "#fff" }, parts.chip);
      var ct = el("text", { x: S[0], y: S[1] + 36, "text-anchor": "middle", "font-size": 14, "font-weight": 800, fill: "#0b0e14", "font-family": "Inter,sans-serif" }, parts.chip); ct.textContent = "ISB";
      var c2 = el("g", {}, svg);
      el("rect", { x: E[0] - 30, y: E[1] + 16, width: 60, height: 26, rx: 13, fill: "#e30613" }, c2);
      var ct2 = el("text", { x: E[0], y: E[1] + 34, "text-anchor": "middle", "font-size": 14, "font-weight": 800, fill: "#fff", "font-family": "Inter,sans-serif" }, c2); ct2.textContent = "HKT";
      plane = el("path", { d: PLANE, fill: "#fff" }, svg);
    } else if (mode === "neon") {
      var gr = el("linearGradient", { id: "ng", gradientUnits: "userSpaceOnUse", x1: S[0], y1: S[1], x2: E[0], y2: E[1] }, defs);
      el("stop", { offset: 0, "stop-color": "#e30613" }, gr); el("stop", { offset: 1, "stop-color": "#ffffff" }, gr);
      parts.glow = el("path", { d: d, fill: "none", stroke: "url(#ng)", "stroke-width": 11, "stroke-linecap": "round", filter: "url(#g" + mode + ")", "stroke-dasharray": "0 " + L, opacity: .8 }, svg);
      parts.core = el("path", { d: d, fill: "none", stroke: "url(#ng)", "stroke-width": 3.5, "stroke-linecap": "round", "stroke-dasharray": "0 " + L }, svg);
      parts.rip = [0, 1, 2].map(function (i) { return el("circle", { cx: S[0], cy: S[1], r: 8, fill: "none", stroke: "#fff", "stroke-width": 2, opacity: 0 }, svg); });
      parts.sp = [];
      for (var k = 0; k < 14; k++) { var q = at(L * (k + 1) / 15); parts.sp.push({ l: L * (k + 1) / 15, c: el("path", { d: "M0,-7 L2,-2 L7,0 L2,2 L0,7 L-2,2 L-7,0 L-2,-2Z", fill: "#fff", transform: "translate(" + (q.x + (Math.random() * 16 - 8)) + "," + (q.y + (Math.random() * 16 - 8)) + ") scale(0)" }, svg) }); }
      plane = el("path", { d: PLANE, fill: "#fff" }, svg);
    } else if (mode === "depth") {
      shadow = el("g", {}, svg);
      parts.sPath = el("path", { d: d, fill: "none", stroke: "rgba(0,0,0,.45)", "stroke-width": 5, "stroke-dasharray": "2 12", "stroke-linecap": "round", transform: "translate(0,70)", filter: "url(#g" + mode + ")" }, svg);
      parts.sPl = el("path", { d: PLANE, fill: "rgba(0,0,0,.5)", filter: "url(#g" + mode + ")" }, svg);
      parts.line = el("path", { d: d, fill: "none", stroke: "#fff", "stroke-width": 3, "stroke-dasharray": "2 12", "stroke-linecap": "round" }, svg);
      plane = el("path", { d: PLANE, fill: "#fff" }, svg);
    } else if (mode === "paper") {
      parts.line = el("path", { d: d, fill: "none", stroke: "#fff", "stroke-width": 2.5, "stroke-dasharray": "0 " + L, "stroke-linecap": "round" }, svg);
      plane = el("path", { d: PAPER, fill: "#fff", "fill-rule": "evenodd" }, svg);
    }

    function frame(now) {
      if (!t0) t0 = now;
      var el_ = now - t0, tot = DUR + HOLD;
      var k = Math.min(1, el_ / DUR), e = ease(k), cur = L * e;
      var p = at(cur), q = at(cur + 2), a = Math.atan2(q.y - p.y, q.x - p.x) * 180 / Math.PI;
      var sc = 1;
      if (mode === "contrail" || mode === "neon") sc = 1.3 + .5 * Math.sin(Math.PI * k);
      else if (mode === "ticket") sc = 1.25;
      else if (mode === "dots") sc = 1.4 + .3 * Math.sin(Math.PI * k);
      else if (mode === "depth") sc = 1 + 1.1 * Math.sin(Math.PI * k) + .3;
      else if (mode === "paper") sc = 1.5;
      plane.setAttribute("transform", "translate(" + p.x + "," + p.y + ") rotate(" + a + ") scale(" + sc + ")");

      if (mode === "contrail") {
        var len = Math.min(cur, L * .38);
        var off = -(cur - len);
        [parts.glow, parts.core].forEach(function (pp) { pp.setAttribute("stroke-dasharray", len + " " + L * 2); pp.setAttribute("stroke-dashoffset", off); });
      } else if (mode === "dots") {
        parts.dots.forEach(function (o) { var v = o.l < cur ? 1 : 0; o.c.setAttribute("opacity", v); o.c.setAttribute("r", v ? 3.2 : 0); });
      } else if (mode === "ticket") {
        parts.prog.setAttribute("stroke-dasharray", cur + " " + L * 2);
        parts.mid.setAttribute("fill", cur > L * .5 ? "#fff" : "#0b0e14");
      } else if (mode === "neon") {
        [parts.glow, parts.core].forEach(function (pp) { pp.setAttribute("stroke-dasharray", cur + " " + L * 2); });
        parts.rip.forEach(function (r, i) {
          var tt = ((el_ / 1400) + i / 3) % 1;
          r.setAttribute("r", 8 + 34 * tt); r.setAttribute("opacity", (1 - tt) * .7);
        });
        parts.sp.forEach(function (s) {
          var v = Math.max(0, 1 - Math.abs(cur - s.l) / 90), tr = s.c.getAttribute("transform").replace(/scale\([^)]*\)/, "scale(" + (v * 1.2) + ")");
          s.c.setAttribute("transform", tr);
        });
      } else if (mode === "depth") {
        parts.line.setAttribute("stroke-dashoffset", 0);
        var alt = Math.sin(Math.PI * k);
        parts.sPl.setAttribute("transform", "translate(" + p.x + "," + (p.y + 70) + ") rotate(" + a + ") scale(" + (1.1 - .25 * alt) + "," + (.55 - .1 * alt) + ")");
        parts.sPl.setAttribute("opacity", .9 - .45 * alt);
      } else if (mode === "paper") {
        parts.line.setAttribute("stroke-dasharray", cur + " " + L * 2);
      }
      // destination ring pulse near the end
      var near = k > .92;
      dst.ring.setAttribute("opacity", near ? 1 - ((el_ - DUR * .92) % 900) / 900 : 0);
      dst.ring.setAttribute("r", near ? 7 + ((el_ - DUR * .92) % 900) / 900 * 26 : 7);
      if (el_ < tot * 2.2) raf = requestAnimationFrame(frame); else raf = 0;
    }
    this.play = function () {
      cancelAnimationFrame(raf); t0 = 0;
      if (reduce) { t0 = performance.now() - DUR; }
      raf = requestAnimationFrame(frame);
    };
    this.play();
  }
  var all = [];
  document.querySelectorAll(".fl-s").forEach(function (b) { all.push(new Stage(b)); });
  document.querySelectorAll("[data-fl-replay]").forEach(function (b) { b.addEventListener("click", function () { all.forEach(function (s) { s.play(); }); }); });
})();
