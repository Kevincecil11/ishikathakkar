"""Build a crisp social card and explicit, same-origin sharing metadata."""
from pathlib import Path
from io import BytesIO
import hashlib
import html
import re

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist"
ORIGIN = "https://www.ishikathakkar.me"
INK, CANVAS = "#121211", "#E8E8E4"


def font_bytes(family):
    """Use the real, already self-hosted brand font, not a system fallback."""
    for css in sorted((OUT / "assets/css").glob("site.*.css")):
        # Google emits latin last, after latin-ext: prefer the ASCII-bearing face.
        for block in reversed(re.findall(r"@font-face\s*\{[^}]+\}", css.read_text())):
            if not re.search(r"font-family:\s*['\"]?" + re.escape(family) + r"['\"]?\s*;", block):
                continue
            url = re.search(r"url\(['\"]?([^)'\"?]+)", block)
            if not url:
                continue
            path = (css.parent / url[1]).resolve()
            if not path.is_file():
                continue
            font = TTFont(path)
            if "fvar" in font and any(a.axisTag == "wght" for a in font["fvar"].axes):
                font = instantiateVariableFont(font, {"wght": 400})
            font.flavor = None
            stream = BytesIO()
            font.save(stream)
            return stream.getvalue()
    raise RuntimeError(f"Brand font missing for social preview: {family}")


def build_assets():
    scale = 2
    display, body = font_bytes("Anton"), font_bytes("Outfit")
    card = Image.new("RGB", (1200 * scale, 630 * scale), CANVAS)
    portrait = ImageOps.exif_transpose(
        Image.open(ROOT / "assets/img/photos/about/cover/ishika-outdoor-portrait.webp")
    ).convert("RGB")
    portrait = ImageOps.fit(portrait, (520 * scale, 630 * scale),
                           Image.Resampling.LANCZOS, centering=(0.5, 0.28))
    card.paste(portrait, (680 * scale, 0))
    draw = ImageDraw.Draw(card)

    def text(x, y, label, size, face=body, fill=INK):
        f = ImageFont.truetype(BytesIO(face), size * scale)
        assert draw.textbbox((0, 0), label, font=f)[2] <= 588 * scale
        draw.text((x * scale, y * scale), label, font=f, fill=fill, anchor="lt")

    for x, color in [(48, "#101D40"), (70, "#ED691D"), (92, "#F4A623")]:
        draw.ellipse((x * scale, 46 * scale, (x + 12) * scale, 58 * scale), fill=color)
    text(124, 42, "BRANDS. COMMUNITIES. STORIES.", 19)
    text(44, 110, "ISHIKA", 139, display)
    text(44, 266, "THAKKAR", 139, display)
    text(48, 439, "Brand strategist & founder", 30)
    text(48, 488, "The Loud Table  /  MTRX Digital", 24)
    text(48, 568, "ishikathakkar.me", 23)
    card = card.resize((1200, 630), Image.Resampling.LANCZOS)
    payload = BytesIO()
    card.save(payload, "JPEG", quality=93, subsampling=0, optimize=True)
    data = payload.getvalue()
    digest = hashlib.sha256(data).hexdigest()[:12]
    image = f"ishika-thakkar-social-{digest}.jpg"
    (OUT / "assets/img" / image).write_bytes(data)
    assert len(data) < 500_000, "Social image should stay light for chat clients"

    icon = Image.new("RGB", (512, 512), INK)
    di = ImageDraw.Draw(icon)
    f = ImageFont.truetype(BytesIO(display), 292)
    box = di.textbbox((0, 0), "IT", font=f)
    di.text(((512 - box[2] + box[0]) / 2 - box[0],
             (512 - box[3] + box[1]) / 2 - box[1]),
            "IT", fill=CANVAS, font=f)
    di.ellipse((369, 366, 409, 406), fill="#ED691D")
    png = BytesIO()
    icon.resize((64, 64), Image.Resampling.LANCZOS).save(png, "PNG", optimize=True)
    icon_name = "ishika-icon-" + hashlib.sha256(png.getvalue()).hexdigest()[:12] + ".png"
    (OUT / "assets/img" / icon_name).write_bytes(png.getvalue())
    apple_name = "ishika-apple-icon-" + digest + ".png"
    icon.resize((180, 180), Image.Resampling.LANCZOS).save(
        OUT / "assets/img" / apple_name, "PNG", optimize=True)
    return image, icon_name, apple_name


