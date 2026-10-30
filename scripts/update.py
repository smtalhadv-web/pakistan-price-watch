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
 import subprocess,sys
 for name in ['collect.py','download_sources.py','ingest.py','expand_fetch.py','expand.py','commerce.py','item_images.py']:
  result=subprocess.run([sys.executable,str(ROOT/'scripts'/name)],check=False)
  if result.returncode:
   print(name+' failed: existing dated quotes retained; manual review required')
