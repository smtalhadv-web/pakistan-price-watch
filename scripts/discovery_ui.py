"""Helpful navigation and source-led search discovery; no invented search-volume claims."""
import json,re
from catalog_ui import archive,E,groups_for
from model import CATS
from presentation import ICONS,store_name
MENU=[('items/gold-24k.html','Gold price'),('items/petrol.html','Petrol price'),('categories/mobiles.html','Mobile prices'),('laptops.html','Laptop prices'),('categories/grocery.html','Grocery prices'),('used-items.html','Used items'),('shares.html','Shares'),('blog.html','Business news'),('search.html','Search')]
_sidebar_cache={}
_row_index={}
def sidebar_for(rows,prefix,path):
 key=id(rows)
 if key not in _row_index:
  _row_index[key]={**{'items/'+r['id']+'.html':r for r in rows},**{'items/'+r['canonical_id']+'.html':r for r in rows},**{'subcategories/'+r['subcategory_slug']+'.html':r for r in rows},**{'categories/'+r['category']+'.html':r for r in rows}}
 active_category=_row_index[key].get(path,{}).get('category','')
 cachekey=(key,prefix,active_category)
 if cachekey in _sidebar_cache:return _sidebar_cache[cachekey]
 sidebar='<button class="category-toggle" aria-expanded="false" aria-controls="category-sidebar">☰ Categories</button><button class="sidebar-backdrop" aria-label="Close categories" hidden></button><aside id="category-sidebar" class="category-sidebar" aria-label="Category menu"><div class="sidebar-heading">Browse categories<button class="sidebar-close" aria-label="Close categories">×</button></div><nav aria-label="Price categories">'
 for k,v in CATS.items():
  items=[r for r in rows if r['category']==k];subs=sorted({(r['subcategory_slug'],r['subcategory'])for r in items});active=active_category==k
  sidebar+='<details class="category-branch"'+(' open' if active else '')+'><summary><span aria-hidden="true">'+ICONS[k]+'</span>'+E(v)+'</summary><a href="'+prefix+'categories/'+k+'.html">All '+E(v)+'</a>'
  for slug,label in subs:
   sidebar+='<details class="subcategory-branch" data-submenu="'+E(slug)+'"><summary>'+E(label)+'</summary><a href="'+prefix+'subcategories/'+E(slug)+'.html">Browse all '+E(label)+' →</a><div class="submenu-items"></div></details>'
  sidebar+='</details>'
 sidebar+='</nav><nav class="sidebar-hubs" aria-label="Market hubs"><a href="'+prefix+'brands.html">Browse brands</a><a href="'+prefix+'blog.html">Economy, business & trade</a><a href="'+prefix+'predictor.html">Price predictor</a><a href="'+prefix+'wholesale.html">Wholesale references</a></nav></aside>'

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
 for name in ['Xiaomi Redmi Note 15 Pro','Xiaomi Redmi Note 15','Xiaomi 17 Ultra']:
  g=next((g for g in multiple if any(x['name']==name for x in g)),None)
  if g:selected+=g
 other=next((g for g in multiple if g[0]['category']=='machinery'),None)
 if other:selected+=other
 scene=''
 return '''<main id="main" class="home-layout focused-home"><section class="seo-hero"><div class="eyebrow">PAKISTAN PRICE COMPARISON</div><h1>Daily prices. Multiple sources.<br><span>Compare your city. Choose your variation.</span></h1><p>Check daily price updates for groceries, fuel, gold and everyday products. Choose an item to compare sources, cities, exact variations and dated price history.</p><form class="home-search" action="search.html" method="get"><label class="visually-hidden" for="home-search">Search an item or model</label><input id="home-search" type="search" name="q" placeholder="Try iPhone, Redmi, gold, petrol or آٹا…"><button type="submit">Find prices →</button></form><div class="hero-shortcuts"><a href="categories/mobiles.html">Mobile phones</a><a href="laptops.html">Laptops & PCs</a><a href="categories/produce.html">Fruit & vegetables</a><a href="categories/meat.html">Meat & poultry</a></div></section><section><div class="section-heading"><h2>Daily price essentials</h2><a href="search.html">Browse all prices →</a></div><p class="muted">Published rates with their original dates. These are source observations, not live trading quotes.</p><div class="market-minis">'''+market+'''</div></section><section><h2>Featured store comparisons</h2><p class="muted">A short editorial selection with more than one verified store. These are not measured search-volume rankings. Storage, kits and warranty may differ.</p>'''+archive(selected)+'''</section><section class="how-it-works"><h2>New here? Compare in three steps</h2><div class="steps"><article><b>1 · Choose your city</b><p>Compare city-specific rates alongside online offers available across Pakistan.</p></article><article><b>2 · Find an item</b><p>Use search or the category sidebar. Cards show a price range instead of a long supplier list.</p></article><article><b>3 · Check the details</b><p>Compare sources, variants and dates on the item page, then visit the seller or official notification.</p></article></div></section><section class="answer-section"><h2>Where do Pakistan Price Watch prices come from?</h2><p>We link to PSO fuel publications, Commissioner Karachi rate sheets, Pakistan Bureau of Statistics surveys, reported gold/currency benchmarks and published retailer or manufacturer listings. Official ceilings, survey averages and store offers are labelled separately.</p><h3>Are these prices updated daily?</h3><p>Supported sources are checked each day at 07:30 Pakistan time. A source may publish weekly, monthly or only when rates change. Every item retains its actual source date; failed checks do not make an older price current.</p><h3>Why can the same item have different prices?</h3><p>Different stores, storage sizes, grades, warranty, stock, taxes or delivery terms can change the offer. Read the full variant and source date before comparing. A model match does not guarantee identical options.</p><h3>Is this an official government website?</h3><p>No. This is an independent comparison reference. Original government notifications and retailer pages are linked on the item detail pages so you can verify each quote.</p></section>'''+scene+'</main>'
