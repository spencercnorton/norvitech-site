/* norvitech.com — the only script on this site.
   No third party, no analytics, no cookies, no storage, no build step. Three
   jobs, each of which leaves the page working when this file does not run:
   the spotlight is a scroll-snap carousel with anchor dots on its own, the
   install command is selectable text, and the clock is simply blank. */
(function () {
  "use strict";
  document.documentElement.className += " js";

  /* ---- Spotlight -------------------------------------------------------
     The track scrolls and snaps without us; we add auto-advance, keep the
     dots in step, and get out of the way the moment a visitor takes over. */
  var track = document.querySelector("[data-track]");
  if (track) {
    var slides = track.children;
    var dots = document.querySelectorAll("[data-dot]");
    var index = 0;
    var timer = null;
    var still = window.matchMedia("(prefers-reduced-motion: reduce)");

    function mark() {
      for (var d = 0; d < dots.length; d++) {
        if (d === index) {
          dots[d].setAttribute("aria-current", "true");
        } else {
          dots[d].removeAttribute("aria-current");
        }
      }
    }

    function go(n) {
      index = (n + slides.length) % slides.length;
      track.scrollTo({ left: slides[index].offsetLeft - slides[0].offsetLeft, behavior: "smooth" });
      mark();
    }

    function stop() {
      if (timer) { clearInterval(timer); timer = null; }
    }

    function start() {
      stop();
      // A paused tab still fires intervals; advancing one nobody can see just
      // burns a decode, so the visibility check is the cheap half of this.
      if (still.matches || document.hidden) { return; }
      timer = setInterval(function () { go(index + 1); }, 7000);
    }

    // Manual scrolling is authoritative: follow it rather than fight it.
    var settle = null;
    track.addEventListener("scroll", function () {
      clearTimeout(settle);
      settle = setTimeout(function () {
        var nearest = 0;
        var best = Infinity;
        for (var s = 0; s < slides.length; s++) {
          var d = Math.abs(slides[s].offsetLeft - slides[0].offsetLeft - track.scrollLeft);
          if (d < best) { best = d; nearest = s; }
        }
        index = nearest;
        mark();
      }, 120);
    }, { passive: true });

    for (var i = 0; i < dots.length; i++) {
      (function (n) {
        dots[n].addEventListener("click", function (e) {
          e.preventDefault();
          go(n);
          start();
        });
      })(i);
    }

    track.addEventListener("pointerenter", stop);
    track.addEventListener("pointerleave", start);
    track.addEventListener("focusin", stop);
    track.addEventListener("focusout", start);
    document.addEventListener("visibilitychange", start);
    if (still.addEventListener) { still.addEventListener("change", start); }
    mark();
    start();
  }

  /* ---- Copy the install command ---------------------------------------- */
  var copy = document.querySelector("[data-copy]");
  if (copy) {
    var source = document.getElementById(copy.getAttribute("data-copy"));
    copy.hidden = false;
    var label = copy.textContent;
    var revert = null;
    var select = function () {
      var range = document.createRange();
      range.selectNodeContents(source);
      var selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
    };
    copy.addEventListener("click", function () {
      var text = source.textContent.trim();
      var done = function (ok) {
        copy.textContent = ok ? "Copied" : "Press Ctrl+C";
        clearTimeout(revert);
        revert = setTimeout(function () { copy.textContent = label; }, 2500);
      };
      // Without a secure context or permission there is no clipboard, so
      // select the block and let the visitor finish the job themselves.
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(function () { done(true); }, function () { select(); done(false); });
      } else {
        select();
        done(false);
      }
    });
  }

  /* ---- About: the career system ------------------------------------------
     One dataset, four linked views: the timeline list (which is the chart's
     table view), the Gantt, the map and the skill / organisation keys. One
     state object; every control changes it and calls paint(), and paint() is
     the only code that touches the linked classes, so no view can drift out
     of step with another. Without this block every view is still plain
     markup: the list is native <details>, and bars, cities and stat tiles
     are links to their entries. */
  // Its own function scope. site.js is one function, and `var` is function-scoped: this
  // module's `var note` and the clock's `var note` below were one variable, so the focus
  // line (with its Clear button) was written into the header clock's link. Sealed off now.
  (function () {
  var career = document.querySelector("[data-career]");
  var openSheet = function (id) {
    // No <dialog>: fall back to the entry itself, opened in place.
    var d = document.getElementById("e-" + id);
    if (d) { d.open = true; d.scrollIntoView({ block: "center" }); }
  };
  if (career) {
    var calm = window.matchMedia("(prefers-reduced-motion: reduce)");
    var wide = window.matchMedia("(min-width: 1280px)");
    var list = career.querySelector(".tl-list");
    var items = [].slice.call(career.querySelectorAll(".tl-item"));
    var byId = {};
    items.forEach(function (el) { byId[el.dataset.id] = el; });
    var marks = [].slice.call(career.querySelectorAll("[data-bar]"));
    var cities = [].slice.call(career.querySelectorAll(".m-city"));
    var keys = [].slice.call(career.querySelectorAll("[data-key]"));
    var fbtns = [].slice.call(career.querySelectorAll(".tl-f"));
    var slider = career.querySelector(".tl-slider");
    var noteEl = career.querySelector("[data-focus]");
    var gantt = career.querySelector("[data-gantt]");
    var tip = document.querySelector("[data-tip]");
    var state = { kind: "all", key: null, hot: null };
    var orgName = {};
    keys.forEach(function (k) {
      if (k.dataset.org) { orgName[k.dataset.org] = textOf(k); }
    });

    function textOf(el) {   // a key's own label, without its count
      var t = "";
      [].forEach.call(el.childNodes, function (n) { if (n.nodeType === 3) { t += n.nodeValue; } });
      return t.trim();
    }
    function has(el, key) {
      var i = key.indexOf(":"), kind = key.slice(0, i), v = key.slice(i + 1);
      if (kind === "skill") { return (" " + el.dataset.skills + " ").indexOf(" " + v + " ") > -1; }
      return el.dataset[kind] === v;             // org or city
    }
    function shown(el) { return !el.classList.contains("out"); }
    function lit(el) { return !state.key || has(el, state.key); }
    function title(el) { return el.querySelector(".tl-head strong").textContent; }

    function paint() {
      items.forEach(function (el) {
        el.classList.toggle("dim", !lit(el));
        el.classList.toggle("hot", state.hot === el.dataset.id);
      });
      marks.forEach(function (m) {
        var el = byId[m.dataset.bar];
        m.classList.toggle("off", !shown(el));
        m.classList.toggle("dim", shown(el) && !lit(el));
        m.classList.toggle("hot", state.hot === el.dataset.id);
        m.tabIndex = shown(el) ? 0 : -1;
      });
      cities.forEach(function (c) {
        var mine = items.filter(function (el) { return el.dataset.city === c.dataset.city && shown(el); });
        c.classList.toggle("dim", !mine.some(lit));
        c.classList.toggle("hot", !!state.hot && byId[state.hot].dataset.city === c.dataset.city);
        c.setAttribute("aria-pressed", String(state.key === "city:" + c.dataset.city));
      });
      keys.forEach(function (k) { k.setAttribute("aria-pressed", String(k.dataset.key === state.key)); });
      if (!noteEl) { return; }
      noteEl.textContent = "";
      if (!state.key) { return; }
      var hits = items.filter(function (el) { return shown(el) && lit(el); });
      var from = 9999, to = 0, live = false;
      hits.forEach(function (el) {
        var p = el.dataset.span.split(" – ");
        from = Math.min(from, Number(p[0]));
        if (p[1] === "now") { live = true; } else { to = Math.max(to, Number(p[1] || p[0])); }
      });
      var src = keys.filter(function (k) { return k.dataset.key === state.key; })[0];
      var city = cities.filter(function (c) { return state.key === "city:" + c.dataset.city; })[0];
      var b = document.createElement("b");
      b.textContent = src ? textOf(src) : city.querySelector(".m-name").textContent;
      noteEl.appendChild(b);
      noteEl.appendChild(document.createTextNode(hits.length
        ? " — " + hits.length + (hits.length === 1 ? " entry, " : " entries, ") + from + (live ? " – now" : (to > from ? " – " + to : ""))
        : " — nothing in this view"));
      var clear = document.createElement("button");
      clear.type = "button";
      clear.textContent = "Clear";
      clear.addEventListener("click", function () { setKey(null); });
      noteEl.appendChild(clear);
    }
    function setKey(k) { state.key = state.key === k ? null : k; paint(); }

    // Park the pill under the active button. Width and position come from the
    // button itself, so the control stays correct at any font size or locale.
    function park(btn) {
      // Measure both in viewport space and subtract the control's own border,
      // because the slider's left:0 is its padding edge.
      var box = slider.parentNode;
      var pr = box.getBoundingClientRect();
      var br = btn.getBoundingClientRect();
      slider.style.width = br.width + "px";
      slider.style.transform = "translateX(" + (br.left - pr.left - box.clientLeft) + "px)";
    }

    // FLIP: measure, change, measure, then play the difference. Without it the
    // surviving entries jump to their new rows the instant one is hidden.
    function setKind(kind) {
      state.kind = kind;
      var first = {};
      items.forEach(function (el) { if (shown(el)) { first[el.dataset.i] = el.getBoundingClientRect().top; } });
      items.forEach(function (el) { el.classList.toggle("out", kind !== "all" && el.dataset.kind !== kind); });
      paint();
      tracked = null;
      frame();
      if (calm.matches) { return; }
      items.forEach(function (el) {
        if (!shown(el)) { return; }
        var last = el.getBoundingClientRect().top, was = first[el.dataset.i];
        if (was === undefined) {
          // Newly shown: fade it in where it now sits rather than sliding it
          // from a position it never occupied.
          el.animate([{ opacity: 0, transform: "translateY(10px)" }, { opacity: 1, transform: "none" }],
            { duration: 320, easing: "cubic-bezier(.22,1,.36,1)" });
        } else if (was !== last) {
          el.animate([{ transform: "translateY(" + (was - last) + "px)" }, { transform: "none" }],
            { duration: 420, easing: "cubic-bezier(.22,1,.36,1)" });
        }
      });
    }
    fbtns.forEach(function (btn) {
      btn.addEventListener("click", function () {
        fbtns.forEach(function (b) { b.setAttribute("aria-pressed", String(b === btn)); });
        park(btn);
        setKind(btn.dataset.filter);
      });
    });
    park(fbtns[0]);
    keys.forEach(function (k) {
      k.disabled = false;
      k.addEventListener("click", function () { setKey(k.dataset.key); });
    });
    cities.forEach(function (c) {
      c.setAttribute("role", "button");
      c.addEventListener("click", function (e) { e.preventDefault(); setKey("city:" + c.dataset.city); });
    });

    // Linked hover: pointing at a bar lights its entry and its city, and the
    // other way round. Focus does the same for the keyboard.
    function hotFrom(t) {
      var m = t.closest && t.closest("[data-bar]");
      if (m) { return m.dataset.bar; }
      var li = t.closest && t.closest(".tl-item");
      return li && shown(li) ? li.dataset.id : null;
    }
    function heat(id) { if (id !== state.hot) { state.hot = id; paint(); } }
    career.addEventListener("pointerover", function (e) { heat(hotFrom(e.target)); });
    career.addEventListener("pointerleave", function () { heat(null); });
    career.addEventListener("focusin", function (e) { heat(hotFrom(e.target)); });

    /* ---- The Gantt ------------------------------------------------------ */
    function span(m) {
      // The live bar's duration is counted at view time, inclusively, the way
      // the record counts it ("March 2026 - Present (7 months)").
      if (!m.dataset.start) { return m.dataset.dur; }
      var p = m.dataset.start.split("-"), d = new Date();
      var n = d.getFullYear() * 12 + d.getMonth() - (Number(p[0]) * 12 + Number(p[1]) - 1) + 1;
      return n < 24 ? n + " months" : Math.floor(n / 12) + " yr " + (n % 12) + " mo";
    }
    function tipShow(m) {
      if (!tip) { return; }
      tip.textContent = "";
      tip.setAttribute("data-org", m.dataset.org);
      var role = document.createElement("span"), when = document.createElement("span"), org = document.createElement("span");
      role.className = "t-role"; when.className = "t-when"; org.className = "t-org";
      role.textContent = m.dataset.role;
      var dur = span(m);
      when.textContent = m.dataset.when + (dur ? " · " + dur : "");
      org.textContent = orgName[m.dataset.org] || "";
      tip.appendChild(role); tip.appendChild(when); tip.appendChild(org);
      // Whatever quote is showing under the entry's card, the bar says too.
      var say = byId[m.dataset.bar].querySelector(".tv-say:not([hidden])");
      if (say) {
        var n = byId[m.dataset.bar].querySelectorAll(".tv-say").length;
        var q = document.createElement("span"), by = document.createElement("span");
        q.className = "t-q"; by.className = "t-by";
        q.textContent = "“" + say.querySelector("p").textContent + "”";
        by.textContent = "— " + say.querySelector("strong").textContent + (n > 1 ? " and " + (n - 1) + " more" : "");
        tip.appendChild(q); tip.appendChild(by);
      }
      tip.hidden = false;
      var r = m.getBoundingClientRect(), w = tip.offsetWidth, h = tip.offsetHeight;
      var x = Math.min(Math.max(8, r.left + r.width / 2 - w / 2), window.innerWidth - w - 8);
      var y = r.top - h - 10;
      if (y < 8) { y = r.bottom + 10; }
      tip.style.left = x + "px";
      tip.style.top = y + "px";
      requestAnimationFrame(function () { tip.classList.add("on"); });
    }
    function tipHide() { if (tip) { tip.classList.remove("on"); tip.hidden = true; } }
    marks.forEach(function (m) {
      m.addEventListener("pointerenter", function () { tipShow(m); });
      m.addEventListener("pointerleave", tipHide);
      m.addEventListener("focus", function () { tipShow(m); });
      m.addEventListener("blur", tipHide);
      m.addEventListener("click", function (e) { e.preventDefault(); tipHide(); openSheet(m.dataset.bar, m); });
    });
    var gs = career.querySelector(".g-scroll");
    if (gs) { gs.addEventListener("scroll", tipHide, { passive: true }); }
    if (gantt) {
      if (window.IntersectionObserver && !calm.matches) {
        // Bars draw left to right, in the order they happened.
        marks.forEach(function (m) { m.style.transitionDelay = Math.round(parseFloat(m.style.getPropertyValue("--x")) * 9) + "ms"; });
        new IntersectionObserver(function (en, o) {
          if (!en[0].isIntersecting) { return; }
          o.disconnect();
          gantt.classList.add("in");
          // Clear the stagger once drawn, or it would delay every later dim/highlight.
          setTimeout(function () { marks.forEach(function (m) { m.style.transitionDelay = ""; }); }, 1900);
        }, { threshold: 0.25 }).observe(gantt);
      } else {
        gantt.classList.add("in");
      }
    }

    /* ---- What they said ----------------------------------------------------
       A role with several recommendations shows one quote at a time under its
       card; pointing at, focusing or tapping a face shows theirs, and "Read all"
       then opens the sheet at that person. Without this block the first quote
       stands on its own and every recommendation is in the entry's detail. */
    [].slice.call(list.querySelectorAll(".tl-voice")).forEach(function (v) {
      var faces = [].slice.call(v.querySelectorAll("button.tv-av"));
      var says = [].slice.call(v.querySelectorAll(".tv-say"));
      var more = v.querySelector(".tv-more");
      function show(rec) {
        if (more.dataset.rec === rec) { return; }
        says.forEach(function (s) { s.hidden = s.dataset.rec !== rec; });
        faces.forEach(function (f) { f.setAttribute("aria-pressed", String(f.dataset.rec === rec)); });
        more.dataset.rec = rec;
      }
      faces.forEach(function (f) {
        f.disabled = false;
        ["pointerenter", "focus", "click"].forEach(function (ev) {
          f.addEventListener(ev, function () { show(f.dataset.rec); });
        });
      });
    });

    /* ---- The list: reveal, spine, and the rail that follows you ---------- */
    var rail = career.querySelector("[data-rail]");
    var nowBox = career.querySelector("[data-now]");
    var tracked = null;
    function track() {
      var vis = items.filter(shown);
      if (!vis.length) { return; }
      var mid = window.innerHeight * 0.42, pick = vis[0], seen = {};
      vis.forEach(function (el) {
        if (el.getBoundingClientRect().top < mid) { pick = el; seen[el.dataset.city] = 1; }
      });
      seen[pick.dataset.city] = 1;
      cities.forEach(function (c) {
        // Narrow screens show the map above the list, not beside it: every
        // place is simply lit there, because nothing tracks what you can't see.
        c.classList.toggle("seen", !wide.matches || !!seen[c.dataset.city]);
        c.classList.toggle("now", wide.matches && c.dataset.city === pick.dataset.city);
      });
      if (pick === tracked || !nowBox || !wide.matches) { return; }
      tracked = pick;
      nowBox.setAttribute("data-org", pick.dataset.org);
      nowBox.querySelector("[data-now-yr]").textContent = pick.dataset.span;
      nowBox.querySelector("[data-now-role]").textContent = title(pick);
      nowBox.querySelector("[data-now-org]").textContent = pick.querySelector(".tl-org").textContent
        + " · " + pick.querySelector(".tl-when").textContent.split(" · ")[0];
      if (!calm.matches) { nowBox.classList.remove("swap"); void nowBox.offsetWidth; nowBox.classList.add("swap"); }
    }
    function fill() {
      // The spine fills to the viewport's midpoint, so the thread reads as
      // "drawn so far"; a CSS transition smooths the steps.
      var r = list.getBoundingClientRect();
      var px = Math.max(0, Math.min(r.height - 12, window.innerHeight * 0.5 - r.top - 6));
      list.style.setProperty("--tl-fill", px + "px");
    }
    var ticking = false;
    function frame() { ticking = false; fill(); track(); }
    window.addEventListener("scroll", function () {
      tipHide();
      if (!ticking) { ticking = true; requestAnimationFrame(frame); }
    }, { passive: true });
    window.addEventListener("resize", function () {
      var on = career.querySelector('.tl-f[aria-pressed="true"]');
      if (on) { park(on); }
      tracked = null;
      frame();
    });
    frame();

    if (window.IntersectionObserver && !calm.matches) {
      list.classList.add("tl-ready");
      var seenIO = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) { return; }
          var el = entry.target;
          setTimeout(function () { el.classList.add("in"); }, Math.min(el.dataset.i % 6, 5) * 70);
          seenIO.unobserve(el);
        });
      }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
      items.forEach(function (el) { seenIO.observe(el); });
      // Insurance: reveal everything only if the observer produced nothing at
      // all; a timer alone would kill the entrance for anyone who reads slowly.
      setTimeout(function () {
        if (!list.querySelector(".tl-item.in")) { items.forEach(function (el) { el.classList.add("in"); }); }
      }, 2500);
    }

    // A glow that follows the pointer across a card.
    if (window.matchMedia("(hover: hover) and (pointer: fine)").matches) {
      list.addEventListener("pointermove", function (e) {
        var c = e.target.closest && e.target.closest(".tl-card");
        if (!c) { return; }
        var r = c.getBoundingClientRect();
        c.style.setProperty("--mx", (e.clientX - r.left) + "px");
        c.style.setProperty("--my", (e.clientY - r.top) + "px");
      }, { passive: true });
    }

    /* ---- The detail sheet ------------------------------------------------
       A native <dialog> brings focus handling, Escape and the backdrop for
       free. The sheet browses the entries in view with the arrow keys, and
       its URL is shareable: /about/#e-sba opens that entry. */
    var sheet = document.querySelector("[data-sheet]");
    if (sheet && typeof sheet.showModal === "function") {
      var body = sheet.querySelector("[data-sheet-body]");
      var steps = [].slice.call(sheet.querySelectorAll("[data-step]"));
      var pos = sheet.querySelector("[data-pos]");
      var opener = null, first = null, current = null, before = "";
      var fillSheet = function (id, dir) {
        var item = byId[id], card = item.querySelector(".tl-card"), sum = card.querySelector("summary");
        current = id;
        sheet.setAttribute("data-org", item.dataset.org);
        body.textContent = "";
        var head = document.createElement("div"), txt = document.createElement("div");
        head.className = "sheet-head";
        head.appendChild(sum.querySelector(".tl-mark").cloneNode(true));
        var h3 = document.createElement("h3"), org = document.createElement("div"), when = document.createElement("div");
        h3.id = "sheet-title"; h3.textContent = title(item);
        org.className = "tl-org"; org.textContent = sum.querySelector(".tl-org").textContent;
        when.className = "tl-when"; when.textContent = sum.querySelector(".tl-when").textContent;
        txt.appendChild(h3); txt.appendChild(org); txt.appendChild(when);
        head.appendChild(txt);
        body.appendChild(head);
        body.appendChild(card.querySelector(".tl-body").cloneNode(true));
        var seq = items.filter(shown), i = seq.indexOf(item);
        steps.forEach(function (b) {
          var n = seq[i + Number(b.dataset.step)];
          b.classList.toggle("none", !n);
          b.tabIndex = n ? 0 : -1;
          b.dataset.to = n ? n.dataset.id : "";
          b.querySelector("[data-lbl]").textContent = n ? title(n) : "";
          b.setAttribute("aria-label", n ? (Number(b.dataset.step) < 0 ? "Previous: " : "Next: ") + title(n) : "");
        });
        pos.textContent = (i + 1) + " / " + seq.length;
        body.scrollTop = 0;
        if (dir && !calm.matches) {
          body.classList.remove("step-l", "step-r");
          void body.offsetWidth;
          body.classList.add(dir < 0 ? "step-l" : "step-r");
        }
        if (history.replaceState) { history.replaceState(null, "", "#e-" + id); }
      };
      openSheet = function (id, from, rec) {
        if (!byId[id]) { return; }
        opener = from || null;
        first = id;
        // Remember the address the page had, so closing puts it back (#career stays #career).
        if (!sheet.open) { before = /^#e-/.test(location.hash) ? "" : location.hash; }
        fillSheet(id, 0);
        if (!sheet.open) { sheet.showModal(); }
        // Straight to the person whose quote you were reading. Layout offsets, not
        // client rects: the sheet is still scaling in, and a rect measured mid-scale
        // lands the scroll short by the scale factor.
        var f = rec && body.querySelector('.rec[data-rec="' + rec + '"]');
        if (f) {
          body.scrollTop = f.offsetTop - body.offsetTop - 14;
          f.classList.add("lit");
        }
      };
      var step = function (d) {
        var b = steps.filter(function (x) { return Number(x.dataset.step) === d; })[0];
        if (b && b.dataset.to) { fillSheet(b.dataset.to, d); }
      };
      steps.forEach(function (b) { b.addEventListener("click", function () { step(Number(b.dataset.step)); }); });
      sheet.addEventListener("keydown", function (e) {
        if (e.key === "ArrowLeft") { e.preventDefault(); step(-1); }
        if (e.key === "ArrowRight") { e.preventDefault(); step(1); }
      });
      list.addEventListener("click", function (e) {
        var sum = e.target.closest ? e.target.closest(".tl-card>summary") : null;
        if (!sum) { return; }
        e.preventDefault();               // keep the <details> shut; the sheet is the surface
        openSheet(sum.closest(".tl-item").dataset.id, sum);
      });
      sheet.addEventListener("click", function (e) {
        // Clicking the backdrop lands on the dialog itself, never on its content.
        if (e.target === sheet || (e.target.closest && e.target.closest("[data-sheet-close]"))) { sheet.close(); }
      });
      sheet.addEventListener("close", function () {
        if (history.replaceState) { history.replaceState(null, "", location.pathname + location.search + before); }
        // Back to where you started - or, if you browsed away, to where you ended.
        var to = current === first && opener ? opener : byId[current].querySelector("summary");
        if (to) { to.focus(); }
        opener = null;
      });
      var fromHash = function () {
        var m = /^#e-([a-z0-9]+)$/.exec(location.hash);
        if (m && byId[m[1]]) { openSheet(m[1], null); }
      };
      window.addEventListener("hashchange", fromHash);
      fromHash();
    }

    /* ---- By the numbers --------------------------------------------------- */
    [].slice.call(document.querySelectorAll("[data-open]")).forEach(function (a) {
      a.addEventListener("click", function (e) { e.preventDefault(); openSheet(a.dataset.open, a, a.dataset.rec); });
    });
    var counters = [].slice.call(document.querySelectorAll("[data-count]"));
    var suffix = function (el) { return el.dataset.suffix || ""; };
    if (counters.length && window.IntersectionObserver && !calm.matches) {
      // The text node always holds the true value; the count is drawn by a
      // pseudo-element over it (data-show). It arms only in a band just below
      // the viewport, so a zero is never on screen, and a number already in
      // view at load keeps its value. Counting to 1 is not a flourish.
      var arm = new IntersectionObserver(function (en) {
        en.forEach(function (x) {
          var el = x.target;
          if (el.dataset.done || el.dataset.running) { return; }
          if (x.isIntersecting) { el.dataset.show = "0" + suffix(el); } else { el.removeAttribute("data-show"); }
        });
      }, { rootMargin: "0px 0px 160px 0px" });
      var go = new IntersectionObserver(function (en) {
        en.forEach(function (x) {
          if (!x.isIntersecting) { return; }
          var el = x.target, to = Number(el.dataset.count), t0 = null;
          go.unobserve(el); arm.unobserve(el);
          el.dataset.running = "1";
          var tick = function (t) {
            if (t0 === null) { t0 = t; }
            var p = Math.min(1, (t - t0) / 1100);
            el.dataset.show = Math.round(to * (1 - Math.pow(1 - p, 4))).toLocaleString("en-US") + suffix(el);
            if (p < 1) { requestAnimationFrame(tick); return; }
            el.removeAttribute("data-show"); el.removeAttribute("data-running"); el.dataset.done = "1";
          };
          requestAnimationFrame(tick);
        });
      }, { threshold: 0.6 });
      counters.forEach(function (el) {
        if (Number(el.dataset.count) < 10 || el.getBoundingClientRect().top < window.innerHeight) { return; }
        arm.observe(el);
        go.observe(el);
      });
    }

    /* ---- Print: the page is its own CV ----------------------------------- */
    var reopened = [];
    window.addEventListener("beforeprint", function () {
      items.forEach(function (el) { var d = el.querySelector("details"); if (!d.open) { d.open = true; reopened.push(d); } });
      counters.forEach(function (el) { el.removeAttribute("data-show"); });
    });
    window.addEventListener("afterprint", function () { reopened.forEach(function (d) { d.open = false; }); reopened = []; });
    var pb = document.querySelector("[data-print]");
    if (pb) { pb.hidden = false; pb.addEventListener("click", function () { window.print(); }); }

    paint();
  }
  })();

  /* ---- The clock -------------------------------------------------------
     The visitor's own wall clock, but disciplined by ours: one uncached read
     of the public NTP edge's clock, corrected for half the round trip, then
     ticked locally and re-read every ten minutes. Rendered in the visitor's
     locale and zone; the tooltip says whose clock is actually driving it. */
  var clock = document.getElementById("clock");
  if (clock) {
    var face = clock.querySelector("[data-face]");
    var note = clock.querySelector("[data-note]");
    var TIME = "https://time.globalentry.systems/api/public/dashboard/time";
    var offset = 0;
    var ours = false;

    // The visitor's zone, named the short way ("MDT", "GMT+1"). Fixed for the
    // life of the page: a DST change mid-visit survives until the next reload.
    var zone = "";
    try {
      var parts = new Intl.DateTimeFormat(undefined, { timeZoneName: "short" }).formatToParts(new Date());
      for (var i = 0; i < parts.length; i++) {
        if (parts[i].type === "timeZoneName") { zone = parts[i].value; }
      }
    } catch (e) { /* no Intl: the face alone still reads correctly */ }

    function tick() {
      var now = new Date(Date.now() + offset);
      face.textContent = now.toLocaleTimeString();
      face.setAttribute("datetime", now.toISOString());
      note.textContent = zone;
      clock.title = ours
        ? "Your local time, set by time.globalentry.systems, a GPS-disciplined NTP service"
        : "time.globalentry.systems could not be reached; this is your own device clock";
    }

    function sync() {
      var sent = Date.now();
      fetch(TIME, { cache: "no-store", referrerPolicy: "no-referrer", mode: "cors" })
        .then(function (r) { return r.ok ? r.json() : Promise.reject(r.status); })
        .then(function (body) {
          var back = Date.now();
          // Assume a symmetric round trip — the honest error bar is half of it,
          // which at any sane latency is well under the second we display.
          offset = body.unix_ms + (back - sent) / 2 - back;
          ours = true;
          tick();
        })
        .catch(function () { ours = false; tick(); });
    }

    tick();
    sync();
    setInterval(tick, 1000);
    setInterval(sync, 600000);
    document.addEventListener("visibilitychange", function () { if (!document.hidden) { sync(); } });
  }
})();
