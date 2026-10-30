"""Item visuals with explicit provenance: listing photo, representative photo, or named illustration."""
import json,re,urllib.parse,urllib.request,concurrent.futures,datetime
from collect import ROOT
# Ordered specific subjects avoid e.g. milk powder becoming a photograph of fresh milk.
SUBJECTS=[
('Sandal',r'sandal|chappal'),('Dress shirt',r'shirting|shirt'),('Textile',r'georgette|lawn printed|long cloth'),
('Powdered milk',r'powdered milk|nido'),('Milk',r'\bmilk\b'),('Yogurt',r'curd|dahi'),('Wheat flour',r'flour|atta|chapati|roti|naan'),('Rice',r'\brice\b'),('Lentil',r'daal|\bdal\b|pulse|masoor|moong|mash'),('Chickpea',r'chickpea|kabuli|gram'),('Bread',r'\bbread\b|rusk'),('Sugar',r'\bsugar\b'),('Jaggery',r'gur|jaggery'),('Cooking oil',r'cooking oil|mustard oil|olive oil|coconut oil'),('Ghee',r'\bghee\b'),('Tea',r'\btea\b'),('Samosa',r'samosa'),('Pakora',r'pakora'),('Jalebi',r'jalebi'),('Turmeric',r'turmeric'),('Coriander',r'coriander'),('Chili pepper',r'chil|chilli'),('Black pepper',r'black pepper'),('Cumin',r'cumin'),('Salt',r'\bsalt\b'),
('Beef',r'beef|buffalo.*meat'),('Mutton',r'\bmutton\b'),('Chicken as food',r'chicken meat|chicken breast|chicken leg'),('Chicken',r'chicken live|chicken farm'),('Egg as food',r'\beggs?\b'),('Fish as food',r'\bfish\b'),('Prawn',r'prawns?'),
('Apple',r'\bapple\b'),('Banana',r'banana'),('Tomato',r'tomato'),('Potato',r'potato'),('Onion',r'\bonion'),('Garlic',r'garlic'),('Ginger',r'ginger'),('Spinach',r'spinach'),('Carrot',r'carrot'),('Radish',r'radish'),('Turnip',r'turnip'),('Eggplant',r'brinjal'),('Cabbage',r'cabbage'),('Cauliflower',r'cauliflower'),('Bell pepper',r'capsicum'),('Cucumber',r'cucumber'),('Okra',r'okra'),('Bitter melon',r'bitter gourd'),('Luffa',r'ridge gourd'),('Calabash',r'bottle gourd'),('Watermelon',r'watermelon'),('Melon',r'\bmelon\b'),('Guava',r'guava'),('Mango',r'mango'),('Pear',r'\bpear\b'),('Persimmon',r'persimmon'),('Pomegranate',r'pomegranate'),('Papaya',r'papaya'),('Grape',r'\bgrapes?\b'),('Date palm',r'\bdates\b'),('Lemon',r'lemon'),('Grapefruit',r'grapefruit'),('Manilkara zapota',r'chikoo'),('Mentha',r'\bmint\b'),('Sweet lemon',r'mosambi'),
('Brick',r'\bbricks?\b'),('Concrete masonry unit',r'cement blocks|concrete blocks'),('Cement',r'\bcement\b'),('Construction aggregate',r'bajri|aggregate'),('Sand',r'\bsand\b'),('Rebar',r'iron bars'),('Paint',r'enamel|paint|coating|putty'),('Plywood',r'plywood'),('Tile',r'\btile\b'),('Door',r'\bdoor\b'),
('Gasoline',r'petrol|premier euro|\bjp-1\b'),('Diesel fuel',r'diesel|\bldo\b'),('Kerosene',r'kerosene|\bsko\b'),('Liquefied petroleum gas',r'\blpg\b|gas charges'),('Firewood',r'firewood'),('Electricity meter',r'electricity charges'),
('Gold bar',r'\bgold\b'),('Silver',r'\bsilver\b'),('Soap',r'\bsoap\b'),('Match',r'match box'),('Compact fluorescent lamp',r'energy saver'),('Cigarette',r'cigarette'),('Telephone',r'telephone call'),
('Smartphone',r'android smartphone|foldable smartphone|rugged phone'),('Feature phone',r'feature phone'),('Sandpaper',r'sandpaper')]
CURRENCY={'US Dollar':'United States dollar','Euro':'Euro','British Pound':'Pound sterling','UAE Dirham':'United Arab Emirates dirham','Saudi Riyal':'Saudi riyal','Kuwaiti Dinar':'Kuwaiti dinar','Canadian Dollar':'Canadian dollar','Australian Dollar':'Australian dollar','Omani Riyal':'Omani rial','Japanese Yen':'Japanese yen','Chinese Yuan':'Renminbi','Swiss Franc':'Swiss franc'}
def subject_for(r):
 n=r['name']
 if r['category']=='currency':return CURRENCY.get(n.split(' · ')[0],n.split(' · ')[0])
 if n.startswith(('Suzuki ','Toyota ')):return '' # Exact current generation/trim photo must come from the manufacturer.
 if r['id'].startswith('catalog-')and r['category']not in ['grocery','produce','meat','construction','fuel','metals','currency']:return n
 if 'ladies sandal'in n.lower():return "Women's sandals"
 if r['category']=='services':return '' # No implied photograph of a particular service provider.
 for subject,pattern in SUBJECTS:
  if re.search(pattern,n,re.I):return subject
 if r['id'].startswith('catalog-'):return n
 return''
