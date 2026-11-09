"""Audited G0 intergenerational report, paired counterfactual metrics and figures."""
from pathlib import Path
import json,statistics
ROOT=Path(__file__).resolve().parent
d=json.loads((ROOT/"results_g0"/"G0_RESULTS.json").read_text(encoding="utf-8"))
rows=d["raw"];groups=d["groups"];excluded=d["ineligible"]
assert d["n_base_attempted"]==40 and d["n_base_eligible"]==37
assert len(rows)==37*3*3 and len(excluded)==3
index={}
for row in rows:
 key=(row["k"],row["seed"],row["fraction_replaced"])
 index.setdefault(key,[]).append(row)
bad=[]
paired=[]
for key,items in index.items():
 if len(items)!=3 or {v["treatment"] for v in items}!={"inherited","no_teaching","contact_teaching"}:
  bad.append("Missing treatment "+str(key));continue
 if len({v["initial_colors_sha256"] for v in items})!=1:bad.append("Shock colors differ "+str(key))
 if len({v["replacement_nodes_sha256"] for v in items})!=1:bad.append("Replacement selection differs "+str(key))
 if len({v["initial_tv"] for v in items})!=1:bad.append("Shock imbalance differs "+str(key))
 a={v["treatment"]:v for v in items}
 frac=key[2]
 if a["no_teaching"]["transmission_count"]!=0 or a["inherited"]["transmission_count"]!=0:
  bad.append("unexpected contact teaching "+str(key))
 if abs(a["inherited"]["frac_rule_after"]-1)>1e-12:bad.append("heritage not retained "+str(key))
 if abs(a["no_teaching"]["frac_rule_after"]-(1-frac))>1e-12:bad.append("no teaching share wrong "+str(key))
 if a["contact_teaching"]["frac_rule_after"]<a["contact_teaching"]["frac_rule_before"]:
  bad.append("de-learning "+str(key))
 paired.append({"k":key[0],"seed":key[1],"fraction":frac,
  "same_postshock_TV":items[0]["initial_tv"],
  "AUC_no_teaching_minus_contact":a["no_teaching"]["auc_tv_150"]-a["contact_teaching"]["auc_tv_150"],
  "AUC_no_teaching_minus_inherited":a["no_teaching"]["auc_tv_150"]-a["inherited"]["auc_tv_150"],
  "AUC_contact_minus_inherited":a["contact_teaching"]["auc_tv_150"]-a["inherited"]["auc_tv_150"],
  "recovered_inherited":a["inherited"]["recovered_by_150"],
  "recovered_no_teaching":a["no_teaching"]["recovered_by_150"],
  "recovered_contact":a["contact_teaching"]["recovered_by_150"]})
out={"status":"PASS" if not bad else "FAIL","errors":bad,"n_raw":len(rows),
     "n_independent_pre_shock_communities":37,
     "n_community_fractions":len(index),
     "note":"Each shock repeated under exactly three treatment regimes; one conversation per agent/tick",
     "pairs":paired}
(ROOT/"RESULTS_G0_AUDIT.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
assert not bad
COLORS={"inherited":"#242424","no_teaching":"#b5b5b5","contact_teaching":"#627083"}
for k in (4,5):
 values=[next(v for v in groups if v["k"]==k and v["fraction"]==fraction
             and v["treatment"]==treat)
         for fraction in (.25,.5,.75) for treat in ("inherited","no_teaching","contact_teaching")]
 W,H=880,430;L,R,T,B=75,30,70,95
 graph=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
 '<rect width="100%" height="100%" fill="#fff"/>',
 f'<text x="35" y="34" font-family="Arial" font-size="19" fill="#222" font-weight="600">Recuperación intergeneracional, k={k}</text>']
 ymax=20
 y=lambda v:H-B-v/ymax*(H-T-B)
 for tick in (0,5,10,15,20):
  py=y(tick)
  graph.append(f'<line x1="{L}" y1="{py:.1f}" x2="{W-R}" y2="{py:.1f}" stroke="#ddd" stroke-dasharray="4 4"/>')
  graph.append(f'<text x="{L-9}" y="{py+4:.1f}" text-anchor="end" font-size="12" font-family="Arial" fill="#555">{tick}</text>')
 for i,frac in enumerate((.25,.5,.75)):
  x=110+i*244
  for j,treat in enumerate(("inherited","no_teaching","contact_teaching")):
   z=next(q for q in values if q["fraction"]==frac and q["treatment"]==treat)
   n=z["recovered"];px=x+42*j
   graph.append(f'<rect x="{px}" y="{y(n):.1f}" width="34" height="{H-B-y(n):.1f}" fill="{COLORS[treat]}"/>')
   graph.append(f'<text x="{px+17}" y="{y(n)-7:.1f}" text-anchor="middle" font-family="Arial" font-size="12" fill="#333">{n}/{z["n_eligible_pre"]}</text>')
  graph.append(f'<text x="{x+59}" y="{H-B+27}" text-anchor="middle" font-family="Arial" font-size="14" fill="#333">{int(frac*100)}% reemplazo</text>')
 for j,(label,key) in enumerate((("Herencia","inherited"),("Sin enseñanza","no_teaching"),("Transmisión por contacto","contact_teaching"))):
  x=75+j*262
  graph.append(f'<rect x="{x}" y="380" width="16" height="11" fill="{COLORS[key]}"/>')
  graph.append(f'<text x="{x+24}" y="390" font-family="Arial" font-size="12" fill="#333">{label}</text>')
 graph.append('<text x="442" y="420" text-anchor="middle" font-family="Arial" font-size="11.5" fill="#555">Casos que recuperan equilibrio sostenido antes de 150 ticks, sujetos a estabilidad previa</text>')
 graph.append("</svg>")
 (ROOT/f"FIG_G0_TURNOVER_K{k}.svg").write_text("\n".join(graph),encoding="utf-8")

