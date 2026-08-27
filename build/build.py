#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Baut die aIQon-Landingpage.

    python3 site/build.py

    python3 build/build.py

Ergebnis:
    index.html            die Seite, eigenstaendig, CSS und JS inline
    build/og.build.html   Quelle fuer das Vorschaubild assets/og.jpg

Nach aussen zeigt die Seite nur auf assets/ und boot.js. Der Ordner
entspricht eins zu eins dem Wurzelverzeichnis des Repositories
accilium/aiqon, ein Update ist also ein Kopiervorgang.

Die Spaltenbreite ist nicht geraten: sie folgt der breitesten Zeile im
Inhalt. Kommt eine laengere Zeile dazu, wird das Fenster automatisch
breiter, damit nie etwas umbricht.
"""
import datetime
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import content as C  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent

# Fuer die absoluten Adressen in den og-Tags. Ohne Schraegstrich am Ende.
BASE_URL = "https://accilium.github.io/aiqon"

LINE_H = 1.52          # Zeilenabstand im Puffer
CAP = 16               # groesste Schriftgroesse in px
FLOOR = 9.5            # kleinste Schriftgroesse in px
GUT = 3.3              # Breite der Zeilennummernspalte in Zeichenbreiten
ADV = 0.6              # Zeichenbreite von JetBrains Mono in em
PAD_X = 26             # Innenabstand des Puffers links und rechts
CHROME = 168           # Leisten, Countdown und Innenabstaende in px,
                       # ohne den Abstand des Fensters zum Fensterrand

# ---------------------------------------------------------------- Schrift
# 800 ist ExtraBold. Alles, was im Text hervorgehoben ist, laeuft damit,
# 700 war bei den kleinen Groessen zu schwach.

WEIGHTS = (400, 500, 700, 800)


def fonts(prefix=""):
    return "".join(
        "@font-face{font-family:'aIQ Mono';font-style:normal;font-display:block;"
        f"font-weight:{w};src:url({prefix}assets/fonts/jetbrainsmono-{w}.woff2)"
        " format('woff2')}"
        for w in WEIGHTS
    )


FONTS = fonts()


# ---------------------------------------------------------------- Maße

def plain(html):
    return re.sub(r"<[^>]+>", "", html).replace("&amp;", "&")


def measure(all_lines):
    """Breiteste Zeile in Zeichen und Zeilenzahl."""
    cols = max(len(plain(l)) for l in all_lines)
    return cols, len(all_lines)


# ---------------------------------------------------------------- CSS

BASE = """
*{margin:0;padding:0;box-sizing:border-box}

:root{
  --ink:#031B24;
  --ground:#04232E;
  --rule:#0E3846;
  --gutrule:#1B4653;
  --linenum:#28596A;
  --dim:#41626D;
  --muted:#6C8C96;
  --body:#B3C8CD;
  --text:#EAEFF0;
  --mint:#54DBC0;
  --teal:#2FA39D;
  --pad:clamp(12px,3vw,44px);
}

html{background:var(--ink);-webkit-text-size-adjust:100%;
  scrollbar-gutter:stable}
/* clip statt hidden, damit position:sticky nicht bricht */
body{overflow-x:clip}
body{
  font-family:'aIQ Mono',ui-monospace,SFMono-Regular,Menlo,monospace;
  font-weight:400;color:var(--body);background:transparent;
  -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;
}

