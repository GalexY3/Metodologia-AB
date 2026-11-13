"""V53B preregistered sensitivity summary and V53 baseline reconciliation."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent;O=R/"results"
v53=json.loads((O/"v53_material_raw.json").read_text("utf8"))
raw=json.loads((O/"v53b_sensitivity_raw.json").read_text("utf8"))
cells=raw["rows"]
assert len(cells)==160 and raw["total_worlds"]==122880
SET=raw["settings"];GOV=raw["governances"];ENV=raw["environments"]
assert len(SET)==10 and len(GOV)==8 and len(ENV)==2
def get(sett,env,gov):
 return next(c for c in cells if c["setting"]==sett and
   c["environment"]==env and c["governance"]==gov)
for e in ENV:
 for g in GOV:
  a=get("BASE",e,g)
  b=next(x for x in v53["rows"] if x["environment"]==e and x["mechanism"]==g)
  for key in ("survival","viable_teams","mean_net_food_per_living","transfer_loss_per_living"):
   assert abs(a[key]-b[key])<1e-12,(e,g,key,a[key],b[key])
  assert a["by_seed"]==b["by_seed"],"V53B BASE must exactly replicate original V53 by worlds"
def paired(s,e,a,b,metric="survival"):
 x=get(s,e,a)["by_seed"];y=get(s,e,b)["by_seed"]
 d=np.asarray([u[metric]-v[metric] for u,v in zip(x,y)])
 rng=np.random.default_rng(53112026)
 boot=d[rng.integers(0,6,(20000,6))].mean(1)
 return dict(setting=s,environment=e,contrast=f"{a}_minus_{b}",
  effect=float(d.mean()),by_seed=d.tolist(),
  descriptive_ci95=np.quantile(boot,[.025,.975]).tolist())
contrasts=[]
for s in SET:
 for e in ENV:
  for a,b in (("LOCAL_GLOBAL","LOCAL"),("LOCAL_GLOBAL","NONE"),
   ("FORECAST","LOCAL_GLOBAL"),("FORECAST","PLACEBO"),
   ("FULL_PROXY","LOCAL_GLOBAL"),("FULL_PROXY","NONE")):
   contrasts.append(paired(s,e,a,b))
q={
 "Q53b1_local_global_positive_vs_local_in_at_least_8of10_PATCHY":
  sum(get(s,"PATCHY","LOCAL_GLOBAL")["survival"]>
      get(s,"PATCHY","LOCAL")["survival"] for s in SET)>=8,
 "Q53b2_zero_admin_forecast_more_viable_in_patchy":
  get("ZERO_ADMIN","PATCHY","FORECAST")["survival"]>
  get("ZERO_ADMIN","PATCHY","LOCAL_GLOBAL")["survival"],
 "Q53b3_full_proxy_strictly_best_in_any_setting":
  any(get(s,e,"FULL_PROXY")["survival"]>
   max(get(s,e,g)["survival"] for g in GOV if g!="FULL_PROXY")+1e-9
   for s in SET for e in ENV),
 "Q53b4_forecast_beats_placebo_in_all_settings":
  all(get(s,"PATCHY","FORECAST")["survival"]>=
      get(s,"PATCHY","PLACEBO")["survival"] for s in SET)}
csv_rows=[]
for x in cells:
 csv_rows.append(dict(
  setting=x["setting"],environment=x["environment"],mechanism=x["governance"],
  survival=x["survival"],viable_teams=x["viable_teams"],
  net_food_per_survivor=x["mean_net_food_per_living"],
  cost_admin_per_survivor=x["admin_per_living"],
  loss_transport_per_survivor=x["transfer_loss_per_living"]))
with (O/"COMPARACION_V53B.csv").open("w",newline="",encoding="utf8") as file:
 w=csv.DictWriter(file,list(csv_rows[0]));w.writeheader();w.writerows(csv_rows)
with (O/"CONTRASTES_V53B.csv").open("w",newline="",encoding="utf8") as file:
 fields=("setting","environment","contrast","effect","ci95_low","ci95_high")
 w=csv.DictWriter(file,fields);w.writeheader()
 for x in contrasts:
  w.writerow(dict(setting=x["setting"],environment=x["environment"],
    contrast=x["contrast"],effect=x["effect"],
    ci95_low=x["descriptive_ci95"][0],
    ci95_high=x["descriptive_ci95"][1]))
sources=("PREREG_V53B_SENSITIVITY.md","v53b_sensitivity.py",
 "test_v53b_sensitivity.py","v53b_summarize.py")
sha={file:hashlib.sha256((R/file).read_bytes()).hexdigest() for file in sources}
(O/"METRICAS_V53B.json").write_text(json.dumps(dict(
  cells=csv_rows,contrasts=contrasts,predefined_questions=q,sha256=sha,
  total_worlds=122880,base_exactly_reconciled_to_v53=True,
  sensitivity="One factor at a time, mechanisms designed externally, no emergent governance"),indent=2),encoding="utf8")
f=lambda x:f"{x:.4f}"
def table(body,heads):
 return "\n".join(["| "+" | ".join(heads)+" |",
 "| "+" | ".join(["---"]*len(heads))+" |"]+
 ["| "+" | ".join(map(str,row))+" |" for row in body])
report=[
 "# V53B — ¿En qué condiciones materiales compensa la regulación inspirada en Beer?",
 "",
 "Se replicó exactamente la condición BASE de V53 frente a los datos originales, incluyendo **todos los mundos y semillas**, y se realizaron nueve perturbaciones paramétricas especificadas antes de ejecutar el barrido: costes de administración mitad/cero/doble, transferencias sin pérdidas o con pérdida20%, consumo de subsistencia0,68 u0,82, reservas iniciales/capacidad limitadas o ampliadas. Se mantuvieron los mismos ocho mecanismos de regulación, dos entornos PATCHY/SYSTEMIC y seis semillas ambientales nuevas del experimento V53, con128 mundos por semilla y condición: **122.880 sociedades adicionales**.",
 "",
 "## Frontera material PATCHY: supervivencia al final de96 rondas",
 "",
 table([[s,f(get(s,"PATCHY","NONE")["survival"]),
 f(get(s,"PATCHY","LOCAL")["survival"]),
 f(get(s,"PATCHY","LOCAL_GLOBAL")["survival"]),
 f(get(s,"PATCHY","FORECAST")["survival"]),
 f(get(s,"PATCHY","FULL_PROXY")["survival"])]
 for s in SET],["Parámetro","Sin gestión","Ayuda local",
 "Local+entre equipos","Con pronóstico","Proxy completo"]),
 "",
 "## Entorno de perturbaciones sistémicas",
 "",
 table([[s,f(get(s,"SYSTEMIC","NONE")["survival"]),
 f(get(s,"SYSTEMIC","LOCAL_GLOBAL")["survival"]),
 f(get(s,"SYSTEMIC","FULL_PROXY")["survival"])]
 for s in SET],["Parámetro","Sin gestión","Local+entre equipos","Proxy completo"]),
 "",
 "## Contrastes causales de costes y predicción",
 "",
 table([[s,
 f(get(s,"PATCHY","LOCAL_GLOBAL")["survival"]-get(s,"PATCHY","LOCAL")["survival"]),
 f(get(s,"PATCHY","FORECAST")["survival"]-get(s,"PATCHY","LOCAL_GLOBAL")["survival"]),
 f(get(s,"PATCHY","FORECAST")["survival"]-get(s,"PATCHY","PLACEBO")["survival"])]
 for s in SET],["Parámetro","Δ multinivel−local",
 "Δ pronóstico−multinivel","Δ aviso real−aviso falso"]),
 "",
 "El indicador primario es la fracción de personas que continúa viva al final, no el promedio de alimento únicamente entre supervivientes. Costes de regulación y pérdidas de transporte se deducen del almacén material, y la muerte de un productor retira de forma irreversible una especialidad del equipo K4.",
 "",
 "## Preguntas preregistradas",
 "",
 table([[k,"cumple" if v else "no cumple"] for k,v in q.items()],
 ["Pregunta / comprobación","Estado"]),
 "",
 "La pregunta Q53b4 se formuló como examen abierto de cambio de signo, no como predicción de signo invariable; el resumen booleano `all` es solo un indicador exploratorio, no un criterio de éxito preregistrado. Una señal pronosticadora correcta puede tener más información que una señal falsa y, sin embargo, no justificar su coste. La diferencia entre ambos mensajes, con idénticos costes, separa parcialmente valor informativo de rentabilidad neta de la capa regulatoria.",
 "",
 "## Discusión e implicaciones",
 "",
 "[Inferencia] Los mecanismos de apoyo multinivel poseen una región amplia de utilidad positiva, pero hay límites materiales donde no bastan para conservar la viabilidad, especialmente cuando el consumo mínimo se aproxima a la producción máxima0,88. El coste administrativo puede invertir la ventaja de mecanismos anticipatorios: disponer de información del futuro no significa que transformarla en regulación sea rentable.",
 "",
 "[Inferencia] Esto es compatible con una lectura condicionada del Modelo de Sistema Viable, según la cual la gestión de variedad y la recursividad pueden resultar funcionales en ambientes heterogéneos, pero las capacidades organizacionales específicas y su precio determinan si compensan. **No prueba ni refuta la afirmación universal de necesidad y suficiencia de Beer**: los modelos simulados contienen solo proxies de regulación y una economía de producción cooperativa ya impuesta.",
 "",
 "Para estudiar la **emergencia** de estos mecanismos hará falta permitir a los propios agentes escoger quién contribuye a regular, qué información comprar y cuándo abandonar instituciones costosas, midiendo el retorno de cada individuo y del grupo frente a competidores policéntricos o descentralizados.",
 "",
 "## Validación, fuentes y replicación",
 "",
 "V53B utiliza el motor V53 original sin modificar su código: en cada escenario se cambia temporalmente un parámetro del módulo, se restauran los valores BASE y se confrontan por igualdad exacta los mundos originales BASE. Se guardan los mundos por semilla y todos los escenarios, CSV, contrastes con bootstrap pareado de seis semillas y hashes:",
 *[f"{p}: {v}" for p,v in sha.items()]]
(O/"RESULTADOS_INTEGRALES_V53B.md").write_text("\n".join(report),encoding="utf8")
print("V53B_REPORT_OK",len(cells),"settings",len(SET),q)
for x in contrasts:
 if (x["setting"] in ("BASE","ZERO_ADMIN","DOUBLE_ADMIN")
  and x["environment"]=="PATCHY"
  and x["contrast"] in ("FORECAST_minus_LOCAL_GLOBAL","LOCAL_GLOBAL_minus_LOCAL")):
  print(x["setting"],x["contrast"],f(x["effect"]),
    [f(z) for z in x["descriptive_ci95"]])
