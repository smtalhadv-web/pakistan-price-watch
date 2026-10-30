import collections,html,json,re,hashlib
from model import CATS,mode
from presentation import ICONS,store_name
E=lambda x:html.escape(str(x or''),quote=True)
def family(r):
 if r.get('family'):return r['family']
 if r.get('manufacturer_model')and r['category']=='machinery':return 'makita-model|'+r['manufacturer_model'].casefold()
 name=r['name'].split(' · ')[0]if mode(r)=='listed'else r['name']
 if r['category']=='mobiles':name=re.sub(r'^xiaomi (?=redmi|poco)','',name,flags=re.I)
 return '|'.join([r['category'],re.sub(r'[^\w]+',' ',name.casefold().replace('+',' plus ')).strip(),'product'if mode(r)=='listed'else r['unit'].casefold(),mode(r),r['kind']if mode(r)!='listed'else''])
def groups_for(rows):
 groups=collections.defaultdict(list)
 for r in rows:groups[family(r)].append(r)
 return groups

def photo(r,prefix=''):
 src=r.get('image')or prefix+'assets/category-'+r['category']+'.svg'
 return '<img data-category="'+r['category']+'" src="'+E(src)+'" alt="'+E(r['name']if r.get('image')else CATS[r['category']]+' · category illustration')+'" loading="lazy" referrerpolicy="no-referrer">'
def archive(items,prefix=''):
 out='<div class="archive-grid" id="archive-grid">'
 for peers in groups_for(items).values():
  r=next((x for x in peers if x.get('image')),peers[0]);priced=[x for x in peers if x['price']is not None];vals=[x['price']for x in priced];lo=min(vals)if vals else None;hi=max(vals)if vals else None
  value=('PKR '+f'{lo:,.2f}'+(' – '+f'{hi:,.2f}'if hi!=lo else''))if vals else'قیمت دستیاب نہیں · Price unavailable'
  out+='<article class="archive-card" data-city="'+E('|'.join(sorted({x['city']for x in peers})))+'"><a class="product-title-link" href="'+prefix+'items/'+r['id']+'.html">'+photo(r,prefix)+'<h3>'+E(r['name'])+'</h3></a>'
  if r.get('urdu'):out+='<p class="original-urdu" lang="ur" dir="rtl">'+E(r['urdu'])+'</p>'
  out+='<strong class="range-price">'+value+'</strong><p>'+E(r['unit'])+' · '+('Latest source '+max(x['date']for x in priced)if priced else'Exact specification / quote needed')+'</p></article>'
 return out+'</div>'
def graph(points,label,compact=False):
 if not points:return '<div class="history-pending">No dated price observation is available yet.</div>'
 if len(points)==1:
  p=points[0];return '<svg class="history-graph" viewBox="0 0 720 170" role="img" aria-label="One recorded source price; no trend"><line x1="70" y1="120" x2="690" y2="120" stroke="#e0e9dd"/><circle cx="370" cy="75" r="6" fill="#1a7d52"/><text x="370" y="50" text-anchor="middle">PKR '+f'{p["price"]:,.2f}'+'</text><text x="370" y="145" text-anchor="middle">'+E(p['date'])+' · One observation, no trend inferred</text></svg>'
 a=points[-60:];W,H=720,170 if compact else 260;L,R,T,B=70,15,20,36;lo=min(p['price']for p in a);hi=max(p['price']for p in a);span=hi-lo or max(hi*.02,1)
 coords=' '.join(f'{L+(W-L-R)*i/(len(a)-1):.1f},{H-B-(p["price"]-lo)/span*(H-T-B):.1f}'for i,p in enumerate(a));color='#18795b'if a[-1]['price']<=a[0]['price']else'#b77833'
 return f'<svg class="history-graph" viewBox="0 0 {W} {H}" role="img" aria-label="{E(label)} recorded price history"><line x1="{L}" x2="{W-R}" y1="{H-B}" y2="{H-B}" stroke="#dce7df"/><text x="8" y="28">{hi:,.2f}</text><text x="8" y="{H-B}">{lo:,.2f}</text><polyline points="{coords}" fill="none" stroke="{color}" stroke-width="3"/>'+''.join(f'<circle cx="{L+(W-L-R)*i/(len(a)-1):.1f}" cy="{H-B-(p["price"]-lo)/span*(H-T-B):.1f}" r="3" fill="{color}"><title>{E(p["date"])} · PKR {p["price"]:,.2f}</title></circle>'for i,p in enumerate(a))+f'<text x="{L}" y="{H-7}">{E(a[0]["date"])}</text><text text-anchor="end" x="{W-R}" y="{H-7}">{E(a[-1]["date"])}</text></svg>'
