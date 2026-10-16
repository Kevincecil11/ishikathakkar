#!/usr/bin/env python3
"""Version 2: studios first, stats retained, colour by organisation.

Biography, outcomes and existing cases come from content.json.
MTRX client credits are studio-level, not individual authorship claims.
"""
from pathlib import Path
import hashlib
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
    {"id": "mordevs-seeds", "name": "Mordevs Seeds", "credit": "Brand identity", "detail": "Brand identity and Next.js development."},
    {"id": "hanswild", "name": "HansWild", "credit": "Wildlife website", "detail": "Website design and Next.js development for a wildlife photographer."},
]
BY = {p["slug"]: p for p in PROJECTS}
BY["stax-living"]["logo"] = "logo-stax.svg"
BY["indravansh"]["logo"] = "logo-indravansh.webp"
for group_id, slugs in MEMBERS.items():
    for slug in slugs:
        BY[slug]["lane"] = group_id
C["lanes"] = GROUPS
g.update(LANES=GROUPS, LANE=GROUP, ORDER=[BY[s] for ids in MEMBERS.values() for s in ids])
original_head, original_project, original_module, original_footer = g["head"], g["project"], g["module"], g["footer"]
STYLE_REV = hashlib.sha256((ROOT / "assets/css/version2.css").read_bytes()).hexdigest()[:12]


def head(title, desc, rel):
    return original_head(title, desc, rel).replace(
        "</head>", f'<link rel="stylesheet" href="{rel}assets/css/version2.css?v={STYLE_REV}">\n</head>'
    )


def header(rel, current):
    items = (
        g["go"](rel, "the-loud-table") + "The Loud Table</a>" +
        g["go"](rel, "mtrx-digital") + "MTRX</a>" +
        f'<a href="{rel}#community">Community</a><a href="{rel}#more">More</a>'
    )
    return f'''<header class="hdr">
      {g["ink_link"](rel or "./", "Ishika Thakkar", "logo")}Ishika T.<sup>©</sup></a>
      <nav class="v2-nav" aria-label="Main">{items}<a href="#contact">Contact</a></nav>
    </header><main id="main">'''


def logo_slot(name, rel, filename=None):
    """Real logos when supplied; honest, neutral slots for assets due later."""
    if filename:
        return f'<span class="logo-stage"><img src="{rel}assets/img/{filename}" alt="{e(name)} logo" loading="lazy"></span>'
    return '<span class="logo-stage logo-pending"><span aria-hidden="true">+</span><span>Logo to be added</span></span>'


def loud_clients(rel):
    # Keep the photographed Loud Table section exactly as in Kevin's reference.
    cards = "".join(g["card"](rel, BY[s], i) for i, s in enumerate(MEMBERS["the-loud-table"][1:]))
    return '<div class="loud-clients">' + cards + "</div>"


def client_ribbon():
    """A compact, pausable reel of existing clients and collaborators.

    Missing logo files use their real names, never invented logo artwork.
    This is cross-portfolio work, not a claim that these are WOA clients.
    """
    brands = [
        ("Stax Living", "logo-stax.svg"),
        ("Indravansh", "logo-indravansh.webp"),
        ("DesignEcho", None),
        ("Finance Solutions", "logo-finance.webp"),
        *[(x["name"], x.get("logo")) for x in CLIENTS],
        ("Mitti", "logo-mitti.webp"),
        ("Trinity Preschool", "logo-trinity.webp"),
        ("TEDx", None),
        ("GUSEC", None),
    ]
    def reel(duplicate=False):
        tiles = "".join(
            '<span class="reel-brand">' +
            (f'<img src="assets/img/{logo}" alt="{e(name)}" loading="lazy">' if logo else
             f'<span class="reel-wordmark">{e(name)}</span>') + "</span>"
            for name, logo in brands
        )
        hidden = ' aria-hidden="true"' if duplicate else ""
        return f'<div class="reel-set"{hidden}>{tiles}</div>'
    return f'''<section class="client-ribbon" aria-label="Clients and collaborators across my work">
      <input class="reel-toggle" id="pause-client-reel" type="checkbox">
      <div class="reel-head"><p>Clients &amp; collaborators <span>Across my work</span></p>
        <label class="reel-control" for="pause-client-reel"><span class="when-playing">Pause</span><span class="when-paused">Play</span><span class="visually-hidden"> logo animation</span></label>
      </div>
      <div class="reel-window"><div class="reel-track">{reel()}{reel(True)}</div></div>
    </section>'''