def fmt(v,d=2):return f"{v:.{d}f}".replace(".",",")
report=[
"# G0 — Traspaso intergeneracional de una regla de coordinación distribuida",
"",
"**Fecha:** 9 de noviembre de 2026. **Equipo:** DESKTOP-I4SULKD. **Estatus:** experimento de simulación controlada, con mecanismo explícito de transmisión cultural local. **No** demuestra aprendizaje autónomo de la regla ni grokking colectivo. El diseño quedó fijado en PROTOCOL_TURNOVER_V0.md antes de los ensayos G0.",
"",
"## Pregunta",
"",
"Cuando una comunidad ya logró mantenerse equilibrada entre k funciones, ¿puede reconstruir su organización tras reemplazar a parte de sus miembros? ¿Qué papel desempeña conservar la regla local de coordinación frente a transmitirla por comunicación o perderla completamente?",
"",
"Los 120 agentes se conectan en un anillo de grado4 y pueden conversar con un solo vecino por turno. Una regla preprogramada de elección de función poco observada produce coordinación sin que ninguno conozca el censo global. Se crean episodios base de 140 pasos con k=4 y k=5, y solo se realiza relevo si el último periodo de 10 ticks cumple TV≤0,06 y cambios≤5%. **No se retiran a posteriori las comunidades que recuperen mal**.",
"",
f"Se intentaron **{d['n_base_attempted']}** comunidades iniciales y **{d['n_base_eligible']}** cumplieron equilibrio: 20/20 para k4 y 17/20 para k5. Los tres casos k5 que no llegaron a estabilidad antes del relevo están conservados como exclusiones previas. Se evaluaron tres fracciones de reemplazo r∈{{0,25;0,5;0,75}}. En cada comunidad/fracción, exactamente los mismos nodos y nuevos colores (un shock 70% a función0 entre recién llegados) se aplicaron a los tres tratamientos contrafactuales.",
"",
"Los tratamientos difieren únicamente en la disponibilidad de una regla diseñada manualmente: **Herencia** hace que todos los nuevos posean inmediatamente la regla; **Sin enseñanza** mantiene novatos que no la conocen y solo conservan su rol; **Enseñanza por contacto** comienza con novatos sin regla pero permite que adopten la de un vecino informado con probabilidad fijada de 0,25 en cada conversación. Quien acaba de recibir la regla solo puede utilizarla a partir del siguiente tick. No existe difusión global instantánea ni conocimiento de los porcentajes del conjunto. El horizonte posterior es de 150 ticks.",
"",
"## Resultados con cuatro funciones",
"",
"![Recuperación tras sustitución con k4](FIG_G0_TURNOVER_K4.svg)",
"",
"| Reemplazo | Herencia | Sin enseñanza | Enseñanza local |",
"|---|---:|---:|---:|"]
for frac in (.25,.5,.75):
 z=[next(v for v in groups if v["k"]==4 and v["fraction"]==frac and v["treatment"]==t) for t in ("inherited","no_teaching","contact_teaching")]
 report.append(f"| {int(frac*100)}% | {z[0]['recovered']}/{z[0]['n_eligible_pre']} | {z[1]['recovered']}/{z[1]['n_eligible_pre']} | {z[2]['recovered']}/{z[2]['n_eligible_pre']} |")
