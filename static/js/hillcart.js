/* Darjeeling Tour Plan · The Hill Cart interactions
   Free libraries (CDN): GSAP + ScrollTrigger, Lenis. Live weather from Open-Meteo (free, no key).
   Maps are server-drawn SVG. Everything degrades: without JS the site reads, links and submits. */
(function () {
  "use strict";
  var doc = document.documentElement;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var track = function (name, data) { window.dataLayer = window.dataLayer || []; window.dataLayer.push(Object.assign({ event: name }, data || {})); };
  var store = {
    get: function (k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { sessionStorage.setItem(k, v); } catch (e) {} }
  };
  var fmt = function (n) { return Math.round(n).toLocaleString("en-IN"); };

  /* analytics: every CTA and form reports itself */
  document.addEventListener("click", function (e) {
    var a = e.target.closest("[data-cta]");
    if (a) track("cta_click", { cta: a.dataset.cta, href: a.getAttribute("href") || "" });
  });
  $$("form[data-cta-form]").forEach(function (f) { f.addEventListener("submit", function () { track("form_submit", { form: f.dataset.ctaForm }); }); });

  /* masthead + floating CTA visibility */
  var mast = $(".mast"), fab = $("[data-fab]");
  var onScroll = function () {
    var y = window.scrollY;
    if (mast) mast.classList.toggle("is-scrolled", y > 24);
    if (fab) fab.classList.toggle("is-on", y > 420);
  };

  /* mega menus: hover on desktop (with a bridge over the gap), click anywhere, Esc closes */
  var drops = $$(".nav__drop");
  var closeAll = function (except) { drops.forEach(function (d) { if (d !== except) { d.classList.remove("is-open"); $("button", d).setAttribute("aria-expanded", "false"); } }); };
  drops.forEach(function (drop) {
    var btn = $("button", drop), timer;
    var open = function () { clearTimeout(timer); closeAll(drop); drop.classList.add("is-open"); btn.setAttribute("aria-expanded", "true"); };
    var close = function () { drop.classList.remove("is-open"); btn.setAttribute("aria-expanded", "false"); };
    btn.addEventListener("click", function (e) { e.stopPropagation(); drop.classList.contains("is-open") ? close() : open(); });
    if (window.matchMedia("(hover: hover)").matches) {
      drop.addEventListener("mouseenter", function () { clearTimeout(timer); if (!drop.classList.contains("is-open")) timer = setTimeout(open, 80); });
      drop.addEventListener("mouseleave", function () { clearTimeout(timer); timer = setTimeout(close, 280); });
    }
  });
  document.addEventListener("click", function (e) { if (!e.target.closest(".nav__drop")) closeAll(); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") { closeAll(); closeSearch(); closeFab(); } });

  /* mobile sheet */
  var sheet = $(".sheet");
  $$("[data-sheet-open]").forEach(function (b) { b.addEventListener("click", function () { sheet.classList.add("is-open"); document.body.style.overflow = "hidden"; $(".sheet__close", sheet).focus(); }); });
  $$("[data-sheet-close]").forEach(function (b) { b.addEventListener("click", function () { sheet.classList.remove("is-open"); document.body.style.overflow = ""; }); });

  /* search overlay: loads a small JSON index on first open, "/" opens it */
  var search = $(".search"), input = $("#q"), results = $(".search__results"), index = null;
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;" }[c]; }); };
  var norm = function (s) { return String(s).toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, ""); };
  function openSearch() {
    if (!search) return;
    if (sheet) sheet.classList.remove("is-open");
    search.hidden = false; document.body.style.overflow = "hidden"; input.focus();
    if (!index) fetch(input.dataset.searchUrl).then(function (r) { return r.json(); }).then(function (d) { index = d.map(function (row) { return { t: row[0], u: row[1], k: row[2], c: row[3], n: norm(row[0] + " " + row[3] + " " + row[2]) }; }); run(); });
    track("search_open");
  }
  function closeSearch() { if (search && !search.hidden) { search.hidden = true; document.body.style.overflow = ""; } }
  function run() {
    if (!index) return;
    var q = norm(input.value.trim());
    if (q.length < 2) { results.innerHTML = ""; return; }
    var words = q.split(/\s+/);
    var hits = index.filter(function (r) { return words.every(function (w) { return r.n.indexOf(w) > -1; }); })
      .sort(function (a, b) { return (norm(a.t).indexOf(words[0]) === 0 ? -1 : 0) - (norm(b.t).indexOf(words[0]) === 0 ? -1 : 0) || a.t.length - b.t.length; })
      .slice(0, 14);
    results.innerHTML = hits.length ? hits.map(function (r) { return '<li><a href="' + esc(r.u) + '"><b>' + esc(r.t) + '</b><small>' + esc(r.k) + (r.c ? " · " + esc(r.c) : "") + "</small></a></li>"; }).join("")
      : '<li class="small muted" style="padding:12px">No match. <a href="/plan/">Ask a planner instead</a>.</li>';
  }
  $$("[data-search-open]").forEach(function (b) { b.addEventListener("click", openSearch); });
  $$("[data-search-close]").forEach(function (b) { b.addEventListener("click", closeSearch); });
  if (search) {
    search.addEventListener("click", function (e) { if (e.target === search) closeSearch(); });
    input.addEventListener("input", run);
    document.addEventListener("keydown", function (e) { if (e.key === "/" && !/input|textarea|select/i.test(document.activeElement.tagName)) { e.preventDefault(); openSearch(); } });
  }

  /* floating CTA */
  var fabPanel = $("#fab-panel"), fabBtn = $(".fab__toggle");
  function closeFab() { if (fabPanel && !fabPanel.hidden) { fabPanel.hidden = true; fabBtn.setAttribute("aria-expanded", "false"); } }
  if (fab && fabBtn) {
    fabBtn.addEventListener("click", function (e) { e.stopPropagation(); var o = fabPanel.hidden; fabPanel.hidden = !o; fabBtn.setAttribute("aria-expanded", String(o)); if (o) track("fab_open"); });
    document.addEventListener("click", function (e) { if (!e.target.closest("[data-fab]")) closeFab(); });
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---------- live weather (Open-Meteo, free, no key) ---------- */
  var WX = { 0: "clear", 1: "mostly clear", 2: "partly cloudy", 3: "cloudy", 45: "fog", 48: "fog", 51: "drizzle", 53: "drizzle", 55: "drizzle", 56: "freezing drizzle", 57: "freezing drizzle",
    61: "light rain", 63: "rain", 65: "heavy rain", 66: "freezing rain", 67: "freezing rain", 71: "light snow", 73: "snow", 75: "heavy snow", 77: "snow grains",
    80: "showers", 81: "showers", 82: "heavy showers", 85: "snow showers", 86: "snow showers", 95: "thunderstorm", 96: "thunderstorm", 99: "thunderstorm" };
  var wxEls = $$("[data-wx]");
  if (wxEls.length && window.fetch) {
    var pts = wxEls.map(function (el) { return el.dataset.wx.split(","); });
    var key = "wx:" + pts.map(function (p) { return p.join(","); }).join("|");
    var paint = function (rows) {
      rows.forEach(function (row, i) {
        var el = wxEls[i]; if (!row || !row.current || !el) return;
        var t = Math.round(row.current.temperature_2m), w = WX[row.current.weather_code] || "";
        $$("[data-wx-t]", el).forEach(function (x) { x.textContent = t + "°"; });
        $$("[data-wx-w]", el).forEach(function (x) { x.textContent = w; });
        el.hidden = false;
      });
    };
    var cached = store.get(key);
    if (cached) { try { var c = JSON.parse(cached); if (Date.now() - c.at < 30 * 60 * 1000) { paint(c.rows); cached = "ok"; } else cached = null; } catch (e) { cached = null; } }
    if (cached !== "ok") {
      var url = "https://api.open-meteo.com/v1/forecast?latitude=" + pts.map(function (p) { return p[0]; }).join(",") + "&longitude=" + pts.map(function (p) { return p[1]; }).join(",") + "&current=temperature_2m,weather_code&timezone=Asia%2FKolkata";
      fetch(url).then(function (r) { return r.ok ? r.json() : null; }).then(function (d) {
        if (!d) return; var rows = Array.isArray(d) ? d : [d];
        store.set(key, JSON.stringify({ at: Date.now(), rows: rows })); paint(rows);
      }).catch(function () {});
    }
  }

  /* ---------- live sky over Kangchenjunga (home hero) ----------
     Sunrise and sunset at Tiger Hill (26.99 N, 88.29 E) by the NOAA approximation, in IST. */
  function sunTimes(d, lat, lng) {
    var rad = Math.PI / 180, start = Date.UTC(d.getUTCFullYear(), 0, 0), day = Math.floor((d - start) / 864e5);
    var g = 2 * Math.PI / 365 * (day - 1);
    var eqt = 229.18 * (0.000075 + 0.001868 * Math.cos(g) - 0.032077 * Math.sin(g) - 0.014615 * Math.cos(2 * g) - 0.040849 * Math.sin(2 * g));
    var decl = 0.006918 - 0.399912 * Math.cos(g) + 0.070257 * Math.sin(g) - 0.006758 * Math.cos(2 * g) + 0.000907 * Math.sin(2 * g) - 0.002697 * Math.cos(3 * g) + 0.00148 * Math.sin(3 * g);
    var ha = Math.acos(Math.cos(90.833 * rad) / (Math.cos(lat * rad) * Math.cos(decl)) - Math.tan(lat * rad) * Math.tan(decl)) / rad;
    return { rise: 720 - 4 * (lng + ha) - eqt + 330, set: 720 - 4 * (lng - ha) - eqt + 330 };  // minutes after IST midnight
  }
  var hhmm = function (m) { m = ((Math.round(m) % 1440) + 1440) % 1440; return String(Math.floor(m / 60)).padStart(2, "0") + ":" + String(m % 60).padStart(2, "0"); };
  var SKIES = {
    night: { sky1: "#060A1A", sky2: "#111735", sky3: "#1D2350", glow: "#29305E", snow: "#8F96B8", snowlit: "#8F96B8", stars: 1, lit: 0, r1: "#262A4D", r2: "#191C38", r3: "#10122A", r4: "#090B1C" },
    dawn: { sky1: "#1A1E46", sky2: "#5B4A80", sky3: "#E58C78", glow: "#FFD3A3", snow: "#D9CFE3", snowlit: "#FF9C78", stars: .25, lit: 1, r1: "#3F3B66", r2: "#2A284C", r3: "#1A1934", r4: "#0F0F22" },
    day: { sky1: "#2F6CB0", sky2: "#77A9D8", sky3: "#C9E0EF", glow: "#EAF3F5", snow: "#FFFFFF", snowlit: "#FFFFFF", stars: 0, lit: 0, r1: "#7D93AE", r2: "#58708C", r3: "#3A4F66", r4: "#233243" },
    dusk: { sky1: "#202450", sky2: "#7A4B79", sky3: "#F08A5A", glow: "#FFC57C", snow: "#E7D6DC", snowlit: "#FFA06A", stars: .1, lit: .85, r1: "#45395F", r2: "#2D2546", r3: "#1C1830", r4: "#100E1E" }
  };
  var hero = $("[data-sky]");
  if (hero) {
    var paintSky = function () {
      var now = new Date(), ist = (now.getUTCHours() * 60 + now.getUTCMinutes() + 330) % 1440;
      var s = sunTimes(now, 26.99, 88.29), phase, note;
      if (ist >= s.rise - 60 && ist < s.rise + 35) { phase = "dawn"; note = "Sunrise at Tiger Hill " + hhmm(s.rise) + " · alpenglow on the snow"; }
      else if (ist >= s.rise + 35 && ist < s.set - 50) { phase = "day"; note = "Daylight · sunset " + hhmm(s.set); }
      else if (ist >= s.set - 50 && ist < s.set + 45) { phase = "dusk"; note = "Sunset " + hhmm(s.set) + " · last light on Kangchenjunga"; }
      else { phase = "night"; note = "Night in the hills · Tiger Hill sunrise " + hhmm(s.rise); }
      var sky = SKIES[phase];
      Object.keys(sky).forEach(function (k) { hero.style.setProperty("--" + k, sky[k]); });
      var clock = $("[data-ist]", hero), ph = $("[data-phase]", hero);
      if (clock) clock.textContent = hhmm(ist) + " IST";
      if (ph) ph.textContent = note;
      hero.dataset.phase = phase;
    };
    paintSky(); setInterval(paintSky, 60 * 1000);
    /* the toy train runs along the lowest ridge */
    var trackPath = $("#hc-track", hero), train = $("[data-train]", hero);
    if (trackPath && train && trackPath.getTotalLength) {
      var len = trackPath.getTotalLength(), t0 = performance.now();
      var place = function (f) {
        var p = trackPath.getPointAtLength(f * len), q = trackPath.getPointAtLength(Math.min(len, f * len + 2));
        var a = Math.atan2(q.y - p.y, q.x - p.x) * 180 / Math.PI;
        train.setAttribute("transform", "translate(" + p.x.toFixed(1) + "," + p.y.toFixed(1) + ") rotate(" + a.toFixed(1) + ")");
      };
      if (reduce) place(.42);
      else { var loop = function (t) { place(((t - t0) / 52000) % 1); requestAnimationFrame(loop); }; requestAnimationFrame(loop); }
    }
  }

  /* ---------- altimeter: altitude climbs as you scroll ---------- */
  var body = document.body, aTo = +body.dataset.altTo, aFrom = +(body.dataset.altFrom || 122);
  if (aTo && aTo > aFrom + 300) {
    var marks = [];
    try { marks = JSON.parse(body.dataset.altMarks || "[]"); } catch (e) {}
    var alti = document.createElement("div"); alti.className = "alti"; alti.setAttribute("aria-hidden", "true");
    var scale = document.createElement("div"); scale.className = "alti__scale"; alti.appendChild(scale);
    var span = aTo - aFrom, pos = function (m) { return ((m - aFrom) / span * 100).toFixed(2) + "%"; };
    var step = span > 5000 ? 1000 : span > 2000 ? 500 : span > 900 ? 250 : 100;
    for (var m = Math.ceil(aFrom / step) * step; m <= aTo; m += step) {
      var tk = document.createElement("i"); tk.className = "alti__tick"; tk.style.bottom = pos(m);
      tk.innerHTML = "<span>" + fmt(m) + "</span>"; scale.appendChild(tk);
    }
    marks.forEach(function (mk) {
      if (mk[1] < aFrom || mk[1] > aTo) return;
      var el = document.createElement("i"); el.className = "alti__mark"; el.style.bottom = "calc(" + pos(mk[1]) + " - 5px)";
      el.innerHTML = "<span>" + esc(mk[0]) + "</span>"; scale.appendChild(el);
    });
    var needle = document.createElement("div"); needle.className = "alti__needle";
    needle.innerHTML = '<span class="alti__read">' + fmt(aFrom) + " m</span>"; scale.appendChild(needle);
    var title = document.createElement("span"); title.className = "alti__title"; title.textContent = body.dataset.altLabel || "Altitude"; alti.appendChild(title);
    body.appendChild(alti);
    var bar = document.createElement("div"); bar.className = "alti-bar"; bar.innerHTML = "<span></span>"; body.appendChild(bar);
    var read = $(".alti__read", needle), barIn = $("span", bar);
    var climb = function () {
      var h = doc.scrollHeight - innerHeight, f = h > 0 ? Math.min(1, Math.max(0, scrollY / h)) : 0;
      needle.style.bottom = (f * 100).toFixed(2) + "%";
      read.textContent = fmt(aFrom + f * span) + " m";
      barIn.style.width = (f * 100).toFixed(1) + "%";
    };
    window.addEventListener("scroll", climb, { passive: true }); climb();
  }

  /* ---------- fare tickets: punch one to choose a class ---------- */
  $$("[data-fares]").forEach(function (box) {
    var tickets = $$(".ticket", box), go = $("[data-fare-go]", box.parentNode), bar = $("[data-buybar-fare]");
    tickets.forEach(function (t) {
      t.addEventListener("click", function () {
        tickets.forEach(function (o) { o.setAttribute("aria-pressed", String(o === t)); });
        if (go) {
          var u = new URL(go.href, location.href); u.searchParams.set("tier", t.dataset.tier); go.href = u.pathname + u.search;
          go.textContent = "Ask for the " + t.dataset.name + " plan";
        }
        if (bar) bar.innerHTML = esc(t.dataset.fare) + "<small>" + esc(t.dataset.name) + " · per person</small>";
        track("fare_select", { tier: t.dataset.tier });
      });
    });
  });

  /* journey buy bar: appears once the head has scrolled away */
  var buybar = $("[data-buybar]");
  if (buybar && "IntersectionObserver" in window) {
    buybar.hidden = false;
    var head = $(".phead") || $("main section");
    new IntersectionObserver(function (en) {
      var on = !en[0].isIntersecting;
      buybar.classList.toggle("is-on", on);
      document.body.classList.toggle("has-buybar", on);
    }).observe(head);
  }

  /* planning nudge on long reads: once per visit, after 55% of the page */
  var nudge = $("[data-nudge]");
  if (nudge && !store.get("nudge-closed")) {
    var shown = false;
    window.addEventListener("scroll", function () {
      if (shown) return;
      var h = doc.scrollHeight - innerHeight;
      if (h > 0 && scrollY / h > 0.55) { shown = true; nudge.hidden = false; track("nudge_shown"); }
    }, { passive: true });
    $("[data-nudge-close]", nudge).addEventListener("click", function () { nudge.hidden = true; store.set("nudge-closed", "1"); });
  }

  /* index rows: a photo follows the cursor */
  var peek = $(".toc__peek");
  if (peek && window.matchMedia("(hover: hover)").matches) {
    var pimg = $("img", peek), tx = 0, ty = 0, px = 0, py = 0, raf = null;
    var loopPeek = function () { px += (tx - px) * 0.18; py += (ty - py) * 0.18; peek.style.left = px + "px"; peek.style.top = py + "px"; raf = requestAnimationFrame(loopPeek); };
    $$(".toc__row[data-img]").forEach(function (row) {
      row.addEventListener("mouseenter", function () { if (!row.dataset.img) return; pimg.src = row.dataset.img; peek.classList.add("is-on"); if (!raf) loopPeek(); });
      row.addEventListener("mouseleave", function () { peek.classList.remove("is-on"); });
      row.addEventListener("mousemove", function (e) { tx = e.clientX + 170; ty = e.clientY; });
    });
  }

  /* complete rows: reveal just enough fill cards to finish the last row of each grid */
  function fillGrid(grid) {
    var fillers = $$(":scope > [data-fill-card]", grid);
    if (!fillers.length) return;
    fillers.forEach(function (f) { f.hidden = true; });
    var cols = getComputedStyle(grid).gridTemplateColumns.split(" ").filter(Boolean).length || 1;
    var visible = $$(":scope > *", grid).filter(function (el) { return !el.hasAttribute("data-fill-card") && !el.hidden; }).length;
    if (!visible || cols < 2) return;
    var need = (cols - (visible % cols)) % cols;
    for (var i = 0; i < need && i < fillers.length; i++) fillers[i].hidden = false;
  }
  var fillAll = function () { $$("[data-fill]").forEach(fillGrid); };
  fillAll();
  var fillTimer;
  window.addEventListener("resize", function () { clearTimeout(fillTimer); fillTimer = setTimeout(fillAll, 120); });

  /* list filters; ?length=short or ?budget=under-15k preselects */
  $$("[data-filter-group]").forEach(function (group) {
    var target = $(group.dataset.filterGroup), state = {};
    var apply = function () {
      $$("[data-item]", target).forEach(function (el) {
        var ok = Object.keys(state).every(function (k) { return !state[k] || (" " + (el.dataset[k] || "") + " ").indexOf(" " + state[k] + " ") > -1; });
        el.hidden = !ok;
      });
      $$("[data-section]", target).forEach(function (sec) { sec.hidden = !$$("[data-item]", sec).some(function (el) { return !el.hidden; }); });
      var none = $("[data-empty]", target.parentNode);
      if (none) none.hidden = $$("[data-item]", target).some(function (el) { return !el.hidden; });
      fillAll();
    };
    $$("button[data-key]", group).forEach(function (b) {
      b.addEventListener("click", function () {
        var k = b.dataset.key;
        $$('button[data-key="' + k + '"]', group).forEach(function (o) { o.setAttribute("aria-pressed", String(o === b)); });
        state[k] = b.dataset.value; apply();
      });
    });
    $$("select[data-key]", group).forEach(function (s) { s.addEventListener("change", function () { state[s.dataset.key] = s.value; apply(); }); });
    var params = new URLSearchParams(location.search);
    $$("select[data-key]", group).forEach(function (s) { var v = params.get(s.dataset.key); if (v) { s.value = v; state[s.dataset.key] = v; } });
    $$("button[data-key]", group).forEach(function (b) { if (params.get(b.dataset.key) === b.dataset.value) b.click(); });
    if (Object.keys(state).length) apply();
  });

  /* plan wizard: three steps, validates the visible step before moving on */
  $$("[data-wizard]").forEach(function (form) {
    var steps = $$(".wizard__step", form), labels = $$(".wizard__steps li", form), wbar = $(".wizard__bar span", form), i = 0;
    if ($(".errorlist", form)) i = steps.length - 1;
    var show = function (n) {
      i = Math.max(0, Math.min(steps.length - 1, n));
      steps.forEach(function (s, k) { s.classList.toggle("is-on", k === i); });
      labels.forEach(function (l, k) { l.classList.toggle("is-on", k <= i); });
      wbar.style.width = ((i + 1) / steps.length * 100) + "%";
      track("wizard_step", { step: i + 1 });
    };
    form.setAttribute("data-ready", "");
    $$("[data-next]", form).forEach(function (b) { b.addEventListener("click", function () {
      var bad = $$("input, select, textarea", steps[i]).filter(function (el) { return !el.checkValidity(); });
      if (bad.length) { bad[0].reportValidity(); return; }
      show(i + 1); var f = steps[i].querySelector("input:not([type=hidden]), select, textarea"); if (f) f.focus();
    }); });
    $$("[data-prev]", form).forEach(function (b) { b.addEventListener("click", function () { show(i - 1); }); });
    show(i);
  });

  /* atlas: pins and legend highlight each other */
  $$(".atlas").forEach(function (fig) {
    var pins = $$(".atlas__pin", fig), items = $$(".atlas__legend li", fig);
    var hot = function (n, on) {
      pins.forEach(function (p) { if (p.dataset.n === n) p.classList.toggle("is-hot", on); });
      items.forEach(function (li) { if (li.dataset.n === n) li.classList.toggle("is-hot", on); });
    };
    pins.concat(items).forEach(function (el) {
      el.addEventListener("mouseenter", function () { hot(el.dataset.n, true); });
      el.addEventListener("mouseleave", function () { hot(el.dataset.n, false); });
    });
  });

  /* contents rails: highlight the section in view */
  var tocLinks = $$(".toc-side a");
  if (tocLinks.length && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) tocLinks.forEach(function (a) { a.classList.toggle("is-on", a.getAttribute("href") === "#" + en.target.id); }); });
    }, { rootMargin: "-30% 0px -60% 0px" });
    tocLinks.forEach(function (a) { var t = document.getElementById(a.getAttribute("href").slice(1)); if (t) io.observe(t); });
  }

  /* smooth scroll + reveals */
  if (!reduce && window.Lenis) {
    var lenis = new Lenis({ lerp: 0.11 });
    if (window.gsap && window.ScrollTrigger) {
      lenis.on("scroll", ScrollTrigger.update);
      gsap.ticker.add(function (t) { lenis.raf(t * 1000); });
      gsap.ticker.lagSmoothing(0);
    } else {
      var rafL = function (t) { lenis.raf(t); requestAnimationFrame(rafL); };
      requestAnimationFrame(rafL);
    }
  }
  if (!reduce && window.gsap && window.ScrollTrigger) {
    gsap.registerPlugin(ScrollTrigger);
    $$(".rv").forEach(function (el) { gsap.to(el, { opacity: 1, y: 0, duration: 0.9, ease: "power3.out", scrollTrigger: { trigger: el, start: "top 90%", once: true } }); });
    var title = $(".hero .h-hero, .phead .h-hero, .phead .h-xl");
    if (title) gsap.from(title, { y: 50, opacity: 0, duration: 1.2, ease: "power4.out" });
    $$(".phead .board, .hero .board").forEach(function (b) { gsap.from(b, { y: -40, rotation: -4, opacity: 0, duration: 1, ease: "back.out(1.6)", delay: .15 }); });
    $$(".chit").forEach(function (c, k) { gsap.from(c, { y: 30, rotation: (k % 2 ? 6 : -6), opacity: 0, duration: .8, ease: "back.out(1.4)", scrollTrigger: { trigger: c, start: "top 92%", once: true } }); });
    $$(".hero__ridges [data-ridge]").forEach(function (p, k) { gsap.to(p, { yPercent: (k + 1) * 3, ease: "none", scrollTrigger: { trigger: ".hero", start: "top top", end: "bottom top", scrub: true } }); });
  } else {
    doc.classList.remove("js");
  }
})();
