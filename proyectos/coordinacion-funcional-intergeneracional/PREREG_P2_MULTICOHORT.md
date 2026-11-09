# P2 — réplica de la generalización en múltiples cohortes entrenadas

**Registro prospectivo previo a ejecutar P2 en GALEXY_TRAVEL (9/11/2026).** P0/P1 en DESKTOP-I4SULKD mostraron 0/10 de estabilidad de P0 en cada k5..8, frente a 10/10,6/10,3/10,1/10 con P1 al cambiar una sola característica de rareza local. Esos resultados solo implicaban una cohorte de entrenamiento por modelo. P2 busca una réplica verdaderamente independiente entre **seis cohortes de entrenamiento**, con parámetros congelados, y un estrés extrapolativo adicional k9..12.

## Hipótesis y diseño

H1: representar la escasez de función local como **−k·f_local** (P1) en vez de **−f_local** (P0) reduce la distancia TV al equilibrio en valores de k nunca usados al entrenar, cuando ambos grupos reciben el MISMO procedimiento de aprendizaje. Contraste primario: **diferencia pareada media (TV_P0−TV_P1)**, primero promedio sobre cinco episodios de prueba por k, después sobre k5..8 para cada cohorte, y finalmente promedio de las seis cohortes como unidades independientes. Mayor que cero favorece la variante P1. Efecto secundario: tasa de estabilidad estricta.

H2 exploratoria: bajo k9,10,11,12 (más lejano al entrenamiento 2..4), la ventaja de TV podría persistir aunque la frecuencia absoluta de equilibrio estable decline por restricción informativa/geométrica. No cambiar el criterio en función del rendimiento observado.

## Conjunto fijado

- Entrenamientos independientes (semillas de cohorte): **20261120, 20261121, 20261122, 20261123, 20261124, 20261125**, seis cohortes; para cada una, P0 y P1 reciben **exactamente los mismos episodios de entrenamiento y semillas**. k=2,3,4 con ocho episodios por k, 120 ticks/episodio, 24 episodios por cohorte y método. N=120, cuatro vecinos anulares, máximo una comunicación por agente/tick.
- Misma recompensa basada en rareza local y coste de cambio, mismo vector θ inicial, mismo REINFORCE, mismas condiciones temporales y memoria local. La **única diferencia P0/P1** es multiplicación de la característica de rareza por k.
- Episodios de evaluación se fijan antes de entrenar: por cohorte i=0..5, función k=5..12 y réplica s=0..4, semilla = **230000 + 5000i +100k + s**. Cada brazo P0/P1 recibe exactamente la misma semilla de emparejamientos y colores; evaluación durante **140 ticks**, sin actualizar θ en test (memoria de observaciones puede actualizarse y se etiqueta como inferencia contextual). Total: seis cohortes × ocho k × cinco réplicas × dos brazos = **480 episodios test**, más 288 episodios de entrenamiento entre ambos métodos.
- k5..8 son *nuevos episodios/semillas*, pero los valores k ya se exploraron en P0/P1. P2 es **réplica independiente entre entrenamientos**, NO otro test virgen de la dimensión k misma. k9..12 sí son nuevos niveles de dificultad no abiertos antes de P2.

## Resultados y censos

Episodio: TV de variación total global en los últimos 10 ticks; churn promedio últimos 10; diversidad local ego+vecinos; estabilidad = TV≤0,06 y churn≤0,05 durante diez ticks finales. Los agentes nunca observan TV, solo el evaluador después de decisiones. Informar todas las semillas por cohorte y por k; ninguna selección adaptativa de grupos/sesiones. Distancias TV continuas son el criterio primario, para no depender solo del umbral arbitrario 0,06. Comparar diferencias emparejadas por cohorte/k y además agregadas sobre k5..8.

Prueba exploratoria de inversión de signos bilateral por **seis cohortes** sobre su diferencia media primaria, con mínimo p alcanzable 2/64=0,03125; no sustituye inferencia general a arquitecturas. Intervalo descriptivo de diferencias por cohorte. k9..12 secundarios y sujetos a multiplicidad.

## Integridad y replicabilidad

La rama de replica parte de commit f4293a4c del estudio P0/P1/G0; NO cambiar model.py, model_p1.py, sus parámetros ni su lógica tras fijar este preregistro. Ejecutar tests de invariantes antes del entrenamiento. Hacer un test-lock JSON con los hashes SHA-256 de código e instrucciones ANTES de abrir resultados test; permitir registrar checkpoint/curvas por cohorte con prevención de sobrescrituras. No mirar k5..12 al seleccionar modelos: se usarán todos los seis entrenamientos y se informarán todos los resultados.

Un éxito de P1 indica que una característica construida por el investigador facilita aprendizaje de una política **invariante al número de opciones**. Esto no demuestra emergencia de normas colectivas autónomas, grokking tardío, ni validez observacional humana. Los seis entrenamientos son independientes, pero todos comparten el mismo generador de simulación, topología y mecanismo diseñado.
