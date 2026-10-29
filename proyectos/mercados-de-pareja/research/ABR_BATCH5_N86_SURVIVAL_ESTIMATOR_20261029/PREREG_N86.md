# N86 · contrato de ingeniería A–J congelado: estimación de supervivencia bajo censura

Fecha 2026-10-29. Parent dac3c01c19e5b683131fa8b25f473a2b08c02cc3. El usuario autorizó N86–N87, manteniendo 19 plazas N88–N106 reservadas. **Es reparación de instrumento, NO nueva ciencia ni validación humana.** Código Python y tests se crean en este commit ANTES de ejecutar pruebas.

A. Pregunta: ¿podemos ofrecer una función reproducible que conserve eventos y censuras y devuelva RMST16, rechazando inputs inválidos, sin reescribir silenciosamente la fuente histórica ESBM v2?
B. Rivales: media completada actual (subgrupo de rupturas, estimando distinto) vs Kaplan–Meier discreto con censura y resultados analíticos exactos en cohortes pequeñas. No afirmar que las salidas históricas ya están arregladas.
C. Estimando: sum_{t=0..tau-1} S_hat(t), empleando hazard discreto de cada momento y ties resueltos con eventos antes de censuras en el mismo tick. No se estima E[D] ilimitada ni supervivencia real humana.
D. Diseño: pure stdlib Python, ficheros survival_metrics.py y test_survival_metrics.py congelados; nueve tests unittest nativos, valores esperados 2.75, 10/3, 4, 1 y 3, dos errores de entrada y uno por censura temprana y equivalencia de adaptador. Sin datos humanos, sin seeds o búsqueda de parámetros.
E. Freeze: guardar archivos y este A–J en GitHub antes de ejecutar unittest en container; SHA256 de cada archivo calculado en el runtime y comparado con bytes del blob GitHub original, no editar tras resultados.
F. Predicción: los nueve tests pasan; si falla alguno, INVALID con recibo, no declarar éxito; solo los tests ejecutados exactamente desde los bytes congelados cuentan.
G. Controles: comparación analítica de esperanza restringida, errores por códigos booleanos y evento a tau, censura completa y censor/event tie, conservación de cuenta de riesgos.
H. Transportabilidad: input futuro tiene que exportar cada duración observada con indicador evento/censura y tick de inicio. Los arrays internos de ESBM actual existen pero no se persisten en RUNS.json; **este ciclo NO ejecuta ni modifica esbm_dynamic.py**, no prueba clean clone del proyecto, no justifica censura no informativa ni recupera retrospectivamente tiempo de individuos solo de medias.
I. Novela: literatura Kaplan–Meier clásica. Mejora de ingeniería rastreable, no 1/3–3/3 científico; U135 en P-UNION-DURATION solo cuando tests ejecutados.
J. Dictamen: si el SHA del código en container coincide con GitHub congelado, y pasan los nueve tests con receipt, N86 válido técnico para su alcance 0/3, CT2=7 sin mejora y STOP_R5 externo. Si no, registrar INVALID sin reparar invisiblemente. N87 permanece disponible.