APPROVED_ALIASES={'Baby diapers':'Diaper','Baby wipes':'Wet wipe','Bench vice':'Vise','Car battery':'Automotive battery','Concrete masonry unit':'Concrete block','Copper pipe':'Copper tubing','Heavy truck':'Large goods vehicle','School bag':'Backpack','Potash fertilizer':'Potash','EV charger':'Charging station','Gaming console':'Video game console','Speaker system':'Loudspeaker','Wheat seed':'Wheat berry','Oats':'Oat','Computer RAM':'Random-access memory','Computer keyboard':'Computer keyboard','Rotavator':'Cultivator','Egg as food':'Eggs as food','Mutton':'Lamb and mutton','Match':'Match','Construction aggregate':'Construction aggregate','Sweet lemon':'Sweet lemon'}
BLOCKED_SUBJECTS={'Animal feed','External hard drive','Electrical wire','Laborer','Canadian dollar','Badminton racket','Tennis racket','Lithium battery'}
def valid_subject(key,value):
 if key in BLOCKED_SUBJECTS:return False
 expected=APPROVED_ALIASES.get(key,key)
 return expected.casefold()==value['subject'].casefold()
def fetch(url):
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'PakistanPriceWatch/1.2 (public source reference; github.com/smtalhadv-web/pakistan-price-watch)'})
  with urllib.request.urlopen(req,timeout=25)as q:return json.loads(q.read(8000000))
 except Exception:return None

