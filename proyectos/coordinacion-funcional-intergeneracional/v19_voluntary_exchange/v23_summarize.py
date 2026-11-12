"""Generate source-backed V23 report from frozen, completed runs."""
from pathlib import Path
import json,csv,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parent
RES=ROOT/"results"
MODELS=[f"v23_SMOOTH_s{s}" for s in (3111,4111,5111,6111)]+[
        f"v23_CONSTANT_s{s}" for s in (3111,4111)]+[
        f"v23_NOSOC_s{s}" for s in (3111,4111)]
def load(p):return json.loads(p.read_text(encoding="utf8"))
def table(data,cols):
 return "\n".join(["| "+" | ".join(cols)+" |",
    "| "+" | ".join(["---"]*len(cols))+" |"]+
    ["| "+" | ".join(map(str,row))+" |" for row in data])
def fmt(x):return f"{x:+.3f}"
out=[];uncertainty={}
for name in MODELS:
 spec=load(ROOT/"runs"/name/"v23_spec.json")
 status=load(ROOT/"runs"/name/"v23_status.json")
 assert status["state"]=="completed" and status["updates"]==1400
 hold=load(RES/("v23_joint_holdout_"+name+".json"))
 causal=load(RES/("v23_joint_audit_"+name+".json"))
 assert len(hold["rows"])==48 and len(causal["rows"])==12
 assert len(hold["seeds"])==6 and len(causal["seeds"])==6
 def findhold(condition):
  return next(x for x in hold["rows"] if x["topology"]=="ring" and
    x["degree"]==2 and x["init"]=="monolith" and x["condition"]==condition)
 def findcausal(mode="normal",topology="ring",degree=2,init="monolith"):
  return next(x for x in causal["rows"] if x["topology"]==topology and
    x["degree"]==degree and x["init"]==init and x["mode"]==mode)
 target=findhold("joint_learned")
 baselines=[findhold("role_random_015"),findhold("role_random_035"),
            findhold("role_random_060")]
 best=max(baselines,key=lambda x:x["mean_food"])
 delta=np.array([z["mean_food"] for z in target["by_seed"]])-np.array(
   [z["mean_food"] for z in best["by_seed"]])
 rng=np.random.default_rng(912112)
 bs=delta[rng.integers(0,6,size=(10000,6))].mean(1)
 uncertainty[name]=dict(best_random=best["condition"],
    paired_by_environment_seed=delta.tolist(),
    mean=float(delta.mean()),
    bootstrap_descriptive_95=np.quantile(bs,[.025,.975]).tolist())
 row=dict(model=name,food=target["mean_food"],
   gift=target["gift"],complementarity=target["complementary_links"],
   exact_balance=target["balanced"],
   best_random=best["mean_food"],best_random_label=best["condition"],
   improvement=target["mean_food"]-best["mean_food"],
   no_history_food=findhold("donation_history_hidden")["mean_food"],
   relocated_food=findhold("people_relocated")["mean_food"],
   no_gifts_food=findhold("all_gifts_blocked")["mean_food"],
   causal=findcausal()["mean_total"],
   positive_persons=findcausal()["positive_agents"],
   causal_no_history=findcausal(mode="no_history")["mean_total"],
   causal_scramble=findcausal(mode="scramble")["mean_total"],
   causal_rewired=findcausal(topology="rewired")["mean_total"],
   causal_random_initial=findcausal(init="random")["mean_total"],
   causal_degree4=findcausal(degree=4)["mean_total"])
 out.append(row)
with (RES/"COMPARACION_V23.csv").open("w",encoding="utf8",newline="") as f:
 w=csv.DictWriter(f,list(out[0]));w.writeheader();w.writerows(out)
(RES/"METRICAS_V23.json").write_text(json.dumps(dict(
 models=out,uncertainty=uncertainty,training_agent_periods=8*1400*20*48*24,
 frozen_holdout_world_condition_paths=8*48*6*24,
 counterfactual_world_person_pairs=8*12*6*12*24),indent=2),encoding="utf8")
