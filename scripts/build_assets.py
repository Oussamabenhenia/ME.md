#!/usr/bin/env python3
"""Generates every SVG in assets/ (pure stdlib, deterministic).

Usage:  python scripts/build_assets.py

All animation is CSS-in-SVG (no JavaScript) and is disabled under
`prefers-reduced-motion`. Every SVG paints its own dark panel, so contrast
is identical in GitHub light and dark mode.
"""
import json
import math
import re
import random
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"

CYAN, PURPLE, MAGENTA = "#00E5FF", "#8B5CF6", "#EC4899"
BLUE, GREEN, GOLD, NAVY = "#3B82F6", "#10B981", "#FBBF24", "#080B1A"
PANEL, TEXT, MUTED = "#0E1330", "#E6EAF7", "#9AA4C7"
SANS = "'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
MONO = "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"

REDUCED = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"


def svg(w, h, body, title, desc, css=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-labelledby="t d"><title id="t">{escape(title)}</title>'
        f'<desc id="d">{escape(desc)}</desc><style>{css}{REDUCED}</style>{body}</svg>\n'
    )


def grad(id_, stops, x2="1", y2="0"):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return f'<linearGradient id="{id_}" x1="0" y1="0" x2="{x2}" y2="{y2}">{s}</linearGradient>'


BRAND = [("0", CYAN), ("0.4", BLUE), ("0.7", PURPLE), ("1", MAGENTA)]


def ribbon(w, h, cy, amp, half, lines, phase_shift=0.0):
    """Twisting mesh ribbon like the reference art: many sine lines whose
    amplitude sweeps +a -> -a, drawn over >= 3 periods so a one-period
    translation loops seamlessly."""
    out = []
    period = half * 2
    x0 = -period + phase_shift
    n = int((w + 3 * period) / half) + 2
    for i in range(lines):
        t = i / (lines - 1)
        a = amp * math.cos(math.pi * t)
        y = cy + (t - 0.5) * amp * 0.9
        d = f"M{x0:.1f} {y:.1f}"
        for k in range(n):
            sign = -1 if k % 2 == 0 else 1
            x1 = x0 + (k + 1) * half
            if k == 0:
                d += f"Q{x0 + half / 2:.1f} {y + sign * a * 2:.1f} {x1:.1f} {y:.1f}"
            else:
                d += f"T{x1:.1f} {y:.1f}"
        op = 0.25 + 0.55 * (1 - abs(2 * t - 1))
        out.append(f'<path d="{d}" opacity="{op:.2f}"/>')
    return "".join(out), period


# ---------------------------------------------------------------- hero
ROLES = [
    "Engineering student @ ENIT",
    "Software developer",
    "AI agents & automation",
    "Robotics builder (ESP32)",
    "Founder of PHYTO Cappuccino",
]