def comparison(peers,r):
 priced=[x for x in peers if x['price']is not None];priced.sort(key=lambda x:x['price'])
 title='Store price comparison'if mode(r)=='listed'else'Latest published rates by city'
 out='<section class="detail-section"><h2>'+title+'</h2>'
 if not priced:return out+'<p>No verified price is available. A missing price is not zero. Browse the related products below for separately identified listings.</p></section>'
 stores=sorted({store_name(x)for x in priced});out+='<div class="source-summary"><strong>'+str(len(stores))+' verified '+('stores'if mode(r)=='listed'else'publishers')+'</strong><span>'+E(' · '.join(stores))+'</span></div>'
 out+='<p class="muted">'+('Supplier model matches can have different storage, kits, condition or warranty. Read the listed variant and dates before comparing.'if mode(r)=='listed'else'Official notifications and survey averages are separate item groups. Rates retain their actual publication dates; a new daily check does not create a new government rate.')+'</p>'
 if mode(r)=='listed'and len({store_name(x)for x in priced})<2:out+='<p>Only one store is verified for this item so far. No other-store price is assumed.</p>'
 low=min(x['price']for x in priced);high=max(x['price']for x in priced)
 out+='<div class="comparison-scroll"><table class="comparison-table"><thead><tr><th>Store / location</th><th>Listed item / variant</th><th>Price · PKR</th><th>Comparison</th><th>Source date</th><th>Original source</th></tr></thead><tbody>'
 for x in priced:
  v=x['price'];label='— Same price'if low==high else'↓ Lowest'if v==low else'↑ Highest'if v==high else'↔ Between';cls='lowest'if v==low else'highest'if v==high else'';width=max(5,v/high*100)
  out+='<tr data-quote-city="'+E(x['city'])+'"><td><b>'+E(store_name(x))+'</b><small>'+E(x['city'])+'</small></td><td>'+E(x['name'])+'<small>'+E(x.get('availability')or x['kind'])+'</small></td><td class="price '+cls+'">'+f'{v:,.2f}'+'<small>/ '+E(x['unit'])+'</small></td><td><span class="'+cls+'">'+label+'</span><div class="price-bar"><i style="width:'+f'{width:.2f}'+'%"></i></div></td><td>'+E(x['date'])+'</td><td><a href="'+E(x['source'])+'" target="_blank" rel="noopener noreferrer">Visit source ↗</a></td></tr>'
 return out+'</tbody></table></div></section>'
def detail(r,peers,hist,rows):
 priced=[x for x in peers if x['price']is not None];vals=[x['price']for x in priced];latest=max((x['date']for x in priced),default=None)
 summary='PKR '+f'{min(vals):,.2f}'+(' – '+f'{max(vals):,.2f}'if min(vals)!=max(vals)else'')if vals else'قیمت دستیاب نہیں · Price unavailable'
 out='<main id="main" class="detail-layout"><div class="detail-head"><div><div class="eyebrow">'+E(CATS[r['category']])+' · Pakistan</div><h1>'+E(r['name'])+'</h1>'
 if r.get('urdu'):out+='<p class="original-urdu" lang="ur" dir="rtl">'+E(r['urdu'])+'</p>'
 out+='<p class="detail-price">'+summary+'</p><p>'+E(r['unit'])+(' · Latest source date '+latest if latest else' · No verified quote yet')+'</p></div><figure class="detail-photo">'+photo(r,'../')+'<figcaption>'+('Source-supplied product photo'if r.get('image')else'Category illustration; no verified photograph of this exact item is available.')+'</figcaption></figure></div>'
 out+=comparison(peers,r)
 out+='<section class="detail-section"><h2>Price history by date</h2><p>Each series keeps one item, location, unit and source. Dates are observations or notification dates, not invented daily prices.</p>'
 # Show representative series first, then other sources/cities as collapsible sections.
 ordered=sorted(priced,key=lambda x:(x['id']!=r['id'],x['city'],store_name(x)))
 for i,x in enumerate(ordered):
  a=hist.get(x['id'],[]);heading=store_name(x)+' · '+x['city']+' · '+x['name']
  out+='<details class="history-series"'+(' open'if i==0 else'')+'><summary>'+E(heading)+'</summary>'+graph(a,heading)
  out+='<table class="historytable"><thead><tr><th>Date</th><th>PKR / '+E(x['unit'])+'</th></tr></thead><tbody>'+''.join('<tr><td>'+E(p['date'])+'</td><td>'+f'{p["price"]:,.2f}'+'</td></tr>'for p in reversed(a[-90:]))+'</tbody></table></details>'
 if not ordered:out+='<p>A history and graph will appear after verified dated observations become available.</p>'
 out+='</section><section class="detail-section"><h2>About this item</h2><p>'+E(r.get('specification')or r.get('note')or'Check the exact model, grade, size, quantity, warranty and source before buying.')+'</p>'
 if not vals:out+='<p>This catalog entry identifies a type of item, not a priced offer. An exact brand/model or grade and a current supplier quote are needed before a price can be assigned.</p>'
 if r.get('urdu'):out+='<h3>Original Urdu wording → English</h3><p lang="ur" dir="rtl" class="original-urdu">'+E(r['urdu'])+'</p><p>'+E(r['name'])+'</p>'
 if r.get('sheet'):out+='<h3>Original official notification</h3><a href="../'+E(r['sheet'])+'"><img class="detail-sheet" loading="lazy" src="../'+E(r['sheet'])+'" alt="Original official Urdu rate sheet"></a><p>The original Urdu wording is retained above; the English title describes the same grade or class. The printed notification date takes precedence.</p>'
 out+='</section><section class="detail-section"><h2>Related items</h2>'+archive([x for x in rows if x['category']==r['category']and family(x)!=family(r)][:8],'../')+'</section></main>'
 data={'@context':'https://schema.org','@type':'WebPage','name':r['name']+' prices in Pakistan','about':{'@type':'Thing','name':r['name']}}
 if latest:data['dateModified']=latest
 if r.get('source'):data['citation']=r['source']
 return out+'<script type="application/ld+json">'+json.dumps(data,ensure_ascii=False).replace('<','\\u003c')+'</script>'
