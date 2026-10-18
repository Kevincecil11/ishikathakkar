"""Export only the freshly built V2 website for static production hosting.

Besides copying the public files, this step:
- adds responsive WebP variants (srcset/sizes) so phones never download
  2600px photographs for 120px thumbnails; originals stay untouched and are
  still what the full-image viewer opens;
- verifies the security policy in vercel.json allows every inline script by
  hash, so a copy change can never silently break the page under CSP;
- refuses to publish internal production notes.
"""
from concurrent.futures import ProcessPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
import base64
import hashlib
import json
import os
import re
import shutil

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "dist"
production = os.environ.get("VERCEL_PROJECT_PRODUCTION_URL", "ishikathakkar.vercel.app")
production = production if production.startswith("https://") else "https://" + production
production = production.rstrip("/")

home = (ROOT / "index.html").read_text(encoding="utf-8")
assert "data-halftone-footer" in home and "v2-nav" in home, "V2 has not been built"
assert "See my work" in home, "Latest V2 hero is missing"
assert (ROOT / "assets/js/portfolio-motion.js").is_file(), "Motion bundle is missing"
assert (ROOT / "assets/js/site-ui.js").is_file(), "Interface script is missing"
assert "khwab-original-preserved-wide.webp" in (ROOT / "work/just-a-khwab/index.html").read_text()
assert "stax-ronin-bench.webp" in (ROOT / "work/stax-living/index.html").read_text()
PORTFOLIO_PDF = ROOT / "assets/documents/ishika-thakkar-portfolio.pdf"
assert PORTFOLIO_PDF.is_file() and PORTFOLIO_PDF.read_bytes()[:5] == b"%PDF-", "Portfolio PDF is missing"
assert "assets/documents/ishika-thakkar-portfolio.pdf" in home, "Portfolio download link is missing"

if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir()
for directory in ("assets", "about", "work"):
    shutil.copytree(ROOT / directory, OUT / directory)
for name in ("index.html", "404.html", ".nojekyll"):
    shutil.copy2(ROOT / name, OUT / name)
# Build-time bookkeeping never needs to be public.
for name in ("image-crops.json", "image-import-map.json", "logo-extraction-map.json"):
    (OUT / "assets" / name).unlink(missing_ok=True)

FORBIDDEN = (
    "version-switch", "Sent securely", "footer-note", "brand-source-note", "image-treatment-note",
    "stand-ins", "AI-recomposed", "individual authorship",
)


# ---------------------------------------------------------------- fonts + css
# Self-host the Google fonts (latin + latin-ext only) and ship one stylesheet,
# so the first paint waits on a single same-origin request. If the fonts can't
# be fetched at build time the original Google Fonts link is kept as is.
GOOGLE_LINK = re.compile(r'<link rel="stylesheet" href="(https://fonts\.googleapis\.com/css2\?[^"]+)">\n?')
PRECONNECT = re.compile(r'<link rel="preconnect" href="https://fonts\.(?:googleapis|gstatic)\.com"[^>]*>\n?')
LOCAL_CSS = re.compile(r'<link rel="stylesheet" href="([^":]+?\.css)(?:\?[^"]*)?">\n?')
CHROME_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
             "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")


