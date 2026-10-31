"""Display source verification separately from source publication/observation dates."""
import datetime,json,pathlib,html
ROOT=pathlib.Path(__file__).resolve().parents[1]
TZ=datetime.timezone(datetime.timedelta(hours=5))
def load_report():
 p=ROOT/'data/refresh-status.json'
 return json.loads(p.read_text())if p.exists()else{}
def format_time(value):
 if not value:return 'Not verified yet'
 try:return datetime.datetime.fromisoformat(value.replace('Z','+00:00')).astimezone(TZ).strftime('%d %b %Y, %I:%M %p PKT')
 except (ValueError,TypeError):return 'Not verified yet'
def next_slot(now=None):
 now=(now or datetime.datetime.now(TZ)).astimezone(TZ)
 slots=[now.replace(hour=h,minute=30,second=0,microsecond=0)for h in [8,20]]
 return next((d for d in slots if d>now),slots[0]+datetime.timedelta(days=1)).isoformat()
def annotate(rows,report):
 for r in rows:
  if r.get('price')is None:r['verification_state']='unpriced'
  elif r.get('sheet'):r['verification_state']='manual'
  elif r.get('last_checked_at')and report.get('started_at')and r['last_checked_at']>=report['started_at']:r['verification_state']='checked'
  else:r['verification_state']='retained'
 return rows
def badge(r):
 e=lambda s:html.escape(str(s),quote=True)
 if r.get('verification_state')=='checked':return '<small class="verification checked">Source checked '+e(format_time(r.get('last_checked_at')))+'</small>'
 if r.get('verification_state')=='unpriced':return '<small class="verification">No verified price yet</small>'
 if r.get('verification_state')=='manual':return '<small class="verification retained">Dated notification · manual rate verification required</small>'
 return '<small class="verification retained">Not reverified in latest refresh'+(' · Last checked '+e(format_time(r['last_checked_at']))if r.get('last_checked_at')else'')+'</small>'
def group_badge(rows):
 priced=[r for r in rows if r.get('price')is not None]
 if not priced:return badge(rows[0])
 checked=[r for r in priced if r.get('verification_state')=='checked']
 if len(checked)==len(priced):return badge(max(checked,key=lambda r:r.get('last_checked_at','')))
 return '<small class="verification retained">'+str(len(checked))+'/'+str(len(priced))+' offers checked this refresh · earlier dated quotes retained</small>'
def banner(report):
 e=lambda s:html.escape(str(s),quote=True)
 label={'complete':'Refresh completed','partial':'Refresh completed · some sources unavailable','failed':'Refresh failed · earlier dated quotes retained','running':'Price refresh in progress'}.get(report.get('status'),'Awaiting verified price refresh')
 last=report.get('completed_at')or report.get('started_at')or''
 return '<aside class="refresh-banner" aria-label="Price update status"><strong>'+e(label)+'</strong><span>Last price check: <time datetime="'+e(last)+'">'+e(format_time(last))+'</time></span><span>Scheduled: 08:30 & 20:30 PKT</span><details><summary>Update details</summary><p>'+str(report.get('verified_quotes',0))+' quotes verified · '+str(report.get('changed_prices',0))+' prices changed · '+str(report.get('retained_quotes',0))+' earlier quotes retained.</p><p>Next scheduled check: '+e(format_time(next_slot()))+'. Start times can be delayed by the scheduler. Source dates stay unchanged when a source has not published a newer rate. Failed or unsupported sources keep their last dated quotes and are marked as unverified.</p></details></aside>'
