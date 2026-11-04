#!/usr/bin/env python3
"""Generates every SVG in assets/ (pure stdlib, deterministic).

    python scripts/build_assets.py

Design system: "the page is a railway line".
  - Paper, ink and one hot vermilion; olive, cobalt and lavender appear only
    where a project owns them.
  - Square corners, hairline rules, no cards, no pills, no glow.
  - Type: a serif for voice, a Swiss sans for titles, a mono for metadata.
    Fonts are system stacks (an SVG used as <img> cannot load web fonts);
    big display lines use textLength so layout survives font substitution.
  - Motion is CSS-in-SVG, slow, and switched off by prefers-reduced-motion.
Every SVG paints its own background, so it reads the same in light and dark mode.
"""
import json
import math
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"

INK, PAPER, KRAFT = "#1B1814", "#F3ECDD", "#E8D8B6"
VERM, OLIVE, COBALT, LAV = "#D9441F", "#5E6B38", "#27479A", "#BDAED0"
MUTE, SOFT = "#6B6457", "#CFC6B2"  # secondary text on paper / on ink

SERIF = "'Iowan Old Style','Palatino Linotype',Palatino,'Book Antiqua','Charter','Bitstream Charter',Georgia,serif"
SANS = "'Helvetica Neue',Helvetica,'Arial Nova',Arial,'Inter',sans-serif"
MONO = "ui-monospace,'SF Mono',Menlo,Consolas,'Liberation Mono','DejaVu Sans Mono',monospace"

REDUCED = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"


def svg(w, h, body, title, desc, css="", defs=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-labelledby="t d"><title id="t">{escape(title)}</title>'
        f'<desc id="d">{escape(desc)}</desc><style>{css}{REDUCED}</style>'
        f'<defs>{defs}<filter id="grain" x="0" y="0" width="100%" height="100%">'
        f'<feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" seed="4" result="n"/>'
        f'<feColorMatrix in="n" type="matrix" values="0 0 0 0 .25  0 0 0 0 .2  0 0 0 0 .1  0 0 0 .11 0"/></filter></defs>'
        f'{body}</svg>\n'
    )


def paper(w, h, fill=PAPER, grain=True):
    g = f'<rect width="{w}" height="{h}" filter="url(#grain)"/>' if grain else ""
    return f'<rect width="{w}" height="{h}" fill="{fill}"/>{g}'


def t(x, y, s, size, fill=INK, family=SANS, weight=400, anchor="start", ls=0, style="", extra=""):
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}" letter-spacing="{ls}"{f' font-style="{style}"' if style else ""} {extra}>{escape(s)}</text>')


# ================================================================ masthead
ROLES = [
    "engineering student at ENIT",
    "software developer",
    "builder of AI agents",
    "robotics tinkerer, ESP32",
    "founder of PHYTO Cappuccino",
]
STATIONS = [(60, "01  ABOUT", "start"), (420, "02  INDEX", "middle"), (780, "03  WORK", "middle"), (1140, "04  ACTIVITY", "end")]