def women_card():
    p = BY["women-of-ahmedabad"]
    return g["go"]("", p["slug"], "group-top woa-card") + f'''
      <div class="woa-title"><p class="mono">{e(p["role"])}</p><h2>{e(p["name"])}</h2></div>
      <div class="group-intro"><p>{e(p["summary"])}</p><span class="group-link">Full story ↗</span></div>
      <span class="woa-arrow" aria-hidden="true">↗</span>
      <span class="woa-band"><span>{e(p["result"])}</span><span aria-hidden="true">Open →</span></span>
    </a>'''


def mtrx_clients(rel):
    color = GROUP["mtrx-digital"]
    cards = []
    for client in CLIENTS:
        href = f'#{client["id"]}' if rel == "../../" else f'{rel}work/mtrx-digital/#{client["id"]}'
        transition = "" if rel == "../../" else (
            f'data-color="{color["color"]}" data-on="{color["on"]}" data-label="{e(client["name"])}"'
        )
        cards.append(f'''<a class="client-tile" href="{href}" {transition}>
          {logo_slot(client["name"], rel, client.get("logo"))}
          <span class="logo-caption"><strong>{e(client["name"])}</strong><span aria-hidden="true">↗</span></span>
          <span class="logo-result">{e(client["credit"])}</span>
        </a>''')
    return '<div class="mtrx-clients">' + "".join(cards) + "</div>"


