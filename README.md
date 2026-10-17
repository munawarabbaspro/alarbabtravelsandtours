# AL ARBAB TRAVEL AND TOURS – website

Static, SEO-ready site: 190 pages, no framework, ~15 KB per page (gzip).

## Folders
- `dist/` – the finished website. Upload **the contents** of this folder to hosting.
- `build.py` – generator. Edit text here, then run `py build.py` to rebuild `dist/`.
- `data/site-data.json` – countries, regions, visa types, packages, airlines, FAQs (taken from the old site).
- `assets/` – `style.css` (inlined into every page at build time) and `app.js`.
- `tools/check.js` – run `node tools/check.js` after a build: checks titles, descriptions, H1, schema and broken links.
- `tools/qa.js` – content QA on every page (leftover text, headings order, image sizes/alt, labels, no fees / IATA / work permit).
- `tools/links.js` – internal-link depth and orphan pages. `tools/audit.js` – word counts and near-duplicate pages.
- `tools/resize_png.py` – shrink a PNG logo without extra software.

## Hosting
Same URLs as the old site (`/umrah`, `/countries/schengen/italy`, …), so Google rankings carry over.
- **Netlify / Cloudflare Pages**: drag `dist/` in. `_redirects` and `_headers` are included.
- **Vercel**: `vercel.json` is included (clean URLs, no trailing slash).
- **cPanel / Apache**: upload to `public_html`. `.htaccess` is included (https + www, clean URLs, 404, gzip).

After going live: submit `https://www.alarbabtravel.com/sitemap.xml` in Google Search Console.

## Change common things
- Phone, email, address: `data/site-data.json` → `brand`
- Office hours: `HOURS` in `build.py`
- Packages: `data/site-data.json` → `packages`
- Umrah prices: `data/site-data.json` → `umrah`
