/* aIQon Landingpage. Faehrt den Terminaltext Zeile fuer Zeile hoch.
   Die Inhalte stehen vollstaendig im HTML. Ohne JS ist alles sofort da,
   Suchmaschinen und Screenreader sehen also den kompletten Text. */
(function () {
  "use strict";

  var SPEED = 0.65;         // globaler Multiplikator, kleiner = schneller
                          // 1.0 waeren 18 s, 0.65 sind knapp 12 s
  var TYPE = 26;            // ms pro Zeichen
  var TYPE_JITTER = 24;     // Streuung, damit es nicht nach Metronom klingt
  var AFTER_ENTER = 310;    // Denkpause zwischen Befehl und Ausgabe
  var GAP = 200;            // Pause vor dem naechsten Befehl
  var STEP = 90;            // Standard je Ausgabezeile

  var root = document.documentElement;
  /* Das Countdown-Band wird wie eine Ausgabezeile eingeblendet,
     deshalb steht es mit in der Reihenfolge. */
  var lines = [].slice.call(document.querySelectorAll(".ln, .clock"));
  var skipBtn = document.querySelector("[data-skip]");
  var replayBtn = document.querySelector("[data-replay]");
  var still = window.matchMedia("(prefers-reduced-motion: reduce)");

  var timer = null;
  var run = 0;              // Laufnummer, macht alte Timer wirkungslos
  var pinned = true;        // false, sobald von Hand gescrollt wurde

  /* -------------------------------------------------- Hilfen */

  function num(el, attr, fallback) {
    var v = el.getAttribute(attr);
    return v === null ? fallback : parseInt(v, 10);
  }

  function wait(ms, fn, id) {
    timer = setTimeout(function () {
      if (id === run) fn();
    }, ms * SPEED);
  }

  function follow(el) {
    if (!pinned) return;
    var r = el.getBoundingClientRect();
    var over = r.bottom - (window.innerHeight - 72);
    if (over > 0) window.scrollBy(0, over);
  }

  /* Zeichen fuer Zeichen. Arbeitet auf den Textknoten, die schon im HTML
     stehen, damit die Auszeichnung der Befehlsteile erhalten bleibt. */
  function type(host, id, done) {
    var nodes = [];
    var walk = document.createTreeWalker(host, NodeFilter.SHOW_TEXT, null, false);
    var n;
    while ((n = walk.nextNode())) nodes.push([n, n.nodeValue]);
    nodes.forEach(function (p) { p[0].nodeValue = ""; });

    host.classList.add("typing");
    var i = 0, j = 0;

    (function step() {
      if (id !== run) return;
      if (i >= nodes.length) {
        host.classList.remove("typing");
        return done();
      }
      var node = nodes[i][0], text = nodes[i][1];
      if (j >= text.length) { i++; j = 0; return step(); }
      node.nodeValue += text.charAt(j++);
      follow(host);
      wait(TYPE + Math.random() * TYPE_JITTER, step, id);
    })();
  }

  /* -------------------------------------------------- Ablauf */

  function reveal(el) {
    el.classList.remove("hid");
    follow(el);
  }

  function play(id) {
    var i = 0;

    (function next() {
      if (id !== run) return;
      if (i >= lines.length) { root.classList.add("done"); return; }

      var line = lines[i++];
      reveal(line);

      var typed = line.querySelector("[data-type]");
      if (typed) {
        return type(typed, id, function () {
          wait(AFTER_ENTER, next, id);
        });
      }
      var pause = num(line, "data-pause", 0);
      wait(num(line, "data-step", STEP) + pause + (pause ? GAP : 0), next, id);
    })();
  }

  function finish() {
    run++;
    clearTimeout(timer);
    lines.forEach(function (l) {
      l.classList.remove("hid");
      var t = l.querySelector("[data-type]");
      if (t) t.classList.remove("typing");
    });
    root.classList.add("done");
  }

  function start() {
    run++;
    clearTimeout(timer);
    pinned = true;
    root.classList.remove("done");
    window.scrollTo(0, 0);
    lines.forEach(function (l) { l.classList.add("hid"); });
    if (still.matches) return finish();
    play(run);
  }

  /* -------------------------------------------------- Bedienung */

  document.addEventListener("keydown", function (e) {
    if (root.classList.contains("done")) return;
    if (e.key === "Tab" || e.altKey || e.metaKey || e.ctrlKey) return;
    finish();
  });

  document.addEventListener("pointerdown", function (e) {
    if (root.classList.contains("done")) return;
    if (e.target.closest("a, button")) return;
    finish();
  });

  ["wheel", "touchmove"].forEach(function (ev) {
    window.addEventListener(ev, function () { pinned = false; }, { passive: true });
  });

  if (skipBtn) skipBtn.addEventListener("click", finish);
  if (replayBtn) replayBtn.addEventListener("click", start);

  /* -------------------------------------------------- Countdown
     NASA-Schreibweise: T-DDD:HH:MM:SS vor dem Start, T+ danach. Laeuft
     unabhaengig von der Animation, damit der Wert beim Einblenden stimmt. */

  function pad(n, w) {
    n = String(n);
    while (n.length < w) n = "0" + n;
    return n;
  }

  var clock = document.querySelector("[data-until]");
  if (clock) {
    var target = Date.parse(clock.getAttribute("data-until"));
    var tick = function () {
      var left = target - Date.now();
      var sign = left < 0 ? "+" : "-";
      var s = Math.floor(Math.abs(left) / 1000);
      clock.textContent = "T" + sign
        + pad(Math.floor(s / 86400), 3) + ":"
        + pad(Math.floor(s % 86400 / 3600), 2) + ":"
        + pad(Math.floor(s % 3600 / 60), 2) + ":"
        + pad(s % 60, 2);
    };
    tick();
    setInterval(tick, 1000);
  }

  /* Erst starten, wenn die Schrift steht. Sonst springt das Rasterlogo. */
  var started = false;
  function go() {
    if (started) return;
    started = true;
    start();
  }
  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(go);
    setTimeout(go, 1200);      // Notbremse, falls die Schrift haengt
  } else {
    go();
  }
})();
