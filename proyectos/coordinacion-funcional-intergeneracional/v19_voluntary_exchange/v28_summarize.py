"""V28 temporal donation profiles with within-env paired descriptive uncertainty."""
from pathlib import Path
import json,hashlib,csv
import numpy as np
ROOT=Path(__file__).resolve().parent
RES=ROOT/"results"
data=json.loads((RES/"v28_temporal_profiles.json").read_text("utf8"))
rows=[];uncertainty={}
for z in data["models"]:
 first=np.asarray(z["avg_first_8_seeds"])
 last=np.asarray(z["avg_last_8_seeds"])
 assert len(first)==len(last)==6
 diff=last-first
 rng=np.random.default_rng(282811)
 bootstrap=diff[rng.integers(0,6,(10000,6))].mean(1)
 uncertainty[z["model"]]=dict(diff_by_environment_seed=diff.tolist(),
      mean=float(diff.mean()),descriptive_bootstrap_95=np.quantile(bootstrap,[.025,.975]).tolist())
 row=dict(model=z["model"],kind=z["kind"],first_eight=z["first_eight"],
     last_eight=z["last_eight"],last_round=z["final_round"],
     delta=z["last_eight"]-z["first_eight"],
     ratio=z["ratio_last_to_first"],
     n_environment_seeds=6,worlds_per_seed=z["worlds_per_seed"])
 rows.append(row)
with (RES/"COMPARACION_V28.csv").open("w",encoding="utf8",newline="") as f:
 w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
(RES/"METRICAS_V28.json").write_text(json.dumps(dict(
    models=rows,uncertainty=uncertainty),indent=2),encoding="utf8")
def table(items,head):
 return "\n".join(["| "+" | ".join(head)+" |",
   "| "+" | ".join(["---"]*len(head))+" |"]
  +["| "+" | ".join(map(str,x))+" |" for x in items])
src=["v28_temporal_profiles.py","v28_summarize.py",
     "V28_FINITE_HORIZON_GAME_THEORY.md"]
hashes={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in src}
report=[
 "# V28. Cooperación observada y racionalidad secuencial en el horizonte finito",
 "",
 "Auditoría congelada de 12/11/2026. Se evaluaron cuatro checkpoints de coaprendizaje V23 N24/k2 y dos de entrega multiunidad V25 N48/k4 a precio 0,04. Seis semillas ambientales y 24 mundos por semilla, 48 rondas por mundo, misma política congelada en toda la trayectoria. Se registró por turno número de regalos enviados por individuo, alimentación y cobertura material. No se entrenó ningún modelo nuevo para esta ronda.",
 "",
 "## Perfil de contribuciones por período",
 "",
 table([[q["model"],q["kind"],f'{q["first_eight"]:.4f}',
   f'{q["last_eight"]:.4f}',f'{q["delta"]:+.4f}',
   f'{q["ratio"]:.3f}',f'{q["last_round"]:.4f}'] for q in rows],
   ["Política","Familia","Regalos t1–8","Regalos t41–48",
    "Diferencia","Ratio","Regalos turno 48"]),
 "",
 "La columna de regalos en V23 equivale a probabilidad de donar una vez (0–1); en V25 es número de regalos por persona (0–3). No comparar esas magnitudes sin considerar distinta capacidad. Los perfiles contienen tasas observadas, no retornos causales del último turno.",
 "",
 "## Proposición estratégica y sus supuestos",
 "",
 "En el último turno, donar reduce exactamente la comida propia en el coste unitario (0,12 en V23, 0,04 en V25), mientras los demás no pueden modificar sus regalos simultáneos en respuesta a la donación actual. No existe futuro dentro de la trayectoria, de modo que la donación no puede recuperar ese coste. Bajo racionalidad secuencial plena, conocimiento común del horizonte y ausencia de valor terminal/reputación interepisódica, este razonamiento se propaga hacia atrás. Una trayectoria sin donaciones ni cambios de oficio es un equilibrio perfecto en subjuegos; más detalles, premisas y demostración en V28_FINITE_HORIZON_GAME_THEORY.md.",
 "",
 "Las redes aprendidas V23 continúan donando en el último turno. La evidencia de cooperación conductual en el entrenamiento no es una prueba de que la política conjunta sea un equilibrio secuencialmente racional; precisamente las donaciones finales son una desviación de la elección óptima a un turno vista. V25 parece acercarse al régimen de no contribución conforme avanza la trayectoria, pero tenía ya regalos casi nulos, lo que limita la interpretabilidad de la disminución.",
 "",
 "## Implicación para rediseño de experimentos",
 "",
 "[Inferencia] Para investigar sostenibilidad estratégica más allá de convenciones finitas podría ser necesario un horizonte indeterminado, continuidad social entre episodios o activos de reputación con valor posterior. Estas intervenciones modifican el juego y deben probarse contra controles, no presumirse mejoras automáticas de capacidad de razonamiento.",
 "",
 "## Datos y reproducción",
 "",
 "JSON por ronda results/v28_temporal_profiles.json; seis semillas por modelo. Código de auditar v28_temporal_profiles.py, función de reporte v28_summarize.py. Contrastes entre segmentos calculados por bootstrap descriptivo agrupado por semilla ambiental, sin inflar n por mundos. Los pesos V23 y V25 permanecen en sus correspondientes runs/ ya versionados.",
 "",
 "SHA256 de archivos:",
 *[f"{name}: {digest}" for name,digest in hashes.items()]]
(RES/"RESULTADOS_INTEGRALES_V28.md").write_text("\n".join(report),encoding="utf8")
print("V28_REPORT_OK",len(rows))
