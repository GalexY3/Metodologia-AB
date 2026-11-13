"""V53 preregistered report, paired environmental-seed bootstrap and controls."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent;O=R/"results"
raw=json.loads((O/"v53_material_raw.json").read_text("utf8"))
rows=raw["rows"]
assert len(rows)==32 and raw["n_worlds_per_seed"]==128
assert tuple(raw["environment_seeds"])==(999101,999107,999109,999121,999131,999137)
GOV=("NONE","LOCAL","GLOBAL","LOCAL_GLOBAL","FORECAST","PLACEBO","POLICY","FULL_PROXY")
ENV=("QUIET","PATCHY","SYSTEMIC","HEAVY")
assert set(x["mechanism"] for x in rows)==set(GOV)
assert set(x["environment"] for x in rows)==set(ENV)
for row in rows:
 assert row["n_worlds"]==768 and len(row["by_seed"])==6
 for x in row["by_seed"]:
  assert len(x["end_alive_worlds"])==128
  assert 0<=x["survival"]<=1
  assert x["pending_food_at_horizon"]<1e-8
  assert x["admin_per_living"]>=0
  assert x["transfer_loss_per_living"]>=0
  assert x["mean_net_food_per_living"]<=x["mean_gross_food_per_living"]+1e-9
  assert x["mean_gross_food_per_living"]<=1.0+1e-8
 def avg(key):
  return float(np.mean([x[key] for x in row["by_seed"]]))
 row["mean_alive_life_fraction"]=avg("total_alive_agent_rounds")/(128*48*96)
 row["net_food_per_initial_person_round"]=float(np.mean([
  x["mean_net_food_per_living"]*x["total_alive_agent_rounds"]/(128*48*96)
  for x in row["by_seed"]]))
def get(env,gov):
 return next(x for x in rows if x["environment"]==env and x["mechanism"]==gov)
def paired(env,a,b,key="survival"):
 va=get(env,a)["by_seed"];vb=get(env,b)["by_seed"]
 av=np.asarray([v[key] for v in va])
 bv=np.asarray([v[key] for v in vb])
 assert [v["seed"] for v in va]==[v["seed"] for v in vb]
 d=av-bv
 rng=np.random.default_rng(53532026)
 boots=d[rng.integers(0,6,(20000,6))].mean(1)
 return dict(environment=env,contrast=f"{a}_minus_{b}",metric=key,
  estimate=float(d.mean()),by_seed=d.tolist(),
  descriptive_ci95=np.quantile(boots,[.025,.975]).tolist())
contrasts=[]
for env in ENV:
 for a,b in (("LOCAL","NONE"),("GLOBAL","NONE"),("LOCAL_GLOBAL","LOCAL"),
  ("LOCAL_GLOBAL","GLOBAL"),("FORECAST","LOCAL_GLOBAL"),
  ("FORECAST","PLACEBO"),("POLICY","LOCAL_GLOBAL"),
  ("FULL_PROXY","LOCAL_GLOBAL"),("FULL_PROXY","NONE")):
  contrasts.append(paired(env,a,b))
p=get("PATCHY","LOCAL_GLOBAL")["survival"]
hyp={
 "h53a_local_improves_patchy_by_5pp":get("PATCHY","LOCAL")["survival"]-
    get("PATCHY","NONE")["survival"]>=.05,
 "h53b_global_plus_local_improves_over_local_by_5pp":p-
    get("PATCHY","LOCAL")["survival"]>=.05,
 "h53c_forecast_improves_over_local_global_by_3pp":
    get("PATCHY","FORECAST")["survival"]-p>=.03,
 "h53d_forecast_at_least_placebo_patchy":
    get("PATCHY","FORECAST")["survival"]>=get("PATCHY","PLACEBO")["survival"],
 "h53e_no_administration_cost_under_quiet":
    get("QUIET","NONE")["mean_net_food_per_living"]>
    get("QUIET","FULL_PROXY")["mean_net_food_per_living"],
 "h53f_full_proxy_not_perfect_under_systemic":
    get("SYSTEMIC","FULL_PROXY")["all_alive_fraction"]<1.
}
s2=get("PATCHY","LOCAL")["survival"]-get("PATCHY","NONE")["survival"]
s3=get("PATCHY","GLOBAL")["survival"]-get("PATCHY","NONE")["survival"]
both=get("PATCHY","LOCAL_GLOBAL")["survival"]-get("PATCHY","NONE")["survival"]
synergy=both-s2-s3
with (O/"COMPARACION_V53.csv").open("w",newline="",encoding="utf8") as handle:
 fields=["environment","mechanism","n_worlds","survival","all_alive_fraction",
  "viable_teams","mean_net_food_per_living","mean_gross_food_per_living",
  "admin_per_living","transfer_loss_per_living","transfers_per_living",
  "mean_alive_life_fraction","net_food_per_initial_person_round"]
 writer=csv.DictWriter(handle,fields)
 writer.writeheader()
 for r in rows:writer.writerow({k:r[k] for k in fields})
with (O/"CONTRASTES_V53.csv").open("w",newline="",encoding="utf8") as f:
 columns=["environment","contrast","metric","estimate","ci95_lower","ci95_upper"]
 writer=csv.DictWriter(f,columns);writer.writeheader()
 for r in contrasts:
  writer.writerow(dict(environment=r["environment"],contrast=r["contrast"],
   metric=r["metric"],estimate=r["estimate"],
   ci95_lower=r["descriptive_ci95"][0],
   ci95_upper=r["descriptive_ci95"][1]))
sha_files=("PREREG_V53_VSM_MATERIAL.md",
 "v53_vsm_material.py","test_v53_vsm_material.py","v53_summarize.py")
sha={file:hashlib.sha256((R/file).read_bytes()).hexdigest()
  for file in sha_files}
metrics=dict(cells=rows,contrasts=contrasts,hypotheses=hyp,
 observed_synergy_patchy=synergy,sha256=sha,
 n_conditions=32,n_worlds=24576,
 external_governance=True,model="limited functions inspired by VSM, NOT the full viable system model",
 assumptions="12 externally fixed K4 teams, 4 roles already complete, ideal all-to-all unilateral donation; new subsistence stocks, temporary production outages, irreversible deaths",
 inference="bootstrap of six paired environment seeds is descriptive, not independent training replicates")
(O/"METRICAS_V53.json").write_text(json.dumps(metrics,indent=2),encoding="utf8")
def table(values,heads):
 return "\n".join(["| "+" | ".join(heads)+" |",
 "| "+" | ".join(["---"]*len(heads))+" |"]+
 ["| "+" | ".join(map(str,r))+" |" for r in values])
f=lambda v:f"{v:.4f}"
report=[
 "# V53 — ¿Merecen la pena materialmente los mecanismos de regulación inspirados en Stafford Beer?",
 "",
 "## Naturaleza de la contrastación",
 "",
 "Experimentamos con **proxies reguladores costosos** inspirados en el VSM y Ashby; no aplicamos el VSM en su forma íntegra. La producción S1 es un límite deliberadamente favorable de la sociedad V25/V51/V52: 48 personas ya diferenciadas en 12 equipos K4, cuatro especialidades por equipo, todos los trabajadores operativos entregan un bien a cada miembro vivo que lo necesita. No se aprendieron roles, convenios o reguladores nuevos en este experimento. **Alimento máximo sin perturbación: 0,88 por persona-ronda**. El valor real de cada supuesto beneficio se calcula con pérdidas del 5 % del volumen transferido y costes administrativos deducidos del alimento, y se mide supervivencia hasta la ronda96.",
 "",
 "Se añade una ecología explícita que no existía en V25: reservas por persona inicialmente1,2, máximo2,2, consumo de subsistencia0,75 por ronda, muerte irreversible si las reservas se agotan, productores temporalmente incapacitados que consumen pero no envían bienes. La muerte elimina la capacidad productiva del especialista de su equipo y puede desencadenar cascadas. No hay intercambio de alimentos entre mundos ni dinero artificial creado por regulación.",
 "",
 "Se simularon32 escenarios (4 distribuciones de perturbaciones ×8 regímenes de gestión), con seis semillas ambientales nuevas y128 mundos por semilla en cada combinación: **24.576 sociedades y2.359.296 rondas-sociedad**. Los episodios de fallo productivo son idénticos entre regímenes para cada pareja semilla/mundo. Las unidades individuales dentro de un mundo comparten shocks y no son réplicas independientes.",
 "",
 "## Alimentación y supervivencia por arquitectura",
 "",
 table([[env,gov,
 f(get(env,gov)["survival"]),
 f(get(env,gov)["viable_teams"]),
 f(get(env,gov)["mean_net_food_per_living"]),
 f(get(env,gov)["mean_alive_life_fraction"])]
 for env in ENV for gov in GOV],
 ["Entorno","Regulación","Población viva al final",
  "Equipos completos al final","Alimento neto/persona viva","Fracción de persona-rondas vivas"]),
 "",
 "**Advertencia sobre denominadores:** alimento neto por persona *viva* es una intensidad condicionada a supervivencia y puede subir cuando mueren personas dependientes; la métrica no debe usarse aisladamente para clasificar regímenes. Para cada celda también se informa el total de persona-rondas vivas y el alimento neto por persona inicial-ronda, evitando el sesgo de supervivencia. La supervivencia final y los equipos aún productivos son los resultados de viabilidad.",
 "",
 "## Interacciones de las funciones y controles de información",
 "",
 "Los proxies son: NONE (sin regulador); LOCAL (ayuda dentro de K4, coste0,004/persona/ronda); GLOBAL (traslados entre equipos con retardo de un turno, coste0,008); LOCAL_GLOBAL (ambos); FORECAST (+0,008 con información verdadera del siguiente shock); PLACEBO (misma función/coste que FORECAST, pero señal del shock atribuida a otros equipos); POLICY (+0,003 por umbral común de reserva adaptativo); FULL_PROXY (LOCAL_GLOBAL+FORECAST+POLICY). Todas las transferencias pagan pérdida material del 5 %, y el alimento queda en stocks conservativos. El lugar de llegada y la disponibilidad de almacén limitan el resultado efectivo.",
 "",
 table([[r["contrast"],f(r["estimate"]),
 f(r["descriptive_ci95"][0]),f(r["descriptive_ci95"][1])]
 for r in contrasts if r["environment"]=="PATCHY"],
 ["Contraste PATCHY","Δ supervivencia","IC descriptivo 95% bajo","IC descriptivo 95% alto"]),
 "",
 f"La interacción material observada en PATCHY entre LOCAL y GLOBAL equivale a **{synergy:+.4f}** de supervivencia adicional más allá de sumar las mejoras individuales (comparadas contra NONE). Es una *interacción factorial bajo esta parametrización*, no una ley universal de complementariedad jerárquica.",
 "",
 "## Hipótesis preregistradas",
 "",
 table([[k,"cumple" if v else "no cumple"] for k,v in hyp.items()],
 ["Hipótesis","Estado"]),
 "",
 "H53a y H53b contrastan utilidad material de ayuda local e interequipos. H53c exigía ventaja de anticipación de shocks sobre la regulación reactiva, **una hipótesis que puede ser falsada** por costes y por la calidad del mecanismo de transferencia. H53d requiere que un mensaje correcto iguale o supere a un placebo con información atribuido a otros equipos; no se sustituye por la afirmación de que el pronóstico sea necesariamente útil. H53e prueba penalización real de administrar en un mundo estable. H53f verifica que añadir canales regulatorios no equivale a capacidad material ilimitada en un entorno de perturbaciones sistémicas.",
 "",
 "## ¿En qué sentido cuestiona o respalda a Beer?",
 "",
 "[Inferencia] Esta prueba apoya la idea general de que integrar funciones de coordinación a diferentes escalas **puede** incrementar la resiliencia material cuando las perturbaciones son heterogéneas y los excedentes transportables. No demuestra que las cinco funciones de Beer sean necesarias o suficientes, porque solo se implementan proxies parciales y porque las especialidades S1, la red y el suministro cooperativo se fijaron externamente.",
 "",
 "[Inferencia] La disminución de supervivencia bajo FORECAST y FULL_PROXY en PATCHY, respecto de LOCAL_GLOBAL, apunta a rendimientos negativos de algunas capas adicionales con un diseño concreto de mensajes, costes y políticas. El hecho de que NONE sea viable sin gestión en QUIET **no refuta** el VSM en términos generales: puede haber funciones implícitas, además de que viabilidad depende de entorno, escala y criterio de supervivencia.",
 "",
 "Asimismo, el colapso en HEAVY sugiere un límite por falta de recursos y redundancia productiva —el entorno K4 dispone de un único productor por especialidad—. Un regulador no puede reponer bienes inexistentes mediante comunicación. La ley de variedad requerida de Ashby funciona aquí como inspiración para estudiar la capacidad de regulación y la diversidad de perturbaciones; V53 no constituye una deducción formal de ese teorema.",
 "",
 "## Alcance hacia emergencia sociológica",
 "",
 "No hay emergencia de un S2–S5 espontáneo. V53 responde a una pregunta material previa: si se incorporase una capacidad de coordinación o anticipación, ¿existiría algún beneficio suficiente para compensar su coste? El siguiente experimento debe permitir a los individuos escoger, financiar y abandonar mecanismos de coordinación, con controles de información y de beneficio privado, para distinguir la aparición endógena de instituciones de su imposición experimental.",
 "",
 "## Fuentes teóricas",
 "",
 "Beer, S. (1984). *The Viable System Model: Its Provenance, Development, Methodology and Pathology*. JORS. https://doi.org/10.1057/jors.1984.2",
 "",
 "Crisan Tran, C. I. (2008/2009). *Assessing the Viable System Model: an empirical test of the viability-hypothesis*. https://doi.org/10.1504/IJASS.2008.022795",
 "",
 "Schwaninger, M. y Scheef, C. (2016). *A Test of the Viable System Model: Theoretical Claim vs. Empirical Evidence*. https://doi.org/10.1080/01969722.2016.1209375",
 "",
 "Ashby, W. R. (1956), cibernética y ley de variedad requerida. https://ashby.info/Ashby-Mechanisms_of_intelligence.pdf",
 "",
 "## Reproducción",
 "",
 "PREREG_V53_VSM_MATERIAL.md, v53_vsm_material.py, test_v53_vsm_material.py, v53_material_raw.json con cada mundo y cada semilla, COMPARACION_V53.csv, CONTRASTES_V53.csv, METRICAS_V53.json y este informe. SHA256:",
 *[f"{p}: {hashval}" for p,hashval in sha.items()]
]
(O/"RESULTADOS_INTEGRALES_V53.md").write_text("\n".join(report),encoding="utf8")
print("V53_SUMMARY",len(rows),"cells",hyp,"interaction",round(synergy,5))
for r in contrasts:
 if r["environment"]=="PATCHY":
  print(r["contrast"],round(r["estimate"],4),
    [round(x,4) for x in r["descriptive_ci95"]])
