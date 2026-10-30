import json,re,datetime,statistics,hashlib
from catalog_ui import E,archive
from model import CATS,mode

def subgroup(r):
 n=r['name'].lower();cat=r['category']
 rules={
 'agriculture':[('Farm machinery',r'tractor|harvester|rotavator|cultivator|seed drill'),('Irrigation & sprayers',r'irrigation|sprayer'),('Fertilizers & soil',r'fertilizer|compost|urea|dap|potash'),('Seeds & animal feed',r'.')],
 'services':[('Vehicle & appliance repairs',r'repair|maintenance|installation'),('Construction trades',r'painter|mason|labour|plumber|electrician|carpenter|welder'),('Other services',r'.')],
 'baby':[('Baby care & feeding',r'diaper|wipes|feeding|molfix'),('Baby transport & furniture',r'stroller|cot|car seat'),('Toys & children’s essentials',r'.')],
 'sports':[('Fitness equipment',r'treadmill|exercise|dumbbell|fitness'),('Outdoor & travel',r'camping|suitcase|tent'),('Sports equipment',r'.')],
 'stationery':[('Books & learning',r'book|quran|reference'),('Paper & writing',r'paper|pen|pencil|notebook|marker|paint'),('Office & school supplies',r'.')],
 'pets':[('Cat food',r'cat'),('Dog food',r'dog'),('Pet supplies',r'.')],
 'other':[('Gift cards',r'gift card'),('Mystery boxes',r'mystery box'),('Unclassified — review pending',r'.')],
 'mobiles':[('Smartphones',r'iphone|galaxy|redmi|poco|xiaomi|samsung|vivo|oppo|tecno|infinix|realme|android|smartphone'),('Feature & specialist phones',r'.')],
 'electronics':[('Tablets & e-readers',r'\b(?:ipad|tablet|e-reader)\b'),('Laptops & desktop PCs',r'laptop|macbook|notebook|ideapad|thinkpad|inbook|desktop computer'),('Computer parts & storage',r'ram|memory|processor|ssd|hard drive|graphics card|motherboard|casing|power suppl'),('Phone accessories',r'charger|adapter|power ?bank|mobile battery|usb cable'),('Audio & wearables',r'earbud|earphone|headphone|speaker|watch|band'),('Monitors & imaging',r'monitor|projector|camera|printer|scanner'),('Other electronics',r'.')],
 'property':[('Rentals',r'rent|studio'),('Property listings',r'.')],
 'grocery':[('Snacks & bakery',r'cookies|biscuit|bread|rusks|kracks|lays|chocolate|cadbury|noms|wheatable|peek freans'),('Prepared & frozen food',r'samosa|kabab|kofta|nugget|paratha|fries|patty|patties|tikka|fajita|croquette|croquet'),('Drinks & beverages',r'nectar|juice|sharbat|sharbet|rooh afza|coca cola|7up|redbull|coconut water'),('Rice, flour & grains',r'rice|flour|wheat|oat|grain'),('Pulses & legumes',r'pulse|dal|daal|lentil|chickpea|gram|moong|mash|masoor'),('Cooking oil & ghee',r'oil|ghee'),('Dairy & eggs',r'milk|curd|yogurt|cheese|butter|egg'),('Spices, salt & sugar',r'salt|sugar|spice|pepper|turmeric|coriander|chilli'),('Tea, snacks & other groceries',r'.')],
 'produce':[('Vegetables',r'potato|tomato|onion|garlic|ginger|cabbage|cauliflower|carrot|radish|turnip|gourd|brinjal|eggplant|spinach|okra|cucumber|capsicum|beet|mint|coriander|chilli'),('Fruit',r'.')],
 'meat':[('Poultry & eggs',r'chicken|poultry|egg'),('Beef & mutton',r'beef|mutton|goat|buffalo|calf'),('Fish & other meat',r'.')],
 'construction':[('Cement, bricks & aggregates',r'cement|brick|bajri|sand|aggregate|concrete'),('Metal, wood & fixtures',r'iron|steel|door|window|plywood|pipe|wire|circuit'),('Finishes & other materials',r'.')],
 'apparel':[('Footwear',r'shoe|sandal|chappal'),('Bags & accessories',r'bag|backpack|sunglass|luggage'),('Children’s clothing',r'girls|boys|newborn|children'),('Outerwear & knitwear',r'jacket|sweater|sweatshirt'),('Clothing & fabrics',r'.')],
 'furniture':[('Chairs & desks',r'chair|desk'),('Beds & bedroom',r'bed|wardrobe|dresser'),('Sofas & living room',r'sofa|couch|coffee|side table'),('Other furniture',r'.')],
 'household':[('Kitchen appliances & utensils',r'kettle|fryer|cooker|oven|microwave|cookware|blender|juicer|mug|casserole|dinner|kitchen'),('Cleaning, laundry & air care',r'vacuum|washing|clean|purifier|humidifier|fan|steamer|soap|detergent'),('Home textiles & decor',r'cushion|runner|clock|planter|curtain|sheet|towel'),('Other household items',r'.')],
 'automobiles':[('Motorcycles & electric mobility',r'motorcycle|scooter|electric bike|gd 110|gs 150|gr 150|gsx'),('Vehicles & parts',r'.')],
 'machinery':[('Power tools',r'drill|saw|grinder|screwdriver|hammer|sander|planer'),('Industrial, pumps & engines',r'.')],
 'health':[('Grooming & personal care',r'shaver|toothbrush|toothpaste|shampoo|soap|cream|cosmetic|perfume|lotion|serum'),('Health equipment & supplies',r'.')],
 'fuel':[('Vehicle fuels',r'petrol|diesel|euro|jp-1'),('Solar, batteries & backup power',r'solar|battery|inverter|ups|turbine|controller|ev charger'),('Utilities & other energy',r'.')],
 'metals':[('Gold',r'gold'),('Silver & other metals',r'.')],
 'currency':[('Open market',r'open market'),('Interbank & other currency quotes',r'.')]}
 label=next((label for label,p in rules.get(cat,[(CATS[cat],r'.')])if re.search(p,n)),CATS[cat]);slug=cat+'-'+re.sub(r'[^a-z0-9]+','-',label.lower()).strip('-')
 return label,slug