def update_metadata(image, icon, apple):
    pages = sorted(OUT.rglob("*.html"))
    for page in pages:
        source = page.read_text(encoding="utf-8")
        # Keep the homepage browser/search and sharing titles concise.
        # Project and About page titles remain unchanged.
        if page == OUT / "index.html":
            home_title = html.escape("Ishika Thakkar · Portfolio", quote=True)
            source, count = re.subn(r"<title>.*?</title>", f"<title>{home_title}</title>", source, count=1, flags=re.S)
            assert count == 1, "Homepage title is missing"
            source = re.sub(r'<meta\b[^>]*property=["\']og:title["\'][^>]*>\s*', "", source)
            source = source.replace("</head>", f'<meta property="og:title" content="{home_title}">\n</head>', 1)
        title = html.unescape(re.search(r"<title>(.*?)</title>", source, re.S)[1])
        desc = html.unescape(re.search(r'<meta name="description" content="([^"]*)"', source)[1])
        source = re.sub(r'<meta\b[^>]*(?:property|name)=["\'](?:og:image(?::[\w]+)?|og:url|og:site_name|og:locale|twitter:[\w:]+)["\'][^>]*>\s*', "", source)
        source = re.sub(r'<link\b[^>]*rel=["\'](?:canonical|icon|shortcut icon|apple-touch-icon)["\'][^>]*>\s*', "", source)
        path = "/" + page.relative_to(OUT).as_posix()
        if path.endswith("index.html"):
            path = path[:-10]
        url = ORIGIN + path
        image_url = ORIGIN + "/assets/img/" + image
        tags = [
            ("property", "og:url", url),
            ("property", "og:site_name", "Ishika Thakkar"),
            ("property", "og:locale", "en_US"),
            ("property", "og:image", image_url),
            ("property", "og:image:secure_url", image_url),
            ("property", "og:image:type", "image/jpeg"),
            ("property", "og:image:width", "1200"),
            ("property", "og:image:height", "630"),
            ("property", "og:image:alt", "Ishika Thakkar, brand strategist and founder, alongside her portrait."),
            ("name", "twitter:card", "summary_large_image"),
            ("name", "twitter:title", title),
            ("name", "twitter:description", desc),
            ("name", "twitter:image", image_url),
            ("name", "twitter:image:alt", "Ishika Thakkar, brand strategist and founder."),
        ]
        head = "\n".join(f'<meta {kind}="{key}" content="{html.escape(value, quote=True)}">'
                         for kind, key, value in tags)
        head += f'\n<link rel="canonical" href="{url}">'
        root_rel = "../" * (len(page.relative_to(OUT).parts) - 1)
        head += f'\n<link rel="icon" type="image/png" sizes="64x64" href="{root_rel}assets/img/{icon}">'
        head += f'\n<link rel="apple-touch-icon" sizes="180x180" href="{root_rel}assets/img/{apple}">'
        source = source.replace("</head>", head + "\n</head>", 1)
        assert source.count('property="og:image"') == 1
        assert source.count('rel="canonical"') == 1
        assert 'ishikathakkar.vercel.app/assets/img/og.jpg' not in source
        page.write_text(source, encoding="utf-8")
    assert len(pages) == 17
    print(f"Social preview: {image}, 1200x630; updated metadata and icons on {len(pages)} pages.")


if __name__ == "__main__":
    update_metadata(*build_assets())