def masthead():
    W, H = 1200, 680
    cycle = 25.0
    css = [
        ".r{opacity:0}.r0{opacity:1}",
    ]
    roles = []
    for k, role in enumerate(ROLES):
        a, b = k * 20, k * 20 + 20
        if k == 0:
            kf = f"0%,17%{{opacity:1}}20%,97%{{opacity:0}}100%{{opacity:1}}"
        else:
            kf = f"0%,{a - 3}%{{opacity:0}}{a}%,{b - 3}%{{opacity:1}}{b}%,100%{{opacity:0}}"
        css.append(f"@keyframes r{k}{{{kf}}}.r{k}{{animation:r{k} {cycle:.0f}s ease-in-out infinite}}")
        roles.append(t(0, 0, role, 44, INK, SERIF, 400, style="italic", extra=f'class="r r{k}"'))
    css.append(
        "@keyframes run{0%,8%{transform:translateX(0)}28%,36%{transform:translateX(360px)}"
        "56%,64%{transform:translateX(720px)}84%,100%{transform:translateX(1080px)}}"
        ".train{animation:run 32s cubic-bezier(.6,0,.4,1) infinite alternate}"
        "@keyframes rise{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}"
        ".a1{animation:rise 1.1s .1s cubic-bezier(.2,.7,.2,1) both}.a2{animation:rise 1.1s .3s cubic-bezier(.2,.7,.2,1) both}"
        ".a3{animation:rise 1.1s .5s cubic-bezier(.2,.7,.2,1) both}"
    )
    line_y = 612
    stations = "".join(
        f'<circle cx="{x}" cy="{line_y}" r="13" fill="{PAPER}" stroke="{INK}" stroke-width="5"/>'
        + t(x, line_y + 44, lab, 16, INK, MONO, 500, anchor=anc, ls=2)
        for x, lab, anc in STATIONS
    )
    body = f"""
{paper(W, H)}
<rect x="50" y="42" width="1100" height="4" fill="{INK}"/>
{t(50, 32, "NOTES FROM A WORKBENCH", 15, INK, MONO, 500, ls=3)}
{t(600, 32, "ISSUE Nº 01", 15, INK, MONO, 500, anchor="middle", ls=3)}
{t(1150, 32, "TUNIS · 2026", 15, INK, MONO, 500, anchor="end", ls=3)}
<circle cx="1020" cy="200" r="104" fill="{VERM}"/>
<circle cx="1020" cy="200" r="132" fill="none" stroke="{INK}" stroke-width="1.5"/>
<g class="a1">{t(44, 318, "Oussama", 214, INK, SERIF, 400, ls=-7, extra='textLength="760" lengthAdjust="spacingAndGlyphs"')}</g>
<g class="a2">{t(250, 510, "Ben Henia", 214, INK, SERIF, 400, ls=-7, style="italic", extra='textLength="820" lengthAdjust="spacingAndGlyphs"')}
<circle cx="1100" cy="494" r="17" fill="{VERM}"/></g>
<g class="a3">
{t(50, 576, "NOW  —", 16, VERM, MONO, 700, ls=3)}
<g transform="translate(150 576)">{"".join(roles)}</g></g>
<line x1="60" y1="{line_y}" x2="1140" y2="{line_y}" stroke="{INK}" stroke-width="7" stroke-linecap="round"/>
{stations}
<g class="train"><g transform="translate(38 {line_y - 26})">
<rect width="44" height="22" fill="{VERM}"/><rect x="5" y="5" width="8" height="7" fill="{PAPER}"/><rect x="18" y="5" width="8" height="7" fill="{PAPER}"/><rect x="31" y="5" width="8" height="7" fill="{PAPER}"/>
<rect y="22" width="44" height="3" fill="{INK}"/></g></g>"""
    return svg(W, H, body, "Oussama Ben Henia",
               "Masthead of the profile: Oussama Ben Henia, " + "; ".join(ROLES) + ". A route diagram with four stations: About, Index, Work, Activity.",
               "".join(css))


# ================================================================ headers
def header(num, title, caption, flip=False):
    W, H = 1200, 200
    css = ("@keyframes d{from{transform:scaleX(0)}to{transform:scaleX(1)}}"
           ".rule{transform-origin:50px 0;animation:d 1.4s cubic-bezier(.6,0,.2,1) both}")
    if not flip:
        num_el = t(46, 170, num, 150, VERM, SERIF, 400, style="italic", ls=-4)
        title_el = t(300, 160, title, 104, INK, SERIF, 400, ls=-2)
        cap_el = t(1150, 84, caption, 15, MUTE, MONO, 500, anchor="end", ls=3)
        tab = f'<rect x="50" y="10" width="90" height="11" fill="{VERM}"/>'
    else:
        num_el = t(1154, 170, num, 150, VERM, SERIF, 400, anchor="end", style="italic", ls=-4)
        title_el = t(50, 160, title, 104, INK, SERIF, 400, ls=-2)
        cap_el = t(50, 84, caption, 15, MUTE, MONO, 500, ls=3)
        tab = f'<rect x="1060" y="10" width="90" height="11" fill="{VERM}"/>'
    body = f"""{paper(W, H, PAPER, False)}
<rect class="rule" x="50" y="14" width="1100" height="3" fill="{INK}"/>{tab}
{num_el}{title_el}{cap_el}"""
    return svg(W, H, body, title, caption, css)


