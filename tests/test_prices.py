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
