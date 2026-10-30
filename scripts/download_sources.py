from bs4 import BeautifulSoup
from collect import ROOT
import urllib.request,concurrent.futures,json,re,hashlib,shutil
jobs=[];sheets=[]
soup=BeautifulSoup((ROOT/'raw/karachi.html').read_text(),'html.parser')
for tr in soup.select('tr'):
 a=tr.select_one('a[href]');td=tr.select('td')
 if a and '/uploads/' in a['href'] and td:
  title=td[0].get_text(' ',strip=True);key=re.sub('[^a-z]+','-',title.lower()).strip('-');url=a['href'];ext='.jpg' if not url.lower().endswith('.pdf') else '.pdf'
  rel='assets/'+key+'-'+hashlib.sha256(url.encode()).hexdigest()[:10]+ext
  sheets.append({'id':key,'title':title,'source':url,'file':rel,'date':'-'.join(reversed(re.search(r'\d{2}/\d{2}/\d{4}',title)[0].split('/'))),'city':'Karachi','note':'Official source image. Read date and units printed on the sheet; website index dates can differ.'});jobs.append((url,ROOT/rel))
s=BeautifulSoup((ROOT/'raw/pbs.html').read_text(),'html.parser')
for k,term in [('construction','Urban Construction'),('monthly','Average Monthly SPI'),('weekly','Annexure for week')]:
 for a in s.select('a[href]'):
  if term in a.get_text(' ',strip=True):jobs.append((a['href'],ROOT/'raw'/f'{k}.xlsx'));break
(ROOT/'data/sheets.json').write_text(json.dumps(sheets,indent=2))
def dl(pair):
 u,p=pair
 try:
  if p.suffix=='.jpg' and p.exists():return p.name,p.stat().st_size
  with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'PakistanPriceWatch/1.0'}),timeout=35)as r:b=r.read(12000000)
  p.write_bytes(b)
  if p.suffix=='.xlsx':shutil.copy(p,ROOT/'assets'/('pbs-'+p.name))
  return p.name,len(b)
 except Exception as e:return p.name,str(e)
with concurrent.futures.ThreadPoolExecutor(max_workers=5)as pool:
 for x in pool.map(dl,jobs):print(x)
