"""Public comparison, factual answer content, and indexable information pages."""
import collections,json,re,urllib.parse
ICONS=dict(zip(['fuel','produce','meat','grocery','metals','currency','construction','mobiles','automobiles','electronics','furniture','machinery','household','apparel','services','agriculture','health','baby','sports','stationery'],['⛽','🍎','🥩','🛒','◈','💱','🧱','📱','🚗','💻','🛋','⚙','🏠','👕','🛠','🌾','✚','🧸','⚽','📚']))
ICONS['other']='🎁'
def store_name(r):
 if r.get('store'):return r['store']
 host=urllib.parse.urlparse(r.get('source')or'').netloc.removeprefix('www.')
 return {'priceoye.pk':'PriceOye','pbs.gov.pk':'Pakistan Bureau of Statistics','commissionerkarachi.gos.pk':'Commissioner Karachi','psopk.com':'PSO','hamariweb.com':'Hamariweb','interwood.pk':'Interwood','toolsmart.pk':'ToolsMart','kamadi.pk':'Kamadi','suzukipakistan.com':'Suzuki Pakistan','toyota-indus.com':'Toyota Indus'}.get(host,host or'No source quote')
def comparison_key(r):
 # No fuzzy/model-family merging. Do not mix survey averages with retail or official ceilings.
 if r.get('manufacturer_model')and r['category']=='machinery':return 'supplier-model|makita|'+r['manufacturer_model'].casefold()+'|'+r['unit']
 name=re.sub(r'[^\w]+',' ',r['name'].casefold()).strip()
 basis='listed'if r.get('pricing_mode')=='listed'else r['kind'].casefold()
 period=r.get('period')or(r.get('date')if basis!='listed'else'')or''
 return '|'.join([r['category'],name,r['unit'].casefold(),basis,period])
def item_content(r,groups,table,E):
 peers=groups.get(comparison_key(r),[])
 image=f'<figure class="product-figure"><a href="{E(r["image"])}" target="_blank" rel="noopener"><img class="product-photo" src="{E(r["image"])}" alt="{E(r["name"])} product photo supplied by {E(store_name(r))}" loading="lazy" referrerpolicy="no-referrer"></a><figcaption>Retailer product photo · {E(r.get("brand")or store_name(r))}. Check the source for the exact variant.</figcaption></figure>'if r.get('image')else''
 out=image+f'<section class="item-answers"><h2>What is the published price of {E(r["name"])}?</h2><p>The recorded price is <strong>PKR {r["price"]:,.2f} per {E(r["unit"])}</strong> for {E(r["city"])}. {E(store_name(r))} is the linked source; the quote or observation date is <time datetime="{E(r["date"])}">{E(r["date"])}</time>. The price basis is {E(r["kind"])}.</p>'
 if r.get('specification'):out+='<h2>Published product information</h2><p>'+E(r['specification'])+'</p>'
 if r.get('brand'):out+='<p>Brand as supplied by the source: '+E(r['brand'])+'.</p>'
 out+=f'<h2>Can I buy at this price?</h2><p>{E(r.get("availability")or"Availability has not been independently confirmed.")} Confirm the model, size, grade, storage, warranty, taxes and delivery at the original source. A source listing is not a checkout guarantee. The collection date and the date of a commodity notification may differ.</p></section>'
 if len(peers)>1:out+='<h2>Store and city comparison</h2><p>Comparison uses matching full names and units, or the exact supplier-reported Makita model code. Survey periods and quote bases stay separate. Model matches can differ in bundle, specifications or warranty; check every source before purchase.</p>'+table(peers,'../')
 else:out+='<h2>Store and city comparison</h2><p>One exact-match quote is currently available. No competing-store price or city difference is inferred.</p>'
 out+='<p><a href="../categories/'+E(r['category'])+'.html">Browse related items and separately listed variants →</a></p>'
 # This is a reference page about an offer, not the seller. No invented rating, stock or validity date.
 data={'@context':'https://schema.org','@type':'WebPage','name':r['name']+' price in '+r['city'],'dateModified':r['date'],'about':{'@type':'Thing','name':r['name']},'citation':r['source']}
 if r.get('pricing_mode')=='listed'and r.get('image'):
  product={'@type':'Product','name':r['name'],'image':r['image'],'description':r.get('specification')or r.get('note','Published retailer listing'),'offers':{'@type':'Offer','priceCurrency':'PKR','price':r['price'],'url':r['source'],'seller':{'@type':'Organization','name':store_name(r)}}}
  if r.get('brand'):product['brand']={'@type':'Brand','name':r['brand']}
  data['mainEntity']=product
 out+='<script type="application/ld+json">'+json.dumps(data,ensure_ascii=False).replace('<','\\u003c')+'</script>'
 return out