primary=out[:4]
cpu_replay=load(RES/"v23_travel_cpu_replication.json")
assert cpu_replay["cpu_torch"].endswith("+cpu") and len(cpu_replay["records"])==8
cpu_rows=[]
for model in ("v23_SMOOTH_s3111","v23_SMOOTH_s4111"):
 gpu=next(z for z in out if z["model"]==model)
 records=[z for z in cpu_replay["records"] if z["model"]==model]
 cpu_food=next(z for z in records if z["analysis"]=="food" and z["social"])
 cpu_causal=next(z for z in records if z["analysis"]=="causal" and z["mode"]=="normal")
 cpu_nohistory=next(z for z in records if z["analysis"]=="causal" and z["mode"]=="no_history")
 cpu_rows.append([model,f'{gpu["food"]:.4f}',f'{cpu_food["food"]:.4f}',
      fmt(gpu["causal"]),fmt(cpu_causal["mean_return"]),
      fmt(gpu["causal_no_history"]),fmt(cpu_nohistory["mean_return"])])
main_rows=[[q["model"],f'{q["food"]:.3f}',f'{q["gift"]:.1%}',
   f'{q["complementarity"]:.1%}',f'{q["exact_balance"]:.1%}',
   f'{q["best_random"]:.3f}',fmt(q["improvement"]),
   fmt(q["causal"]),f'{q["positive_persons"]}/24'] for q in out]
causal_rows=[[q["model"],fmt(q["causal"]),fmt(q["causal_no_history"]),
   fmt(q["causal_scramble"]),fmt(q["causal_rewired"]),
   fmt(q["causal_degree4"]),fmt(q["causal_random_initial"])] for q in out]
ablation_rows=[[q["model"],f'{q["food"]:.3f}',
  f'{q["no_history_food"]:.3f}',f'{q["relocated_food"]:.3f}',
  f'{q["no_gifts_food"]:.3f}'] for q in out]
sources=("v23_joint_cold.py","v23_joint_audit.py","v23_joint_holdout.py",
  "test_v23_joint.py","v23_travel_cpu_replication.py","PREREG_V23_JOINT_COLD_START.md")
