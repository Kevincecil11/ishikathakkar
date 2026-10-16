#!/usr/bin/env python3
"""Builds the static site from content.json.

Edit content.json, then run:  python3 build.py
Outputs index.html, about/index.html, work/<slug>/index.html and 404.html.
No dependencies beyond Python 3.
"""
import json, os, html
from pathlib import Path

ROOT = Path(__file__).resolve().parent
C = json.loads((ROOT / "content.json").read_text(encoding="utf-8"))
SITE, LANES, PROJECTS = C["site"], C["lanes"], C["projects"]
LANE = {l["id"]: l for l in LANES}
BY = {p["slug"]: p for p in PROJECTS}
ORDER = [p for l in LANES for p in PROJECTS if p["lane"] == l["id"]]
INK, CANVAS = "#121211", "#E8E8E4"
FONTS = "https://fonts.googleapis.com/css2?family=Anton&family=Cormorant+Garamond:ital,wght@0,500;1,400;1,500&family=IBM+Plex+Mono:wght@400;500&family=Outfit:wght@400;500;600&display=swap"

e = lambda s: html.escape(str(s), quote=True)
pad = lambda n: f"{n:02d}"


def plink(rel, slug):
    return f"{rel}work/{slug}/"


def go(rel, slug, cls="", extra=""):
    """Opening <a> to a project, carrying its lane colour for the curtain."""
    p = BY[slug]; l = LANE[p["lane"]]
    return (f'<a class="{cls}" href="{plink(rel, slug)}" data-color="{l["color"]}" data-on="{l["on"]}" '
            f'data-label="{e(p["name"])}" style="--c:{l["color"]};--on:{l["on"]}"{extra}>')


def ink_link(href, label, cls="", extra=""):
    return f'<a class="{cls}" href="{href}" data-color="{INK}" data-on="{CANVAS}" data-label="{e(label)}"{extra}>'


def head(title, desc, rel):
    return f"""<!doctype html>
<html lang="en" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<meta property="og:image" content="{SITE.get("url", rel)}assets/img/og.jpg">
<meta name="theme-color" content="{CANVAS}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{rel}assets/css/style.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
"""


def header(rel, current):
    def nav(href, label, key, extra=""):
        cur = ' aria-current="page"' if key == current else ""
        return f'<a class="pill" href="{href}"{cur}{extra}>{label}</a>'
    return f"""<header class="hdr">
  {ink_link(rel or "./", "Ishika Thakkar", "logo", ' aria-label="Ishika Thakkar, home"')}Ishika T.<sup>©</sup></a>
  <nav class="pills" aria-label="Main">
    {nav(f"{rel}#work", f"Work <sup>({len(PROJECTS)})</sup>", "work")}
    {ink_link(f"{rel}about/", "About", "pill", ' aria-current="page"' if current == "about" else "")}About</a>
    {nav("#contact", "Contact", "contact")}
  </nav>
</header>
<main id="main">
"""


def footer(rel):
    ct = SITE["contact"]
    links = []
    if ct.get("email"): links.append(f'<a class="pill dark" href="mailto:{e(ct["email"])}">{e(ct["email"])}</a>')
    if ct.get("linkedin"): links.append(f'<a class="pill" href="{e(ct["linkedin"])}" target="_blank" rel="noopener">LinkedIn ↗</a>')
    if ct.get("instagram"): links.append(f'<a class="pill" href="{e(ct["instagram"])}" target="_blank" rel="noopener">Instagram ↗</a>')
    if ct.get("website"): links.append(f'<a class="pill" href="{e(ct["website"])}" target="_blank" rel="noopener">MTRX Digital ↗</a>')
    return f"""</main>
<footer class="footer wrap" id="contact">
  <div class="sec-head"><span>Contact</span><span class="grow"></span><a class="mono" href="#main">Back to top ↑</a></div>
  <p class="fit" aria-label="Say hello"><span>Say hello</span></p>
  <div class="footer-row">
    <div class="pills">{''.join(links)}</div>
    <span class="mono">©2026 {e(SITE["name"])}</span>
  </div>
  <p class="footer-note">{e(SITE["note"])}</p>
</footer>
<div class="curtain" aria-hidden="true"><span class="mono">Opening</span><b></b></div>
<script src="{rel}assets/js/main.js" defer></script>
</body>
</html>
"""