/* Hintergrund: der leere Saal im 15. Obergeschoss, gerastert */
.bg{position:fixed;inset:0;z-index:-1;
  background:#04232E url(assets/bg-juwel.png) center center/cover no-repeat}
.bg::after{content:"";position:absolute;inset:0;
  background:linear-gradient(180deg,rgba(3,27,36,.58) 0%,
    rgba(3,27,36,.74) 45%,rgba(3,27,36,.90) 100%)}

/* ---------------- Fenster ----------------
   Die Breite haengt an der Schriftgroesse, das Fenster umschliesst den
   Text also immer knapp. Deshalb wird die Schriftgroesse aus dem
   Viewport berechnet und nicht aus dem Container: sonst waere es rund. */
.stage{display:flex;min-height:100svh;padding:var(--pad)}
.term{
  /* Innenbreite, die dem Puffer bleibt. 16px Abzug fuer den Scrollbalken. */
  --avail:calc(100vw - 2 * var(--pad) - __PADSUM__px - 16px);
  --fs-w:calc(var(--avail) / __TOTAL__);
  --fs-h:calc((100svh - 2 * var(--pad) - __CHROME__px) / __LINEEM__);
  --fs:clamp(__FLOOR__px, var(--fs-w), __CAP__px);
  --gut:calc(var(--fs) * __GUT__);
  margin:auto;
  width:calc(var(--fs) * __TOTAL__ + __PADSUM__px);
  max-width:100%;
  /* Ohne min-width:0 zieht die Mindestbreite des Inhalts das Fenster
     auf, sobald eine breite Zeile auftaucht. Dann springt es. */
  min-width:0;
  background:rgba(4,35,46,.80);
  -webkit-backdrop-filter:blur(16px) saturate(1.08);
  backdrop-filter:blur(16px) saturate(1.08);
  border:1px solid var(--rule);border-radius:12px;
  box-shadow:0 30px 90px rgba(0,0,0,.55),0 0 0 1px rgba(84,219,192,.05);
  overflow:hidden;
}
@media (max-width:520px){.term{border-radius:9px}}

/* ---------------- Zeilenraster ----------------
   --fs-w: so gross, dass die breiteste Zeile plus Nummernspalte in die
           Viewportbreite passt.
   --fs-h: so gross, dass alle Zeilen plus Leisten in die Viewporthoehe
           passen. Wird nur ab __ONEPAGE__px Viewporthoehe benutzt, weil
           die Schrift darunter zu klein wuerde. Dann scrollt die Seite. */
@media (min-height:__ONEPAGE__px){
  .term{--fs:clamp(__FLOOR__px, min(var(--fs-w), var(--fs-h)), __CAP__px)}
}
.buf{
  position:relative;
  counter-reset:ln;
  font-size:var(--fs);
  line-height:__LINEH__;
}
.buf::before{content:"";position:absolute;left:calc(var(--fs) * 2.5);
  top:0;bottom:0;width:1px;background:var(--gutrule)}

.ln{position:relative;
  padding-left:calc(var(--gut) + var(--fs) * 1.2);
  text-indent:calc(var(--fs) * -1.2);
  min-height:__LINEH__em;
  white-space:pre-wrap;overflow-wrap:break-word}
.ln::before{
  counter-increment:ln;content:counter(ln,decimal-leading-zero);
  position:absolute;left:0;top:0;width:calc(var(--fs) * 1.8);
  font-size:var(--fs);font-weight:400;line-height:__LINEH__;
  text-align:right;color:var(--linenum);letter-spacing:.03em;
  -webkit-user-select:none;user-select:none;
}
/* Das Rasterlogo ist 58 Zeichen breit und darf nie umbrechen. Mit
   0.9655 der Textgroesse ist es genauso breit wie 56 Zeichen Text. */
.ln.logo{white-space:pre;
  font-size:min(calc(var(--fs) * .9655),
    calc((var(--avail) - var(--gut)) / 34.8))}
html.js .hid{display:none}

/* ---------------- Syntax ---------------- */
.ps{color:var(--muted)}
.c1{color:var(--mint)}
.c2{color:var(--teal)}
.lg{color:var(--text)}
.ok{color:var(--mint);font-weight:800}
.dim{color:var(--muted)}
.fc{color:var(--dim)}
.k{color:var(--body)}
.v{color:var(--text);font-weight:800}
.hh{color:var(--mint);font-weight:800}
.h{color:var(--text);font-weight:800}
.p{color:var(--body)}
.t,.n{color:var(--body)}
.ts,.ns,.until{color:var(--text);font-weight:800}
/* pre, nicht nowrap: nowrap kollabiert die Leerzeichen im Platzhalter,
   dann steht tbd nicht mehr in einer Spalte. */
.phg{white-space:pre}
.ph{color:var(--dim)}
.tbd{color:var(--teal)}
/* Links behalten die Farbe des Werts, mint ist nur die Unterstreichung.
   So bleibt die Spalte ruhig und man sieht trotzdem, dass es klickbar ist. */
.lk{text-decoration:underline;text-decoration-thickness:1px;
  text-decoration-color:var(--teal);text-underline-offset:.2em}
.lk:hover,.lk:focus-visible{color:var(--mint);
  text-decoration-color:var(--mint)}
.lk:focus-visible{outline:1px solid var(--mint);outline-offset:3px}

@keyframes blink{50%{opacity:0}}
.cm.typing::after,.caret::after{
  content:"\\258C";color:var(--mint);
  animation:blink 1.05s steps(1) infinite;
}
@media (prefers-reduced-motion:reduce){
  .cm.typing::after,.caret::after{animation:none}
}

/* ---------------- Countdown ----------------
   NASA-Schreibweise T-DDD:HH:MM:SS, nach dem Start laeuft es als T+
   weiter. Monospace ist von sich aus tabellarisch, die Ziffern wackeln
   also nicht. */
.clock{
  display:flex;flex-wrap:wrap;align-items:baseline;
  gap:0 calc(var(--fs) * 2);
  padding:clamp(12px,1.6vw,18px) __PADX__px;
  padding-left:calc(__PADX__px + var(--gut));
  border-top:1px solid var(--rule);
  font-size:var(--fs);line-height:__LINEH__}
.clock .lab{color:var(--muted);white-space:nowrap}
.clock .cd{color:var(--mint);font-weight:800;white-space:nowrap}
.clock .fmt{color:var(--dim);white-space:nowrap}
@media (max-width:560px){.clock .fmt{display:none}}

/* ---------------- Leisten ---------------- */
.bar{display:flex;align-items:center;gap:9px;padding:12px __PADX__px;
  overflow:hidden;
  border-bottom:1px solid var(--rule);
  background:rgba(7,43,54,.72);
  -webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px)}