def hero():
    W, H = 1200, 460
    rnd = random.Random(7)
    stars = []
    for i in range(28):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        r = rnd.choice([0.8, 1.1, 1.6, 2.2])
        c = rnd.choice([CYAN, CYAN, BLUE, PURPLE, MAGENTA, "#FFFFFF"])
        stars.append(
            f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{c}" class="st" '
            f'style="animation-delay:{rnd.uniform(0, 6):.1f}s;animation-duration:{rnd.uniform(3, 7):.1f}s"/>'
        )
    # constellation lines between nearby stars
    pts = [(rnd.uniform(0, W), rnd.uniform(0, H)) for _ in range(12)]
    lines = []
    for i, (x, y) in enumerate(pts):
        for (x2, y2) in pts[i + 1:]:
            if math.hypot(x - x2, y - y2) < 260:
                lines.append(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x2:.0f}" y2="{y2:.0f}"/>')
        lines.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="2.4" fill="{CYAN}" stroke="none"/>')

    r1, p1 = ribbon(W, H, 392, 52, 150, 28)
    r2, p2 = ribbon(W, H, 410, 34, 110, 20, phase_shift=40)

    # typing animation: one cycle = len(ROLES) slots
    slot = 4.0
    total = slot * len(ROLES)
    CW = 15.6  # px per monospace char at 26px
    css = [
        ".st{animation:tw 4s ease-in-out infinite}@keyframes tw{0%,100%{opacity:.15}50%{opacity:1}}",
        f".w1{{animation:d1 {p1 / 20:.0f}s linear infinite}}@keyframes d1{{to{{transform:translateX(-{int(p1)}px)}}}}",
        f".w2{{animation:d2 {p2 / 14:.0f}s linear infinite reverse}}@keyframes d2{{to{{transform:translateX(-{int(p2)}px)}}}}",
        ".hi{animation:rise 1.2s ease-out both}.hi2{animation:rise 1.2s .35s ease-out both}"
        "@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}",
        ".blink{animation:bl 1s steps(1) infinite}@keyframes bl{50%{opacity:0}}",
        ".glow{animation:gl 5s ease-in-out infinite}@keyframes gl{50%{opacity:.75}}",
    ]
    typing = []
    cu_keys = []
    for k, role in enumerate(ROLES):
        n = len(role)
        a = k * slot / total * 100
        b = (k * slot + 1.6) / total * 100
        c = (k * slot + 3.4) / total * 100
        e = (k + 1) * slot / total * 100
        wpx = n * CW
        css.append(
            f"#c{k}{{width:{wpx if k == 0 else 0:.0f}px;animation:ty{k} {total:.0f}s infinite}}"
            f"@keyframes ty{k}{{0%,{a:.2f}%{{width:0;animation-timing-function:steps({n},end)}}"
            f"{b:.2f}%,{c:.2f}%{{width:{wpx:.0f}px;animation-timing-function:step-end}}"
            f"{e:.2f}%,100%{{width:0}}}}"
        )
        cu_keys.append(
            f"{a:.2f}%{{transform:translateX(0);animation-timing-function:steps({n},end)}}"
            f"{b:.2f}%,{c:.2f}%{{transform:translateX({wpx:.0f}px);animation-timing-function:step-end}}"
            f"{e - 0.01:.2f}%{{transform:translateX({wpx:.0f}px)}}"
        )
        typing.append(
            f'<clipPath id="cp{k}"><rect id="c{k}" x="0" y="-30" height="44"/></clipPath>'
            f'<text x="0" y="0" font-family="{MONO}" font-size="26" fill="{TEXT}" clip-path="url(#cp{k})">{escape(role)}</text>'
        )
    css.append(f"#cur{{transform:translateX({len(ROLES[0]) * CW:.0f}px);animation:cu {total:.0f}s infinite}}"
               f"@keyframes cu{{0%{{transform:translateX(0)}}{''.join(cu_keys)}100%{{transform:translateX(0)}}}}")
    typing.append(f'<g id="cur"><rect class="blink" x="2" y="-26" width="12" height="30" fill="{CYAN}"/></g>')

    body = f"""
<defs>
  {grad("bg", [("0", "#05060F"), ("0.5", NAVY), ("1", "#120A28")], "1", "1")}
  {grad("brand", BRAND)}
  <linearGradient id="wg" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="0">
    <stop offset="0" stop-color="{CYAN}"/><stop offset="0.45" stop-color="{BLUE}"/>
    <stop offset="0.75" stop-color="{PURPLE}"/><stop offset="1" stop-color="{MAGENTA}"/></linearGradient>
  <pattern id="grid" width="48" height="48" patternUnits="userSpaceOnUse">
    <path d="M48 0H0V48" fill="none" stroke="#1B2350" stroke-width="1" opacity=".55"/></pattern>
  <filter id="blur" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="9"/></filter>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="22"/></clipPath>
  {"".join(re.findall(r"<clipPath.*?</clipPath>", "".join(typing)))}
</defs>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" fill="url(#grid)"/>
  <g stroke="{BLUE}" stroke-width=".8" opacity=".22" fill="none">{"".join(lines)}</g>
  {"".join(stars)}
  <g fill="none" stroke="url(#wg)" stroke-width="1.1" opacity=".8">
    <g class="w1">{r1}</g>
  </g>
  <g fill="none" stroke="url(#wg)" stroke-width=".9" opacity=".7"><g class="w2">{r2}</g></g>
  <rect y="{H - 170}" width="{W}" height="170" fill="url(#bg)" opacity=".0"/>

  <text x="70" y="86" font-family="{MONO}" font-size="17" fill="{MUTED}" letter-spacing="3" class="hi">ENIT · TUNIS · SOFTWARE · EMBEDDED · AI</text>
  <g class="hi2">
    <text x="66" y="232" font-family="{SANS}" font-size="78" font-weight="700" fill="#F4F6FF" letter-spacing="-1">Oussama Ben Henia</text>
    <rect x="70" y="256" width="120" height="5" rx="2.5" fill="url(#brand)"/>
  </g>
  <g transform="translate(70 318)" font-family="{MONO}">
    <text x="0" y="0" font-size="26" fill="{CYAN}">&gt;</text>
    <g transform="translate(30 0)">{re.sub(r"<clipPath.*?</clipPath>", "", "".join(typing))}</g>
  </g>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="21" fill="none" stroke="url(#brand)" stroke-width="2" opacity=".8"/>
</g>"""
    return svg(
        W, H, body, "Oussama Ben Henia",
        "Animated banner: Oussama Ben Henia, engineering student at ENIT, with rotating roles: "
        + ", ".join(ROLES), "".join(css),
    )


