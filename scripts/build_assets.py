#!/usr/bin/env python3
"""Generates every SVG in assets/ (pure stdlib, deterministic).

    python scripts/build_assets.py

DESIGN SYSTEM  ("the page is a railway line")
  Canvas      1000 units wide for every asset; margins 50; one 16px gutter between images (from Markdown).
  Two kinds   PLATES are opaque printed sheets (masthead + four projects).
              SECTIONS (headers, index, stats, footer) are transparent and come in a light and a dark
              variant (README switches them with #gh-light-mode-only / #gh-dark-mode-only), so they sit
              on the page instead of leaving blocks and gaps.
  Palette     paper / ink / vermilion; olive, cobalt, lavender, kraft belong to one project each.
  Type        three voices only: serif (voice, titles), Swiss sans (engineering wordmarks), mono (metadata).
              Smallest meaningful text is 18 units, which stays legible when GitHub scales to a phone.
  Texture     speckle pattern, halftone dots, hairline frames with corner ticks. No filters, no glow.
  Motion      CSS-in-SVG, slow, off under prefers-reduced-motion; every asset is complete when still.
"""
import json
import math
import random
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"
W = 1000

INK, PAPER, KRAFT = "#1B1814", "#F3ECDD", "#E6D2AB"
VERM, OLIVE, COBALT, LAV = "#D9441F", "#5E6B38", "#27479A", "#BDAED0"
OLIVE2, COFFEE = "#7E8E4D", "#5B3520"
VERM_TXT, VERM_ON_INK = "#B03410", "#F0643C"  # text-safe vermilions (contrast >= 4.5 on paper/kraft, on ink)
MUTE, SOFT = "#675F52", "#CFC6B2"

SERIF = "'Iowan Old Style','Palatino Linotype',Palatino,'Book Antiqua','Charter','Bitstream Charter',Georgia,serif"
SANS = "'Helvetica Neue',Helvetica,'Arial Nova',Arial,'Inter',sans-serif"
MONO = "ui-monospace,'SF Mono',Menlo,Consolas,'Liberation Mono','DejaVu Sans Mono',monospace"

# palettes for transparent sections
LIGHT = dict(fg=INK, mute=MUTE, verm=VERM, olive=OLIVE, cobalt=COBALT, rule=INK, window=PAPER)
DARK = dict(fg=PAPER, mute="#AFA896", verm="#F0643C", olive="#AAB878", cobalt="#8FA6E8", rule=PAPER, window="#0D1117")

REDUCED = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"


# ------------------------------------------------------------------ helpers
def svg(w, h, body, title, desc, css="", defs=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-labelledby="t d"><title id="t">{escape(title)}</title>'
        f'<desc id="d">{escape(desc)}</desc><style>{css}{REDUCED}</style><defs>{defs}</defs>{body}</svg>\n'
    )


def t(x, y, s, size, fill=INK, family=SANS, weight=400, anchor="start", ls=0, style="", extra=""):
    fs = f' font-style="{style}"' if style else ""
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}" letter-spacing="{ls}"{fs} {extra}>{escape(s)}</text>')


def fit(x, y, s, size, tl, fill=INK, family=SERIF, weight=400, ls=0, style="", extra=""):
    """Display text with a fixed width (textLength) so layout survives font substitution."""
    return t(x, y, s, size, fill, family, weight, ls=ls, style=style,
             extra=f'textLength="{tl}" lengthAdjust="spacingAndGlyphs" {extra}')


def speckle(pid, color, op=1.0, seed=3, n=46, tile=140):
    """Print-style paper speckle as a tiny repeating pattern (safe everywhere, unlike filters)."""
    r = random.Random(seed)
    dots = "".join(
        f'<circle cx="{r.uniform(0, tile):.1f}" cy="{r.uniform(0, tile):.1f}" r="{r.choice([.5, .7, .9, 1.2, 1.6]):.1f}" '
        f'fill="{color}" fill-opacity="{r.uniform(.06, .2) * op:.2f}"/>' for _ in range(n))
    return f'<pattern id="{pid}" width="{tile}" height="{tile}" patternUnits="userSpaceOnUse">{dots}</pattern>'


def plate_bg(w, h, fill, color, op=1.0, pid="sp"):
    return (speckle(pid, color, op),
            f'<rect width="{w}" height="{h}" fill="{fill}"/><rect width="{w}" height="{h}" fill="url(#{pid})"/>')


def frame(w, h, color, m=16, op=.55):
    """Hairline plate frame with corner ticks."""
    a = 24
    ticks = "".join(f'<path d="M{x} {y + dy * a}V{y}H{x + dx * a}" fill="none"/>'
                    for x, y, dx, dy in [(m, m, 1, 1), (w - m, m, -1, 1), (m, h - m, 1, -1), (w - m, h - m, -1, -1)])
    return (f'<rect x="{m}" y="{m}" width="{w - 2 * m}" height="{h - 2 * m}" fill="none" stroke="{color}" stroke-opacity="{op}" stroke-width="1"/>'
            f'<g stroke="{color}" stroke-width="3" stroke-opacity=".9">{ticks}</g>')


