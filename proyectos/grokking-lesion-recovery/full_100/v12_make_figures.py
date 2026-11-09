"""Pure-Python SVG figures from frozen V12 JSON; no plotting dependencies."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
v=json.loads((ROOT/"V12_ROBUSTNESS.json").read_text(encoding="utf-8"))
b=json.loads((ROOT/"V12B_ANALYSIS.json").read_text(encoding="utf-8"))
seeds=v["eligible_seeds"]
rob={z["seed"]:z for z in v["paired_changes"]}
rec={z["seed"]:z for z in b["per_seed"]}

def make_chart(name,title,data_a,data_b,label_a,label_b,ymin,ymax,ylabel):
 w,h=880,420
 xmin,xmax=90,840;ytop,ybottom=70,330
 xfor=lambda i:xmin+((xmax-xmin)/len(seeds))*(i+.5)
 yfor=lambda x:ybottom-(x-ymin)/(ymax-ymin)*(ybottom-ytop)
 els=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
    '<rect width="100%" height="100%" fill="white"/>',
    f'<text x="60" y="35" font-family="Arial" font-size="18" font-weight="bold" fill="#202020">{title}</text>']
 for i in range(6):
  val=ymin+(ymax-ymin)*i/5
  y=yfor(val)
  els.append(f'<line x1="{xmin}" y1="{y:.1f}" x2="{xmax}" y2="{y:.1f}" stroke="#dfdfdf" stroke-dasharray="3,4"/>')
  els.append(f'<text x="78" y="{y+4:.1f}" text-anchor="end" font-family="Arial" font-size="12" fill="#444">{val:.1f}</text>')
 if ymin<0<ymax:
  y=yfor(0)
  els.append(f'<line x1="{xmin}" y1="{y:.1f}" x2="{xmax}" y2="{y:.1f}" stroke="#888" stroke-width="1.6"/>')
 for i,seed in enumerate(seeds):
  x=xfor(i)
  for val,offset,color in ((data_a[i],-30,"#343434"),(data_b[i],5,"#999999")):
   baseline=yfor(0) if ymin<0 else ybottom
   y=yfor(val)
   top=min(y,baseline);height=abs(y-baseline)
   els.append(f'<rect x="{x+offset:.1f}" y="{top:.1f}" width="25" height="{height:.1f}" fill="{color}"/>')
   label_y=top-6 if val>=0 else max(y,baseline)+14
   els.append(f'<text x="{x+offset+12.5:.1f}" y="{label_y:.1f}" text-anchor="middle" font-family="Arial" font-size="10" fill="#333">{val:.1f}</text>')
  els.append(f'<text x="{x:.1f}" y="{ybottom+22}" text-anchor="middle" font-family="Arial" font-size="13" fill="#333">Semilla {seed}</text>')
 els.append('<rect x="440" y="46" width="16" height="12" fill="#343434"/>')
 els.append(f'<text x="463" y="57" font-family="Arial" font-size="12" fill="#333">{label_a}</text>')
 els.append('<rect x="650" y="46" width="16" height="12" fill="#999999"/>')
 els.append(f'<text x="673" y="57" font-family="Arial" font-size="12" fill="#333">{label_b}</text>')
 els.append(f'<text x="{w//2}" y="395" font-family="Arial" font-size="12" fill="#555" text-anchor="middle">{ylabel}</text>')
 els.append('</svg>')
 (ROOT/name).write_text("\n".join(els),encoding="utf-8")

make_chart("FIG_V12_ROBUSTNESS.svg",
 "Diferencia de vulnerabilidad tras ablacion (A menos B)",
 [rob[s]["before_difference"] for s in seeds],
 [rob[s]["after_difference"] for s in seeds],
 "Antes de L1 comun","Despues de L1 comun",-30,15,"Puntos porcentuales; mas cerca de cero = menor diferencia")
make_chart("FIG_V12B_RECOVERY.svg",
 "Deficit acumulado de recuperacion por red (AUC)",
 [rec[s]["auc_A"] for s in seeds],[rec[s]["auc_B"] for s in seeds],
 "A: grokking tardio","B: aprendizaje rapido",0,110,"Menor AUC = menos deficit acumulado durante 500 actualizaciones")
print("FIGURES_CREATED",len(seeds))
