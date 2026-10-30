"""Match only explicit trade-stage quotes with the same item, city, unit and publisher."""
import re
from urllib.parse import urlparse
from catalog_ui import E

def stage(r):
 return 'wholesale' if re.search(r'\bwholesale\b',r['name'],re.I) else 'farm gate' if re.search(r'\bfarm[ -]gate\b',r['name'],re.I) else 'retail'
def identity(r):
 name=re.sub(r'\b(?:wholesale|retail|farm[ -]gate)\b','',r['name'],flags=re.I)
 return (r['category'],re.sub(r'[^\w]+',' ',name.casefold()).strip(),r['city'],r['unit'].casefold(),urlparse(r.get('source') or '').netloc)
def attach(rows):
 quotes={}
 for r in rows:
  r['trade_stage']=stage(r)
  if r['price'] is not None and stage(r)!='retail':quotes.setdefault(identity(r),[]).append(r)
 for r in rows:
  r['wholesale_quotes']=[{k:x.get(k) for k in ['id','name','price','unit','city','date','source','kind','trade_stage']}for x in quotes.get(identity(r),[]) if x['id']!=r['id'] and (not r.get('date') or x['date']==r['date'])]
def section(r):
 quotes=r.get('wholesale_quotes',[])
 if stage(r)!='retail' and r['price'] is not None:quotes=[r]+quotes
 out='<section class="detail-section wholesale-section"><h2>Wholesale & farm-gate prices</h2>'
 if not quotes:return out+'<p>No matching verified wholesale quote is available for this exact item, unit and location.</p></section>'
 for q in quotes:
  out+='<p><strong>'+E(q['trade_stage'].title())+' · PKR '+f'{q["price"]:,.2f}'+' / '+E(q['unit'])+'</strong><br>'+E(q['city'])+' · '+E(q['date'])+' · '+E(q['kind'])+' · <a href="'+E(q['source'])+'" target="_blank" rel="noopener">Original quote ↗</a></p>'
 return out+'<p>These published reference rates retain their original dates. Bulk quantities, delivery and current dealer availability must be confirmed separately.</p></section>'
