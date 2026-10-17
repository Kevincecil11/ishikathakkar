#!/usr/bin/env python3
"""Version 2: studios first, stats retained, colour by organisation.

Biography, outcomes and existing cases come from content.json.
MTRX client credits are studio-level, not individual authorship claims.
"""
from pathlib import Path
import hashlib
import json
import re
import runpy
from urllib.parse import unquote
from asset_library import load_library, load_banners

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
    {"id": "swati-interiors", "name": "Swati Interiors", "credit": "Website design", "detail": "Website design and Next.js development.", "url": "https://www.swatiinterior.com/"},
    {"id": "spaces-and-design", "name": "Spaces & Design", "credit": "Website design", "detail": "Website design and WordPress.", "url": "https://www.spacesanddesign.com/"},
    {"id": "birc", "name": "BIRC", "credit": "Website design", "detail": "Website design.", "url": "https://birc.in/"},
    {"id": "hanswild", "name": "HansWild", "credit": "Wildlife website", "detail": "Website design and Next.js development for a wildlife photographer.", "url": "https://hanswild.in/"},
]
BY = {p["slug"]: p for p in PROJECTS}
BY["stax-living"]["logo"] = "logo-stax.svg"
BY["indravansh"]["logo"] = "logo-indravansh.webp"
# Remove the explicitly rejected self-description from V2 without inventing
# replacement claims or changing the source content used by V1.
BY["the-loud-table"]["result"] = ""
BY["the-loud-table"]["org"] = "The Loud Table"
BY["the-loud-table"]["sections"] = [
    (heading.replace("How I work", "How we work"),
     text.replace("The Loud Table is my own marketing firm. ", "")
         .replace("I ask", "We ask").replace("I build", "We build").replace("I sell", "We sell"))
    for heading, text in BY["the-loud-table"]["sections"]
]
PHOTOS, LOGOS = load_library(ROOT)
BANNERS = load_banners(ROOT)
EDITORIAL_ORIGINALS = {}
# These are presentation crops, never replacements for the complete originals.
# The image viewer still opens the uncropped supplied photo.
def editorial_crop(source, box, label):
    from PIL import Image
    file = ROOT / "assets/img" / unquote(source)
    digest = hashlib.sha256(file.read_bytes() + repr(box).encode()).hexdigest()[:16]
    display = f"_generated/{label}-{digest}.webp"
    target = ROOT / "assets/img" / display
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        with Image.open(file) as image:
            image.convert("RGB").crop(box).save(target, "WEBP", quality=92, method=6)
    EDITORIAL_ORIGINALS[display] = source
    return display


PEOPLE_CROPS = {
    "women-of-ahmedabad": editorial_crop(
        "photos/women-of-ahmedabad/cover/community-group-photo.webp",
        (0, 1180, 1950, 2170), "women-complete-group",
    ),
    "mitti": editorial_crop(
        "photos/mitti/cover/event-conversation.webp",
        (0, 180, 1950, 1160), "mitti-conversation-faces",
    ),
    "tech-kaushalya": editorial_crop(
        "photos/tech-kaushalya/cover/university-festival-team.webp",
        (120, 1620, 1680, 2400), "tech-front-row-women",
    ),
}
MITTI_POSTERS = [
    ("Workshop", "#FFBD17", "#121211", "-3deg", "painting-workshop.webp", "People painting around a workshop table"),
    ("Rave", "#E83E8C", "#FFFFFF", "2deg", "music-evening.webp", "A performer at a Mitti music evening"),
    ("Screening", "#4D6CFA", "#FFFFFF", "0deg", "audience-conversation.webp", "Audience members at a Mitti event"),
    ("Lecture", "#B499F4", "#121211", "2deg", "cafe-audience.webp", "Audience members listening at a Mitti lecture"),
    ("Community brunch", "#79D89C", "#121211", "-2deg", "community-table.webp", "People gathered around the community table"),
]
CROP_MAP_PATH = ROOT / "assets/image-crops.json"
CROPS = json.loads(CROP_MAP_PATH.read_text()) if CROP_MAP_PATH.exists() else {}
for slug, files in PHOTOS.items():
    if slug not in BY:
        continue
    p = BY[slug]
    p.update(image=files[0], placeholder=False, pos="50% 40%")
    p["gallery"] = {
        "title": "Project images",
        "note": "Tap any image to enlarge",
        "cols": 3,
        "items": [CROPS.get(src, {}).get("display", src) for src in files],
    }
for slug, logo in LOGOS.items():
    if slug in BY:
        BY[slug]["logo"] = logo
    for client in CLIENTS:
        if client["id"] == slug:
            client["logo"] = logo
TRINITY_CLEAN = {
    "photos/trinity-preschool/cover/annual-function-speaking-one.webp": "trinity-annual-function-speaking-one.webp",
    "photos/trinity-preschool/annual-function-speaking-two.webp": "trinity-annual-function-speaking-two.webp",
}
if "gallery" in BY["trinity-preschool"]:
    BY["trinity-preschool"]["gallery"]["items"] = [
        TRINITY_CLEAN.get(src, src) for src in BY["trinity-preschool"]["gallery"]["items"]
    ]
for brand in C["brands"]:
    if brand.get("slug") in LOGOS:
        brand["logo"] = LOGOS[brand["slug"]]
