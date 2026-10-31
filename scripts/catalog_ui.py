import collections,html,json,re,hashlib
from model import CATS,mode
from freshness import badge,group_badge
from presentation import ICONS,store_name
E=lambda x:html.escape(str(x or''),quote=True)
def family(r):
 if r.get('comparison_eligible')is False:return'review-only|'+r['id']
 if r.get('family'):return r['family']
 if r.get('manufacturer_model')and r['category']=='machinery':return 'makita-model|'+r['manufacturer_model'].casefold()
 name=r['name'].split(' · ')[0]if mode(r)=='listed'else r['name']
 if mode(r)=='listed'and r['category']in ['grocery','health','household']:
  from decimal import Decimal
  def pack(match):
   value=Decimal(match[1]);unit=match[2].lower();value*=1000 if unit in ['kg','l','ltr','litre','liter','litres','liters']else 1;return (format(value,'f').rstrip('0').rstrip('.')if'.'in format(value,'f')else format(value,'f'))+('ml'if unit in ['ml','l','ltr','litre','liter','litres','liters']else'g')
  # Exact dimensional equivalence only; all brand, product-type and grade words are preserved.
  name=re.sub(r'\b(\d+(?:\.\d+)?)\s*(kg|gm|g|ml|litres?|liters?|ltr|l)\b',pack,name,flags=re.I)
 if r['category']=='mobiles':name=re.sub(r'^xiaomi (?=redmi|poco)','',name,flags=re.I)
 return '|'.join([r['category'],re.sub(r'[^\w]+',' ',name.casefold().replace('+',' plus ')).strip(),'product'if mode(r)=='listed'else r['unit'].casefold(),mode(r),r['kind']if mode(r)!='listed'else''])
def groups_for(rows):
 groups=collections.defaultdict(list)
 for r in rows:groups[family(r)].append(r)
 return groups

def photo(r,prefix=''):
 src=r.get('image')or'assets/category-'+r['category']+'.svg'
 if not src.startswith('https://'):src=prefix+src
 return '<img data-category="'+r['category']+'" data-fallback-src="'+E(prefix+r.get('fallback_image','assets/category-'+r['category']+'.svg'))+'" src="'+E(src)+'" alt="'+E(r['name']+(' · representative image'if r.get('image_kind')=='representative'else' · item illustration'if r.get('image_kind')=='illustration'else''))+'" loading="lazy" referrerpolicy="no-referrer">'
def archive(items,prefix=''):
 out='<div class="archive-grid" id="archive-grid">'
 for peers in groups_for(items).values():
  r=next((x for x in peers if x.get('image')),peers[0]);priced=[x for x in peers if x['price']is not None];vals=[x['price']for x in priced];lo=min(vals)if vals else None;hi=max(vals)if vals else None
  value=('PKR '+f'{lo:,.2f}'+(' – '+f'{hi:,.2f}'if hi!=lo else''))if vals else'قیمت دستیاب نہیں · Price unavailable'
  out+='<article class="archive-card" data-city="'+E('|'.join(sorted({x['city']for x in peers})))+'"><a class="product-title-link" href="'+prefix+'items/'+r.get('canonical_id',r['id'])+'.html">'+photo(r,prefix)+'<h3>'+E(r.get('product_name',r['name']))+'</h3></a>'
  if r.get('variant_count',1)>1:out+='<small class="variant-badge">'+str(r['variant_count'])+' variations · Choose variation →</small>'
  if r.get('urdu'):out+='<p id="product-urdu" class="original-urdu" lang="ur" dir="rtl">'+E(r['urdu'])+'</p>'
  out+=('<small class="quote-scope">'+E(r.get('condition','Condition not verified'))+'</small>'if mode(r)=='asking'else'<small class="quote-scope">Verify store area / pack before comparison</small>'if r.get('comparison_eligible')is False else'')
  out+='<small class="item-taxonomy">'+E(r.get('subcategory',''))+'</small>'
  quotes=r.get('wholesale_quotes',[])
  if quotes:out+='<small class="wholesale-badge">Wholesale from PKR '+f'{min(q["price"]for q in quotes):,.2f}'+' / '+E(r['unit'])+'</small>'
  out+='<strong class="range-price">'+value+'</strong>'+group_badge(peers)+'<p>'+E(r['unit'])+' · '+('Latest source '+max(x['date']for x in priced)if priced else'Exact specification / quote needed')+'</p></article>'
 return out+'</div>'
