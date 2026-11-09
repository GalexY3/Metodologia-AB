"""V15 analysis report + vector chart from the audited result JSON.
Reports the optimizer intervention within the same initial weights and lesion.
"""
from pathlib import Path
import json,math
ROOT=Path(__file__).resolve().parent
d=json.loads((ROOT/"V15_ANALYSIS.json").read_text(encoding="utf-8"))
assert d["audit"]["status"]=="PASS"
rows=d["by_dose"]
assert len(rows)==3
fmt=lambda x,dec=1:f"{x:.{dec}f}".replace(".",",")
# 4 series: A fresh/resumed, B fresh/resumed.
series=[
 ("Grokking tardío / nuevo","mean_auc_A_fresh","#252525",""),
 ("Grokking tardío / conservado","mean_auc_A_resumed","#252525","7 5"),
 ("Aprendizaje rápido / nuevo","mean_auc_B_fresh","#8b97a7",""),
 ("Aprendizaje rápido / conservado","mean_auc_B_resumed","#8b97a7","7 5"),
]
W,H=920,445
L,R,T,B=90,38,85,95
x=lambda i:L+i*(W-L-R)/2
maxv=max(r[key] for r in rows for _,key,_,_ in series)
topv=math.ceil(maxv/20)*20+10
y=lambda v:H-B-v/topv*(H-T-B)
parts=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
 '<rect width="100%" height="100%" fill="#fff"/>',
 '<text x="36" y="30" font-family="Arial" font-size="19" fill="#202020" font-weight="600">V15 — Reconstrucción con y sin estado previo de AdamW</text>']
for i in range(6):
 val=i*topv/5
 py=y(val)
 parts.append(f'<line x1="{L}" y1="{py:.1f}" x2="{W-R}" y2="{py:.1f}" stroke="#dddddd" stroke-dasharray="3 4"/>')
 parts.append(f'<text x="{L-10}" y="{py+4:.1f}" font-family="Arial" font-size="12" text-anchor="end" fill="#555">{round(val)}</text>')
for i,r in enumerate(rows):
 parts.append(f'<text x="{x(i)}" y="{H-B+23}" font-family="Arial" font-size="12" text-anchor="middle" fill="#333">{int(r["percent"])}% destruido</text>')
for label,key,color,dash in series:
 points=" ".join(f"{x(i):.1f},{y(r[key]):.1f}" for i,r in enumerate(rows))
 parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3" stroke-dasharray="{dash if dash else "none"}"/>')
 for i,r in enumerate(rows):
  parts.append(f'<circle cx="{x(i):.1f}" cy="{y(r[key]):.1f}" r="4" fill="{color}"/>')
