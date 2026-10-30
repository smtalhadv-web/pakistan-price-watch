"""Bounded public catalog readers. No login/captcha bypass, seller identity, or guessed prices."""
import json,re,hashlib,datetime,urllib.request,urllib.parse,concurrent.futures
from bs4 import BeautifulSoup
from collect import ROOT
NOW=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5)));TODAY=NOW.date().isoformat()
SOURCES={
 'Chase Value':('https://chasevalue.pk/','Public catalog; Chase Value is separate from Chase Up.'),
 'Chase Up':('https://chaseupgrocery.com/','Store/location selection needs verification.'),
 'Naheed':('https://www.naheed.pk/','Public product cards; fresh delivery area must be checked.'),
 'Metro':('https://metro-online.pk/','Public default page; branch/location is not selected.'),
 'Paklap':('https://www.paklap.pk/','Public laptop listings; variant, condition and warranty retained.'),
 'Daraz':('https://www.daraz.pk/','No validated product price cards parsed; authorized catalog API is available.'),
 'Foodpanda / Kifayah':('https://www.foodpanda.pk/shop/a036/kifayah-supermarket-pechs','Public Kifayah PECHS, Karachi product cards; delivery area and checkout availability need confirmation.'),
 'Imtiaz':('https://shop.imtiaz.com.pk/','City and area selection required; no default national price assumed.'),
 'Krave Mart':('https://kravemart.com/','Delivery area/app catalog required; no price feed connected.'),
 'PriceOye':('https://priceoye.pk/','Existing daily public catalog reader.'),
 'OLX':('https://www.olx.com.pk/','Public classified asking prices; condition and seller claims are unverified.'),
 'Facebook Marketplace':('https://www.facebook.com/marketplace/','Not connected; no logged-in or private listings collected.'),
 'Google Ads':('https://adstransparency.google.com/?region=PK','Research link only. An advertised amount is not a verified checkout price.'),
 'Meta Ads':('https://www.facebook.com/ads/library/','Research link only. No verified Pakistan commercial-ad price feed connected.'),
 'Wholesale markets / AMIS':('https://amis.pk/','Current public request failed; no wholesale figure invented.'),
 'News references':('https://www.dawn.com/business','Context only; no news headline converted to a current product price.'),
 'PSX':('https://dps.psx.com.pk/','External official hub only. Redistribution of price feeds requires a PSX license.')}
def number(text):
 s=str(text).replace(',','');m=re.search(r'\d+(?:\.\d+)?',s)
 if not m:return None
 n=float(m[0]);return n*(1e7 if re.search(r'crore',s,re.I)else 1e5 if re.search(r'lac|lakh',s,re.I)else 1e6 if re.search(r'million|\d\s*m\b',s,re.I)else 1e3 if re.search(r'thousand|\d\s*k\b',s,re.I)else 1)
def sanitize(text):
 text=re.sub(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}','[contact removed]',str(text));return re.sub(r'(?<!\d)(?:\+?92|0)3\d{9}(?!\d)','[contact removed]',text).strip()[:550]
def category(name,hint=''):
 n=(name+' '+hint).lower()
 rules=[('household',r'\b(?:laundry|detergent|insecticide|bedsheet|bed sheet|curtain|crockery|towel|kitchen|kettle|fryer|cooker|cookware|casserole|dinner set|mug|vacuum|refrigerator|freezer|washing machine)\b'),('furniture',r'\b(?:sofa|couch|chair|wardrobe|cabinet|dining table|gaming desk|bedframe)\b'),('electronics',r'\b(?:laptop|notebook|macbook|desktop|inbook|ideapad|thinkpad|headphone|powerbank|charger|monitor|ssd|router|usb|television)\b'),('baby',r'\b(?:diaper|diapers|nappy|baby wipes|feeding bottle)\b'),('health',r'\b(?:perfume|shampoo|conditioner|moistur|cream|cosmetic|lipstick|lotion|sunscreen|face wash|serum|soap|body wash|toothpaste|toothbrush|health|beauty)\b'),('apparel',r'\b(?:socks|underwear|legging|pajama|jeans|pants|scarf|hijab|abaya|belt|wallet|handbag|kurti|kurta|unstitched|fabric|shirt|trouser|tshirt|t-shirt|sandal|shoe|dupatta|chappal|stitched|suit|dress|women|mens|womens|garment)\b'),('meat',r'\b(?:meat|poultry|beef|mutton|chicken|seafood)\b'),('produce',r'\b(?:fresh products|vegetables|fresh fruit)\b'),('grocery',r'\b(?:oil|rice|flour|salt|sugar|food|grocery|groceries|pulses|lentil|daal|tea|coffee|milk|ghee|spice|chocolate|biscuit|snack|butter|cheese)\b')]
 for c,p in rules:
  if re.search(p,n):return c
 return'other'
