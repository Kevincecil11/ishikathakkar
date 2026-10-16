# Ishika Thakkar · Portfolio

Static site, no framework, no build server. Works on GitHub Pages as-is.

## Deploy on GitHub Pages
1. Create a repo (e.g. `ishika-portfolio`) and push **everything in this folder** to the root of `main`.
2. Repo → Settings → Pages → Source: *Deploy from a branch* → `main` / `(root)` → Save.
3. Live in ~1 minute at `https://<user>.github.io/ishika-portfolio/`.
4. Custom domain: add it under Settings → Pages, then point a CNAME record at `<user>.github.io`.

All links are relative, so it works in a sub-folder or on a custom domain. `.nojekyll` is included so GitHub serves every file untouched.

## Editing content
**Easiest: edit `content.json` right on GitHub and commit.** The *Build site* action (`.github/workflows/build.yml`) runs `build.py` and commits the regenerated pages within a minute. No Python needed.

Don't edit the HTML by hand (it gets regenerated). All text, numbers, roles and image paths live in **`content.json`**.
```
python3 build.py      # regenerates index.html, about/, work/*/ and 404.html
```
Then commit and push. Preview locally with `python3 -m http.server` and open http://localhost:8000.

- New project: copy a block in `projects`, give it a new `slug` and a `lane` (ventures / brand / community / stage). Build. It shows up on the homepage, in its lane, in "next project", and gets its own page.
- Contact links: fill `site.contact.email / linkedin / instagram`. Empty ones are hidden.

## Images
Real: `ishika-portrait`, `ishika-hosting`, all `logo-*`.
**Placeholders (AI stand-ins, replace with real photos, same filename, ~1600px wide, .webp or update the path in content.json):**
stax-sofa, stax-city, stax-grid-1…6, indravansh, indravansh-grid-1…8, designecho, finance, mitti, woa, trinity, onstage, khwab, tech, mtrx.
When all are real, delete `site.note` in content.json.

## Files
```
index.html            home
about/                full story
work/<slug>/          12 project pages
404.html
assets/css/style.css  all styling (colours = CSS variables at the top)
assets/js/main.js     reveals, page-curtain transition, nav
assets/img/           images
content.json          ALL content
build.py              content.json → HTML
STRUCTURE.md          why the site is organised this way
.github/workflows/    auto-build on every push
```