report+=["",
"Con el 25% de sustitución, los veteranos que conservaron la regla fueron suficientes para restaurar el equilibrio en 19/20 comunidades incluso sin enseñar a los recién llegados. Con reemplazo del 50% o 75%, la ausencia total de enseñanza produjo **0/20 recuperaciones**, mientras que la transmisión por conversación produjo **20/20**. Esta diferencia se obtiene desde shocks demográficos estrictamente idénticos dentro de cada comunidad.",
"",
"## Resultados con cinco funciones, una tarea más exigente",
"",
"![Recuperación tras sustitución con k5](FIG_G0_TURNOVER_K5.svg)",
"",
"| Reemplazo | Herencia | Sin enseñanza | Enseñanza local |",
"|---|---:|---:|---:|"]
for frac in (.25,.5,.75):
 z=[next(v for v in groups if v["k"]==5 and v["fraction"]==frac and v["treatment"]==t) for t in ("inherited","no_teaching","contact_teaching")]
 report.append(f"| {int(frac*100)}% | {z[0]['recovered']}/{z[0]['n_eligible_pre']} | {z[1]['recovered']}/{z[1]['n_eligible_pre']} | {z[2]['recovered']}/{z[2]['n_eligible_pre']} |")
report+=["",
"Con k5, la coordinación posterior resulta menos fiable. A reemplazo del 50%, la enseñanza por contacto recuperó **11/17** frente a **0/17** sin enseñanza; al 75%, **5/17** frente a **0/17**. La herencia inmediata de la regla recuperó **17/17** en ambas fracciones, lo que indica que la tarea no era imposible tras ese choque: el mecanismo de conservación o transmisión de conocimiento marcaba la diferencia dentro del simulador.",
"",
"## Magnitud y duración del desajuste",
"",
"Los contrastes no se basan solamente en una fotografía del último tick. Se calculó también la AUC de TV acumulada durante los 150 ticks posteriores. Una AUC menor indica menos desequilibrio temporal. Estos promedios están condicionados a que la comunidad anterior fuera elegible, y la unidad independiente es la cohorte inicial, no los mensajes ni los ticks.",
"",
"| k | Reemplazo | AUC herencia | AUC sin enseñanza | AUC contacto |",
"|---|---:|---:|---:|---:|"]
for k in (4,5):
 for frac in (.25,.5,.75):
  z=[next(v for v in groups if v["k"]==k and v["fraction"]==frac and v["treatment"]==t) for t in ("inherited","no_teaching","contact_teaching")]
  report.append(f"| {k} | {int(frac*100)}% | {fmt(z[0]['mean_auc_tv'])} | {fmt(z[1]['mean_auc_tv'])} | {fmt(z[2]['mean_auc_tv'])} |")
report += [
"",
"## Interpretación sociológica y límites",
"",
"[Inferencia] Este modelo demuestra una forma sencilla de **dependencia de portadores de conocimiento distribuido**. El equilibrio macroscópico puede existir antes del relevo y perderse cuando desaparece la capacidad de corregir desviaciones locales; la supervivencia de otros agentes y de la red física no basta para conservar esa competencia. La posibilidad de enseñar mediante interacción uno-a-uno actúa como un mecanismo de redundancia y reproducción de reglas.",
"",
"**La regla fue proporcionada por el investigador y se copia con un parámetro de transmisión definido externamente**. Por ello el resultado no demuestra que el conocimiento haya emergido espontáneamente, ni que exista enseñanza social humana análoga. El efecto del tratamiento dentro del simulador sí se identifica causalmente porque se interviene sobre la transferencia de conocimiento preservando colores, nodos, red y choque inicial. Su relevancia para comunidades reales es una hipótesis teórica, no una inferencia empírica.",
"",
"Una sustitución del 50–75% coloca a los recién llegados en un estado funcional inicial sesgado (70% en el rol0) y les impide corregir desequilibrios si no conocen la regla. La intervención de «sin enseñanza» está diseñada para que puedan permanecer inertes; por ello el fracaso no es sorprendente en sentido teórico general. La comparación permite estimar la importancia del acceso a esa regla en este modelo, pero no descubrir una ley universal de fragilidad generacional.",
"",
"El test P0/P1 independiente encontró que una política REINFORCE basada en escalado de escasez local consigue cierta extrapolación a k5..8, pero G0 prueba la difusión de una **heurística explícita**. No debe combinarse su tasa de recuperación con una tasa de traspaso de conocimientos aprendidos por agentes; esa sería una nueva simulación G1 con control específico.",
"",
"## Auditoría, código y registros",
"",
f"El análisis de pares [RESULTS_G0_AUDIT.json](RESULTS_G0_AUDIT.json) informa **{out['status']}** en **{out['n_raw']} ramas postrelevo** y {out['n_community_fractions']} shocks emparejados, sin discrepancias de colores iniciales ni nodos reemplazados entre las tres condiciones. Los scripts [turnover_v0.py](turnover_v0.py), [report_turnover.py](report_turnover.py) y el archivo [results_g0/G0_RESULTS.json](results_g0/G0_RESULTS.json) contienen parámetros y resultados. La limitación de un vecino por tick se implementa en el mismo modelo base que pasó diez pruebas automáticas.",
]
(ROOT/"REPORT_G0.md").write_text("\n".join(report)+"\n",encoding="utf-8")
print("G0_REPORT",len(report),"lines",out["status"],flush=True)
