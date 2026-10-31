import json,re,datetime
from bs4 import BeautifulSoup
from collect import ROOT
from ingest import slug,num,TODAY

def expand():
 rows={r['id']:r for r in json.loads((ROOT/'data/prices.json').read_text())};history=json.loads((ROOT/'data/history.json').read_text());pending={r['id']:r for r in json.loads((ROOT/'data/extra-catalog.json').read_text())}if(ROOT/'data/extra-catalog.json').exists()else {};status=[]
 def add(id,name,category,price,source,unit='item',**kw):
  if price is None or price<=0:
   if id not in rows:pending[id]=dict(id=id,name=name,category=category,price=None,source=source,unit=unit,date=None,city='Pakistan',kind='Catalog · price unavailable',pricing_mode='unpriced',**kw)
   return
  pending.pop(id,None);r=dict(id=id,name=name,category=category,price=price,source=source,unit=unit,date=TODAY,city='Pakistan',kind='Published listing · observed',pricing_mode='listed',**kw);r['last_checked_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();rows[id]=r
  a={p['date']:p for p in history.get(id,[])};a[TODAY]={'date':TODAY,'price':price,'source':source};history[id]=sorted(a.values(),key=lambda p:p['date'])[-400:]
 def attempt(name,fn):
  try:n=len(rows);fn();status.append(dict(source=name,status='parsed',new_records=len(rows)-n))
  except Exception as e:status.append(dict(source=name,status='manual_required',reason=str(e)))
 def retail():
  for key in ['apple','laptops','watches','earbuds']+[b+'-2'for b in ['samsung','xiaomi','vivo','oppo','realme','infinix','tecno','apple']]:
   p=ROOT/'raw'/f'{key}.html'
   if not p.exists():continue
   s=BeautifulSoup(p.read_text(),'html.parser')
   for b in s.select('.productBox'):
    a=b.select_one('a[href]');n=b.select_one('.p-title');v=b.select_one('.price-box')
    if not a or not n or not v:continue
    u=a['href']
    if not u.startswith('https://priceoye.pk/'):continue
    add('retail-'+slug(u.split('/')[-1]),n.get_text(' ',strip=True),'mobiles'if'/mobiles/'in u else'electronics',num(v.get_text(' ',strip=True)),u,unit='device; verify variant',note='Advertised retailer listing. Check exact variant, warranty, delivery and stock; not a daily commodity rate.')
 attempt('Additional mobile, laptop, watch and audio listings',retail)
 def shops():
  for key,base,cat in [('interwood-products','https://interwood.pk','furniture'),('makita-products','https://www.toolsmart.pk','machinery'),('kamadi-products','https://kamadi.pk','machinery')]:
   p=ROOT/'raw'/f'{key}.html'
   if not p.exists():continue
   payload=json.loads(p.read_text());products=payload.get('products',[])
   if not products:continue
   for product in products:
    for v in product.get('variants',[]):
     title=product['title'];variant=v.get('title','')
     if variant and variant!='Default Title':title+=' · '+variant
     u=base+'/products/'+product['handle']+'?variant='+str(v['id'])
     add('shop-'+slug(base.split('//')[1])+'-'+str(v['id']),title,cat,float(v.get('price')or 0),u,availability='In stock'if v.get('available')else'Out of stock',note='Published variant listing; not a permanent or guaranteed price. Check supplier, exact model, specifications, availability and delivery.')
 attempt('Furniture and power-tool variant listings',shops)
 def suzuki():
  s=BeautifulSoup((ROOT/'raw/suzuki.html').read_text(),'html.parser')
  for t in s.select('table'):
   heading=t.find_previous(['h2','h3','h4']);model=heading.get_text(' ',strip=True)if heading else''
   cat='machinery'if'Strokes'in model else'automobiles'
   for tr in t.select('tr')[1:]:
    td=tr.select('td')
    if len(td)<2:continue
    name=td[0].get_text(' ',strip=True)
    if not name:continue
    if model and not name.lower().startswith(model.lower())and cat!='machinery':name=model+' '+name
    add('suzuki-'+slug(name),'Suzuki '+name,cat,num(td[1].get_text()),'https://suzukipakistan.com/all-prices',unit='vehicle'if cat=='automobiles'else'outboard engine',note='Manufacturer published list price observed on the date shown. Registration, withholding taxes, freight and delivery charges may be additional; not a daily rate.')
 attempt('Suzuki manufacturer vehicles and marine engines',suzuki)
 def toyota():
  raw=(ROOT/'raw/corolla.html').read_text()
  for key,value in re.findall(r'"([\w]+Price)"\s*:\s*"([^"]+)"',raw):
   title=re.sub('Price$','',key);title=re.sub(r'([a-z])([A-Z])',r'\1 \2',title)
   title=re.sub(r'([A-Z]+)([A-Z][a-z])',r'\1 \2',title)
   title=title.replace('Toyota','').strip();title='Toyota '+title
   price=num(value)if value.startswith('Rs ')else None
   add('toyota-'+slug(key.replace('Price','')),title,'automobiles',price,'https://toyota-indus.com/corolla/',unit='vehicle',availability=value if price is None else'Check dealer',note='Price from the manufacturer’s published vehicle-price configuration, observed on the date shown. Ex-factory/list basis; taxes, freight, registration and actual order availability need dealer verification.')
 attempt('Toyota manufacturer vehicle price configuration',toyota)
 # Existing phone listings belong in their own category. Keep observed dates intact.
 for r in rows.values():
  if r['id'].startswith('pbs-'):r['pricing_mode']='reference'
  elif 'priceoye.pk/mobiles/'in r.get('source',''):r['category']='mobiles';r['pricing_mode']='listed'
  elif r['category']in['electronics','furniture','machinery','automobiles']:r['pricing_mode']='listed'
 (ROOT/'data/prices.json').write_text(json.dumps(list(rows.values()),ensure_ascii=False,separators=(',',':'))+'\n')
 (ROOT/'data/history.json').write_text(json.dumps(history,ensure_ascii=False,separators=(',',':'))+'\n')
 (ROOT/'data/extra-catalog.json').write_text(json.dumps(list(pending.values()),ensure_ascii=False,separators=(',',':'))+'\n')
 report=json.loads((ROOT/'data/update-report.json').read_text());report['sources']=[x for x in report['sources']if x['source']not in {x['source']for x in status}]+status;report['quotes']=len(rows);report['unpriced_supplier_items']=len(pending)
 (ROOT/'data/update-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'quotes':len(rows),'supplier_catalog_without_price':len(pending),'sources':status},indent=2))
if __name__=='__main__':expand()