SITE["note"] = (
    "Uploaded photographs, screenshots and supplied logos are real. Some remaining project "
    "illustrations are stand-ins. MTRX client credits describe studio work, not individual authorship."
)
for group_id, slugs in MEMBERS.items():
    for slug in slugs:
        BY[slug]["lane"] = group_id
# Canonical covers also feed group cards and next-project previews.
BY["stax-living"].update(image="stax-ronin-bench.webp", pos="50% 50%")
BY["just-a-khwab"].update(image="khwab-original-preserved-wide.webp", pos="50% 50%")
BY["trinity-preschool"].update(image="trinity-classroom-added.webp", pos="50% 50%")
C["lanes"] = GROUPS
g.update(LANES=GROUPS, LANE=GROUP, ORDER=[BY[s] for ids in MEMBERS.values() for s in ids])
original_head, original_project, original_module, original_footer = g["head"], g["project"], g["module"], g["footer"]
STYLE_REV = hashlib.sha256((ROOT / "assets/css/version2.css").read_bytes()).hexdigest()[:12]
HUB_REV = hashlib.sha256((ROOT / "assets/css/logo-hub.css").read_bytes()).hexdigest()[:12]
PHYSICS_REV = hashlib.sha256((ROOT / "assets/css/logo-physics.css").read_bytes()).hexdigest()[:12]
MAIN_REV = hashlib.sha256((ROOT / "assets/js/main.js").read_bytes()).hexdigest()[:12]
PREMIUM_REV = hashlib.sha256((ROOT / "assets/css/premium-motion.css").read_bytes()).hexdigest()[:12]
MOTION_JS = ROOT / "assets/js/portfolio-motion.js"
MOTION_READY = MOTION_JS.exists() and (ROOT / "assets/css/motion.css").exists()
MOTION_REV = hashlib.sha256(MOTION_JS.read_bytes()).hexdigest()[:12] if MOTION_READY else ""


# Set before first paint so the opening screen is staged, never flashed.
# Reduced Motion never opts in; a stalled bundle releases content after 3.5s.
MOTION_BOOT = (
    "<script>(function(d){try{if(window.matchMedia&&!matchMedia('(prefers-reduced-motion: reduce)').matches)"
    "{d.classList.add('motion-on');setTimeout(function(){if(!window.__itMotion)d.classList.add('motion-fallback')},3500)}}"
    "catch(e){}})(document.documentElement)</script>\n"
)


def head(title, desc, rel):
    motion_css = (
        f'<link rel="stylesheet" href="{rel}assets/css/motion.css?v={MOTION_REV}">\n'
        f'<link rel="stylesheet" href="{rel}assets/css/premium-motion.css?v={PREMIUM_REV}">\n' + MOTION_BOOT
    ) if MOTION_READY else ""
    return original_head(title, desc, rel).replace(
        "</head>", f'<link rel="stylesheet" href="{rel}assets/css/version2.css?v={STYLE_REV}">\n'
        f'<link rel="stylesheet" href="{rel}assets/css/logo-hub.css?v={HUB_REV}">\n'
        f'<link rel="stylesheet" href="{rel}assets/css/logo-physics.css?v={PHYSICS_REV}">\n{motion_css}</head>'
    )


# Real organisations only, coloured by the same system as the section dots.
MARQUEE = [
    ("The Loud Table", "#101D40"), ("MTRX Digital", "#ED691D"), ("Women of Ahmedabad", "#F4A623"),
    ("Mitti", "#121211"), ("TEDx", "#69388C"), ("GUSEC HerStart", "#69388C"),
    ("Tech Kaushalya", "#24564C"), ("Trinity Preschool", "#24564C"),
]


def marquee():
    items = "".join(
        f'<span class="it-marquee-item"><i style="--dot:{color}"></i>{e(name)}</span>' for name, color in MARQUEE
    )
    return f'<div class="it-marquee" aria-hidden="true"><div class="it-marquee-track">{items}{items}</div></div>'


def header(rel, current):
    about_current = ' aria-current="page"' if current == "about" else ""
    items = (
        g["go"](rel, "the-loud-table") + "The Loud Table</a>" +
        g["go"](rel, "mtrx-digital") + "MTRX</a>" +
        f'<a href="{rel}about/"{about_current}>About</a>' +
        f'<a href="{rel}#community">Community</a>'
    )
    return f'''<header class="hdr">
      {g["ink_link"](rel or "./", "Ishika Thakkar", "logo")}Ishika T.<sup>©</sup></a>
      <nav class="v2-nav" aria-label="Main">{items}<a href="#contact">Contact</a></nav>
    </header><main id="main">'''


def logo_slot(name, rel, filename=None):
    """Real logos when supplied; honest, neutral slots for assets due later."""
    if filename:
        return f'<span class="logo-stage"><img src="{rel}assets/img/{filename}" alt="{e(name)} logo" loading="lazy"></span>'
    return f'<span class="logo-stage logo-pending"><strong>{e(name)}</strong><span>Logo pending</span></span>'


