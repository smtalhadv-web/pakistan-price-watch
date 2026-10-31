"""Run current source readers, preserve valid dated data, publish auditable refresh health."""
import datetime,json,math,pathlib,subprocess,sys,time,os
ROOT=pathlib.Path(__file__).resolve().parents[1]
FILES=['prices.json','partner-prices.json','extra-prices.json']
STAGES=[('collect.py',120),('download_sources.py',150),('ingest.py',180),('expand_fetch.py',150),('expand.py',180),('commerce.py',600),('partner_sources.py',210),('extra_sources.py',100)]
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(path,data):
 tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');os.replace(tmp,path)
def records():
 result={}
 for name in FILES:
  p=ROOT/'data'/name
  if p.exists():
   for r in json.loads(p.read_text()):result[r['id']]=r
 return result

def validate_prices():
 for r in records().values():
  value=r['price']
  if isinstance(value,bool)or not isinstance(value,(int,float))or not math.isfinite(value)or not 0<value<1e10:raise ValueError('Invalid price for '+r['id'])
  if not r.get('source','').startswith('https://'):raise ValueError('Missing source for '+r['id'])
  if datetime.date.fromisoformat(r['date'])>datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5))).date():raise ValueError('Future quote date for '+r['id'])

def source_checks(started,stages=None):
 checks=[]
 for name,key in [('update-report.json','sources'),('commerce-report.json','sources'),('partner-source-report.json','checks'),('extra-source-report.json','checks')]:
  owner={'update-report.json':'ingest.py','commerce-report.json':'commerce.py','partner-source-report.json':'partner_sources.py','extra-source-report.json':'extra_sources.py'}[name]
  if stages is not None and owner not in stages:continue
  path=ROOT/'data'/name
  if not path.exists():continue
  if datetime.datetime.fromtimestamp(path.stat().st_mtime,datetime.timezone.utc).isoformat()<started:continue
  data=json.loads(path.read_text())
  for x in data.get(key,[]):
   status=x.get('status','');ok=status in ['parsed','updated']and x.get('observed_offers',x.get('observed_records',x.get('offers',x.get('quotes',1))))>0
   checks.append(dict(source=x.get('store')or x.get('source')or x.get('url'),url=x.get('url'),status='verified'if ok else'not_verified',detail=status,quotes=x.get('observed_offers',x.get('observed_records',x.get('offers',x.get('quotes',0))))))
 return checks

def run():
 before=records();path=ROOT/'data/refresh-status.json';started=now();report=dict(started_at=started,completed_at=None,status='running',timezone='Asia/Karachi',scheduled_times=['08:30','20:30'],stages=[],source_checks=[])
 save(path,report)
 for filename,timeout in STAGES:
  # A failed/aborted writer must not replace the last valid price/history files.
  backup={p:p.read_bytes()for p in (ROOT/'data').glob('*.json')if p.name!='refresh-status.json'};t=time.monotonic();state='completed';detail=''
  try:
   result=subprocess.run([sys.executable,str(ROOT/'scripts'/filename)],cwd=ROOT,capture_output=True,text=True,timeout=timeout,check=False,env={**os.environ,'PPW_REFRESH_STARTED_AT':started})
   if result.returncode:state='failed';detail=result.stdout[-600:]+result.stderr[-600:]
   validate_prices()
  except subprocess.TimeoutExpired:state='timeout';detail='Stage time limit reached; valid dated observations retained.'
  except Exception as exc:state='failed';detail=str(exc)
  if state!='completed':
   for p,b in backup.items():p.write_bytes(b)
  report['stages'].append(dict(name=filename,status=state,elapsed_seconds=round(time.monotonic()-t,1),detail=detail[-1200:]));save(path,report)
  print(filename,state,round(time.monotonic()-t,1),'seconds',flush=True)
 after=records();verified=[r for r in after.values()if r.get('last_checked_at','')>=started]
 report.update(completed_at=now(),source_checks=source_checks(started,{x['name']for x in report['stages']if x['status']=='completed'}),total_quotes=len(after),verified_quotes=len(verified),changed_prices=sum(r['id']in before and r['price']!=before[r['id']]['price']for r in verified),new_quotes=sum(r['id']not in before for r in verified),retained_quotes=len(after)-len(verified))
 report['status']='failed'if not verified else'partial'if any(x['status']!='completed'for x in report['stages'])or any(x['status']=='not_verified'for x in report['source_checks'])else'complete'
 # A refreshed public page can legitimately repeat an older official notification.
 # Only fetched/parsed observations receive verification timestamps; quote dates are untouched.
 save(path,report);print(json.dumps({k:v for k,v in report.items()if k not in ['stages','source_checks']}),flush=True)
 return report
if __name__=='__main__':run()
