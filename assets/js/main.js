/* Ishika Thakkar portfolio: fitted type, scroll reveals, colour curtain. No dependencies. */
(function () {
  var doc = document.documentElement;
  doc.classList.remove("no-js");
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* 1. Fit display lines to the exact width of their container. */
  function fit(el) {
    var span = el.firstElementChild;
    if (!span) return;
    var max = parseFloat(el.getAttribute("data-max")) || Infinity;
    el.style.fontSize = "100px";
    var w = el.clientWidth;
    var tw = span.getBoundingClientRect().width;
    if (!tw || !w) return;
    var size = Math.min(max, (100 * w) / tw) * 0.995;
    el.style.fontSize = Math.floor(size * 10) / 10 + "px";
    el.classList.add("ready");
  }
  var fits = [].slice.call(document.querySelectorAll(".fit"));
  function fitAll() {
    var live = fits.filter(function (el) { return el.firstElementChild; });
    live.forEach(function (el) { el.style.fontSize = "100px"; });
    var sizes = live.map(function (el) {
      var w = el.clientWidth, tw = el.firstElementChild.getBoundingClientRect().width;
      if (!tw || !w) return null;
      var max = parseFloat(el.getAttribute("data-max")) || Infinity;
      return Math.floor(Math.min(max, (100 * w) / tw) * 0.995 * 10) / 10;
    });
    live.forEach(function (el, i) {
      if (sizes[i] == null) return;
      el.style.fontSize = sizes[i] + "px";
      el.classList.add("ready");
    });
  }
  fitAll();
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitAll);
  var t;
  window.addEventListener("resize", function () { clearTimeout(t); t = setTimeout(fitAll, 80); });

  /* Deep links land after font fitting and image dimensions have settled.
     Hash destinations use native navigation, never a delayed curtain redirect. */
  [].forEach.call(document.querySelectorAll(".all-work-link"), function (link) {
    var url = new URL(link.href, location.href);
    url.searchParams.set("view", "work");
    link.href = url.href;
  });
  function settleHash() {
    var workView = new URLSearchParams(location.search).get("view") === "work";
    if (!location.hash && !workView) return;
    var id;
    try { id = workView ? "work" : decodeURIComponent(location.hash.slice(1)); } catch (e) { return; }
    var target = document.getElementById(id);
    if (!target) return;
    requestAnimationFrame(function () { target.scrollIntoView({ block: "start", behavior: "instant" }); });
  }
  window.addEventListener("load", function () {
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(settleHash);
    else settleHash();
  });

  /* 2. Reveal on scroll. */
  var io = "IntersectionObserver" in window ? new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
    });
  }, { threshold: 0.18 }) : null;
  [].forEach.call(document.querySelectorAll(".reveal, .panel, .daynight .home"), function (el) {
    if (io) io.observe(el); else el.classList.add("in");
  });

  /* 3. Colour curtain between pages: links carry data-color / data-on / data-label. */
  var curtain = document.querySelector(".curtain");
  var KEY = "it-curtain";
  if (curtain && !reduce) {
    try {
      var saved = JSON.parse(sessionStorage.getItem(KEY) || "null");
      if (saved) {
        sessionStorage.removeItem(KEY);
        curtain.style.setProperty("--cc", saved.c);
        curtain.style.setProperty("--con", saved.on);
        curtain.querySelector("b").textContent = saved.label || "";
        curtain.className = "curtain hold";
        requestAnimationFrame(function () {
          requestAnimationFrame(function () { curtain.className = "curtain lift"; });
        });
      }
    } catch (e) {}
    document.addEventListener("click", function (ev) {
      var a = ev.target.closest && ev.target.closest("a[data-color]");
      if (!a || ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.altKey || ev.button !== 0) return;
      if (a.target === "_blank") return;
      var destination = new URL(a.href, location.href);
      if (destination.hash || destination.origin !== location.origin) return;
      ev.preventDefault();
      var data = { c: a.getAttribute("data-color"), on: a.getAttribute("data-on") || "#121211", label: a.getAttribute("data-label") || "" };
      curtain.style.setProperty("--cc", data.c);
      curtain.style.setProperty("--con", data.on);
      curtain.querySelector("b").textContent = data.label;
      curtain.className = "curtain cover";
      try { sessionStorage.setItem(KEY, JSON.stringify(data)); } catch (e) {}
      setTimeout(function () { window.location.href = a.href; }, 480);
    });
    window.addEventListener("pageshow", function (e) { if (e.persisted) curtain.className = "curtain"; });
  }
})();