def estimate(r,points,today=None):
 if mode(r)!='daily'or not re.search(r'reported|benchmark',r.get('kind',''),re.I):return {'status':'unavailable','reason':'This quote type is not eligible. Official rates, survey averages, used asking prices and retail variants are not inferred from a daily-market model.'}
 today=today or datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5))).date()
 a=sorted({p['date']:p for p in points if p.get('source')==r.get('source')and p.get('price',0)>0 and datetime.date.fromisoformat(p['date'])<=today}.values(),key=lambda p:p['date'])[-30:]
 if len(a)<8:return {'status':'unavailable','reason':'At least 8 same-source dated observations are needed. No missing price history is generated.'}
 latest=datetime.date.fromisoformat(a[-1]['date'])
 if (today-latest).days>0:return {'status':'unavailable','reason':'The latest observation is stale; no next-day estimate is displayed.'}
 diffs=[abs(y['price']-x['price'])for x,y in zip(a,a[1:])if(datetime.date.fromisoformat(y['date'])-datetime.date.fromisoformat(x['date'])).days==1]
 if len(diffs)<7:return {'status':'unavailable','reason':'Not enough consecutive daily observations; irregular or weekly observations cannot establish this baseline.'}
 spread=sorted(diffs)[min(len(diffs)-1,int(.8*len(diffs)))];last=a[-1]['price']
 return dict(status='experimental',date=(latest+datetime.timedelta(days=1)).isoformat(),as_of=latest.isoformat(),center=last,low=max(.01,last-spread),high=last+spread,observations=len(a),mae=statistics.mean(diffs[-3:]),method='Carry-forward baseline; range uses the 80th-percentile observed absolute daily change. This is a scenario range, not a calibrated confidence interval.')
def predictor(r,points):
 e=estimate(r,points);out='<section class="detail-section predictor"><div class="eyebrow">EXPERIMENTAL · NOT A GUARANTEE</div><h2>Price predictor</h2>'
 if e['status']=='unavailable':return out+'<p>'+E(e['reason'])+'</p></section>'
 return out+'<p>Next-day baseline for '+E(e['date'])+' · PKR / '+E(r['unit'])+'</p><strong class="forecast-range">'+f'{e["low"]:,.2f} – {e["high"]:,.2f}'+'</strong><p>Carry-forward center: PKR '+f'{e["center"]:,.2f}'+'. Based on '+str(e['observations'])+' observations through '+e['as_of']+'.</p><p>'+E(e['method'])+'</p><p>Recent one-day backtest mean absolute error: PKR '+f'{e["mae"]:,.2f}'+'. Small-sample result; future performance is unknown. Policy changes, supply shocks and taxes are not modelled. Not a trading signal or financial advice.</p></section>'