# ================================================================ index
LEFT = [("Python", "04"), ("JavaScript", "04"), ("HTML & CSS", "04"), ("Local language models", "04"),
        ("Agents & tool calling", "04"), ("Desktop apps, pywebview", "04"), ("Desktop automation", "04")]
RIGHT = [("ESP32", "03"), ("PID control", "03"), ("Sensors & motors", "03"), ("Progressive web apps", "01"),
         ("Responsive web", "01"), ("Brand & product", "02"), ("Git, GitHub Actions", "—")]


def index():
    W, H = 1200, 600
    def col(x0, x1, title, rows, refcol):
        o = [t(x0, 56, title, 30, INK, SERIF, 400, style="italic"),
             f'<rect x="{x0}" y="74" width="{x1 - x0}" height="2" fill="{INK}"/>']
        for i, (name, ref) in enumerate(rows):
            y = 134 + i * 60
            wd = sum(23 if c.isupper() else 8.5 if c in ' ,' else 10 if c in '&.' else 16 for c in name)
            o.append(t(x0, y, name, 34, INK, SERIF, 400, extra=f'textLength="{wd:.0f}" lengthAdjust="spacingAndGlyphs"'))
            nx = x0 + wd + 16
            o.append(f'<line x1="{nx:.0f}" y1="{y - 7}" x2="{x1 - 56}" y2="{y - 7}" stroke="{INK}" stroke-opacity=".45" stroke-width="2.5" stroke-dasharray="0.1 9" stroke-linecap="round"/>')
            o.append(t(x1, y, ref, 24, refcol, MONO, 700, anchor="end"))
        return "".join(o)
    body = f"""{paper(W, H)}
{col(50, 640, "Software & intelligence", LEFT, VERM)}
{col(730, 1150, "Hardware, web & making", RIGHT, OLIVE)}
<line x1="685" y1="40" x2="685" y2="530" stroke="{INK}" stroke-width="1"/>
{t(50, 568, "FIGURES REFER TO PROJECTS ·  01 R3T  ·  02 PHYTO  ·  03 LINE FOLLOWER  ·  04 NEURAL AGENT", 14, MUTE, MONO, 500, ls=1.5)}"""
    names = ", ".join(n for n, _ in LEFT + RIGHT)
    return svg(W, H, body, "Index of tools", "Tools and skills, each with the project number where it was used: " + names)


# ================================================================ projects
def _kv(x, y, rows, fill, keyfill, size=16, gap=30):
    o = []
    for i, (k, v) in enumerate(rows):
        o.append(t(x, y + i * gap, k, size, keyfill, MONO, 700, ls=2))
        o.append(t(x + 130, y + i * gap, v, size, fill, MONO, 400))
    return "".join(o)


