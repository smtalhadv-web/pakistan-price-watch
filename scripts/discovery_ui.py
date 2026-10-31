"""Helpful navigation and source-led search discovery; no invented search-volume claims."""
import json,re
from catalog_ui import archive,E,groups_for
from model import CATS
from presentation import ICONS,store_name
MENU=[('items/gold-24k.html','Gold price'),('items/petrol.html','Petrol price'),('categories/mobiles.html','Mobile prices'),('laptops.html','Laptop prices'),('categories/grocery.html','Grocery prices'),('used-items.html','Used items'),('shares.html','Shares'),('blog.html','Business news'),('search.html','Search')]
# Small, consistent outline icons; no external icon dependency.
MENU_ICONS={
 'grocery':'M3 4h2l3 12h11l2-8H6 M9 20h.01 M18 20h.01',
 'produce':'M12 8c-7-5-11 5-6 11 3 4 5 1 6 1s3 3 6-1c5-6 1-16-6-11 M12 8c0-4 2-6 5-6 M12 6c-3 0-5-1-5-4 3 0 5 1 5 4',
 'meat':'M4 12c4-8 14-8 16-2s-4 12-10 11S1 18 4 12 M9 12c2-3 6-3 7-1s-2 5-4 5-4-2-3-4',
 'health':'M9 3h6v6h6v6h-6v6H9v-6H3V9h6Z',
 'baby':'M5 12a7 7 0 0 1 14 0 M5 12c-4-2-4 5 0 4a7 7 0 0 0 14 0c4 1 4-6 0-4 M9 13h.01 M15 13h.01 M9 17q3 3 6 0 M10 5q4 5 4 0',
 'pets':'M8 13c3-4 5-4 8 0 7 8-2 8-4 6-2 2-11 2-4-6 M7 8a2 3 0 1 0 0-.1 M17 8a2 3 0 1 0 0-.1 M3 12h.01 M21 12h.01',
 'mobiles':'M7 2h10v20H7Z M10 5h4 M11 19h2',
 'electronics':'M3 4h18v13H3Z M8 21h8 M12 17v4',
 'automobiles':'M3 11l3-6h12l3 6v7H3Z M3 11h18 M7 15h.01 M17 15h.01 M5 18v3 M19 18v3',
 'fuel':'M4 3h10v18H4Z M6 6h6v6H6Z M14 9h3v8c0 3 4 3 4 0V7l-3-3 M2 21h14',
 'household':'M3 10l9-7 9 7 M5 9v12h14V9 M9 21v-8h6v8',
 'furniture':'M5 11V5h14v6 M4 11H2v9h20v-9h-2 M4 11v5h16v-5 M4 20v2 M20 20v2',
 'construction':'M3 3h18v18H3Z M3 9h18 M3 15h18 M9 3v6 M15 9v6 M9 15v6',
 'machinery':'M14 3a6 6 0 0 0-7 7L2 19l3 3 9-9a6 6 0 0 0 7-7l-4 4-3-3 4-4Z',
 'services':'M14 3a6 6 0 0 0-7 7L2 19l3 3 9-9a6 6 0 0 0 7-7l-4 4-3-3 4-4Z',
 'property':'M4 21V3h12v18 M16 10h4v11 M8 7h4 M8 11h4 M8 15h4 M2 21h20',
 'apparel':'M8 3l-6 4 3 5 3-2v11h8V10l3 2 3-5-6-4c0 4-8 4-8 0Z',
 'sports':'M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0 M3 12h18 M12 3v18 M6 5q12 7 12 14 M18 5Q6 12 6 19',
 'stationery':'M3 3h7l2 2 2-2h7v17h-7l-2 2-2-2H3Z M12 5v17',
 'agriculture':'M12 21V10 M12 14C3 15 2 9 3 4c7-1 10 2 9 10 M12 10c0-6 4-8 9-7 1 6-2 9-9 9',
 'metals':'M6 5h12l4 8-10 9L2 13Z M2 13h20 M6 5l6 17 6-17',
 'currency':'M3 5h18v14H3Z M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0 M6 9h.01 M18 15h.01',
 'other':'M3 8h18v4H3Z M5 12v9h14v-9 M12 8v13 M12 8C3 8 5 0 10 4l2 4c9 0 7-8 2-4Z'}
