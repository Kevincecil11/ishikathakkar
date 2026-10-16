#!/usr/bin/env python3
"""Build version 2: About leads directly into Ventures and the work.

Run python3 build_version2.py, not build.py, on this branch.
The original builder stays identical to version 1 for a clean comparison.
Results remain on the individual project pages.
"""
from pathlib import Path
import re
import runpy

ROOT = Path(__file__).resolve().parent
runpy.run_path(str(ROOT / "build.py"), run_name="__main__")
page = ROOT / "index.html"
text = page.read_text(encoding="utf-8")
pattern = r'<section class="sec wrap" aria-labelledby="glance-h">.*?</section>'
text, count = re.subn(pattern, "", text, count=1, flags=re.S)
if count != 1:
    raise RuntimeError("Expected exactly one At a glance section; aborting.")
page.write_text(text, encoding="utf-8")
print("Version 2 ready: Hero > About > Ventures and work. No stats strip.")