def rails(x0, x1, y, color, gap=12, tie=16, lw=2.5):
    o = [f'<line x1="{x0}" y1="{y - gap / 2}" x2="{x1}" y2="{y - gap / 2}" stroke="{color}" stroke-width="{lw}"/>',
         f'<line x1="{x0}" y1="{y + gap / 2}" x2="{x1}" y2="{y + gap / 2}" stroke="{color}" stroke-width="{lw}"/>']
    x = x0 + tie / 2
    while x < x1:
        o.append(f'<line x1="{x:.1f}" y1="{y - gap / 2 - 5}" x2="{x:.1f}" y2="{y + gap / 2 + 5}" stroke="{color}" stroke-width="1.6" stroke-opacity=".55"/>')
        x += tie
    return "".join(o)


def train(color, window, wheel, x=0, y=0, s=1.0):
    return (f'<g transform="translate({x} {y}) scale({s})"><rect width="64" height="26" fill="{color}"/>'
            f'<rect x="6" y="6" width="9" height="9" fill="{window}"/><rect x="20" y="6" width="9" height="9" fill="{window}"/>'
            f'<rect x="34" y="6" width="9" height="9" fill="{window}"/><rect x="48" y="6" width="10" height="9" fill="{window}"/>'
            f'<rect y="19" width="64" height="3" fill="{wheel}" fill-opacity=".35"/>'
            f'<circle cx="12" cy="29" r="4.5" fill="{wheel}"/><circle cx="52" cy="29" r="4.5" fill="{wheel}"/></g>')


# ============================================================== masthead (plate)
ROLES = ["engineering student at ENIT", "software developer", "builder of AI agents",
         "robotics tinkerer, ESP32", "founder of PHYTO Cappuccino"]
STATIONS = [(70, "01 ABOUT", "start"), (357, "02 INDEX", "middle"), (643, "03 WORK", "middle"), (930, "04 ACTIVITY", "end")]


def masthead():
    H = 730
    cycle = 25.0
    css = [".r{opacity:0}.r0{opacity:1}"]
    roles = []
    for k, role in enumerate(ROLES):
        a, b = k * 20, k * 20 + 20
        kf = (f"0%,17%{{opacity:1}}20%,97.5%{{opacity:0}}100%{{opacity:1}}" if k == 0
              else f"0%,{a}%{{opacity:0}}{a + 2.5}%,{b - 3}%{{opacity:1}}{b}%,100%{{opacity:0}}")
        css.append(f"@keyframes r{k}{{{kf}}}.r{k}{{animation:r{k} {cycle:.0f}s ease-in-out infinite}}")
        roles.append(t(0, 0, role, 36, INK, SERIF, 400, style="italic", extra=f'class="r r{k}"'))
    css.append("@keyframes run{0%,8%{transform:translateX(0)}28%,36%{transform:translateX(287px)}"
               "56%,64%{transform:translateX(573px)}84%,100%{transform:translateX(860px)}}"
               ".train{animation:run 32s cubic-bezier(.6,0,.4,1) infinite alternate}"
               "@keyframes rise{from{transform:translateY(14px)}to{transform:none}}"
               ".a1{animation:rise 1.1s .1s cubic-bezier(.2,.7,.2,1) both}.a2{animation:rise 1.1s .3s cubic-bezier(.2,.7,.2,1) both}"
               ".a3{animation:rise 1.1s .5s cubic-bezier(.2,.7,.2,1) both}")
    # halftone shading on the disc
    cx, cy, R = 800, 238, 138
    dots = []
    for gx in range(cx - R, cx + R + 1, 13):
        for gy in range(cy - R, cy + R + 1, 13):
            if math.hypot(gx - cx, gy - cy) > R - 3:
                continue
            tt = ((gx - cx) + (gy - cy)) / (2 * R)
            rr = max(0, tt - 0.05) * 9
            if rr > .6:
                dots.append(f'<circle cx="{gx}" cy="{gy}" r="{rr:.1f}"/>')
    ln = 650
    stations = "".join(
        f'<circle cx="{x}" cy="{ln}" r="15" fill="{PAPER}" stroke="{INK}" stroke-width="5"/>'
        + t(x, ln + 52, lab, 20, INK, MONO, 700, anchor=anc, ls=2.5) for x, lab, anc in STATIONS)
    d, bg = plate_bg(W, H, PAPER, INK)
    body = f"""{bg}
{frame(W, H, INK)}
{t(50, 64, "NOTES FROM A WORKBENCH", 20, INK, MONO, 700, ls=3)}{t(500, 64, "ISSUE Nº 01", 20, INK, MONO, 700, anchor="middle", ls=3)}{t(950, 64, "TUNIS · 2026", 20, INK, MONO, 700, anchor="end", ls=3)}
<rect x="50" y="78" width="900" height="4" fill="{INK}"/><rect x="50" y="87" width="900" height="1.5" fill="{INK}"/>
<clipPath id="disc"><circle cx="{cx}" cy="{cy}" r="{R}"/></clipPath>
<circle cx="{cx}" cy="{cy}" r="{R}" fill="{VERM}"/>
<g clip-path="url(#disc)" fill="{INK}" fill-opacity=".82">{"".join(dots)}</g>
<circle cx="{cx + 14}" cy="{cy + 14}" r="{R}" fill="none" stroke="{INK}" stroke-width="2"/>
<g class="a1">{fit(44, 342, "Oussama", 176, 625, INK, SERIF, 400, ls=-6)}</g>
<g class="a2">{fit(176, 512, "Ben Henia", 176, 674, INK, SERIF, 400, ls=-6, style="italic")}<circle cx="878" cy="498" r="14" fill="{VERM}"/></g>
<g class="a3">{t(50, 566, "NOW", 20, VERM_TXT, MONO, 700, ls=3)}<g transform="translate(124 566)">{"".join(roles)}</g></g>
{rails(70, 930, ln, INK)}
{stations}
<g class="train">{train(VERM, PAPER, INK, 38, ln - 50)}</g>"""
    return svg(W, H, body, "Oussama Ben Henia",
               "Masthead: Oussama Ben Henia, " + "; ".join(ROLES) + ". A route diagram with four stations: About, Index, Work, Activity.",
               "".join(css), d)


