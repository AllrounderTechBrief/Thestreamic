# The Streamic — Final Production Build

## Deploy
1. Upload all files to your GitHub repository root.
2. Ensure GitHub Pages is enabled for the `main` (or `gh-pages`) branch.
3. The workflow in `rss.yml` will fetch RSS and populate `data/*.json` daily at 06:00 UTC.

## Edit
- Navigation order: set in HTML and CSS (Audio last).
- Homepage cards: handled in `app.js` (10 items per category).
- Category pages: `category.js` renders 6, then **Load more**.

## Assets
- Logo: `assets/logo.svg` (vector) + `assets/logo.png`.
- Fallback image: `assets/fallback.jpg` for entries without images.

## Performance
- Lazy-loading images.
- Minimal JS.
- CSS only for layout/animations.
- Static hosting friendly (GitHub Pages / Netlify).
