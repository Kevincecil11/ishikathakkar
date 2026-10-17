# Drop images into a project folder. Keep any filename.

Use the **version-2** branch. Commit the upload in GitHub and the site rebuilds automatically.

## Photos

Open `assets/img/photos/`, then the matching project folder. Drop the images there. They appear in that project's gallery.

To pick its main image without renaming anything, put **one** image in the project's `cover/` folder. If there is no cover folder, the first filename in natural alphabetical order becomes the main image.

Projects: `about`, `the-loud-table`, `mtrx-digital`, `stax-living`, `indravansh`, `designecho`, `finance-solutions`, `women-of-ahmedabad`, `mitti`, `on-stage`, `tech-kaushalya`, `trinity-preschool`, `just-a-khwab`.

`portfolio-highlights` holds general photographs that have not been assigned to a named project. They are stored, not automatically displayed. About uses its first photo as the portrait.

JPG, JPEG, PNG, WebP, AVIF, GIF, HEIC and HEIF are accepted. The publisher converts HEIC/HEIF and other raster files to metadata-free, browser-friendly WebP, keeping uploaded source filenames intact. Animated inputs use their first frame.

## Logos

Open `assets/img/logos/`, then the brand folder. Drop **one final logo** there. No naming convention. If several files exist, the first filename in natural alphabetical order wins.

SVG, PNG, JPG and WebP are supported. Existing flat-folder logo uploads remain supported and are not moved or deleted.

## PDFs

Brand documents are in `assets/documents/stax-living/` and `assets/documents/designecho/`. These are linked from their project stories.

## This import

The 65-file source ZIP contains 63 images and two PDFs. One photo appears twice byte-for-byte, so 62 unique images and both PDFs are retained here. `assets/image-import-map.json` maps every original path to its new descriptive name, including that duplicate.

Images were resized and converted to WebP for the website. Original full-resolution images remain in Kevin's source ZIP. No claim or event attribution was guessed for general root-folder photographs.

## Logo interaction

Grab a badge itself and move it in either direction. A quick release throws it; a slow release lets it settle. Badges collide with one another, the panel edges and the parent-studio hub.

No speed slider, arrow buttons, Pause/Play controls or automatic spin. Pointer speed supplies the energy. Springs and damping settle the scene, then the GSAP ticker sleeps.

Touch dragging is captured only on a badge. The rest of the panel scrolls normally. Keyboard: Space or Enter grabs, arrows move, Space releases, Escape resets. Reduced Motion disables throwing and animated settling.