# ============================================================== sections (transparent, two modes)
def header(num, title, caption, flip, P):
    H = 220
    css = ""
    sx = 950 if flip else 50
    num_el = (t(956, 190, num, 150, P["verm"], SERIF, 400, anchor="end", style="italic", ls=-4) if flip
              else t(44, 190, num, 150, P["verm"], SERIF, 400, style="italic", ls=-4))
    title_el = t(50, 178, title, 104, P["fg"], SERIF, 400, ls=-2) if flip else t(300, 178, title, 104, P["fg"], SERIF, 400, ls=-2)
    cap_el = t(50, 80, caption, 20, P["mute"], MONO, 700, ls=3) if flip else t(950, 80, caption, 20, P["mute"], MONO, 700, anchor="end", ls=3)
    body = f"""{rails(50, 950, 34, P["rule"], gap=8, tie=14, lw=2.2)}
<circle cx="{sx}" cy="34" r="13" fill="{P["verm"]}" stroke="{P["fg"]}" stroke-width="4"/>
{num_el}{title_el}{cap_el}"""
    return svg(W, H, body, title, caption, css)


LEFT = [("Python", "04"), ("JavaScript", "04"), ("HTML & CSS", "04"), ("Local language models", "04"),
        ("Agents & tool calling", "04"), ("Desktop apps, pywebview", "04"), ("Desktop automation", "04")]
RIGHT = [("ESP32", "03"), ("PID control", "03"), ("Sensors & motors", "03"), ("Progressive web apps", "01"),
         ("Responsive web", "01"), ("Brand & product", "02"), ("Git, GitHub Actions", "—")]


def index(P):
    H = 650

    def col(x0, x1, title, rows, refcol):
        o = [t(x0, 56, title, 32, P["fg"], SERIF, 400, style="italic"),
             f'<rect x="{x0}" y="76" width="{x1 - x0}" height="2.5" fill="{P["rule"]}"/>']
        for i, (name, ref) in enumerate(rows):
            y = 142 + i * 62
            wd = sum(21 if c.isupper() else 7.5 if c in " ," else 9 if c in "&." else 14.6 for c in name)
            o.append(fit(x0, y, name, 31, f"{wd:.0f}", P["fg"], SERIF))
            o.append(f'<line x1="{x0 + wd + 14:.0f}" y1="{y - 7}" x2="{x1 - 46}" y2="{y - 7}" stroke="{P["fg"]}" stroke-opacity=".5" stroke-width="2.6" stroke-dasharray="0.1 9" stroke-linecap="round"/>')
            o.append(t(x1, y, ref, 24, refcol, MONO, 700, anchor="end"))
        return "".join(o)

    legend = "".join(t(x, 612, f"{n}  {name}", 20, P["mute"], MONO, 700, ls=1.5)
                     for x, n, name in [(50, "01", "R3T"), (185, "02", "PHYTO"), (347, "03", "LINE FOLLOWER"), (617, "04", "NEURAL AGENT")])
    body = f"""{col(50, 478, "Software & intelligence", LEFT, P["verm"])}
{col(522, 950, "Hardware, web & making", RIGHT, P["olive"])}
<line x1="500" y1="40" x2="500" y2="570" stroke="{P["fg"]}" stroke-opacity=".5"/>
<rect x="50" y="582" width="900" height="1.5" fill="{P["fg"]}" fill-opacity=".5"/>{legend}"""
    names = ", ".join(n for n, _ in LEFT + RIGHT)
    return svg(W, H, body, "Index of tools", "Tools and skills with the project number where each was used (01 R3T, 02 PHYTO, 03 Line follower, 04 Neural Agent): " + names)