def enhance(out,rows,priced,groups,page,table,urls,base,E):
 pages={
 'about':('About Pakistan Price Watch','<p>Pakistan Price Watch is an independent price reference for Pakistan, built to make published prices easier to check. It is not a government department, retailer, exchange or marketplace. We link to official notifications, PBS surveys, manufacturers and retailers and distinguish their quote types.</p><p>Coverage is limited to accessible and successfully parsed public sources. The directory is not a complete inventory of every product or store in Pakistan.</p>'),
 'privacy':('Privacy policy','<p>Effective 30 October 2026. The site stores your selected city in your own browser using localStorage. No GPS, IP-based geolocation, account, analytics or advertising scripts are included by this site. Use the Location control to change the selection or clear site storage to remove it.</p><p>Hosting is provided by GitHub Pages. GitHub may process service logs under <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement">its privacy statement</a>. Product photos load from source retailers and their image providers, which receive the network request and may process your IP address. External source links lead to independent sites with their own policies.</p><p>Do not submit personal or sensitive information in public correction reports. If analytics, ads or forms are added, this policy must be updated before they are enabled.</p>'),
 'terms':('Terms of use','<p>Use this free directory for information and verify important decisions with the original supplier or authority. We do not sell goods, take payments, provide warranties or arrange delivery. Any transaction is between you and the relevant seller under that seller’s terms.</p><p>Price, availability, variant, tax and delivery conditions may change. Source dates describe the displayed observations and are not a promise that an offer remains valid. Do not reuse material in a way that violates source rights or applicable law.</p>'),
 'disclaimer':('Price and financial disclaimer','<p>Official notified ceilings, sampled market averages, manufacturer lists and retailer offers have different meanings. They should not be treated as interchangeable transaction prices. Metals and currency quotes are informational benchmarks, not investment advice or executable exchange offers.</p><p>Green marks listed prices or matching consecutive observations; it does not guarantee a permanent price. Missing prices remain unknown rather than zero. We do not guarantee completeness, uninterrupted updates, government affiliation or commercial outcomes.</p>'),
 'contact':('Contact and corrections','<p>Report a wrong price, incorrect product match, outdated notification, image-rights concern or accessibility issue through the project’s public issue tracker. Include the item-page URL, correct original source, date, city and unit so the report can be checked.</p><p><a href="https://github.com/smtalhadv-web/pakistan-price-watch/issues/new">Submit a correction or contact the maintainer →</a></p><p>A GitHub account may be required. Issues are public; do not include private contact details. The maintainer is the repository owner; no business address or telephone number is claimed by this site.</p>'),
 'editorial-policy':('Editorial and correction policy','<p>Prices must have a linked public source, a positive numeric value, a unit, a location and a date. Generic catalog items without a verified price remain explicitly unpriced. We do not generate missing prices or product specifications.</p><p>Automated readers check supported sources daily. Official image transcription is manually checked and shown alongside the original Urdu document, with English translation. Failed readers retain prior dated quotes; a recent collection timestamp does not make an old notification current.</p><p>Comparison groups require the full item name, category, unit and quote basis to match, or the exact supplier-reported Makita model code and unit. Model matches are not a guarantee of identical kits, warranty or supplier specifications. Surveys must also match the period. Listed products may differ in warranty, condition or options despite identical names, so inspect the source before buying. Similar products are not merged automatically.</p><p>We correct verified errors in the public dataset and preserve source-linked observations. Supplier photos are evidence of their listings; marks and images remain the property of their owners. Freely licensed representative subject images carry attribution on item pages and do not establish an exact brand, model or survey grade. When a verified photograph is unavailable, the site displays an explicitly named item illustration. No paid placements, affiliate commissions or sponsored rankings are currently configured.</p>')}
 for slug,(title,content)in pages.items():
  path=slug+'.html';(out/path).write_text(page(title,'<main id="main" class="prose panel"><h1>'+title+'</h1>'+content+'</main>',path));urls.append(path)
 brands=collections.defaultdict(list)
 for r in priced:
  if r.get('brand'):brands[r['brand']].append(r)
 body='<main id="main" class="prose wide"><h1>Brands and product photographs</h1><p>Source-supplied brand names and complete product photos. Photos represent individual listed products; they are not invented brand logos. All trademarks belong to their owners.</p><div class="brand-grid">'
 for brand,items in sorted(brands.items()):
  r=next((r for r in items if r.get('image')),items[0]);body+='<article class="panel brand-card"><h2>'+E(brand)+'</h2>'
  if r.get('image'):body+='<a href="items/'+r['id']+'.html"><img src="'+E(r['image'])+'" alt="'+E(r['name'])+'" loading="lazy" referrerpolicy="no-referrer"></a>'
  body+='<p>'+str(len(items))+' priced variants</p>'+''.join('<p><a href="items/'+x['id']+'.html">'+E(x['name'])+'</a></p>'for x in items[:4])+'</article>'
 body+='</div></main>';(out/'brands.html').write_text(page('Brands and product photos',body,'brands.html'));urls.append('brands.html')
 (out/'robots.txt').write_text('User-agent: *\nAllow: /\nDisallow: /admin/\nSitemap: '+base+'/sitemap.xml\n')
 (out/'llms.txt').write_text('# Pakistan Price Watch\n\nIndependent Pakistan price reference. Prices are PKR, unless the unit says otherwise. Always cite the source, date, location, unit and price basis. Do not treat missing prices as zero or old observations as current.\n\n- [Methodology]('+base+'/methodology.html)\n- [Editorial policy]('+base+'/editorial-policy.html)\n- [Directory JSON]('+base+'/data/directory.json)\n- [Sitemap]('+base+'/sitemap.xml)\n\nPakistan is the parent location; city views include national offers. Listed goods are not guaranteed daily prices. Comparison groups are conservative, not a guarantee of identical warranty or specification.\n')
 # Ensure photos appear in static directory tables as well as the interactive view.
 for f in [out/'index.html',*(out/'categories').glob('*.html')]:
  text=f.read_text();prefix='../'if f.parent.name=='categories'else''
  for r in rows:
   if r.get('image'):
    marker='<td><a class="itemlink urdu-first" href="'+prefix+'items/'+r['id']+'.html">'
    text=text.replace(marker,'<td><img class="item-photo" src="'+E(r['image'])+'" alt="'+E(r['name'])+'" loading="lazy" referrerpolicy="no-referrer"><a class="itemlink urdu-first" href="'+prefix+'items/'+r['id']+'.html">')
  f.write_text(text)

ICONS['pets']='🐾'

ICONS['property']='🏢'