# ------------------------------------------------------------ headers
def header(label, sub):
    W, H = 1200, 80
    body = f"""
<defs>{grad("g", BRAND)}</defs>
<text x="4" y="46" font-family="{SANS}" font-size="38" font-weight="700" fill="{TEXT}">{escape(label)}</text>
<text x="{26 + len(label) * 21}" y="46" font-family="{SANS}" font-size="20" fill="{MUTED}">{escape(sub)}</text>
<rect x="4" y="64" width="1192" height="3" rx="1.5" fill="url(#g)" opacity=".85"/>"""
    return svg(W, H, f'<rect width="{W}" height="{H}" fill="{NAVY}" rx="10"/>' + body, label, sub)


# -------------------------------------------------------------- about
def about_terminal():
    W, H = 1200, 330
    lines = [
        ("$", "whoami", TEXT),
        ("", "oussama-ben-henia", CYAN),
        ("$", "cat education.txt", TEXT),
        ("", "École Nationale d'Ingénieurs de Tunis (ENIT), engineering cycle", MUTED),
        ("$", "ls projects/", TEXT),
        ("", "r3t/   phyto-cappuccino/   line-follower/   neural-agent/", MUTED),
        ("$", "cat interests.txt", TEXT),
        ("", "software · local AI agents · embedded control · building a business", MUTED),
    ]
    out, css = [], []
    for i, (pre, txt, col) in enumerate(lines):
        y = 92 + i * 30
        delay = 0.4 + i * 0.55
        css.append(f".l{i}{{opacity:0;animation:sh .01s {delay:.2f}s forwards}}")
        out.append(
            f'<g class="l{i}"><text x="40" y="{y}" font-family="{MONO}" font-size="20" fill="{GREEN}">{pre}</text>'
            f'<text x="66" y="{y}" font-family="{MONO}" font-size="20" fill="{col}" xml:space="preserve">{escape(txt)}</text></g>'
        )
    css.append("@keyframes sh{to{opacity:1}}.cur{animation:bl 1s steps(1) infinite}@keyframes bl{50%{opacity:0}}"
               "@media (prefers-reduced-motion: reduce){[class^=l]{opacity:1!important}}")
    body = f"""
<defs>{grad("g", BRAND)}</defs>
<rect width="{W}" height="{H}" rx="16" fill="{NAVY}" stroke="url(#g)" stroke-width="2"/>
<rect width="{W}" height="44" rx="16" fill="{PANEL}"/><rect y="28" width="{W}" height="16" fill="{PANEL}"/>
<circle cx="30" cy="22" r="7" fill="{MAGENTA}"/><circle cx="54" cy="22" r="7" fill="{GOLD}"/><circle cx="78" cy="22" r="7" fill="{GREEN}"/>
<text x="600" y="28" text-anchor="middle" font-family="{MONO}" font-size="16" fill="{MUTED}">oussama@enit: ~</text>
{"".join(out)}
<rect class="cur" x="66" y="{92 + len(lines) * 30 - 18}" width="11" height="20" fill="{CYAN}"/>"""
    return svg(W, H, body, "About me, terminal style", "Engineering student at ENIT building software, AI agents, robots and a beverage brand.", "".join(css))