def run():
 rows=[]
 for fn in ['prices','catalog','extra-catalog']:rows+=json.loads((ROOT/'data'/f'{fn}.json').read_text())
 from taxonomy import normalize
 normalize(rows)
 subjects=sorted({subject_for(r)for r in rows if not r.get('image')and subject_for(r)})
 registry=json.loads((ROOT/'data/item-images.json').read_text())if(ROOT/'data/item-images.json').exists()else{}
 new=[s for s in subjects if s not in registry]
 batches=[new[i:i+40]for i in range(0,len(new),40)]
 for batch in batches:
  q=fetch('https://en.wikipedia.org/w/api.php?'+urllib.parse.urlencode(dict(action='query',titles='|'.join(batch),prop='pageimages',piprop='thumbnail|name',pithumbsize=500,redirects=1,format='json')))
  if not q:continue
  pages={p['title']:p for p in q.get('query',{}).get('pages',{}).values()};aliases={x['from']:x['to']for x in q.get('query',{}).get('normalized',[])+q.get('query',{}).get('redirects',[])}
  for title in batch:
   target=title
   for _ in range(4):target=aliases.get(target,target)
   p=pages.get(target,{})
   if p.get('thumbnail')and p.get('pageimage'):
    registry[title]={'image':p['thumbnail']['source'],'file':p['pageimage'],'article':'https://en.wikipedia.org/wiki/'+urllib.parse.quote(p['title'].replace(' ','_')),'image_source':'https://commons.wikimedia.org/wiki/File:'+urllib.parse.quote(p['pageimage']),'subject':p['title'],'image_kind':'representative','checked_at':datetime.date.today().isoformat()}
 # Licensing evidence is captured from the Commons file itself, not inferred from an article.
 files=sorted({x['file']for x in registry.values()if not x.get('license')})
 for i in range(0,len(files),40):
  q=fetch('https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(dict(action='query',titles='|'.join('File:'+x for x in files[i:i+40]),prop='imageinfo',iiprop='extmetadata',format='json')))
  if not q:continue
  for p in q.get('query',{}).get('pages',{}).values():
   meta=next(iter(p.get('imageinfo',[])),{}).get('extmetadata',{});name=p.get('title','').removeprefix('File:');license=meta.get('LicenseShortName',{}).get('value','');artist=meta.get('Artist',{}).get('value','')
   for x in registry.values():
    if x['file'].replace('_',' ')==name.replace('_',' '):x['license']=license;x['artist_html']=artist;x['license_url']=meta.get('LicenseUrl',{}).get('value','')
 # Keep only photos with verifiable free/public-domain licenses. Unknown/nonfree images are not reused.
 registry={k:v for k,v in registry.items()if valid_subject(k,v)and re.search(r'^(CC|Public domain|PD|GFDL|FAL|CC0)',v.get('license',''),re.I)}
 (ROOT/'data/item-images.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'subjects_requested':len(subjects),'licensed_representative_images':len(registry)}))
if __name__=='__main__':run()

def apply_images(rows,out):
 """Preserve listing photos; enrich known subjects and provide honest named fallback art."""
 import hashlib,html,textwrap
 from html.parser import HTMLParser
 from presentation import ICONS
 class Plain(HTMLParser):
  def __init__(self):super().__init__();self.parts=[]
  def handle_data(self,data):self.parts.append(data)
 registry=json.loads((ROOT/'data/item-images.json').read_text())if(ROOT/'data/item-images.json').exists()else{}
 dest=out/'assets/item-illustrations';dest.mkdir(exist_ok=True)
 icon_rules=[(r'badminton','🏸'),(r'tennis','🎾'),(r'cricket','🏏'),(r'table tennis','🏓'),(r'chess','♟'),(r'tyre|tire','🛞'),(r'painter','🖌'),(r'mason|labour|laborer','👷'),(r'plumber','🔧'),(r'electrician','⚡'),(r'sandal|sandals|chappal','👡'),(r'shoe','👟'),(r'backpack|bag|luggage','🎒'),(r'shirt|cloth|georgette','👕'),(r'watch|band strap','⌚'),(r'phone|mobile|smartphone','📱'),(r'laptop|macbook|notebook','💻'),(r'monitor|television|projector','🖥'),(r'camera','📷'),(r'battery|power ?bank','🔋'),(r'charger|adapter|cable','🔌'),(r'headphone|earbud|headset','🎧'),(r'speaker|microphone','🔊'),(r'keyboard','⌨'),(r'mouse','🖱'),(r'carrot','🥕'),(r'onion','🧅'),(r'tomato','🍅'),(r'potato','🥔'),(r'rice|wheat|flour|grain','🌾'),(r'milk|yogurt|curd','🥛'),(r'egg','🥚'),(r'bread|rusk','🍞'),(r'fish|prawn','🐟'),(r'beef|mutton|chicken meat','🥩'),(r'chicken','🐓'),(r'apple','🍎'),(r'banana','🍌'),(r'grape','🍇'),(r'lemon','🍋'),(r'mango','🥭'),(r'watermelon','🍉'),(r'brick|cement block','🧱'),(r'bulb|lamp|energy saver','💡'),(r'toothbrush|toothpaste','🪥'),(r'soap','🧼'),(r'chair','🪑'),(r'bed|mattress','🛏'),(r'car|suzuki|toyota|sedan|suv','🚗'),(r'bike|motorcycle|scooter','🏍'),(r'ball','⚽'),(r'pen|pencil','🖊'),(r'paper|book','📚')]
 for r in rows:
  filename=hashlib.sha256((r['category']+'|'+r['name']).encode()).hexdigest()[:18]+'.svg';r['fallback_image']='assets/item-illustrations/'+filename
  n=r['name'].lower();icon=next((icon for pattern,icon in icon_rules if re.search(r'\b(?:'+pattern+r')\b',n)),'◇');lines=textwrap.wrap(r['name'],37)[:5]
  svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 380"><rect width="500" height="380" rx="22" fill="#eff5ed"/><text x="250" y="130" text-anchor="middle" font-size="86">'+icon+'</text>'+''.join('<text x="250" y="'+str(185+i*27)+'" text-anchor="middle" font-family="sans-serif" font-size="18" fill="#305c42">'+html.escape(line)+'</text>'for i,line in enumerate(lines))+'<text x="250" y="354" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#70856b">ITEM ILLUSTRATION · EXACT PHOTO UNAVAILABLE</text></svg>';(dest/filename).write_text(svg)
  if r.get('image'):
   r['image_kind']=r.get('image_kind','listing');continue
  subject=subject_for(r);entry=registry.get(subject)
  if entry:
   r['image']=entry['image'];r['image_kind']='representative';r['image_subject']=entry['subject'];r['image_source']=entry['image_source'];r['image_license']=entry['license'];r['image_license_url']=entry.get('license_url','');p=Plain();p.feed(entry.get('artist_html',''));r['image_credit']=' '.join(p.parts).strip()
  else:r['image']=r['fallback_image'];r['image_kind']='illustration'
 return rows
