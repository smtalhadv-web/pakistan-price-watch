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
