"""Export only the freshly built V2 website for static production hosting."""
from pathlib import Path
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
assert "khwab-original-preserved-wide.webp" in (ROOT / "work/just-a-khwab/index.html").read_text()
assert "stax-ronin-bench.webp" in (ROOT / "work/stax-living/index.html").read_text()

if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir()
for directory in ("assets", "about", "work"):
    shutil.copytree(ROOT / directory, OUT / directory)
for name in ("index.html", "404.html", ".nojekyll"):
    shutil.copy2(ROOT / name, OUT / name)
for page in OUT.rglob("*.html"):
    text = page.read_text(encoding="utf-8")
    text = re.sub(
        r'(<meta property="og:image" content=")[^"]+(">)',
        lambda m: m[1] + production + "/assets/img/og.jpg" + m[2],
        text,
    )
    assert "version-switch" not in text, f"Unexpected comparison switch: {page}"
    page.write_text(text, encoding="utf-8")
assert len(list(OUT.rglob("*.html"))) == 17, "Unexpected V2 page count"
print("Exported 17 V2 pages to dist; no source code, credentials or build tools included.")
