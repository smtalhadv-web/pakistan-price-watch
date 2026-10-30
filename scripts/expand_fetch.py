from collect import ROOT,fetch
import concurrent.futures
URLS={
'suzuki':'https://suzukipakistan.com/all-prices',
'corolla':'https://toyota-indus.com/corolla/',
'yaris':'https://toyota-indus.com/yaris/',
'interwood':'https://interwood.pk/collections/living',
'interwood-products':'https://interwood.pk/products.json?limit=250',
'makita':'https://www.toolsmart.pk/collections/makita',
'makita-products':'https://www.toolsmart.pk/collections/makita/products.json?limit=250',
'kamadi':'https://kamadi.pk/collections/makita',
'kamadi-products':'https://kamadi.pk/collections/makita/products.json?limit=250',
'apple':'https://priceoye.pk/mobiles/apple',
'laptops':'https://priceoye.pk/laptops',
'watches':'https://priceoye.pk/smart-watches',
'earbuds':'https://priceoye.pk/wireless-earbuds',

}
URLS.update({brand+'-2':'https://priceoye.pk/mobiles/'+brand+'?page=2'for brand in ['samsung','xiaomi','vivo','oppo','realme','infinix','tecno','apple']})
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
  for r in ex.map(fetch,URLS.items()):print(r)