def loud_clients(rel):
    # Curated covers stay separate from uploaded evidence and gallery ordering.
    # Stax: genuine product-post detail from the supplied historical grid.
    # DesignEcho: stationery mockup from the supplied Style Guide, page 22.
    # Finance: the same advisory photograph used on its official supplied site:
    # https://financesolutions2.vercel.app/ (Insurance, Unsplash 1450101499163).
    covers = {
        "stax-living": ("stax-ronin-bench.webp", "50% 50%"),
        "designecho": ("designecho-editorial-stationery.webp", "50% 45%"),
        "finance-solutions": ("finance-solutions-advisory.webp", "50% 50%"),
    }
    cards = []
    for i, slug in enumerate(MEMBERS["the-loud-table"][1:]):
        p = dict(BY[slug])
        if slug in covers:
            p["image"], p["pos"] = covers[slug]
        cards.append(g["card"](rel, p, i))
    return '<div class="loud-clients">' + "".join(cards) + "</div>"


def client_ribbon():
    """All clients are present together, as tangible, individually grabbable badges."""
    brands = [
        ("Stax Living", LOGOS.get("stax-living", "logo-stax.svg")),
        ("Indravansh", LOGOS.get("indravansh", "logo-indravansh.webp")),
        ("DesignEcho", LOGOS.get("designecho")),
        ("Finance Solutions", LOGOS.get("finance-solutions", "logo-finance.webp")),
        *[(x["name"], x.get("logo")) for x in CLIENTS],
        ("Mitti", LOGOS.get("mitti", "logo-mitti.webp")),
        ("Trinity Preschool", LOGOS.get("trinity-preschool", "logo-trinity.webp")),
        ("TEDx", LOGOS.get("tedx")),
        ("GUSEC", LOGOS.get("gusec")),
    ]
    tiles = []
    for name, logo in brands:
        label = {
            "Swati Interiors": ["Swati", "Interiors"],
            "Spaces & Design": ["Spaces", "&", "Design"],
            "Mordevs Seeds": ["Mordevs", "Seeds"],
            "HansWild": ["Hans", "Wild"],
        }.get(name, [name])
        mark = (f'<img src="assets/img/{e(logo)}" alt="" loading="lazy" draggable="false">' if logo else
                '<span class="logo-text">' + "".join(f'<span class="logo-word">{e(word)}</span>' for word in label) + '</span>')
        tiles.append(
            f'<li class="logo-body"><button class="logo-grab" type="button" disabled '
            f'aria-label="Move {e(name)} logo" aria-pressed="false" aria-describedby="logo-keyboard-help" '
            f'data-name="{e(name)}" title="{e(name)}">{mark}</button></li>'
        )
    return f'''<section class="client-ribbon logo-playground" aria-label="Clients and collaborators across my work">
      <div class="reel-head"><p>Clients &amp; collaborators <span>Across my work</span></p></div>
      <div class="logo-stage-area">
        <div class="orbit-center studio-hub" role="img" aria-label="The Loud Table plus MTRX Digital">
          <img class="hub-loud" src="assets/img/{LOGOS.get("the-loud-table", "logo-loud-table.webp")}" alt="">
          <span class="hub-plus" aria-hidden="true">+</span>
          <img class="hub-mtrx" src="assets/img/{LOGOS.get("mtrx-digital", "logo-mtrx.svg")}" alt="">
        </div>
        <ul class="logo-bodies" aria-label="Clients and collaborators">{"".join(tiles)}</ul>
      </div>
      <p class="logo-physics-hint">Grab a logo. Give it a flick.</p>
      <p class="visually-hidden" id="logo-keyboard-help">Press Space to grab a logo. Use arrow keys to move it, Space to release, or Escape to return it. Touch anywhere outside a badge to scroll the page.</p>
      <span class="logo-status visually-hidden" role="status" aria-live="polite"></span>
    </section>'''


def brand_grid():
    """All supplied identities together, with honest names for missing marks."""
    entries = [
        ("The Loud Table", "the-loud-table", LOGOS.get("the-loud-table", "logo-loud-table.webp")),
        ("MTRX Digital", "mtrx-digital", LOGOS.get("mtrx-digital", "logo-mtrx.svg")),
        ("Stax Living", "stax-living", LOGOS.get("stax-living", "logo-stax.svg")),
        ("Indravansh", "indravansh", LOGOS.get("indravansh", "logo-indravansh.webp")),
        ("DesignEcho", "designecho", LOGOS.get("designecho")),
        ("Finance Solutions", "finance-solutions", LOGOS.get("finance-solutions", "logo-finance.webp")),
        *[(x["name"], "mtrx-digital#" + x["id"], x.get("logo")) for x in CLIENTS],
        ("Mitti", "mitti", LOGOS.get("mitti", "logo-mitti.webp")),
        ("Trinity Preschool", "trinity-preschool", LOGOS.get("trinity-preschool", "logo-trinity.webp")),
        ("TEDx", "on-stage", LOGOS.get("tedx")),
        ("GUSEC", "on-stage", LOGOS.get("gusec")),
        ("HerStart", "on-stage", LOGOS.get("herstart")),
        ("Tech Kaushalya", "tech-kaushalya", LOGOS.get("tech-kaushalya")),
    ]
    tiles = []
    for name, destination, logo in entries:
        slug, _, anchor = destination.partition("#")
        href = f'work/{slug}/' + (f"#{anchor}" if anchor else "")
        client = next((x for x in CLIENTS if x["id"] == anchor), None)
        external = ' target="_blank" rel="noopener noreferrer"' if client else ""
        if client:
            href = client["url"]
        mark = (f'<img src="assets/img/{e(logo)}" alt="{e(name)}" loading="lazy">'
                if logo else f'<strong>{e(name)}</strong>')
        contrast = " identity-dark" if name in {"TEDx", "Tech Kaushalya"} else " identity-green" if name == "DesignEcho" else ""
        tiles.append(f'<a class="brand identity-tile{contrast}" href="{href}"{external} aria-label="{e(name)}" '
                     f'data-logo-state="{"supplied" if logo else "name-only"}">{mark}</a>')
    return f'''<section class="brand-index" aria-labelledby="brands-h">
      {sec_head('<span id="brands-h">Brands &amp; stages</span>', f'({len(entries):02d})', '<span class="mono muted">Across my work</span>')}
      <div class="brands identity-grid">{"".join(tiles)}</div>
      <p class="brand-source-note">Original logo artwork, extracted from supplied files and the MTRX selected-work board.</p>
    </section>'''