MENU_GROUPS=[('Everyday essentials',['grocery','produce','meat','health','baby','pets']),('Technology & transport',['mobiles','electronics','automobiles','fuel']),('Home & work',['household','furniture','construction','machinery','services','property']),('Lifestyle & markets',['apparel','sports','stationery','agriculture','metals','currency','other'])]
def menu_icon(category):
 return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="'+MENU_ICONS.get(category,MENU_ICONS['other'])+'"/></svg>'
_sidebar_cache={}
_row_index={}
def sidebar_for(rows,prefix,path):
 key=id(rows)
 if key not in _row_index:
  _row_index[key]={**{'items/'+r['id']+'.html':r for r in rows},**{'items/'+r['canonical_id']+'.html':r for r in rows},**{'subcategories/'+r['subcategory_slug']+'.html':r for r in rows},**{'categories/'+r['category']+'.html':r for r in rows}}
 active_category=_row_index[key].get(path,{}).get('category','')
 cachekey=(key,prefix,active_category)
 if cachekey in _sidebar_cache:return _sidebar_cache[cachekey]
 sidebar='<button class="category-toggle" aria-expanded="false" aria-controls="category-sidebar">Categories</button><button class="sidebar-backdrop" aria-label="Close categories" hidden></button><aside id="category-sidebar" class="category-sidebar" aria-label="Category menu"><div class="sidebar-heading"><div><small>PAKISTAN PRICE WATCH</small><strong>Explore categories</strong><p>Find your item. Compare prices.</p></div><button class="sidebar-close" aria-label="Close categories">×</button></div><nav aria-label="Price categories">'
 listed=set()
 groups=MENU_GROUPS+[('More categories',[k for k in CATS if not any(k in keys for _,keys in MENU_GROUPS)])]
 for label,keys in groups:
  keys=[k for k in keys if k in CATS]
  if not keys:continue
  sidebar+='<div class="menu-group"><h2>'+E(label)+'</h2>'
  for k in keys:
   v=CATS[k];listed.add(k);items=[r for r in rows if r['category']==k];subs=sorted({(r['subcategory_slug'],r['subcategory'])for r in items});active=active_category==k
   sidebar+='<details class="category-branch"'+(' open' if active else '')+'><summary><span class="menu-icon">'+menu_icon(k)+'</span><span class="category-label">'+E(v)+'</span></summary><div class="category-children"><a class="browse-category" href="'+prefix+'categories/'+k+'.html">View all '+E(v)+' <span aria-hidden="true">→</span></a>'
   for slug,name in subs:
    sidebar+='<details class="subcategory-branch" data-submenu="'+E(slug)+'"><summary>'+E(name)+'</summary><a href="'+prefix+'subcategories/'+E(slug)+'.html">View all '+E(name)+' →</a><div class="submenu-items"></div></details>'
   sidebar+='</div></details>'
  sidebar+='</div>'
 sidebar+='</nav><nav class="sidebar-hubs" aria-label="Market hubs"><h2>More to explore</h2>'+''.join('<a href="'+prefix+target+'">'+E(label)+'<span aria-hidden="true">↗</span></a>'for target,label in [('search.html','All prices'),('shares.html','Shares & stocks'),('used-items.html','Used items'),('brands.html','Browse brands'),('blog.html','Business & trade news'),('predictor.html','Price predictor'),('wholesale.html','Wholesale prices')])+'</nav></aside>'

 _sidebar_cache[cachekey]=sidebar
 return sidebar

def chrome(title,body,path,prefix,rows,base):
 sidebar=sidebar_for(rows,prefix,path)
 crumbs=[('Home',prefix+'index.html')]
 if path.startswith('items/'):
  r=_row_index[id(rows)].get(path)
  if r:crumbs.append((CATS[r['category']],prefix+'categories/'+r['category']+'.html'));crumbs.append((r['subcategory'],prefix+'subcategories/'+r['subcategory_slug']+'.html'));current=r['name']
  else:current=title
 elif path.startswith('categories/'):current=CATS.get(path.split('/')[-1][:-5],title)
 elif path.startswith('subcategories/'):
  r=next((r for r in rows if path=='subcategories/'+r.get('subcategory_slug','')+'.html'),None)
  if r:crumbs.append((CATS[r['category']],prefix+'categories/'+r['category']+'.html'));current=r['subcategory']
  else:current=title
 elif path.startswith('brands/'):crumbs.append(('Brands',prefix+'brands.html'));current=title
 else:current={'index.html':'Pakistan price comparison','search.html':'Search prices','brands.html':'Brands','laptops.html':'Laptop prices'}.get(path,title)
 crumbs.append((current,None))
 breadcrumb='<nav class="breadcrumbs" aria-label="Breadcrumb"><ol>'+''.join('<li>'+('<a href="'+E(url)+'">'+E(name)+'</a>'if url else'<span aria-current="page">'+E(name)+'</span>')+'</li>'for name,url in crumbs)+'</ol></nav>'
 schema={'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':i+1,'name':name,'item':base+'/'+(re.sub(r'^(?:\.\./)+','',url)if url else path)}for i,(name,url)in enumerate(crumbs)]}
 if path=='index.html':
  breadcrumb='';schema={'@context':'https://schema.org','@type':'WebSite','name':'Pakistan Price Watch','url':base+'/','description':'Independent Pakistan price comparison with original sources, cities, units and dates.'}
 body='<div class="discovery-layout">'+sidebar+'<div class="discovery-content">'+breadcrumb+body+'</div></div><script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False).replace('<','\\u003c')+'</script>'
 return body

