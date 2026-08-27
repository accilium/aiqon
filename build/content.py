# -*- coding: utf-8 -*-
"""Inhalt der aIQon-Landingpage. Eine Quelle fuer beide Varianten.

Alles hier drin steht auch auf dem Flyer. Nichts dazu erfinden.
"""
import html
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LOGO = (HERE / "logo-ascii.txt").read_text(encoding="utf-8") \
    .rstrip("\n").split("\n")

TITLE = "aIQon, 22. Oktober 2026, Juwel Wien"
DESC = ("aIQon, 22. Oktober 2026, Juwel Wien, 15. Obergeschoss. AI-Use-Cases, "
        "die bei accilium im Echtbetrieb laufen, vorgestellt von den Menschen, "
        "die sie gebaut haben.")
FILE = "offizielle-einladung.md"


# ---------------------------------------------------------------- Bausteine

def esc(s):
    return html.escape(s, quote=False)


def ln(inner, cls=None, step=None, pause=None):
    """Eine Terminalzeile. step = ms bis zur naechsten, pause = Extrapause danach."""
    a = f' class="ln {cls}"' if cls else ' class="ln"'
    if step is not None:
        a += f' data-step="{step}"'
    if pause is not None:
        a += f' data-pause="{pause}"'
    return f"<div{a}>{inner}</div>"


def blank(step=90):
    return ln("", step=step)


def cmd(head, tail=""):
    """Prompt plus Befehl. Der Befehl wird Zeichen fuer Zeichen getippt."""
    inner = ('<span class="ps">aiqon ~ % </span>'
             '<span class="cm" data-type>'
             f'<span class="c1">{esc(head)}</span>')
    if tail:
        inner += f'<span class="c2">{esc(tail)}</span>'
    return ln(inner + "</span>", cls="cmd")


def kv(key, value, step=78, pause=None, href=None):
    """Schluessel und Wert. Mit href wird der Wert ein Link, die
    Zeichenbreite bleibt gleich, das Raster verschiebt sich also nicht."""
    val = esc(value)
    if href:
        val = (f'<a class="v lk" href="{href}" target="_blank" '
               f'rel="noopener">{val}</a>')
    else:
        val = f'<span class="v">{val}</span>'
    return ln(f'<span class="k">{esc(key.ljust(10))}</span>{val}',
              step=step, pause=pause)


def head2(text):
    return ln(f'<span class="hh">## </span><span class="h">{esc(text)}</span>',
              step=110, pause=200)


def prose(text, pause=None):
    return ln(f'<span class="p">{esc(text)}</span>', step=250, pause=pause)


def fence(step=78, pause=None):
    return ln('<span class="fc">---</span>', step=step, pause=pause)


def slot(time, title, ph_key=None, tail=None, strong=False, step=96, pause=None):
    """Programmzeile. Titel ab Spalte 9, Platzhalter ab Spalte 36."""
    row = (f'<span class="{"ts" if strong else "t"}">{esc(time)}</span>'
           f'<span class="sp">   </span>')
    n = "ns" if strong else "n"
    if ph_key:
        row += f'<span class="{n}">{esc(title.ljust(27))}</span>'
        # Der Platzhalter haengt in einer Klammer zusammen. Sonst bleibt
        # auf schmalen Geraeten die schliessende Klammer allein zurueck.
        row += (f'<span class="phg"><span class="ph">'
                f'{esc(("[ " + ph_key + ":").ljust(10))}</span>'
                f'<span class="tbd">tbd</span><span class="ph"> ]</span></span>')
    else:
        row += f'<span class="{n}">{esc(title)}</span>'
        if tail:
            row += f'<span class="until">{esc(tail)}</span>'
    return ln(row, step=step, pause=pause)


# ---------------------------------------------------------------- Bloecke
# Ein Block ist ein Befehl plus seine Ausgabe.