.bar i{width:9px;height:9px;border-radius:50%;background:#1C5B68;flex:0 0 auto}
.bar i:nth-of-type(2){background:#249C97}
.bar i:nth-of-type(3){background:var(--mint)}
.bar .path{font-size:12px;letter-spacing:.04em;color:var(--muted);
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bar .path b{color:var(--body);font-weight:500}
.bar .when{margin-left:auto;font-size:11px;letter-spacing:.08em;
  color:var(--dim);white-space:nowrap}
@media (max-width:560px){.bar .when{display:none}}

.screen{padding:clamp(18px,2.4vw,26px) __PADX__px clamp(20px,2.8vw,30px)}

.status{display:flex;align-items:center;gap:14px;padding:11px __PADX__px;
  flex-wrap:wrap;
  border-top:1px solid var(--rule);
  background:rgba(3,27,36,.72);
  -webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);
  font-size:11px;letter-spacing:.07em;color:var(--dim)}
.status .grow{flex:1 1 auto}
.status .mark{height:18px;width:auto;opacity:.9;flex:0 0 auto}
.status button{
  font:inherit;letter-spacing:inherit;color:var(--muted);
  background:none;border:1px solid var(--rule);border-radius:3px;
  padding:3px 9px;cursor:pointer;white-space:nowrap}
.status button:hover{color:var(--mint);border-color:rgba(84,219,192,.45)}
.status button:focus-visible{outline:1px solid var(--mint);outline-offset:2px}
@media (max-width:430px){.status .when-rsvp{display:none}}
html.done [data-skip],html:not(.done) [data-replay]{display:none}
html:not(.js) [data-skip],html:not(.js) [data-replay]{display:none}
"""

# ---------------------------------------------------------------- Gerüst

PAGE = """<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index,follow">
<meta property="og:type" content="website">
<meta property="og:site_name" content="aIQon">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{base}/">
<meta property="og:image" content="{base}/assets/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#04232E">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="preload" href="assets/fonts/jetbrainsmono-400.woff2" as="font"
      type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/jetbrainsmono-800.woff2" as="font"
      type="font/woff2" crossorigin>
<script>document.documentElement.className+=" js";</script>
<style>{fonts}{css}</style>
</head>
<body>
<div class="bg" aria-hidden="true"></div>
{body}
<script src="boot.js"></script>
</body>
</html>
"""

BAR = ('<header class="bar">'
       '<i></i><i></i><i></i>'
       f'<span class="path">aiqon&nbsp;~&nbsp;/&nbsp;<b>{C.FILE}</b></span>'
       '<span class="when">DO 22.10.2026 &middot; JUWEL WIEN, 15. OG</span>'
       '</header>')

CLOCK = ('<section class="clock hid" data-step="300">'
         '<span class="lab">countdown to doors open</span>'
         f'<span class="cd" data-until="{C.LAUNCH}" aria-live="off">'
         '{start}</span>'
         '<span class="fmt">dd:hh:mm:ss</span>'
         '</section>')

STATUS = ('<footer class="status">'
          '<span class="when-rsvp">RSVP bis 18.09.2026</span>'
          '<span class="grow"></span>'
          '<button type="button" data-skip>Ausgabe &uuml;berspringen</button>'
          '<button type="button" data-replay>Neu starten</button>'
          '<img class="mark" src="assets/accilium-logo-white.svg" alt="accilium">'
          '</footer>')


def all_lines():
    """Alle Pufferzeilen in Reihenfolge, Trenner dazwischen."""
    parts = []
    for i, block in enumerate(C.BLOCKS):
        if i:
            parts.append(C.SEP)
        parts.extend(block)
    parts.append(C.SEP)
    parts.append(C.PROMPT_END)
    return parts


def countdown_start():
    """Startwert fuer das Markup, nur fuer den Fall ohne JavaScript.
    Auf ganze Tage abgeschnitten: sonst stuende in jedem Build eine andere
    Sekunde und die generierte Datei haette bei jedem Lauf einen Diff."""
    left = (datetime.datetime.fromisoformat(C.LAUNCH)
            - datetime.datetime.now(datetime.timezone.utc))
    days = max(0, int(left.total_seconds()) // 86400)
    return f"T-{days:03d}:00:00:00"


def css(cols, lines):
    total = cols * ADV + GUT              # Zeichenbreiten je Zeile
    padsum = 2 * PAD_X + 2                # Innenabstand plus Rahmen
    line_em = round(lines * LINE_H, 2)    # Puffer hoehe in em
    # Ab welcher Viewporthoehe lohnt der Onepager: dort kommt gerade noch
    # die Mindestschriftgroesse heraus.
    onepage = int(FLOOR * line_em + CHROME + 2 * 44) + 1
    out = BASE
    for token, value in (
        ("__TOTAL__", f"{total:.2f}"),
        ("__PADSUM__", str(padsum)),
        ("__PADX__", str(PAD_X)),
        ("__CHROME__", str(CHROME)),
        ("__LINEEM__", f"{line_em}"),
        ("__LINEH__", f"{LINE_H}"),
        ("__GUT__", f"{GUT}"),
        ("__FLOOR__", f"{FLOOR}"),
        ("__CAP__", str(CAP)),
        ("__ONEPAGE__", str(onepage)),
    ):
        out = out.replace(token, value)
    assert "__" not in out, "unersetzter Platzhalter im CSS"
    return out, total, onepage


OG = """<!doctype html>
<html lang="de"><head><meta charset="utf-8"><title>aIQon og</title><style>
{fonts}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1200px;height:630px;overflow:hidden;
  font-family:'aIQ Mono',monospace;
  background:#04232E url(../assets/bg-juwel.png) center center/cover no-repeat}}
.scrim{{position:absolute;inset:0;
  background:linear-gradient(180deg,rgba(3,27,36,.55),rgba(3,27,36,.82))}}
.buf{{position:relative;counter-reset:ln;padding:44px 54px;
  font-size:20px;line-height:1.62}}
.buf::before{{content:"";position:absolute;left:104px;top:36px;bottom:36px;
  width:1px;background:#1B4653}}
.ln{{position:relative;padding-left:66px;min-height:1.62em;white-space:pre}}
.ln::before{{counter-increment:ln;content:counter(ln,decimal-leading-zero);
  position:absolute;left:0;top:0;width:36px;text-align:right;color:#28596A}}
.ps{{color:#6C8C96}}.c1{{color:#54DBC0}}.c2{{color:#2FA39D}}
.lg{{color:#EAEFF0}}.k{{color:#B3C8CD}}.v{{color:#EAEFF0;font-weight:800}}
.mark{{position:absolute;right:54px;bottom:40px;height:26px;opacity:.9}}
</style></head><body>
<div class="scrim"></div>
<div class="buf">
<div class="ln"><span class="ps">aiqon ~ % </span><span class="c1">cat</span
  ><span class="c2"> ./{file}</span></div>
<div class="ln"></div>
{logo}
<div class="ln"></div>
<div class="ln"><span class="k">date:     </span><span class="v">2026-10-22, 13:00 bis 18:00</span></div>
<div class="ln"><span class="k">venue:    </span><span class="v">Juwel Wien, Taborstra&szlig;e 1-3, 1020 Wien, 15. OG</span></div>
</div>
<img class="mark" src="../assets/accilium-logo-white.svg" alt="">
</body></html>
"""


def build_og():
    logo = "\n".join(f'<div class="ln"><span class="lg">{C.esc(r)}</span></div>'
                     for r in C.LOGO)
    out = HERE / "og.build.html"
    out.write_text(OG.format(fonts=fonts("../"), logo=logo, file=C.FILE),
                   encoding="utf-8")
    print(f"{out.name}  Quelle fuer assets/og.jpg")


if __name__ == "__main__":
    lines = all_lines()
    cols, n = measure(lines)
    sheet, total, onepage = css(cols, n)

    body = ('<main class="stage"><div class="term">'
            + BAR
            + '<div class="screen"><div class="pane"><div class="buf">'
            + "\n".join(lines)
            + '</div></div></div>'
            + CLOCK.format(start=countdown_start())
            + STATUS
            + '</div></main>')

    out = ROOT / "index.html"
    out.write_text(PAGE.format(title=C.TITLE, desc=C.DESC, fonts=FONTS,
                               css=sheet, body=body, base=BASE_URL),
                   encoding="utf-8")
    print(f"{out.name}  {out.stat().st_size / 1024:.0f} KB")
    print(f"  breiteste Zeile   {cols} Zeichen")
    print(f"  Zeilen            {n}")
    print(f"  Fenster bei {CAP} px  {total * CAP + 2 * PAD_X + 2:.0f} px breit")
    print(f"  Onepager ab       {onepage} px Viewporthoehe")
    build_og()