def graph(points,label,compact=False):
 if not points:return '<div class="history-pending">No dated price observation is available yet.</div>'
 if len(points)==1:
  p=points[0];return '<svg class="history-graph" viewBox="0 0 720 170" role="img" aria-label="One recorded source price; no trend"><line x1="70" y1="120" x2="690" y2="120" stroke="#e0e9dd"/><circle cx="370" cy="75" r="6" fill="#1a7d52"/><text x="370" y="50" text-anchor="middle">PKR '+f'{p["price"]:,.2f}'+'</text><text x="370" y="145" text-anchor="middle">'+E(p['date'])+' · One observation, no trend inferred</text></svg>'
 a=points[-60:];W,H=720,170 if compact else 260;L,R,T,B=70,15,20,36;lo=min(p['price']for p in a);hi=max(p['price']for p in a);span=hi-lo or max(hi*.02,1)
 coords=' '.join(f'{L+(W-L-R)*i/(len(a)-1):.1f},{H-B-(p["price"]-lo)/span*(H-T-B):.1f}'for i,p in enumerate(a));color='#18795b'if a[-1]['price']<=a[0]['price']else'#b77833'
 return f'<svg class="history-graph" viewBox="0 0 {W} {H}" role="img" aria-label="{E(label)} recorded price history"><line x1="{L}" x2="{W-R}" y1="{H-B}" y2="{H-B}" stroke="#dce7df"/><text x="8" y="28">{hi:,.2f}</text><text x="8" y="{H-B}">{lo:,.2f}</text><polyline points="{coords}" fill="none" stroke="{color}" stroke-width="3"/>'+''.join(f'<circle cx="{L+(W-L-R)*i/(len(a)-1):.1f}" cy="{H-B-(p["price"]-lo)/span*(H-T-B):.1f}" r="3" fill="{color}"><title>{E(p["date"])} · PKR {p["price"]:,.2f}</title></circle>'for i,p in enumerate(a))+f'<text x="{L}" y="{H-7}">{E(a[0]["date"])}</text><text text-anchor="end" x="{W-R}" y="{H-7}">{E(a[-1]["date"])}</text></svg>'
def comparison(peers,r):
 from products import exact_key
 priced=[x for x in peers if x['price']is not None];priced.sort(key=lambda x:(x.get('variant_key',''),x['city'],x['price']))
 out='<section class="detail-section product-comparison"><h2>Daily prices · sources & cities</h2><p class="muted">Each row keeps its exact variation, city, price basis and source date. Online offers available across Pakistan are labelled Pakistan. A daily check does not make an older quote current.</p><p id="comparison-status" class="comparison-status" aria-live="polite"></p>'
 if not priced:return out+'<p>No verified price is available for this product yet. No competing-store price is assumed.</p></section>'
 out+='<div class="source-summary"><strong id="source-count">'+str(len({store_name(x)for x in priced}))+' sources</strong><span id="city-count">'+str(len({x['city']for x in priced}))+' locations</span></div><div class="comparison-scroll"><table class="comparison-table"><thead><tr><th>Source / city</th><th>Exact variation / unit</th><th>Price · PKR</th><th>Price basis / availability</th><th>Quote date / source check</th><th>Original source</th></tr></thead><tbody>'
 for x in priced:
  out+='<tr data-quote-city="'+E(x['city'])+'" data-variant="'+E(x.get('variant_key',''))+'" data-price="'+str(x['price'])+'" data-store="'+E(store_name(x))+'"><td><b>'+E(store_name(x))+'</b><small>'+E(x['city'])+'</small></td><td>'+E(x['name'])+'<small>/ '+E(x['unit'])+'</small></td><td class="price">'+f'{x["price"]:,.2f}'+'</td><td>'+E(x['kind'])+'<small>'+E(x.get('availability','Check source'))+'</small>'+('<small>Branch / pack must be verified</small>'if x.get('comparison_eligible')is False else'')+'</td><td>'+E(x['date'])+badge(x)+'</td><td><a href="'+E(x['source'])+'" target="_blank" rel="noopener noreferrer">Visit source ↗</a></td></tr>'
 return out+'</tbody></table></div></section>'

