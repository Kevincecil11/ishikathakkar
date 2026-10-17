# Footer, buttons and section assets

## Current asset and interaction update

Compact proof update: uploaded galleries are viewport-bounded contact sheets, with accessible click-to-enlarge image viewers, previous/next controls, Escape close and original-file links. `assets/image-crops.json` records 11 reviewed screenshot-chrome crops under `assets/img/crops/`; no original upload is overwritten or deleted. Indravansh's campaign banner combines the full contact sheet with two supplied blue-sari portraits to fill the side columns. The homepage's lower physics/image panels are replaced by one Brands & stages grid: every supplied logo appears, while four MTRX clients use clearly disclosed names pending logo files. Mordevs is removed from V2's client collection; BIRC's confirmed credit is Website design. V1, contact state and footer behaviour remain unchanged.

Connected-work correction: when a project has only one related item, it uses a full-width editorial image/copy feature instead of leaving half a two-column grid empty. The original related project, role, summary, result and link remain unchanged. Stax replaces the illustrative train/red-sofa pair with its supplied brand-book cover (linked to the original PDF) and two authentic product-post details extracted from the supplied Instagram grid. The grid is linked visibly as the source; these are not claimed to be newly downloaded full-resolution posts. Original supplied screenshots and gallery files remain intact.

Geometry pass: uploaded galleries now carry natural image dimensions and use `src/gallery-layout.ts` to choose responsive justified rows. Each row fills its width with equal image heights, preserving original source order and the full photos. A compact masonry fallback works without JavaScript. Single-result panels use a balanced label/number/caption grid, and takeaways align with project copy rather than occupying a narrow left column. Project section gaps follow a 32-64px rhythm. Studio banners are about 15% taller, paired community/other banners about 20%, with larger display type. The rejected "my own marketing firm" wording is removed from V2 only.

Footer update: 220px maximum influence radius, responsive circular exclusion field, eased pointer tracking and critically damped time-based return. Tiny square particles stay monochrome; no glow, click wave or idle animation. The canvas batches its draw and sleeps after settling, offscreen or while hidden. Reduced Motion stays static.

Latest UX polish: all five section headers are full clickable cards with hover/focus result reveals, matching Women of Ahmedabad. Small directional arrows use a two-face roll. All work uses native hash navigation after font fitting, with a cache-versioned navigation script. Indravansh uses the original landscape campaign sheet; Women of Ahmedabad shows the full original group photo. Both fit the viewport without cropping or parallax. Uploaded galleries no longer zoom/crop on hover. The footer now uses monochrome pointer-only particles, batched into one canvas fill, with time-based damped springs and no warmth, grain or click-wave effects.

The current upload workflow is [UPLOAD-IMAGES.md](UPLOAD-IMAGES.md). Its project folders and automatic scanning supersede the older filename examples below. `asset_library.py` accepts original filenames and converts HEIC/HEIF at publish time using `requirements-images.txt`.

`src/logo-physics.ts` provides continuous upright circular motion with individual two-axis dragging, release velocity, spring forces, impulse collisions and hub/edge constraints. Grabbing interrupts the moving spring targets; release blends the bodies back into the loop. GSAP 3.13.0 provides the ticker and transform setters. There are no visible slider, arrow or playback controls. Keyboard focus and Reduced Motion pause the orbit; offscreen/hidden-tab detection sleeps the ticker.

The Loud Table client cards use curated covers separately from uploaded project evidence. Stax uses an interior rendering from its supplied Brand Book (page 2); DesignEcho uses its supplied stationery mockup (Style Guide, page 22). Finance Solutions uses the same stock advisory photograph as the Insurance section of https://financesolutions2.vercel.app/, not an invented office or founder portrait. Indravansh remains unchanged.

Real uploaded galleries are connected on V2; the disabled contact form, existing portfolio prose, React footer and V1 design remain separate. General unassigned photographs are stored under `portfolio-highlights`, not attributed to a named event.

## Architecture

V2 keeps its existing Python-generated HTML and GitHub Pages routes. A React
island replaces only the final "Say hello" footer. The contact form and all
project content remain separate and unchanged. V1 is not redesigned.

The supplied halftone footer keeps coverage-based dots, pointer springs,
orange warmth and click shock rings. Its Ishika instance uses the existing
gray canvas, black ink, Anton wordmark, IBM Plex Mono and "SAY HELLO" text.
Only real internal links are passed. No sample studio/email/phone is used.

Dependencies: React/React DOM 18.3.1, TypeScript 5.6.3, esbuild 0.27.2,
Tailwind 3.4.18, Lucide React 0.577.0. The component itself requires React
only: no provider, state manager, remote image or Framer Motion. The host's
fonts are reused. Lucide supplies CTA arrows, never brand-logo substitutes.

The supplied paste's Markdown-auto-linked identifiers are repaired to valid
TypeScript. Metadata is 14px instead of 10.5px. No-href demo links are text,
not fake anchors. Resize, late web fonts, offscreen/tab sleep, unmount cleanup,
live Reduced Motion changes and touch scrolling are handled.

## File locations

