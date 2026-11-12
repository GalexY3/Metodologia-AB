"""Source-backed V24/V24b results and feasibility boundaries."""
import json,csv,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
RES=ROOT/"results"
NAMES=[f"v24_K4_N{n}_s{seed}" for n in (48,120) for seed in (3111,4111)]+[
 f"v24B_K4_N48_s{seed}" for seed in (3111,4111)]
def load(p):return json.loads(p.read_text(encoding="utf8"))
def fmt(x):return f"{x:.4f}"
def table(rows,headers):
 return "\n".join(["| "+" | ".join(headers)+" |",
   "| "+" | ".join(["---"]*len(headers))+" |"]
   +["| "+" | ".join(map(str,r))+" |" for r in rows])
out=[]
for name in NAMES:
 folder=ROOT/"runs"/name
 spec=load(folder/"v24_spec.json")
 status=load(folder/"v24_status.json")
 assert status["state"]=="completed" and status["updates"]==spec["updates"]
 lines=[json.loads(z) for z in (folder/"v24_history.jsonl").read_text().splitlines()]
 last=lines[-1]
 assert last["update"]==status["updates"] and np.isclose(last["cost"],.12)
 def dev(z):
  return next(x for x in z["development"] if x["topology"]=="ring" and
     x["init"]=="monolith" and x["condition"]=="normal")
 a=dev(last)
 record=dict(model=name,n=spec["n"],seed=spec["seed"],
    schedule="delayed" if name.startswith("v24B") else "smooth",
    updates=spec["updates"],food=a["food"],gift=a["gift"],
    coverage=a["coverage"],full=a["full"],
    potential=a["potential_coverage"],
    balance=a["balanced"],
    theoretical_food_upper_at_actual_donations=.20+
         a["gift"]*(.8/3-.12),
    absolute_capacity_bound=.2+.8/3-.12)
 if name.startswith("v24B"):
  protocol=load(folder/"v24b_protocol.json")
  assert protocol["flat_through_update"]==800
  assert protocol["increase_through_update"]==1100
  checkpoints=[]
  for z in lines:
   b=dev(z)
   checkpoints.append(dict(update=z["update"],cost_train=z["cost"],
      food_test_high=b["food"],donation_test_high=b["gift"],
      coverage_test_high=b["coverage"]))
  record["stages"]=checkpoints
 out.append(record)
with (RES/"COMPARACION_V24.csv").open("w",encoding="utf8",newline="") as f:
 names=[k for k in out[0] if k!="stages"]
 w=csv.DictWriter(f,names);w.writeheader()
 for rec in out:w.writerow({k:rec.get(k) for k in names})
(RES/"METRICAS_V24.json").write_text(json.dumps(dict(models=out,
 theorem=dict(k=4,cost=.12,capacity_per_donor=1,
   max_full_fraction=1/3,max_average_food=.2+.8/3-.12,
   economy_without_donations=.2,
   production_cap_constraint="At most N donation units for N*(k-1) goods required for universal coverage.")),indent=2),encoding="utf8")
mainrows=[[x["model"],str(x["n"]),str(x["updates"]),
   fmt(x["food"]),f'{x["gift"]:.3%}',
   fmt(x["coverage"]),fmt(x["potential"]),
   fmt(x["full"]),fmt(x["theoretical_food_upper_at_actual_donations"])] for x in out]
stage=[]
for row in out:
 if "stages" in row:
  for x in row["stages"]:
   stage.append([row["model"],x["update"],fmt(x["cost_train"]),
      fmt(x["food_test_high"]),fmt(x["donation_test_high"]),
      fmt(x["coverage_test_high"])])
hfiles=["v24_k4_joint.py","v24b_delayed.py","test_v24_k4.py",
 "test_v24_feasibility.py","V24_TEOREMA_FACTIBILIDAD.md",
 "PREREG_V24_SCALING_K4.md","PREREG_V24B_DELAYED_COST.md"]
hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in hfiles}
report=[
 "# V24 y V24b. Escalamiento con cuatro profesiones y límite de capacidad",
 "",
 "Experimentos del 12/11/2026 sobre redes circulares de grado seis. Dos profesiones no implican cuatro: cada individuo necesita tres categorías complementarias, pero en V24 cada donante solo puede emitir un regalo por ronda. Actores privados, entrenamiento simultáneo sin preentrenamiento y costo final 0,12.",
 "",
 "## Resultados finales congelados en escenarios de desarrollo",
 "",
 table(mainrows,["Política","N","Actualizaciones","Alimento","Donaciones",
  "Cobertura realizada","Cobertura potencial","Plenitud",
  "Cota de alimento por tasa real de donaciones"]),
 "",
 "Las cuatro condiciones V24 (N48 y N120, dos inicializaciones por tamaño) colapsan a prácticamente ninguna donación. La capacidad de red para acceder a roles complementarios sigue alta y la cobertura material efectiva se aproxima a cero. La cota ajustada a la tasa real de donaciones permite comprobar que el colapso de alimento es compatible con la contabilidad material del modelo.",
 "",
 "## V24b — Intento preregistrado después del fracaso exploratorio a u200",
 "",
 "Protocolo alternativo: precio 0,002 hasta u800, elevación lineal hasta 0,12 entre u800 y u1100, después precio fijo hasta u1800; N48 y dos semillas. El archivo v24b_protocol.json documenta la excepción a la configuración heredada V24. Evaluación siempre con precio final 0,12.",
 "",
 table(stage,["Modelo","Actualización","Coste al entrenar",
   "Alimento evaluado a coste alto","Donaciones a coste alto",
   "Cobertura efectiva"]),
 "",
 "Un periodo barato prolongado retiene donaciones moderadas y alimento ligeramente por encima del baseline durante etapas tempranas, pero ambas políticas vuelven a dejar de donar cuando se impone el coste elevado. No se observa conservación estable de reciprocidad.",
 "",
 "## Interpretación matemática: factibilidad y límites",
 "",
 "Teorema en V24_TEOREMA_FACTIBILIDAD.md, comprobado con regresiones en test_v24_feasibility.py. Si G es la cantidad de regalos emitidos y cada donante puede hacer como máximo uno, la cantidad de necesidades distintas satisfecha no supera G; cada destinatario completamente abastecido requiere k-1 bienes. Por tanto, con g=G/N se verifica plenitud media ≤g/(k-1), y alimentación media ≤0,20+g(0,80/(k-1)−c), antes de costes de cambio de profesión.",
 "",
 "Para k=4 y c=0,12, el máximo de alimento medio para todas las políticas posibles es 0,3467 (q=1), y la plenitud máxima por ronda es un tercio. No se debe evaluar la calidad de estos experimentos comparándolos con alimentos de 0,7 de la sociedad k=2, pues ese valor es materialmente imposible bajo la capacidad de producción de V24. Para k≥8, regalar unidades a coste 0,12 jamás puede elevar la alimentación social media sobre 0,2 en este modelo unitario, por el límite de beneficio incremental por categoría.",
 "",
 "## Próximo contraste V25",
 "",
 "Abrir tres decisiones voluntarias de donación por persona y por ronda, manteniendo la posibilidad de rechazo y el aprendizaje privado. Dos condiciones: precio 0,12 por unidad y precio 0,04 por unidad. La primera prueba el aumento de capacidad con precio unitario idéntico; la segunda controla el gasto máximo total a 0,12. El oráculo determinista de pleno abastecimiento (0,64 y 0,88) solo verifica factibilidad matemática, no constituye una política aprendida.",
 "",
 "## Reproducibilidad",
 "",
 "Entrenador v24_k4_joint.py, protocolo de coste v24b_delayed.py, artefactos runs/v24_K4_N*/ y runs/v24B_K4_N48_*, especificaciones, logs, checkpoints y scripts de test. Las pruebas de integridad del laboratorio superan 50 casos.",
 "",
 "Hashes SHA256:",
 *[f"{p}: {digest}" for p,digest in hashes.items()]]
(RES/"RESULTADOS_INTEGRALES_V24.md").write_text("\n".join(report),encoding="utf8")
print("V24_REPORT_OK",len(out),[(x["model"],round(x["food"],4),round(x["gift"],4)) for x in out])
