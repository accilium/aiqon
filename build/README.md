# aIQon Landingpage

Stand 27.08.2026. Noch nichts gepusht, bewusst nur lokal.

Die Seite fährt hoch wie ein Terminal. Beim Öffnen ist der Bildschirm leer,
dann tippt sich der erste Befehl selbst, das aIQ-Logo wird als Raster
gerendert, danach kommen Hard Facts, Inhalt, Programm und RSVP. Zuletzt
das Countdown-Band. Nach etwa zwölf Sekunden steht alles.

Venue und Parkgarage sind mit Google Maps verlinkt. Der Wert bleibt weiß
wie die anderen Werte, nur die Unterstreichung ist petrol, damit die
Spalte ruhig bleibt.

Inhaltlich steht genau das drauf, was auch auf dem Flyer steht. Keine Use
Cases, keine Häuserregeln, keine Kalenderdatei.

## Öffnen

    open site/index.html

Irgendwohin klicken oder eine Taste drücken springt ans Ende.
„Neu starten" in der Fußleiste spielt es nochmal.

## Bauen

    python3 site/build.py

Erzeugt `index.html` und `og.build.html`. Die Seite ist eigenständig, CSS
steckt inline, nach außen zeigt sie nur auf `site/assets` und `site/boot.js`.

Das Teilerbild `assets/og.jpg` wird nicht automatisch neu gebaut:

    chrome --headless --window-size=1200,630 --virtual-time-budget=6000 \
           --screenshot=/tmp/og.png site/og.build.html

danach das PNG als JPEG nach `site/assets/og.jpg`.

## Dateien

| Datei | Inhalt |
|---|---|
| `content.py` | Der Text, die Startzeit für den Countdown. |
| `build.py` | Farben, Zeilenraster, Layout, Gerüst. |
| `boot.js` | Tippen, Zeilen einblenden, Überspringen, Countdown. |
| `assets/bg-juwel.png` | Der leere Saal im 15. OG, gerastert, 540 × 675, 278 KB. |
| `assets/fonts/` | JetBrains Mono, latin subset, 8 KB je Schnitt, selbst gehostet. |
| `assets/og.jpg` | Vorschaubild 1200 × 630 für Mail und Social. |

Ganze Seite rund 335 KB, davon 278 KB Hintergrundbild.

## Breite und Onepager

Die Spaltenbreite ist nicht gesetzt, sie folgt der breitesten Zeile im
Inhalt. Aktuell sind das 74 Zeichen, nämlich `Echtbetrieb laufen. Sie
erledigen Aufgaben, zu einem Bruchteil der Kosten.` Daraus ergibt sich bei
16 px Schrift ein Fenster von 817 px. Kommt eine längere Zeile dazu, wird
das Fenster von selbst breiter, damit nie etwas umbricht.

Der Onepager läuft über die Höhe: ab 1080 px Viewporthöhe rechnet die Seite
die Schrift so klein, dass alle 57 Zeilen plus Leisten auf einen Bildschirm
passen, und das Fenster schrumpft mit. Darunter bleibt die Schrift bei 16 px
und die Seite scrollt.

**Die Breite springt nicht.** Sie hängt nur an Viewportbreite und
Viewporthöhe, nie am Inhalt. Dazu gehören zwei Dinge: `min-width:0` auf dem
Fenster, sonst zieht die Mindestbreite einer breiten Zeile es auf, sobald
sie auftaucht. Und `scrollbar-gutter:stable` auf `html`, sonst verschiebt
der Scrollbalken die Breite in dem Moment, in dem der Inhalt höher als der
Viewport wird.

**Warum nicht auf jedem Laptop:** 57 Zeilen in einer Spalte brauchen bei
lesbarer Schrift rund 1080 px Höhe. Ein 13-Zoll-Laptop hat im Browser etwa
760 px, dort käme 6,5 px Schriftgröße heraus. Wenn der Onepager auch dort
sein soll, gibt es genau zwei Wege: zwei Spalten im Fenster, dann sind es
29 Zeilen und es passt überall, oder Inhalt streichen.

Gemessen: 1213 px Viewporthöhe ergibt 11,0 px Schrift und ein 581 px
breites Fenster, alles auf einem Bildschirm. 1413 px ergeben 13,4 px und
691 px. Bei 813 px bleibt es bei 16 px und 817 px, die Seite scrollt.

## Was sich schrauben lässt

- **Tempo:** `SPEED` in `boot.js`, oben. 1.0 wären 18 Sekunden, 0.65 sind
  knapp zwölf. Die einzelnen Zeilentakte stehen als `step` und `pause` in
  `content.py`.
- **Onepager-Schwelle:** `FLOOR` und `CHROME` in `build.py`.
- **Countdown-Ziel:** `LAUNCH` in `content.py`.

## Bewusste Entscheidungen

- **Kein Weg zur Zusage.** Eingeladen wird persönlich per Mail mit .ics im
  Anhang. Auf der Seite steht deshalb weder Link noch Formular noch
  Mailadresse. Die Zeile `zugang: persönliche einladung` ist die
  geschlossene Tür: sie sagt, dass es nichts anzuklicken gibt.
- **Der Countdown läuft in Textgröße.** Er sitzt als Statuszeile unter dem
  Puffer, linksbündig zur Textspalte, mint und ExtraBold. Groß gesetzt hat
  er den Rest der Seite erschlagen.
- **Hervorhebungen laufen mit ExtraBold, nicht Bold.** Bei 10 bis 16 px war
  700 zu schwach. ExtraBold hat dieselbe Zeichenbreite von 0.6 em, das
  Raster bleibt also stehen.
- **Fließtext mit den Umbrüchen des Flyers.** Vorher hat die Seite selbst
  umgebrochen, dann sprang die Zeilennummer nicht mehr mit dem Text und es
  sah nach Fehler aus.
- **Schrift selbst gehostet, nicht von Google Fonts.** Ein
  Google-Fonts-Link schickt die IP jedes Gasts an Google, das ist bei einer
  Einladung an C-Level unnötiges Risiko. Vier Schnitte kosten 32 KB.
- **Der Text steht vollständig im HTML.** JavaScript blendet ihn nur
  schrittweise ein. Ohne JS, mit Screenreader und für Suchmaschinen ist
  sofort alles da. `prefers-reduced-motion` zeigt alles ohne Animation.
- **Schriftgröße aus dem Viewport, nicht aus dem Container.** Die
  Fensterbreite hängt an der Schriftgröße, also darf die Schriftgröße nicht
  an der Fensterbreite hängen. Nebenbei: `cqi` in den eigenen Regeln eines
  Containers misst ohnehin den Vorfahren, und `counter-reset` am Container
  wird von dessen Style-Containment gekappt.
- **Das Rasterlogo läuft mit 0.9655 der Textgröße.** Es ist 58 Zeichen
  breit, damit ist es genauso breit wie 56 Zeichen Text.

## Offen

- Der Flyer als PNG nennt noch `accilium.github.io/aIQon`. Der Quelltext in
  `flyer/why-attend.txt` steht jetzt auf `aiqon`, das Artwork braucht also
  einen neuen Export.
- Auf Handys unter etwa 560 px Breite bricht die längste Fließtextzeile um.
  74 Zeichen gehen dort nicht in eine Zeile, egal wie klein die Schrift.
