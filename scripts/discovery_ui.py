"""Helpful navigation and source-led search discovery; no invented search-volume claims."""
import json,re
from catalog_ui import archive,E,groups_for
from model import CATS
from presentation import ICONS,store_name
MENU=[('items/gold-24k.html','Gold price'),('items/petrol.html','Petrol price'),('categories/mobiles.html','Mobile prices'),('laptops.html','Laptop prices'),('categories/grocery.html','Grocery prices'),('brands.html','Brands'),('search.html','Search')]
def chrome(title,body,path,prefix,rows,base):
 sidebar='<aside class="category-sidebar"><details open><summary>Browse categories</summary><nav aria-label="Price categories">'+''.join('<a'+(' aria-current="page"'if path=='categories/'+k+'.html'else'')+' href="'+prefix+'categories/'+k+'.html"><span aria-hidden="true">'+ICONS[k]+'</span>'+E(v)+'</a>'for k,v in CATS.items())+'</nav></details></aside>'
 crumbs=[('Home',prefix+'index.html')]
 if path.startswith('items/'):
  r=next((r for r in rows if r['id']==path.split('/')[-1][:-5]),None)
  if r:crumbs.append((CATS[r['category']],prefix+'categories/'+r['category']+'.html'));current=r['name']
  else:current=title
 elif path.startswith('categories/'):current=CATS.get(path.split('/')[-1][:-5],title)
 elif path.startswith('brands/'):crumbs.append(('Brands',prefix+'brands.html'));current=title
 else:current={'index.html':'Pakistan price comparison','search.html':'Search prices','brands.html':'Brands','laptops.html':'Laptop prices'}.get(path,title)
 crumbs.append((current,None))
 breadcrumb='<nav class="breadcrumbs" aria-label="Breadcrumb"><ol>'+''.join('<li>'+('<a href="'+E(url)+'">'+E(name)+'</a>'if url else'<span aria-current="page">'+E(name)+'</span>')+'</li>'for name,url in crumbs)+'</ol></nav>'
 schema={'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':i+1,'name':name,'item':base+'/'+(re.sub(r'^(?:\.\./)+','',url)if url else path)}for i,(name,url)in enumerate(crumbs)]}
 if path=='index.html':
  breadcrumb='';schema={'@context':'https://schema.org','@type':'WebSite','name':'Pakistan Price Watch','url':base+'/','description':'Independent Pakistan price comparison with original sources, locations, units and dates.'}
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
 return '''<main id="main" class="home-layout focused-home"><section class="seo-hero"><div class="eyebrow">PAKISTAN PRICE COMPARISON</div><h1>Compare prices in Pakistan.<br><span>Know the source. Check the date.</span></h1><p>Find gold, petrol, mobile, laptop and grocery prices. Open an item to compare published store offers, check city rates and explore its price history.</p><form class="home-search" action="search.html" method="get"><label class="visually-hidden" for="home-search">Search an item or model</label><input id="home-search" type="search" name="q" placeholder="Try iPhone, Redmi, gold, petrol or آٹا…"><button type="submit">Find prices →</button></form><div class="hero-shortcuts"><a href="categories/mobiles.html">Mobile phones</a><a href="laptops.html">Laptops & PCs</a><a href="categories/produce.html">Fruit & vegetables</a><a href="categories/meat.html">Meat & poultry</a></div></section><section><div class="section-heading"><h2>Daily price essentials</h2><a href="search.html">Browse all prices →</a></div><p class="muted">Published rates with their original dates. These are source observations, not live trading quotes.</p><div class="market-minis">'''+market+'''</div></section><section><h2>Featured store comparisons</h2><p class="muted">A short editorial selection with more than one verified store. These are not measured search-volume rankings. Storage, kits and warranty may differ.</p>'''+archive(selected)+'''</section><section class="how-it-works"><h2>New here? Compare in three steps</h2><div class="steps"><article><b>1 · Choose your city</b><p>National Pakistan listings are included automatically. Other cities are excluded from the archive.</p></article><article><b>2 · Find an item</b><p>Use search or the category sidebar. Cards show a price range instead of a long supplier list.</p></article><article><b>3 · Check the details</b><p>Compare sources, variants and dates on the item page, then visit the seller or official notification.</p></article></div></section><section class="answer-section"><h2>Where do Pakistan Price Watch prices come from?</h2><p>We link to PSO fuel publications, Commissioner Karachi rate sheets, Pakistan Bureau of Statistics surveys, reported gold/currency benchmarks and published retailer or manufacturer listings. Official ceilings, survey averages and store offers are labelled separately.</p><p><a href="methodology.html">Read the source and correction methodology →</a></p><h3>Are these prices updated daily?</h3><p>Supported sources are checked each day at 07:30 Pakistan time. A source may publish weekly, monthly or only when rates change. Every item retains its actual source date; failed checks do not make an older price current.</p><h3>Why can the same item have different prices?</h3><p>Different stores, storage sizes, grades, warranty, stock, taxes or delivery terms can change the offer. Read the full variant and source date before comparing. A model match does not guarantee identical options.</p><h3>Is this an official government website?</h3><p>No. This is an independent comparison reference. Original government notifications and retailer pages are linked on the item detail pages so you can verify each quote.</p></section></main>'''
