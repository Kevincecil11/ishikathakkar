"""Drop-in project assets. Folder names choose the project; filenames are free."""
from pathlib import Path
from urllib.parse import quote
import hashlib
import re

PHOTO_SECTIONS = (
    "about", "the-loud-table", "mtrx-digital", "stax-living", "indravansh",
    "designecho", "finance-solutions", "women-of-ahmedabad", "mitti",
    "on-stage", "tech-kaushalya", "trinity-preschool", "just-a-khwab",
    "portfolio-highlights", "swati-interiors", "spaces-and-design", "birc",
    "mordevs-seeds", "hanswild",
)
LOGO_SECTIONS = (
    "the-loud-table", "mtrx-digital", "stax-living", "indravansh", "designecho",
    "finance-solutions", "swati-interiors", "spaces-and-design", "birc",
    "mordevs-seeds", "hanswild", "women-of-ahmedabad", "mitti",
    "trinity-preschool", "tedx", "gusec", "herstart", "tech-kaushalya",
)
IMAGE_TYPES = {".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif", ".heic", ".heif"}
LEGACY_LOGOS = {
    "stax-living": "stax-living-round.png", "indravansh": "Indravansh.jpg",
    "designecho": "designecho-round.png", "finance-solutions": "Finance_Solutions_round.png",
    "mitti": "Mitti_round_enhanced.png", "trinity-preschool": "trinity-preschool-enhanced.png",
    "tedx": "TEDxPrahladnagar-light.png", "gusec": "GUSEC.png",
    "herstart": "herSTART.png", "tech-kaushalya": "Tech-Kaushalya-2026-light.png",
}


def _sort(path):
    return [int(x) if x.isdigit() else x.casefold() for x in re.split(r"(\d+)", path.as_posix())]


def _image(root, path, logo=False):
    """Browser-safe, metadata-free cached WebP, without renaming user sources."""
    if path.suffix.lower() == ".svg":
        return quote(path.relative_to(root / "assets/img").as_posix(), safe="/")
    if path.suffix.lower() == ".webp" and not logo:
        return quote(path.relative_to(root / "assets/img").as_posix(), safe="/")
    try:
        from PIL import Image, ImageOps
        import pillow_heif
        pillow_heif.register_heif_opener()
    except ImportError:
        if path.suffix.lower() in {".heic", ".heif"}:
            raise RuntimeError("HEIC uploads need Pillow and pillow-heif. See image requirements.")
        return quote(path.relative_to(root / "assets/img").as_posix(), safe="/")
    digest = hashlib.sha256(path.read_bytes() + (b"logo-v1" if logo else b"photo-v1")).hexdigest()[:20]
    target = root / "assets/img/_generated" / f"{digest}.webp"
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        with Image.open(path) as original:
            image = ImageOps.exif_transpose(original).convert("RGBA" if "A" in original.getbands() else "RGB")
            image.thumbnail((768, 768) if logo else (2000, 2600), Image.Resampling.LANCZOS)
            image.save(target, "WEBP", quality=88, method=6)
    return target.relative_to(root / "assets/img").as_posix()


def load_library(root):
    root = Path(root)
    base = root / "assets/img"
    photos, logos = {}, {}
    for slug in PHOTO_SECTIONS:
        folder = base / "photos" / slug
        files = sorted((p for p in folder.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_TYPES), key=_sort) if folder.exists() else []
        # An optional cover/ folder wins, so changing a cover never needs renaming.
        covers = [p for p in files if "cover" in p.relative_to(folder).parts[:-1]]
        ordered = covers + [p for p in files if p not in covers]
        if ordered:
            photos[slug] = [_image(root, p) for p in ordered]
    for slug in LOGO_SECTIONS:
        folder = base / "logos" / slug
        files = sorted((p for p in folder.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_TYPES | {".svg"}), key=_sort) if folder.exists() else []
        if files:
            logos[slug] = _image(root, files[0], True)
        elif slug in LEGACY_LOGOS and (base / "logos" / LEGACY_LOGOS[slug]).is_file():
            logos[slug] = _image(root, base / "logos" / LEGACY_LOGOS[slug], True)
    return photos, logos