def home(rows,market):
 groups=groups_for([r for r in rows if r['price']is not None and r['city']=='Pakistan'])
 multiple=[p for p in groups.values()if len({store_name(x)for x in p})>1]
 selected=[]
 # A small everyday selection; exact groups retain all collected variants and sources.
 for pattern in [r'\b(?:wheat flour|atta)\b',r'\b(?:uht milk|milk uht)\b',r'\b(?:banana|bananas)\b',r'\b(?:cooking oil)\b']:
  candidates=[g for g in groups.values() if re.search(pattern,g[0]['name'],re.I)]
  if candidates:selected+=sorted(candidates,key=lambda g:(g[0]['category'] not in ['grocery','produce','meat'],len(g[0]['name']),g[0]['name']))[0]
 if not selected:
  for g in multiple[:4]:selected+=g
 scene=''
 return '''<main id="main" class="home-layout focused-home"><section class="seo-hero"><div class="eyebrow">PAKISTAN PRICE COMPARISON</div><h1>Everyday prices,<br><span>made simple.</span></h1><p>Find your item. Compare dated prices across sources and cities, with exact sizes and variations in one place.</p><form class="home-search" action="search.html" method="get"><label class="visually-hidden" for="home-search">Search an item or model</label><input id="home-search" type="search" name="q" placeholder="Search flour, milk, mobiles or آٹا…"><button type="submit">Search prices</button></form><div class="hero-shortcuts"><a href="categories/grocery.html">Groceries</a><a href="categories/mobiles.html">Mobiles</a><a href="categories/produce.html">Fruit & vegetables</a><a href="categories/construction.html">Building materials</a><a href="search.html">All items →</a></div></section><section><div class="section-heading"><h2>Market at a glance</h2><a href="search.html">Browse all prices →</a></div><p class="muted">Published rates with their original dates. These are source observations, not live trading quotes.</p><div class="market-minis">'''+market+'''</div></section><section><h2>Everyday essentials</h2><p class="muted">A small selection of everyday items. Open an item to compare sources, cities and exact variations.</p>'''+archive(selected)+'''</section><section class="how-it-works"><h2>New here? Compare in three steps</h2><div class="steps"><article><b>1 · Choose your city</b><p>Compare city-specific rates alongside online offers available across Pakistan.</p></article><article><b>2 · Find an item</b><p>Use search or the category sidebar. Switch between list and grid. Open an item for the full comparison.</p></article><article><b>3 · Check the details</b><p>Compare sources, variants and dates on the item page, then visit the seller or official notification.</p></article></div></section><section class="answer-section"><h2>Where do Pakistan Price Watch prices come from?</h2><p>We link to PSO fuel publications, Commissioner Karachi rate sheets, Pakistan Bureau of Statistics surveys, reported gold/currency benchmarks and published retailer or manufacturer listings. Official ceilings, survey averages and store offers are labelled separately.</p><h3>Are these prices updated daily?</h3><p>Supported sources are fetched twice daily at 08:30 and 20:30 Pakistan time. The last actual check is shown above; individual quotes show whether their source was verified. A source may publish weekly, monthly or only when rates change. Every item retains its actual source date; failed checks do not make an older price current.</p><h3>Why can the same item have different prices?</h3><p>Different stores, storage sizes, grades, warranty, stock, taxes or delivery terms can change the offer. Read the full variant and source date before comparing. A model match does not guarantee identical options.</p><h3>Is this an official government website?</h3><p>No. This is an independent comparison reference. Original government notifications and retailer pages are linked on the item detail pages so you can verify each quote.</p></section>'''+scene+'</main>'