def pillars():
    W, H = 1200, 190
    items = [
        ("Engineering", "Maths & systems thinking", CYAN, "∑"),
        ("AI", "Local agents & automation", PURPLE, "◈"),
        ("Robotics", "ESP32 · sensors · PID", MAGENTA, "⚙"),
        ("Venture", "PHYTO Cappuccino", GOLD, "★"),
    ]
    cw = 285
    out, css = [], []
    for i, (t, s, c, ic) in enumerate(items):
        x = i * (cw + 20)
        css.append(f".p{i}{{animation:fl 6s ease-in-out {i * 0.7}s infinite}}")
        out.append(
            f'<g transform="translate({x} 0)"><g class="p{i}"><rect width="{cw}" height="{H - 10}" rx="16" fill="{PANEL}" stroke="{c}" stroke-opacity=".7" stroke-width="2"/>'
            f'<text x="26" y="66" font-family="{SANS}" font-size="44" fill="{c}">{ic}</text>'
            f'<text x="26" y="112" font-family="{SANS}" font-size="30" font-weight="700" fill="{TEXT}">{t}</text>'
            f'<text x="26" y="146" font-family="{SANS}" font-size="19" fill="{MUTED}">{escape(s)}</text></g></g>'
        )
    css.append("@keyframes fl{50%{transform:translateY(-4px)}}")
    return svg(W, H, "".join(out), "Four pillars", "Engineering, AI, robotics, and entrepreneurship.", "".join(css).replace(".p0{", ".p0{", 1))


# --------------------------------------------------------------- tech
TECH = [
    ("Languages", CYAN, ["Python", "JavaScript", "HTML / CSS"]),
    ("Web & apps", BLUE, ["PWA", "Responsive UI", "Desktop apps (pywebview)"]),
    ("AI & automation", PURPLE, ["Ollama · local LLMs", "AI agents / tool calling", "PyAutoGUI"]),
    ("Robotics & embedded", MAGENTA, ["ESP32", "PID control", "Sensors & motors"]),
    ("Workflow", GREEN, ["Git & GitHub", "GitHub Actions", "AI-assisted development"]),
]


def tech():
    W = 1200
    rowh = 78
    H = len(TECH) * rowh + 10
    out = []
    for r, (cat, col, items) in enumerate(TECH):
        y = r * rowh
        out.append(f'<rect y="{y}" width="{W}" height="{rowh - 12}" rx="14" fill="{PANEL}"/>'
                   f'<rect y="{y}" width="8" height="{rowh - 12}" rx="4" fill="{col}"/>'
                   f'<text x="30" y="{y + 40}" font-family="{SANS}" font-size="22" font-weight="700" fill="{col}">{escape(cat)}</text>')
        x = 290
        for it in items:
            w = 28 + len(it) * 12.5
            out.append(f'<rect x="{x:.0f}" y="{y + 12}" width="{w:.0f}" height="40" rx="20" fill="{col}" fill-opacity=".12" stroke="{col}" stroke-opacity=".8"/>'
                       f'<text x="{x + w / 2:.0f}" y="{y + 38}" text-anchor="middle" font-family="{SANS}" font-size="19" fill="{TEXT}">{escape(it)}</text>')
            x += w + 14
    return svg(W, H, "".join(out), "Technology stack",
               "; ".join(f"{c}: {', '.join(i)}" for c, _, i in TECH))


# ----------------------------------------------------------- projects
PROJECTS = [
    ("r3t", "R3T", "Real-time railway tracking", CYAN, BLUE,
     "Tracks trains in real time, built as a mobile-friendly PWA.",
     ["PWA", "Real-time", "Mobile-first"], "PRIVATE REPOSITORY"),
    ("phyto", "PHYTO Cappuccino", "Beverage brand & website", GOLD, MAGENTA,
     "My beverage brand: the product, the identity and the website.",
     ["Brand", "Web", "Startup"], "PRIVATE REPOSITORY"),
    ("robot", "ESP32 Line-Follower", "Robotics · control systems", GREEN, CYAN,
     "Follows a line using a sensor array, motor control and PID.",
     ["ESP32", "PID", "Sensors"], "ROBOTICS PROJECT"),
    ("neural", "Neural Agent", "Local AI desktop assistant", PURPLE, MAGENTA,
     "Windows assistant on local Ollama models: chat, files, PC actions.",
     ["Python", "Ollama", "pywebview"], "PUBLIC REPOSITORY"),
]


