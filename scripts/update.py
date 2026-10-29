"""Fail closed: update only a supported dated PSO table; retain other quotes."""
import json,re,datetime,urllib.request,pathlib
from html.parser import HTMLParser
ROOT=pathlib.Path(__file__).resolve().parents[1]
class Text(HTMLParser):
 def __init__(self):super().__init__();self.parts=[]
 def handle_data(self,d):self.parts.append(d.strip())
def parse_pso(raw):
 t=Text();t.feed(raw);s=' '.join(t.parts)
 m=re.search(r'Effective\s+From\s*:\s*([A-Za-z]+\s+\d{1,2},\s*\d{4})',s)
 if not m:raise ValueError('Effective date missing; retain prior quotes')
 date=datetime.datetime.strptime(m[1],'%B %d, %Y').date()
 if date>datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5))).date():raise ValueError('Future effective date')
 values={}
 for key,label in [('petrol','PREMIER EURO 5'),('diesel','HI-CETANE DIESEL EURO 5')]:
  m=re.search(re.escape(label)+r'\s+(?:Rs\.?\s*)?([\d,]+\.\d{1,2})\s*(?:/\s*Ltr|/\s*Litre)',s,re.I)
  if not m:raise ValueError('Fuel table format changed')
  value=float(m[1].replace(',',''))
  if not 50<value<1500:raise ValueError('Fuel price out of bounds')
  values[key]=(value,date.isoformat())
 return values
if __name__=='__main__':
 report={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sources':[],'manual_queue':['Commissioner Karachi fruit, vegetables and meat image sheets','SBP currency quotes','Gold and silver benchmarks: manual cross-check required','Electronics: variant and availability verification','Construction: dated supplier quote or PBS report']}
 prices=json.loads((ROOT/'data/prices.json').read_text())
 try:
  url='https://www.psopk.com/en/fuels/fuel-prices'
  req=urllib.request.Request(url,headers={'User-Agent':'PakistanPriceWatch/1.0 (daily public price check)'})
  with urllib.request.urlopen(req,timeout=35) as response: raw=response.read(4000000).decode('utf-8')
  values=parse_pso(raw)
  for r in prices:
   if r['id'] in values:
    value,date=values[r['id']]
    if date<r['date']:continue
    if date==r['date'] and value!=r['price']:raise ValueError('Conflicting same-date source value; manual review required')
    r.update(price=value,date=date,source=url)
  report['sources'].append({'source':'PSO','status':'checked','effective_date':next(iter(values.values()))[1]})
  (ROOT/'data/prices.json').write_text(json.dumps(prices,indent=2)+'\n')
 except Exception as e:report['sources'].append({'source':'PSO','status':'manual_required','reason':str(e)})
 (ROOT/'data/update-report.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
