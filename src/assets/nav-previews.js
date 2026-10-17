/* navigation bar concepts (preview only) */
(function () {
  // light / dark toggle on every stage
  document.querySelectorAll(".nb-stg .nb-tg button").forEach(function (b) {
    b.addEventListener("click", function () {
      var s = b.closest(".nb-stg");
      s.classList.toggle("lt");
      b.textContent = s.classList.contains("lt") ? "Dark" : "Light";
      s.dispatchEvent(new Event("themechange"));
    });
  });

  // A: the plane flies to the hovered / active stop
  document.querySelectorAll(".nb-fr").forEach(function (fr) {
    var route = fr.querySelector(".nb-route"), pl = fr.querySelector(".nb-pl"), tr = fr.querySelector(".nb-trail");
    var stops = [].slice.call(fr.querySelectorAll(".nb-st")), cur = fr.querySelector(".nb-st.on") || stops[0];
    function go(el) {
      var r = route.getBoundingClientRect(), s = el.getBoundingClientRect(), x = s.left + s.width / 2 - r.left;
      pl.style.left = x + "px"; tr.style.width = x + "px";
    }
    function set(el) { stops.forEach(function (s) { s.classList.remove("on"); }); el.classList.add("on"); cur = el; go(el); }
    stops.forEach(function (s) {
      s.addEventListener("mouseenter", function () { go(s); });
      s.addEventListener("focus", function () { go(s); });
      s.addEventListener("click", function (e) { e.preventDefault(); set(s); });
    });
    route.addEventListener("mouseleave", function () { go(cur); });
    addEventListener("resize", function () { go(cur); });
    setTimeout(function () { go(cur); }, 60);
  });

  // E: highlight pill slides under the hovered / active item
  document.querySelectorAll(".nb-is .nb-nv").forEach(function (nv) {
    var hl = nv.querySelector(".nb-hl"), items = [].slice.call(nv.querySelectorAll("a")), cur = nv.querySelector("a.on") || items[0];
    function go(el) { hl.style.left = el.offsetLeft + "px"; hl.style.width = el.offsetWidth + "px"; }
    items.forEach(function (a) {
      a.addEventListener("mouseenter", function () { go(a); });
      a.addEventListener("click", function (e) { e.preventDefault(); items.forEach(function (x) { x.classList.remove("on"); }); a.classList.add("on"); cur = a; go(a); });
    });
    nv.addEventListener("mouseleave", function () { go(cur); });
    addEventListener("resize", function () { go(cur); });
    setTimeout(function () { go(cur); }, 60);
  });

  // keep demo links from navigating
  document.querySelectorAll(".nbx a").forEach(function (a) { a.addEventListener("click", function (e) { e.preventDefault(); }); });
})();
