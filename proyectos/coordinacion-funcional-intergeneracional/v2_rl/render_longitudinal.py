"""Render inspectable longitudinal graphs from V2-E research results.

Use pure SVG to avoid adding plotting dependencies to the research venv.
Three task graphs (k2..4) for progress, TV and churn, from t0 to t240.
"""
from pathlib import Path
import json,html,statistics
ROOT=Path(__file__).resolve().parent
data=json.loads((ROOT/"longitudinal_v2e"/"SUMMARY.json").read_text(encoding="utf-8"))
assert data["n_results"]==45 and data["n_independent_trained_cohorts"]==3
rows=data["summary"]
palette={
 "credit2":("#315EAA","Aprendida · contribución contrafactual"),
 "credit0":("#A85E39","Aprendida · recompensa global"),
 "random_always":("#B28B2E","Aleatorio continuo"),
 "random_T24":("#278472","Aleatorio 24 rondas, luego parar"),
 "stay":("#898989","Sin cambios")}
ORDER=("credit2","credit0","random_always","random_T24","stay")
WIDTH,HEIGHT=1000,560
left,right,top,bottom=85,35,84,123
plotwidth=WIDTH-left-right;plotheight=HEIGHT-top-bottom
X=lambda t:left+(t/240)*plotwidth
FMT=lambda v,d=3:format(v,f".{d}f").replace(".",",")
def plot(k,kind):
 obj={r["mode"]:r for r in rows if r["k"]==k}
 if kind=="progress":
  title=f"k={k} funciones · mejora respecto al error inicial"
  key="progress_curve_mean";minimum=0.;maximum=105.
  ytitle="Reducción del error inicial (%)"
  ticks=[0,20,40,60,80,100]
 elif kind=="TV":
  title=f"k={k} funciones · distancia al reparto ideal"
  key="distance_curve_mean"
  minimum=0.;maximum={2:.22,3:.40,4:.48}[k]
  ytitle="Distancia TV (menor = mejor)"
  ticks=[minimum+(maximum-minimum)*v/5 for v in range(6)]
 else:
  title=f"k={k} funciones · agentes que cambian color por turno"
  key="churn_curve_mean";minimum=0;maximum=.39
  ytitle="Fracción que cambia de color"
  ticks=[0,.05,.1,.2,.3,.39]
 Y=lambda val:top+(maximum-val)/(maximum-minimum)*plotheight
 out=[
 f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}">',
 f'<rect width="{WIDTH}" height="{HEIGHT}" fill="#fff"/>',
 f'<text x="38" y="34" fill="#1c2631" font-size="23" font-weight="600" font-family="Arial">{html.escape(title)}</text>',
 '<text x="38" y="56" fill="#526170" font-size="12" font-family="Arial">N=120 · 3 cohortes de entrenamiento independientes · 24 sociedades por cohorte y política · 240 turnos</text>'
 ]
 for tick in ticks:
  yy=Y(tick)
  out.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{WIDTH-right}" y2="{yy:.1f}" stroke="#e6ebef" stroke-width="1"/>')
  lbl=round(tick,1) if kind=="progress" else FMT(tick,2)
  out.append(f'<text x="{left-12}" y="{yy+4:.1f}" text-anchor="end" fill="#526170" font-size="12" font-family="Arial">{lbl}</text>')
 for tick in range(0,241,40):
  xx=X(tick)
  out.append(f'<line x1="{xx:.1f}" y1="{top}" x2="{xx:.1f}" y2="{HEIGHT-bottom}" stroke="#f1f3f5"/>')
  out.append(f'<text x="{xx:.1f}" y="{HEIGHT-bottom+24}" text-anchor="middle" fill="#526170" font-size="12" font-family="Arial">{tick}</text>')
 if kind=="TV":
  yy=Y(.06)
  out.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{WIDTH-right}" y2="{yy:.1f}" stroke="#6b7280" stroke-width="1.3" stroke-dasharray="5 5"/>')
  out.append(f'<text x="{WIDTH-right-5}" y="{yy-7:.1f}" text-anchor="end" fill="#636b76" font-size="11" font-family="Arial">Umbral D = 0,06</text>')
 elif kind=="progress":
  yy=Y(100)
  out.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{WIDTH-right}" y2="{yy:.1f}" stroke="#6b7280" stroke-dasharray="5 5"/>')
  out.append(f'<text x="{WIDTH-right-4}" y="{yy-7:.1f}" text-anchor="end" fill="#636b76" font-size="11" font-family="Arial">Reparto exacto (100 %)</text>')
 out.append(f'<text x="{left+plotwidth/2:.1f}" y="{HEIGHT-bottom+53}" text-anchor="middle" fill="#526170" font-family="Arial" font-size="13">Turno desde la inicialización</text>')
 for j,mode in enumerate(ORDER):
  color,label=palette[mode]
  series=obj[mode][key]
  assert len(series)==241
  pts=" ".join(f"{X(t):.2f},{Y(val):.2f}" for t,val in enumerate(series))
  dash="6,4" if mode.startswith("random") else "none"
  width=3.2 if mode=="credit2" else 2.1
  out.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{width}" stroke-dasharray="{dash}" stroke-linejoin="round" stroke-linecap="round"/>')
  v=series[-1]
  out.append(f'<circle cx="{X(240):.2f}" cy="{Y(v):.2f}" r="4.2" fill="{color}"/>')
  lx=85+(j%2)*445
  ly=HEIGHT-60+(j//2)*18
  out.append(f'<line x1="{lx}" y1="{ly}" x2="{lx+29}" y2="{ly}" stroke="{color}" stroke-width="3" stroke-dasharray="{dash}"/>')
  out.append(f'<text x="{lx+38}" y="{ly+4}" font-size="12" font-family="Arial" fill="#343e48">{html.escape(label)}</text>')
 out.append('</svg>')
 outpath=ROOT/f"FIG_V2E_K{k}_{kind}.svg"
 outpath.write_text("\n".join(out),encoding="utf-8")
 print("FIG",outpath.name,"bytes",outpath.stat().st_size,flush=True)

for k in (2,3,4):
 for kind in ("progress","TV","churn"):plot(k,kind)

lines=[
 "# V2-E — Curvas temporales de coordinación aprendida y aleatoria",
 "",
 "**Fecha:** 10 de noviembre de 2026. **Diseño:** [PREREG_LONGITUDINAL.md](PREREG_LONGITUDINAL.md).",
 "",
 "Se mide N=120 agentes durante 240 turnos, con k=2,3,4 funciones, mediante 3 cohortes de aprendizaje independientes y 24 sociedades nuevas por cohorte. Todas comienzan con 70% de los agentes en un mismo color, cuyo nombre se aleatoriza. Los modelos están congelados (sin aprendizaje en test).",
 "",
 "**Eje «progreso».** La variable P(t)=100·[1−D(t)/D(0)] es el **porcentaje de reducción de error desde el inicio**, con D la distancia de variación total al reparto 1/k. P=100 significa equilibrio exactamente perfecto. P=80 NO significa 80% de agentes correctamente asignados ni 80% de aciertos en una clasificación; solo que se redujo un 80% el desequilibrio inicial.",
 "",
 "**Criterio de estabilidad distinto del progreso.** Además de una buena D final, se exige D≤0,06 y ≤5% de agentes cambiando por turno durante los últimos 10 turnos. Un aleatorio que continúa actuando puede presentar P alto pero 0% de estabilidad. El aleatorio que se detiene tras 24 turnos es un control diseñado con reloj externo, no una política adaptativa.",
 ""
]
for k in (2,3,4):
 lines +=[
  f"## {k} funciones",
  "",
  f"![Mejora relativa desde turno 0 con {k} colores](FIG_V2E_K{k}_progress.svg)",
  "",
  f"![Distancia absoluta desde turno 0 con {k} colores](FIG_V2E_K{k}_TV.svg)",
  "",
  f"![Tasa de cambios desde turno 0 con {k} colores](FIG_V2E_K{k}_churn.svg)",
  "",
  "| Condición | Reducción del error al turno 240 | D al turno 240 | Estables /72 | Churn final | Cambio D promedio 200–240 vs160–200 |",
  "|---|---:|---:|---:|---:|---:|"]
 for mode in ORDER:
  x=next(r for r in rows if r["k"]==k and r["mode"]==mode)
  label=palette[mode][1]
  lines.append(f"| {label} | {FMT(x['final_progress_pct'],1)}% | {FMT(x['final_D'])} | {x['stable_count']}/72 | {FMT(x['final_churn'])} | {FMT(x['late_D_change_mean_last40_minus_prev40'],4)} |")
 lines +=[""]
lines +=[
 "## Auditoría e interpretación",
 "",
 "Todos los puntos temporales proceden de los archivos completos en [longitudinal_v2e](longitudinal_v2e), 45 archivos por condición/cohorte/tarea y curvas de 241 observaciones. [SUMMARY.json](longitudinal_v2e/SUMMARY.json) contiene medias agregadas calculadas sin seleccionar las cohortes exitosas. Las primeras 24 actualizaciones de random_T24 son aleatorias; desde la 25 no hay mensajes ni cambios y por eso su curva se vuelve estrictamente horizontal. No es aprendizaje.",
 "",
 "Las tres cohortes de actores con crédito contrafactual aprendieron estrategias bajo supervisión global del **entrenador**, mientras los actores solamente vieron colores locales, solicitudes y el feedback global escalar anterior. Por ello es aprendizaje descentralizado en ejecución, **pero no** aprendizaje con refuerzo global puro exclusivamente. El control credit0 sí usa solamente refuerzo común en gradiente, con crítico global durante entrenamiento.",
 "",
 "No afirmar convergencia matemática a un punto fijo por observar una meseta en media de 240 turnos: el comportamiento puede variar entre sociedades, y el promedio aleatorio puede ser plano mientras cada sociedad sigue cambiando. La prueba causal social no se ha realizado.",
]
(ROOT/"REPORT_LONGITUDINAL.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
print("REPORT_LONGITUDINAL_DONE",len(lines),flush=True)