def render_stats(d=None, P=LIGHT):
    """d: dict(repos, commits, prs, langs=[(name, pct)], updated) or None (placeholder)."""
    H = 516
    pending = d is None
    cols = [(50, "repos", ("PUBLIC", "REPOSITORIES"), P["verm"]), (370, "commits", ("CONTRIBUTIONS", "LAST 12 MONTHS"), P["fg"]),
            (690, "prs", ("PULL", "REQUESTS"), P["olive"])]
    o = []
    for x, key, lab, col in cols:
        v = "—" if pending else (f"{d[key]:02d}" if d[key] < 100 else str(d[key]))
        o.append(f'<rect x="{x}" y="30" width="260" height="3" fill="{P["rule"]}"/>')
        o.append(t(x - 4, 196, v, 160, col, SERIF, 400, ls=-6))
        o.append(t(x, 236, lab[0], 20, P["mute"], MONO, 700, ls=2) + t(x, 262, lab[1], 20, P["mute"], MONO, 700, ls=2))
    if pending:
        o.append(t(50, 380, "Live numbers appear after the first run of .github/workflows/stats.yml", 20, P["mute"], MONO, 400))
    else:
        o.append(t(50, 322, "LANGUAGES IN PUBLIC REPOSITORIES, SET IN PROPORTION", 20, P["mute"], MONO, 700, ls=2))
        x, cs = 50, [P["verm"], P["fg"], P["olive"], P["cobalt"], P["mute"]]
        for i, (n, p) in enumerate(d["langs"][:5]):
            size = round(30 + p * 1.0)
            o.append(t(x, 430, n, size, cs[i % 5], SERIF, 400, style="italic" if i % 2 else "normal", ls=-1))
            o.append(t(x + 2, 466, f"{p:.0f}%", 20, P["mute"], MONO, 700))
            x += len(n) * size * 0.5 + 46
    foot = "Placeholder, not yet generated" if pending else f"Source: GitHub API · updated {d['updated']}"
    body = "".join(o) + t(950, 498, foot, 18, P["mute"], MONO, 400, anchor="end")
    return svg(W, H, body, "GitHub activity",
               "Public repositories, contributions over the last year, pull requests, and language mix, from the GitHub API."
               + ("" if pending else f" {d['repos']} repositories, {d['commits']} contributions, {d['prs']} pull requests. Languages: "
                  + ", ".join(f"{n} {p:.0f}%" for n, p in d["langs"][:5]) + "."))


def footer(P):
    H = 220
    css = "@keyframes sl{from{transform:translateX(-90px)}to{transform:translateX(1000px)}}.tr{animation:sl 44s linear infinite}"
    body = f"""{rails(50, 950, 70, P["rule"], gap=12, tie=16)}
<g class="tr">{train(P["verm"], P["window"], P["fg"], 0, 24)}</g>
{t(50, 140, "COLOPHON", 20, P["verm"], MONO, 700, ls=3)}
{t(50, 170, "Set in your system's serif, sans and mono.", 20, P["mute"], MONO, 400)}
{t(50, 198, "Every drawing is generated by scripts/build_assets.py. Tunis, 2026.", 20, P["mute"], MONO, 400)}"""
    return svg(W, H, body, "Colophon", "Colophon: all drawings are generated by a script; Tunis, 2026.", css)


# ============================================================== project plates
def label(x, y, num, cat, color):
    return t(x, y, f"Nº {num} — {cat}", 20, color, MONO, 700, ls=3)


def kv(x, y, rows, vfill, kfill, gap=38, size=20, kw=128):
    return "".join(t(x, y + i * gap, k, size - 2, kfill, MONO, 700, ls=2) + t(x + kw, y + i * gap, v, size, vfill, MONO, 400)
                   for i, (k, v) in enumerate(rows))