def project(slug, name, kind, c1, c2, desc, tags, status):
    W, H = 1200, 250
    chips, x = [], 44
    for t in tags:
        w = 30 + len(t) * 12
        chips.append(f'<rect x="{x}" y="186" width="{w}" height="36" rx="18" fill="{c1}" fill-opacity=".14" stroke="{c1}" stroke-opacity=".8"/>'
                     f'<text x="{x + w / 2}" y="210" text-anchor="middle" font-family="{MONO}" font-size="17" fill="{TEXT}">{escape(t)}</text>')
        x += w + 12
    hint = "Open details" if slug != "neural" else "Open details · repo"
    body = f"""
<defs>{grad("g", [("0", c1), ("1", c2)], "0", "1")}
<linearGradient id="p" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#121842"/><stop offset="1" stop-color="{PANEL}"/></linearGradient>
<linearGradient id="hl" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{c1}" stop-opacity=".9"/><stop offset=".6" stop-color="{c2}" stop-opacity=".25"/><stop offset="1" stop-color="{c2}" stop-opacity="0"/></linearGradient>
<radialGradient id="gl" cx="1" cy="0" r="1"><stop offset="0" stop-color="{c2}" stop-opacity=".22"/><stop offset="1" stop-color="{c2}" stop-opacity="0"/></radialGradient>
<clipPath id="f"><rect width="{W}" height="{H}" rx="16"/></clipPath></defs>
<g clip-path="url(#f)">
<rect width="{W}" height="{H}" fill="url(#p)"/>
<rect width="{W}" height="{H}" fill="url(#gl)"/>
<rect width="{W}" height="2" fill="url(#hl)"/>
<rect width="7" height="{H}" fill="url(#g)"/></g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="16" fill="none" stroke="#2A3270" stroke-opacity=".9"/>
<text x="44" y="56" font-family="{MONO}" font-size="16" fill="{c1}" letter-spacing="2.5">{escape(status)}</text>
<text x="44" y="114" font-family="{SANS}" font-size="50" font-weight="700" fill="{TEXT}" letter-spacing="-.5">{escape(name)}</text>
<text x="44" y="148" font-family="{SANS}" font-size="23" fill="{c1}">{escape(kind)}</text>
<text x="44" y="178" font-family="{SANS}" font-size="21" fill="{MUTED}">{escape(desc)}</text>
{"".join(chips)}
<text x="{W - 44}" y="{H - 28}" text-anchor="end" font-family="{MONO}" font-size="16" fill="{MUTED}" letter-spacing="1">{hint}  ▾</text>"""
    css = ""
    return svg(W, H, body, f"{name}: {kind}", f"{desc} Status: {status}.", css)


# ---------------------------------------------------------------- nav
NAV = [("about", "About", CYAN), ("stack", "Stack", BLUE), ("projects", "Projects", PURPLE),
       ("activity", "Activity", MAGENTA)]


def nav(label, c):
    W, H = 220, 56
    body = f"""<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#151B48"/><stop offset="1" stop-color="{PANEL}"/></linearGradient></defs>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="28" fill="url(#g)" stroke="{c}" stroke-opacity=".55" stroke-width="1.5"/>
<circle cx="38" cy="28" r="5" fill="{c}"/>
<text x="60" y="35" font-family="{SANS}" font-size="22" font-weight="600" fill="{TEXT}">{escape(label)}</text>"""
    return svg(W, H, body, label, f"Jump to the {label} section")


