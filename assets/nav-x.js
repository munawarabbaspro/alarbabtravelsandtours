/* five non-glass navigation ideas (preview only) */
(function () {
  document.querySelectorAll(".nx-x a").forEach(function (a) { a.addEventListener("click", function (e) { e.preventDefault(); }); });
  var abc = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";

  // A · departure board: letters flip and scramble like a split-flap display
  document.querySelectorAll(".nx-fl").forEach(function (cell) {
    var chars = [].slice.call(cell.querySelectorAll(".nx-ch b")), word = chars.map(function (c) { return c.textContent; }), busy = 0;
    function flip() {
      if (busy) return; busy = 1;
      chars.forEach(function (c, i) {
        var n = 0, max = 5 + i * 2;
        var t = setInterval(function () {
          n++;
          if (n >= max) { c.textContent = word[i]; clearInterval(t); if (i === chars.length - 1) busy = 0; }
          else { c.textContent = abc[Math.floor(Math.random() * 26)]; }
        }, 45);
      });
    }
    cell.addEventListener("mouseenter", flip);
    cell.addEventListener("click", function () {
      var all = document.querySelectorAll(".nx-fl");
      all.forEach(function (x) { x.classList.remove("on"); x.querySelector("em").textContent = "ON TIME"; });
      cell.classList.add("on"); cell.querySelector("em").textContent = "BOARDING"; flip();
    });
  });

  // B · luggage tags: click pulls the tag down on its string
  document.querySelectorAll(".nx-tag").forEach(function (t) {
    t.addEventListener("click", function () {
      document.querySelectorAll(".nx-tag").forEach(function (x) { x.classList.remove("on"); });
      t.classList.add("on");
    });
  });

  // C · type takeover
  document.querySelectorAll(".nx-C").forEach(function (C) {
    var btn = C.querySelector(".nx-mb"), items = [].slice.call(C.querySelectorAll(".nx-ls a")), imgs = [].slice.call(C.querySelectorAll(".nx-pic img")), cap = C.querySelector(".nx-pic span");
    function set(i) {
      items.forEach(function (a, k) { a.classList.toggle("on", k === i); });
      imgs.forEach(function (m, k) { m.classList.toggle("on", k === i); });
      cap.textContent = items[i].getAttribute("data-c");
    }
    btn.addEventListener("click", function () { C.classList.toggle("open"); btn.firstChild.nodeValue = C.classList.contains("open") ? "CLOSE" : "MENU"; });
    items.forEach(function (a, i) { a.addEventListener("mouseenter", function () { set(i); }); });
    set(0);
  });

  // E · fan: items sit on an arc below the hub
  document.querySelectorAll(".nx-E").forEach(function (E) {
    var hub = E.querySelector(".nx-hub"), dots = [].slice.call(E.querySelectorAll(".nx-dot")), n = dots.length;
    function lay() {
      var narrow = E.clientWidth < 640, R = narrow ? 128 : 250;
      dots.forEach(function (d, i) {
        var a = (155 - 130 * (i / (n - 1))) * Math.PI / 180;
        d.style.setProperty("--x", Math.round(Math.cos(a) * R) + "px");
        d.style.setProperty("--y", Math.round(Math.sin(a) * R * .62 + 22) + "px");
        d.style.setProperty("--i", i);
      });
    }
    lay(); addEventListener("resize", lay);
    hub.addEventListener("click", function () { E.classList.toggle("open"); });
    dots.forEach(function (d) { d.addEventListener("click", function () { dots.forEach(function (x) { x.classList.remove("on"); }); d.classList.add("on"); }); });
    setTimeout(function () { E.classList.add("open"); }, 300);
  });
})();
