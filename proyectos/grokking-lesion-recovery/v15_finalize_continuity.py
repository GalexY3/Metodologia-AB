"""Finalize continuity after V15 corrected-run audit PASS; never modify raw data."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
D=ROOT/"full_100"
e=json.loads((D/"V15_ANALYSIS.json").read_text(encoding="utf-8"))
assert e["audit"]["status"]=="PASS" and e["audit"]["n_runs"]==240
body=(ROOT/"CURRENT.md").read_text(encoding="utf-8")
body=body.replace(
"**Estado:** completados V10–V14B, incluyendo nuevo barrido de dosis V13 y control del optimizador V14B. V15 aún **no ejecutado** en el momento de este corte;",
"**Estado:** completados V10–V15, incluyendo nuevo barrido de dosis V13, control del optimizador V14B y comparación de recuperación V15 corregida y auditada;")
start="## Próximo paso V15, ya registrado y pendiente"
end="## Reanudación y GitHub"
a=body.index(start)
b=body.index(end,a)
replacement="""## V15 finalizado: optimizador conservado frente a reiniciado durante la reparación

Se reconstruyeron los diez checkpoints V12 con **diferencia máxima de pesos de 0,0** y el estado real de AdamW. La primera ejecución de V15 se invalidó por memoria compartida entre los tensores de momentos de AdamW y se aisló en una carpeta local de cuarentena, fuera de Git. La prueba de regresión comprobó **12/12 alias en carga directa y 0/12 tras copia profunda**. La ejecución válida se repitió desde cero con nuevo código y auditó **240/240 lesiones PASS**, máscaras y daños iniciales iguales. Ver full_100/V15_ALIAS_ERRATUM.md, REPORT_V15.md y V15_ANALYSIS.json.

AUC de déficit de validación **nuevo/restaurado** a dosis 30%: A 35,6/35,3 y B 25,2/17,7; a 60%: A 86,8/92,9 y B 83,4/76,8; a 90%: A 214,7/234,9 y B 179,3/192,0. A dosis 90%, el AdamW reiniciado tuvo menor AUC en ambos grupos, mientras el estado conservado favoreció B a dosis menores. El efecto del optimizador no es uniforme, pero se identifica *dentro de la misma red y lesión*. La comparación entre historias sigue sin identificar causalidad aislada del grokking, por confusión con L1 de adquisición.

**Cierre del objetivo neuronal del usuario:** se obtuvo una curva de dosis 10–90%, una extensión de 90% a 2000 pasos, un control factorial de L1 y tiempo (V14), el efecto de reiniciar AdamW en robustez (V14B), y el de reiniciarlo en recuperación de las mismas lesiones (V15). Los resultados son claros respecto a que la recuperabilidad varía con dosis, identidad funcional y procedimiento de optimización; **no se acreditó una ventaja general ni una desventaja general causada por grokking**. Las limitaciones n=5, una sola tarea y arquitectura, y L1 histórica distinta permanecen. No prolongar automáticamente el estudio con infinitas pruebas posthoc; siguiente reto: nueva cohorte/tarea, si se solicita.

**Siguiente tarea en cola conforme al orden del usuario:** iniciar el programa separado en ../coordinacion-funcional-intergeneracional/QUEUE.md, con agentes que equilibran 1/k funciones usando comunicación local, entrenamiento k<=4, pruebas zero-shot k>4 y relevo generacional. Se han preparado criterios metodológicos pero **no se han ejecutado experimentos sociales** al cerrar esta etapa.

"""
body=body[:a]+replacement+body[b:]
body=body.replace("3. Ejecutar V15; analizar y registrar resultados positivos y negativos; versionarlos en rama. Utilizar Python de",
"3. V15 corregido y auditado; consultar REPORT_V15.md y V15_ALIAS_ERRATUM.md. Utilizar Python de")
(ROOT/"CURRENT.md").write_text(body.replace("\r\n","\n"),encoding="utf-8")
readme=ROOT/"README.md"
r=readme.read_text(encoding="utf-8")
r=r.replace(
"**En el momento\nde esta actualización aún no está ejecutado.**",
"**V15 completado y auditado con 240 reconstrucciones.** Leer [REPORT_V15.md](full_100/REPORT_V15.md), [V15_ANALYSIS.json](full_100/V15_ANALYSIS.json) y [V15_ALIAS_ERRATUM.md](full_100/V15_ALIAS_ERRATUM.md).")
if "## V15 — reparación y estado de AdamW" not in r:
 r += """
## V15 — reparación y estado de AdamW

**V15 completado y auditado (PASS, 240 reconstrucciones desde pesos idénticos)**.
Leer el [informe V15](full_100/REPORT_V15.md), los [resultados](full_100/V15_ANALYSIS.json)
y la [errata de integridad](full_100/V15_ALIAS_ERRATUM.md).

Se invalidó una primera ejecución debido a memoria compartida entre estados
AdamW; sus datos fueron aislados fuera del repositorio. La repetición corrigió
el alias con copia profunda, comprobó cero punteros compartidos, y preservó
exactamente el mismo daño inicial entre brazos de optimizador.
La recuperación mostró efectos del estado de AdamW que varían según la dosis:
restaurar momentos no siempre mejora, especialmente ante 90% de destrucción.
El estudio no identifica causalmente un efecto exclusivo del grokking.

**El siguiente proyecto autorizado por el usuario está en cola**:
[coordinacion-funcional-intergeneracional/QUEUE.md](../coordinacion-funcional-intergeneracional/QUEUE.md).
"""
readme.write_text(r.replace("\r\n","\n"),encoding="utf-8")
print("CONTINUITY_V15_FINALIZED",len(body),len(r),flush=True)
