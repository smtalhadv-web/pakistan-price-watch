# Pakistan Price Watch

GitHub Pages price directory with optional chart sidebar, a first-visit location chooser, Urdu-first official rate transcriptions with English translations, and a broad priced/unpriced catalog.

## Coverage
The current source snapshot contains **2,723 priced records**, plus **304 unpriced catalog entries**, across 36 locations and 20 directory categories. Counts include city, unit, supplier and variant differences, not only unique products. Priced coverage includes 411 mobile listings, 108 electronics listings, 315 furniture variants, 369 machinery/tool/engine records, 57 vehicle/motorcycle variants, official Karachi rates and PBS survey references. Unpriced entries include generic item types and supplier products without a published price; their price and quote date are null, never zero or estimated.

Sources: PSO, Commissioner Karachi original rate sheets, PBS city workbooks, published Hamariweb metal/FX tables, PriceOye, Interwood, Toolsmart, Kamadi, Suzuki Pakistan and Toyota Indus. Toyota figures come from the manufacturer's published vehicle-price configuration and may exclude taxes, freight and registration. Listings need exact model, variant, stock and checkout verification. Source dates and observation dates are labelled. Original milk notification image is unavailable (404); no image-derived price was fabricated.

## Interface
- The price list begins near the top. Charts and market watch are hidden until the user opens the right-side drawer from the sidebar, toolbar or an item row.
- On first visit, users choose a location. Their choice and whether national listings are included stay in browser localStorage. No GPS or IP lookup occurs. The Location control can reopen the chooser.
- Official image transcriptions show Urdu first and English underneath, including inside the zoomable image viewer. There are 149 manually checked item/class records; notification/index date differences stay explicit.
- Durable supplier/manufacturer/retailer prices are shown green and labelled **Listed price**, separate from daily notified rates and survey references. Green does not promise a fixed future price. An unchanged-price claim requires two matching actual observations.
- Unknown-price entries remain visible, searchable and filterable. No price, source availability, inventory or historical trend is invented.

## Automation
`.github/workflows/pages.yml` checks supported sources at 07:30 Pakistan time (02:30 UTC), on manual workflow dispatch, and rebuilds on main pushes. GitHub schedules may be delayed or disabled on inactive repositories. The pipeline fetches public sources, retains original images/workbooks, parses quotes, expands supplier catalogs, records source histories, validates and deploys. Failed sources retain previously dated quotes; inspect `data/update-report.json`. Images refresh automatically but new text transcriptions require human verification. No paid API, AI OCR or secret frontend token is needed.

## Manual updates
Open Update desk → Load published data → edit/add the English and optional Urdu name, price, unit, source date and HTTPS source → Validate → download `prices.json` → commit it as `data/prices.json` in GitHub. Existing metadata is preserved when replacing a quote through the form. The editor prepares files only; GitHub permissions control publishing. To correct a source-image transcription, also update `data/manual-quotes.json` so the transcription registry remains consistent. Generic unpriced entries are maintained in `data/catalog.json`; supplier unpriced entries are in `data/extra-catalog.json`.

## Build and test
```
python -m pip install -r requirements.txt
python scripts/update.py
python -m unittest discover -s tests -v
python scripts/build.py
python -m http.server 8000 --directory dist
```

`data/prices.json` is the strictly positive priced feed. `data/history.json` records actual source observations. Build emits `dist/data/directory.json` combining priced and unpriced entries. Its version and JS/CSS versions prevent stale cached data. `raw/` and `dist/` are ignored; original snapshots in `assets/` are tracked. All fields used in generated HTML are escaped. New generic catalog entries have no individual indexable item page; useful category tables remain crawlable. Set SITE_URL for the canonical URL/sitemap (the workflow supplies it).

This is an independent reference, not a government service, an exchange, a complete inventory of every possible product, or a transaction-price guarantee. No ads or analytics are configured; rankings, revenue and availability are not guaranteed. External sources retain their rights.