# ---------------------------------------------------------------- R3T
def project_r3t():
    H = 620
    defs, bg = plate_bg(W, H, INK, PAPER, .8, "sp1")
    defs += (f'<pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.1" fill="{PAPER}" fill-opacity=".16"/></pattern>'
             '<clipPath id="chart"><rect x="480" y="324" width="470" height="196"/></clipPath>')
    # network map: orthogonal + 45 degree geometry (transit-map language)
    full = "M440 196 H560 L610 146 H770 L820 196 H930"
    live = "M440 196 H560 L610 146 H770"
    st = [(440, 196, "t+0", "b"), (610, 146, "t+12", "t"), (770, 146, "t+31", "t"), (862, 196, "t+47", "b"), (936, 196, "t+58", "b")]
    nodes = ""
    for i, (x, y, lab, side) in enumerate(st):
        ly = y + (-28 if side == "t" else 42)
        if i == 2:  # interchange
            nodes += f'<circle cx="{x}" cy="{y}" r="17" fill="{INK}" stroke="{PAPER}" stroke-width="3"/><circle cx="{x}" cy="{y}" r="8" fill="{PAPER}"/>'
        else:
            nodes += f'<circle cx="{x}" cy="{y}" r="10" fill="{INK}" stroke="{PAPER}" stroke-width="4"/>'
        nodes += t(x, ly, lab, 20, SOFT, MONO, 700, anchor="middle")
    css = ("@keyframes dr{0%{stroke-dashoffset:100}70%,100%{stroke-dashoffset:0}}"
           "@keyframes mv{0%{offset-distance:0%;opacity:0}6%{opacity:1}70%{offset-distance:100%;opacity:1}94%{offset-distance:100%;opacity:1}100%{offset-distance:100%;opacity:0}}"
           ".live{stroke-dasharray:100;animation:dr 12s cubic-bezier(.5,0,.4,1) infinite}"
           ".m{transform:translate(770px,146px)}"
           f"@supports (offset-path: path('M0 0')){{.m{{transform:none;offset-path:path('{live}');offset-rotate:0deg;animation:mv 12s cubic-bezier(.5,0,.4,1) infinite}}}}"
           "@media (prefers-reduced-motion: reduce){.live{stroke-dashoffset:0}.m{offset-path:none!important;transform:translate(770px,146px)!important;opacity:1!important}}")
    # Marey (time-distance) chart: stations vs time
    rows_y = [490, 430, 370, 330]
    grid = "".join(f'<line x1="480" y1="{y}" x2="950" y2="{y}" stroke="{PAPER}" stroke-opacity=".28"/>' for y in rows_y)
    grid += "".join(f'<line x1="{x}" y1="324" x2="{x}" y2="{520 if (x - 480) % 94 == 0 else 514}" stroke="{PAPER}" stroke-opacity=".14"/>' for x in range(480, 951, 47))
    labs = "".join(t(466, y + 6, f"S{4 - i}", 20, SOFT, MONO, 700, anchor="end") for i, y in enumerate(rows_y))

    def sched(dx):
        pts = [(500, 490), (556, 490), (640, 430), (676, 430), (760, 370), (796, 370), (880, 330)]
        return "M" + " L".join(f"{x + dx} {y}" for x, y in pts)
    sched_lines = "".join(f'<path d="{sched(dx)}" fill="none" stroke="{PAPER}" stroke-opacity="{op}" stroke-width="1.8"/>' for dx, op in [(0, .55), (96, .4), (192, .28)])
    live_path = "M" + " L".join(f"{x} {y}" for x, y in [(500, 490), (556, 490), (652, 430), (698, 430), (790, 370)])
    delta = (f'<path d="M760 370H790M760 360V380M790 360V380" stroke="{PAPER}" stroke-width="2" fill="none"/>'
             + t(775, 348, "Δt", 22, PAPER, SERIF, 400, anchor="middle", style="italic"))
    body = f"""{bg}<rect x="400" y="0" width="600" height="{H}" fill="url(#dots)"/>
{frame(W, H, PAPER)}
{label(50, 70, "01", "TRANSPORT", VERM_ON_INK)}
{t(40, 306, "R3T", 196, PAPER, SANS, 700, ls=-10)}
{t(52, 366, "Real-time railway tracking", 30, SOFT, SERIF, 400, style="italic")}
{kv(52, 448, [("FORMAT", "Progressive web app"), ("SURFACE", "Phone first"), ("STATUS", "Private repository")], PAPER, VERM_ON_INK)}
<path d="{full}" fill="none" stroke="{PAPER}" stroke-opacity=".7" stroke-width="5" stroke-dasharray="0.1 11" stroke-linecap="round"/>
<path class="live" pathLength="100" d="{live}" fill="none" stroke="{VERM}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>
{nodes}
<g class="m"><circle r="15" fill="{PAPER}"/><circle r="8" fill="{VERM}"/></g>
{t(440, 270, "━ LIVE POSITION", 20, SOFT, MONO, 700, ls=1)}{t(690, 270, "┅ TIMETABLE ESTIMATE", 20, SOFT, MONO, 700, ls=1)}
<g>{grid}{labs}</g>
<g clip-path="url(#chart)">{sched_lines}</g>
<path d="{live_path}" fill="none" stroke="{VERM}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
<circle cx="790" cy="370" r="7" fill="{VERM}" stroke="{PAPER}" stroke-width="2.5"/>
{delta}
{t(950, 546, "TIME →", 20, SOFT, MONO, 700, anchor="end", ls=2)}{t(480, 580, "FIG. 01 · LIVE VS TIMETABLE", 20, SOFT, MONO, 700, ls=2)}
{t(950, 70, "01 / 04", 20, SOFT, MONO, 700, anchor="end", ls=2)}"""
    return svg(W, H, body, "R3T: real-time railway tracking",
               "Project 01. R3T, a phone-first progressive web app for real-time railway tracking. Private repository. Drawing: a transit-style route map with a live position against the timetable estimate, and a time-distance chart where the live train line drifts from the scheduled paths.",
               css, defs)


# ---------------------------------------------------------------- PHYTO
def leaf(L, Wd, light, dark, rib):
    """Pointed ovate leaf, base at origin, tip at (0,-L). Left half lighter (two-tone), midrib + veins."""
    half = f"M0 0C{Wd * .55:.1f} {-L * .22:.1f} {Wd * .5:.1f} {-L * .72:.1f} 0 {-L}"
    body = (f'<path d="{half}C{-Wd * .5:.1f} {-L * .72:.1f} {-Wd * .55:.1f} {-L * .22:.1f} 0 0Z" fill="{dark}"/>'
            f'<path d="{half}L0 0Z" fill="{light}" fill-opacity=".9"/>'
            f'<path d="M0 {L * .04:.1f}V{-L * .96:.1f}" fill="none" stroke="{rib}" stroke-width="2.4" stroke-linecap="round"/>')
    veins = ""
    for i in range(1, 6):
        y = -L * (.12 + i * .15)
        spread = Wd * .36 * (1 - i * .13)
        veins += (f'<path d="M0 {y:.1f}Q{spread * .6:.1f} {y - 6:.1f} {spread:.1f} {y - 22:.1f}M0 {y:.1f}Q{-spread * .6:.1f} {y - 6:.1f} {-spread:.1f} {y - 22:.1f}" '
                  f'fill="none" stroke="{rib}" stroke-width="1.3" stroke-opacity=".75"/>')
    return body + veins


