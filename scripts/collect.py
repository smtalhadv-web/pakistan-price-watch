import concurrent.futures,urllib.request,pathlib,json
ROOT=pathlib.Path(__file__).resolve().parents[1]
URLS={'karachi':'https://commissionerkarachi.gos.pk/karachi/pricelist','forex':'https://hamariweb.com/finance/forex/Default.aspx','gold':'https://hamariweb.com/finance/gold_rate/','silver':'https://hamariweb.com/finance/silver_rate/','pso-history':'https://www.psopk.com/fuel-prices/pol/archives','samsung':'https://priceoye.pk/mobiles/samsung','xiaomi':'https://priceoye.pk/mobiles/xiaomi','vivo':'https://priceoye.pk/mobiles/vivo','oppo':'https://priceoye.pk/mobiles/oppo','realme':'https://priceoye.pk/mobiles/realme','infinix':'https://priceoye.pk/mobiles/infinix','tecno':'https://priceoye.pk/mobiles/tecno','appliances':'https://priceoye.pk/air-conditioners','pbs':'https://www.pbs.gov.pk/price-statistics/'}
def fetch(pair):
 k,u=pair
 (ROOT/'raw').mkdir(exist_ok=True)
 try:
  req=urllib.request.Request(u,headers={'User-Agent':'PakistanPriceWatch/1.0 (public price reference)'})
  with urllib.request.urlopen(req,timeout=30) as r:b=r.read(6000000)
  (ROOT/'raw'/f'{k}.html').write_bytes(b)
  return k,len(b)
 except Exception as e:
  (ROOT/'raw'/f'{k}.html').unlink(missing_ok=True)
  return k,str(e)
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
  results=list(pool.map(fetch,URLS.items()))
  (ROOT/'data/fetch-status.json').write_text(json.dumps(results,indent=2))
  for row in results:print(row)
