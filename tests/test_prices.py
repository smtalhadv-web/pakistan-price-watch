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
  result=subprocess.run(['node','-e',function+"if(!localMatch({city:'Pakistan'},'Karachi')||!localMatch({city:'Karachi'},'Karachi')||localMatch({city:'Lahore'},'Karachi')||localMatch({city:'Karachi'},'Pakistan'))process.exit(1)"],capture_output=True)
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