def project_phyto():
    H = 620
    defs, bg = plate_bg(W, H, KRAFT, "#6B4A1E", 1.1, "sp2")
    P0, P1, P2 = (600, 588), (640, 285), (892, 128)

    def B(tv):
        return ((1 - tv) ** 2 * P0[0] + 2 * (1 - tv) * tv * P1[0] + tv ** 2 * P2[0],
                (1 - tv) ** 2 * P0[1] + 2 * (1 - tv) * tv * P1[1] + tv ** 2 * P2[1])

    def ang(tv):
        dx = 2 * (1 - tv) * (P1[0] - P0[0]) + 2 * tv * (P2[0] - P1[0])
        dy = 2 * (1 - tv) * (P1[1] - P0[1]) + 2 * tv * (P2[1] - P1[1])
        return math.degrees(math.atan2(dy, dx))
    stem = f'<path d="M{P0[0]} {P0[1]}Q{P1[0]} {P1[1]} {P2[0]} {P2[1]}" fill="none" stroke="{COFFEE}" stroke-width="7" stroke-linecap="round"/>'
    leaves, cherries = [], []
    for k, tv in enumerate([.16, .31, .46, .61, .76]):
        x, y = B(tv)
        a = ang(tv)
        L = 138 - k * 13
        for sgn in (-1, 1):
            leaves.append(f'<g transform="translate({x:.1f} {y:.1f}) rotate({a + sgn * 62 + 90:.1f})">{leaf(L, L * .5, OLIVE2, OLIVE, KRAFT)}</g>')
        if k in (1, 3):
            for dx, dy in [(-14, 16), (8, 24), (22, 8)]:
                cherries.append(f'<path d="M{x:.0f} {y:.0f}Q{x + dx * .4:.0f} {y + dy * .2:.0f} {x + dx:.0f} {y + dy:.0f}" fill="none" stroke="{COFFEE}" stroke-width="2.5"/>'
                                f'<circle cx="{x + dx:.0f}" cy="{y + dy + 12:.0f}" r="15" fill="{VERM}"/><circle cx="{x + dx - 5:.0f}" cy="{y + dy + 7:.0f}" r="4.5" fill="{PAPER}" fill-opacity=".55"/>'
                                f'<circle cx="{x + dx:.0f}" cy="{y + dy - 1:.0f}" r="3.5" fill="{COFFEE}"/>')
    tip = f'<g transform="translate({P2[0]} {P2[1]}) rotate({ang(1) + 90:.1f})">{leaf(84, 42, OLIVE2, OLIVE, KRAFT)}</g>'
    cup = f"""<g transform="translate(842 470)">
<circle r="92" fill="{PAPER}" stroke="{INK}" stroke-width="1.5"/><circle r="82" fill="none" stroke="{INK}" stroke-opacity=".35"/>
<circle r="62" fill="{PAPER}" stroke="{INK}" stroke-width="2.5"/><circle r="50" fill="{COFFEE}"/>
<g transform="rotate(-18)"><path d="M0 34C-26 12 -24 -14 0 -34C24 -14 26 12 0 34Z" fill="{PAPER}" fill-opacity=".92"/><path d="M0 30V-28" stroke="{COFFEE}" stroke-width="2" fill="none"/>
<path d="M0 12L-12 2M0 12L12 2M0 -2L-11 -12M0 -2L11 -12M0 -16L-8 -23M0 -16L8 -23" stroke="{COFFEE}" stroke-width="1.5" fill="none"/></g>
<path d="M62 -10C96 -22 98 22 62 12" fill="none" stroke="{INK}" stroke-width="2.5"/></g>"""
    css = "@keyframes sw{50%{transform:rotate(1.2deg)}}.bough{transform-origin:600px 588px;animation:sw 12s ease-in-out infinite}"
    body = f"""{bg}
<circle cx="730" cy="322" r="226" fill="{PAPER}" fill-opacity=".72"/>
<circle cx="742" cy="334" r="226" fill="none" stroke="{INK}" stroke-width="1.5"/>
<g class="bough">{stem}{"".join(leaves)}{tip}{"".join(cherries)}</g>
{cup}
{frame(W, H, INK)}
{label(50, 70, "02", "BEVERAGE BRAND", VERM_TXT)}
{fit(44, 292, "Phyto", 196, 443, INK, SERIF, 400, ls=-8)}
{fit(50, 396, "Cappuccino", 100, 462, OLIVE, SERIF, 400, ls=-3, style="italic")}
{kv(52, 470, [("FORMAT", "Product, identity, web"), ("STATUS", "Private repository")], INK, VERM_TXT)}
{t(950, 70, "02 / 04", 20, INK, MONO, 700, anchor="end", ls=2)}"""
    return svg(W, H, body, "PHYTO Cappuccino: beverage brand",
               "Project 02. PHYTO Cappuccino, my beverage brand: product, identity and website. Private repository. Drawing: a coffee branch with leaves and red cherries beside a cappuccino seen from above, on kraft paper.",
               css, defs)


