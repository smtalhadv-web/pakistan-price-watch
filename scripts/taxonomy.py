"""Conservative item-type classification; boundaries prevent sand/sandal collisions."""
import re

def has(pattern,name):return bool(re.search(pattern,name,re.I))
def survey_category(name):
 if has(r'\b(?:shirt(?:ing)?|shoes?|sandals?|lawn|cloth|chappal|georgette)\b',name):return'apparel'
 if has(r'\b(?:beef|mutton|chicken|eggs?)\b',name):return'meat'
 if has(r'\b(?:potatoes|potato|onions?|tomatoes|tomato|bananas?|garlic|ginger)\b',name):return'produce'
 if has(r'\b(?:cement|iron bars?|bricks?|bajri|sand|enamel)\b',name):return'construction'
 if has(r'\b(?:petrol|diesel|lpg|firewood|electricity|gas charges)\b',name):return'fuel'
 if has(r'\b(?:painter|mason|labour|plumber|electrician|haircut|telephone)\b',name):return'services'
 if has(r'\b(?:urea|dap|fertilizer)\b',name):return'agriculture'
 if has(r'\b(?:toilet soap|toothpaste|shampoo)\b',name):return'health'
 if has(r'\b(?:soap|match box|energy saver|bulb|washing|detergent)\b',name):return'household'
 return'grocery'

def category_for(r):
 n=r['name'];old=r['category'];id=r['id']
 if id.startswith('pbs-weekly-'):return survey_category(n)
 if id.startswith('pbs-construction-'):return'services'if has(r'^(?:painter|mason|labour|plumber|electrician)\b',n)else'construction'
 if r.get('sheet'):return old # Verified official class/grade has an explicit category.
 # Subject nouns, not power ratings or incidental model-description substrings.
 if has(r'\b(?:e[ -]?gift card|mystery box)\b',n):return'other'
 if has(r'\b(?:repair|installation) service\b',n):return'services'
 if has(r'\bshoe (?:cabinet|rack)\b',n):return'furniture'
 if has(r'^(?:Redmi\s+(?:Note\s*\d|A\d|\d)|Xiaomi\s+\d+\s+(?:Ultra|Pro))',n)and '+'in n and not has(r'\b(?:charger|power bank|adapter|cable|cover|case)\b',n):return'mobiles'
 if has(r'\b(?:sandals?|chappal|shoes?|backpack|daypack|sling bag|luggage|sunglasses|computer glasses|reusable bag)\b',n):return'apparel'
 if old=='electronics'and has(r'\b(?:chair|gaming desk|motorized desk|adjustable (?:height )?(?:electric )?gaming desk)\b',n):return'furniture'
 if has(r'\b(?:robot builder|mini robot builder)\b',n):return'baby'
 if has(r'\b(?:electric scooter|electric (?:folding )?bike)\b',n):return'automobiles'
 if old in ['electronics','mobiles']and has(r'\b(?:screwdriver|tool kit|air compressor)\b',n):return'machinery'
 if old in ['electronics','mobiles']and has(r'\b(?:toothbrush|shaver|hair dryer|body composition scale|smart scale|anti-pollution mask|trimmer)\b',n):return'health'
 if old in ['electronics','mobiles']and has(r'\b(?:vacuum|air purifier|humidifier|kettle|air fryer|induction cooker|standing fan|portable fan|bedside lamp|desk lamp|ceiling light|led bulb|space heater|garment steamer|lint remover|soap dispenser|water filter|vacuum flask|mosquito repellent|umbrella)\b',n):return'household'
 if old in ['electronics','mobiles']and has(r'\b(?:writing tablet|roller pen|gel pen|roller pen refill|photo printer paper)\b',n):return'stationery'
 # A charger beginning "Xiaomi 20W" is not a Xiaomi phone. Phone-plus-accessory bundles keep their primary handset category.
 if old=='mobiles'and has(r'\b(?:power bank|powerbank|power adapter|charger|charging stand|mobile battery|display panel|usb cable)\b',n)and not has(r'\b(?:redmi|poco|galaxy|iphone)\b.*\+',n):return'electronics'
 if old=='electronics'and (has(r'^Mi\s+(?:\d{1,2}\b|\d{1,2}\s+Lite\b)',n)or has(r'^(?:Redmi\s+(?:A\d|Note\s*\d|\d)|POCO\s+[CFMX]\s*\d)',n))and not has(r'\b(?:pad|watch|monitor|projector|tv|power bank|adapter|charger|cable|cover|case)\b',n):return'mobiles'
 return old

def normalize(rows):
 changes=[]
 for r in rows:
  category=category_for(r)
  if r['category']!=category:changes.append({'id':r['id'],'name':r['name'],'from':r['category'],'to':category});r['category']=category
 return changes