def package(name,cat):
 m=re.search(r'\b(\d+(?:\.\d+)?)\s*(kg|gm|g|ml|litres?|liters?|ltr|l|pcs)\b',name,re.I)
 return(m[0],True)if m else('device; verify exact variant',True)if cat in ['electronics','mobiles']else('item; verify pack or variant',False)
def fetch(pair):
 store,url=pair
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'PakistanPriceWatch/1.3 (source-linked public catalog reference)'})
  with urllib.request.urlopen(req,timeout=25)as q:body=q.read(9000000).decode('utf-8')
  return store,url,body,None
 except Exception as e:return store,url,None,str(e)
def objects(value):
 if isinstance(value,dict):
  yield value
  for v in value.values():yield from objects(v)
 elif isinstance(value,list):
  for v in value:yield from objects(v)
def parse(store,url,text):
 offers=[];soup=BeautifulSoup(text,'html.parser')
 def add(name,value,source,image=None,hint='',variant='',city='Pakistan',asking=False,scope='listed online; verify delivery',eligible=None):
  price=number(value)
  if not price or not 0<price<1e10 or not source.startswith('https://'):return
  name=sanitize(name)
  if not name:return
  cat='mobiles'if asking and re.search(r'iphone|phone|samsung|redmi',name,re.I)else category(name,hint);unit,known=package(name,cat)
  if asking:unit='individual listing; verify condition'
  identity=store+'|'+source+'|'+str(variant);id='partner-'+hashlib.sha256(identity.encode()).hexdigest()[:20]
  r=dict(id=id,name=name,category=cat,price=price,unit=unit,date=TODAY,observed_on=TODAY,source=source,store=store,city=city,country='Pakistan',pricing_mode='asking'if asking else'listed',kind='Classified asking price · observed'if asking else'Retailer listing · observed',condition=('Seller states new'if re.search(r'\bnew\b',name,re.I)else'Seller states used'if re.search(r'\bused\b',name,re.I)else'Condition not verified')if asking else'Check source',scope=scope,comparison_eligible=False if asking else known if eligible is None else eligible,availability='Check original listing',note='Date is the observation date, not the publication date. '+scope+'. '+('Seller asking price, not a completed-sale value. PTA/JV, battery, storage and condition claims are unverified. No seller identity/contact details are collected.'if asking else'Confirm exact pack, stock, warranty, delivery, taxes and applicable branch before buying.'))
  if image and image.startswith('https://'):r['image']=image;r['image_kind']='listing'
  offers.append(r)
 if store=='Chase Value':
  q=json.loads(text)
  for p in q.get('products',[]):
   for v in p.get('variants',[]):
    name=p['title']+(' · '+v['title']if v.get('title')and v['title']!='Default Title'else'');im=v.get('featured_image')or next(iter(p.get('images',[])),{});source='https://chasevalue.pk/products/'+p['handle']+'?variant='+str(v['id'])
    before=len(offers);add(name,v.get('price'),source,im.get('src'),p.get('product_type',''),v['id'])
    if len(offers)>before:offers[-1]['brand']=p.get('vendor','')
 elif store in ['Naheed','Paklap']:
  for card in soup.select('.product-item-info'):
   a=card.select_one('a.product-item-link')or card.select_one('a.product-item-photo');im=card.select_one('img.product-image-photo');p=card.select_one('[data-price-type="finalPrice"][data-price-amount]')or card.select_one('[data-price-amount]');n=card.select_one('.product-item-link')
   if not(a and p):continue
   name=n.get_text(' ',strip=True)if n else im.get('alt','')if im else''
   hint='laptop'if store=='Paklap'else'vegetables'if'/vegetables'in url else'groceries'
   add(name,p['data-price-amount'],a['href'],im.get('src')if im else None,hint,scope='Online listing; fresh-item delivery coverage and checkout location need confirmation')
 elif store=='Metro':
  seen=set()
  for sc in soup.select('script'):
   t=sc.get_text();prefix='self.__next_f.push('
   if not t.startswith(prefix):continue
   try:p=json.loads(t[len(prefix):].strip().rstrip(';)'));data=json.loads(p[1])if isinstance(p[1],str)and p[1].startswith('{')else None
   except (ValueError,IndexError,TypeError):continue
   for p in objects(data):
    if not(p.get('name')and p.get('price')and p.get('imageURL')and p.get('storeVariantId')):continue
    if p['storeVariantId']in seen:continue
    seen.add(p['storeVariantId']);add(p['name'],p['price'],url,p['imageURL'],p.get('productCategoryName',''),p['storeVariantId'],scope='Public default-page offer; branch, delivery area and exact pack are unconfirmed. Not a national commodity rate',eligible=False)
 elif store=='Foodpanda / Kifayah':
  schema=soup.select_one('script[data-testid="groceries-vendor-schema"]')
  if not schema:return offers
  vendor=json.loads(schema.get_text())
  if vendor.get('address',{}).get('addressLocality')!='Karachi'or'kifayah'not in vendor.get('name','').lower():return offers
  for card in soup.select('.groceries-product-card[data-id]'):
   n=card.select_one('[data-testid="groceries-product-card-name"]');p=card.select_one('[data-testid="groceries-product-card-price"]');im=card.select_one('img')
   if not(n and p):continue
   add(n.get_text(' ',strip=True),p.get_text(' ',strip=True),url,im.get('src')if im else None,'groceries',card['data-id'],city='Karachi',scope='Kifayah Supermarket PECHS, Karachi only. Delivery area, fees, pack and checkout availability require confirmation')
 elif store=='OLX':
  for card in soup.select('li[aria-label="Listing"]'):
   a=card.select_one('a[href*="/item/"]');n=card.select_one('[aria-label="Title"]');p=card.select_one('[aria-label="Price"]');im=card.select_one('img');loc=card.select_one('[aria-label="Location"]')
   if not(a and n and p):continue
   city=loc.get_text(' ',strip=True).rstrip('• ').split(',')[-1].strip()if loc else'Location unconfirmed'
   # City only; no neighbourhood, precise address, seller name, phone or account ID.
   if len(city)>45:city='Location unconfirmed'
   add(n.get_text(' ',strip=True),p.get_text(' ',strip=True),urllib.parse.urljoin(url,a['href']),im.get('src')if im else None,'laptop'if'q-laptop'in url else'sofa'if'q-sofa'in url else'phone',city=city,asking=True,scope='Public classified snapshot; individual availability and condition are unverified')
 return offers

