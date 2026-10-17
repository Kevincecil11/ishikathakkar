# Drop images into a project folder. Keep any filename.

Use the **version-2** branch. Commit the upload in GitHub and the site rebuilds automatically.

## Replace a project banner

1. Open the matching project's `banner/` folder below.
2. Click **Add file > Upload files**, then drag your images in.
3. Click **Commit changes** on **version-2**. The live V2 rebuilds automatically.

Use one image for a full-width banner, or two/three images for a side-by-side collage. All images in `banner/` are used, in natural filename order. Original filenames are fine; optional `01`, `02`, `03` prefixes only matter if you want a particular order.

These banner folders override the default banner, including the hand-picked Indravansh images. They do **not** add extra gallery images. Upload gallery images into the parent project folder instead.

Every project has the same banner frame as Indravansh. Banner and thumbnail previews crop to fill their cells, with no padding or coloured bars. Clicking opens the **complete** image, uncropped. Use landscape images for a single-image banner or portrait images for a multi-image collage. A 1,600px-or-larger original is a good starting point; small screenshots cannot become genuine high-resolution photos.

| Project | Upload banner images here |
| --- | --- |
| Stax Living | [stax-living/banner](https://github.com/Kevincecil11/ishikathakkar/tree/version-2/assets/img/photos/stax-living/banner) |
| Indravansh | [indravansh/banner](https://github.com/Kevincecil11/ishikathakkar/tree/version-2/assets/img/photos/indravansh/banner) |
| DesignEcho | [designecho/banner](https://github.com/Kevincecil11/ishikathakkar/tree/version-2/assets/img/photos/designecho/banner) |
| Finance Solutions | [finance-solutions/banner](https://github.com/Kevincecil11/ishikathakkar/tree/version-2/assets/img/photos/finance-solutions/banner) |
| The Loud Table | [the-loud-table/banner](https://github.com/Kevincecil11/ishikathakkar/tree/version-2/assets/img/photos/the-loud-table/banner) |
| MTRX Digital | [mtrx-digital/banner](https://github.com/Kevincecil11/ishikathakkar/tree/version-2/assets/img/photos/mtrx-digital/banner) |
| Women of Ahmedabad | [women-of-ahmedabad/banner](https://github.com/Kevincecil11/ishikathakkar/tree/version-2/assets/img/photos/women-of-ahmedabad/banner) |
| Mitti | [mitti/banner](https://github.com/Kevincecil11/ishikathakkar/tree/version-2/assets/img/photos/mitti/banner) |
| On Stage | [on-stage/banner](https://github.com/Kevincecil11/ishikathakkar/tree/version-2/assets/img/photos/on-stage/banner) |
| Tech Kaushalya | [tech-kaushalya/banner](https://github.com/Kevincecil11/ishikathakkar/tree/version-2/assets/img/photos/tech-kaushalya/banner) |
| Trinity Preschool | [trinity-preschool/banner](https://github.com/Kevincecil11/ishikathakkar/tree/version-2/assets/img/photos/trinity-preschool/banner) |
| Just a Khwab | [just-a-khwab/banner](https://github.com/Kevincecil11/ishikathakkar/tree/version-2/assets/img/photos/just-a-khwab/banner) |

GitHub uploads add files; they do not silently replace different filenames. To replace an existing custom banner, replace those files or remove the old banner files before adding new ones. Leave the README alone. An empty banner folder falls back to the existing default photos.

## Photos

Open `assets/img/photos/`, then the matching project folder. Drop the images there. They appear in that project's gallery.

To pick its gallery lead/homepage card image without renaming anything, put **one** image in the project's `cover/` folder. If there is no cover folder, the first filename in natural alphabetical order becomes the gallery lead. Curated client cards may use separately selected covers. Use `banner/`, not `cover/`, to control the large project-page banner.

Projects: `about`, `the-loud-table`, `mtrx-digital`, `stax-living`, `indravansh`, `designecho`, `finance-solutions`, `women-of-ahmedabad`, `mitti`, `on-stage`, `tech-kaushalya`, `trinity-preschool`, `just-a-khwab`.

`portfolio-highlights` holds general photographs that have not been assigned to a named project. They are stored, not automatically displayed. About uses its first photo as the portrait.

JPG, JPEG, PNG, WebP, AVIF, GIF, HEIC and HEIF are accepted. The publisher converts HEIC/HEIF and other raster files to metadata-free, browser-friendly WebP, keeping uploaded source filenames intact. Animated inputs use their first frame.

## Logos

Open `assets/img/logos/`, then the brand folder. Drop **one final logo** there. No naming convention. If several files exist, the first filename in natural alphabetical order wins.

SVG, PNG, JPG and WebP are supported. Existing flat-folder logo uploads remain supported and are not moved or deleted.

## PDFs

DesignEcho's supplied style guide remains linked from its story. Stax's brand book and its derived cover/interior images have been withdrawn because Kevin confirmed that the book is not Ishika's work. Do not re-add them.

## This import

The original import contained 63 image entries and two PDFs. One photo appeared twice byte-for-byte. `assets/image-import-map.json` records the original mapping; the Stax PDF entry is now explicitly marked as excluded.

Images were resized and converted to WebP for the website. Original full-resolution images remain in Kevin's source ZIP. No claim or event attribution was guessed for general root-folder photographs.

## Image viewer and logo grid

Banner images and gallery thumbnails open an uncropped image viewer. Use Previous/Next or the keyboard arrow keys to browse; Escape closes it and returns focus to the thumbnail. The viewer has no "Open original file" button. Without JavaScript, the image link still opens the full file.

The current homepage uses a static Brands & stages grid, not the older physics panel. All 16 current brands now have supplied logo artwork. Board extracts cover BIRC, Swati Interiors, Spaces & Design, Finance Solutions and HansWild; round background badges are not used. The source board's other clients, including Mordevs, are not automatically added to Ishika's portfolio.