hashes={q:hashlib.sha256((ROOT/q).read_bytes()).hexdigest() for q in sources}
report=[
 "# V23. Coaprendizaje de reciprocidad y ocupaciones desde cero",
 "",
 "Estudio fechado 12/11/2026, sobre el commit V21-V22 18d617c6. Ambos actores privados de cada uno de los 24 individuos se inicializan aleatoriamente y aprenden conjuntamente con REINFORCE sobre alimento individual descontado, sin imitación, actor congelado previo, reparto planificado de profesiones ni recompensa conjunta. Dos profesiones, anillo grado 2, coste de movilidad 0,015 cada ocho rondas, gamma 0,995, 1400 actualizaciones. Coste final de donación 0,12 para todos. Cuatro semillas de currículo progresivo, dos de coste alto constante y dos sin historial de donaciones.",
 "",
 "## Resultado fuera de muestra con seis semillas ambientales y 24 mundos por semilla",
 "",
 table(main_rows,["Modelo","Alimento","Donaciones","Enlaces de oficios distintos",
  "Repartos 12/12","Mejor control aleatorio","Ganancia","Retorno causal","Agentes positivos"]),
 "",
 "El mejor control aleatorio se obtiene entre tres probabilidades predefinidas de cambio ocupacional: 0,15; 0,35 y 0,60. Se selecciona la mayor alimentación de cada una, sin reajustar el modelo; esto es conservador frente a un solo control pero la selección afecta la inferencia de intervalos. El resultado se evalúa sobre políticas congeladas y semillas ambientales no entrenadas.",
 "",
 "## Auditoría de donación inicial forzada (todas las personas)",
 "",
 table(causal_rows,["Modelo","Normal","Sin memoria social de donaciones",
   "Identidades sociales alteradas","Grafo reconectado",
   "Anillo grado 4","Inicio ocupacional aleatorio"]),
 "",
 "El agente obligado a dar asume exactamente -0,12 de alimento en la primera ronda frente al brazo emparejado sin donación. Se estima su retorno propio futuro con las políticas de roles y donaciones congeladas. Seis semillas ambientales por escenario, 12 mundos por semilla, 24 focos individuales. Conservar signo negativo y personas con retorno desfavorable; no interpretar magnitudes como una probabilidad de cooperación universal.",
 "",
 "## Controles mecanísticos y transferencia",
 "",
 table(ablation_rows,["Modelo","Normal","Sin historial social","Personas reasignadas","Donaciones bloqueadas"]),
 "",
 "Las redes aprendidas con escaso historial social forman a veces distribuciones ocupacionales casi perfectas y simultáneamente dejan de donar: la complementariedad de puestos no equivale a cooperación material. La permutación de políticas privadas entre posiciones reduce la alimentación. La generalización a red reconectada es desigual y dos de cuatro semillas progresivas pierden retorno causal positivo.",
 "",
 "## Replicación de V23 en el segundo ordenador",
 "",
 "Se replicaron las políticas congeladas de V23 en GalexY_travel con PyTorch CPU 2.15.0 en lugar del entorno GPU original. Se ha utilizado el mismo código y los mismos checkpoints, con 16 mundos por semilla en evaluación de alimento y 4 en auditoría causal (frente a 24 y 12 en el PC principal). La diferencia en lotes explica parte del error Monte Carlo y no permite interpretar la réplica como una implementación independiente. Las señales de retorno individual permanecieron consistentes.",
 "",
 table(cpu_rows,["Modelo","Alimento GPU","Alimento CPU","Retorno causal GPU","Retorno causal CPU","Sin historial GPU","Sin historial CPU"]),
 "",
 "## Estructura de dependencia estadística",
 "",
 "Las seis semillas ambientales son unidades de agrupamiento de la evaluación, pero no equivalen a seis entrenamientos nuevos. Se empleó bootstrap descriptivo de contrastes emparejados por esas seis semillas; los intervalos no cubren variación sobre infinitas inicializaciones de redes. Solo existen cuatro semillas neuronales principales y dos por control negativo.",
 "",
 "Se ejecutaron 258.048.000 transiciones agente-ronda de entrenamiento; se registraron 55.296 trayectorias mundo-condición para evaluación de alimento y 165.888 pares contrafactuales mundo-persona, cada uno con dos brazos. Estas cifras describen el trabajo computacional y no multiplican el tamaño muestral efectivo de entrenamientos.",
 "",
 "## Conclusión",
 "",
 "[Inferencia] V23 demuestra que, bajo este modelo artificial específico, políticas privadas de contribución voluntaria y movilidad ocupacional pueden aprenderse conjuntamente desde pesos aleatorios y producir beneficios individuales causales en más de una inicialización. Quedan límites de dependencia de identidades, transferencia a redes reconectadas y escala de más profesiones. No se declara OBJETIVO COMPLETADO: la condición multiescala k=4/N=120 requiere superar nuevas pruebas.",
 "",
 "## Archivos para reproducción",
 "",
 "Entrenador v23_joint_cold.py; auditor causal v23_joint_audit.py; holdout v23_joint_holdout.py; logs y checkpoints conjuntos en runs/v23_*/; resultados originales en results/v23_joint_audit_*.json y results/v23_joint_holdout_*.json. Pruebas unitarias con test_v23_joint.py.",
 "",
 "Hashes SHA256:",
 *[f"{file}: {digest}" for file,digest in hashes.items()]]
(RES/"RESULTADOS_INTEGRALES_V23.md").write_text("\n".join(report),encoding="utf8")
print("V23_REPORT_OK",len(out),"mean food primary",round(np.mean([q["food"] for q in primary]),4),
      "mean return primary",round(np.mean([q["causal"] for q in primary]),4))
for q in primary:
 print("BOOTSTRAP",q["model"],[round(x,4) for x in uncertainty[q["model"]]["bootstrap_descriptive_95"]])
