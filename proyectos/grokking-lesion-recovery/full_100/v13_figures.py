"""Draw three inspectable vector figures from frozen V13_ANALYSIS.json.
No GUI or plotting dependencies; figures are generated exclusively from data.
"""
from pathlib import Path
import json,math
ROOT=Path(__file__).resolve().parent
data=json.loads((ROOT/"V13_ANALYSIS.json").read_text(encoding="utf-8"))
rows=data["dose_summary"]
assert len(rows)==9
COLORS=("#262626","#8994a4")
def svgplot(name,title,measure_a,measure_b,ymax,ylabel,format_y="{:.0f}",ymin=0.,legend_a="Grokking tardío",legend_b="Aprendizaje rápido"):
 W,H=950,465; L,R,T,B=90,30,62,100
 cx=lambda i:L+i*((W-L-R)/(len(rows)-1))
 cy=lambda y:T+(ymax-y)/(ymax-ymin)*(H-T-B)
 s=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
    '<rect width="100%" height="100%" fill="#fff"/>',
    f'<text x="44" y="32" font-family="Arial" font-size="19" font-weight="600" fill="#181818">{title}</text>']
 for i in range(6):
  v=ymin+(ymax-ymin)*i/5
  py=cy(v)
  s.append(f'<line x1="{L}" y1="{py:.1f}" x2="{W-R}" y2="{py:.1f}" stroke="#dedede" stroke-width="1" stroke-dasharray="4 5"/>')
  s.append(f'<text x="{L-12}" y="{py+4:.1f}" font-family="Arial" font-size="12" fill="#525252" text-anchor="end">{format_y.format(v)}</text>')
 for i,row in enumerate(rows):
  x=cx(i)
  s.append(f'<text x="{x:.1f}" y="{H-B+25}" font-family="Arial" font-size="12" fill="#333" text-anchor="middle">{round(row["percent"])}%</text>')
 for key,colour in ((measure_a,COLORS[0]),(measure_b,COLORS[1])):
  vs=[min(ymax,max(ymin,float(r[key]))) for r in rows]
  pts=" ".join(f"{cx(i):.1f},{cy(v):.1f}" for i,v in enumerate(vs))
  s.append(f'<polyline points="{pts}" fill="none" stroke="{colour}" stroke-width="3"/>')
  for i,v in enumerate(vs):s.append(f'<circle cx="{cx(i):.1f}" cy="{cy(v):.1f}" r="4.7" fill="{colour}"/>')
 for x,y,c,label in ((L+8,H-46,COLORS[0],legend_a),(L+250,H-46,COLORS[1],legend_b)):
  s.append(f'<line x1="{x}" y1="{y}" x2="{x+34}" y2="{y}" stroke="{c}" stroke-width="3"/>')
  s.append(f'<text x="{x+43}" y="{y+4}" font-family="Arial" font-size="13" fill="#333">{label}</text>')
 s.append(f'<text x="{W/2}" y="{H-62}" text-anchor="middle" font-family="Arial" font-size="13" fill="#555">Porcentaje de neuronas ocultas desactivadas permanentemente</text>')
 s.append(f'<text x="18" y="{H/2}" transform="rotate(-90 18 {H/2})" text-anchor="middle" font-family="Arial" font-size="13" fill="#555">{ylabel}</text>')
 s.append('<text x="90" y="448" font-family="Arial" font-size="11.5" fill="#666">Medias de 5 pares de redes; 4 mascaras por red y dosis. Las mascaras NO son replicaciones independientes.</text>')
 s.append("</svg>")
 (ROOT/name).write_text("\n".join(s),encoding="utf-8")

svgplot("FIG_V13_DAMAGE.svg","V13 | Daño funcional inmediato según porcentaje eliminado",
 "initial_damage_A_pp","initial_damage_B_pp",70,
 "Pérdida media de precisión (puntos porcentuales)")
svgplot("FIG_V13_AUC.svg","V13 | Déficit acumulado durante 500 pasos de recuperación",
 "mean_auc_A","mean_auc_B",270,
 "AUC del déficit frente al control (menor = mejor)")
for row in rows:
 a=row["A_masks_damaged_gt2pp"];b=row["B_masks_damaged_gt2pp"]
 row["frac_recovery_A"]=row["A_masks_recovered_given_damage"]/a if a else 1.
 row["frac_recovery_B"]=row["B_masks_recovered_given_damage"]/b if b else 1.
svgplot("FIG_V13_RECOVERY.svg","V13 | Lesiones recuperadas en un máximo de 500 pasos",
 "frac_recovery_A","frac_recovery_B",1.0,
 "Proporción de lesiones con recuperación observada",format_y="{:.1f}")
print("FIG_V13_DONE",len(rows),flush=True)
