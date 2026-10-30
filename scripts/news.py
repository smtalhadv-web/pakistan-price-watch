"""Daily source-linked news digests. Never fabricate a news story or republish article bodies."""
import concurrent.futures,datetime,email.utils,hashlib,json,pathlib,urllib.parse,urllib.request,xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).resolve().parents[1]
TOPICS={
 'economy':('Economy','Pakistan economy inflation rupee interest rates', 'Watch how inflation, currency movements and borrowing costs may affect household budgets and import costs. A headline alone does not establish that a retail price has changed.'),
 'business':('Business','Pakistan business companies industry investment', 'Company and industry developments can affect supply, stock availability and competition. Compare dated supplier offers before making a purchase decision.'),
 'trade':('Trade','Pakistan trade imports exports customs tariffs', 'Trade and customs developments can affect landed costs and delivery times. Check the original notification, effective date and product classification before applying a reported change to an item.')}
TZ=datetime.timezone(datetime.timedelta(hours=5))
def parse_feed(raw,topic,now):
 result=[]
 for item in ET.fromstring(raw).findall('./channel/item'):
  title=(item.findtext('title')or'').strip();link=(item.findtext('link')or'').strip();pub=(item.findtext('source')or'Publisher').strip()
  try:dt=email.utils.parsedate_to_datetime(item.findtext('pubDate')or'').astimezone(TZ)
  except (ValueError,TypeError):continue
  if not title or not link.startswith('https://') or not 0<=(now-dt).total_seconds()<=4*86400:continue
  if title.endswith(' - '+pub):title=title[:-len(pub)-3]
  result.append(dict(id=hashlib.sha256(link.encode()).hexdigest()[:16],title=title[:240],url=link,publisher=pub,published_at=dt.isoformat(),topic=topic))
 return result[:8]
def refresh():
 now=datetime.datetime.now(TZ);path=ROOT/'data/news.json';old=json.loads(path.read_text())if path.exists()else{'posts':[]};posts={p['id']:p for p in old.get('posts',[])};report=[]
 def fetch(topic):
  query=TOPICS[topic][1]+' when:2d';url='https://news.google.com/rss/search?'+urllib.parse.urlencode(dict(q=query,hl='en-PK',gl='PK',ceid='PK:en'))
  req=urllib.request.Request(url,headers={'User-Agent':'PakistanPriceWatch/1.2 (source-linked daily news digest)'})
  with urllib.request.urlopen(req,timeout=20)as response:raw=response.read(2000000)
  items=parse_feed(raw,topic,now)
  if not items:raise ValueError('No recent dated headlines returned')
  return items
 with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:
  futures={pool.submit(fetch,t):t for t in TOPICS}
  for future in concurrent.futures.as_completed(futures):
   t=futures[future]
   try:
    headlines=future.result();day=now.date().isoformat();id=t+'-'+day
    posts[id]=dict(id=id,topic=t,date=day,title=TOPICS[t][0]+' news briefing · '+day,context=TOPICS[t][2],headlines=headlines,fetched_at=now.isoformat());report.append(dict(topic=t,status='updated',headlines=len(headlines)))
   except Exception as exc:report.append(dict(topic=t,status='failed — previous dated posts retained',reason=str(exc)[:180]))
 data=dict(checked_at=now.isoformat(),checks=report,posts=sorted(posts.values(),key=lambda p:(p['date'],p['topic']),reverse=True)[:90]);path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print(json.dumps(data['checks']))
def publish(out,page,urls):
 from catalog_ui import E
 path=ROOT/'data/news.json';data=json.loads(path.read_text())if path.exists()else{'posts':[]};posts=data.get('posts',[]);(out/'blog').mkdir(exist_ok=True)
 def cards(a,prefix=''):
  return '<div class="hub-grid">'+''.join('<article class="hub-card"><small>'+E(TOPICS[p['topic']][0])+' · '+E(p['date'])+'</small><h2><a href="'+prefix+'blog/'+E(p['id'])+'.html">'+E(p['title'])+'</a></h2><p>'+E(p['context'])+'</p><strong>'+str(len(p['headlines']))+' linked headlines →</strong></article>'for p in a)+'</div>'
 body='<main id="main" class="home-layout"><h1>Pakistan economy, business & trade</h1><p>Daily news briefings from recent search-news results, with publisher links and publication dates. Selection reflects feed relevance and recency; it is not a measured popularity ranking. Briefings provide context, not verified product price changes.</p>'
 if any(x['status'].startswith('failed')for x in data.get('checks',[])):body+='<p class="notice">The latest news refresh was incomplete. Earlier briefings keep their original dates.</p>'
 for topic,(label,_,__)in TOPICS.items():body+='<section id="'+topic+'"><h2>'+label+'</h2>'+ (cards([p for p in posts if p['topic']==topic]) or '<p>No recent news briefing is available. The daily feed will appear after a successful refresh.</p>')+'</section>'
 (out/'blog.html').write_text(page('Pakistan economy, business and trade news',body+'</main>','blog.html'));urls.append('blog.html')
 for p in posts:
  path='blog/'+p['id']+'.html';body='<main id="main" class="prose panel"><p>'+E(TOPICS[p['topic']][0])+' · '+E(p['date'])+'</p><h1>'+E(p['title'])+'</h1><p>'+E(p['context'])+'</p><h2>Recent headlines</h2><p>These are attributed news links. Read the full reporting at the publisher; article bodies are not reproduced here.</p><ul class="news-headlines">'
  for h in p['headlines']:body+='<li><a href="'+E(h['url'])+'" target="_blank" rel="noopener noreferrer">'+E(h['title'])+' ↗</a><small>'+E(h['publisher'])+' · <time datetime="'+E(h['published_at'])+'">'+E(h['published_at'][:16].replace('T',' '))+' PKT</time></small></li>'
  body+='</ul><h2>Using news when comparing prices</h2><p>Check whether the report describes a proposal, an announcement or an effective rule. Then compare the same model, unit, grade and location using dated item quotes. News headlines do not change this site’s product prices automatically.</p><a href="../blog.html">All daily briefings →</a></main>'
  schema={'@context':'https://schema.org','@type':'BlogPosting','headline':p['title'],'datePublished':p['fetched_at'],'dateModified':p['fetched_at'],'description':p['context'],'author':{'@type':'Organization','name':'Pakistan Price Watch'},'citation':[h['url']for h in p['headlines']]}
  body+='<script type="application/ld+json">'+json.dumps(schema).replace('<','\\u003c')+'</script>';(out/path).write_text(page(p['title'],body,path,'../'));urls.append(path)
 return cards(posts[:3])
if __name__=='__main__':refresh()
