CATS={'fuel':'Petroleum & energy','produce':'Fruit & vegetables','meat':'Meat & poultry','grocery':'Groceries','metals':'Gold & silver','currency':'Currencies','construction':'Building materials','mobiles':'Mobile phones','automobiles':'Automobiles & motorcycles','electronics':'Electronics & computing','furniture':'Furniture','machinery':'Machinery & power tools','household':'Household & kitchen','apparel':'Clothing, footwear & accessories','services':'Labour & services','agriculture':'Agriculture','health':'Health & personal care','baby':'Baby & children','sports':'Sports & leisure','stationery':'Stationery & books'}
def mode(r):
 if r.get('price')is None:return'unpriced'
 if r['id'].startswith('pbs-')or r.get('period'):return'reference'
 if r.get('pricing_mode'):return r['pricing_mode']
 if r['category']in['mobiles','automobiles','electronics','furniture','machinery','apparel']:return'listed'
 if r['id'].startswith('pbs-') or r.get('period'):return'reference'
 return'daily'

CATS['other']='Other items & gift cards'

CATS['pets']='Pet food & supplies'

CATS['property']='Property & rentals'
