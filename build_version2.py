#!/usr/bin/env python3
"""Version 2: studios first, stats retained, colour by organisation.

Biography, outcomes and existing cases come from content.json.
MTRX client credits are studio-level, not individual authorship claims.
"""
from pathlib import Path
import re
import runpy

ROOT = Path(__file__).resolve().parent
api = runpy.run_path(str(ROOT / "build.py"), run_name="__main__")
g = api["home"].__globals__
C, SITE, PROJECTS = g["C"], g["SITE"], g["PROJECTS"]
e, sec_head, write = g["e"], g["sec_head"], g["write"]
SITE["url"] = SITE.get("url", "").rstrip("/") + "/version-2/"
SITE["note"] = (
    "Portrait, hosting photo and supplied logos are real. Other project imagery "
    "is illustrative. MTRX client credits describe studio work, not individual authorship."
)
GROUPS = [
    {"id": "the-loud-table", "name": "The Loud Table", "color": "#101D40", "on": "#FFFFFF"},
    {"id": "mtrx-digital", "name": "MTRX Digital", "color": "#ED691D", "on": "#121211"},
    {"id": "women-of-ahmedabad", "name": "Women of Ahmedabad", "color": "#F4A623", "on": "#121211"},
    {"id": "mitti", "name": "Mitti", "color": "#121211", "on": "#FFFFFF"},
    {"id": "stage-and-hosting", "name": "Stage & Hosting", "color": "#69388C", "on": "#FFFFFF"},
    {"id": "leadership-and-teaching", "name": "Leadership & Teaching", "color": "#24564C", "on": "#FFFFFF"},
]
GROUP = {x["id"]: x for x in GROUPS}
MEMBERS = {
    "the-loud-table": ["the-loud-table", "stax-living", "indravansh", "designecho", "finance-solutions"],
    "mtrx-digital": ["mtrx-digital"],
    "women-of-ahmedabad": ["women-of-ahmedabad"],
    "mitti": ["mitti"],
    "stage-and-hosting": ["on-stage", "just-a-khwab"],
    "leadership-and-teaching": ["tech-kaushalya", "trinity-preschool"],
}
CLIENTS = [
    {"id": "swati-interiors", "name": "Swati Interiors", "credit": "Website design", "detail": "Website design and Next.js development."},
    {"id": "spaces-and-design", "name": "Spaces & Design", "credit": "Website design", "detail": "Website design and WordPress."},
    {"id": "birc", "name": "BIRC", "credit": "Studio project", "detail": "Project details will be added after confirmation."},
    {"id": "mordevs-seeds", "name": "Mordevs Seeds", "credit": "Brand identity", "detail": "Brand identity and Next.js development."},
    {"id": "hanswild", "name": "HansWild", "credit": "Wildlife website", "detail": "Website design and Next.js development for a wildlife photographer."},
]
BY = {p["slug"]: p for p in PROJECTS}
for group_id, slugs in MEMBERS.items():
    for slug in slugs:
        BY[slug]["lane"] = group_id
C["lanes"] = GROUPS
g.update(LANES=GROUPS, LANE=GROUP, ORDER=[BY[s] for ids in MEMBERS.values() for s in ids])
original_head, original_project, original_module = g["head"], g["project"], g["module"]


def head(title, desc, rel):
    return original_head(title, desc, rel).replace(
        "</head>", f'<link rel="stylesheet" href="{rel}assets/css/version2.css">\n</head>'
    )


def header(rel, current):
    links = [("the-loud-table", "The Loud Table"), ("mtrx-digital", "MTRX"),
             ("community", "Community"), ("more", "More")]
    items = "".join(f'<a href="{rel}#{anchor}">{label}</a>' for anchor, label in links)
    return f'''<header class="hdr">
      {g["ink_link"](rel or "./", "Ishika Thakkar", "logo")}Ishika T.<sup>©</sup></a>
      <nav class="v2-nav" aria-label="Main">{items}<a href="#contact">Contact</a></nav>
    </header><main id="main">'''