def module(rel, p):
    if p.get("module") == "clients":
        return f'''<section class="gallery">
          {sec_head("Work from The Loud Table", "(04)", '<span class="mono muted">Client case studies</span>')}
          {loud_clients(rel)}
        </section>'''
    if p.get("module") == "mtrx":
        credits = "".join(
            f'<div class="row client-credit" id="{x["id"]}"><h2>{e(x["name"])}</h2><p>{e(x["detail"])}</p></div>'
            for x in CLIENTS
        )
        return original_module(rel, p) + f'''<section class="gallery" id="studio-work">
          {sec_head("Work from MTRX", "(04)", '<span class="mono muted">Studio portfolio</span>')}
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


def category_heading(title, anchor=None):
    attr = f' id="{anchor}"' if anchor else ""
    color = {"ventures": "#FFB81C", "community": "#7BDC9E", "more": "#E83E8C"}.get(anchor, "#ED691D")
    return f'<div class="category-heading"{attr} style="--category:{color}"><i aria-hidden="true"></i><h2>{e(title)}</h2></div>'


def footer(rel):
    # No destination is configured yet. All controls are explicitly disabled:
    # this is a visual form, not a working submission service or fake success.
    contact = '''<section class="wrap v2-contact" id="contact" aria-labelledby="contact-heading">
      <div class="contact-grid contact-sheet">
        <div class="contact-intro">
          <div class="contact-kicker"><span class="contact-dots" aria-hidden="true"><i></i><i></i><i></i></span><p class="mono">A note, an idea, an invitation</p></div>
          <h2 id="contact-heading">Good things<br>start here.</h2>
          <p>Tell me what you're thinking. A brand, a room full of people, or an idea that doesn't fit a box yet.</p>
          <span class="contact-signature">Let's find the story.</span>
        </div>
        <form class="contact-form" aria-label="Contact Ishika" aria-describedby="contact-preview-note">
          <fieldset disabled>
            <legend class="visually-hidden">Contact details</legend>
            <div class="form-two">
              <label>Your name<input type="text" autocomplete="name" placeholder="The name behind the idea"></label>
              <label>Email address<input type="email" autocomplete="email" placeholder="you@example.com"></label>
            </div>
            <label>What's on your mind?<textarea rows="4" placeholder="A little about what you have in mind..."></textarea></label>
            <div class="form-bottom"><button type="button" disabled>Send message <span aria-hidden="true">↗</span></button>
              <p id="contact-preview-note">Preview only. Sending isn't connected yet.</p>
            </div>
          </fieldset>
        </form>
      </div>
    </section>'''
    tail = original_footer(rel)
    tail = tail.replace('id="contact"', 'id="say-hello"')
    tail = re.sub(r'<a class="pill" href="https://mtrxdigital\.com"[^>]*>MTRX Digital ↗</a>', "", tail)
    return contact + tail


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
    stubs = "".join(
        f'{g["go"]("", h["slug"], "stub")}<b>{e(h["n"])}</b>'
        f'<span class="tear"><span>{e(h["label"])}</span><small>{e(BY[h["slug"]]["name"])} ↗</small></span></a>'
        for h in C["highlights"]
    )
    out.append(f'''<section class="wrap v2-proof" style="padding-top:16px" aria-labelledby="glance-h">
      {sec_head('<span id="glance-h">At a glance</span>', "(05)", '<span class="mono muted">Results from the work</span>')}
      <div class="stubs">{stubs}</div>
    </section>''')
    a = C["about"]
    role_rows = "".join(
        f'<li>{g["go"]("", s)}<i></i><strong>{e(r)}</strong><span>{e(o)}</span><em aria-hidden="true">→</em></a></li>'
        for r, o, s in a["roles"][:5]
    )
    out.append(f'''<section class="sec wrap v1-about" aria-labelledby="about-h">
      {sec_head('<span id="about-h">About</span>', "(Ishika)", g["ink_link"]("about/", "About", "mono") + "Full story →</a>")}
      <div class="about-grid">
        <img class="portrait reveal" src="assets/img/ishika-portrait.webp" alt="Ishika Thakkar">
        <div>
          <p class="statement">{e(a["statement"])}</p>
          <p class="lead">{e(a["short"])}</p>
          <ul class="roles">{role_rows}</ul>
          {g["ink_link"]("about/", "About", "pill dark more")}Read my story →</a>
        </div>
      </div>
    </section>''')
    out.append('<div id="work" class="wrap v2-work">')
    out.append(category_heading("Ventures", "ventures"))
    out.append(f'''<section class="work-group studio-group" id="the-loud-table" style="{group_style("the-loud-table")}">
      {group_top("the-loud-table", "Founder & Creative Director", "Brand strategy and content, built around what a brand really stands for.")}
      {loud_clients("")}
      <p class="group-services">Brand strategy · Personal branding · Market research · Social media · Creative direction · PR · Influencer marketing</p>
    </section>''')
    out.append(f'''<section class="work-group studio-group" id="mtrx-digital" style="{group_style("mtrx-digital")}">
      {group_top("mtrx-digital", "Co-founder", "A design and development studio. I help lead client relationships, marketing and design.")}
      {mtrx_clients("")}
      <div class="studio-more"><p class="group-services">Client management · Marketing · Design</p>
        <a class="pill dark" href="https://mtrxdigital.com" target="_blank" rel="noopener">Visit MTRX ↗</a></div>
    </section>''')
    out.append(category_heading("Community & Events", "community"))
    out.append('<div class="v2-pair">')
    for slug, role in [("women-of-ahmedabad", "Founder, curator & moderator"), ("mitti", "Events Manager")]:
        p = BY[slug]
        visual = client_ribbon() if slug == "women-of-ahmedabad" else (
            g["go"]("", slug, "story-image") +
            f'<img loading="lazy" src="assets/img/{p["image"]}" alt="">'
            f'<span>{e(p["result"])} <span aria-hidden="true">↗</span></span></a>'
        )
        top = women_card() if slug == "women-of-ahmedabad" else group_top(slug, role, p["summary"])
        out.append(f'''<section class="work-group story-group" id="{slug}" style="{group_style(slug)}">
          {top}
          {visual}
          <p class="group-services">{'Four editions · Newspaper coverage · Held at Mitti' if slug == 'women-of-ahmedabad' else '4-5 events a month · Instagram 11k to 19k'}</p>
        </section>''')
    out.append("</div>")
    out.append(category_heading("And more", "more"))
    out.append('<div class="v2-pair">')
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


g.update(head=head, header=header, module=module, footer=footer)
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
