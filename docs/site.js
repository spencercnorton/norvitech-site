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

  /* ---- About: the career timeline --------------------------------------
     Three behaviours, all optional. Without this block the list is a plain
     <ol> of native <details>: every entry is visible, every detail opens,
     and the only thing missing is the filtering. */
  var tl = document.querySelector("[data-timeline]");
  if (tl) {
    var list = tl.querySelector(".tl-list");
    var items = [].slice.call(tl.querySelectorAll(".tl-item"));
    var fbtns = [].slice.call(tl.querySelectorAll(".tl-f"));
    var slider = tl.querySelector(".tl-slider");
    var calm = window.matchMedia("(prefers-reduced-motion: reduce)");

    // Park the pill under the active button. Width and position come from the
    // button itself, so the control stays correct at any font size or locale.
    function park(btn) {
      // Measure both in viewport space and subtract the control's own border,
      // because the slider's left:0 is its padding edge. offsetLeft alone is
      // relative to the offsetParent and double-counts once the control moves.
      var box = slider.parentNode;
      var pr = box.getBoundingClientRect();
      var br = btn.getBoundingClientRect();
      slider.style.width = br.width + "px";
      slider.style.transform = "translateX(" + (br.left - pr.left - box.clientLeft) + "px)";
    }

    // FLIP: measure, change, measure, then play the difference. Without it the
    // surviving entries jump to their new rows the instant one is hidden.
    function show(kind) {
      var first = {};
      items.forEach(function (el) {
        if (!el.classList.contains("out")) { first[el.dataset.i] = el.getBoundingClientRect().top; }
      });
      items.forEach(function (el) {
        el.classList.toggle("out", kind !== "all" && el.dataset.kind !== kind);
      });
      if (calm.matches) { return; }
      items.forEach(function (el) {
        if (el.classList.contains("out")) { return; }
        var last = el.getBoundingClientRect().top;
        var was = first[el.dataset.i];
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
        show(btn.dataset.filter);
      });
    });
    park(fbtns[0]);
    window.addEventListener("resize", function () {
      var on = tl.querySelector('.tl-f[aria-pressed="true"]');
      if (on) { park(on); }
    });

    // Reveal on scroll. The class goes on only now, so a visitor without
    // IntersectionObserver is never left with an invisible list.
    if (window.IntersectionObserver && !calm.matches) {
      list.classList.add("tl-ready");
      var seen = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) { return; }
          var el = entry.target;
          // Stagger by position in the viewport batch, not by index, so a
          // deep link partway down the page does not wait on rows above it.
          setTimeout(function () { el.classList.add("in"); }, Math.min(entry.target.dataset.i % 6, 5) * 55);
          seen.unobserve(el);
        });
      }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
      items.forEach(function (el) { seen.observe(el); });
      // Insurance: a CV that never becomes visible is far worse than one that
      // skips its entrance. If anything stops the observer, show everything.
      setTimeout(function () {
        items.forEach(function (el) { el.classList.add("in"); });
      }, 2500);
    }

    /* ---- The detail sheet ---------------------------------------------
       A native <dialog> gets focus handling, Escape and the backdrop for
       free. If the browser has no dialog support we leave the <details>
       alone and it simply expands in place, which is the fallback anyway. */
    var sheet = document.querySelector("[data-sheet]");
    if (sheet && typeof sheet.showModal === "function") {
      var body = sheet.querySelector("[data-sheet-body]");
      var opener = null;
      tl.addEventListener("click", function (e) {
        var sum = e.target.closest ? e.target.closest(".tl-card>summary") : null;
        if (!sum) { return; }
        e.preventDefault();               // keep the <details> shut; the sheet is the surface
        var card = sum.parentNode;
        var item = card.closest(".tl-item");
        var head = sum.querySelector(".tl-head");
        body.innerHTML = "";
        var h = document.createElement("div");
        h.className = "sheet-head";
        h.appendChild(sum.querySelector(".tl-mark").cloneNode(true));
        var t = document.createElement("div");
        t.innerHTML = "<h3>" + head.querySelector("strong").innerHTML + "</h3>"
          + '<div class="tl-org">' + head.querySelector(".tl-org").innerHTML + "</div>"
          + '<div class="tl-when">' + head.querySelector(".tl-when").innerHTML + "</div>";
        h.appendChild(t);
        body.appendChild(h);
        body.appendChild(card.querySelector(".tl-body").cloneNode(true));
        sheet.style.setProperty("--accent", item.style.getPropertyValue("--accent"));
        opener = sum;
        sheet.showModal();
      });
      sheet.addEventListener("click", function (e) {
        // Clicking the backdrop lands on the dialog itself, never on its content.
        if (e.target === sheet || (e.target.closest && e.target.closest("[data-sheet-close]"))) {
          sheet.close();
        }
      });
      sheet.addEventListener("close", function () {
        if (opener) { opener.focus(); opener = null; }
      });
    }
  }

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
