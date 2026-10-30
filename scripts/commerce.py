"""Public retailer catalog discovery; source failures retain last dated observations."""
import concurrent.futures,datetime,hashlib,json,re,urllib.request,urllib.parse
from bs4 import BeautifulSoup
from collect import ROOT
TODAY=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5))).date().isoformat()
def key(s):return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
def fetch(url):
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'PakistanPriceWatch/1.1 (public source-linked price comparison)'})
  with urllib.request.urlopen(req,timeout=25)as r:return url,r.read(8000000).decode('utf-8')
 except Exception as e:return url,None

def run():
 rows={r['id']:r for r in json.loads((ROOT/'data/prices.json').read_text())};hist=json.loads((ROOT/'data/history.json').read_text());logs=[];seen=set();metadata={}
 def add(name,price,url,store,image=None,brand=None,category='electronics',availability='Check store',description='',unit='device; verify variant'):
  if not isinstance(price,(int,float))or not 0<price<1e10:return
  # Keep existing source IDs and histories where already known.
  old=next((r for r in rows.values()if r['source']==url),None)
  id=old['id']if old else'offer-'+hashlib.sha256(url.encode()).hexdigest()[:18]
  r=dict(id=id,name=name,price=price,source=url,store=store,category=category,city='Pakistan',country='Pakistan',date=TODAY,unit=unit,kind='Retailer listing · observed',pricing_mode='listed',availability=availability,note='Advertised listing, observed on the date shown. Confirm exact variant, warranty, taxes, delivery and stock at the retailer.')
  if old:r={**old,**r}
  if image and image.startswith('https://'):r['image']=image
  if brand:r['brand']=brand
  if description:r['specification']=description[:1600]
  rows[id]=r;seen.add(id)
  a={p['date']:p for p in hist.get(id,[])};a[TODAY]={'date':TODAY,'price':price,'source':url};hist[id]=sorted(a.values(),key=lambda x:x['date'])[-400:]
 def parse(url,text):
  if text is None:logs.append({'url':url,'status':'fetch failed; previous quote retained'});return
  before=len(seen);s=BeautifulSoup(text,'html.parser')
  if 'products.json'in url:
   try:products=json.loads(text).get('products',[])
   except ValueError:products=[]
   for p in products:
    for v in p.get('variants',[]):
     name=p['title']+(' · '+v['title']if v.get('title')and v['title']!='Default Title'else'')
     image=v.get('featured_image')or next(iter(p.get('images',[])),{})
     cat='mobiles'if re.search(r'\b(redmi note|poco [fmcx]\d|xiaomi \d|redmi \d)',name,re.I)and not re.search(r'case|cover|protector|cable',name,re.I)else'electronics'
     add(name,float(v.get('price')or 0),'https://mistore.pk/products/'+p['handle']+'?variant='+str(v['id']),'MiStore',image.get('src'),p.get('vendor'),cat,'In stock'if v.get('available')else'Out of stock',BeautifulSoup(p.get('body_html',''),'html.parser').get_text(' ',strip=True),unit='item; exact listed variant')
  elif 'priceoye.pk'in url:
   for b in s.select('.productBox'):
    a=b.select_one('a[href]');n=b.select_one('.p-title');v=b.select_one('.price-box');im=b.select_one('img.product-thumbnail')
    if not(a and n and v):continue
    u=a['href'];m=re.search(r'(?:Rs\s*)?([\d,]+)',v.get_text(' ',strip=True))
    if not u.startswith('https://priceoye.pk/')or not m:continue
    image=im.get('src')if im else None
    if im and im.get('srcset'):image=im['srcset'].split(',')[-1].strip().split()[0]
    add(n.get_text(' ',strip=True),float(m[1].replace(',','')),u,'PriceOye',image,category='mobiles'if'/mobiles/'in u else'electronics')
  elif 'galaxy.pk'in url:
   for b in s.select('.product-card-2'):
    n=b.select_one('.product-title');v=b.select_one('.product-price');im=b.select_one('img');d=b.select_one('.description-wrapper')
    if not(n and v):continue
    m=re.search(r'Rs\.?\s*([\d,]+)',v.get_text(' ',strip=True))
    if not m:continue
    add(n.get_text(' ',strip=True),float(m[1].replace(',','')),urllib.parse.urljoin(url,n['href']),'Galaxy',im.get('src')if im else None,description=d.get_text(' ',strip=True)if d else'')
  elif 'zahcomputers.pk'in url:
   for b in s.select('article[data-product-id]'):
    a=b.select_one('a[href^="/product/"]');im=b.select_one('img');v=b.select_one('button[data-price]');brand=b.select_one('[class*="__brand"]')
    if not(a and v):continue
    add(v.get('data-name')or a.get('aria-label',''),float(v['data-price']),urllib.parse.urljoin(url,a['href']),'ZAH Computers',urllib.parse.urljoin(url,im['src'])if im else None,brand.get_text(' ',strip=True)if brand else None,availability='Check store')
  logs.append({'url':url,'status':'parsed','observed_offers':len(seen)-before})
 # Discover public categories; limits prevent an accidental unbounded crawl.
 urls=['https://www.zahcomputers.pk/shop/','https://www.galaxy.pk/laptops']
 for brand in ['samsung','xiaomi','vivo','oppo','realme','infinix','tecno','apple']:
  urls.extend('https://priceoye.pk/mobiles/'+brand+'?page='+str(p)for p in range(1,5))
 urls+=['https://priceoye.pk/'+c+'?page='+str(p)for c in ['laptops','smart-watches','wireless-earbuds','tablets','power-banks','trimmers-shavers','speakers']for p in range(1,4)]
 urls+=['https://mistore.pk/products.json?limit=250&page='+str(p)for p in range(1,7)]
 with concurrent.futures.ThreadPoolExecutor(max_workers=5)as ex:
  for url,text in ex.map(fetch,urls):
   parse(url,text)
   if url.endswith('/shop/')and text:
    soup=BeautifulSoup(text,'html.parser');metadata['zah_categories']=sorted({urllib.parse.urljoin(url,a['href'])for a in soup.select('a[href^="/category/"]')})[:40]
 extra=metadata.get('zah_categories',[])
 extra+=['https://www.galaxy.pk/'+c for c in ['desktops','monitors','processors','motherboards','graphic-cards','memory','solid-state-drive','printers']]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4)as ex:
  for u,t in ex.map(fetch,extra):parse(u,t)
 # Attach images/brand metadata from already fetched furniture/tools feeds without refreshing their dates.
 for fn in ['interwood-products','makita-products','kamadi-products']:
  try:ps=json.loads((ROOT/'raw'/f'{fn}.html').read_text())['products']
  except (FileNotFoundError,ValueError,KeyError):continue
  for p in ps:
   for v in p.get('variants',[]):
    for r in rows.values():
     if r['id'].endswith('-'+str(v['id']))and r['id'].startswith('shop-'):
      im=v.get('featured_image')or next(iter(p.get('images',[])),{});r['image']=im.get('src');r['brand']=p.get('vendor');r['store']=urllib.parse.urlparse(r['source']).netloc
      if fn=='makita-products':r['manufacturer_model']=v.get('sku')
      elif fn=='kamadi-products'and' | 'in p['title']:r['manufacturer_model']=p['title'].split(' | ')[0]
 from taxonomy import normalize
 normalize(list(rows.values()))
 (ROOT/'data/prices.json').write_text(json.dumps(list(rows.values()),ensure_ascii=False,separators=(',',':'))+'\n')
 (ROOT/'data/history.json').write_text(json.dumps(hist,ensure_ascii=False,separators=(',',':'))+'\n')
 (ROOT/'data/commerce-report.json').write_text(json.dumps({'checked_at':TODAY,'observed_offers':len(seen),'sources':logs},indent=2))
 print(json.dumps({'total':len(rows),'observed':len(seen),'fetched':len(logs),'failed':sum('failed'in x['status']for x in logs)}))
if __name__=='__main__':run()
