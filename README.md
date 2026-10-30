# Pakistan Price Watch

Public source-linked Pakistan price dashboard, hosted on GitHub Pages. Stock-market-style list view, real historical charts, market watch, search, location/category/basis filters, pagination, static category and item pages, original official image viewer with zoom, and a manual update desk.

Live: https://smtalhadv-web.github.io/pakistan-price-watch/

## Current coverage
1,586 dated quote records across 36 locations, including national benchmarks. Records are distinct by unit, location and quote basis; these are not 1,586 unique products. Sources include PBS weekly city surveys and monthly construction/labour surveys, PSO fuel tables, reported gold/silver/FX tables, PriceOye listings, and 137 manually verified Karachi image transcriptions. Eleven official image sheets are saved; the milk source image returns 404 and is labelled unavailable. Dates printed on images take precedence over website index dates.

## Daily update
`.github/workflows/pages.yml` runs at 07:30 Pakistan time (02:30 UTC), on pushes, and on manual dispatch. GitHub may delay schedules or disable them on inactive repositories. The workflow installs the two source-reader dependencies, collects supported public sources, parses numeric data and saves official image snapshots. It commits `data/` and `assets/`, validates, builds, then deploys Pages. Failures retain the previous dated record; see `data/update-report.json`. There is no AI OCR or paid service dependency. New image-only prices require manual verification; the image itself is available inside the site after a successful fetch.

Fuel and metals charts use actual historical observations from the source. Other records accumulate history when subsequent observations arrive. Single quotes have no inferred trend. Each chart keeps the same item, unit, location and quote basis. Source history contains exact date/price/source tuples.

## Manual daily fallback
1. Open **Update desk**, then **Load published data**.
2. Use the form to add/replace a quote by ID, or import JSON/CSV. Preserve unit, source date and HTTPS original source URL.
3. Validate and download `prices.json`.
4. Commit the reviewed file as `data/prices.json` in GitHub. The public editor cannot publish and never asks for tokens.
5. If adding a new quote manually, the build fills its initial history point; subsequent daily ingestion preserves it. To correct a manually transcribed source image rate, also update `data/manual-quotes.json` so the original transcription registry stays consistent.

## Development
Python 3.10+, Node for JS syntax checks:

```
python -m pip install -r requirements.txt
python scripts/update.py
python -m unittest discover -s tests -v
python scripts/build.py
python -m http.server 8000 --directory dist
```

`raw/` contains temporary downloaded HTML and workbooks and is ignored. `assets/` stores original source images and PBS workbooks for durable deployment. `data/prices.json` is the current quote set, `history.json` is dated observations, `sheets.json` is the image source index. Source images use URL-hashed snapshot filenames so later notifications do not overwrite old evidence. Failed image downloads are visible as unavailable, never zero-priced quotes.

Set SITE_URL for canonical URLs and sitemap; the workflow obtains it from Pages. Static category tables include all records for crawlers without JS. Individual item pages preserve sources and dates. Rankings, ad approval, revenue and complete national coverage are not guaranteed. No ads are configured.

## Quote types
Official notified ceilings, weekly/monthly surveyed averages, reported exchange/metal benchmarks and advertised retailer listings are separate records. PBS dates mean week ending or month end, not the current daily transaction price. Retail dates are observation dates. Use exact brand, variant, grade, purity, city and unit before comparison. This is an independent reference, not an official government service or live exchange.
