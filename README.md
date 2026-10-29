# Pakistan Price Watch

Buildless, responsive price portal for GitHub Pages. No paid services, secret tokens in the frontend, accounts, or fabricated quotes.

## Publish
1. Create a **new public repository** named `pakistan-price-watch` in GitHub. Upload all source files, including `.github/workflows/pages.yml`, keeping their folders.
2. In Settings → Pages → Build and deployment, select **GitHub Actions**.
3. Open Actions → Refresh prices and publish Pages → Run workflow. The deploy job returns the live URL.
4. Ensure Actions has read/write repository permission if the daily commit step is denied. This workflow requests contents:write, pages:write and id-token:write.

## Daily manual fallback
Open `editor.html` on the website → Load published data → edit records or import CSV/JSON → Validate & preview → Download prices.json. Open `data/prices.json` in your GitHub repository and replace its contents with the downloaded JSON. Commit to main; Pages rebuilds automatically. The editor only prepares a file; it is not a public write endpoint. Repository access controls publishing.

Source categories: fuel, produce, meat, metals, currency, construction, electronics. Each quote needs a unique lowercase id, name, category, city, numeric positive price, unit, ISO date, kind and HTTPS source URL. Add individual source-linked records for fruit, vegetables and meat only after reading the official sheets.

## Automation scope
Daily schedule: 07:30 Pakistan time (02:30 UTC); GitHub may delay scheduled runs. The scheduled workflow attempts dated PSO fuel extraction. Other categories remain manual until reliable permitted adapters are implemented. `data/update-report.json` records check failures and manual queue; stale rates retain their original effective date. Run the workflow manually any time. GitHub can disable scheduled workflows in inactive public repositories; check Actions regularly.

The PSO adapter passed fixture tests and a live source fetch in the build environment. GitHub runner execution still needs deployment verification. HTML changes, blocking and network failures are handled by keeping prior quotes. It will never read the Commissioner website's placeholder 0.00 as a price. That website provides actual rates in image attachments, requiring manual verification.

## Local build
Python 3.10+: `python -m unittest discover -s tests -v` then `python scripts/build.py`. Serve `dist` using `python -m http.server 8000 --directory dist`.

Set SITE_URL to the final Pages URL for sitemap generation. The GitHub workflow does this automatically. Static item pages provide crawlable text, dates and source links without JavaScript. No rankings, AdSense approval or revenue are guaranteed. No ad account has been added.

## Data provenance
Initial quotes were read from PSO, Hamariweb and PriceOye on 30 October 2026; effective dates are in each record. Metal quotes are secondary published benchmarks, not independently verified direct association feeds. Retail listings need exact variant/stock checks before purchase. The portal is independent and must not be presented as an official government service. Check source terms before scaling or republishing at volume.
