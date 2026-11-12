"""Summarize V40 private/social incentive wedge, frozen-policy and paired evidence."""
from __future__ import annotations
import csv,json,hashlib
from pathlib import Path
import numpy as np
from v39_contract_outage import SOURCE_NAMES
ROOT=Path(__file__).resolve().parent
RES=ROOT/"results"
def load(p):return json.loads(p.read_text(encoding="utf8"))
def f(x):return f"{x:.4f}"
def plus(x):return f"{x:+.4f}"
def table(rows,heads):
 return "\n".join(["| "+" | ".join(heads)+" |",
   "| "+" | ".join(["---"]*len(heads))+" |"]+
    ["| "+" | ".join(map(str,r))+" |" for r in rows])
rows=[];seedwise={};evidence={}
for name in SOURCE_NAMES:
 z=load(RES/("v40_marginal_"+name+".json"))
 assert z["no_training"] and z["all_agents_forced"]
 assert z["seeds"] and len(z["seeds"])==len(z["rows"])==6
 assert all(v["seed"]==seed for seed,v in zip(z["seeds"],z["rows"]))
 assert all(v["n"] in (48,120) for v in z["rows"])
 def S(regime,k):
  return np.asarray([v["by_regime"][regime][k] for v in z["rows"]],dtype=float)
 private=S("unilateral","own_private")
 recipient=S("unilateral","targeted_recipient_gain")
 social=S("unilateral","net_social_total")
 contract_own=S("contract","own_private")
 # Conservation: one person pays cost, only the intended neighbor can gain.
 assert np.allclose(private,-z["rows"][0]["cost"],atol=2e-5)
 assert np.allclose(social,private+recipient,atol=2e-5)
 rng=np.random.default_rng(40112026)
 def ci(x):
  samp=x[rng.integers(0,len(x),(10000,len(x)))].mean(1)
  return np.quantile(samp,[.025,.975]).tolist()
 n=z["rows"][0]["n"]
 def byagent(regime,key):
  q=np.asarray([r["by_regime"][regime][key] for r in z["rows"]])
  assert q.shape==(6,n)
  return q.mean(0)
 marg=byagent("unilateral","social_agent_means")
 cov=byagent("unilateral","recipients_positive_per_agent")
 r=dict(model=name,n=n,cost=z["rows"][0]["cost"],
   unit_cost_paid_unilateral=float(private.mean()),
   recipient_gain_unilateral=float(recipient.mean()),
   total_social_gain_unilateral=float(social.mean()),
   social_gain_ci025=float(ci(social)[0]),
   social_gain_ci975=float(ci(social)[1]),
   positive_society_marginal_share=float((marg>0).mean()),
   useful_fraction_unilateral=float(S("unilateral","useful_fraction").mean()),
   private_gain_conditional=float(contract_own.mean()),
   private_contract_ci025=float(ci(contract_own)[0]),
   private_contract_ci975=float(ci(contract_own)[1]),
   social_gain_conditional=float(S("contract","net_social_total").mean()),
   useful_fraction_conditional=float(S("contract","useful_fraction").mean()),
   positive_private_contract_agents=int((byagent("contract","private_agent_means")>0).sum()),
   fraction_agents_with_useful_unilateral_gift=float((cov>.0).mean()),
   worlds_per_environment=z["worlds"],
   env_seeds=len(z["rows"]))
 rows.append(r)
 seedwise[name]=dict(unilateral_private=private.tolist(),
   unilateral_recipient=recipient.tolist(),
   unilateral_social=social.tolist(),
   contract_private=contract_own.tolist())
 evidence[name]=dict(per_agent_unilateral_social=marg.tolist(),
   per_agent_usefulness=cov.tolist())
with (RES/"COMPARACION_V40.csv").open("w",newline="",encoding="utf8") as fw:
 writer=csv.DictWriter(fw,list(rows[0]));writer.writeheader();writer.writerows(rows)
h40=dict(
 h40a_all_exact_own_cost=all(abs(x["unit_cost_paid_unilateral"]+x["cost"])<2e-5 for x in rows),
 h40b_positive_social_low_cost=sum(x["total_social_gain_unilateral"]>0
    for x in rows if x["cost"]==.04)>=3,
 h40c_nonpositive_social_high_cost=any(x["total_social_gain_unilateral"]<=0
    for x in rows if x["cost"]==.12),
 h40d_positive_contract_private=sum(x["private_gain_conditional"]>=0 for x in rows)>=4)
paths=("PREREG_V40_INDIVIDUAL_SOCIAL_WEDGE.md",
  "v40_marginal_wedge.py","v40_summarize.py","test_v40_wedge.py")
hashes={k:hashlib.sha256((ROOT/k).read_bytes()).hexdigest() for k in paths}
(RES/"METRICAS_V40.json").write_text(json.dumps(dict(
  rows=rows,criteria=h40,per_environment=seedwise,by_agent=evidence,
  n_models=6,env_seeds_per_model=6,
  number_of_world_individual_counterfactual_pairs=sum(
    x["n"]*x["worlds_per_environment"]*x["env_seeds"] for x in rows),
  limitations="Immediate one offer at t25 only, pretrained policies; not a one-stage equilibrium or long-term learning.",
  sha256=hashes),indent=2),encoding="utf8")