def sec_head(left, mid="", right=""):
    return (f'<div class="sec-head"><span>{left}</span><span class="grow"></span>'
            f'{f"<span class=mono>{mid}</span>" if mid else ""}<span class="grow"></span>{right}</div>')


def card(rel, p, i=0):
    l = LANE[p["lane"]]
    return f"""<div class="reveal" style="--i:{i}">{go(rel, p["slug"], "card")}
  <span class="tile">
    <img src="{rel}assets/img/{p["image"]}" alt="" loading="lazy" style="object-position:{p.get("pos", "50% 50%")}">
    <span class="tag mono"><i></i>{e(l["name"])}</span>
    <span class="arrow" aria-hidden="true">↗</span>
    <span class="name">{e(p["name"])}</span>
    <span class="band"><span>{e(p["result"])}</span><span aria-hidden="true">Open →</span></span>
  </span>
  <span class="cap"><strong>{e(p["role"])}</strong><span>{e(p["result"])}</span></span>
</a></div>"""


# ---------------------------------------------------------------- home
def home():
    rel = ""
    out = [head(SITE["title"], SITE["description"], rel), header(rel, "home")]
    roles = "".join(f"<li>{e(r.split(', ')[0])}, <span>{e(r.split(', ')[1])}</span></li>" for r in SITE["roles"])
    out.append(f"""<section class="hero wrap" aria-labelledby="name">
  <h1 class="fit" id="name"><span>{e(SITE["name"])}</span></h1>
  <div class="hero-row">
    <p class="positioning">{e(SITE["positioning"])}</p>
    <ul class="hero-roles">{roles}</ul>
  </div>
</section>""")

    stubs = "".join(
        f'<div class="reveal" style="--i:{i}">{go(rel, h["slug"], "stub")}<b>{e(h["n"])}</b>'
        f'<span class="tear"><span>{e(h["label"])}</span><small>{e(BY[h["slug"]]["name"])} →</small></span></a></div>'
        for i, h in enumerate(C["highlights"]))
    out.append(f"""<section class="wrap" style="padding-top:16px" aria-labelledby="glance-h">
  {sec_head('<span id="glance-h">At a glance</span>', f'({pad(len(C["highlights"]))})', '<span class="mono muted">Results from the work</span>')}
  <div class="stubs">{stubs}</div>
</section>""")

    a = C["about"]
    role_rows = "".join(
        f'<li>{go(rel, s, "", "")}<i></i><strong>{e(r)}</strong><span>{e(o)}</span><em aria-hidden="true">→</em></a></li>'
        for r, o, s in a["roles"][:5])
    out.append(f"""<section class="sec wrap" aria-labelledby="about-h">
  {sec_head('<span id="about-h">About</span>', "(Ishika)", ink_link("about/", "About", "mono") + "Full story →</a>")}
  <div class="about-grid">
    <img class="portrait reveal" src="assets/img/ishika-portrait.webp" alt="Ishika Thakkar">
    <div>
      <p class="statement">{e(a["statement"])}</p>
      <p class="lead">{e(a["short"])}</p>
      <ul class="roles">{role_rows}</ul>
      {ink_link("about/", "About", "pill dark more")}Read my story →</a>
    </div>
  </div>
</section>""")

    blocks = []
    for l in LANES:
        ps = [p for p in PROJECTS if p["lane"] == l["id"]]
        cards = "".join(card(rel, p, i % 2) for i, p in enumerate(ps))
        blocks.append(f"""<div class="lane-block" id="{l["id"]}" style="--c:{l["color"]};--on:{l["on"]}">
  <div class="lane-head"><h3><i></i>{e(l["name"])}</h3><p><span class="mono muted">({pad(len(ps))}) · {e(l["short"])}</span>{e(l["blurb"])}</p></div>
  <div class="grid">{cards}</div>
</div>""")
    out.append(f"""<section class="sec wrap" id="work" aria-labelledby="work-h">
  {sec_head('<span id="work-h">Work</span>', f"({pad(len(PROJECTS))})", '<span class="mono muted">By discipline</span>')}
  {''.join(blocks)}
</section>""")
    out.append(brands(rel))
    out.append(footer(rel))
    return "".join(out)


