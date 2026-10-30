import unittest,sys,pathlib,json
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from update import parse_pso
from build import validate,ROOT
class PriceTests(unittest.TestCase):
 def test_seed(self):validate(json.loads((ROOT/'data/prices.json').read_text()))
 def test_parser(self):
  data=parse_pso('<p>Effective From: October 29, 2026</p><td>PREMIER EURO 5</td><td>Rs.377.91/Ltr</td><td>HI-CETANE DIESEL EURO 5</td><td>Rs.399.82/Ltr</td>')
  self.assertEqual(data['petrol'],(377.91,'2026-10-29'))
 def test_no_placeholder(self):
  with self.assertRaises(ValueError):parse_pso('<p>Service unavailable 0.00</p>')
 def test_missing_rate(self):
  with self.assertRaises(ValueError):parse_pso('Effective From: October 29, 2026 PREMIER EURO 5 Rs.377.91/Ltr')
 def test_duplicates(self):
  r=json.loads((ROOT/'data/prices.json').read_text())[0]
  with self.assertRaises(AssertionError):validate([r,r])


class ExpandedDataTests(unittest.TestCase):
 def test_histories_match_quote_units_and_latest(self):
  h=json.loads((ROOT/'data/history.json').read_text())
  for r in json.loads((ROOT/'data/prices.json').read_text()):
   a=h.get(r['id'],[])
   self.assertEqual(a,sorted(a,key=lambda p:p['date']))
   self.assertEqual(len({p['date']for p in a}),len(a))
   self.assertTrue(all(p['price']>0 and p['source'].startswith('https://') for p in a))
 def test_transcribed_quotes_keep_original_image(self):
  for r in json.loads((ROOT/'data/manual-quotes.json').read_text()):
   self.assertTrue((ROOT/r['sheet']).is_file(),r['sheet'])
   self.assertIn('commissionerkarachi.gos.pk/uploads/',r['source'])
 def test_pbs_averages_explicit(self):
  for r in json.loads((ROOT/'data/prices.json').read_text()):
   if r['id'].startswith('pbs-'):
    self.assertIn('average',r['kind'])
    self.assertTrue(r.get('period'))

class CatalogTests(unittest.TestCase):
 def test_unknown_prices_are_not_zero_quotes(self):
  for name in ['catalog.json','extra-catalog.json']:
   for r in json.loads((ROOT/'data'/name).read_text()):
    self.assertIsNone(r['price'])
    self.assertIsNone(r['date'])
    self.assertEqual(r['pricing_mode'],'unpriced')
 def test_surveys_stay_references(self):
  from model import mode
  for r in json.loads((ROOT/'data/prices.json').read_text()):
   if r['id'].startswith('pbs-'):self.assertEqual(mode(r),'reference')

class ComparisonTests(unittest.TestCase):
 def test_comparisons_preserve_variant_and_period(self):
  from presentation import comparison_key
  base=dict(category='electronics',name='Laptop 16GB 512GB',unit='device',kind='Retailer listing',pricing_mode='listed',date='2026-10-30')
  self.assertNotEqual(comparison_key(base),comparison_key({**base,'name':'Laptop 8GB 512GB'}))
  survey={**base,'kind':'PBS weekly average','pricing_mode':'reference','period':'Week ending 2026-10-22'}
  self.assertNotEqual(comparison_key(survey),comparison_key({**survey,'period':'Week ending 2026-10-29'}))
  self.assertNotEqual(comparison_key(base),comparison_key(survey))
 def test_parent_location(self):
  import subprocess
  app=(ROOT/'app.js').read_text();function=app[app.index('function localMatch'):app.index('function readLocation')]
  result=subprocess.run(['node','-e',function+"if(!localMatch({city:'Pakistan'},'Karachi')||!localMatch({city:'Karachi'},'Karachi')||localMatch({city:'Lahore'},'Karachi')||!localMatch({city:'Karachi'},'Pakistan'))process.exit(1)"],capture_output=True)
  self.assertEqual(result.returncode,0,result.stderr)

class ItemArchiveTests(unittest.TestCase):
 def test_plus_model_is_distinct(self):
  from catalog_ui import family
  r=dict(id='test-phone',name='Redmi Note 15 Pro 5G',category='mobiles',unit='device',price=1,pricing_mode='listed',kind='Retailer')
  self.assertNotEqual(family(r),family({**r,'name':'Redmi Note 15 Pro+ 5G'}))
 def test_one_observation_graph_has_no_fabricated_line(self):
  from catalog_ui import graph
  result=graph([{'date':'2026-10-30','price':100}],'Test')
  self.assertIn('<circle',result);self.assertNotIn('<polyline',result)

