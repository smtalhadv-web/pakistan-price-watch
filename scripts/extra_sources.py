"""Additional public price readers; retain dated quotes when a reader fails."""
import concurrent.futures,datetime,hashlib,json,pathlib,re,urllib.parse,urllib.request
from bs4 import BeautifulSoup
from partner_sources import parse as partner_parse,category,package
from taxonomy import normalize
ROOT=pathlib.Path(__file__).resolve().parents[1]
URLS=[('Al-Fatah','https://alfatah.pk/products.json?limit=100'),('Shophive','https://www.shophive.com/mobile-phones'),('Mega.pk','https://www.mega.pk/mobiles/')]
def parse(store,url,raw,today):
 rows=[]
 def add(name,price,source,image,cat,variant='',spec='',unit_override=None):
  try:price=float(str(price).replace(',',''))
  except (TypeError,ValueError):return
  if not 0<price<1e10 or not source.startswith('https://'):return
  id='extra-'+hashlib.sha256((store+'|'+source+'|'+str(variant)).encode()).hexdigest()[:20];unit,known=package(name,cat)
  if unit_override:unit,known=unit_override
  rows.append(dict(id=id,name=name.strip(),price=price,category=cat,source=source,store=store,city='Pakistan',country='Pakistan',date=today,observed_on=today,last_checked_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),unit=unit,kind='Retailer listing · observed',pricing_mode='listed',comparison_eligible=known,scope='Public online listing; confirm delivery area, exact variant, warranty, tax and stock',availability='Check original listing',specification=spec[:1200],image=image or'',image_kind='listing'))
 if store=='Al-Fatah':
  for p in json.loads(raw).get('products',[]):
   for v in p.get('variants',[]):
    name=p['title']+(' · '+v['title']if v.get('title')not in [None,'Default Title']else'');image=v.get('featured_image')or next(iter(p.get('images',[])),{});add(name,v.get('price'),'https://alfatah.pk/products/'+p['handle']+'?variant='+str(v['id']),image.get('src'),category(name,p.get('product_type','')),v['id'],unit_override=(package(v.get('title',''),category(name,p.get('product_type','')))if v.get('title')not in [None,'Default Title']and re.search(r'\b\d+\s*(?:kg|gm|g|ml|l)\b',v['title'],re.I)else('listed pack; verify selected weight',False)if re.search(r'\bTO\b',p['title'])else None))
 elif store=='Shophive':
  for r in partner_parse('Paklap',url,raw):add(r['name'],r['price'],r['source'],r.get('image'),'mobiles')
 elif store=='Mega.pk':
  soup=BeautifulSoup(raw,'html.parser')
  for card in soup.select('.lap_thu_box'):
   a=card.select_one('h3 a[href]');price=card.select_one('.cat_price');im=card.select_one('img')
   if not a or not price:continue
   for old in price.select('.was'):old.decompose()
   m=re.search(r'[\d,]+',price.get_text(' ',strip=True))
   if m:add(a.get_text(' ',strip=True),m[0],urllib.parse.urljoin(url,a['href']),im.get('src')if im else None,'mobiles',spec=(card.select_one('.detailer').get_text(' ',strip=True)if card.select_one('.detailer')else''))
 normalize(rows);return rows

def run():
 today=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5))).date().isoformat();path=ROOT/'data/extra-prices.json';rows={r['id']:r for r in json.loads(path.read_text())}if path.exists()else{};hp=ROOT/'data/extra-history.json';history=json.loads(hp.read_text())if hp.exists()else{};checks=[]
 def fetch(pair):
  store,url=pair
  try:
   req=urllib.request.Request(url,headers={'User-Agent':'PakistanPriceWatch/1.4 (daily public source-linked prices)'})
   with urllib.request.urlopen(req,timeout=22)as response:raw=response.read(6000000).decode('utf-8')
   offers=parse(store,url,raw,today)
   if not offers:raise ValueError('No validated priced product cards')
   return store,url,offers,None
  except Exception as e:return store,url,[],str(e)
 with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:
  for store,url,offers,error in pool.map(fetch,URLS):
   for r in offers:
    rows[r['id']]=r;a={x['date']:x for x in history.get(r['id'],[])};a[today]=dict(date=today,price=r['price'],source=r['source']);history[r['id']]=sorted(a.values(),key=lambda x:x['date'])[-400:]
   checks.append(dict(store=store,url=url,quotes=len(offers),status='updated'if offers else'failed; previous dated quotes retained',error=error))
 path.write_text(json.dumps(list(rows.values()),ensure_ascii=False,separators=(',',':'))+'\n');hp.write_text(json.dumps(history,separators=(',',':'))+'\n');(ROOT/'data/extra-source-report.json').write_text(json.dumps(dict(checked_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),checks=checks),indent=2)+'\n');print(json.dumps(checks))
if __name__=='__main__':run()
