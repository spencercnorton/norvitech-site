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

  /* ---- The clock -------------------------------------------------------
     Our time, not the visitor's: one uncached read of the public NTP edge's
     own clock, corrected for half the round trip, then ticked locally and
     re-read every ten minutes. If that host cannot be reached we say whose
     clock is on screen rather than quietly showing the wrong one. */
  var clock = document.getElementById("clock");
  if (clock) {
    var face = clock.querySelector("[data-face]");
    var note = clock.querySelector("[data-note]");
    var TIME = "https://time.globalentry.systems/api/public/dashboard/time";
    var offset = 0;
    var ours = false;

    function two(n) { return n < 10 ? "0" + n : "" + n; }

    function tick() {
      var now = new Date(Date.now() + offset);
      face.textContent = two(now.getUTCHours()) + ":" + two(now.getUTCMinutes()) + ":" + two(now.getUTCSeconds());
      face.setAttribute("datetime", now.toISOString());
      note.textContent = ours ? "UTC · our NTP" : "UTC · your device";
      clock.title = ours
        ? "Coordinated Universal Time from time.globalentry.systems, a GPS-disciplined NTP service"
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
