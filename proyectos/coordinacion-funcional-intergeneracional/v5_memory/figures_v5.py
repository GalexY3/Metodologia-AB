"""Render inspectable SVG trajectories from frozen V5 test results."""
import json,html
from pathlib import Path
R=Path(__file__).resolve().parent
H=R/"holdout"
W,Ht=1060,545
left,right,top,bottom=85,40,75,138
palette={
 "W1H64":"#A67839","W1H128":"#7654A1",
 "W8H64":"#2C76AA","W8H128":"#218268",
 "IID random":"#7B8491"}
names={
 "W1H64":("W1_H64_trained","sample"),
 "W1H128":("W1_H128_trained","sample"),
 "W8H64":("W8_H64_trained","sample"),
 "W8H128":("W8_H128_trained","sample"),
 "IID random":("baseline","random_always")}
x=lambda t:left+(W-left-right)*t/100
y=lambda v:top+(Ht-top-bottom)*(0.85-v)/0.85
for k in (2,3,4):
 svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{Ht}" viewBox="0 0 {W} {Ht}">',
      '<rect width="100%" height="100%" fill="#fff"/>',
      f'<text x="30" y="30" font-family="Arial" font-size="23" font-weight="bold" fill="#223649">Diez estados posibles: organizarse en {k} grupos iguales</text>',
      '<text x="32" y="52" font-family="Arial" font-size="14" fill="#6B7782">Distancia D al equilibrio, media de 100 sociedades con pesos congelados; menor es mejor</text>']
 for j in range(5):
  v=.2*j
  yy=y(v)
  svg.extend([
    f'<line x1="{left}" x2="{W-right}" y1="{yy:.1f}" y2="{yy:.1f}" stroke="#E6EBF0" stroke-width="1"/>',
    f'<text x="{left-10}" y="{yy+5:.1f}" font-family="Arial" font-size="13" fill="#5D6975" text-anchor="end">{v:.1f}</text>'])
 for t in range(0,101,20):
  svg.append(f'<text x="{x(t):.1f}" y="{Ht-bottom+24}" font-family="Arial" font-size="12" text-anchor="middle" fill="#5D6975">{t}</text>')
 for i,(label,(variant,kind)) in enumerate(names.items()):
  fn=R/"holdout"/f"k{k}_{variant}_{kind}.json"
  v=json.loads(fn.read_text(encoding="utf-8"))
  points=" ".join(f"{x(t):.2f},{y(d):.2f}" for t,d in enumerate(v["D_curve"]))
  color=palette[label]
  dash='5,5' if label=="IID random" else 'none'
  svg.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round" stroke-dasharray="{dash}"/>')
  xx=left+(i%2)*460;yy=Ht-92+(i//2)*29
  svg.append(f'<line x1="{xx}" x2="{xx+36}" y1="{yy}" y2="{yy}" stroke="{color}" stroke-width="3" stroke-dasharray="{dash}"/>')
  svg.append(f'<text x="{xx+44}" y="{yy+5}" font-family="Arial" font-size="14" fill="#43525E">{html.escape(label)}</text>')
 svg.append(f'<text x="{(W+left-right)/2}" y="{Ht-bottom+50}" font-family="Arial" text-anchor="middle" font-size="14" fill="#536373">Turno de simulación</text>')
 svg.append('</svg>')
 out=R/f"FIG_V5_k{k}.svg"
 out.write_text("\n".join(svg),encoding="utf-8")
 print("CHART_DONE",out.name,flush=True)
