# CURRENT — grokking y reparación tras lesión neuronal (portátil)

**Fecha de captura:** 2026-11-09. **Estado:** V10B y V10C completados y auditados localmente; ambas evaluaciones son **exploratorias, no confirmatorias**.

**Autoridad del investigador:** comparar redes con 100% de precisión (en conjuntos observados), una con generalización tardía grokking y otra con generalización más continua, para medir su robustez ante eliminación permanente de unidades y su capacidad **condicional** de recuperación cuando ambas sufren daño funcional equivalente. Igual accuracy global no implica mismos circuitos.

**Empieza por** `README.md`, `full_100/PREREG_V10B.md`, `full_100/V10_ELIGIBILITY.json`, `full_100/V10_ANALYSIS.json`, `full_100/PREREG_V10C.md`, `full_100/REPORT_V10C.md`, `full_100/V10C_MATCHED_ANALYSIS.json`, `ARCHIVE_MANIFEST.json`.

**V10B:** cinco pares de redes (MLP 300 neuronas; 30 bits con paridad en 3) llegan a 100% train/val/test en los datos evaluados al paso 8000. Grupo A regularización L1 λ=1e-5, generalización tardía; grupo B L1 λ=.001, adquisición más rápida. 150 pruebas de lesión en 30, 90, 150 neuronas, con máscaras emparejadas. Grupo A fue más robusto a igual número de neuronas eliminadas. No es demostración de recuperación más rápida porque pierde menos precisión inicialmente.

**V10C:** análisis de sensibilidad posterior al V10B, con máscaras nuevas 1001..2000, selección de las primeras cinco por par de redes que causan entre 10 y 40pp de daño en ambos y difieren <=5pp, elegidas **antes de observar recuperación**. 25 pares de máscaras, 50 lesiones de 150/300 unidades. Promedio de pérdida inicial de validación A=23,808pp, B=23,768pp. Déficit acumulado de validación A−B medio por semilla = −8,614 unidades precisión×paso, favorable a A en 4 de 5 semillas, una favorable a B. Recuperaciones observadas a >=99% durante 400 pasos A=22/25, B=17/25. **Solo n=5 pares de redes independientes**; máscaras son repeticiones anidadas. Superposición de ejemplos erróneos entre brazos, Jaccard medio=0,183: equiparar caída de accuracy NO iguala tipo de daño. L1 distinta confunde cualquier inferencia causal sobre grokking.

**Dictamen actual:** asociación exploratoria entre historia + régimen L1 y robustez/recuperabilidad, sin causalidad aislada del grokking. No se ha demostrado novedad publicable, superioridad metodológica AB ni un mecanismo universal. Se conserva resultado V10B de perturbación física aleatoria y V10C de emparejamiento por severidad; ninguno sustituye al otro.

**Siguiente trabajo:** diseño factorial que desacople tipo de historia de L1, grupo con aprendizaje continuo auténtico, semillas nuevas y partición de datos reservada, múltiples tareas/arquitecturas, análisis de tipos de error y daño por pérdidas/márgenes, lesionado vs continuo, estudio de mecanismos internos. Registrar negativos y controles adversariales.

**Ruta original sobremesa:** `C:\Programación\grokking_lesion_20261109`. **Github:** `GalexY3/Metodologia-AB`, rama `research/grokking-lesion-v10-portable-20261109`, carpeta `proyectos/grokking-lesion-recovery/`. El snapshot excluye checkpoints intermedios redundantes y contiene checkpoints finales V7/V9/V10, curvas, datos, código y su manifiesto con hashes.
