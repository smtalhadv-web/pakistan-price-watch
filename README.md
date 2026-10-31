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


## Taxonomy and image checks
A shared word-boundary taxonomy is applied both during the daily import and at build time. Sandals cannot match construction sand; household appliances, gaming chairs, grooming devices, tools, phone accessories and handsets use subject rules. Survey prices, units, source dates and history are untouched by categorization. Product images retain their source; freely licensed representative subject photos carry file attribution and are explicitly not asserted to match an unspecified survey grade or SKU. Where no verified photograph exists, every item receives a named item illustration, labelled as such. The image registry refreshes on the existing daily workflow, preserving previous metadata on failed requests.


## Additional source readers and market hubs
`partner_sources.py` writes a separate positive `partner-prices.json` feed and `partner-history.json`. Current bounded reads cover two Chase Value catalog pages, Naheed groceries/vegetables, Paklap laptops/deals, Metro public default-page offers, Kifayah PECHS Karachi via Foodpanda's public product cards, and public OLX asking listings for iPhone, laptop and sofa searches. No seller names, contact details, account identifiers or precise residential locations are copied. OLX amounts in Lac/Lakh/Crore are normalized to PKR; date means observed, not published. Used/new/unknown seller conditions are not mixed into retail model groups. Metro branch/pack-unconfirmed offers cannot be auto-merged into a verified comparison.

The source-coverage page distinguishes real integrations from research links. Daraz, Imtiaz, Chase Up, Krave Mart, Facebook Marketplace, Google/Meta ads and news do not have verified numeric feeds connected. Kifayah and Paklap are independent source identities. Wholesale pages retain dated official wholesale/farm-gate references and do not imply actual mandi transactions. The shares hub links to official PSX research; numeric quotes, histories and forecasts require redistribution rights and are not republished.

Subcategory pages, source/type filters and a separate classified-asking hub are generated. An experimental next-day carry-forward scenario is shown only for eligible reported daily benchmarks with enough consecutive same-source history and a current observation. It displays an empirical range, small-sample one-day backtest error and limitations; no calibrated confidence, trading signal or guaranteed future price is claimed. Documentary Pakistani market photographs are attributed to their freely licensed original Commons files, rather than treated as reusable merely because Google indexes them.

### Category navigation, wholesale and news

The fixed desktop sidebar scrolls independently; mobile navigation opens as a drawer.
Categories expand to subcategories and item links. Every category archive includes
scoped search, city, subcategory, brand, source, unit/pack, condition (when present),
price range, quote type and sorting controls. Unknown products stay in an explicitly
unclassified group. Product photos remain; bazaar photos and source-directory pages
are no longer published.

`python scripts/news.py` refreshes three dated economy/business/trade news briefings
from recent Google News RSS search results. Posts contain attributed headlines,
publisher links, publication times and editorial context; article bodies are not
copied. The existing GitHub Actions schedule runs this daily at 07:30 Pakistan time.
Failed feeds retain prior dated posts and display an incomplete-refresh notice.

Wholesale sections match explicit wholesale/farm-gate notices by normalized product,
category, city, unit, publisher and effective date. No bulk discount is inferred from
retail offers. Missing wholesale quotes remain unavailable.

### Daily multi-source and city comparison

Filters are collapsed until the visitor clicks **Filters**. Pakistan shows all cities;
a selected city also includes online offers available across Pakistan. City labels do
not use “national”.

`products.py` separates product groups from exact variations. Color, capacity and pack
choices share a product card and canonical item URL; quote tables and price histories
filter by exact variation and city. Used listings stay separate. Duplicate source
observations retain the newest dated quote; old item links continue via aliases.
Different grades, quote bases, cities and pack units remain identifiable.

Additional daily readers in `extra_sources.py` fetch public Al-Fatah, Shophive and
Mega.pk listings. Source names, dates, exact quotes and extra research links appear on
item detail pages. A research search link never counts as a verified competing price.

### Twice-daily live source refresh

The Pages workflow now fetches current source data on scheduled runs, manual runs and
code pushes. Schedule: **08:30 and 20:30 Asia/Karachi** (`30 3,15 * * *` UTC).
GitHub may delay a scheduled start. A separate scheduled guard checks missed/failed
refreshes and can retrigger the existing push workflow without creating duplicate runs.

`update.py` runs `refresh.py`: bounded stages, retained valid data on failure, and a
machine-readable `data/refresh-status.json`. A run with zero freshly verified quotes
fails rather than reporting success. Partial source availability is explicit.

`last_checked_at` records a successfully parsed source observation; `date` retains
the source publication/effective date or the actual retailer observation date.
Reimporting manual transcriptions does not certify a newer notice. Source dates
are never advanced merely because a build or scheduled check ran.

The website shows the last completed price check, verification/retention counts and
per-offer verification timestamps. Open tabs check for a newly published refresh
about every five minutes and when returning to the tab, then reload the new data.