report=[
 "# V40. Brecha causal entre el beneficio alimentario privado y social de una oferta",
 "",
 "Auditoría preregistrada después de los resultados V39, ejecutada con seis checkpoints contractuales finales V30/V31, cuatro profesiones y N48 o N120, dos precios c0,04 y c0,12, seis semillas ambientales reservadas por checkpoint y 8–12 mundos por semilla. Se congelaron todas las redes privadas. Las decisiones de ocupación y ofertas se simularon normalmente durante 24 rondas, y en la ronda25 se impuso para cada persona individualmente la primera oferta de regalo frente a su prohibición, manteniendo iguales las demás propuestas y ocupaciones. Las dos reglas de liquidación comparadas son contratos recíprocos bilaterales y regalos unilaterales.",
 "",
 "## Efectos materiales marginales, por propuesta dirigida",
 "",
 table([[r["model"],str(r["cost"]),plus(r["unit_cost_paid_unilateral"]),
    plus(r["recipient_gain_unilateral"]),plus(r["total_social_gain_unilateral"]),
    f'{r["useful_fraction_unilateral"]:.1%}',
    plus(r["private_gain_conditional"]),
    f'{r["positive_private_contract_agents"]}/{r["n"]}'] for r in rows],
   ["Modelo","Coste","Cambio privado unilateral",
    "Beneficio a receptor","Beneficio social neto",
    "Ofertas unilat. útiles","Cambio privado contractual",
    "Personas privadas positivas con contrato"]),
 "",
 "La utilidad privada de una donación unilateral forzada es exactamente −c en el turno intervenido. El beneficio del destinatario depende de si aporta un tipo profesional que faltaba; el beneficio social neto inmediato es igual al beneficio recibido por ese destinatario menos c, en unidades de alimento total. El test de conservación confirma que no hay efectos inmediatos sobre terceros distintos del destinatario. Una oferta contractual puede no ejecutarse si falta contrapropuesta, y si se ejecuta ambas partes intercambian un bien; por tanto, el cambio privado del donante puede ser positivo al mismo tiempo que paga su unidad.",
 "",
 "El resultado de intervención es **local y marginal**. No puede explicar automáticamente la diferencia agregada V39 entre ejecutar de golpe todas las propuestas bajo ambos regímenes, porque el beneficio por unidad puede depender de la redundancia, de otras ofertas simultáneas y de qué vecinos ya estén satisfechos. V40 tampoco simula la adaptación de los agentes después de cambiar las reglas de liquidación; esa cuestión corresponde a entrenamientos de un juego distinto.",
 "",
 "## Hipótesis preregistradas y falsaciones",
 "",
 table([[h,'cumple' if verdict else 'no cumple'] for h,verdict in h40.items()],
   ["Hipótesis","Resultado"]),
 "",
 "H40a exige identidad mecánica del coste privado; H40b requiere beneficio social inmediato marginal positivo en ≥3/4 de los modelos de coste0,04; H40c espera neto marginal social no positivo en al menos uno de los dos modelos de coste0,12; H40d espera retorno privado inmediato contractual medio no negativo en ≥4/6 checkpoints. Las hipótesis se concibieron tras observar V39, por lo que son contrastes exploratorios preregistrados antes de V40, no replicaciones ciegas.",
 "",
 "## Incertidumbre y alcance",
 "",
 "Seis ambientes reservados por modelo, 8 o12 mundos por ambiente, intervención independiente sobre cada persona. La persona es unidad de tratamiento en un mundo simulado, pero la inferencia sobre políticas neuronales debe considerar que solo hay seis entrenamientos distintos y algunos son pares de la misma semilla a tamaños diferentes. Los intervalos bootstrap descriptivos agrupados por semilla ambiental se guardan en METRICAS_V40.json. No convertir el número de intervenciones en el número de redes entrenadas.",
 "",
 "[Inferencia] La brecha entre ganancia material de terceros e incentivo marginal propio ayuda a separar eficacia técnica potencial y estabilidad estratégica. Una regla contractual puede operar como mecanismo de apropiación simultánea de beneficios, aunque la entrega de todas las propuestas bajo una norma unilateral genere mayor alimento agregado a bajo precio. Esto no demuestra surgimiento endógeno de instituciones ni reciprocidad diferida sostenible.",
 "",
 "## Reproducibilidad",
 "",
 "Preregistro PREREG_V40_INDIVIDUAL_SOCIAL_WEDGE.md, código v40_marginal_wedge.py, pruebas test_v40_wedge.py, resultados originales results/v40_marginal_v30_*.json y results/v40_marginal_v31_*.json, resumen COMPARACION_V40.csv y METRICAS_V40.json. SHA256:",
 *[f'{key}: {value}' for key,value in hashes.items()]]
(RES/"RESULTADOS_INTEGRALES_V40.md").write_text("\n".join(report),encoding="utf8")
print("V40_REPORT_OK",len(rows),h40)
for r in rows:
 print(r["model"],"private",round(r["unit_cost_paid_unilateral"],4),
    "recipient",round(r["recipient_gain_unilateral"],4),
    "social",round(r["total_social_gain_unilateral"],4),
    "contractprivate",round(r["private_gain_conditional"],4))
