"""V42: show that reciprocal cooperation is an available self-enforcing
strategy in an uncertain-horizon unilateral giving game, under an EXPLICIT
grim-trigger oracle. This is NOT learned emergence or an enforced contract.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from pathlib import Path
import numpy as np,torch
from targeted_gifts import C
from v24_k4_joint import start4
from v25_multi_capacity import step_multi

ROOT=Path(__file__).resolve().parent;OUT=ROOT/"results"
B=.20
V=.55/3.
GAMMA=.995
Q=(.0,.15,.20,.25,.40,.50,.60,.75,.80,.95,.98)
COSTS=(.04,.12)

def material_verification(cost):
 """Pairs are (0,1), (2,3)... (46,47) with different professions."""
 c=C(n=48,k=4,degree=6,topology="ring",batch=8,horizon=48,
     cost=cost,device="cpu")
 def start():return start4(c,42112026,"balanced")
 n=torch.arange(48)
 target=(n^1).view(1,48,1).expand(8,-1,3).clone()
 yes=torch.zeros(8,48,3);yes[:,:,0]=1.
 world=start()
 ownroles=world["roles"]
 partners=ownroles[:,n^1]
 assert bool((ownroles!=partners).all())
 full,_=step_multi(c,world,target,yes)
 expected=B+V-cost
 assert torch.allclose(full,torch.full_like(full,expected),atol=1e-6)
 altered=yes.clone()
 altered[:,0,0]=0.
 world_no=start()
 defect,_=step_multi(c,world_no,target,altered)
 delta=defect-full
 assert torch.allclose(delta[:,0],torch.full_like(delta[:,0],cost),atol=1e-6)
 assert torch.allclose(delta[:,1],torch.full_like(delta[:,1],-V),atol=1e-6)
 assert torch.allclose(delta[:,2:],torch.zeros_like(delta[:,2:]),atol=1e-6)
 return dict(cost=cost,n=48,k=4,degree=6,pairs=24,
  extra_private_gain_from_defection=float(delta[:,0].mean()),
  loss_of_one_reciprocal_recipient=float(delta[:,1].mean()),
  cooperative_one_round_food=float(full.mean()),
  analytical_cooperative_food=expected,
  no_other_bystanders_affected=True)

def analytical_delta(cost,q,gamma=GAMMA,value=V):
 beta=gamma*q
 assert 0<=beta<1
 return (beta*value-cost)/(1-beta)

def mc_one(cost,q,samples,seed,gamma=GAMMA,value=V):
 rng=np.random.default_rng(seed)
 length=np.ones(samples,dtype=np.int64) if q==0 else rng.geometric(1-q,samples)
 discounted_sum=(1-np.power(gamma,length))/(1-gamma)
 differences=(value-cost)*discounted_sum-value
 expected=analytical_delta(cost,q,gamma,value)
 mean=float(differences.mean())
 std=float(differences.std(ddof=1))
 se=std/math.sqrt(samples)
 agree=abs(mean-expected)<=max(4*se,1e-9)
 return dict(cost=cost,continuation_probability=q,
   actual_mean=mean,analytical_mean=expected,monte_carlo_std=std,
   se=se,abs_error=abs(mean-expected),
   within_4se=agree,n=samples,
   sign_prediction=bool(expected>0),
   sign_estimated=bool(mean>0),
   mean_lifetime=float(length.mean()),
   seed=seed)

def table(rows,heads):
 return "\n".join(["| "+" | ".join(heads)+" |",
 "| "+" | ".join(["---"]*len(heads))+" |"]+
 ["| "+" | ".join(map(str,r))+" |" for r in rows])

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--samples",type=int,default=200000)
 p.add_argument("--seed",type=int,default=42112026)
 a=p.parse_args()
 assert a.samples>=500
 torch.set_num_threads(2)
 mechanics=[material_verification(cost) for cost in COSTS]
 records=[]
 for cost in COSTS:
  for q in Q:
   data=mc_one(cost,q,a.samples,a.seed+int(cost*1000)*1000+int(q*1000))
   records.append(data)
   print("V42",cost,q,"analytical",round(data["analytical_mean"],4),
      "MC",round(data["actual_mean"],4),
      "4SE_PASS",data["within_4se"],flush=True)
 qcrit={str(cost):cost/(GAMMA*V) for cost in COSTS}
 def sign(cost,q):return analytical_delta(cost,q)>0
 checks=dict(
  h42a_material_mechanics=all(m["no_other_bystanders_affected"] for m in mechanics),
  h42b_threshold_signs=(
   not sign(.04,.20) and sign(.04,.25)
   and not sign(.12,.60) and sign(.12,.75)),
  h42c_monte_carlo_4se_all=all(x["within_4se"] for x in records),
  h42d_profitable_indefinite_pair_both_costs=sign(.04,.80) and sign(.12,.80))
 assert all(checks.values()),checks
 with (OUT/"COMPARACION_V42.csv").open("w",newline="",encoding="utf8") as f:
  w=csv.DictWriter(f,list(records[0]));w.writeheader();w.writerows(records)
 hashes={x:hashlib.sha256((ROOT/x).read_bytes()).hexdigest() for x in
  ("PREREG_V42_SHADOW_OF_FUTURE.md","v42_shadow_future.py","test_v42_shadow_future.py")}
 (OUT/"METRICAS_V42.json").write_text(json.dumps(dict(
   b=B,v=V,gamma=GAMMA,
   mechanical_payoffs=mechanics,random_horizon_monte_carlo=records,
   thresholds=qcrit,hypotheses=checks,source_sha256=hashes,
   methodological_caveat="The conditional grim-trigger policy is supplied as an oracle. This proves feasibility, not endogenous learning or equilibrium of the entire k4 world."),indent=2),encoding="utf8")
 result=[
 "# V42 — Factibilidad estratégica de reciprocidad sin liquidación contractual",
 "",
 "Simulación preregistrada el 13/11/2026 sobre el componente diádico de la economía de cuatro profesiones con N48/k4. Se construyeron 24 parejas disjuntas de oficios complementarios (i, i XOR1), con los mismos pagos materiales y topología del simulador. Se verifica primero el código físico original que permite entregar un producto pagando el coste c, sin condicionar ni impedir la donación del otro participante. **La norma de reciprocidad contingente grim-trigger está introducida como oráculo hipotético, no fue aprendida por las redes neuronales**.",
 "",
 "## Mecánica de un único regalo recíproco",
 "",
 table([[str(x["cost"]),
   f'{x["cooperative_one_round_food"]:.4f}',
   f'{x["extra_private_gain_from_defection"]:+.4f}',
   f'{x["loss_of_one_reciprocal_recipient"]:+.4f}'] for x in mechanics],
 ["Coste","Alimento por persona cooperando","Ahorro privado si defrauda",
  "Pérdida del vecino que no recibe"]),
 "",
 "En un par, recibir una especialidad que falta aporta exactamente v=0,55/3≈0,18333 unidades por turno. Si ambos donan, cada persona obtiene b+v−c; si una persona incumple mientras la otra dona, el desertor se ahorra c y su contraparte pierde v. El resto de las46 personas conserva exactamente el mismo alimento. Esto valida la posibilidad material sin contratos.",
 "",
 "## Continuidad incierta y equilibrio condicional de la pareja",
 "",
 "La norma hipotética se mantiene mientras ambos se hayan ayudado siempre y se interrumpe definitivamente si uno incumple. Con vida de continuación geométrica q y descuento temporal gamma0,995, el cálculo de la ganancia descontada de seguir cooperando frente a desertar una sola vez es (gamma·q·v−c)/(1−gamma·q). La condición de incentivos es gamma·q·v ≥ c.",
 "",
 f"**Umbral de continuidad a coste0,04:** q ≥ {qcrit[str(.04)]:.4f}. **A coste0,12:** q ≥ {qcrit[str(.12)]:.4f}.",
 "",
 "## Validación Monte Carlo del valor presente, con duración aleatoria",
 "",
 table([[str(x["cost"]),str(x["continuation_probability"]),
   f'{x["analytical_mean"]:+.4f}',f'{x["actual_mean"]:+.4f}',
   f'{x["se"]:.5f}',"sí" if x["within_4se"] else "no"]
   for x in records],
 ["Coste","Prob. continuidad","Ventaja analítica cooperación",
  "Ventaja simulada","Error estándar","Dentro 4 SE"]),
 "",
 "Los valores simulados proceden de duraciones geométricas exógenas, con al menos200.000 episodios independientes por punto y semilla fija. Las incertidumbres aquí provienen del muestreo de duraciones del oráculo matemático, no de variación entre entrenamientos neuronales: los modelos no fueron entrenados. El signo de la ganancia es **propiedad de una pareja que ya sabe aplicar esta norma** y no implica que la norma surja espontáneamente.",
 "",
 "## Hipótesis",
 "",
 table([[k,"cumple" if v else "no cumple"] for k,v in checks.items()],
 ["Prueba preregistrada","Resultado"]),
 "",
 "## Significado sociológico y limitaciones",
 "",
 "[Inferencia] El juego material permite estrategias de reciprocidad condicional con incentivos positivos cuando existe suficiente continuidad futura; en la misma economía los agentes de V41 abandonaron la ayuda unilateral tras aprender, incluso teniendo buenas oportunidades colectivas de intercambio. Esto sugiere que conviene investigar la capacidad de descubrir y estabilizar convenciones de castigo o recompensa en relaciones de duración incierta, antes de aumentar simplemente el tamaño de las redes.",
 "",
 "No se infiere que el juego completo de cuatro profesiones tenga equilibrio único o que la duración incierta baste para aprender cooperación; la deducción se limita al subsistema aislado de parejas complementarias y su norma oracular. En un horizonte finito y conocido, la deserción puede propagarse hacia atrás bajo hipótesis de racionalidad e información propias de juegos repetidos con equilibrio único de etapa, pero no se ha demostrado ese razonamiento para el sistema MARL completo.",
 "",
 "## Reproducción",
 "",
 "Preregistro PREREG_V42_SHADOW_OF_FUTURE.md, evaluador v42_shadow_future.py, casos mecánicos en test_v42_shadow_future.py, CSV y METRICAS_V42.json con semillas y desviaciones. SHA256:",
 *[f'{k}: {v}' for k,v in hashes.items()]]
 (OUT/"RESULTADOS_INTEGRALES_V42.md").write_text("\n".join(result),encoding="utf8")
 print("V42_REPORT_OK",len(records),"thresholds",qcrit,"checks",checks)
if __name__=="__main__":main()
