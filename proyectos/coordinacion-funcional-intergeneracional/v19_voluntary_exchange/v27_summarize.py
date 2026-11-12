"""V27 cross-seed estimate, transparent about CPU vs GPU training."""
from __future__ import annotations
import csv,json,math,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent;RES=ROOT/"results"
SEEDS=(7311,8311,9311,10311,11311,12311)
NEW=[f"v27_CPU_REP_s{s}" for s in SEEDS]
ORIG=[f"v23_SMOOTH_s{s}" for s in (3111,4111,5111,6111)]
def read(p):return json.loads(p.read_text("utf8"))
def table(rows,head):
 return "\n".join(["| "+" | ".join(head)+" |","| "+" | ".join(["---"]*len(head))+" |"]+
  ["| "+" | ".join(map(str,r))+" |" for r in rows])
def wilson(ok,n,z=1.96):
 p=ok/n;den=1+z*z/n
 center=(p+z*z/(2*n))/den
 half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
 return max(0,center-half),min(1,center+half)
combined=[]
for name in NEW:
 folder=ROOT/"runs"/name
 spec=read(folder/"v23_spec.json");status=read(folder/"v23_status.json")
 assert status["state"]=="completed" and status["updates"]==1400
 assert spec["seed"] in SEEDS and spec["device"]=="cpu" and spec["social"]==1
 hold=read(RES/("v23_joint_holdout_"+name+".json"))
 audit=read(RES/("v23_joint_audit_"+name+".json"))
 assert len(hold["rows"])==48 and len(audit["rows"])==12
 def h(condition):
  return next(x for x in hold["rows"] if x["topology"]=="ring" and x["degree"]==2 and x["init"]=="monolith" and x["condition"]==condition)
 def c(mode):
  return next(x for x in audit["rows"] if x["topology"]=="ring" and x["degree"]==2 and x["init"]=="monolith" and x["mode"]==mode)
 target=h("joint_learned")
 random=max(h(cond)["mean_food"] for cond in ("role_random_015","role_random_035","role_random_060"))
 cf=c("normal")["mean_total"]
 no_social=c("no_history")["mean_total"]
 row=dict(model=name,training_platform="GalexY_travel_CPU",
    food=target["mean_food"],random_best=random,
    improvement=target["mean_food"]-random,
    gifts=target["gift"],links=target["complementary_links"],
    causal=cf,causal_positive_agents=c("normal")["positive_agents"],
    causal_no_history=no_social,
    success_double=(target["mean_food"]-random>.05 and cf>0),
    social_sensitivity=(no_social<0))
 combined.append(row)
legacy=read(RES/"METRICAS_V23.json")["models"]
for name in ORIG:
 a=next(x for x in legacy if x["model"]==name)
 row=dict(model=name,training_platform="DESKTOP_I4SULKD_GPU",
   food=a["food"],random_best=a["best_random"],
   improvement=a["improvement"],gifts=a["gift"],
   links=a["complementarity"],
   causal=a["causal"],causal_positive_agents=a["positive_persons"],
   causal_no_history=a["causal_no_history"],
   success_double=(a["improvement"]>.05 and a["causal"]>0),
   social_sensitivity=a["causal_no_history"]<0)
 combined.append(row)
assert len(combined)==10
n=len(combined);success=sum(x["success_double"] for x in combined)
lo,hi=wilson(success,n)
alone=sum(x["success_double"] for x in combined[:6])
with (RES/"COMPARACION_V27.csv").open("w",encoding="utf8",newline="") as f:
 w=csv.DictWriter(f,list(combined[0]));w.writeheader();w.writerows(combined)
(RES/"METRICAS_V27.json").write_text(json.dumps(dict(
 results=combined,n_training_initializations=n,
 n_new_cpu=6,n_original_gpu=4,
 success_double=success,
 success_new_cpu=alone,
 wilson_95=[lo,hi],
 setup="V23 same code and hyperparameters. New seeds trained on CPU PyTorch 2.15, original seeds trained GPU PyTorch 2.11; environmental holdouts and causal auditors same implementation."),indent=2),encoding="utf8")