# ---------------------------------------------------------------- robot
def project_robot():
    H = 620
    defs, bg = plate_bg(W, H, COBALT, PAPER, .9, "sp3")
    grid = "".join(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}" stroke="{PAPER}" stroke-opacity="{.2 if x % 200 == 0 else .09}"/>' for x in range(0, W + 1, 40))
    grid += "".join(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{PAPER}" stroke-opacity="{.2 if y % 200 == 0 else .09}"/>' for y in range(0, H + 1, 40))
    line = "M640 366V16"
    css = "@keyframes bm{to{stroke-dashoffset:-14}}.beam{animation:bm 1.6s linear infinite}"
    s, ox, oy, P = 1.5, 600, 232, PAPER
    sens = "".join(
        f'<rect x="{x - 8}" y="-98" width="16" height="14" fill="{COBALT}" stroke="{P}" stroke-width="2"/><circle cx="{x}" cy="-91" r="4" fill="{VERM}"/>'
        f'<line x1="{x}" y1="-102" x2="{x}" y2="-118" stroke="{P}" stroke-width="1.6" stroke-dasharray="3 4" class="beam"/>' for x in (-48, -24, 0, 24, 48))
    pins = "".join(f'<rect x="-19" y="{y}" width="4" height="4" fill="{P}"/><rect x="15" y="{y}" width="4" height="4" fill="{P}"/>' for y in range(-56, -8, 7))
    meander = f'<path d="M-14 -54H14V-58H-10V-62H14V-66H-10" fill="none" stroke="{P}" stroke-width="1.6"/>'
    robot = f"""<g transform="translate({ox} {oy}) scale({s})">
<polygon points="-62,-78 -44,-80 44,-80 62,-78 62,82 -62,82" fill="#1F3B86" stroke="{P}" stroke-width="2.2"/>
{sens}
<path d="M-48 -84V-70H48V-84M-36 -70V-38H-20" fill="none" stroke="{P}" stroke-width="1.5"/>
<rect x="-20" y="-64" width="40" height="62" fill="{INK}" fill-opacity=".55" stroke="{P}" stroke-width="2"/>
<rect x="-12" y="-50" width="24" height="26" fill="none" stroke="{P}" stroke-width="1.5"/>{pins}{meander}
<rect x="-6" y="-8" width="12" height="8" fill="none" stroke="{P}" stroke-width="1.6"/>
<rect x="-26" y="6" width="52" height="26" fill="none" stroke="{P}" stroke-width="2"/><path d="M-18 14H18M-18 22H18" stroke="{P}" stroke-width="1.4"/>
<path d="M-26 20H-40M26 20H40M0 6V0" stroke="{P}" stroke-width="1.5" fill="none"/>
<rect x="-30" y="42" width="60" height="28" fill="none" stroke="{P}" stroke-width="2"/><path d="M-22 56H22M0 42V32" stroke="{P}" stroke-width="1.4" fill="none"/>
<rect x="-62" y="26" width="22" height="46" fill="none" stroke="{P}" stroke-width="2"/><rect x="40" y="26" width="22" height="46" fill="none" stroke="{P}" stroke-width="2"/>
<rect x="-80" y="22" width="20" height="68" fill="{INK}" stroke="{P}" stroke-width="2"/><rect x="60" y="22" width="20" height="68" fill="{INK}" stroke="{P}" stroke-width="2"/>
<line x1="0" y1="-128" x2="0" y2="104" stroke="{P}" stroke-width="1" stroke-dasharray="14 5 3 5" stroke-opacity=".8"/>
</g>"""

    def G(lx, ly):
        return ox + lx * s, oy + ly * s

    def callout(lx, ly, text, ty):
        ax, ay = G(lx, ly)
        return (f'<circle cx="{ax:.0f}" cy="{ay:.0f}" r="3.5" fill="{P}"/><polyline points="{ax:.0f},{ay:.0f} {ax + 40:.0f},{ty} 760,{ty}" fill="none" stroke="{P}" stroke-width="1.3"/>'
                + t(770, ty + 6, text, 20, P, MONO, 700))
    calls = (callout(48, -91, "sensor array", 104) + callout(20, -40, "ESP32 board", 168) +
             callout(26, 19, "motor driver", 232) + callout(80, 60, "motor + wheel", 296))
    ax0, ax1 = G(-80, 0)[0], G(80, 0)[0]
    dim = (f'<path d="M{ax0:.0f} 384H{ax1:.0f}M{ax0:.0f} 376V392M{ax1:.0f} 376V392" stroke="{P}" stroke-width="1.3" fill="none"/>'
           + t((ax0 + ax1) / 2, 410, "wheel track", 20, P, MONO, 700, anchor="middle"))
    by = 482

    def blk(x, w_, lab, y=by):
        return f'<rect x="{x}" y="{y - 24}" width="{w_}" height="48" fill="none" stroke="{P}" stroke-width="2"/>' + t(x + w_ / 2, y + 6, lab, 20, P, MONO, 700, anchor="middle")

    def arr(x1, x2):
        return f'<line x1="{x1}" y1="{by}" x2="{x2 - 8}" y2="{by}" stroke="{P}" stroke-width="1.8"/><path d="M{x2 - 10} {by - 6}L{x2} {by}L{x2 - 10} {by + 6}" fill="{P}"/>'
    pid = (t(404, by - 30, "r(t)", 20, SOFT, MONO, 700, anchor="middle") + t(490, by - 30, "e(t)", 20, SOFT, MONO, 700, anchor="middle") + t(590, by - 30, "u(t)", 20, SOFT, MONO, 700, anchor="middle")
           + f'<circle cx="452" cy="{by}" r="16" fill="none" stroke="{P}" stroke-width="2"/><path d="M441 {by + 11}L463 {by - 11}M441 {by - 11}L463 {by + 11}" stroke="{P}" stroke-width="1.5"/>'
           + arr(420, 436) + arr(468, 500) + blk(500, 74, "PID") + arr(574, 606) + blk(606, 108, "MOTORS") + arr(714, 746) + blk(746, 90, "ROBOT")
           + f'<path d="M836 {by}H880V{by + 52}H640" fill="none" stroke="{P}" stroke-width="1.8"/>' + blk(540, 100, "SENSORS", by + 52)
           + f'<path d="M540 {by + 52}H452V{by + 24}" fill="none" stroke="{P}" stroke-width="1.8"/><path d="M446 {by + 32}L452 {by + 20}L458 {by + 32}" fill="{P}"/>')
    body = f"""{bg}{grid}
{frame(W, H, P)}
{label(50, 70, "03", "ROBOTICS", SOFT)}
{t(46, 220, "Line", 150, P, SANS, 700, ls=-8)}
{t(46, 340, "follower", 124, P, SERIF, 400, ls=-4, style="italic")}
{kv(52, 412, [("BOARD", "ESP32"), ("CONTROL", "PID, closed loop"), ("STATUS", "Robotics project")], P, SOFT)}
{t(52, 560, "DWG Nº 03 · NOT TO SCALE", 20, SOFT, MONO, 700, ls=2)}
<path d="{line}" fill="none" stroke="{P}" stroke-width="16" stroke-opacity=".92"/>
{robot}{calls}{dim}{pid}
{t(420, 590, "u(t) = Kp·e(t) + Ki·∫e dt + Kd·de/dt", 20, P, MONO, 700)}
{t(950, 70, "03 / 04", 20, SOFT, MONO, 700, anchor="end", ls=2)}"""
    return svg(W, H, body, "ESP32 line-follower robot",
               "Project 03. A line-following robot built on an ESP32 with a sensor array, a motor driver, two DC motors and PID control. Drawing: a blueprint-style top view with labelled parts, a wheel-track dimension, and the feedback loop from sensors through PID and motors back to the error signal.",
               css, defs)


# ---------------------------------------------------------------- Neural Agent
def project_neural():
    H = 500
    defs, bg = plate_bg(W, H, PAPER, INK, 1, "sp4")
    defs += speckle("sp5", INK, 1.2, seed=9)
    log = [("opens apps and websites", True), ("reads and writes files", True), ("reports system status", True), ("asks before typing", False)]
    css, rows = "", []
    for i, (txt, ok) in enumerate(log):
        y = 190 + i * 62
        mark = (f'<polyline points="620,{y - 8} 632,{y + 5} 654,{y - 22}" fill="none" stroke="{OLIVE}" stroke-width="5" stroke-linecap="square"/>' if ok
                else t(622, y + 6, "?", 34, VERM, MONO, 700))
        rows.append(f'<g>{mark}{t(672, y, txt, 20, INK, MONO, 400)}</g>'
                    f'<line x1="620" y1="{y + 24}" x2="950" y2="{y + 24}" stroke="{INK}" stroke-opacity=".25"/>')
    body = f"""{bg}
<rect x="560" y="0" width="440" height="{H}" fill="{LAV}"/><rect x="560" y="0" width="440" height="{H}" fill="url(#sp5)"/>
{frame(W, H, INK)}
{label(50, 70, "04", "OPEN SOURCE", VERM_TXT)}
{fit(44, 216, "Neural", 118, 381, INK, SERIF, 400, ls=-4)}
{fit(44, 326, "Agent", 118, 295, INK, SERIF, 400, ls=-4, style="italic")}
{t(50, 384, "A Windows assistant that runs on local models.", 24, MUTE, SERIF, 400, style="italic")}
{t(50, 414, "No cloud, no API key.", 24, MUTE, SERIF, 400, style="italic")}
{t(50, 452, "PYTHON · OLLAMA · PYWEBVIEW", 20, INK, MONO, 700, ls=2)}
{t(620, 112, "IT CAN", 20, INK, MONO, 700, ls=3)}<rect x="620" y="128" width="330" height="3" fill="{INK}"/>
{"".join(rows)}
{t(950, 70, "04 / 04", 20, INK, MONO, 700, anchor="end", ls=2)}{t(620, 452, "PUBLIC REPOSITORY", 20, INK, MONO, 700, ls=2)}"""
    return svg(W, H, body, "Neural Agent",
               "Project 04. Neural Agent, a Windows desktop assistant built on local Ollama models. Public repository. It opens apps and websites, reads and writes files, reports system status, and asks before typing.",
               css, defs)


# ============================================================== main
def main():
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.svg"):
        old.unlink()
    cache = OUT / "stats.json"
    stats = json.loads(cache.read_text()) if cache.exists() else None
    files = {"masthead.svg": masthead(), "project-r3t.svg": project_r3t(), "project-phyto.svg": project_phyto(),
             "project-robot.svg": project_robot(), "project-neural.svg": project_neural()}
    for mode, P in (("light", LIGHT), ("dark", DARK)):
        files[f"h-about-{mode}.svg"] = header("01", "About", "WHO · WHERE", False, P)
        files[f"h-index-{mode}.svg"] = header("02", "Index", "WHAT I HAVE USED", True, P)
        files[f"h-work-{mode}.svg"] = header("03", "Work", "FOUR PROJECTS", False, P)
        files[f"h-activity-{mode}.svg"] = header("04", "Activity", "FROM THE GITHUB API", True, P)
        files[f"index-{mode}.svg"] = index(P)
        files[f"stats-{mode}.svg"] = render_stats(stats, P)
        files[f"footer-{mode}.svg"] = footer(P)
    for n, c in files.items():
        (OUT / n).write_text(c, encoding="utf-8")
    print(f"wrote {len(files)} files to {OUT}")


if __name__ == "__main__":
    main()