def project_r3t():
    W, H = 1200, 470
    VP = (905, 214)
    bl, br, by = 745, 1065, 456
    rails = "".join(f'<line x1="{x}" y1="{by}" x2="{VP[0]}" y2="{VP[1]}" stroke="{PAPER}" stroke-width="3.5"/>' for x in (bl, br))
    ties = []
    for k in range(0, 16):
        s = 1 - 0.8 ** k
        y = by + s * (VP[1] - by)
        xl, xr = bl + s * (VP[0] - bl), br + s * (VP[0] - br)
        ext = (xr - xl) * 0.16
        ties.append(f'<line x1="{xl - ext:.1f}" y1="{y:.1f}" x2="{xr + ext:.1f}" y2="{y:.1f}" stroke="{PAPER}" stroke-opacity=".65" stroke-width="{max(.8, 4 * (1 - s)):.1f}"/>')
    sx = [560, 730, 900, 1070]
    stations = "".join(f'<circle cx="{x}" cy="116" r="10" fill="{INK}" stroke="{PAPER}" stroke-width="3.5"/>' for x in sx)
    css = ("@keyframes go{0%{transform:translateX(0);opacity:0}10%{opacity:1}82%{opacity:1}100%{transform:translateX(340px);opacity:0}}"
           ".m{animation:go 11s cubic-bezier(.5,0,.5,1) infinite}")
    body = f"""{paper(W, H, INK)}
{t(50, 62, "Nº 01 — TRANSPORT", 16, VERM, MONO, 700, ls=3)}
{t(40, 262, "R3T", 230, PAPER, SANS, 700, ls=-14)}
{t(52, 322, "Real-time railway tracking", 32, SOFT, SERIF, 400, style="italic")}
{_kv(52, 384, [("FORMAT", "Progressive web app"), ("SURFACE", "Phone first"), ("STATUS", "Private repository")], PAPER, VERM)}
<line x1="560" y1="116" x2="900" y2="116" stroke="{PAPER}" stroke-width="6" stroke-linecap="round"/>
<line x1="900" y1="116" x2="1150" y2="116" stroke="{PAPER}" stroke-width="4" stroke-dasharray="0.1 12" stroke-linecap="round" stroke-opacity=".8"/>
{stations}
<circle class="m" cx="560" cy="116" r="9" fill="{VERM}"/>
{t(560, 170, "— LIVE POSITION", 15, SOFT, MONO, 500, ls=2)}{t(820, 168, "··· TIMETABLE ESTIMATE", 15, SOFT, MONO, 500, ls=2)}
{rails}{"".join(ties)}
<circle cx="{VP[0]}" cy="{VP[1]}" r="7" fill="{VERM}"/>"""
    return svg(W, H, body, "R3T: real-time railway tracking",
               "Project 01. R3T, a mobile-first progressive web app for real-time railway tracking. Private repository. Drawing: a route line showing live position against timetable estimate, above railway tracks in perspective.", css)


def leaf(scale=1.0):
    veins = "".join(f'<path d="M0 {y}L-20 {y - 18}M0 {y}L20 {y - 18}" fill="none" stroke-width="1.6"/>' for y in (30, 8, -14, -36))
    return (f'<g transform="scale({scale})"><path d="M0 62C-52 22 -48 -36 0 -72C48 -36 52 22 0 62Z"/>'
            f'<path d="M0 58V-64" fill="none" stroke-width="2.2"/>{veins}</g>')


def project_phyto():
    W, H = 1200, 520
    cx, cy = 940, 268
    ring = f"M{-168} 0a168 168 0 1 1 336 0a168 168 0 1 1 -336 0"
    css = ("@keyframes sp{to{transform:rotate(360deg)}}.spin{transform-origin:0 0;animation:sp 140s linear infinite}"
           "@keyframes br{50%{transform:translateY(-6px)}}.bob{animation:br 9s ease-in-out infinite}")
    sprig = ""
    for i, (x, y, rot, sc) in enumerate([(0, 0, 6, .55), (-26, -58, -38, .5), (28, -98, 36, .48), (-20, -146, -32, .44), (6, -190, 8, .4)]):
        sprig += f'<g transform="translate({x} {y}) rotate({rot})" fill="{OLIVE}" stroke="{KRAFT}" fill-opacity="{.95 - i * .08:.2f}">{leaf(sc)}</g>'
    body = f"""{paper(W, H, KRAFT)}
{t(50, 62, "Nº 02 — BEVERAGE BRAND", 16, VERM, MONO, 700, ls=3)}
{t(44, 262, "Phyto", 230, INK, SERIF, 400, ls=-8, extra='textLength="520" lengthAdjust="spacingAndGlyphs"')}
{t(50, 380, "Cappuccino", 120, OLIVE, SERIF, 400, ls=-3, style="italic", extra='textLength="560" lengthAdjust="spacingAndGlyphs"')}
{_kv(52, 446, [("FORMAT", "Product, identity, website"), ("STATUS", "Private repository")], INK, VERM)}
<g transform="translate({cx} {cy})">
 <g class="spin"><path id="rp" d="{ring}" fill="none"/>
  <text font-family="{MONO}" font-size="21" font-weight="700" fill="{INK}" letter-spacing="3"><textPath href="#rp" textLength="1040" lengthAdjust="spacingAndGlyphs">PHYTO · CAPPUCCINO · PHYTO · CAPPUCCINO · PHYTO · CAPPUCCINO ·</textPath></text></g>
 <circle r="198" fill="none" stroke="{INK}" stroke-width="1.5"/>
 <circle r="138" fill="{PAPER}" stroke="{INK}" stroke-width="3"/>
 <circle r="112" fill="#5B3520"/>
 <g class="bob"><g fill="{PAPER}" stroke="#5B3520">{leaf(1.05)}</g></g>
</g>
<circle cx="1120" cy="74" r="48" fill="{VERM}"/>{t(1120, 80, "Nº 02", 20, PAPER, MONO, 700, anchor="middle", ls=1)}
<path d="M700 520C704 440 692 380 702 300" fill="none" stroke="{OLIVE}" stroke-width="3"/>
<g transform="translate(704 470)">{sprig}</g>"""
    return svg(W, H, body, "PHYTO Cappuccino: beverage brand",
               "Project 02. PHYTO Cappuccino, my beverage brand: product, identity and website. Private repository. Drawing: a cappuccino seen from above with a leaf in the foam, inside a rotating wordmark seal.", css)