| Purpose | Path |
| --- | --- |
| Reusable React component | `/components/ui/halftone-wordmark-footer.tsx` |
| Standalone demo | `/components/ui/demo.tsx` |
| Site adapter and rolling buttons | `/src/portfolio-motion.tsx` |
| Tailwind input and motion CSS | `/src/styles/motion.css` |
| Existing styles | `/assets/css/style.css`, `version2.css`, `logo-hub.css` |
| Generated browser bundle | `/assets/js/portfolio-motion.js` |
| Generated Tailwind CSS | `/assets/css/motion.css` |
| shadcn configuration | `/components.json` |
| Shared helper | `/src/lib/utils.ts` |

This repo previously had no React components folder. `components/ui` is now
the configured shared UI location; `@/components/ui/...` resolves there.
It makes imports and future shadcn additions predictable, but is a project
convention rather than a universal React requirement.

Tailwind is intentionally pinned to v3 and preflight is disabled, preventing
an unrelated global reset from changing the existing website. The shadcn
configuration uses New York, non-RSC, TSX and CSS variables, with cn/cva/clsx/
tailwind-merge available for later controls. No existing form is replaced.

## Build this repository

Use Node 22 and Python 3. From branch `version-2`:

```bash
npm install
npm run typecheck
npm run build
python3 -m http.server 8765
```

Open the local root route. GitHub Pages still publishes this checkout at
`/ishikathakkar/version-2/`. The shared workflow installs dependencies,
typechecks, builds the JS/CSS and runs both existing Python builders.
Visitors receive local bundles, not a React CDN.

The static footer is kept as a no-JS fallback. If motion assets have not been
built, the Python builder emits the previous footer. Edit source TSX, not
generated minified files. After the first install, commit package-lock.json
to lock transitive dependencies too.

## shadcn CLI / optional full React app

This is a custom static/React-island build, not Vite/Next. Do not run a full
framework initializer over it just to add this footer. The components.json
aliases are set up; future CLI additions may need shadcn's manual-install
path because custom builds are not automatically detected.

To create a SEPARATE full React application later:

```bash
npx shadcn@latest init -t vite
```

Or manually:

```bash
npm create vite@latest ishika-react -- --template react-ts
cd ishika-react
npm install
npm install tailwindcss @tailwindcss/vite
npm install -D @types/node
```

Configure the Tailwind Vite plugin and @ alias in vite.config.ts, add
`@import "tailwindcss";` to that NEW application's CSS, configure the same
alias in both TS configs, then run `npx shadcn@latest init`.
Do not mix that Tailwind 4 recipe into this pinned Tailwind 3 build.

Official references:
- https://ui.shadcn.com/docs/installation/vite
- https://ui.shadcn.com/docs/installation/manual
- https://ui.shadcn.com/docs/cli

## Responsive / accessible behavior

The footer spans the page with definite height `clamp(360px, 39vw, 560px)`.
The word fills the width, slightly cropped below the bottom edge. Metadata
rearranges below 720px. Mouse/pen displaces dots; taps trigger a ring without
capturing scrolling. Reduced Motion keeps dots static and disables label
movement. Back-to-top respects that preference too.

Pill CTAs and actual Full story anchors use paired label faces rolling from
top to bottom with paired Lucide arrows. Accessible names, hrefs, target/rel
and transition data stay intact. Disabled forms and orbit controls are excluded.

## Section-by-section image handoff

Upload a ZIP here or share an accessible Drive folder. Actual files are better
than pictures pasted into Word; the last DOCX contained no embedded images.

Suggested handoff folders:

```text
Ishika-assets/
  01-Hero-About/
  02-The-Loud-Table/
    logo.svg
    Stax-Living/
    Indravansh/
    DesignEcho/
    Finance-Solutions/
  03-MTRX/
    logo.svg
    Swati-Interiors/
    Spaces-and-Design/
    BIRC/
    HansWild/
  04-Women-of-Ahmedabad/
    edition-1/
    edition-2/
    edition-3/
    edition-4/
    press/
  05-Mitti/
  06-Stage-Hosting/
    TEDx/
    GUSEC/
    Just-a-Khwab/
  07-Leadership-Teaching/
    Tech-Kaushalya/
    Trinity-Preschool/
```

Add placements.txt listing: filename, section/page, cover/gallery/logo,
and exact caption/alt text. For example:

```text
stax-cover.jpg | Stax Living | Cover | [your exact caption]
edition-1-01.jpg | Women of Ahmedabad | Edition 1 gallery | [your exact caption]
```

Logos: SVG preferred, otherwise transparent PNG/WebP. Photos: original
JPG/PNG, preferably 1600px+ wide. Use originals rather than screenshots;
include photographer/usage credits where relevant.

In the current repo, final files live in `/assets/img/`. The `image`, `logo`
and `gallery.items` fields in `/content.json` map filenames to sections.
V2 also has explicit mappings in `BY`, `CLIENTS`, `client_ribbon()` and the
studio hub in `/build_version2.py`. Update those when replacing assets.
Do not overwrite shared filenames if only one placement should change.

No new stock images are needed for this footer or these buttons. Real studio
logos remain unchanged. Existing illustrative photos are not documentary
evidence; section media will be mapped to what Kevin actually supplies.

## Content boundary

This integration does not apply the still-pending verbatim DOCX copy
migration. BIRC remains included, the homepage MTRX row stays Swati Interiors,
Spaces & Design, BIRC and HansWild, and Mordevs stays only where retained.
The contact form remains clearly inactive until a destination is supplied.