def feature_pages(out,rows,page,urls,base):
 subgroups={}
 for r in rows:subgroups.setdefault(r['subcategory_slug'],[]).append(r)
 (out/'subcategories').mkdir(exist_ok=True)
 for slug,items in subgroups.items():
  r=items[0];path='subcategories/'+slug+'.html';body='<main id="main" class="home-layout" data-archive-subcategory="'+E(slug)+'"><h1>'+E(r['subcategory'])+' prices in Pakistan</h1><p>Open an item for source dates, exact variants and separately identified retail or asking prices.</p><div id="archive-host">'+archive([x for x in items if x['city']=='Pakistan'and mode(x)!='asking'],'../')+'</div><div class="pagination"><button id="previous">← Previous</button><span id="page-label"></span><button id="next">Next →</button></div></main>'
  (out/path).write_text(page(r['subcategory']+' prices in Pakistan',body,path,'../'));urls.append(path)
 wholesale=[r for r in rows if r['price']is not None and re.search(r'wholesale|farm gate',r['name'],re.I)and r['category']in ['grocery','meat','produce']]
 path='wholesale.html';body='<main id="main" class="home-layout" data-archive-kind="wholesale"><h1>Wholesale and farm-gate reference rates</h1><p>These are dated, source-linked official reference notifications. They are not independently observed mandi transactions or a guarantee of current dealer prices. Check unit, grade, city and original notice.</p><div id="archive-host">'+archive([r for r in wholesale if r['city']=='Pakistan'])+'</div><div class="pagination"><button id="previous">← Previous</button><span id="page-label"></span><button id="next">Next →</button></div><p><a href="https://amis.pk/" target="_blank" rel="noopener">AMIS official wholesale information ↗</a> · No fresh AMIS quote is republished until a verified dated source is available.</p></main>'
 (out/path).write_text(page('Pakistan wholesale and farm-gate reference rates',body,path));urls.append(path)
 asking=[r for r in rows if mode(r)=='asking'];path='used-items.html';body='<main id="main" class="home-layout" data-archive-mode="asking"><h1>Used items & classified asking prices</h1><p>Public classified snapshots, not completed-sale values. Listings can be new, used or condition-unconfirmed. Check PTA/JV, battery, storage, condition and availability with the original listing. No seller contact details are copied.</p><div class="archive-filters"><input id="search" type="search" aria-label="Search items" placeholder="Search classified titles…"></div><p id="count"></p><div id="archive-host">'+archive([r for r in asking if r['city']=='Pakistan'][:30])+'</div><div class="pagination"><button id="previous">← Previous</button><span id="page-label"></span><button id="next">Next →</button></div></main>'
 (out/path).write_text(page('Used item asking prices in Pakistan',body,path));urls.append(path)
 candidates=[r for r in rows if r['id']in ['gold-24k','silver','fx-us-dollar-open-market-sell']]
 histories=json.loads((out/'data/history.json').read_text());body='<main id="main" class="home-layout"><h1>Experimental price predictor</h1><p>Baseline scenarios from dated, same-source reported benchmarks. These are not statistical confidence intervals, trading signals or guaranteed future prices. Many quote types remain ineligible until enough suitable observations exist.</p>'+''.join('<h2>'+E(r['name'])+'</h2>'+predictor(r,histories.get(r['id'],[]))for r in candidates)+'</main>'
 (out/'predictor.html').write_text(page('Experimental Pakistan price predictor and history-based ranges',body,'predictor.html'));urls.append('predictor.html')
 path='shares.html';body='''<main id="main" class="home-layout"><h1>Pakistan shares & stock market hub</h1><p>Research Pakistani shares through the official exchange. No live, delayed, historical share prices or index levels are republished here without the relevant data rights.</p><div class="hub-grid"><a class="hub-card" href="https://dps.psx.com.pk/" target="_blank" rel="noopener"><h2>PSX market watch ↗</h2><p>Open the official portal. Its data is generally delayed 5 minutes unless indicated otherwise.</p></a><a class="hub-card" href="https://dps.psx.com.pk/screener/" target="_blank" rel="noopener"><h2>Official share screener ↗</h2><p>Explore companies and published exchange information at the original source.</p></a><article class="hub-card"><h2>On-site quote feed</h2><p>Not connected. A PSX-authorized redistribution feed is required before numeric share prices, histories or predictions can be published here.</p><a href="https://www.psx.com.pk/psx/product-and-services/data-services-vending" target="_blank" rel="noopener">PSX data licensing information ↗</a></article></div><p>Compare securities only with appropriate financial context. No purchase recommendation or guaranteed-return claim is made.</p></main>'''
 (out/path).write_text(page('Pakistan shares and PSX stock market hub',body,path));urls.append(path)