def project_robot():
    W, H = 1200, 480
    cx, cy = 735, 215
    grid = "".join(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}" stroke="{PAPER}" stroke-opacity=".10"/>' for x in range(0, W, 40)) + \
           "".join(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{PAPER}" stroke-opacity=".10"/>' for y in range(0, H, 40))
    path = "M440 400 C 560 400 600 330 700 330 S 840 410 960 410 S 1100 340 1190 340"
    css = ("@keyframes sw{0%,100%{transform:rotate(-3.5deg)}50%{transform:rotate(3.5deg)}}.sway{transform-origin:0 0;animation:sw 7s ease-in-out infinite}"
           "@keyframes fl{to{stroke-dashoffset:-60}}.track{animation:fl 6s linear infinite}")
    sensors = "".join(f'<circle cx="{x}" cy="-78" r="7" fill="{VERM}" stroke="{PAPER}" stroke-width="2"/>' for x in (-70, -35, 0, 35, 70))
    pins = "".join(f'<line x1="{x}" y1="-28" x2="{x}" y2="-38" stroke="{PAPER}" stroke-width="2"/><line x1="{x}" y1="28" x2="{x}" y2="38" stroke="{PAPER}" stroke-width="2"/>' for x in range(-40, 41, 16))
    body = f"""{paper(W, H, COBALT)}
{grid}
{t(50, 62, "Nº 03 — ROBOTICS", 16, PAPER, MONO, 700, ls=3)}
{t(46, 200, "Line", 150, PAPER, SANS, 700, ls=-8)}
{t(46, 330, "follower", 130, PAPER, SERIF, 400, ls=-4, style="italic")}
{_kv(52, 392, [("BOARD", "ESP32"), ("CONTROL", "PID, closed loop"), ("STATUS", "Robotics project")], PAPER, LAV)}
<path class="track" d="{path}" fill="none" stroke="{PAPER}" stroke-width="16" stroke-linecap="round" stroke-dasharray="46 14" stroke-opacity=".9"/>
<g transform="translate({cx} {cy}) scale(1.25)"><g class="sway">
 <rect x="-52" y="-72" width="104" height="144" fill="none" stroke="{PAPER}" stroke-width="2.5"/>
 <rect x="-82" y="-40" width="26" height="70" fill="{INK}" stroke="{PAPER}" stroke-width="2"/><rect x="56" y="-40" width="26" height="70" fill="{INK}" stroke="{PAPER}" stroke-width="2"/>
 <rect x="-34" y="-26" width="68" height="52" fill="none" stroke="{PAPER}" stroke-width="2"/>{pins}
 {t(0, 6, "ESP32", 15, PAPER, MONO, 700, anchor="middle", ls=1)}
 {sensors}
 <line x1="0" y1="-120" x2="0" y2="110" stroke="{PAPER}" stroke-width="1" stroke-dasharray="10 6 2 6" stroke-opacity=".8"/>
</g>
 <line x1="60" y1="-78" x2="170" y2="-130" stroke="{PAPER}" stroke-width="1.2"/><line x1="170" y1="-130" x2="330" y2="-130" stroke="{PAPER}" stroke-width="1.2"/>{t(176, -138, "sensor array", 16, PAPER, MONO, 500)}
 <line x1="82" y1="0" x2="170" y2="30" stroke="{PAPER}" stroke-width="1.2"/><line x1="170" y1="30" x2="330" y2="30" stroke="{PAPER}" stroke-width="1.2"/>{t(176, 22, "motor + wheel", 16, PAPER, MONO, 500)}
</g>
{t(440, 456, "u(t) = Kp·e(t) + Ki·∫e dt + Kd·de/dt", 20, PAPER, MONO, 500)}"""
    return svg(W, H, body, "ESP32 line-follower robot",
               "Project 03. A line-following robot with an ESP32, a sensor array, motors and PID control. Drawing: top-view technical sketch with callouts and the PID equation.", css)