def women_card():
    p = BY["women-of-ahmedabad"]
    return g["go"]("", p["slug"], "group-top woa-card") + f'''
      <div class="woa-title"><p class="mono">{e(p["role"])}</p><h2>{e(p["name"])}</h2></div>
      <div class="group-intro"><p>{e(p["summary"])}</p><span class="group-link">Full story ↗</span></div>
      <span class="woa-band"><span>{e(p["result"])}</span></span>
    </a>'''


def mtrx_clients(rel):
    cards = []
    visible_clients = [x for x in CLIENTS if rel or x["id"] != "mordevs-seeds"]
    for client in visible_clients:
        cards.append(f'''<a class="client-tile" href="{client["url"]}" target="_blank" rel="noopener noreferrer"
          aria-label="Visit {e(client["name"])} website (opens in a new tab)">
          {logo_slot(client["name"], rel, client.get("logo"))}
          <span class="logo-caption"><strong>{e(client["name"])}</strong><span aria-hidden="true">↗</span></span>
          {f'<span class="logo-result">{e(client["credit"])}</span>' if client["credit"] else ""}
        </a>''')
    return '<div class="mtrx-clients">' + "".join(cards) + "</div>"


def module(rel, p):
    if p.get("module") == "posters":
        posters = []
        for title, color, on, rotation, file, alt in MITTI_POSTERS:
            src = f'{rel}assets/img/photos/mitti/{file}'
            posters.append(
                f'<article class="poster poster-photo" style="--pc:{color};--pon:{on};--r:{rotation}">'
                f'<b>{e(title)}</b><a href="{src}" data-original="{src}" aria-label="Enlarge {e(title)} photo">'
                f'<img src="{src}" alt="{e(alt)}" loading="lazy"></a><span class="mono">At Mitti</span></article>'
            )
        return (
            '<section class="gallery noticeboard">' +
            sec_head("On the noticeboard", "(4-5 a month)", '<span class="mono muted">Every format, one community</span>') +
            '<div class="board">' + "".join(posters) + '</div></section>'
        )
    if p.get("module") == "clients":
        return f'''<section class="gallery">
          {sec_head("Work from The Loud Table", "(04)", '<span class="mono muted">Client case studies</span>')}
          {loud_clients(rel)}
        </section>'''
    if p.get("module") == "mtrx":
        credits = "".join(
            f'<div class="row client-credit" id="{x["id"]}"><h2>{e(x["name"])}</h2>'
            + (f'<p>{e(x["detail"])}</p>' if x["detail"] else "")
            + (
                '<div class="ggrid uploaded-gallery" style="--cols:3">' + "".join(
                    f'<figure><a href="{rel}assets/img/{src}" target="_blank" rel="noopener" aria-label="Open full image">'
                    f'<img src="{rel}assets/img/{src}" alt="" loading="lazy"></a></figure>'
                    for src in PHOTOS[x["id"]]
                ) + "</div>"
                if x["id"] in PHOTOS else ""
            ) + "</div>"
            for x in CLIENTS
        )
        return original_module(rel, p) + f'''<section class="gallery" id="studio-work">
          {sec_head("Work from MTRX", f"({len(CLIENTS):02d})", '<span class="mono muted">Studio portfolio</span>')}
          <p class="v2-credit-note">These are MTRX studio projects. My co-founder role spans client management,
          marketing and design; individual project contributions will be added separately.</p>
          {mtrx_clients(rel)}{credits}
          <a class="pill more" href="https://mtrxdigital.com" target="_blank" rel="noopener">Visit MTRX ↗</a>
        </section>'''
    content = original_module(rel, p)
    document = {
        "designecho": ("designecho/designecho-brand-style-guide.pdf", "Brand style guide (PDF)"),
    }.get(p["slug"])
    if document and (ROOT / "assets/documents" / document[0]).is_file():
        content += f'<p class="more"><a class="pill" href="{rel}assets/documents/{document[0]}" target="_blank" rel="noopener">{document[1]} ↗</a></p>'
    return content


def group_style(group_id):
    x = GROUP[group_id]
    return f'--c:{x["color"]};--on:{x["on"]}'


def group_top(group_id, role, summary):
    x = GROUP[group_id]
    result = BY[group_id]["result"] if group_id in BY else " · ".join(BY[s]["name"] for s in MEMBERS[group_id])
    inverse = " hover-card-inverse" if group_id == "mitti" else ""
    band = f'<span class="hover-band"><span>{e(result)}</span></span>' if result else (
        '<span class="hover-band"><span>Full story</span></span>'
    )
    return f'''<a class="group-top hover-card{inverse}" href="work/{group_id}/"
      data-color="{x["color"]}" data-on="{x["on"]}" data-label="{e(x["name"])}" style="{group_style(group_id)}">
      <div class="hover-title"><p class="mono">{e(role)}</p><h2>{e(x["name"])}</h2></div>
      <div class="group-intro"><p>{e(summary)}</p><span class="group-link">Full story ↗</span></div>
      {band}
    </a>'''