BLOCK_LOGO = [
    cmd("aiq render logo", " --über den Dächern Wiens --scale 1"),
    blank(step=340),
    *[ln(f'<span class="lg">{esc(r)}</span>', cls="logo", step=52) for r in LOGO],
    blank(step=170),
    ln('<span class="ok">✓</span><span class="dim"> aiq.svg rendered</span>',
       step=110, pause=520),
]

BLOCK_FACTS = [
    cmd("aiq show", " --facts"),
    blank(step=210),
    fence(),
    kv("event:", "aIQon #1 VIENNA"),
    kv("date:", "2026-10-22"),
    kv("doors:", "13:00"),
    kv("end:", "18:00"),
    kv("venue:", "Juwel Wien, Taborstraße 1-3, 1020 Wien",
       href="https://maps.app.goo.gl/tZwYaqccg2DTDj6k7"),
    kv("floor:", "15"),
    kv("parking:", "Garage Praterstraße, BEST IN PARKING",
       href="https://maps.app.goo.gl/AFxFrwgYQfp82En39"),
    fence(pause=520),
]

BLOCK_EXPECT = [
    cmd("aiq show", " --what-to-expect"),
    blank(step=210),
    head2("No Slides, Live Demos only"),
    blank(step=140),
    # Umbrueche wie auf dem Flyer, Zeichen fuer Zeichen. Die Spaltenbreite
    # der Seite richtet sich danach, damit hier nichts umbricht.
    prose("auf der aIQon sehen Sie AI-Use-Cases, die bei accilium schon im"),
    prose("Echtbetrieb laufen. Sie erledigen Aufgaben, zu einem Bruchteil "
          "der Kosten."),
    prose("Vorgestellt von den Menschen, die sie gebaut haben.", pause=560),
]

BLOCK_PROGRAMM = [
    cmd("aiq show", " --programm"),
    blank(step=210),
    head2("programm"),
    blank(step=140),
    slot("13:00", "empfang", strong=True),
    slot("13:30", "begrüßung"),
    slot("13:40", "fireside chat + q&a", ph_key="gäste"),
    slot("14:10", "live use case I", ph_key="case"),
    slot("14:30", "coffee break", strong=True),
    slot("14:50", "live use case II", ph_key="case"),
    slot("15:10", "live use case III", ph_key="case"),
    slot("15:30", "closing chat + q&a", ph_key="gäste"),
    slot("16:00", "flying dinner + networking", tail="  ->  18:00",
         strong=True, pause=560),
]

# Kein oeffentlicher Weg zur Teilnahme. Eingeladen wird persoenlich per
# Mail mit .ics im Anhang, deshalb steht hier weder Link noch Formular
# noch Mailadresse. Die Zeile "zugang" ist die geschlossene Tuer: sie sagt,
# dass es nichts anzuklicken gibt.
BLOCK_RSVP = [
    cmd("aiq show", " --rsvp"),
    blank(step=210),
    head2("rsvp"),
    blank(step=140),
    ln('<span class="k">deadline:  </span><span class="v">2026-09-18</span>',
       step=140),
    ln('<span class="k">zugang:    </span>'
       '<span class="v">persönliche einladung</span>', step=140, pause=460),
]

# Startzeit des Events. Am 22.10.2026 gilt in Wien noch Sommerzeit,
# die Umstellung ist erst am 25.10., deshalb +02:00.
LAUNCH = "2026-10-22T13:00:00+02:00"

PROMPT_END = ln('<span class="ps">aiqon ~ % </span><span class="caret"></span>',
                cls="end")

# Leerzeile zwischen zwei Bloecken. Wird beim Zusammensetzen eingeschoben,
# nicht in den Block selbst, damit Variante B ohne fuehrende Leerzeile
# in die zweite Spalte starten kann.
SEP = blank(step=170)

BLOCKS = [BLOCK_LOGO, BLOCK_FACTS, BLOCK_EXPECT, BLOCK_PROGRAMM, BLOCK_RSVP]

# Variante B: linke Spalte Logo und Hard Facts, rechte Spalte Inhalt,
# Programm und RSVP. Teilt die Zeilen etwa 25 zu 30.
SPLIT_B = 2