def mtrx_clients(rel):
    color = GROUP["mtrx-digital"]
    cards = []
    for client in CLIENTS:
        href = f'#{client["id"]}' if rel == "../../" else f'{rel}work/mtrx-digital/#{client["id"]}'
        transition = "" if rel == "../../" else (
            f'data-color="{color["color"]}" data-on="{color["on"]}" data-label="{e(client["name"])}"'
        )
        cards.append(f'''<a class="client-tile" href="{href}" {transition}>
          <span class="client-wordmark">{e(client["name"])}</span>
          <span class="client-foot"><span>{e(client["credit"])}</span><span aria-hidden="true">↗</span></span>
        </a>''')
    return '<div class="mtrx-clients">' + "".join(cards) + "</div>"


def module(rel, p):
    if p.get("module") == "clients":
        ps = [BY[s] for s in MEMBERS["the-loud-table"][1:]]
        return f'''<section class="gallery">
          {sec_head("Work from The Loud Table", "(04)", '<span class="mono muted">Client case studies</span>')}
          <div class="grid" style="padding-top:16px">{''.join(g["card"](rel, q, i % 2) for i, q in enumerate(ps))}</div>
        </section>'''
    if p.get("module") == "mtrx":
        credits = "".join(
            f'<div class="row client-credit" id="{x["id"]}"><h2>{e(x["name"])}</h2><p>{e(x["detail"])}</p></div>'
            for x in CLIENTS
        )
        return original_module(rel, p) + f'''<section class="gallery" id="studio-work">
          {sec_head("Work from MTRX", "(05)", '<span class="mono muted">Studio portfolio</span>')}
          <p class="v2-credit-note">These are MTRX studio projects. My co-founder role spans client management,
          marketing and design; individual project contributions will be added separately.</p>
          {mtrx_clients(rel)}{credits}
          <a class="pill more" href="https://mtrxdigital.com" target="_blank" rel="noopener">Visit MTRX ↗</a>
        </section>'''
    return original_module(rel, p)


def group_style(group_id):
    x = GROUP[group_id]
    return f'--c:{x["color"]};--on:{x["on"]}'


def group_top(group_id, role, summary):
    x = GROUP[group_id]
    link = g["go"]("", group_id, "group-link") + "Full story ↗</a>" if group_id in BY else (
        f'<a class="group-link" href="work/{group_id}/">Full story ↗</a>'
    )
    return f'''<div class="group-top" style="{group_style(group_id)}">
      <div><p class="mono">{e(role)}</p><h2>{e(x["name"])}</h2></div>
      <div class="group-intro"><p>{e(summary)}</p>{link}</div>
    </div>'''