def category_heading(title, anchor=None):
    attr = f' id="{anchor}"' if anchor else ""
    color = {"ventures": "#101D40", "community": "#121211", "more": "#E83E8C"}.get(anchor, "#ED691D")
    return f'<div class="category-heading"{attr} style="--category:{color}"><i aria-hidden="true"></i><h2>{e(title)}</h2></div>'


def footer(rel):
    # User-supplied Web3Forms access key. The provider handles submission.
    contact = '''<section class="wrap v2-contact" id="contact" aria-labelledby="contact-heading">
      <div class="contact-grid contact-sheet">
        <div class="contact-intro">
          <div class="contact-kicker"><span class="contact-dots" aria-hidden="true"><i></i><i></i><i></i></span><p class="mono">A note, an idea, an invitation</p></div>
          <h2 id="contact-heading">Good things<br>start here.</h2>
          <p>Tell me what you're thinking. A brand, a room full of people, or an idea that doesn't fit a box yet.</p>
          <span class="contact-signature">Let's find the story.</span>
        </div>
        <form class="contact-form" action="https://api.web3forms.com/submit" method="POST" aria-label="Contact Ishika">
          <input type="hidden" name="access_key" value="6756b89f-e818-4c12-8f40-cdc5628ee0f7">
          <input type="hidden" name="subject" value="New enquiry from Ishika's portfolio">
          <input type="checkbox" name="botcheck" class="hidden" style="display:none" tabindex="-1" aria-hidden="true">
          <fieldset>
            <legend class="visually-hidden">Contact details</legend>
            <div class="form-two">
              <label>Your name<input type="text" name="name" required autocomplete="name" placeholder="The name behind the idea"></label>
              <label>Email address<input type="email" name="email" required autocomplete="email" placeholder="you@example.com"></label>
            </div>
            <label>What's on your mind?<textarea name="message" required rows="4" placeholder="A little about what you have in mind..."></textarea></label>
            <div class="form-bottom"><button type="submit">Send message <span aria-hidden="true">↗</span></button>
              <p>Sent securely through Web3Forms.</p>
            </div>
          </fieldset>
        </form>
      </div>
    </section>'''
    tail = original_footer(rel)
    tail = tail.replace(f'{rel}assets/js/main.js"', f'{rel}assets/js/main.js?v={MAIN_REV}"')
    tail = tail.replace('id="contact"', 'id="say-hello"')
    tail = re.sub(r'<a class="pill" href="https://mtrxdigital\.com"[^>]*>MTRX Digital ↗</a>', "", tail)
    if MOTION_READY:
        fallback = re.search(r"<footer\b.*?</footer>", tail, re.S).group(0)
        fallback = fallback.replace(' id="say-hello"', "")
        fallback = re.sub(r'<p class="footer-note">.*?</p>', "", fallback, flags=re.S)
        enhanced = (
            f'<div id="say-hello" data-halftone-footer data-relative="{e(rel)}">'
            + fallback + "</div>"
            + f'<p class="footer-note wrap">{e(SITE["note"])}</p>'
        )
        tail = re.sub(r"<footer\b.*?</footer>", lambda _: enhanced, tail, count=1, flags=re.S)
        tail = tail.replace("</body>", f'<script src="{rel}assets/js/portfolio-motion.js?v={MOTION_REV}" defer></script>\n</body>')
    return contact + tail