def product_controls(r,peers):
 variants={}
 for x in peers:variants.setdefault(x.get('variant_key',x['id']),x)
 out='<div class="product-controls"><label for="product-variation">Choose variation<select id="product-variation"><option value="*">All variations — compare separately</option>'
 out+=''.join('<option value="'+E(key)+'">'+E(x.get('variant_label',x['name']))+'</option>'for key,x in sorted(variants.items(),key=lambda pair:pair[1]['name']))+'</select></label><label for="comparison-city">Compare cities<select id="comparison-city"><option value="">All cities</option>'+''.join('<option value="'+E(city)+'">'+E(city)+'</option>'for city in sorted({x['city']for x in peers}))+'</select></label></div>'
 if len(variants)>1:out+='<p class="variant-notice">Choose one variation for like-for-like prices. All-variation ranges may include different sizes, colors, storage, packs or quote bases.</p>'
 data=[{k:x.get(k)for k in ['id','name','urdu','variant_key','wholesale_quotes','trade_stage','kind','image','image_kind','image_subject','unit','date','price','city','store','source','last_checked_at','verification_state']}for x in peers]
 return out+'<script type="application/json" id="product-data">'+json.dumps(data,ensure_ascii=False).replace('<','\\u003c')+'</script>'

def more_sources(r):
 import urllib.parse
 q=urllib.parse.quote(r.get('product_name',r['name']));out='<section class="detail-section source-research"><h2>Check additional price sources</h2><p>These links search for this product at other stores. They are research links, not verified competing prices. Only successfully collected exact listings appear in the comparison table above.</p><ul>'
 sources=[('Google product search','https://www.google.com/search?q='+urllib.parse.quote(r.get('product_name',r['name'])+' price Pakistan'))]
 if r['category']in ['mobiles','electronics','machinery']:
  sources+=[('Shophive','https://www.shophive.com/catalogsearch/result/?q='+q),('Mega.pk','https://www.google.com/search?q='+urllib.parse.quote('site:mega.pk '+r.get('product_name',r['name']))),('Paklap','https://www.paklap.pk/catalogsearch/result/?q='+q)]
 if r['category']in ['grocery','produce','meat','household','health','baby','pets']:
  sources+=[('Naheed','https://www.naheed.pk/catalogsearch/result/?q='+q),('Al-Fatah','https://alfatah.pk/search?q='+q+'&type=product'),('Metro','https://www.google.com/search?q='+urllib.parse.quote('site:metro-online.pk '+r.get('product_name',r['name'])))]
 return out+''.join('<li><a href="'+E(url)+'" target="_blank" rel="noopener noreferrer">'+E(name)+' ↗</a></li>'for name,url in sources)+'</ul></section>'

