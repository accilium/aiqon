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
  var edgeCheck = null;     // wird unten gesetzt, sobald .screen bekannt ist
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
    if (typeof edgeCheck === "function") edgeCheck();
  }

  function play(id) {
    var i = 0;

    (function next() {
      if (id !== run) return;
      if (i >= lines.length) { root.classList.add("done"); armShell(); focusShell(); return; }

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
    armShell();
  }

  function start() {
    run++;
    clearTimeout(timer);
    pinned = true;
    root.classList.remove("done");
    window.scrollTo(0, 0);
    lines.forEach(function (l) { l.classList.add("hid"); });
    if (buf) [].slice.call(buf.querySelectorAll(".ln")).forEach(function (l) {
      if (lines.indexOf(l) < 0) l.parentNode.removeChild(l);
    });
    if (live) live.textContent = "";
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
    if (e.target.closest("a, button")) return;
    if (root.classList.contains("done")) {
      if (e.target.closest(".term")) setTimeout(function () { focusShell(true); }, 0);
      return;
    }
    finish();
  });
  /* Eine Taste nach dem Hochfahren landet im Prompt, auch ohne Klick. */
  document.addEventListener("keydown", function (e) {
    if (!root.classList.contains("done") || !live) return;
    if (document.activeElement === live) return;
    if (e.altKey || e.metaKey || e.ctrlKey || e.key.length !== 1) return;
    live.focus({ preventScroll: true }); place();
  });

  ["wheel", "touchmove"].forEach(function (ev) {
    window.addEventListener(ev, function () { pinned = false; }, { passive: true });
  });

  if (skipBtn) skipBtn.addEventListener("click", finish);
  if (replayBtn) replayBtn.addEventListener("click", start);


  /* -------------------------------------------------- Shell
     Nach dem Hochfahren nimmt der letzte Prompt Eingaben an. Die Befehle
     sind die, die die Seite beim Hochfahren selbst benutzt hat; ihre
     Ausgabe wird aus dem Puffer kopiert, nichts steht doppelt im HTML. */

  var buf = document.querySelector(".buf");
  var endLine = document.querySelector(".ln.end");
  var live = null;
  var history = [], hIdx = 0;

  function esc(t) {
    return t.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  function out(html, cls) {
    var d = document.createElement("div");
    d.className = "ln" + (cls ? " " + cls : "");
    d.innerHTML = html;
    buf.insertBefore(d, endLine);
    return d;
  }

  function outText(text, cls) {
    return out('<span class="' + (cls || "p") + '">' + esc(text) + "</span>");
  }

  /* Ausgabe eines Blocks noch einmal: alle Zeilen nach seinem Befehl bis
     zum naechsten Befehl, ohne die Leerzeile am Blockende. */
  function block(name) {
    var head = buf.querySelector('.cmd[data-block="' + name + '"]');
    if (!head) return false;
    var rows = [], el = head.nextElementSibling;
    while (el && lines.indexOf(el) >= 0 && !el.classList.contains("cmd")
           && !el.classList.contains("end")) {
      rows.push(el);
      el = el.nextElementSibling;
    }
    while (rows.length && !rows[rows.length - 1].textContent.trim()
           && !rows[rows.length - 1].querySelector("img")) rows.pop();
    rows.forEach(function (r) {
      var c = r.cloneNode(true);
      c.classList.remove("hid");
      c.removeAttribute("data-step"); c.removeAttribute("data-pause");
      buf.insertBefore(c, endLine);
    });
    return true;
  }

  function echoCmd(text) {
    var parts = text.split(" "), head = [], tail = [];
    parts.forEach(function (w) {
      if (tail.length || w.charAt(0) === "-") tail.push(w); else head.push(w);
    });
    var html = '<span class="ps">aiqon ~ % </span><span class="cm">'
      + '<span class="c1">' + esc(head.join(" ")) + "</span>";
    if (tail.length) html += '<span class="c2"> ' + esc(tail.join(" ")) + "</span>";
    out(html + "</span>", "cmd");
  }

  /* Ein Wort reicht: facts, programm, rsvp. Die lange Form mit
     aiq show -- geht weiter, sie steht ja oben auf der Seite. */
  var SHOW = {
    "facts": "facts", "fakten": "facts", "hard facts": "facts",
    "what-to-expect": "expect", "expect": "expect", "format": "expect",
    "programm": "programm", "program": "programm", "agenda": "programm",
    "programm detail": "detail", "programm --detail": "detail", "detail": "detail",
    "details": "detail", "use-cases": "detail", "use cases": "detail", "cases": "detail",
    "speaker": "detail", "rsvp": "rsvp", "zugang": "rsvp", "deadline": "rsvp",
    "logo": "logo", "all": "all", "alles": "all"
  };

  function show(key) {
    if (key === "all") {
      ["logo", "facts", "expect", "programm", "detail", "rsvp"].forEach(block);
      return true;
    }
    return block(key);
  }

  function help() {
    outText("facts        datum, ort, garage", "p");
    outText("format       was einen erwartet", "p");
    outText("programm     der nachmittag", "p");
    outText("detail       fireside chat und die drei use cases", "p");
    outText("rsvp         frist und zugang", "p");
    outText("countdown    bis doors open", "p");
    outText("logo         das rasterlogo", "p");
    outText("all          alles noch einmal", "p");
    outText("replay       die seite von vorne", "p");
    outText("clear        bildschirm leeren", "p");
    outText("aiq show --facts und die anderen langen formen gehen auch.", "dim");
  }

  function pad2(n) { return pad(n, 2); }

  function exec(raw) {
    var text = raw.replace(/\s+/g, " ").trim();
    echoCmd(text);
    if (!text) return;
    history.push(text); hIdx = history.length;
    var cmd = text.toLowerCase();

    if (cmd === "help" || cmd === "aiq" || cmd === "aiq help" || cmd === "aiq --help"
        || cmd === "?" || cmd === "man aiq") return help();

    /* Praefixe abstreifen: aiq show --facts, show facts, aiq facts, --facts */
    var key = cmd.replace(/^aiq\s+/, "").replace(/^(show|render)\s+/, "")
      .replace(/(^|\s)--/g, "$1").replace(/\s+/g, " ").trim();
    if (key.indexOf("logo") === 0) key = "logo";
    if (SHOW[key]) { show(SHOW[key]); return; }
    if (cmd === "aiq show" || cmd === "show")
      return outText("show: welchen teil? help zeigt die liste.", "err");
    if (cmd.indexOf("aiq show") === 0 || cmd.indexOf("show ") === 0)
      return outText("show: " + key + " kenne ich nicht. help zeigt die liste.", "err");
    if (key === "countdown") {
      var c = document.querySelector("[data-until]");
      out('<span class="k">doors open: </span><span class="v">'
          + esc(c ? c.textContent : "") + "</span>");
      return;
    }
    if (cmd === "ls" || cmd === "ls -la" || cmd === "ls -l" || cmd === "dir")
      return outText("offizielle-einladung.md", "v");
    if (cmd === "cat offizielle-einladung.md" || cmd === "cat offizielle-einladung"
        || key === "replay" || key === "restart") return start();
    if (cmd.indexOf("cat ") === 0)
      return outText("cat: " + text.slice(4) + ": no such file. ls zeigt, was da ist.", "err");
    if (cmd === "pwd") return outText("/aiqon", "v");
    if (cmd === "whoami") return outText("gast", "v");
    if (cmd === "date") {
      var d = new Date();
      return outText(d.getFullYear() + "-" + pad2(d.getMonth() + 1) + "-" + pad2(d.getDate())
        + " " + pad2(d.getHours()) + ":" + pad2(d.getMinutes()), "v");
    }
    if (cmd === "clear" || cmd === "cls") {
      lines.forEach(function (l) { l.classList.add("hid"); });
      [].slice.call(buf.querySelectorAll(".ln")).forEach(function (l) {
        if (l !== endLine && lines.indexOf(l) < 0) l.parentNode.removeChild(l);
      });
      endLine.classList.remove("hid");
      window.scrollTo(0, 0);
      return;
    }
    if (cmd === "exit" || cmd === "logout" || cmd === "quit")
      return outText("logout: erst am 22.10. um 18:00.", "p");
    if (cmd.indexOf("sudo") === 0)
      return outText("gast is not in the sudoers file. this incident will be reported.", "err");
    if (cmd === "rm -rf /" || cmd.indexOf("rm ") === 0)
      return outText("rm: die einladung bleibt.", "err");
    outText("aiqon: command not found: " + text.split(" ")[0] + ". help zeigt die befehle.", "err");
  }

  function armShell() {
    if (live || !endLine) return;
    var caret = endLine.querySelector(".caret");
    live = document.createElement("span");
    live.className = "cm live";
    live.setAttribute("contenteditable", "true");
    live.setAttribute("spellcheck", "false");
    live.setAttribute("autocapitalize", "off");
    live.setAttribute("autocorrect", "off");
    live.setAttribute("aria-label", "Befehl eingeben, help zeigt die Liste");
    endLine.insertBefore(live, caret);

    live.addEventListener("keydown", function (e) {
      if (e.key === "Enter") {
        e.preventDefault();
        var t = live.textContent;
        live.textContent = "";
        exec(t);
        pinned = true;
        follow(endLine);
        live.focus();
      } else if (e.key === "ArrowUp" && history.length) {
        e.preventDefault();
        hIdx = Math.max(0, hIdx - 1);
        live.textContent = history[hIdx];
        place();
      } else if (e.key === "ArrowDown" && history.length) {
        e.preventDefault();
        hIdx = Math.min(history.length, hIdx + 1);
        live.textContent = hIdx < history.length ? history[hIdx] : "";
        place();
      } else if (e.key === "l" && e.ctrlKey) {
        e.preventDefault(); exec("clear");
      }
    });
    live.addEventListener("input", function () {
      if (/\n/.test(live.textContent)) live.textContent = live.textContent.replace(/\n/g, " ");
    });
    live.addEventListener("paste", function (e) {
      e.preventDefault();
      var t = (e.clipboardData || window.clipboardData).getData("text");
      document.execCommand("insertText", false, t.replace(/\s+/g, " "));
    });
  }

  function place() {
    var r = document.createRange(), s = window.getSelection();
    r.selectNodeContents(live); r.collapse(false);
    s.removeAllRanges(); s.addRange(r);
  }

  var keyboard = window.matchMedia("(hover:hover) and (pointer:fine)");
  function focusShell(force) {
    if (!live || !root.classList.contains("done")) return;
    if (!force && !keyboard.matches) return;
    if (window.getSelection && String(window.getSelection())) return;
    live.focus({ preventScroll: true });
  }

  /* -------------------------------------------------- Seitlicher Rand
     Keine Zeile bricht um. Passt eine nicht in die Breite, scrollt der
     Puffer seitlich. Damit das nicht nach abgeschnitten aussieht,
     blendet die Kante aus, solange dort noch etwas steht. */

  var screenEl = document.querySelector(".screen");
  if (screenEl) {
    var edges = function () {
      var over = screenEl.scrollWidth - screenEl.clientWidth;
      var x = screenEl.scrollLeft;
      screenEl.classList.toggle("x-more", over > 2 && x < over - 2);
      screenEl.classList.toggle("x-back", over > 2 && x > 2);
    };
    edgeCheck = edges;
    screenEl.addEventListener("scroll", edges, { passive: true });
    window.addEventListener("resize", edges);
    if (window.ResizeObserver) new ResizeObserver(edges).observe(screenEl);
    edges();
  }

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