def brands(rel):
    cells = []
    for b in C["brands"]:
        inner = f'<img src="{rel}assets/img/{b["logo"]}" alt="{e(b["name"])}" loading="lazy">' if b.get("logo") else f'<span>{e(b["name"])}</span>'
        cells.append(f'{go(rel, b["slug"], "brand", f" aria-label=\"{e(b["name"])}\"")}{inner}</a>')
    return f"""<section class="sec wrap" aria-labelledby="brands-h">
  {sec_head('<span id="brands-h">Brands &amp; stages</span>', f'({pad(len(C["brands"]))})', '<span class="mono muted">Logos: real</span>')}
  <div class="brands">{''.join(cells)}</div>
</section>"""


# ---------------------------------------------------------------- project pages
POSTERS = [("Workshop", "#FFB81C", "#121211", "-3deg"), ("Rave", "#E83E8C", "#FFFFFF", "2.5deg"),
           ("Screening", "#4A6CF7", "#FFFFFF", "-1.5deg"), ("Lecture", "#B79CFF", "#121211", "3deg"),
           ("Community brunch", "#7BDC9E", "#121211", "-2deg")]


def module(rel, p):
    m = p.get("module")
    if m == "shift":
        return """<div class="panel"><div class="panel-label"><span class="mono">The shift</span><span class="mono">DesignEcho</span></div>
  <div class="shift"><s>Writer</s><span aria-hidden="true">→</span><span>Editorial strategist</span></div></div>"""
    if m == "posters":
        ps = "".join(f'<div class="reveal" style="--i:{i}"><div class="poster" style="--pc:{c};--pon:{on};--r:{r}"><b>{e(w)}</b><span class="mono">At Mitti</span></div></div>'
                     for i, (w, c, on, r) in enumerate(POSTERS))
        return f"""<section class="gallery">{sec_head("On the noticeboard", "(4–5 a month)", '<span class="mono muted">Every format, one community</span>')}
  <div class="board">{ps}</div></section>"""
    if m == "mtrx":
        site = SITE["contact"].get("website", "")
        link = f'<p class="panel-foot"><a href="{e(site)}" target="_blank" rel="noopener">See the studio at mtrxdigital.com ↗</a></p>' if site else ""
        return f"""<div class="panel"><div class="panel-label"><span class="mono">The studio approach</span><span class="mono">MTRX Digital</span></div>
  <div class="steps"><div><b>Discover &amp; Define</b></div><div><b>Design &amp; Build</b></div><div><b>Launch &amp; Grow</b></div></div>{link}</div>"""
    if m == "words":
        ws = "".join(f'<span style="--i:{i}">{e(w)}</span>' for i, w in enumerate(p["words"]))
        return f"""<div class="panel"><div class="panel-label"><span class="mono">{e(p.get("words_label", ""))}</span><span class="mono">{e(p["name"])}</span></div>
  <div class="words">{ws}</div></div>"""
    if m == "clients":
        ps = [q for q in PROJECTS if q["lane"] == "brand"]
        return f"""<section class="gallery">{sec_head("Work from The Loud Table", f"({pad(len(ps))})", '<span class="mono muted">Client brands</span>')}
  <div class="grid" style="padding-top:16px">{''.join(card(rel, q, i % 2) for i, q in enumerate(ps))}</div></section>"""
    return ""


