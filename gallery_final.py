"""Website-only gallery crops and a mixed sequence, without deleting originals."""
from pathlib import Path
import hashlib
from PIL import Image

ROOT = Path(__file__).resolve().parent
IMAGES = ROOT / "assets/img"
BOXES = {
    "photos/indravansh/blue-sari-story-preview.webp": (0, 196, 591, 1091),
    "photos/indravansh/social-content-grid.webp": (0, 442, 1179, 1999),
    "photos/indravansh/social-profile-overview.webp": (0, 468, 1179, 2038),
    "photos/stax-living/cover/social-profile-overview.webp": (0, 1992, 1179, 2290),
    "photos/stax-living/social-content-grid-one.webp": (0, 424, 1179, 1996),
    "photos/stax-living/social-content-grid-four.webp": (0, 570, 1179, 2088),
    "photos/stax-living/social-content-grid-three.webp": (0, 183, 1179, 2277),
    "photos/stax-living/social-content-grid-two.webp": (0, 216, 1179, 2290),
}
ORDER = {
    "stax-living": [
        "stax-chair-balloon.webp",
        "photos/stax-living/social-content-grid-three.webp",
        "stax-verdura-wing-shelf.webp",
        "photos/stax-living/social-content-grid-one.webp",
        "stax-gallery-campaign.webp",
        "photos/stax-living/social-content-grid-four.webp",
        "stax-intentional-spaces.webp",
        "photos/stax-living/social-content-grid-two.webp",
        "stax-honest-materials.webp",
        "stax-art-of-living.webp",
        "photos/stax-living/cover/social-profile-overview.webp",
        "stax-customisation.webp",
    ],
    "indravansh": [
        "photos/indravansh/cover/blue-sari-brand-portrait.webp",
        "photos/indravansh/social-content-grid.webp",
        "photos/indravansh/blue-sari-bracelet-detail.webp",
        "photos/indravansh/blue-sari-shoot-contact-sheet.webp",
        "photos/indravansh/blue-sari-story-preview.webp",
        "photos/indravansh/gold-jewellery-detail.webp",
        "photos/indravansh/outdoor-fashion-portrait.webp",
        "photos/indravansh/social-profile-overview.webp",
        "photos/indravansh/outdoor-heritage-portrait.webp",
        "photos/indravansh/purple-jewellery-editorial.webp",
        "photos/indravansh/silver-earring-detail.webp",
        "photos/indravansh/silver-jewellery-detail.webp",
    ],
}
REMOVED = {
    "stax-sierra-supplied.webp",
    "stax-aximo-supplied.webp",
    "stax-material-narratives.webp",
}


def crop(source):
    image_path = IMAGES / source
    box = BOXES[source]
    digest = hashlib.sha256(image_path.read_bytes() + repr(box).encode()).hexdigest()[:16]
    dest = f"_generated/gallery-{image_path.stem}-{digest}.webp"
    target = IMAGES / dest
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        with Image.open(image_path) as image:
            assert 0 <= box[0] < box[2] <= image.width
            assert 0 <= box[1] < box[3] <= image.height
            image.convert("RGB").crop(box).save(target, "WEBP", quality=94, method=6)
    return dest


def refine_gallery(project):
    slug = project["slug"]
    if slug not in ORDER:
        return project
    items = ORDER[slug]
    assert len(items) == len(set(items)) == 12
    assert not REMOVED.intersection(items)
    gallery = dict(project.get("gallery", {}))
    gallery.update(
        title="Project images", note="Tap any image to enlarge", cols=3,
        items=[crop(src) if src in BOXES else src for src in items],
    )
    return dict(project, gallery=gallery)
