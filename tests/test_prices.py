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