def project_neural():
    W, H = 1200, 400
    log = [("opens apps and websites", True), ("reads and writes files", True), ("reports CPU, memory, disk", True), ("asks before typing", False)]
    css = ""
    rows = []
    for i, (txt, ok) in enumerate(log):
        y = 156 + i * 56
        css += f".g{i}{{opacity:0;animation:sh .01s {0.6 + i * 0.9:.1f}s forwards}}"
        mark = (f'<polyline points="760,{y - 8} 770,{y + 2} 788,{y - 20}" fill="none" stroke="{OLIVE}" stroke-width="4" stroke-linecap="square"/>' if ok
                else t(762, y + 2, "?", 28, VERM, MONO, 700))
        rows.append(f'<g class="g{i}">{mark}{t(808, y, txt, 22, INK, MONO, 400)}</g>')
    css += "@keyframes sh{to{opacity:1}}@media (prefers-reduced-motion: reduce){[class^=g]{opacity:1!important}}"
    body = f"""{paper(W, H)}
<rect x="720" y="0" width="480" height="{H}" fill="{LAV}"/><rect x="720" y="0" width="480" height="{H}" filter="url(#grain)"/>
{t(50, 62, "Nº 04 — OPEN SOURCE", 16, VERM, MONO, 700, ls=3)}
{t(44, 172, "Neural", 124, INK, SERIF, 400, ls=-4, extra='textLength="400" lengthAdjust="spacingAndGlyphs"')}
{t(44, 278, "Agent", 124, INK, SERIF, 400, ls=-4, style="italic", extra='textLength="310" lengthAdjust="spacingAndGlyphs"')}
{t(50, 340, "A Windows assistant that runs on local models. No cloud, no API key.", 21, MUTE, SERIF, 400, style="italic")}
{t(50, 376, "PYTHON · OLLAMA · PYWEBVIEW   —   PUBLIC REPOSITORY", 14, INK, MONO, 700, ls=2)}
{t(760, 74, "IT CAN", 15, INK, MONO, 700, ls=3)}
<rect x="760" y="88" width="390" height="2" fill="{INK}"/>
{"".join(rows)}"""
    return svg(W, H, body, "Neural Agent",
               "Project 04. Neural Agent, a Windows desktop assistant built on local Ollama models. Public repository. It opens apps and websites, reads and writes files, reports system status, and asks before typing.", css)