def self_host_fonts(url):
    import urllib.request
    def get(address):
        request = urllib.request.Request(address, headers={"User-Agent": CHROME_UA})
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.read()
    css = get(os.environ.get("FONTS_CSS_URL") or url.replace("&amp;", "&")).decode("utf-8")
    folder = OUT / "assets/fonts"
    folder.mkdir(parents=True, exist_ok=True)
    saved, faces, preload, files = {}, [], [], {}
    for subset, block in re.findall(r"/\*\s*([\w-]+)\s*\*/\s*(@font-face\s*\{[^}]+\})", css):
        if subset not in ("latin", "latin-ext"):
            continue
        source = re.search(r"url\(([^)]+?\.woff2)\)", block)
        if not source:
            continue
        source = source[1].strip("'\"")
        if source not in saved:
            data = get(source)
            assert data[:4] == b"wOF2", "Unexpected font payload"
            saved[source] = hashlib.sha1(data).hexdigest()[:12] + ".woff2"
            (folder / saved[source]).write_bytes(data)
        family = re.search(r"font-family:\s*'([^']+)'", block)[1]
        weight = re.search(r"font-weight:\s*(\d+)", block)
        weight = weight[1] if weight else ""
        italic = "italic" in (re.search(r"font-style:\s*(\w+)", block) or ["", ""])[1]
        # Anton sets every display line: block (preloaded, tiny) so fitted
        # headings never reflow. Small labels/quotes never swap mid-view.
        display = {"Anton": "block", "Cormorant Garamond": "optional", "IBM Plex Mono": "optional"}.get(family, "swap")
        block = re.sub(r"font-display:\s*\w+", "font-display: " + display, block)
        faces.append(block.replace(source, "../fonts/" + saved[source]))
        if subset == "latin":
            files.setdefault(family, saved[source])
            wanted = (family, italic, weight) in (("Anton", False, "400"), ("Outfit", False, "400"),
                                                  ("IBM Plex Mono", False, "400"), ("Cormorant Garamond", True, "400"))
            if wanted and saved[source] not in preload:
                preload.append(saved[source])
    assert faces, "No font faces found"
    return "\n".join(faces) + "\n", preload, files


def minify_css(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"[ \t]*\n[ \t\n]*", "\n", css)
    return css.strip() + "\n"


sample = (OUT / "index.html").read_text(encoding="utf-8")
google = GOOGLE_LINK.search(sample)
font_faces, font_preload, font_files = "", [], {}
if google:
    try:
        font_faces, font_preload, font_files = self_host_fonts(google[1])
        print(f"Self-hosted {len(list((OUT / 'assets/fonts').glob('*.woff2')))} font files")
    except Exception as error:  # Offline builds keep Google Fonts.
        print("Font self-hosting skipped:", type(error).__name__, error)
        font_faces = ""
order = [m[1] for m in LOCAL_CSS.finditer(sample)]
assert order and all(name.startswith("assets/css/") for name in order), order
# Fitted display lines: size them from Anton's real metrics in CSS, so the
# first layout already matches the final one (main.js only trims kerning).
FIT = re.compile(r'<(h1|p) class="fit"((?: [\w-]+="[^"]*")*)><span>([^<]+)</span>')
fit_metrics = None
if font_files.get("Anton"):
    try:
        from fontTools.ttLib import TTFont
        anton = TTFont(OUT / "assets/fonts" / font_files["Anton"])
        fit_metrics = (anton.getBestCmap(), anton["hmtx"].metrics, anton["head"].unitsPerEm)
    except Exception as error:
        print("Fitted-type metrics skipped:", type(error).__name__, error)


def precompute_fit(text):
    if not fit_metrics:
        return text
    cmap, metrics, em = fit_metrics
    import html as html_lib

    def apply(match):
        tag, attrs, label = match[1], match[2], match[3]
        if "data-fit" in attrs:
            return match[0]
        glyphs = html_lib.unescape(label).upper()
        if not glyphs.strip() or any(ord(ch) not in cmap for ch in glyphs):
            return match[0]
        width = sum(metrics[cmap[ord(ch)]][0] for ch in glyphs) / em - 0.005 * len(glyphs)
        k = 0.995 / width
        top = re.search(r'data-max="(\d+)"', attrs)
        size = f"min({k * 100:.4f}cqw, {top[1]}px)" if top else f"{k * 100:.4f}cqw"
        return f'<{tag} class="fit" data-fit{attrs} style="--fit-size:{size}"><span>{label}</span>'
    return FIT.sub(apply, text)


bundle = font_faces + "".join(minify_css((OUT / name).read_text(encoding="utf-8")) for name in order)
bundle_name = "site." + hashlib.sha256(bundle.encode()).hexdigest()[:12] + ".css"
(OUT / "assets/css" / bundle_name).write_text(bundle, encoding="utf-8")


