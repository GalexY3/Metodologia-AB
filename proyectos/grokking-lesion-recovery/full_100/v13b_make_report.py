"""Create V13B figure and report from audited 40 long-horizon lesion curves."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
d=json.loads((ROOT/"V13B_ANALYSIS.json").read_text(encoding="utf-8"))
assert d["audit"]["status"]=="PASS"
a=d["aggregate"]
horizons=[500,1000,1500,2000]
A=[a["A_recovered_at_horizons"][str(h)] for h in horizons]
B=[a["B_recovered_at_horizons"][str(h)] for h in horizons]
w,h=880,425
x=lambda i:100+i*225
y=lambda v:335-v/20*245
s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
 '<rect width="100%" height="100%" fill="white"/>',
 '<text x="45" y="34" font-family="Arial" font-size="19" font-weight="bold" fill="#222">V13B — Supervivencia funcional tras perder el 90% de neuronas</text>']
for val in (0,5,10,15,20):
 py=y(val)
 s.append(f'<line x1="92" x2="805" y1="{py:.1f}" y2="{py:.1f}" stroke="#ddd" stroke-dasharray="4 4"/>')
 s.append(f'<text x="80" y="{py+4:.1f}" fill="#555" text-anchor="end" font-family="Arial" font-size="12">{val}</text>')
for i,hor in enumerate(horizons):
 s.append(f'<text x="{x(i):.1f}" y="360" text-anchor="middle" font-size="13" font-family="Arial" fill="#333">{hor} pasos</text>')
for numbers,col in ((A,"#282828"),(B,"#8b97a7")):
 pts=" ".join(f"{x(i):.1f},{y(v):.1f}" for i,v in enumerate(numbers))
 s.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="3"/>')
 for i,v in enumerate(numbers):
  s.append(f'<circle cx="{x(i):.1f}" cy="{y(v):.1f}" r="5" fill="{col}"/>')
  s.append(f'<text x="{x(i):.1f}" y="{y(v)-11:.1f}" text-anchor="middle" font-family="Arial" font-size="12" fill="{col}">{v}/20</text>')
s += ['<line x1="470" y1="64" x2="505" y2="64" stroke="#282828" stroke-width="3"/>',
 '<text x="513" y="68" font-family="Arial" font-size="12" fill="#333">Grokking tardío</text>',
 '<line x1="650" y1="64" x2="685" y2="64" stroke="#8b97a7" stroke-width="3"/>',
 '<text x="693" y="68" font-family="Arial" font-size="12" fill="#333">Aprendizaje rápido</text>',
 '<text x="440" y="405" font-family="Arial" font-size="12" text-anchor="middle" fill="#555">Número de lesiones que recuperan ≥99% en dos observaciones consecutivas</text>',
 '</svg>']
(ROOT/"FIG_V13B_LONG.svg").write_text("\n".join(s),encoding="utf-8")
formatnum=lambda v:f"{v:.2f}".replace(".",",")
report=[
"# V13B — ¿Basta con entrenar más para recuperarse de una lesión del 90%?",
"",
"**Equipo:** GALEXY_TRAVEL. **Fecha:** 9 de noviembre de 2026. **Estudio exploratorio definido después de observar V13**, utilizando máscaras nuevas 4201..4204 y horizonte de 2.000 actualizaciones, en lugar de reutilizar las máscaras del barrido original. **No es un ensayo confirmatorio independiente** de V13.",
"",
"## Diseño",
"",
"Cinco parejas de redes idénticas en arquitectura y datos iniciales, con 300 neuronas ocultas, 100% validación antes del daño y L1 final común 0,0001. Se destruyen permanentemente 270 de 300 unidades (90%) con las mismas cuatro máscaras para cada pareja. Total 40 reconstrucciones y controles intactos bajo AdamW LR 0,001, CE+L1=0,0001, hasta 2.000 pasos, medidas cada25. El test no se consulta. Protocolo [PREREG_V13B_LONG_RECOVERY.md](PREREG_V13B_LONG_RECOVERY.md).",
"",
"## Resultado principal",
"",
"![Evolución de recuperaciones observadas tras destrucción del 90%](FIG_V13B_LONG.svg)",
"",
"| Horizonte | A: grokking tardío | B: aprendizaje rápido |",
"|---|---:|---:|",
]
for hor,av,bv in zip(horizons,A,B):
 report.append(f"| {hor} pasos | {av}/20 | {bv}/20 |")
report += [
"",
f"La pérdida inmediata media de validación fue A={formatnum(a['A_initial_damage_mean_pp'])} puntos porcentuales y B={formatnum(a['B_initial_damage_mean_pp'])}. Tras 2.000 actualizaciones, únicamente 3/20 A y 4/20 B alcanzaron dos veces consecutivas el umbral de 99% de validación. La mayoría de las lesiones graves no se recuperó dentro de este horizonte. En cuatro de las cinco semillas hubo al menos una diferencia A/B de AUC, pero no hay una ventaja de signo estable: dos pares favorecen A y tres B.",
"",
f"El déficit acumulado de validación entre 0 y 2.000 pasos (AUC, menor mejor) fue A={formatnum(a['A_auc_2000_mean'])} y B={formatnum(a['B_auc_2000_mean'])}. Diferencia media pareada A−B={formatnum(a['paired_auc_2000_diff']['mean'])}; p bilateral exacta exploratoria por inversión de signos={str(a['exact_p_two_sided_exploratory']).replace('.',',')}. AUC mezcla daño inicial y duración de déficit; no identifica velocidad pura de reparación.",
"",
"**Con más tiempo sí aparecieron algunas recuperaciones adicionales**, de manera que la falta de recuperación a 500 pasos no equivale a imposibilidad definitiva. No obstante, entre 1.000 y 2.000 pasos no se añadieron recuperaciones en estas cuarenta trayectorias. Tampoco se puede deducir un umbral estructural universal de muerte de redes: otros optimizadores, tareas, arquitecturas, inicializaciones o horizontes podrían modificarlo.",
"",
"## Interpretación y controles",
"",
"Esta es una prueba de **recuperabilidad funcional restringida**, no regeneración física. Las neuronas destruidas mantienen una máscara cero y las supervivientes deben reorganizarse para resolver la paridad. Incluso conservar 30 neuronas, suficiente en principio para representar una función de paridad sencilla, no garantiza llegar a una solución mediante el procedimiento de optimización estipulado.",
"",
"El diseño conserva el confusor del L1 histórico y solo tiene cinco pares independientes de modelos; las cuatro máscaras por red están anidadas. Las 40 curvas no son cuarenta repeticiones independientes del fenómeno de aprendizaje. La prueba es post hoc frente a V13 y debe informarse como sensibilidad, no como descubrimiento preregistrado anterior.",
"",
"## Reproducción",
"",
"Datos por máscara y curvas CSV en v13b_long_runs; scripts v13b_long_recovery.py, v13b_analyze.py, v13b_make_report.py. [V13B_ANALYSIS.json](V13B_ANALYSIS.json) conserva la auditoría local PASS (40 trayectorias, máscaras emparejadas, 270 índices distintos por lesión, controles y AUC coherentes). El estudio amplio de dosis se presenta en [REPORT_V13.md](REPORT_V13.md).",
]
(ROOT/"REPORT_V13B.md").write_text("\n".join(report)+"\n",encoding="utf-8")
print("V13B_REPORT_DONE",len(report),flush=True)