# ================================================================ stats
def render_stats(d=None):
    """d: dict(repos, commits, prs, langs=[(name, pct)], updated) or None (placeholder)."""
    W, H = 1200, 470
    pending = d is None
    cols = [(50, "repos", "Public repositories", VERM), (440, "commits", "Contributions, last year", INK), (830, "prs", "Pull requests", OLIVE)]
    o = []
    for x, key, lab, col in cols:
        v = "—" if pending else (f"{d[key]:02d}" if d[key] < 100 else str(d[key]))
        o.append(f'<rect x="{x}" y="40" width="320" height="3" fill="{INK}"/>')
        o.append(t(x - 4, 190, v, 168, col, SERIF, 400, ls=-6))
        o.append(t(x, 228, lab.upper(), 15, MUTE, MONO, 700, ls=2.5))
    if pending:
        o.append(t(50, 360, "Live numbers appear after the first run of .github/workflows/stats.yml", 20, MUTE, MONO, 400))
    else:
        o.append(t(50, 290, "LANGUAGES IN PUBLIC REPOSITORIES, SET IN PROPORTION", 15, MUTE, MONO, 700, ls=2.5))
        x, cols_ = 50, [VERM, INK, OLIVE, COBALT, MUTE]
        for i, (n, p) in enumerate(d["langs"][:5]):
            size = 30 + p * 1.05
            o.append(t(x, 400, n, round(size), cols_[i % 5], SERIF, 400, style="italic" if i % 2 else "normal", ls=-1))
            w = len(n) * size * 0.5
            o.append(t(x + 2, 428, f"{p:.0f}%", 15, MUTE, MONO, 700))
            x += w + 56
    foot = "Placeholder, not yet generated" if pending else f"Source: GitHub API · updated {d['updated']}"
    body = f"""{paper(W, H)}{"".join(o)}{t(1150, 450, foot, 13, MUTE, MONO, 400, anchor="end")}"""
    return svg(W, H, body, "GitHub activity",
               "Public repositories, contributions over the last year, pull requests, and language mix, from the GitHub API."
               + ("" if pending else f" {d['repos']} repositories, {d['commits']} contributions, {d['prs']} pull requests. Languages: "
                  + ", ".join(f"{n} {p:.0f}%" for n, p in d["langs"][:5]) + "."))


# ================================================================ footer
def footer():
    W, H = 1200, 170
    css = "@keyframes sl{from{transform:translateX(-80px)}to{transform:translateX(1200px)}}.tr{animation:sl 40s linear infinite}"
    ties = "".join(f'<line x1="{x}" y1="52" x2="{x}" y2="70" stroke="{INK}" stroke-width="2"/>' for x in range(0, W + 1, 24))
    body = f"""{paper(W, H, PAPER, False)}{ties}
<line x1="0" y1="56" x2="{W}" y2="56" stroke="{INK}" stroke-width="3"/><line x1="0" y1="66" x2="{W}" y2="66" stroke="{INK}" stroke-width="3"/>
<g class="tr"><rect x="0" y="30" width="40" height="20" fill="{VERM}"/><rect x="5" y="35" width="8" height="6" fill="{PAPER}"/><rect x="17" y="35" width="8" height="6" fill="{PAPER}"/><rect x="29" y="35" width="6" height="6" fill="{PAPER}"/></g>
{t(50, 126, "COLOPHON", 14, VERM, MONO, 700, ls=3)}
{t(50, 150, "Set in your system's serif, sans and mono. Every drawing is generated from scripts/build_assets.py. Tunis, 2026.", 15, MUTE, MONO, 400)}"""
    return svg(W, H, body, "Colophon", "Colophon: all drawings are generated by a script; Tunis, 2026.", css)


# ================================================================ main
def main():
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.svg"):
        old.unlink()
    files = {
        "masthead.svg": masthead(),
        "h-about.svg": header("01", "About", "WHO · WHERE"),
        "h-index.svg": header("02", "Index", "WHAT I HAVE USED", flip=True),
        "h-work.svg": header("03", "Work", "FOUR PROJECTS"),
        "h-activity.svg": header("04", "Activity", "FROM THE GITHUB API", flip=True),
        "index.svg": index(),
        "project-r3t.svg": project_r3t(),
        "project-phyto.svg": project_phyto(),
        "project-robot.svg": project_robot(),
        "project-neural.svg": project_neural(),
        "footer.svg": footer(),
    }
    cache = OUT / "stats.json"  # written by generate_stats.py from the GitHub API
    files["stats.svg"] = render_stats(json.loads(cache.read_text()) if cache.exists() else None)
    for n, c in files.items():
        (OUT / n).write_text(c, encoding="utf-8")
    print(f"wrote {len(files)} files to {OUT}")


if __name__ == "__main__":
    main()