def run():
 path=ROOT/'data/partner-prices.json';rows={r['id']:r for r in json.loads(path.read_text())}if path.exists()else{};hist=json.loads((ROOT/'data/partner-history.json').read_text())if(ROOT/'data/partner-history.json').exists()else{};logs=[]
 urls=[('Chase Value','https://chasevalue.pk/products.json?limit=100&page='+str(p))for p in range(1,3)]+[('Naheed','https://www.naheed.pk/groceries-pets'),('Naheed','https://www.naheed.pk/groceries-pets/fresh-products/vegetables'),('Naheed','https://www.naheed.pk/groceries-pets/dairy/milk-dairy-drinks'),('Naheed','https://www.naheed.pk/groceries-pets/baking-cooking/rice'),('Naheed','https://www.naheed.pk/groceries-pets/baking-cooking/flours-meals'),('Paklap','https://www.paklap.pk/laptops-prices.html'),('Paklap','https://www.paklap.pk/daily-deals.html'),('Metro','https://metro-online.pk/'),('Foodpanda / Kifayah','https://www.foodpanda.pk/shop/a036/kifayah-supermarket-pechs'),('OLX','https://www.olx.com.pk/items/q-iphone-15'),('OLX','https://www.olx.com.pk/items/q-laptop'),('OLX','https://www.olx.com.pk/items/q-sofa')]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4)as ex:
  for store,url,text,error in ex.map(fetch,urls):
   if error:logs.append(dict(store=store,url=url,status='fetch failed; dated offers retained',error=error));continue
   try:offers=parse(store,url,text)
   except Exception as e:logs.append(dict(store=store,url=url,status='parse failed; dated offers retained',error=str(e)));continue
   for r in offers:
    rows[r['id']]=r;a={p['date']:p for p in hist.get(r['id'],[])};a[TODAY]={'date':TODAY,'price':r['price'],'source':r['source']};hist[r['id']]=sorted(a.values(),key=lambda p:p['date'])[-400:]
   logs.append(dict(store=store,url=url,status='parsed'if offers else'no verified quotes',offers=len(offers)))
 from taxonomy import normalize
 normalize(list(rows.values()));path.write_text(json.dumps(list(rows.values()),ensure_ascii=False,separators=(',',':'))+'\n');(ROOT/'data/partner-history.json').write_text(json.dumps(hist,ensure_ascii=False,separators=(',',':'))+'\n');(ROOT/'data/partner-source-report.json').write_text(json.dumps(dict(checked_at=NOW.isoformat(),quotes=len(rows),checks=logs),indent=2)+'\n');print(json.dumps(dict(quotes=len(rows),checks=logs)))
if __name__=='__main__':run()
