import json,pathlib,html,shutil,os,re,math,datetime,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
from model import CATS,mode
from taxonomy import normalize
from item_images import apply_images
from presentation import comparison_key, store_name, enhance, item_content, ICONS

def validate(rows):
 ids=set()
 for r in rows:
  assert re.fullmatch(r'[a-z0-9-]+',r['id']),'Invalid item ID'
  assert r['id'] not in ids,'Duplicate item ID';ids.add(r['id'])
  assert r['category'] in CATS
  assert isinstance(r['price'],(int,float)) and not isinstance(r['price'],bool) and math.isfinite(r['price']) and 0<r['price']<1e10
  assert r['source'].startswith('https://')
  datetime.date.fromisoformat(r['date'])
  assert all(isinstance(r.get(k),str) and r[k].strip() for k in ['name','unit','city','kind'])
 return rows
from catalog_ui import family,groups_for,archive,detail,graph,photo
from discovery_ui import chrome,home,MENU
from market_features import subgroup,feature_pages

def build():
 priced=validate(json.loads((ROOT/'data/prices.json').read_text()));catalog=[]
 if (ROOT/'data/partner-prices.json').exists():priced+=validate(json.loads((ROOT/'data/partner-prices.json').read_text()))
 if (ROOT/'data/extra-prices.json').exists():priced+=validate(json.loads((ROOT/'data/extra-prices.json').read_text()))
 for fn in ['catalog.json','extra-catalog.json']:catalog+=json.loads((ROOT/'data'/fn).read_text())
 normalize(priced);normalize(catalog)
 ids={r['id']for r in priced};rows=priced+[r for r in catalog if r['id']not in ids]
 from products import deduplicate,prepare
 rows,aliases=deduplicate(rows)
 priced=[r for r in rows if r['price'] is not None]
 for r in rows:
  r['category_label']=CATS[r['category']];r['pricing_mode']=mode(r);r['subcategory'],r['subcategory_slug']=subgroup(r);r['store']=store_name(r)
  if 'priceoye.pk/mobiles/'in (r.get('source')or'')and not r.get('brand'):r['brand']=r['source'].split('/mobiles/')[1].split('/')[0].title()
 prepare(rows)
 from wholesale import attach
 attach(rows)
 groups=groups_for(rows);hist=json.loads((ROOT/'data/history.json').read_text());hist.update(json.loads((ROOT/'data/partner-history.json').read_text())if(ROOT/'data/partner-history.json').exists()else{});hist.update(json.loads((ROOT/'data/extra-history.json').read_text())if(ROOT/'data/extra-history.json').exists()else{});out=ROOT/'dist';shutil.rmtree(out,ignore_errors=True);out.mkdir()
 for f in ['style.css','app.js']:shutil.copy(ROOT/f,out/f)
 (out/'data').mkdir();shutil.copytree(ROOT/'assets',out/'assets');(out/'admin').mkdir();(out/'admin/.gitkeep').touch()
 for cat,label in CATS.items():
  (out/'assets'/('category-'+cat+'.svg')).write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300"><rect width="400" height="300" rx="24" fill="#edf4ee"/><text x="200" y="145" font-size="75" text-anchor="middle">'+ICONS[cat]+'</text><text x="200" y="210" font-family="sans-serif" font-size="17" text-anchor="middle" fill="#315b48">'+html.escape(label)+'</text><text x="200" y="250" font-family="sans-serif" font-size="12" text-anchor="middle" fill="#6c8577">CATEGORY ILLUSTRATION</text></svg>')
 apply_images(rows,out)
 for old,target in aliases.items():
  merged={p['date']:p for p in hist.get(old,[])};merged.update({p['date']:p for p in hist.get(target,[])})
  hist[target]=sorted(merged.values(),key=lambda p:p['date'])
 for r in priced:
  a=hist.setdefault(r['id'],[])
  if not any(p['date']==r['date']and p['price']==r['price']for p in a):
   a[:]=[p for p in a if p['date']!=r['date']];a.append(dict(date=r['date'],price=r['price'],source=r['source']));a.sort(key=lambda p:p['date'])
 (out/'data/directory.json').write_text(json.dumps(rows,ensure_ascii=False,separators=(',',':')));(out/'data/history.json').write_text(json.dumps(hist,ensure_ascii=False,separators=(',',':')))
 E=lambda x:html.escape(str(x or''),quote=True);version=hashlib.sha256((ROOT/'app.js').read_bytes()+(ROOT/'style.css').read_bytes()+(ROOT/'data/prices.json').read_bytes()+(ROOT/'data/history.json').read_bytes()+(ROOT/'scripts/catalog_ui.py').read_bytes()+(ROOT/'scripts/discovery_ui.py').read_bytes()+(ROOT/'scripts/build.py').read_bytes()+(ROOT/'scripts/taxonomy.py').read_bytes()+(ROOT/'scripts/market_features.py').read_bytes()+(ROOT/'scripts/partner_sources.py').read_bytes()+((ROOT/'data/partner-prices.json').read_bytes()if(ROOT/'data/partner-prices.json').exists()else b'')+(ROOT/'scripts/item_images.py').read_bytes()+((ROOT/'data/item-images.json').read_bytes()if(ROOT/'data/item-images.json').exists()else b'')).hexdigest()[:12];base=os.environ.get('SITE_URL','https://smtalhadv-web.github.io/pakistan-price-watch').rstrip('/')
 cities=sorted({r['city']for r in rows if r['city']not in ['Pakistan','Location unconfirmed']})
 options='<option value="Pakistan">Pakistan · All cities</option><optgroup label="↳ Cities in Pakistan">'+''.join('<option value="'+E(c)+'">↳ '+E(c)+'</option>'for c in cities)+'</optgroup>'
 location='<dialog id="location-dialog" class="location-dialog"><form id="location-form"><div class="eyebrow">YOUR LOCATION</div><h2>اپنا شہر منتخب کریں</h2><div class="country-parent">🇵🇰 Pakistan <strong>✓ Parent country</strong></div><p>City views also include online offers available across Pakistan.</p><label for="location-pick">Pakistan → City / شہر</label><select id="location-pick">'+options+'</select><p id="parent-confirm" lang="ur" dir="rtl">آپ کے منتخب شہر کے ساتھ پاکستان بھر میں دستیاب آن لائن نرخ بھی شامل ہیں۔</p><button class="primary" type="submit">Show prices / قیمتیں دکھائیں</button></form></dialog>'
 def page(title,body,path='index.html',prefix='',description=None):
  desc=description or title+'. Compare source-linked prices with locations, dates, original Urdu wording and separately identified supplier variants.'
  canonical_path=path
  if path.startswith('items/'):
   item=next((r for r in rows if path=='items/'+r['id']+'.html'),None)
   if item:canonical_path='items/'+item['canonical_id']+'.html'
  if 'id="archive-host"'in body:
   if 'class="archive-filters"' not in body:body=body.replace('<div id="archive-host">','<div class="archive-filters"></div><div id="archive-host">',1)
   body=re.sub(r'(<div class="archive-filters">.*?</div>)',r'<details class="filter-panel"><summary>Filters <span>Search, city, variation & price</span></summary>\1</details>',body,count=1,flags=re.S)
  body=chrome(title,body,path,prefix,rows,base)
  markup='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+E(title)+' | Pakistan Price Watch</title><meta name="description" content="'+E(desc)+'"><link rel="canonical" href="'+E(base+'/'+canonical_path)+'"><meta property="og:title" content="'+E(title)+'"><meta property="og:description" content="'+E(desc)+'"><link rel="stylesheet" href="'+prefix+'style.css?v='+version+'"></head><body><a class="skip" href="#main">Skip to content</a><header><a class="brand" href="'+prefix+'index.html?v='+version+'"><span class="brandmark">P<span>↗</span></span><span>PRICE<strong>WATCH</strong><small>PAKISTAN PRICE COMPARISON</small></span></a><nav aria-label="Main navigation">'+''.join('<a href="'+prefix+target+'">'+label+'</a>'for target,label in MENU)+'<button class="navbutton" data-open-location>📍 <span class="current-location">Pakistan</span></button></nav></header>'+body+'<footer><span>Pakistan Price Watch · Independent price reference</span><span>'+''.join('<a href="'+prefix+x+'.html">'+label+'</a> · 'for x,label in [('about','About'),('privacy','Privacy'),('terms','Terms'),('disclaimer','Disclaimer'),('contact','Contact'),('editorial-policy','Editorial policy')])+'</span></footer>'+location+'<script src="'+prefix+'app.js?v='+version+'" defer></script></body></html>'
  def stamp(match):
   target=match.group(1)
   if target.startswith(('https://','http://')):return match.group(0)
   return 'href="'+target+'?v='+version+'"'
  if path=='search.html':markup=markup.replace('<head>','<head><meta name="robots" content="noindex,follow">',1)
  return re.sub(r'href="([^"?]+\.html)"',stamp,markup)
 cattiles='<div class="category-grid">'+''.join('<a class="category-tile" href="categories/'+c+'.html"><span aria-hidden="true">'+ICONS[c]+'</span><strong>'+E(label)+'</strong></a>'for c,label in CATS.items())+'</div>'
 brands={}
 for r in rows:
  if r.get('brand'):brands.setdefault(r['brand'],[]).append(r)
 def brand_slug(b):return re.sub('[^a-z0-9]+','-',b.lower()).strip('-')+'-'+hashlib.sha256(b.encode()).hexdigest()[:6]
 def brandtiles(prefix='',limit=None):
  bs=sorted(brands.items(),key=lambda x:(-len(x[1]),x[0]));return '<div class="brand-strip">'+''.join('<a class="brand-tile" href="'+prefix+'brands/'+brand_slug(b)+'.html">'+photo(next((x for x in a if x.get('image')),a[0]),prefix)+'<strong>'+E(b)+'</strong></a>'for b,a in bs[:limit])+'</div>'
 market=''
 for id in ['gold-24k','silver','petrol','fx-us-dollar-open-market-sell']:
  r=next((x for x in priced if x['id']==id),None)
  if r:market+='<a class="market-mini" href="items/'+r['id']+'.html"><span class="market-photo">'+photo(r)+'</span><b>'+E(r['name'])+'</b><strong>PKR '+f'{r["price"]:,.2f}'+'</strong>'+graph(hist.get(id,[]),r['name'],True)+'<small>'+E(r['date'])+' · / '+E(r['unit'])+'</small></a>'
 body='<main id="main" class="home-layout"><div class="home-heading"><div class="eyebrow">FIND YOUR EVERYDAY PRICE</div><h1>Prices near you. <span>Compare with confidence.</span></h1><p>Choose a category or brand, then open an item for store comparisons and dated prices.</p></div><section><h2>Browse categories</h2>'+cattiles+'</section><section><div class="section-heading"><h2>Shop by brand</h2><a href="brands.html">All brands →</a></div>'+brandtiles(limit=12)+'</section><section class="compact-market"><h2>Daily market watch</h2><div class="market-minis">'+market+'</div></section><section id="prices"><div class="section-heading"><h2>Explore items</h2><span class="current-location">Pakistan</span></div><div class="archive-filters"><input id="search" type="search" aria-label="Search items" placeholder="Search an item, model or Urdu name…"><select id="city" aria-label="Location">'+options+'</select><select id="category" aria-label="Category"><option value="">All categories</option>'+''.join('<option value="'+c+'">'+E(v)+'</option>'for c,v in CATS.items())+'</select></div><p id="count" class="muted"></p><div id="archive-host">'+archive([r for r in rows if r['city']=='Pakistan'][:36])+'</div><div class="pagination"><button id="previous">← Previous</button><span id="page-label"></span><button id="next">Next →</button></div></section></main>'
 searchbody='<main id="main" class="home-layout"><h1>Search Pakistan prices</h1><p>Choose a city and search in English or Urdu. Open an item for its sources and price comparison.</p>'+body[body.index('<section id="prices">'):]
 (out/'search.html').write_text(page('Search Pakistan prices by item, city and brand',searchbody,'search.html'))
 (out/'index.html').write_text(page('Pakistan Price Comparison – Gold, Petrol, Mobiles & Groceries',home(rows,market),description='Compare published prices in Pakistan for gold, petrol, mobile phones, laptops and groceries. Check city rates, multiple stores, source dates and price histories.'));urls=['index.html','laptops.html'];(out/'items').mkdir(exist_ok=True);(out/'categories').mkdir(exist_ok=True);(out/'brands').mkdir(exist_ok=True)
 for c,label in CATS.items():
  items=[r for r in rows if r['category']==c];path='categories/'+c+'.html';body='<main id="main" class="home-layout" data-archive-category="'+c+'"><h1>'+ICONS[c]+' '+E(label)+'</h1><p>Open an item for the current source prices, store comparisons and dated history.</p><p class="current-location"></p><div class="subcategory-links">'+''.join('<a href="../subcategories/'+E(slug)+'.html">'+E(label)+'</a>'for slug,label in sorted({(r['subcategory_slug'],r['subcategory'])for r in items}))+'</div><div id="archive-host">'+archive([r for r in items if r['city']=='Pakistan'and mode(r)!='asking'],'../')+'</div><div class="pagination"><button id="previous">← Previous</button><span id="page-label"></span><button id="next">Next →</button></div></main>';(out/path).write_text(page(label+' prices in Pakistan',body,path,'../'));urls.append(path)
 items=[r for r in rows if r['category']=='electronics'and re.search(r'laptop|desktop|mini pc|workstation|macbook|thinkpad|vivobook|ideapad',r['name'],re.I)]
 laptopbody='<main id="main" class="home-layout" data-archive-topic="computers"><h1>Laptop and PC prices in Pakistan</h1><p>Compare published laptop and desktop listings. Check processor, RAM, storage, graphics, condition and warranty on each item page.</p><div id="archive-host">'+archive(items,'')+'</div><div class="pagination"><button id="previous">← Previous</button><span id="page-label"></span><button id="next">Next →</button></div></main>'
 (out/'laptops.html').write_text(page('Laptop and PC prices in Pakistan',laptopbody,'laptops.html'))
 for b,items in brands.items():
  path='brands/'+brand_slug(b)+'.html';body='<main id="main" class="home-layout" data-archive-brand="'+E(b)+'"><h1>'+E(b)+' prices</h1><p>Choose an item to inspect the listed variants, source dates and store comparison.</p><div id="archive-host">'+archive([r for r in items if r['city']=='Pakistan'and mode(r)!='asking'],'../')+'</div><div class="pagination"><button id="previous">← Previous</button><span id="page-label"></span><button id="next">Next →</button></div></main>';(out/path).write_text(page(b+' prices and products in Pakistan',body,path,'../'));urls.append(path)
 # Policy pages stay available without technical download links on the customer dashboard.
 def dummy_table(items,prefix=''):return archive(items,prefix)
 enhance(out,rows,priced,groups,page,dummy_table,urls,base,E)
 (out/'brands.html').write_text(page('Brands and products in Pakistan','<main id="main" class="home-layout"><h1>Browse brands</h1>'+brandtiles()+'</main>','brands.html'))
 method='<main id="main" class="prose panel"><h1>Sources and price methodology</h1><p>Official Commissioner Karachi notifications, PSO fuel publications, PBS weekly and monthly city surveys, reported metals/currency tables, and manufacturer/retailer listings have different price bases and are labelled separately.</p><p>Supported sources are checked daily at 07:30 Pakistan time. A daily check does not mean a new government notification has been issued. Source failures retain the last actual date. New image text requires verified transcription before publication; we do not invent dates or rates.</p><p>Original Urdu wording and English translation appear on relevant item pages alongside the original notification. Exact manufacturer models can be compared, while different kits, storage, warranty and condition remain visible. Missing prices are not zero.</p><p>Country-wide listings appear with every selected city. Item pages can show other-city comparisons explicitly. Graphs connect real observations of the same source and location, with no fabricated daily interpolation.</p></main>'

 def redirect_item(old,target,variant=''):
  destination=target+'.html'+('?variation='+variant if variant else'')
  (out/'items'/f'{old}.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex,follow"><meta http-equiv="refresh" content="0;url='+E(destination)+'"><link rel="canonical" href="'+E(base+'/items/'+target+'.html')+'"><title>Open product comparison</title></head><body><a href="'+E(destination)+'">Choose variation and compare prices</a></body></html>')
 for peers in groups.values():
  r=min(peers,key=lambda x:(x['price']is None,x['id']));path='items/'+r['canonical_id']+'.html'
  (out/path).write_text(page(r['product_name']+' prices in Pakistan',detail(r,peers,hist,rows),path,'../',r['product_name']+' daily price comparison in Pakistan. Compare sources, cities, exact variations, original quote dates and price history.'));urls.append(path)
 for r in rows:redirect_item(r['id'],r['canonical_id'],r['variant_key'])
 byid={r['id']:r for r in rows}
 for old,target in aliases.items():
  r=byid[target];redirect_item(old,r['canonical_id'],r['variant_key'])
 feature_pages(out,rows,page,urls,base)
 from news import publish
 news_cards=publish(out,page,urls)
 index=out/'index.html';text=index.read_text();text=text.replace('</main>', '<section><div class="section-heading"><h2>Economy, business & trade</h2><a href="blog.html">Daily briefings →</a></div>'+news_cards+'</section></main>',1);index.write_text(text)
 (out/'llms.txt').write_text((out/'llms.txt').read_text().replace('- [Methodology]('+base+'/methodology.html)\n',''))
 (out/'sitemap.xml').write_text('<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+E(base+'/'+u)+'</loc></url>'for u in dict.fromkeys(urls))+'</urlset>');(out/'.nojekyll').touch();print('Built',len(rows),'working item pages and',len(set(urls)),'crawlable pages')
if __name__=='__main__':build()
