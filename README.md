# aiqon

Source for the [**aIQon**](https://accilium.github.io/aiqon/) page, acciliums
afternoon on AI in Vienna. Thursday, 22 October 2026, Juwel Wien, 15th floor.

## What this is

One static page, served via GitHub Pages. No framework, no tracking, no
third-party requests: the typeface is self-hosted and the only images are our
own.

The page boots like a terminal. It starts empty, types its first command,
renders the aIQ logo as a character raster, then prints the hard facts, the
format, the programme and the RSVP date. A countdown to doors open sits at the
bottom. The whole sequence takes about twelve seconds; a click or a keypress
skips to the end. `prefers-reduced-motion` shows everything at once.

The full text is in the HTML. JavaScript only reveals it step by step, so
search engines, screen readers and anyone with JavaScript off get the complete
page immediately.

The format in one line: AI solutions that are in operation today, shown live by
the people who built them. No slides, no concepts, no vendor pitch.

## Attendance

aIQon is invitation-only. Guests are invited personally, by mail, with a
calendar file attached. There is deliberately no sign-up link, no form and no
address on this page.

## Layout

The page has one column and a fixed character grid, the way the printed flyer
does. Two consequences worth knowing before editing:

- **The window width follows the widest line in the content**, currently 74
  characters. Add a longer line and the window gets wider on its own so that
  nothing ever wraps on a desktop screen. The width depends only on the
  viewport, never on the content, so it cannot jump while the page boots.
- **From 1080 px of viewport height the page fits on one screen.** It scales
  the type down so all 57 lines plus the bars fit, and the window shrinks with
  it. Below that the type stays at 16 px and the page scrolls.

## Local preview

Open `index.html` in a browser. Nothing to install.

## Editing

`index.html` is generated. Do not hand-edit it, the next build overwrites it.
The text lives in `build/content.py`, the layout in `build/build.py`:

    python3 build/build.py

That writes `index.html` and `build/og.build.html`. `build/README.md` explains
the rest, including how the preview image is rendered. `boot.js` is written by
hand and is not generated.

## Why this repo is public

We publish how we build the consultancy, and that includes how we run our
events. Like the [aIQ blog](https://github.com/accilium/aIQ-blog), the source
and its history are part of what we share.

## Maintainers

Maintained by the accilium aIQ team. For corrections, open an issue.
Speaker line-ups and invitations are handled internally, not here.

## License

Content and code under the [MIT License](LICENSE). The accilium logo is a
trademark and not covered by the license. JetBrains Mono is licensed under the
SIL Open Font License, see `assets/fonts/OFL.txt`.