def project(p, idx):
    rel = "../../"
    l = LANE[p["lane"]]
    out = [head(f'{p["name"]} · {SITE["name"]}', p["summary"], rel), header(rel, "work")]
    nxt = ORDER[(idx + 1) % len(ORDER)]
    nl = LANE[nxt["lane"]]
    meta = [("Role", p["role"]), ("Organisation", p["org"]), ("Discipline", l["name"])]
    meta_html = "".join(f'<div><dt class="mono">{k}</dt><dd>{e(v)}</dd></div>' for k, v in meta)
    if p.get("module") == "daynight":
        visual = f"""<div class="daynight">
  <figure><div class="frame"><img src="{rel}assets/img/stax-city.webp" alt="A packed Bombay local train in black and white"></div><figcaption>The day outside is black and white.</figcaption></figure>
  <figure class="home"><div class="frame"><img src="{rel}assets/img/stax-sofa.webp" alt="A red sofa in a sunlit home"></div><figcaption>Then you get home, and there is red.</figcaption></figure>
</div>"""
    else:
        visual = f'<figure class="hero-img"><img src="{rel}assets/img/{p["image"]}" alt="" style="object-position:{p.get("pos", "50% 50%")}"></figure>'
    rows = "".join(f'<div class="row reveal"><h2>{e(h)}</h2><p>{e(t)}</p></div>' for h, t in p["sections"])
    if p.get("did"):
        chips = "".join(f"<li>{e(d)}</li>" for d in p["did"])
        rows += f'<div class="row reveal"><h2>{e(p.get("did_title", "What I did"))}</h2><ul>{chips}</ul></div>'
    stats = ""
    if p.get("stats"):
        s = "".join(f'<div class="stat"><b>{e(n)}</b><span>{e(t)}</span></div>' for n, t in p["stats"])
        stats = f"""<div class="panel"><div class="panel-label"><span class="mono">What came of it</span><span class="mono">{e(p["name"])}</span></div>
  <div class="stats{' flow' if p.get('flow') else ''}" style="--n:{min(len(p['stats']), 4)}">{s}</div></div>"""
    gal = ""
    if p.get("gallery"):
        g = p["gallery"]
        figs = "".join(f'<figure class="reveal" style="--i:{i % 4}"><img src="{rel}assets/img/{src}" alt="" loading="lazy"></figure>' for i, src in enumerate(g["items"]))
        gal = f"""<section class="gallery">{sec_head(e(g["title"]), f'({pad(len(g["items']))})', f'<span class="mono muted">{e(g["note"])}</span>')}
  <div class="ggrid" style="--cols:{g["cols"]}">{figs}</div></section>"""
    learned = f'<p class="learned reveal">{e(p["learned"])}</p>' if p.get("learned") else ""
    related = ""
    if p.get("related"):
        cs = "".join(card(rel, BY[s], i) for i, s in enumerate(p["related"]))
        related = f'<section class="gallery">{sec_head("Connected work", f"({pad(len(p["related"]))})")}<div class="related">{cs}</div></section>'
    out.append(f"""<article class="wrap" style="--c:{l["color"]};--on:{l["on"]}">
  <div class="crumbs">
    <a class="mono" href="{rel}#work" data-color="{INK}" data-on="{CANVAS}" data-label="Work">← All work</a>
    <a class="mono lane-tag" href="{rel}#{l["id"]}"><i></i>{e(l["name"])}</a>
  </div>
  <h1 class="fit" data-max="300"><span>{e(p["name"])}</span></h1>
  <p class="summary">{e(p["summary"])}</p>
  <dl class="meta">{meta_html}</dl>
  {visual}
  {rows}
  {stats}
  {module(rel, p)}
  {gal}
  {learned}
  {related}
  {go(rel, nxt["slug"], "next")}<span class="mono">Next · {e(nl["name"])}</span><b>{e(nxt["name"])}</b><em aria-hidden="true">→</em><span class="peek" aria-hidden="true"><img src="{rel}assets/img/{nxt["image"]}" alt="" style="object-position:{nxt.get("pos", "50% 50%")}"></span></a>
</article>""")
    out.append(footer(rel))
    return "".join(out)


