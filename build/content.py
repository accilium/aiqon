# -*- coding: utf-8 -*-
"""Inhalt der aIQon-Landingpage. Eine Quelle fuer beide Varianten.

Alles hier drin steht auch auf dem Flyer. Nichts dazu erfinden.
"""
import html
import pathlib
import textwrap

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
    slot("14:10", "live use case I"),
    slot("14:30", "coffee break", strong=True),
    slot("14:50", "live use case II"),
    slot("15:10", "live use case III"),
    slot("15:30", "closing chat + q&a", ph_key="gäste"),
    slot("16:00", "flying dinner + networking", tail="  ->  18:00",
         strong=True, pause=560),
]

# ---------------------------------------------------------------- Use Cases
# Zwei Portraits, gerastert wie das Hintergrundbild, stehen links neben
# den ersten fuenf Zeilen eines Falls. Sie haengen an der Titelzeile und
# sind so hoch wie fuenf Zeilen; die vier Zeilen darunter ruecken per
# Leerzeichen ein, damit das Raster stehen bleibt. Textbreite: 46 Zeichen.
FIG_LINES = 5
FIG_INDENT = 28
CASE_WIDTH = 74 - FIG_INDENT


def fig(title, pair):
    """Titelzeile eines Falls mit den beiden Portraits davor."""
    imgs = "".join(
        f'<img class="pic {c}" src="assets/team/{f}.png" alt="{esc(n)}">'
        for c, (f, n) in zip(("a", "b"), pair))
    return ln(f'{imgs}{" " * FIG_INDENT}<span class="h">{esc(title)}</span>',
              cls="fig", step=140)


def case_lines(title, pair, problem, solution):
    names = ", ".join(n for _, n in pair)
    pad = " " * FIG_INDENT
    rows = [
        fig(title, pair),
        ln(f'{pad}<span class="dim">{esc(names)}</span>', step=90),
        blank(),
        ln(f'{pad}<span class="k">problem:</span>', step=90),
    ]
    rows += [ln(f'{pad}<span class="p">{esc(t)}</span>', step=70)
             for t in textwrap.wrap(problem, CASE_WIDTH)]
    rows += [blank(), ln(f'{pad}<span class="k">lösung:</span>', step=90)]
    rows += [ln(f'{pad}<span class="p">{esc(t)}</span>', step=70)
             for t in textwrap.wrap(solution, CASE_WIDTH)]
    return rows


LEO = ("leonhard-kuehne-hellmessen", "Leonhard Kühne-Hellmessen")
MARY = ("mary-koryakina", "Mary Koryakina")
ALEX = ("alex-rinner", "Alex Rinner")
SEBASTIAN = ("sebastian-kindl", "Sebastian Kindl")
DAVID = ("david-schneiderbauer", "David Schneiderbauer")

# Platzhalter bis zur Shortlist. Text aus aiqon-orga/demo-candidates.md,
# Abschnitt "Kurztexte fuer Save the Date und Landing Page".
CASES = [
    ("live use case I", "Der Projektmanager, der nie schläft", (LEO, MARY),
     "Ein Projekt unter Zeitdruck. Termine stehen im Chat, Aufgaben in "
     "einer Tabelle, Entscheidungen in Köpfen. Der Projektlead verbringt "
     "den Tag damit, den Stand zusammenzusuchen.",
     "Ein Agent wird Mitglied im Teams-Chat, liest den Projektordner mit "
     "und hält Fristen, Aufgaben und offene Punkte nach. Freitags schickt "
     "er den Status von selbst. Was entschieden wird, entscheidet das Team."),
    ("live use case II", "Das Wissen der besten Kollegin für das ganze Team",
     (ALEX, SEBASTIAN),
     "Der Angebotsvergleich funktioniert, solange eine bestimmte Kollegin "
     "ihn macht. Sie weiß, dass Wartung und Mindestabnahme mitgerechnet "
     "werden müssen. Ist sie im Urlaub, fehlen diese Zeilen in der Tabelle.",
     "Die Kollegin erklärt ihre Regeln einmal. Daraus entsteht eine "
     "gespeicherte Arbeitsanweisung, die beim nächsten Fall in einer neuen "
     "Sitzung greift. Wer im Raum eine Regel ergänzen will, sieht sofort, "
     "was sich am Ergebnis ändert."),
    ("live use case III", "Einmal erzählen statt überall eintragen",
     (DAVID, MARY),
     "Nach dem Kundentermin weiß die Führungskraft viel: eine Zusage mit "
     "Frist, ein Termin ohne Datum, eine Folie, die nicht mehr stimmt. Am "
     "Abend landen davon zwei Zeilen in der Aufgabenliste. Der Rest bleibt "
     "im Kopf.",
     "Auf der Rückfahrt eine Sprachnachricht in Teams, 90 Sekunden, ohne "
     "Ordnung. Der Assistent macht daraus Termine, Aufgaben und Notizen am "
     "Dokument und zitiert alles, was er nicht zuordnen konnte. Geschrieben "
     "wird erst nach Bestätigung."),
]

BLOCK_CASES = [cmd("aiq show", " --use-cases"), blank(step=210)]
for i, (slot_name, title, pair, problem, solution) in enumerate(CASES):
    if i:
        BLOCK_CASES.append(blank(step=140))
    BLOCK_CASES.append(head2(slot_name))
    BLOCK_CASES.append(blank(step=140))
    BLOCK_CASES.extend(case_lines(title, pair, problem, solution))
BLOCK_CASES[-1] = BLOCK_CASES[-1].replace('class="ln"', 'class="ln" data-pause="560"', 1)

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

BLOCKS = [BLOCK_LOGO, BLOCK_FACTS, BLOCK_EXPECT, BLOCK_PROGRAMM, BLOCK_CASES,
          BLOCK_RSVP]

# Variante B: linke Spalte Logo und Hard Facts, rechte Spalte Inhalt,
# Programm und RSVP. Teilt die Zeilen etwa 25 zu 30.
SPLIT_B = 2