def bundle_page(page, text):
    rel = os.path.relpath(OUT, page.parent).replace(os.sep, "/")
    rel = "" if rel == "." else rel + "/"
    found = [m[1].split("?")[0] for m in LOCAL_CSS.finditer(text)]
    assert [f.replace(rel, "", 1) if rel else f for f in found] == order, f"Stylesheet order differs on {page}"
    head = []
    if font_faces:
        text = GOOGLE_LINK.sub("", text)
        text = PRECONNECT.sub("", text)
        head += [f'<link rel="preload" href="{rel}assets/fonts/{name}" as="font" type="font/woff2" crossorigin>'
                 for name in font_preload]
    head.append(f'<link rel="stylesheet" href="{rel}assets/css/{bundle_name}">')
    first = LOCAL_CSS.search(text)
    text = text[:first.start()] + "\n".join(head) + "\n" + text[first.start():]
    text = LOCAL_CSS.sub(lambda m: m[0] if bundle_name in m[1] else "", text)
    text = precompute_fit(text)
    # Generic containers need a role before they can carry an accessible name.
    text = re.sub(r'<div class="project-banner([^"]*)"(?![^>]*\brole=)', r'<div role="group" class="project-banner\1"', text)
    return text


# ---------------------------------------------------------------- images
VARIANT_WIDTHS = (240, 360, 480, 800, 1200, 1800)
VARIANT_DIR = OUT / "assets/img/_r"
RASTER = (".webp", ".jpg", ".jpeg", ".png")
VOID = {"img", "br", "hr", "input", "meta", "link", "source", "area", "base", "col", "embed", "param", "track", "wbr"}


def columns(style):
    """Share of the widest column in a banner's --banner-columns value."""
    value = re.search(r"--banner-columns:([^;\"]+)", style or "")
    if not value:
        return 1.0
    value = value[1].strip()
    repeat = re.match(r"repeat\((\d+)", value)
    if repeat:
        return 1 / int(repeat[1])
    parts = [float(x[:-2]) for x in re.findall(r"[\d.]+fr", value)]
    return max(parts) / sum(parts) if parts else 1.0


def sizes_for(classes, banner_share):
    if "project-banner" in classes:
        return f"calc((100vw - 32px) * {banner_share:.3f})"
    if "ggrid" in classes or "uploaded-gallery" in classes:
        return "(max-width: 600px) calc((100vw - 48px) / 3), 33vw"
    if "poster" in classes or "board" in classes:
        return "(max-width: 600px) 40vw, (max-width: 960px) 48vw, 20vw"
    if "peek" in classes:
        return "200px"
    if "logo-stage" in classes or "brand" in classes:
        return "(max-width: 600px) 45vw, 300px"
    if "tile" in classes:
        return "(max-width: 600px) 94vw, 48vw"
    if "portrait" in classes or "duo" in classes or "about-grid" in classes:
        return "(max-width: 1199px) 96vw, 48vw"
    return "100vw"


