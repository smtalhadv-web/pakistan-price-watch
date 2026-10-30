import json, pathlib, html, shutil, os
ROOT=pathlib.Path(__file__).resolve().parents[1]
CATS={'fuel':'Petroleum','produce':'Fruit & vegetables','meat':'Meat & poultry','metals':'Gold & silver','currency':'Currencies','construction':'Building materials','electronics':'Electronics'}
def validate(rows):
 ids=set()
 for r in rows:
  import re, math
  assert re.fullmatch(r'[a-z0-9-]+',r['id']), 'Invalid item ID'
  assert r['id'] not in ids,'Duplicate item ID'; ids.add(r['id'])
  assert r['category'] in CATS
  assert isinstance(r['price'],(int,float)) and not isinstance(r['price'],bool) and math.isfinite(r['price']) and 0<r['price']<1e10
  assert r['source'].startswith('https://')
  import datetime
  datetime.date.fromisoformat(r['date'])
  assert all(r.get(k) for k in ['name','unit','city','kind'])
 return rows
def build():
 rows=validate(json.loads((ROOT/'data/prices.json').read_text()))
 out=ROOT/'dist'; shutil.rmtree(out,ignore_errors=True);out.mkdir()
 for f in ['style.css','app.js','editor.html','editor.js']:shutil.copy(ROOT/f,out/f)
 shutil.copytree(ROOT/'data',out/'data')
 def card(r):
  e=lambda k:html.escape(str(r[k]),quote=True)
  return f'''<article class="card" data-category="{e('category')}" data-city="{e('city')}" data-name="{e('name')}"><div class="eyebrow">{html.escape(CATS[r['category']])} · {e('city')}</div><h3><a href="items/{e('id')}.html">{e('name')}</a></h3><div class="price">Rs {r['price']:,.2f}<span> / {e('unit')}</span></div><p class="badge">{e('kind')}</p><p>Effective / quoted: <time datetime="{e('date')}">{e('date')}</time></p><p class="freshness" data-date="{e('date')}"></p><a href="{e('source')}" target="_blank" rel="noopener noreferrer">View original source ↗</a></article>'''
 def page(title,content,prefix=''):
  return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} | Pakistan Price Watch</title><meta name="description" content="Source-linked Pakistan prices with effective dates, city filters and official versus market labels. Check fuel, food, metals and electronics."><link rel="stylesheet" href="{prefix}style.css"></head><body><header><a class="brand" href="{prefix}index.html">◈ Pakistan <strong>Price Watch</strong></a><nav><a href="{prefix}index.html#prices">Explore prices</a><a href="{prefix}methodology.html">Our sources</a><a href="{prefix}editor.html">Update desk</a></nav></header>{content}<footer>Pakistan Price Watch · Independent price reference. Source dates matter.<br><a href="{prefix}methodology.html">Methodology & privacy</a></footer><script src="{prefix}app.js" defer></script></body></html>'''
 content='''<main><section class="hero"><div class="eyebrow">PAKISTAN'S EVERYDAY PRICE REFERENCE</div><h1>Know the price.<br><em>See the source.</em></h1><p>Fuel, food, metals and more — with transparent dates and a clear distinction between official rates and market listings.</p><a class="primary" href="#prices">Explore the price board ↓</a></section><div class="notice">Initial verified source snapshots. These are not guaranteed live transaction prices. Older quotes stay dated until a new source is verified.</div><section id="prices"><div class="sectionhead"><h2>The price board</h2><a href="data/prices.json" download>Download data ↗</a> · <a href="data/update-report.json">Update status ↗</a></div><div class="filters"><label>Search items<input id="search" type="search" placeholder="Petrol, gold, Samsung…"></label><label>City<select id="city"><option value="">All locations</option><option>Pakistan</option><option>Karachi</option></select></label><label>Category<select id="category"><option value="">All categories</option>'''+''.join(f'<option value="{k}">{v}</option>' for k,v in CATS.items())+'''</select></label></div><p id="count" aria-live="polite"></p><div class="grid">'''+''.join(map(card,rows))+'''</div><p id="empty" hidden>No matching prices. Try another filter.</p></section><section><h2>More categories, responsibly sourced</h2><div class="grid"><article class="card"><h3>Fruit, vegetables & meat</h3><p>Karachi official lists are published as images. Individual prices require transcription and verification.</p><a href="https://commissionerkarachi.gos.pk/karachi/pricelist">Open official rate sheets ↗</a></article><article class="card"><h3>Currency exchange</h3><p>Direct SBP extraction has not been verified. Add a dated bank or exchange quote through the update desk.</p><a href="https://www.sbp.org.pk/economic-data">SBP economic data ↗</a></article><article class="card"><h3>Construction materials</h3><p>PBS publishes periodic construction price reports. Daily dealer prices need a dated supplier quote.</p><a href="https://www.pbs.gov.pk/price-statistics/">PBS price statistics ↗</a></article></div></section></main>'''
 (out/'index.html').write_text(page('Pakistan prices with dated sources',content))
 (out/'methodology.html').write_text(page('Sources, methodology & privacy','''<main class="prose"><h1>Trust starts with a source.</h1><p>We are an independent reference, not a government service. Official notified rates, retailer listings and reported market benchmarks are labelled separately. A quote is not a guarantee of availability or final checkout cost.</p><h2>How updates work</h2><p>The scheduled workflow checks supported sources daily. Failed fetches retain the last source date and produce an update report. Image rate sheets and unsupported categories enter a manual verification queue. A successful check does not change a price's effective date.</p><h2>Corrections and manual updates</h2><p>Repository maintainers can use the update desk to validate and download a replacement data file, then commit it through GitHub. The public editor cannot publish changes and never asks for tokens.</p><h2>Units and comparisons</h2><p>Compare the same location, grade, weight, purity, model and warranty. SBP reference rates and cash exchange quotes differ. Gold jewellery making charges and retailer delivery fees may be additional.</p><h2>Privacy</h2><p>No analytics, advertising trackers or account system are included. The editor processes imported files in your browser. GitHub Pages may process access logs under GitHub's own privacy policy.</p></main>'''))
 (out/'items').mkdir()
 for r in rows:
  c=card(r).replace('href="items/','href="')
  (out/'items'/f"{r['id']}.html").write_text(page(r['name']+' price in '+r['city'],f'<main class="prose"><h1>{html.escape(r["name"])} price</h1>{c}<h2>Read this quote correctly</h2><p>This is the source-linked price for the unit and location shown. The effective date is preserved until a newer quote is verified. Check the original source before a purchase.</p></main>','../'))
 base=os.environ.get('SITE_URL','').rstrip('/')
 if base:
  urls=['index.html','methodology.html']+[f'items/{r["id"]}.html' for r in rows]
  (out/'sitemap.xml').write_text('<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{html.escape(base+"/"+u)}</loc></url>' for u in urls)+'</urlset>')
 (out/'.nojekyll').touch()
if __name__=='__main__':build()
