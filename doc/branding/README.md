# mtv_dl_web branding

Design: TV Archive (concept 02). Navy `#0A2856`, cyan `#06B5E8`.

- `logo-light.svg`: wordmark for light website / README backgrounds.
- `logo-dark.svg`: wordmark for dark website backgrounds (transparent canvas).
- `icon.svg`: compact, scalable symbol without lettering, used in the app header.
- `icon-16.png`, `icon-32.png`, etc.: raster icon variants.
- `favicon.ico`: browser favicon with standard sizes.
- `github-social-preview.png`: 1280 × 640 social preview image.

## Integration in this repository

The [project README](../../README.md) uses both SVG wordmarks for GitHub's light and dark themes.

The app's compact SVG, favicon, and Apple touch icon live in
[`src/mtv_dl_web/static/branding/`](../../src/mtv_dl_web/static/branding/) and
are served by Flask under `/static/branding/`.

The social preview artwork is included for future use. GitHub requires a
separate upload in repository settings to enable a custom social preview.

These are newly authored, editable SVG files implementing the selected concept, not vector traces of the rendered inspiration sheet. The SVG wordmark uses a font and may be displayed with a fallback if DejaVu Sans is not available.