class Images(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.found = [], []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = (attrs.get("class") or "").split()
        if tag == "img":
            context = set(classes)
            share = 1.0
            for _, cls, style in self.stack:
                context.update(cls)
                if "project-banner" in cls:
                    share = columns(style)
            self.found.append((self.getpos(), self.get_starttag_text(), attrs, context, share))
        if tag not in VOID:
            self.stack.append((tag, classes, attrs.get("style")))

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break


def variant_name(source, width):
    digest = hashlib.sha1(str(source.relative_to(OUT)).encode()).hexdigest()[:10]
    return VARIANT_DIR / f"{source.stem}-{digest}-{width}.webp"


def make_variants(job):
    from PIL import Image, ImageOps
    source, widths = Path(job[0]), job[1]
    with Image.open(source) as image:
        image = ImageOps.exif_transpose(image)
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGBA" if "A" in image.getbands() else "RGB")
        made = []
        for width in widths:
            target = variant_name(source, width)
            height = round(image.height * width / image.width)
            image.resize((width, height), Image.LANCZOS).save(target, "WEBP", quality=72, method=5)
            made.append((width, str(target)))
        return str(source), made


pages = sorted(OUT.rglob("*.html"))
plans = []
needed = {}
for page in pages:
    text = page.read_text(encoding="utf-8")
    parser = Images()
    parser.feed(text)
    plans.append((page, text, parser.found))
    for _, _, attrs, _, _ in parser.found:
        src = (attrs.get("src") or "").split("?")[0]
        if not src or src.startswith(("http:", "https:", "data:")) or not src.lower().endswith(RASTER):
            continue
        source = (page.parent / src).resolve()
        if source.is_file() and OUT in source.parents:
            needed.setdefault(source, None)

try:
    from PIL import Image
    PIL_READY = True
except ImportError:  # GitHub Pages fallback: originals still work everywhere.
    PIL_READY = False

variants = {}
if PIL_READY and needed:
    VARIANT_DIR.mkdir(parents=True, exist_ok=True)
    jobs = []
    for source in needed:
        with Image.open(source) as image:
            width = image.width
        widths = tuple(w for w in VARIANT_WIDTHS if w < width * 0.88)
        if width > 900 and widths:
            jobs.append((str(source), widths))
            variants[source] = width
    with ProcessPoolExecutor(max_workers=max(1, min(8, os.cpu_count() or 2))) as pool:
        made = dict(pool.map(make_variants, jobs, chunksize=2))
    variants = {source: (width, made[str(source)]) for source, width in variants.items()}

responsive = 0
for page, text, found in plans:
    lines = text.split("\n")
    offsets = [0]
    for line in lines[:-1]:
        offsets.append(offsets[-1] + len(line) + 1)
    edits = []
    first_banner = True
    for (line, col), raw, attrs, context, share in found:
        start = offsets[line - 1] + col
        if text[start:start + len(raw)] != raw:
            continue
        tag = raw
        src = (attrs.get("src") or "").split("?")[0]
        source = (page.parent / src).resolve() if src and not src.startswith(("http", "data:")) else None
        if source in variants and "srcset" not in attrs:
            width, made = variants[source]
            entries = [f"{os.path.relpath(path, page.parent).replace(os.sep, '/')} {w}w" for w, path in made]
            entries.append(f"{attrs['src']} {width}w")
            tag = tag[:-1].rstrip("/").rstrip() + f' srcset="{", ".join(entries)}" sizes="{sizes_for(context, share)}">'
            responsive += 1
        if "project-banner" in context and "loading" not in attrs:
            tag = tag[:-1] + ' fetchpriority="high">'
        elif "decoding" not in attrs:
            tag = tag[:-1] + ' decoding="async">'
        if tag != raw:
            edits.append((start, len(raw), tag))
    for start, length, tag in sorted(edits, reverse=True):
        text = text[:start] + tag + text[start + length:]
    text = bundle_page(page, text)
    text = re.sub(
        r'(<meta property="og:image" content=")[^"]+(">)',
        lambda m: m[1] + production + "/assets/img/og.jpg" + m[2],
        text,
    )
    for marker in FORBIDDEN:
        assert marker not in text, f"Internal note or stale markup '{marker}' in {page}"
    page.write_text(text, encoding="utf-8")

assert len(pages) == 17, "Unexpected V2 page count"

# ---------------------------------------------------------------- policy
config = json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))
policy = ""
for rule in config.get("headers", []):
    for header in rule.get("headers", []):
        if header["key"].lower() == "content-security-policy":
            policy += header["value"]
assert policy, "vercel.json is missing its Content-Security-Policy"
inline = set()
for page in pages:
    for body in re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", page.read_text(encoding="utf-8"), re.S):
        inline.add("'sha256-" + base64.b64encode(hashlib.sha256(body.encode()).digest()).decode() + "'")
missing = sorted(h for h in inline if h not in policy)
assert not missing, "Add these inline script hashes to the CSP in vercel.json: " + " ".join(missing)
contact = (OUT / "index.html").read_text(encoding="utf-8")
assert 'action="https://api.web3forms.com/submit"' in contact and 'name="access_key"' in contact
assert "https://api.web3forms.com" in policy, "CSP must allow the contact form endpoint"

print(f"Exported 17 V2 pages to dist with {responsive} responsive images; "
      f"{len(inline)} inline scripts covered by CSP; no source code, credentials or build tools included.")