# -------------------------------------------------------------- stats
def render_stats(d=None):
    """d: dict(repos, followers, commits, prs, issues, since, langs=[(name, pct)]) or None."""
    W, H = 1200, 360
    pending = d is None
    nums = [("Public repos", "repos", CYAN), ("Contributions (last year)", "commits", PURPLE),
            ("Pull requests", "prs", MAGENTA), ("Top language", "top", GOLD)]
    out = []
    for i, (lab, key, c) in enumerate(nums):
        x, y = 40 + (i % 2) * 290, 126 + (i // 2) * 105
        if pending:
            v = "—"
        elif key == "top":
            v = d["langs"][0][0] if d["langs"] else "—"
        else:
            v = f"{d[key]:,}"
        out.append(f'<rect x="{x}" y="{y - 52}" width="270" height="90" rx="14" fill="{NAVY}" stroke="{c}" stroke-opacity=".6"/>'
                   f'<text x="{x + 20}" y="{y + 8}" font-family="{SANS}" font-size="{44 if len(str(v)) < 9 else 34}" font-weight="800" fill="{c}">{v}</text>'
                   f'<text x="{x + 20}" y="{y + 30}" font-family="{SANS}" font-size="16" fill="{MUTED}">{escape(lab)}</text>')
    langs = [] if pending else d["langs"][:6]
    pal = [CYAN, PURPLE, MAGENTA, BLUE, GREEN, GOLD]
    if pending:
        out.append(f'<text x="700" y="150" font-family="{MONO}" font-size="20" fill="{MUTED}">Live numbers appear after the first run of</text>'
                   f'<text x="700" y="180" font-family="{MONO}" font-size="20" fill="{CYAN}">.github/workflows/stats.yml</text>')
    else:
        out.append(f'<text x="640" y="86" font-family="{SANS}" font-size="22" font-weight="700" fill="{TEXT}">Languages (public repositories)</text>')
        for i, (n, p) in enumerate(langs):
            y = 112 + i * 38
            out.append(f'<text x="640" y="{y + 16}" font-family="{SANS}" font-size="18" fill="{TEXT}">{escape(n)}</text>'
                       f'<rect x="780" y="{y}" width="340" height="14" rx="7" fill="{NAVY}"/>'
                       f'<rect x="780" y="{y}" width="{max(6, 340 * p / 100):.0f}" height="14" rx="7" fill="{pal[i % 6]}"/>'
                       f'<text x="1130" y="{y + 14}" font-family="{MONO}" font-size="16" fill="{MUTED}">{p:.0f}%</text>')
    foot = "Placeholder: not yet generated" if pending else f"Source: GitHub API · updated {d['updated']}"
    body = f"""<defs>{grad("g", BRAND)}</defs>
<rect width="{W}" height="{H}" rx="18" fill="{PANEL}" stroke="url(#g)" stroke-width="2"/>
<text x="40" y="44" font-family="{SANS}" font-size="22" font-weight="700" fill="{TEXT}">GitHub activity</text>
{"".join(out)}
<text x="40" y="{H - 18}" font-family="{MONO}" font-size="14" fill="{MUTED}">{escape(foot)}</text>"""
    return svg(W, H, body, "GitHub statistics", "Public repositories, contributions, pull requests, followers and language mix, from the GitHub API.")


def footer():
    W, H = 1200, 110
    r, p = ribbon(W, H, 55, 34, 120, 18)
    css = f".w{{animation:dr {p / 18:.0f}s linear infinite}}@keyframes dr{{to{{transform:translateX(-{int(p)}px)}}}}"
    body = f"""<defs><linearGradient id="g" gradientUnits="userSpaceOnUse" x1="0" x2="{W}" y1="0" y2="0">
<stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{PURPLE}"/><stop offset="1" stop-color="{MAGENTA}"/></linearGradient>
<clipPath id="f"><rect width="{W}" height="{H}" rx="18"/></clipPath></defs>
<g clip-path="url(#f)"><rect width="{W}" height="{H}" fill="{NAVY}"/>
<g fill="none" stroke="url(#g)" stroke-width="1"><g class="w">{r}</g></g></g>"""
    return svg(W, H, body, "Footer wave", "Animated gradient wave footer.", css)


def main():
    OUT.mkdir(exist_ok=True)
    files = {"hero.svg": hero(), "about-terminal.svg": about_terminal(), 
             "tech.svg": tech(), "footer.svg": footer()}
    for k, (lab, sub) in {"about": ("About", ""), "stack": ("Stack", "what I have used on real projects"),
                          "projects": ("Projects", ""), "stats": ("Activity", "from the GitHub API"),
                          "snake": ("Contributions", "")}.items():
        files[f"h-{k}.svg"] = header(lab, sub)
    for k, lab, c in NAV:
        files[f"nav-{k}.svg"] = nav(lab, c)
    for p in PROJECTS:
        files[f"project-{p[0]}.svg"] = project(*p)
    cache = OUT / "stats.json"  # written by generate_stats.py from the GitHub API
    files["stats.svg"] = render_stats(json.loads(cache.read_text()) if cache.exists() else None)
    for n, c in files.items():
        (OUT / n).write_text(c, encoding="utf-8")
    print(f"wrote {len(files)} files to {OUT}")


if __name__ == "__main__":
    main()