report=[
 "# V27. Prevalencia empírica de soluciones cooperativas entre diez inicializaciones neuronales",
 "",
 "Campaña preregistrada el 12/11/2026. Seis nuevas semillas entrenadas en GALEXY_TRAVEL con el código original V23, sin importar pesos anteriores, y evaluadas con seis semillas ambientales y modelos congelados. Se integran las cuatro semillas V23 originales entrenadas en GPU. Los 10 entrenamientos comparten arquitectura, REINFORCE individual, curso de coste de regalo 0,01→0,12 hasta u800, 1400 actualizaciones, anillo grado dos, 24 personas, dos profesiones, lote20 y horizonte48. Diferencias de hardware y PyTorch quedan declaradas.",
 "",
 "## Resultados por inicialización",
 "",
 table([[r["model"],r["training_platform"],
       f'{r["food"]:.3f}',f'{r["random_best"]:.3f}',
       f'{r["improvement"]:+.3f}',f'{r["gifts"]:.1%}',
       f'{r["links"]:.1%}',f'{r["causal"]:+.3f}',
       f'{r["causal_positive_agents"]}/24',str(r["success_double"])] for r in combined],
   ["Modelo","Hardware entrenamiento","Alimento","Mejor aleatorio","Ventaja",
    "Donaciones","Enlaces complem.","Causal regalo","Personas positivas","Éxito doble"]),
 "",
 "## Criterio de éxito previamente fijado",
 "",
 "El criterio doble requiere alimento de la política congelada >0,05 por encima del mejor control de movilidad aleatoria entre tres tasas predefinidas, y retorno propio medio causal positivo al forzar una donación inicial. La sensibilidad social adicional exige retorno negativo al retirar el historial social en evaluación.",
 "",
 f"El criterio doble se observa en **{success}/{n}** inicializaciones; de ellas, **{alone}/6** en el segundo ordenador. El intervalo Wilson binomial 95% descriptivo sobre diez modelos es **[{lo:.3f}, {hi:.3f}]**. No debe interpretarse como estimación representativa de todos los espacios de parámetros, grafos o sociedades humanas. Las mismas seis semillas ambientales por evaluación no equivalen a replicaciones independientes del entrenamiento.",
 "",
 "## Qué se ha aprendido sobre la robustez",
 "",
 "La misma intervención de coste y algoritmo no conduce necesariamente a soluciones cooperativas. Registrar fallos y soluciones débiles sirve para estudiar cuencas de atracción, dependencia de trayectoria, sensibilidad al azar y barreras de exploración; la proporción encontrada depende de la arquitectura y los hiperparámetros congelados. [Inferencia] La alta variabilidad es compatible con un problema de coordinación de múltiples agentes y no permite describir el éxito como garantizado ni universal.",
 "",
 "El criterio de éxito no exige abastecimiento completo, ni estabilidad en redes reconectadas o N120/k4. El proyecto general continúa abierto. Para su reproducción se conservan las seis carpetas runs/v27_CPU_REP_s*, sus redes inicializadas individualmente, historias, estados finales y JSON de tests de roles y auditoría contrafactual.",
 "",
 "## Integridad y procedencia",
 "",
 "Preregistro PREREG_V27_INDEPENDENT_NEURAL_SEEDS.md; entrenador V23 idéntico al commit de referencia 210fc99a; evaluación v23_joint_holdout.py y causal v23_joint_audit.py. Los modelos de GPU se recuperan de results/METRICAS_V23.json, y los nuevos de results/v23_joint_holdout_v27_*.json y results/v23_joint_audit_v27_*.json. No se han cambiado las semillas de evaluación en función del resultado.",
 "",
 "Hash del preregistro:",
 hashlib.sha256((ROOT/"PREREG_V27_INDEPENDENT_NEURAL_SEEDS.md").read_bytes()).hexdigest()]
(RES/"RESULTADOS_INTEGRALES_V27.md").write_text("\n".join(report),encoding="utf8")
print("V27_REPORT",success,"/",n,"new",alone,"/6",
      "Wilson",round(lo,3),round(hi,3))
