/* nav D + crystal tube ideas (preview only) */
(function () {
  document.querySelectorAll(".nd-s .nd-tg button").forEach(function (b) {
    b.addEventListener("click", function () {
      var s = b.closest(".nd-s"); s.classList.toggle("lt");
      b.textContent = s.classList.contains("lt") ? "Dark" : "Light";
    });
  });
  document.querySelectorAll(".nd-x a").forEach(function (a) { a.addEventListener("click", function (e) { e.preventDefault(); }); });

  // 1 · lens tube: the glass slides to the pointed item and the red copy shows through it
  document.querySelectorAll(".nd-tube").forEach(function (t) {
    var lens = t.querySelector(".nd-lens"), top = t.querySelector(".nd-top"), base = t.querySelector(".nd-base");
    var items = [].slice.call(base.querySelectorAll(".nd-l")), tops = [].slice.call(top.querySelectorAll(".nd-l")), cur = 0;
    function go(i) {
      var el = items[i], w = t.offsetWidth, l = el.offsetLeft, r = w - (l + el.offsetWidth);
      lens.style.left = l + "px"; lens.style.width = el.offsetWidth + "px";
      top.style.clipPath = "inset(0 " + r + "px 0 " + l + "px round 99px)";
    }
    items.forEach(function (el, i) {
      el.addEventListener("mouseenter", function () { go(i); });
      el.addEventListener("click", function () { cur = i; go(i); });
    });
    t.addEventListener("mouseleave", function () { go(cur); });
    addEventListener("resize", function () { go(cur); });
    setTimeout(function () { go(0); }, 80);
  });

  // 2 · drum: items sit on a cylinder, arrows / wheel / click turn it
  document.querySelectorAll(".nd-hold").forEach(function (h) {
    var cyl = h.querySelector(".nd-cyl"), items = [].slice.call(cyl.querySelectorAll(".nd-l")), n = items.length, step = 24, R = 300, cur = 0;
    items.forEach(function (el, i) { el.style.transform = "rotateY(" + (i * step) + "deg) translateZ(" + R + "px)"; });
    function show(i) {
      cur = (i + n) % n;
      cyl.style.transform = "translateZ(-" + R + "px) rotateY(" + (-cur * step) + "deg)";
      items.forEach(function (el, k) {
        var d = Math.abs(((k - cur + n + n / 2) % n) - n / 2);
        el.classList.toggle("on", k === cur); el.style.opacity = d > 2.2 ? 0 : 1 - d * .28;
      });
    }
    items.forEach(function (el, i) { el.addEventListener("click", function () { show(i); }); });
    h.querySelector(".nd-prev").addEventListener("click", function () { show(cur - 1); });
    h.querySelector(".nd-next").addEventListener("click", function () { show(cur + 1); });
    var lock = 0;
    h.addEventListener("wheel", function (e) { e.preventDefault(); var now = Date.now(); if (now - lock < 220) return; lock = now; show(cur + (e.deltaY > 0 || e.deltaX > 0 ? 1 : -1)); }, { passive: false });
    show(0);
  });

  // 3 · funnel: the glass funnel follows the active item, name drops in red
  document.querySelectorAll(".nd-fun").forEach(function (f) {
    var fun = f.querySelector(".nd-funnel"), tx = f.querySelector(".nd-tx"), links = f.querySelector(".nd-lay");
    var items = [].slice.call(f.querySelectorAll(".nd-l")), cur = 0;
    function go(i, hover) {
      var el = items[i], fr = f.getBoundingClientRect(), r = el.getBoundingClientRect();
      fun.style.left = (r.left + r.width / 2 - fr.left) + "px";
      tx.textContent = el.getAttribute("data-n");
      if (!hover) { items.forEach(function (x) { x.classList.remove("on"); }); el.classList.add("on"); }
    }
    items.forEach(function (el, i) {
      el.addEventListener("mouseenter", function () { go(i, true); });
      el.addEventListener("click", function () { cur = i; go(i); });
    });
    links.addEventListener("mouseleave", function () { go(cur, true); });
    addEventListener("resize", function () { go(cur); });
    setTimeout(function () { go(0); }, 80);
  });
})();
