from pathlib import Path
import csv,json
ROOT=Path(r'C:\Programación\Grokking\runs')
hits=[]
for p in ROOT.rglob('metrics.csv'):
 try:
  with p.open(encoding='utf-8-sig',newline='') as f:
   rows=list(csv.DictReader(f))
  if len(rows)<10 or 'train_accuracy' not in rows[0]:continue
  key='clean_accuracy' if 'clean_accuracy' in rows[0] else 'test_accuracy'
  vals=[float(r[key]) for r in rows if r.get(key) not in ('',None)]
  tr=[float(r['train_accuracy']) for r in rows if r.get('train_accuracy') not in ('',None)]
  if len(vals)!=len(rows) or len(tr)!=len(rows):continue
  steps=[int(r['step']) for r in rows]
  early=vals[:max(2,len(vals)//4)]
  late=vals[-max(3,len(vals)//5):]
  hit={'rel':str(p.parent.relative_to(ROOT)),'n':len(rows),'step_final':steps[-1], 'train_final':round(tr[-1],3),'test_final':round(vals[-1],3),'test_peak':round(max(vals),3),'early_max':round(max(early),3),'late_mean':round(sum(late)/len(late),3),'late_min':round(min(late),3),'late_max':round(max(late),3)}
  hits.append(hit)
 except Exception as e:print('SKIP',p,str(e)[:80])
hits.sort(key=lambda r:abs(r['late_mean']-.6))
print('TOTAL',len(hits))
for h in hits[:45]: print(json.dumps(h,ensure_ascii=False))
Path(__file__).with_name('candidate_scan.json').write_text(json.dumps(hits,ensure_ascii=False,indent=2),encoding='utf-8')
