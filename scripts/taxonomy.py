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
 # Product type takes precedence over ingredient words and retailer hints.
 if not r.get('sheet') and not id.startswith('pbs-'):
  if has(r'\b(?:hair (?:oil|colou?r|clipper|straightener)|facewash|face wash|body (?:lotion|wash|spray)|shampoo|conditioner|toothpaste|toothbrush|skin cream|facial|moisturizer|sunscreen|razor|sanitary)\b',n):return'health'
  if has(r'\b(?:milk|curd|yogurt|yoghurt|cheese|mozzarella)\b',n)and not has(r'\b(?:soap|lotion|shampoo|body|face|feeding bottle)\b',n):return'grocery'
  if has(r'\b(?:diapers?|baby wipes|molfix|nappy)\b',n):return'baby'
  if has(r'\b(?:phone case|iphone case|back case|flip (?:book )?cover|silicone case|power strip|phone cover)\b',n):return'electronics'
  if old in ['electronics','mobiles'] and has(r'\b(?:rice cooker|mini fan|tower fan|fan heater|steam iron|microwave oven|reading light|night light|lightstrip|flashlight|steam mop|washing machine|refrigerator)\b',n):return'household'
  if old=='other' and has(r'\b(?:fruita vitals|grape juice)\b',n):return'grocery'
  if has(r'\b(?:foundation|make[ -]?up|nail polish|lip gloss)\b',n):return'health'
  if has(r'\b(?:school bag|pencil (?:case|pouch))\b',n):return'stationery'
  if has(r'\b(?:lunch bag|trolley bag|duffle|travel bag)\b',n):return'apparel'
  if has(r'\b(?:storage basket)\b',n):return'household'
  if has(r'\b(?:misri)\b',n):return'grocery'
  if old=='other'and has(r'\b(?:kids? keyboard|kidz|musical|transformer|projection wrist watch|flying aircraft|drone r/c|quadcopter)\b',n):return'baby'

 # Classify the product itself before ingredient or retailer catch-all rules.
 if has(r'\b(?:cat food|dog food|pet (?:food|snack)|cat litter)\b',n):return'pets'
 if has(r'\b(?:cushion cover|runner|wall clock|planter|curtain|bed sheet|bedsheet|towel)\b',n):return'household'
 if old=='other':
  rules=[('apparel',r'\b(?:sweatshirt|jacket|trousers|sneakers|sweater|socks|romper|cotton pants|denim pants|joggers|co-ord|frock|knitted top|embroidered|crossbody bag|(?:fusion|essentials|ethnic).*?(?:printed|dyed))\b'),('baby',r'\b(?:diaper|molfix|pampers|baby wipes|feeding bottle)\b'),('health',r'\b(?:facewash|face wash|body spray|facial mask|razor|hair color|shampoo|palmolive|sensitive (?:maxi|ultra)|sanitary|toothpaste|lotion|serum)\b'),('household',r'\b(?:airfreshner|air freshener|detergent|dishwash|washing|cleaner|charcoal|charcoa|tissue|foil|pillow|wipes|cushion)\b'),('meat',r'\b(?:fish|snapper)\b'),('property',r'\b(?:for rent|studio fully furnished)\b'),('mobiles',r'^infinix note'),('electronics',r'\b(?:laptops?|core i5|security cameras)\b'),('furniture',r'\b(?:safas|armchairs|soled wood)\b'),('produce',r'\b(?:tomatoes|banana|apple|capsicum|gourd|potato|cucumber|onion|ginger|garlic|mango|orange|lemon|spinach|okra|grapefruit|mussammi|pomegranate|cauliflower)\b'),('grocery',r'\b(?:atta|baisan|besan|lobia|chana|nescafe|chai|kracks|peek freans|cadbury|wheatable|lays|noms|rice|flour|milk|sugar|salt|ghee|tea|biscuit|juice|chocolate|noodle|pasta|ketchup|sauce|jam|honey|coffee|water|oil|rooh afza|nectar|sharbat|sharbet|redbull|coca cola|7up|fries|samosa|kabab|paratha|tikka|croquets|yogurt|cheddar|mozz|oats|porridge|cornflakes|fajita|nuggets|kofta|patties|rusks)\b'),('electronics',r'\bwatches\b')]
  for target,pattern in rules:
   if has(pattern,n):return target
 if old=='meat'and has(r'\b(?:powder|shan|masala|spice|seasoning)\b',n):return'grocery'
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
