/* Galaxy welcome-screen preview: nebula + hyperspace star flight, then the logo pops in. Canvas 2D only, no libraries. */
(function () {
  var SETS = {
    asia: [["th", "Thailand"], ["my", "Malaysia"], ["id", "Indonesia"], ["sg", "Singapore"], ["vn", "Vietnam"], ["jp", "Japan"], ["kr", "South Korea"], ["cn", "China"],
           ["ae", "UAE"], ["tr", "Turkey"], ["lk", "Sri Lanka"], ["np", "Nepal"], ["kh", "Cambodia"], ["ph", "Philippines"], ["mv", "Maldives"], ["kz", "Kazakhstan"], ["az", "Azerbaijan"], ["hk", "Hong Kong"]],
    schengen: [["fr", "France"], ["de", "Germany"], ["it", "Italy"], ["es", "Spain"], ["ch", "Switzerland"], ["gr", "Greece"], ["nl", "Netherlands"], ["at", "Austria"],
               ["pt", "Portugal"], ["be", "Belgium"], ["se", "Sweden"], ["no", "Norway"], ["dk", "Denmark"], ["fi", "Finland"], ["cz", "Czechia"], ["pl", "Poland"], ["hu", "Hungary"], ["is", "Iceland"], ["mt", "Malta"], ["hr", "Croatia"]]
  };
  SETS.mix = [];
  for (var q = 0; q < 18; q++) { SETS.mix.push(SETS.asia[q % SETS.asia.length]); if (SETS.schengen[q]) SETS.mix.push(SETS.schengen[q]); }
  var IMG = {};
  function img(c) { if (!IMG[c]) { IMG[c] = new Image(); IMG[c].src = "/assets/flags/w80/" + c + ".png"; } return IMG[c]; }
  var reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  function Galaxy(stage) {
    var cv = stage.querySelector("canvas"), ctx = cv.getContext("2d");
    var W = 0, H = 0, D = 1, neb = null, stars = [], t0 = 0, raf = 0, N = 0;
    var set = null, cards = [], nx = 0;
    function ease(x) { return x < 0 ? 0 : x > 1 ? 1 : x * x * (3 - 2 * x); }
    function build() {
      set = SETS[stage.getAttribute("data-set")] || null; nx = 0;
      if (set) set.forEach(function (f) { img(f[0]); });
      D = Math.min(2, devicePixelRatio || 1);
      W = cv.width = Math.round(stage.clientWidth * D);
      H = cv.height = Math.round(stage.clientHeight * D);
      N = set ? (W < 700 ? 60 : 110) : (W < 700 ? 130 : 230);
      cards = [];
      if (set) for (var k = 0; k < (W < 700 ? 7 : 12); k++) cards.push(newCard(.3 + (k / (W < 700 ? 7 : 12)) * .7));
      stars = [];
      for (var i = 0; i < N; i++) stars.push({ x: Math.random() * 2 - 1, y: Math.random() * 2 - 1, z: Math.random() * .96 + .04, pz: 0 });
      // nebula, rendered once at low resolution and scaled up
      neb = document.createElement("canvas");
      var nw = Math.max(64, W >> 2), nh = Math.max(64, H >> 2), n = neb.getContext("2d");
      neb.width = nw; neb.height = nh;
      n.fillStyle = "#04070f"; n.fillRect(0, 0, nw, nh);
      function blob(x, y, r, c) {
        var g = n.createRadialGradient(x * nw, y * nh, 0, x * nw, y * nh, r * Math.max(nw, nh));
        g.addColorStop(0, c); g.addColorStop(1, "rgba(0,0,0,0)");
        n.fillStyle = g; n.fillRect(0, 0, nw, nh);
      }
      blob(.28, .42, .62, "rgba(28,84,214,.60)");
      blob(.74, .62, .55, "rgba(112,58,205,.40)");
      blob(.56, .24, .46, "rgba(30,170,225,.28)");
      blob(.5, .5, .34, "rgba(227,6,19,.14)");
      blob(.12, .86, .40, "rgba(20,48,130,.50)");
    }
    function newCard(z) {
      var a = Math.random() * Math.PI * 2, r = .8 + Math.random() * .8, f = set[nx++ % set.length];
      return { x: Math.cos(a) * r, y: Math.sin(a) * r * .72, z: z, c: f[0], n: f[1] };
    }
    function circ(x, y, d, im) {
      ctx.save(); ctx.beginPath(); ctx.arc(x, y, d / 2, 0, 6.2832); ctx.clip();
      if (im.complete && im.naturalWidth) {
        var iw = im.naturalWidth, ih = im.naturalHeight, z = Math.min(iw, ih);
        ctx.drawImage(im, (iw - z) / 2, (ih - z) / 2, z, z, x - d / 2, y - d / 2, d, d);
      } else { ctx.fillStyle = "#223"; ctx.fill(); }
      ctx.restore();
    }
    function drawCircle(c, t, sty) {
      var cx = W / 2, cy = H / 2, f = Math.max(W, H) * .55 * .35;
      var x = cx + c.x / c.z * f, y = cy + c.y / c.z * f;
      var d = Math.min(W * .072, Math.max(W * .026, 20 * D) / Math.pow(c.z, .7));
      var al = Math.min(1, (1 - c.z) * 3) * (1 - ease((t - 1.15) / .7));
      if (al <= .01 || x < -d * 3 || x > W + d * 3 || y < -d * 2 || y > H + d * 2) return;
      var im = img(c.c), lab;
      ctx.globalAlpha = al; ctx.textAlign = "center"; ctx.textBaseline = "middle";
      if (sty === "pill") {
        lab = Math.max(8 * D, d * .38); ctx.font = "700 " + lab + "px Inter,Arial,sans-serif";
        var ph = d * 1.3, tw = ctx.measureText(c.n).width, pw = ph + tw + lab * .9, rx = x - pw / 2, ry = y - ph / 2;
        ctx.fillStyle = "rgba(16,30,66,.58)"; ctx.strokeStyle = "rgba(180,208,255,.45)"; ctx.lineWidth = Math.max(1, D);
        ctx.beginPath(); ctx.arc(rx + ph / 2, y, ph / 2, Math.PI / 2, Math.PI * 1.5); ctx.arc(rx + pw - ph / 2, y, ph / 2, -Math.PI / 2, Math.PI / 2); ctx.closePath(); ctx.fill(); ctx.stroke();
        circ(rx + ph / 2, y, d, im);
        ctx.fillStyle = "#fff"; ctx.textAlign = "left"; ctx.fillText(c.n, rx + ph + lab * .1, y + lab * .04);
      } else {
        if (sty === "comet") {
          var z2 = Math.min(1.4, c.z + .16), x2 = cx + c.x / z2 * f, y2 = cy + c.y / z2 * f;
          var g = ctx.createLinearGradient(x2, y2, x, y);
          g.addColorStop(0, "rgba(120,170,255,0)"); g.addColorStop(1, "rgba(150,200,255,.85)");
          ctx.strokeStyle = g; ctx.lineCap = "round"; ctx.lineWidth = d * .62;
          ctx.beginPath(); ctx.moveTo(x2, y2); ctx.lineTo(x, y); ctx.stroke();
        }
        ctx.shadowColor = "rgba(110,165,255,.9)"; ctx.shadowBlur = d * .55;
        circ(x, y, d, im);
        ctx.shadowBlur = 0; ctx.shadowColor = "transparent";
        ctx.strokeStyle = "rgba(255,255,255,.92)"; ctx.lineWidth = Math.max(1.4 * D, d * .06);
        ctx.beginPath(); ctx.arc(x, y, d / 2, 0, 6.2832); ctx.stroke();
        lab = Math.max(8 * D, d * .3); ctx.font = "700 " + lab + "px Inter,Arial,sans-serif";
        ctx.shadowColor = "rgba(0,0,20,.9)"; ctx.shadowBlur = 4 * D;
        ctx.fillStyle = "#fff"; ctx.fillText(c.n, x, y + d / 2 + lab * 1.05);
        ctx.shadowBlur = 0; ctx.shadowColor = "transparent";
      }
      ctx.globalAlpha = 1;
    }
    function drawCard(c, t, sp) {
      var sty = stage.getAttribute("data-style");
      if (sty) return drawCircle(c, t, sty);
      var cx = W / 2, cy = H / 2, f = Math.max(W, H) * .55 * .35;
      var x = cx + c.x / c.z * f, y = cy + c.y / c.z * f;
      var cw = Math.min(W * .24, Math.max(W * .055, 40 * D) / Math.pow(c.z, .8)), ch = cw * .68, lab = Math.max(9 * D, cw * .15);
      var fade = 1 - ease((t - 1.1) / .7);
      var al = Math.min(1, (1 - c.z) * 3) * fade;
      if (al <= .01 || x < -cw || x > W + cw || y < -cw || y > H + cw) return;
      var pad = cw * .07, bw = cw + pad * 2, bh = ch + lab * 1.9 + pad;
      ctx.globalAlpha = al;
      ctx.fillStyle = "rgba(14,26,58,.62)"; ctx.strokeStyle = "rgba(170,200,255,.38)"; ctx.lineWidth = Math.max(1, D);
      var rx = x - bw / 2, ry = y - bh / 2, rr = Math.min(14 * D, bw * .12);
      ctx.beginPath();
      ctx.moveTo(rx + rr, ry); ctx.arcTo(rx + bw, ry, rx + bw, ry + bh, rr); ctx.arcTo(rx + bw, ry + bh, rx, ry + bh, rr);
      ctx.arcTo(rx, ry + bh, rx, ry, rr); ctx.arcTo(rx, ry, rx + bw, ry, rr); ctx.closePath(); ctx.fill(); ctx.stroke();
      var im = img(c.c);
      if (im.complete && im.naturalWidth) ctx.drawImage(im, rx + pad, ry + pad, cw, ch);
      ctx.fillStyle = "#fff"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
      ctx.font = "700 " + lab + "px Inter,Arial,sans-serif";
      ctx.fillText(c.n, x, ry + pad + ch + lab * 1.05, bw - pad);
      ctx.globalAlpha = 1;
    }
    function frame(now) {
      var t = (now - t0) / 1000;
      var sp = t < .25 ? .25 + t * 2.2 : t < 1.5 ? .8 : Math.max(.04, .8 * (1 - ease((t - 1.5) / 1.1)));
      var drift = 1.06 - Math.min(1, t / 3) * .06;
      ctx.globalCompositeOperation = "source-over";
      ctx.save();
      ctx.translate(W / 2, H / 2); ctx.scale(drift, drift); ctx.rotate(Math.sin(t * .3) * .02);
      ctx.drawImage(neb, -W / 2, -H / 2, W, H);
      ctx.restore();
      var cx = W / 2, cy = H / 2, f = Math.max(W, H) * .55;
      ctx.lineCap = "round";
      for (var i = 0; i < stars.length; i++) {
        var s = stars[i];
        s.pz = s.z;
        s.z -= sp * .012;
        if (s.z <= .03) { s.x = Math.random() * 2 - 1; s.y = Math.random() * 2 - 1; s.z = 1; s.pz = 1; }
        var x = cx + s.x / s.z * f * .35, y = cy + s.y / s.z * f * .35;
        var px = cx + s.x / s.pz * f * .35, py = cy + s.y / s.pz * f * .35;
        var b = Math.min(1, (1 - s.z) * 1.4 + .15);
        ctx.strokeStyle = "rgba(" + (190 + (i % 3) * 20) + "," + (215 + (i % 2) * 20) + ",255," + b + ")";
        ctx.lineWidth = (.6 + (1 - s.z) * 1.7) * D;
        ctx.beginPath(); ctx.moveTo(px, py); ctx.lineTo(x, y); ctx.stroke();
      }
      if (set) {
        cards.sort(function (a, b) { return b.z - a.z; });
        for (var j = 0; j < cards.length; j++) {
          var c = cards[j];
          if (t < 1.8) c.z -= sp * .0066;
          if (c.z <= .24) { var nc = newCard(1); cards[j] = nc; continue; }
          drawCard(c, t, sp);
        }
      }
      if (t < 4) raf = requestAnimationFrame(frame);
    }
    this.play = function () {
      cancelAnimationFrame(raf);
      stage.classList.remove("go");
      void stage.offsetWidth;
      build();
      t0 = performance.now();
      if (reduce) { stage.classList.add("go", "still"); return; }
      stage.classList.add("go");
      raf = requestAnimationFrame(frame);
    };
    addEventListener("resize", function () { build(); });
    build();
  }
  var list = [];
  document.querySelectorAll(".gx").forEach(function (s) { list.push(new Galaxy(s)); });
  function all() { list.forEach(function (g) { g.play(); }); }
  document.querySelectorAll("[data-setbtn]").forEach(function (b) {
    b.addEventListener("click", function () {
      document.querySelectorAll(".gx[data-style]").forEach(function (s) { s.setAttribute("data-set", b.getAttribute("data-setbtn")); });
      document.querySelectorAll("[data-setbtn]").forEach(function (o) { o.classList.toggle("on", o === b); });
      all();
    });
  });
  document.querySelectorAll("[data-replay]").forEach(function (b) { b.addEventListener("click", all); });
  setTimeout(all, 250);
})();