class TaxonomyTests(unittest.TestCase):
 def test_whole_words_prevent_sand_sandal_collision(self):
  from taxonomy import survey_category
  self.assertEqual(survey_category('Ladies Sandal Bata'),'apparel')
  self.assertEqual(survey_category('Gents Sandal Bata'),'apparel')
  self.assertEqual(survey_category('Sand · black pit'),'construction')
  self.assertEqual(survey_category('Energy Saver Philips 14 Watt'),'household')
 def test_retail_subjects_and_phone_accessories(self):
  from taxonomy import category_for
  base=dict(id='test',category='electronics')
  for name,category in [('Gaming Chair Black','furniture'),('Mi 23.8 Desktop Monitor','electronics'),('Mi 11 Lite','mobiles'),('Mi Cordless Screwdriver','machinery'),('Mi Electric Toothbrush','health'),('Mi Smart Kettle','household'),('Shoe rack','furniture')]:
   self.assertEqual(category_for({**base,'name':name}),category,name)
  self.assertEqual(category_for({**base,'category':'mobiles','name':'Xiaomi 20W Power Adapter'}),'electronics')
  self.assertEqual(category_for({**base,'category':'mobiles','name':'Redmi 12 + Mi LCD Writing Tablet'}),'mobiles')
 def test_full_snapshot_reclassification_preserves_quotes(self):
  from taxonomy import normalize
  rows=json.loads((ROOT/'data/prices.json').read_text());before={r['id']:(r['price'],r['date'],r['source'],r['unit'])for r in rows};normalize(rows)
  for r in rows:
   self.assertEqual(before[r['id']],(r['price'],r['date'],r['source'],r['unit']))
   if 'Sandal Bata'in r['name']:self.assertEqual(r['category'],'apparel')

class ItemImageTests(unittest.TestCase):
 def test_subject_does_not_confuse_a_product_with_its_contents(self):
  from item_images import subject_for,valid_subject
  self.assertEqual(subject_for(dict(id='catalog-rice-cooker',name='Rice cooker',category='household')),'Rice cooker')
  self.assertEqual(subject_for(dict(id='pbs-weekly-40-karachi',name='Ladies Sandal Bata',category='apparel')),"Women's sandals")
  self.assertEqual(subject_for(dict(id='suzuki-alto',name='Suzuki Alto VXR',category='automobiles')),'')
  self.assertFalse(valid_subject('Badminton racket',{'subject':'Racket (sports equipment)'}))

class PartnerMarketTests(unittest.TestCase):
 def test_classified_price_units_and_contacts(self):
  from partner_sources import number,sanitize
  self.assertEqual(number('Rs 1.69 Lac'),169000)
  self.assertEqual(number('Rs 1.2 crore'),12000000)
  self.assertEqual(number('Rs 35K'),35000)
  self.assertIsNone(number('Call for price'))
  self.assertNotIn('03001234567',sanitize('Call 03001234567 phone'))
 def test_unconfirmed_packs_do_not_merge_with_verified_offers(self):
  from catalog_ui import family
  a=dict(id='a',name='Cooking Oil',category='grocery',price=100,pricing_mode='listed',kind='Retailer listing',unit='item',comparison_eligible=False)
  self.assertNotEqual(family(a),family({**a,'id':'b'}))
 def test_branch_schema_is_required_for_foodpanda_quotes(self):
  from partner_sources import parse
  self.assertEqual(parse('Foodpanda / Kifayah','https://www.foodpanda.pk/shop/a036/kifayah-supermarket-pechs','<p>Rs. 50</p>'),[])
 def test_predictor_uses_past_same_source_daily_observations(self):
  from market_features import estimate
  import datetime
  r=dict(id='test-gold',category='metals',price=109,pricing_mode='daily',kind='Reported benchmark',source='https://example.com/gold')
  today=datetime.date(2026,10,30)
  pts=[dict(date=(today-datetime.timedelta(days=9-i)).isoformat(),price=100+i,source=r['source'])for i in range(10)]
  e=estimate(r,pts,today);self.assertEqual(e['status'],'experimental');self.assertEqual(e['date'],'2026-10-31');self.assertLessEqual(e['low'],e['center']);self.assertLessEqual(e['center'],e['high'])
  self.assertEqual(estimate({**r,'pricing_mode':'asking'},pts,today)['status'],'unavailable')
  self.assertEqual(estimate(r,pts[:2],today)['status'],'unavailable')
 def test_subcategories_keep_household_and_phone_accessories_apart(self):
  from market_features import subgroup
  self.assertEqual(subgroup(dict(category='apparel',name='Ladies Sandal Bata'))[0],'Footwear')
  self.assertEqual(subgroup(dict(category='grocery',name='Cooking Oil 5L'))[0],'Cooking oil & ghee')
  self.assertEqual(subgroup(dict(category='electronics',name='Xiaomi 20W Power Adapter'))[0],'Phone accessories')