def home():
    out = [head(SITE["title"], SITE["description"], ""), header("", "home")]
    roles = "".join(f'<li>{e(r)}</li>' for r in SITE["roles"])
    out.append(f'''<section class="hero wrap v2-hero" aria-labelledby="name">
      <h1 class="fit" id="name"><span>{e(SITE["name"])}</span></h1>
      <div class="hero-row"><p class="positioning">{e(SITE["positioning"])}</p>
      <ul class="hero-roles">{roles}</ul></div>
      <div class="pills hero-actions"><a class="pill hero-work" href="#work">See my work ↘</a></div>
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
        <img class="portrait reveal" src="assets/img/{PHOTOS.get("about", ["ishika-portrait.webp"])[0]}" alt="Ishika Thakkar">
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
        top = women_card() if slug == "women-of-ahmedabad" else group_top(slug, role, p["summary"])
        out.append(f'''<section class="work-group story-group" id="{slug}" style="{group_style(slug)}">
          {top}
          <p class="group-services">{'Four editions · Newspaper coverage · Held at Mitti' if slug == 'women-of-ahmedabad' else '4-5 events a month · Instagram 11k to 19k'}</p>
        </section>''')
    out.append("</div>")
    out.append(brand_grid())
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


def project_banner(p):
    """One shared frame, with edge-to-edge photos and complete-image links."""
    if p["slug"] == "designecho":
        def video_tile(file, poster, title):
            return (
                '<div class="banner-video" data-video-tile>'
                f'<video playsinline preload="none" poster="../../assets/img/{poster}" '
                f'aria-label="{e(title)}" controlslist="nodownload">'
                f'<source src="../../assets/video/designecho/{file}" type="video/mp4">'
                f'Your browser cannot play this video. <a href="../../assets/video/designecho/{file}">Open video</a>'
                '</video>'
                f'<button class="video-play" type="button" aria-label="Play {e(title)}">'
                '<span class="play-symbol" aria-hidden="true">▶</span><span>Click to play</span></button>'
                '<span class="video-error" role="status" hidden>Playback could not start. Use the video controls to try again.</span>'
                '</div>'
            )
        return (
            '<div class="project-banner media-triptych" data-project-banner="designecho" '
            'style="--banner-columns:repeat(3,minmax(0,1fr))" aria-label="DesignEcho videos and featured image">'
            + video_tile("brand-story.mp4", "designecho-video-left-poster.webp", "DesignEcho brand story")
            + '<a class="banner-image" data-safe-frame href="../../assets/img/designecho-career-spotlight.webp" '
              'data-original="../../assets/img/designecho-career-spotlight.webp" aria-label="Enlarge DesignEcho career spotlight">'
              '<img src="../../assets/img/designecho-career-spotlight.webp" alt="Career Spotlight: Content Writing, featuring Diya Shah of DesignEcho" decoding="async"></a>'
            + video_tile("career-conversation.mp4", "designecho-video-right-poster.webp", "DesignEcho career conversation")
            + '</div>'
        )
    defaults = {
        "indravansh": [
            ("photos/indravansh/blue-sari-bracelet-detail.webp", "Bracelets and ring against a blue sari", "campaign-bracelet"),
            ("indravansh-portrait-centered.webp", "Blue-sari campaign portrait, AI-recomposed with a centered subject and balanced drapery", "campaign-portrait"),
            ("photos/indravansh/silver-earring-detail.webp", "Silver earring close-up", "campaign-earring"),
        ],
        "stax-living": [
            ("stax-ronin-bench.webp", "Stax Living Ronin Bench campaign artwork", ""),
            ("stax-brava-armchair.webp", "Stax Living Brava Armchair campaign artwork", ""),
            ("stax-material-narratives.webp", "Stax Living Material Narratives campaign artwork", ""),
        ],
        "trinity-preschool": [
            ("photos/trinity-preschool/classroom-portrait.webp", "Ishika with children in the classroom", ""),
            ("trinity-center-supplied.webp", "Ishika speaking at the Trinity annual function, newly supplied photograph", ""),
            ("photos/trinity-preschool/classroom-group-photo.webp", "Ishika and the Trinity classroom group", ""),
        ],
        "designecho": [
            ("crops/designecho-social-profile-overview.webp", "DesignEcho supplied social artwork", ""),
            ("crops/designecho-social-content-grid.webp", "DesignEcho supplied content grid", ""),
        ],
        "finance-solutions": [
            ("photos/finance-solutions/cover/award-presentation-group.webp", "Finance Solutions receiving an award", ""),
            ("photos/finance-solutions/award-presentation-portrait.webp", "Finance Solutions at the award presentation", ""),
        ],
        "mtrx-digital": [
            ("mtrx-studio-home.webp", "MTRX Digital studio website: Design and Develop", ""),
        ],
        "women-of-ahmedabad": [
            (PEOPLE_CROPS["women-of-ahmedabad"], "The complete Women of Ahmedabad group, including the seated women", ""),
        ],
        "mitti": [
            ("photos/mitti/creative-workshop-participant.webp", "A participant painting at a Mitti workshop", ""),
            ("photos/mitti/colour-workshop.webp", "A conversation around the table at Mitti", ""),
            ("photos/mitti/workshop-table.webp", "People working together around a Mitti workshop table", ""),
        ],
        "on-stage": [
            ("photos/on-stage/gusec-at-the-lectern.webp", "Ishika hosting at the GUSEC lectern", ""),
        ],
        "tech-kaushalya": [
            ("tech-kaushalya-women-retouched.webp", "The front-row women at Tech Kaushalya (cropped and AI-retouched to remove background people)", ""),
        ],
        "just-a-khwab": [
            ("khwab-original-preserved-wide.webp", "The complete original Just a Khwab cast and crew in the courtyard", ""),
        ],
        "the-loud-table": [
            ("loud-table-hosting-clear.webp", "Ishika presenting at a community event, sharpened with a head-safe crop", ""),
        ],
    }
    custom = BANNERS.get(p["slug"], [])
    items = [(src, f'{p["name"]} supplied banner image {i + 1}', "") for i, src in enumerate(custom)]
    if not items:
        items = defaults.get(p["slug"], [(p["image"], f'{p["name"]} project photograph', "")])
    originals = {entry["display"]: source for source, entry in CROPS.items()}
    originals.update({display: source for source, display in TRINITY_CLEAN.items()})
    originals.update(EDITORIAL_ORIGINALS)
    safe = p["slug"] in {"women-of-ahmedabad", "mitti", "finance-solutions", "mtrx-digital", "on-stage", "tech-kaushalya", "trinity-preschool", "stax-living", "just-a-khwab", "indravansh", "the-loud-table"}
    links = []
    for src, alt, cls in items:
        original = originals.get(src, src)
        links.append(
            f'<a class="banner-image {cls}"{" data-safe-frame" if safe else ""} href="../../assets/img/{e(original)}" '
            f'data-original="../../assets/img/{e(original)}" aria-label="Open full image: {e(alt)}">'
            f'<img src="../../assets/img/{e(src)}" alt="{e(alt)}" decoding="async"></a>'
        )
    is_indra = p["slug"] == "indravansh" and not custom
    classes = "project-banner" + (" campaign-collage" if is_indra else "")
    columns = ("1fr 1.2fr 1fr" if is_indra else "1fr 1fr" if p["slug"] == "finance-solutions" and not custom
               else f"repeat({len(items)},minmax(0,1fr))")
    return (
        f'<div class="{classes}" data-project-banner="{e(p["slug"])}" '
        f'data-banner-source="{"upload-folder" if custom else "default"}" '
        f'style="--banner-columns:{columns}" aria-label="{e(p["name"])} project images">'
        + "".join(links) + "</div>"
    )


def project_with_uploads(p, index):
    display_project = dict(p)
    # No related/Connected work blocks anywhere; the next-project link stays.
    display_project.pop("related", None)
    if p["slug"] in {"designecho", "finance-solutions", "tech-kaushalya"}:
        display_project.pop("gallery", None)
    if p["slug"] == "trinity-preschool":
        # Restore real evidence without repeating any of the three banner photos.
        display_project["gallery"] = {
            "title": "Project images", "note": "Tap any image to enlarge", "cols": 3,
            "items": [
                "trinity-classroom-added.webp",
            ],
        }
    if p["slug"] == "finance-solutions":
        display_project["flow"] = False
    if p["slug"] in {"mitti", "women-of-ahmedabad"} and p.get("gallery"):
        used = ({EDITORIAL_ORIGINALS[PEOPLE_CROPS[p["slug"]]]} if p["slug"] != "mitti" else {
            "photos/mitti/creative-workshop-participant.webp", "photos/mitti/colour-workshop.webp",
            "photos/mitti/workshop-table.webp",
        })
        if p["slug"] == "mitti":
            used.update(f"photos/mitti/{entry[4]}" for entry in MITTI_POSTERS)
            # Curated full rows of three: omit two near-repeated room/table
            # views, keeping every original available in the asset library.
            used.update({
                "photos/mitti/creative-workshop-table.webp",
            })
        seen = set()
        items = []
        for src in p["gallery"]["items"]:
            file = ROOT / "assets/img" / unquote(src)
            digest = hashlib.sha256(file.read_bytes()).hexdigest() if file.is_file() else src
            if src in used or digest in seen:
                continue
            seen.add(digest)
            items.append(src)
        display_project["gallery"] = dict(p["gallery"], items=items)
        if p["slug"] == "women-of-ahmedabad":
            display_project["gallery"]["items"] = [
                src for src in items if not src.endswith("event-editorial-poster.webp")
            ] + ["woa-community-added.webp"]
        if not items:
            display_project.pop("gallery", None)
    if p["slug"] == "indravansh" and p.get("gallery"):
        excluded = {
            "photos/indravansh/gold-necklace-editorial.webp",
            "photos/indravansh/her-vision-editorial.webp",
        }
        display_project["gallery"] = dict(
            p["gallery"], items=[src for src in p["gallery"]["items"] if src not in excluded],
        )
    if p["slug"] == "stax-living":
        # Keep the five existing social proofs and move the previous two
        # banner photographs here: fifteen images, five complete rows.
        display_project["gallery"] = dict(
            p["gallery"],
            items=p["gallery"]["items"] + [
                "stax-verdura-wing-shelf.webp",
                "stax-material-narratives.webp",
                "stax-gallery-campaign.webp",
                "stax-intentional-spaces.webp",
                "stax-honest-materials.webp",
                "stax-art-of-living.webp",
                "stax-customisation.webp",
                "stax-chair-balloon.webp",
                "stax-sierra-supplied.webp",
                "stax-aximo-supplied.webp",
            ],
        )
    if p["slug"] in {"stax-living", "just-a-khwab", "tech-kaushalya"}:
        display_project["module"] = ""
    page = original_project(display_project, index)
    page = re.sub(
        r'<figure class="hero-img">.*?</figure>',
        lambda _: project_banner(p), page, count=1, flags=re.S,
    )
    if len(display_project.get("related", [])) == 1:
        related = BY[p["related"][0]]
        feature = f'''<div class="related-single">
          {g["go"]("../../", related["slug"], "connected-feature")}
            <span class="connected-photo"><img src="../../assets/img/{e(related["image"])}" alt="" loading="lazy"></span>
            <span class="connected-copy">
              <span class="mono">{e(related["role"])}</span>
              <strong>{e(related["name"])}</strong>
              <span class="connected-summary">{e(related["summary"])}</span>
              <span class="connected-result">{e(related["result"])}</span>
              <span class="connected-cta">Full story <span aria-hidden="true">↗</span></span>
            </span>
          </a>
        </div>'''
        original_related = '<div class="related">' + g["card"]("../../", related, 0) + '</div>'
        page = page.replace(original_related, feature)
    # Returning to the work index must not depend on the transition JavaScript.
    page = re.sub(
        r'<a class="mono" href="([^"]*#work)"[^>]*>← All work</a>',
        r'<a class="mono all-work-link" href="\1">← All work</a>',
        page,
    )
    if p["slug"] in PHOTOS:
        def link_images(match):
            gallery = match.group(0).replace('class="ggrid"', 'class="ggrid uploaded-gallery proof-board"', 1)
            originals = {entry["display"]: source for source, entry in CROPS.items()}
            originals.update({display: source for source, display in TRINITY_CLEAN.items()})
            def image_link(image):
                src = image[3]
                relative = src.split("assets/img/", 1)[1]
                original = originals.get(relative, relative)
                return (image[1] + f'<a href="../../assets/img/{e(original)}" data-original="../../assets/img/{e(original)}" '
                        'aria-label="Enlarge project image">' + image[2] + '</a>' + image[4])
            return re.sub(
                r'(<figure\b[^>]*>)(<img\b[^>]*src="([^"]+)"[^>]*>)(</figure>)',
                image_link,
                gallery,
            )
        page = re.sub(r'<div class="ggrid"[^>]*>.*?</div>', link_images, page, flags=re.S)
    if p["slug"] == "mitti":
        # A full-width film row follows the twelve-photo grid. No photos are
        # removed or repeated merely to fill the new video row.
        film = (
            '<figure class="proof-video" aria-label="Mitti workshop film">'
            '<div class="banner-video" data-video-tile>'
            '<video playsinline preload="none" poster="../../assets/img/mitti-workshop-film-poster.webp" '
            'aria-label="Mitti workshop film" controlslist="nodownload">'
            '<source src="../../assets/video/mitti/workshop-film.mp4" type="video/mp4">'
            'Your browser cannot play this video. <a href="../../assets/video/mitti/workshop-film.mp4">Open video</a>'
            '</video>'
            '<button class="video-play" type="button" aria-label="Play Mitti workshop film">'
            '<span class="play-symbol" aria-hidden="true">▶</span><span>Click to play</span></button>'
            '<span class="video-error" role="status" hidden>Playback could not start. Use the video controls to try again.</span>'
            '</div></figure>'
        )
        page = re.sub(
            r'(<div class="ggrid uploaded-gallery proof-board"[^>]*>.*?)(</div>)',
            lambda match: match[1] + film + match[2], page, count=1, flags=re.S,
        )
    # All results panels use the unchanged Indravansh panel as their sizing
    # reference. Its responsive, content-led height is measured, not guessed.
    if p.get("stats"):
        page = page.replace(
            '<div class="panel"><div class="panel-label"><span class="mono">What came of it',
            f'<div class="panel outcome-panel" data-outcome-panel="{e(p["slug"])}" '
            f'data-outcome-count="{len(p["stats"])}"><div class="panel-label"><span class="mono">What came of it',
            1,
        )
        reference_stats = "".join(
            f'<div class="stat"><b>{e(number)}</b><span>{e(caption)}</span></div>'
            for number, caption in BY["indravansh"]["stats"]
        )
        template = (
            '<template data-outcome-reference><div class="panel">'
            '<div class="panel-label"><span class="mono">What came of it</span><span class="mono">Indravansh</span></div>'
            f'<div class="stats" style="--n:4">{reference_stats}</div></div></template>'
        )
        # Mitti contains nested photo-card <article>s, so use the OUTER close.
        before, separator, after = page.rpartition("</article>")
        if separator:
            page = before + template + separator + after
    if p["slug"] == "indravansh" and not BANNERS.get(p["slug"]):
        note = "Center portrait: AI-recomposed for a balanced layout; the original photograph is retained."
        start = page.find(f'data-project-banner="{p["slug"]}"')
        end = page.find("</div>", start)
        if end != -1:
            page = page[:end + 6] + f'<p class="image-treatment-note">{note}</p>' + page[end + 6:]
    # Reserve each photo's natural dimensions before loading and supply ratios
    # to the justified-row layout. No image is cropped, repeated or omitted.
    from PIL import Image
    def dimensions(match):
        tag, src = match[0], match[1]
        if "assets/img/" not in src or re.search(r'\bwidth=', tag):
            return tag
        file = ROOT / "assets/img" / unquote(src.split("assets/img/", 1)[1].split("?", 1)[0])
        if not file.is_file() or file.suffix.lower() == ".svg":
            return tag
        with Image.open(file) as image:
            width, height = image.size
        return tag.replace("<img ", f'<img width="{width}" height="{height}" ', 1)
    page = re.sub(r'<img\b[^>]*\bsrc="([^"]+)"[^>]*>', dimensions, page)
    page = re.sub(
        r'<p class="learned reveal">(.*?)</p>',
        r'<aside class="learned-note"><span class="mono">What I took from it</span><blockquote>\1</blockquote></aside>',
        page, flags=re.S,
    )
    if p["slug"] == "the-loud-table":
        page = page.replace("The Loud Table, my marketing firm", "The Loud Table")
    return page


g.update(head=head, header=header, module=module, footer=footer)
write("index.html", home())
about_page = g["about"]()
if "about" in PHOTOS:
    about_page = about_page.replace("assets/img/ishika-portrait.webp", "assets/img/" + PHOTOS["about"][0])
write("about/index.html", about_page)
for i, p in enumerate(g["ORDER"]):
    write(f'work/{p["slug"]}/index.html', project_with_uploads(p, i))
write("work/stage-and-hosting/index.html", grouped_page(
    "stage-and-hosting", "Hosting live stages, writing for them, and stepping onto them."
))
write("work/leadership-and-teaching/index.html", grouped_page(
    "leadership-and-teaching", "From a university fest to a preschool classroom."
))
write("404.html", g["notfound"]())
print("Version 2 built: stats retained, six organisation-led groups, brand-specific colours.")