# ---------------------------------------------------------------- about
def about():
    rel = "../"
    a = C["about"]
    out = [head(f'About · {SITE["name"]}', SITE["description"], rel), header(rel, "about")]
    paras = "".join(f"<p>{e(t)}</p>" for t in a["paragraphs"])
    role_rows = "".join(
        f'<li>{go(rel, s)}<i></i><strong>{e(r)}</strong><span>{e(o)}</span><em aria-hidden="true">→</em></a></li>' for r, o, s in a["roles"])
    skills = "".join(f"<li>{e(s)}</li>" for s in a["skills"])
    ventures = "".join(
        f'<li>{go(rel, s)}<i></i><strong>{e(BY[s]["name"])}</strong><span>{e(BY[s]["role"])}</span><em aria-hidden="true">→</em></a></li>'
        for s in ["the-loud-table", "mtrx-digital", "women-of-ahmedabad"])
    out.append(f"""<section class="about-hero wrap">
  <div class="crumbs"><span class="mono">About</span><span class="mono muted">{e(SITE["name"])}</span></div>
  <h1 class="statement">{e(a["statement"])}</h1>
</section>
<section class="wrap about-body">
  <img class="portrait reveal" src="{rel}assets/img/ishika-portrait.webp" alt="Ishika Thakkar">
  <div class="copy">{paras}</div>
</section>
<section class="sec wrap" aria-labelledby="roles-h">
  {sec_head('<span id="roles-h">Roles</span>', f'({pad(len(a["roles"]))})', '<span class="mono muted">Open any to see the work</span>')}
  <ul class="roles">{role_rows}</ul>
</section>
<section class="sec wrap" aria-labelledby="ventures-h">
  {sec_head('<span id="ventures-h">What I’ve started</span>', "(03)")}
  <div class="duo">
    <div class="frame reveal"><img src="{rel}assets/img/ishika-hosting.webp" alt="Ishika hosting a session" loading="lazy"></div>
    <div><p class="statement" style="font-size:clamp(32px,3.6vw,56px)">I’ve run departments, not just projects. I’ve built brands, not just posts.</p>
    <ul class="roles">{ventures}</ul></div>
  </div>
</section>
<section class="sec wrap" aria-labelledby="skills-h">
  {sec_head('<span id="skills-h">Skills</span>', f'({pad(len(a["skills"]))})')}
  <ul class="skills">{skills}</ul>
</section>
{brands(rel)}""")
    out.append(footer(rel))
    return "".join(out)


BASE_JS = ("<script>(function(){var s=location.pathname.split('/');"
           "var b=(/github\\.io$/.test(location.hostname)&&s.length>2&&s[1])?'/'+s[1]+'/':'/';"
           "document.write('<base href=\"'+b+'\">');})();</script>\n")


def notfound():
    # GitHub Pages serves 404.html at the missing URL, so pin the base to the site root first.
    rel = ""
    page = head(f'Not found · {SITE["name"]}', SITE["description"], rel).replace("<meta charset=\"utf-8\">", "<meta charset=\"utf-8\">\n" + BASE_JS, 1)
    return (page + header(rel, "") +
            f'<section class="wrap" style="min-height:50vh"><h1 class="fit"><span>Not on the shelf</span></h1>'
            f'<a class="pill dark" href="{rel}">Back to the portfolio →</a></section>' + footer(rel))


def write(path, text):
    path = ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


write("index.html", home())
write("about/index.html", about())
for i, p in enumerate(ORDER):
    write(f"work/{p['slug']}/index.html", project(p, i))
write("404.html", notfound())
print(f"Built home, about, 404 and {len(ORDER)} project pages.")
