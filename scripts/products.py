"""Product grouping is separate from exact quote matching. Never mix variant prices."""
import collections,hashlib,html,re,urllib.parse
from decimal import Decimal
from model import mode

def textkey(s):
 return re.sub(r'[^\w]+',' ',html.unescape(str(s)).casefold().replace('+',' plus ')).strip()
def unitkey(s):
 s=str(s).casefold().strip()
 if re.search(r'device|exact.*variant',s):return'device'
 def convert(m):
  n=Decimal(m[1]);u=m[2].lower();n*=1000 if u in ['kg','l','ltr','litre','liter','litres','liters'] else 1
  return str(n.normalize())+('ml' if u in ['ml','l','ltr','litre','liter','litres','liters']else'g')
 return textkey(re.sub(r'\b(\d+(?:\.\d+)?)\s*(kg|gm|g|ml|litres?|liters?|ltr|l)\b',convert,s))
def sourcekey(url):
 u=urllib.parse.urlsplit(url or'');q=urllib.parse.parse_qsl(u.query)
 q=[(k,v)for k,v in q if not k.lower().startswith(('utm_','fbclid','gclid'))]
 return urllib.parse.urlunsplit((u.scheme,u.netloc.lower().removeprefix('www.'),u.path.rstrip('/'),urllib.parse.urlencode(sorted(q)),''))
def base_name(r):
 name=html.unescape(r['name']).strip();base=name.split(' · ')[0]
 if r['category']in ['mobiles','electronics'] and mode(r)=='listed':
  # Remove RAM/storage/color choices, preserving generation, connectivity and model suffixes.
  base=re.sub(r'\([^)]*\b(?:\d+\s*(?:GB|TB))[^)]*\)','',base,flags=re.I)
  base=re.sub(r'\b\d+\s*GB\s*(?:RAM)?\s*[/+-]\s*\d+\s*(?:GB|TB)\b','',base,flags=re.I)
  base=re.sub(r'\b\d+\s*(?:GB|TB)\s*(?:RAM|ROM|SSD|Storage)?\b','',base,flags=re.I)
  base=re.sub(r'\b(?:NON[ -]?PTA|PTA (?:Approved|Non Approved))\b','',base,flags=re.I)
  base=re.sub(r'\s*[-–·]\s*(?:black|white|blue|green|grey|gray|silver|gold|purple|pink)\s*$','',base,flags=re.I)
 if r['category']in ['grocery','health','household','pets'] and mode(r)=='listed':
  base=re.sub(r'\b\d+(?:\.\d+)?\s*(?:kg|gm|g|ml|litres?|liters?|ltr|l|pcs)\b','',base,flags=re.I)
  base=re.sub(r'\(\s*(?:to)?\s*\)','',base,flags=re.I)
  base=re.sub(r'\s*[,/-]\s*$','',base)
 return re.sub(r'\s+',' ',base).strip(' ,-·') or name

def exact_key(r):
 # Full titles and pack identity remain authoritative even when cards share a product.
 return '|'.join([textkey(r['name']),unitkey(r['unit']),mode(r),r.get('condition','')if mode(r)=='asking' else''])
def product_key(r):
 if r.get('manufacturer_model')and r['category']=='machinery':return 'machinery|'+textkey(r['manufacturer_model'])
 if mode(r)=='asking':return 'classified|'+r['id'] # Individual used items are never interchangeable stock.
 basis=mode(r)
 if basis=='unpriced':basis='catalog'
 return '|'.join([r['category'],textkey(base_name(r)).removeprefix('xiaomi ')if r['category']=='mobiles'and textkey(base_name(r)).startswith('xiaomi redmi')else textkey(base_name(r)),basis,r['kind']if basis in ['reference','daily']else''])
def deduplicate(rows):
 chosen={};aliases={}
 for r in rows:
  if r['price']is None:key=('catalog',r['id'])
  else:key=(urllib.parse.urlsplit(r.get('source')or'').netloc.lower().removeprefix('www.')or r.get('store'),r['city'],exact_key(r),r.get('scope',''),r.get('kind','')if mode(r)in ['reference','daily']else'',r.get('period',''),sourcekey(r.get('source')) if mode(r)=='asking' or r.get('comparison_eligible')is False else'')
  if key not in chosen:chosen[key]=r;continue
  old=chosen[key]
  # Latest source observation wins; keep aliases so old URLs continue to work.
  if (r.get('date')or'',r.get('last_checked_at',''),bool(r.get('image')),r['id'])>(old.get('date')or'',old.get('last_checked_at',''),bool(old.get('image')),old['id']):aliases[old['id']]=r['id'];chosen[key]=r
  else:aliases[r['id']]=old['id']
 for key in aliases:
  while aliases[key]in aliases:aliases[key]=aliases[aliases[key]]
 return list(chosen.values()),aliases

def prepare(rows):
 groups=collections.defaultdict(list)
 for r in rows:
  r.pop('family',None);r['product_key']=product_key(r);r['product_name']=base_name(r);r['variant_key']=hashlib.sha256(exact_key(r).encode()).hexdigest()[:16]
  suffix=r['name'].partition(' · ')[2]
  r['variant_label']=(suffix+' · 'if suffix else'')+r['name']+' / '+r['unit']
  r['family']=r['product_key'];groups[r['product_key']].append(r)
 for peers in groups.values():
  representative=min(peers,key=lambda r:(r['price'] is None,r['id']));canonical='product-'+re.sub(r'[^a-z0-9]+','-',representative['product_key'].split('|')[1]).strip('-')[:65]+'-'+hashlib.sha256(representative['product_key'].encode()).hexdigest()[:10];count=len({r['variant_key']for r in peers})
  for r in peers:r.update(canonical_id=canonical,variant_count=count)
 return groups