def detail(r,peers,hist,rows):
 priced=[x for x in peers if x['price']is not None];vals=[x['price']for x in priced];latest=max((x['date']for x in priced),default=None)
 summary='PKR '+f'{min(vals):,.2f}'+(' – '+f'{max(vals):,.2f}'if min(vals)!=max(vals)else'')if vals else'قیمت دستیاب نہیں · Price unavailable'
 out='<main id="main" class="detail-layout"><div class="detail-head"><div><div class="eyebrow">'+E(CATS[r['category']])+' · Pakistan</div><h1>'+E(r.get('product_name',r['name']))+'</h1>'
 if r.get('urdu'):out+='<p id="product-urdu" class="original-urdu" lang="ur" dir="rtl">'+E(r['urdu'])+'</p>'
 out+='<p id="product-price" class="detail-price">'+summary+'</p><p id="product-meta">'+E(r['unit'])+(' · Latest source date '+latest if latest else' · No verified quote yet')+'</p></div><figure class="detail-photo">'+photo(r,'../')+'<figcaption>'+('Representative '+E(r.get('image_subject','item'))+' image; exact brand, model or survey grade is not confirmed.'if r.get('image_kind')=='representative'else'Item illustration; a verified photograph of this exact item is not available.'if r.get('image_kind')=='illustration'else'Source-supplied product photo')+'</figcaption></figure></div>'
 if r.get('image_kind')=='representative':out+='<p class="image-credit">Photo: '+E(r.get('image_credit'))+' · '+E(r.get('image_license'))+' · <a href="'+E(r.get('image_source'))+'" target="_blank" rel="noopener noreferrer">Image source and attribution ↗</a></p>'
 if r.get('scope'):out+='<p class="quote-scope">'+E(r['scope'])+' · '+E(r.get('condition',''))+'</p>'
 from wholesale import section
 out+=product_controls(r,peers)+comparison(peers,r)+section(r)
 out+='<section class="detail-section"><h2>Price history by date</h2><p>Each series keeps one item, location, unit and source. Dates are observations or notification dates, not invented daily prices.</p>'
 # Show representative series first, then other sources/cities as collapsible sections.
 ordered=sorted(priced,key=lambda x:(x['id']!=r['id'],x['city'],store_name(x)))
 for i,x in enumerate(ordered):
  a=hist.get(x['id'],[]);heading=store_name(x)+' · '+x['city']+' · '+x['name']
  out+='<details data-history-city="'+E(x['city'])+'" data-variant="'+E(x.get('variant_key',''))+'" class="history-series"'+(' open'if i==0 else'')+'><summary>'+E(heading)+'</summary>'+graph(a,heading)
  out+='<table class="historytable"><thead><tr><th>Date</th><th>PKR / '+E(x['unit'])+'</th></tr></thead><tbody>'+''.join('<tr><td>'+E(p['date'])+'</td><td>'+f'{p["price"]:,.2f}'+'</td></tr>'for p in reversed(a[-90:]))+'</tbody></table></details>'
 if not ordered:out+='<p>A history and graph will appear after verified dated observations become available.</p>'
 from market_features import predictor
 out+='</section>'+predictor(r,hist.get(r['id'],[]))+'<section class="detail-section"><h2>About this item</h2><p>'+E(r.get('specification')or r.get('note')or'Check the exact model, grade, size, quantity, warranty and source before buying.')+'</p>'
 if not vals:out+='<p>This catalog entry identifies a type of item, not a priced offer. An exact brand/model or grade and a current supplier quote are needed before a price can be assigned.</p>'
 if r.get('urdu'):out+='<h3>Original Urdu wording → English</h3><p lang="ur" dir="rtl" class="original-urdu">'+E(r['urdu'])+'</p><p>'+E(r['name'])+'</p>'
 if r.get('sheet'):out+='<h3>Original official notification</h3><a href="../'+E(r['sheet'])+'"><img class="detail-sheet" loading="lazy" src="../'+E(r['sheet'])+'" alt="Original official Urdu rate sheet"></a><p>The original Urdu wording is retained above; the English title describes the same grade or class. The printed notification date takes precedence.</p>'
 out+='</section>'+more_sources(r)+'<section class="detail-section"><h2>Related items</h2>'+archive([x for x in rows if x['category']==r['category']and family(x)!=family(r)][:8],'../')+'</section></main>'
 data={'@context':'https://schema.org','@type':'WebPage','name':r['name']+' prices in Pakistan','about':{'@type':'Thing','name':r['name']}}
 if latest:data['dateModified']=latest
 if r.get('source'):data['citation']=r['source']
 return out+'<script type="application/ld+json">'+json.dumps(data,ensure_ascii=False).replace('<','\\u003c')+'</script>'