class PartnerFeedTests(unittest.TestCase):
 def test_partner_records_are_sourced_and_public_fields_only(self):
  import json
  p=ROOT/'data/partner-prices.json'
  if not p.exists():return
  rows=json.loads(p.read_text());validate(rows)
  for r in rows:
   self.assertFalse({'seller','phone','email','address','latitude','longitude'}.intersection(r))
   if r['store']in ['OLX','Metro']:self.assertFalse(r['comparison_eligible'])
   if r['store']=='Foodpanda / Kifayah':self.assertEqual(r['city'],'Karachi')

class PackIdentityTests(unittest.TestCase):
 def test_exact_pack_equivalence_keeps_variants_separate(self):
  from catalog_ui import family
  r=dict(id='test-pack',category='grocery',name='Brand Milk 1 Ltr',price=1,unit='item',pricing_mode='listed',kind='Retailer listing')
  self.assertEqual(family(r),family({**r,'name':'Brand Milk 1000ml'}))
  self.assertNotEqual(family(r),family({**r,'name':'Brand Milk 100ml'}))
  self.assertNotEqual(family(r),family({**r,'name':'Brand Lactose Free Milk 1000ml'}))

class NavigationAndTradeTests(unittest.TestCase):
 def test_primary_product_category(self):
  from taxonomy import category_for
  for name,cat in [("Eminent Men's Knitted Sweatshirt",'apparel'),('Zimbo Cat Food Chicken Flavour','pets'),('Terra Cushion Cover','household'),('Shan Chicken Handi 50Gm','grocery'),('Sunridge Super White Atta','grocery'),('Queen Fish','meat'),('Coca Cola Can 250 ML','grocery')]:
   self.assertEqual(category_for(dict(id='test',name=name,category='other' if name!='Shan Chicken Handi 50Gm'else'meat')),cat,name)
 def test_wholesale_does_not_cross_grade_city_or_unit(self):
  from wholesale import attach
  base=dict(id='retail',category='grocery',name='Regular flour · retail',city='Karachi',unit='kg',date='2026-10-30',price=130,source='https://example.com/notice',kind='Official notified')
  bulk={**base,'id':'bulk','name':'Regular flour · wholesale','price':122}
  rows=[base,bulk,{**base,'id':'lahore','city':'Lahore'},{**base,'id':'fine','name':'Fine flour · retail'},{**base,'id':'bag','unit':'20 kg'},{**base,'id':'old','date':'2026-10-20'}];attach(rows)
  self.assertEqual(base['wholesale_quotes'][0]['price'],122)
  for r in rows[2:]:self.assertEqual(r['wholesale_quotes'],[])
 def test_news_ignores_undated_and_future_items(self):
  from news import parse_feed,TZ
  import datetime
  now=datetime.datetime(2026,10,31,8,tzinfo=TZ)
  xml='<rss><channel><item><title>No date</title><link>https://example.com/a</link></item><item><title>Future</title><link>https://example.com/b</link><pubDate>Sun, 01 Nov 2026 10:00:00 GMT</pubDate></item><item><title>A headline - Publisher</title><link>https://example.com/c</link><source>Publisher</source><pubDate>Fri, 30 Oct 2026 10:00:00 GMT</pubDate></item></channel></rss>'
  a=parse_feed(xml,'trade',now);self.assertEqual(len(a),1);self.assertEqual(a[0]['title'],'A headline')