for i,(label,key,color,dash) in enumerate(series):
 yy=50+(i//2)*20
 xx=90+(i%2)*350
 parts.append(f'<line x1="{xx}" y1="{yy}" x2="{xx+35}" y2="{yy}" stroke="{color}" stroke-width="3" stroke-dasharray="{dash if dash else "none"}"/>')
 parts.append(f'<text x="{xx+43}" y="{yy+4}" font-family="Arial" font-size="12" fill="#333">{label}</text>')
parts.append('<text x="460" y="426" text-anchor="middle" font-family="Arial" font-size="12" fill="#555">AUC del déficit en 500 pasos, menor = mejor. 5 pares independientes; 4 mascaras por red y dosis.</text>')
parts.append('</svg>')
(ROOT/"FIG_V15_OPTIMIZER_REPAIR.svg").write_text("\n".join(parts),encoding="utf-8")

report=[
"# V15 — Efecto del estado de AdamW sobre la recuperación tras la misma lesión",
"",
"**Equipo:** GALEXY_TRAVEL. **Fecha:** 9 de noviembre de 2026. **Estado:** experimento computacional exploratorio, con protocolo fijado antes de reconstruir y lesionar. El efecto de conservar o reiniciar AdamW está intervenido **dentro de un mismo modelo**; no se ha intervenido causalmente en la entidad abstracta grokking.",
"",
"## Pregunta y criterio de causalidad computacional",
"",
"¿Si un modelo ya resuelve el 100% de los ejemplos evaluados y sufre exactamente la misma ablación permanente, cambia la recuperación por conservar el estado adaptativo de su optimizador en lugar de inicializarlo desde cero? Esto separa un componente del **mecanismo de aprendizaje** de la competencia y pesos neuronales, que permanecen idénticos al inicio de cada par.",
"",
"Se reconstruyeron los diez checkpoints finales de V12 desde step6000 hasta step10000 con L1 común 0,0001, conservando ahora los momentos AdamW. **Los diez coincidieron exactamente con los tensores de pesos originales, con máxima diferencia absoluta cero.** Este control de exactitud impide atribuir el efecto a un cambio de pesos antes de la lesión.",
"",
"El estudio compara cinco pares de historias (A: generalización tardía bajo L1 inicial 1e-5; B: aprendizaje más rápido bajo L1 inicial .001), 300 neuronas ocultas, tarea de paridad 3 de 30 bits, 100% de validación, tres dosis fijas 30%,60%,90% y cuatro máscaras nuevas compartidas por pareja y dosis. En cada red lesionada se crean dos brazos: AdamW **nuevo** y AdamW **con momentos y contador restaurados** desde el checkpoint10000. Ambos realizan 500 actualizaciones bajo CE+L1=0,0001, lr0,001, wd0; hay controles intactos para ambos modos. Los datos de test no se utilizan. El total es **240 reconstrucciones**, con máscaras anidadas y solo cinco pares independientes de adquisición.",
"",
"## Auditoría de integridad y errata",
"",
"La **primera ejecución de V15 fue descartada completamente** al detectar memoria compartida entre estados AdamW de experimentos consecutivos. Se detuvieron procesos, se aislaron sus archivos fuera del repositorio y se corrigió el cargador mediante copia profunda y comprobación de punteros. La prueba de regresión confirmó 12 tensores compartidos en carga directa frente a **cero** con copia profunda. El archivo [V15_ALIAS_ERRATUM.md](V15_ALIAS_ERRATUM.md) detalla la decisión. Ningún resultado de esa primera ejecución inválida se incorpora a las estadísticas.",
"",
f"En la repetición válida, la auditoría [V15_ANALYSIS.json](V15_ANALYSIS.json) informa **{d['audit']['status']}**: {d['audit']['n_runs']} trayectorias, iguales pesos, índices de lesión y daño inicial entre versiones del optimizador. Esto controla un componente de la recuperabilidad que los experimentos anteriores habían mantenido fijo en AdamW nuevo.",
"",
"## Daño y recuperación por dosis",
"",
"![Área bajo el déficit para AdamW nuevo o restaurado](FIG_V15_OPTIMIZER_REPAIR.svg)",
"",
"| Dosis | AUC A, nuevo | AUC A, restaurado | AUC B, nuevo | AUC B, restaurado |",
"|---|---:|---:|---:|---:|",
]
for r in rows:
 report.append(f"| {int(r['percent'])}% | {fmt(r['mean_auc_A_fresh'])} | {fmt(r['mean_auc_A_resumed'])} | {fmt(r['mean_auc_B_fresh'])} | {fmt(r['mean_auc_B_resumed'])} |")
report+=["",
"Menor AUC significa menor déficit de precisión en relación con el control intacto a lo largo de 500 pasos. En este contraste de **mismos pesos y misma máscara**, la diferencia entre AdamW nuevo y restaurado no puede explicarse por una gravedad inicial distinta: el daño ocurre antes de actualizar los pesos.",
"",
"### Recuperaciones entre lesiones con caída inicial superior a 2 puntos",
"",
"| Dosis | Grupo A, nuevo → restaurado | Grupo B, nuevo → restaurado |",
"|---|---|---|",
]
for r in rows:
 report.append(f"| {int(r['percent'])}% | {r['A_recovered_fresh']}/{r['damaged_A']} → {r['A_recovered_resumed']}/{r['damaged_A']} | {r['B_recovered_fresh']}/{r['damaged_B']} → {r['B_recovered_resumed']}/{r['damaged_B']} |")
report += [
"",
"Estas cuentas describen eventos de recuperación a ≥99% de validación en dos observaciones consecutivas; los no recuperados a 500 pasos quedan **censurados**, no declarados irrecuperables. Las máscaras son repeticiones dentro de una misma red y no réplicas independientes del grupo.",
"",
"## Efecto del optimizador dentro del mismo modelo",
"",
"En cada dosis, la diferencia AUC_nuevo − AUC_restaurado mide el efecto de conservar AdamW **para una red fija**; valores positivos favorecen restaurar momentos. Las diferencias entre historias A/B se analizan por separado y continúan confundidas por L1 inicial. La comparación utiliza solo cinco semillas independientes y tres dosis, por lo que las pruebas de signo son exploratorias y múltiples.",
"",
"| Dosis | Efecto AdamW en A (nuevo−restaurado) | Efecto AdamW en B (nuevo−restaurado) | Semillas favorables a restaurar A/B |",
"|---|---:|---:|---|",
]
for r in rows:
 report.append(f"| {int(r['percent'])}% | {fmt(r['optimizer_effect_A_fresh_minus_resumed'])} | {fmt(r['optimizer_effect_B_fresh_minus_resumed'])} | {r['seed_A_optim_resumed_better']}/5 y {r['seed_B_optim_resumed_better']}/5 |")
report += [
"",
"## Interpretación y límites",
"",
"**La conclusión sobre el estado de AdamW es causal dentro del montaje:** dos ramas del mismo checkpoint con la misma lesión, datos y función de pérdida tienen trayectorias distintas por una intervención explícita sobre el estado del optimizador. El tamaño y consistencia de ese efecto dependen de la dosis y la semilla; las observaciones de una muestra finita no prueban una ley universal.",
"",
"Esto no identifica causalmente el efecto de haber experimentado grokking. Los dos grupos iniciales difirieron en L1 durante la adquisición y sus momentos, geometrías y estrategias internas pueden ser mediadores. El ordenador no simula neuronas que vuelven a crecer: reparan la función los pesos de las unidades supervivientes.",
"",
"El test original V12 constaba de 2.000 ejemplos reservados y se auditó una vez después de fijar los criterios V12; V15 trabaja exclusivamente con train y validación. Solo cinco pares independientes y cuatro máscaras por dosis no permiten afirmar equivalencia ni ausencia de diferencias pequeñas. El horizonte de 500 pasos no permite extrapolar a tiempos ilimitados.",
"",
"## Procedencia y continuidad",
"",
"Los protocolos y scripts completos están en [PREREG_V15_OPTIMIZER_REPAIR.md](PREREG_V15_OPTIMIZER_REPAIR.md), [v15_rebuild_optimizer.py](v15_rebuild_optimizer.py), [v15_optimizer_repair.py](v15_optimizer_repair.py), [v15_analyze.py](v15_analyze.py), [v15_check_optimizer_alias.py](v15_check_optimizer_alias.py), el directorio v15_optimizer_states con pesos y momentos reproducidos, y v15_repair con curvas CSV/JSON para cada dosis, máscara, semilla y modalidad. Informe V13/V14 disponible en REPORT_V13.md, REPORT_V13B.md y REPORT_V14.md.",
]
(ROOT/"REPORT_V15.md").write_text("\n".join(report)+"\n",encoding="utf-8")
print("V15_REPORT_READY",len(report),flush=True)