def home():
    out = [head(SITE["title"], SITE["description"], ""), header("", "home")]
    roles = "".join(f'<li>{e(r)}</li>' for r in SITE["roles"])
    out.append(f'''<section class="hero wrap v2-hero" aria-labelledby="name">
      <h1 class="fit" id="name"><span>{e(SITE["name"])}</span></h1>
      <div class="hero-row"><p class="positioning">{e(SITE["positioning"])}</p>
      <ul class="hero-roles">{roles}</ul></div>
      <div class="pills hero-actions"><a class="pill dark" href="#work">See my work ↘</a>
      <a class="pill" href="#contact">Get in touch ↗</a></div>
    </section>''')
    a = C["about"]
    out.append(f'''<section class="sec wrap v2-about" aria-labelledby="about-h">
      {sec_head('<span id="about-h">About me</span>', "", g["ink_link"]("about/", "About", "mono") + "Full story ↗</a>")}
      <div class="v2-about-grid">
        <img class="portrait" src="assets/img/ishika-portrait.webp" alt="Ishika Thakkar">
        <div><p class="statement">{e(a["statement"])}</p>
        <p class="lead">Founder of The Loud Table. Co-founder at MTRX. I work across brand strategy,
        design, client relationships and the live experiences that bring people together.</p>
        <p class="v2-about-tail">From building Women of Ahmedabad at Mitti to writing and performing a play:
        the thread is the same. Find the story, bring the right people together, and make it happen.</p></div>
      </div>
    </section>''')
    stubs = "".join(
        f'{g["go"]("", h["slug"], "stub")}<b>{e(h["n"])}</b>'
        f'<span class="tear"><span>{e(h["label"])}</span><small>{e(BY[h["slug"]]["name"])} ↗</small></span></a>'
        for h in C["highlights"]
    )
    out.append(f'''<section class="sec wrap v2-proof" aria-labelledby="glance-h">
      {sec_head('<span id="glance-h">At a glance</span>', "(05)", '<span class="mono muted">Results from the work</span>')}
      <div class="stubs">{stubs}</div>
    </section>''')
    out.append('<div id="work" class="wrap v2-work">')
    loud = [BY[s] for s in MEMBERS["the-loud-table"][1:]]
    cards = "".join(g["card"]("", p, i % 4) for i, p in enumerate(loud))
    out.append(f'''<section class="work-group studio-group" id="the-loud-table" style="{group_style("the-loud-table")}">
      {group_top("the-loud-table", "Founder & Creative Director", "Brand strategy and content, built around what a brand really stands for.")}
      <div class="loud-clients">{cards}</div>
      <p class="group-services">Brand strategy · Personal branding · Market research · Social media · Creative direction · PR · Influencer marketing</p>
    </section>''')
    out.append(f'''<section class="work-group studio-group" id="mtrx-digital" style="{group_style("mtrx-digital")}">
      {group_top("mtrx-digital", "Co-founder", "A design and development studio. I help lead client relationships, marketing and design.")}
      {mtrx_clients("")}
      <p class="group-services">Client management · Marketing · Design</p>
    </section>''')
    out.append('<div class="v2-pair" id="community">')
    for slug, role in [("women-of-ahmedabad", "Founder, curator & moderator"), ("mitti", "Events Manager")]:
        p = BY[slug]
        out.append(f'''<section class="work-group story-group" id="{slug}" style="{group_style(slug)}">
          {group_top(slug, role, p["summary"])}
          {g["go"]("", slug, "story-image")}<img loading="lazy" src="assets/img/{p["image"]}" alt="">
          <span>{e(p["result"])} <span aria-hidden="true">↗</span></span></a>
          <p class="group-services">{'Four editions · Newspaper coverage · Held at Mitti' if slug == 'women-of-ahmedabad' else '4-5 events a month · Instagram 11k to 19k'}</p>
        </section>''')
    out.append('</div><div class="v2-pair" id="more">')
    for slug, desc in [
        ("stage-and-hosting", "TEDx. GUSEC. And a play I wrote, directed and performed."),
        ("leadership-and-teaching", "Four years behind a university fest, and time in the classroom."),
    ]:
        items = "".join(
            g["go"]("", s, "mini-work") +
            f'<div><strong>{e(BY[s]["name"])}</strong><span>{e(BY[s]["result"])}</span></div><span aria-hidden="true">↗</span></a>'
            for s in MEMBERS[slug]
        )
        out.append(f'''<section class="work-group compact-group" id="{slug}" style="{group_style(slug)}">
          {group_top(slug, "Beyond the studios", desc)}
          <div class="mini-works">{items}</div>
        </section>''')
    out.append("</div></div>")
    out.append(g["footer"](""))
    return "".join(out)


def grouped_page(group_id, summary):
    group = GROUP[group_id]
    cards = "".join(g["card"]("../../", BY[s], i) for i, s in enumerate(MEMBERS[group_id]))
    return head(group["name"] + " · Ishika Thakkar", summary, "../../") + header("../../", "work") + f'''
      <article class="wrap" style="{group_style(group_id)}">
        <div class="crumbs"><a class="mono" href="../../#{group_id}">← All work</a></div>
        <h1 class="fit" data-max="210"><span>{e(group["name"])}</span></h1>
        <p class="summary">{e(summary)}</p>
        <div class="grid gallery">{cards}</div>
      </article>''' + g["footer"]("../../")


g.update(head=head, header=header, module=module)
write("index.html", home())
write("about/index.html", g["about"]())
for i, p in enumerate(g["ORDER"]):
    write(f'work/{p["slug"]}/index.html', original_project(p, i))
write("work/stage-and-hosting/index.html", grouped_page(
    "stage-and-hosting", "Hosting live stages, writing for them, and stepping onto them."
))
write("work/leadership-and-teaching/index.html", grouped_page(
    "leadership-and-teaching", "From a university fest to a preschool classroom."
))
write("404.html", g["notfound"]())
print("Version 2 built: stats retained, six organisation-led groups, brand-specific colours.")
