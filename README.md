# Pakistan Price Watch

GitHub Pages price directory with optional chart sidebar, a first-visit location chooser, Urdu-first official rate transcriptions with English translations, and a broad priced/unpriced catalog.

## Coverage
The current snapshot contains **5,283 priced observations** and **304 unpriced catalog entries** across 36 locations and 20 categories. These are city, supplier and variant records, not unique universal products. 3,744 records have source-supplied product photos. The expanded commerce reader observed 3,078 offers across 109 fetched URLs; 6 fetches failed in the initial run. No universal completeness is claimed.

Sources: PSO, Commissioner Karachi original rate sheets, PBS city workbooks, published Hamariweb metal/FX tables, PriceOye, MiStore, ZAH Computers, Galaxy, Interwood, Toolsmart, Kamadi, Suzuki Pakistan and Toyota Indus. Toyota figures come from the manufacturer's published vehicle-price configuration and may exclude taxes, freight and registration. Listings need exact model, variant, stock and checkout verification. Source dates and observation dates are labelled. Original milk notification image is unavailable (404); no image-derived price was fabricated.

## Interface
- The price list begins near the top. Charts and market watch are hidden until the user opens the right-side drawer from the sidebar, toolbar or an item row.
- On first visit, users choose a location. Their city choice stays in browser localStorage. Pakistan is the parent location: national items always appear with the selected city; all other cities are excluded. Choosing Pakistan shows national entries only. No GPS or IP lookup occurs. The Location control can reopen the chooser.
- Official image transcriptions show Urdu first and English underneath, including inside the zoomable image viewer. There are 149 manually checked item/class records; notification/index date differences stay explicit.
- Durable supplier/manufacturer/retailer prices are shown green and labelled **Listed price**, separate from daily notified rates and survey references. Green does not promise a fixed future price. An unchanged-price claim requires two matching actual observations.
- Unknown-price entries remain visible, searchable and filterable. No price, source availability, inventory or historical trend is invented.

## Automation
`.github/workflows/pages.yml` checks supported sources at 07:30 Pakistan time (02:30 UTC), on manual workflow dispatch, and rebuilds on main pushes. GitHub schedules may be delayed or disabled on inactive repositories. The pipeline fetches public sources, retains original images/workbooks, parses quotes, expands supplier catalogs, records source histories, validates and deploys. Failed sources retain previously dated quotes; inspect `data/update-report.json`. Images refresh automatically but new text transcriptions require human verification. No paid API, AI OCR or secret frontend token is needed.

## Manual updates
Edit validated source JSON through the repository and commit changes. No public editor or admin dashboard is deployed. `admin/.gitkeep` reserves the directory only. GitHub Pages is a public static host; do not place credentials or private admin data there. Original report files stay in the source repository but are excluded from the public build. `data/catalog.json` and `data/extra-catalog.json` retain unknown prices as null.

## Comparisons and search discovery
Full names, unit and basis are conservatively grouped; city surveys also require matching periods. Makita offers can additionally match by exact supplier-reported model code, with explicit kit, warranty and specification caveats. The comparison view intentionally shows other cities while the main directory retains the city filter. Related products are separately labelled, never assumed to be interchangeable.

Public pages include About, Privacy, Terms, Disclaimer, Contact/corrections and Editorial policy. Per-item factual answers contain actual observed prices, dates, source links and available specifications/photos. Canonical metadata, descriptive snippets, supported Product/Offer markup for photographed listed products, robots.txt, sitemap.xml and llms.txt support discovery. These do not guarantee indexation, AI inclusion, AdSense approval or rankings. No keyword-stuffed or invented reviews/specifications are generated.

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


## Item-first customer interface (30 October 2026)
The homepage leads with category icons and brand tiles, a compact daily market strip, and grouped item cards showing price ranges. Cards contain a single item-page link; source/store comparisons, visual price bars, original Urdu notifications and dated history live on item posts. Every priced and unpriced record has a working post. Unpriced generic items use explicitly labelled category illustrations when no verified item photo exists. Pakistan is the parent location, with cities nested beneath it and national offers always included. Category and brand archives reuse the saved location. The chart drawer, dashboard counters, raw downloads and sheet library are removed from the public dashboard. The existing daily workflow remains active; notification dates and failed-source dates are never advanced just to imply freshness.


## Search-led navigation
The homepage contains four essential market quotes and four curated multi-store model comparisons, rather than a full directory. No search-volume or popularity ranking is claimed without analytics. Full search lives at search.html (noindex/follow), category and brand archives remain crawlable, and laptops.html targets laptop/PC intent. All pages use category sidebar navigation, visible breadcrumbs and matching BreadcrumbList structured data. The homepage includes a short usage guide and factual source/update answers. SEO, AEO, AIO and GEO use useful text, crawlable links, original sources and visible-data-consistent metadata; inclusion and rankings are not guaranteed.