class ProductGroupTests(unittest.TestCase):
 def test_capacity_choices_share_product_but_never_quote_identity(self):
  from products import prepare
  base=dict(id='a',name='Samsung Galaxy A56 (8GB-128GB)',category='mobiles',unit='device',price=100,source='https://shop.example/a',city='Pakistan',kind='Retailer',pricing_mode='listed')
  a=dict(base);b={**base,'id':'b','name':'Samsung Galaxy A56 (12GB-256GB)'}
  prepare([a,b]);self.assertEqual(a['product_key'],b['product_key']);self.assertNotEqual(a['variant_key'],b['variant_key']);self.assertEqual(a['variant_count'],2)
 def test_plus_models_and_generations_remain_distinct(self):
  from products import product_key
  a=dict(id='a',name='Redmi Note 15 Pro',category='mobiles',unit='device',price=1,kind='Retailer',pricing_mode='listed')
  self.assertNotEqual(product_key(a),product_key({**a,'name':'Redmi Note 15 Pro+'}))
  self.assertNotEqual(product_key(a),product_key({**a,'name':'Redmi Note 14 Pro'}))
 def test_same_store_duplicates_keep_latest_and_old_url_alias(self):
  from products import deduplicate
  a=dict(id='a',name='Same phone',category='mobiles',unit='device',store='Shop',price=120,source='https://shop.example/phone',city='Karachi',date='2026-10-29',kind='Retailer',pricing_mode='listed')
  b={**a,'id':'b','price':110,'date':'2026-10-30'}
  rows,aliases=deduplicate([a,b]);self.assertEqual(len(rows),1);self.assertEqual(rows[0]['price'],110);self.assertEqual(aliases['a'],'b')
 def test_city_quotes_and_used_listings_stay_separate(self):
  from products import deduplicate,product_key
  a=dict(id='a',name='Phone 128GB',category='mobiles',unit='device',store='Shop',price=120,source='https://shop.example/phone',city='Karachi',date='2026-10-30',kind='Retailer',pricing_mode='listed')
  rows,_=deduplicate([a,{**a,'id':'b','city':'Lahore'}]);self.assertEqual(len(rows),2)
  self.assertNotEqual(product_key({**a,'pricing_mode':'asking'}),product_key({**a,'id':'b','pricing_mode':'asking'}))
 def test_pack_sizes_share_card_but_remain_selectable(self):
  from products import prepare
  a=dict(id='a',name='Brand Milk 1L',category='grocery',unit='1L',price=1,kind='Retailer',pricing_mode='listed');b={**a,'id':'b','name':'Brand Milk 500ml','unit':'500ml'}
  prepare([a,b]);self.assertEqual(a['product_key'],b['product_key']);self.assertNotEqual(a['variant_key'],b['variant_key'])
 def test_subject_before_ingredient(self):
  from taxonomy import category_for
  for name,cat,old in [('Vatika Onion Hair Oil 100Ml','health','grocery'),('Olper Full Cream Milk 1000Ml','grocery','health'),('Gray Silicone Back Case for iPhone 15 Pro','electronics','mobiles'),('Xiaomi Multifunctional Rice Cooker 4L','household','electronics')]:self.assertEqual(category_for(dict(id='test',name=name,category=old)),cat)

class ExtraSourceReaderTests(unittest.TestCase):
 def test_shopify_selected_weight_overrides_title_range(self):
  from extra_sources import parse
  raw=json.dumps({'products':[{'title':'Apple (1 KG TO 250 GM)','handle':'apple','variants':[{'id':1,'title':'250 GM','price':'100'}]}]})
  r=parse('Al-Fatah','https://alfatah.pk/products.json',raw,'2026-10-31')[0]
  self.assertEqual(r['unit'],'250 GM');self.assertEqual(r['price'],100);self.assertEqual(r['category'],'produce')
 def test_mega_uses_current_price_not_struck_out_price(self):
  from extra_sources import parse
  raw='<div class="lap_thu_box"><h3><a href="https://www.mega.pk/mobiles_products/1/phone.html">Samsung Galaxy A56 128GB</a></h3><div class="cat_price"><div class="was">120,000 - PKR</div>110,000<span> - PKR</span></div></div>'
  r=parse('Mega.pk','https://www.mega.pk/mobiles/',raw,'2026-10-31')[0]
  self.assertEqual(r['price'],110000);self.assertEqual(r['category'],'mobiles')

class StableProductURLTests(unittest.TestCase):
 def test_new_store_and_title_prefix_keep_product_url(self):
  from products import prepare
  a=dict(id='z',name='Xiaomi Redmi Note 15 Pro',category='mobiles',unit='device',price=100,kind='Retailer',pricing_mode='listed')
  prepare([a]);canonical=a['canonical_id']
  b={**a,'id':'a','name':'Redmi Note 15 Pro · Blue / 8GB - 256GB'}
  prepare([a,b]);self.assertEqual(canonical,a['canonical_id']);self.assertEqual(canonical,b['canonical_id'])
