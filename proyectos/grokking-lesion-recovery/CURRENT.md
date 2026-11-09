# CURRENT — estudio sobre grokking, robustez y reconstrucción neuronal

**Fecha:** 2026-11-09. **Estado científico:** V10, V11 y réplica V12 completados, hallazgos exploratorios; no existe identificación causal del efecto propio del grokking ni demostración de equivalencia. **Segundo ordenador:** GALEXY_TRAVEL. **Rama de réplica:** research/grokking-lesion-v12-travel-20261109 en GalexY3/Metodologia-AB, carpeta proyectos/grokking-lesion-recovery. La rama original del sobremesa se conserva separada: research/grokking-lesion-v10-portable-20261109 (commit base 898bca86).

## Pregunta del investigador
Comparar modelos con la MISMA capacidad funcional final (100% sobre entrenamiento, validación y test finitos), alcanzada por historias diferentes: grokking tardío frente a aprendizaje más continuo, y probar si la resistencia y la recuperación tras eliminar neuronas internas difieren. No confundir mayor competencia con mayor reconstrucción, ni robustez inmediata con plasticidad funcional.

## Lo ejecutado y validado
- **V10B:** 5 parejas, red MLP de 300 neuronas, paridad3bits/30, 100% train/val/test, historia A L1=1e-5 tardía y B L1=.001 rápida, 150 ensayos de lesiones aleatorias. A fue inicialmente más resistente. Confusión directa por regularización histórica.
- **V10C:** 25 parejas de máscaras con 150/300 neuronas, daño inicial emparejado por criterio preestablecido antes de reparación, 50 curvas de reconstrucción. A favorable en 4/5 semillas, pero daños afectaron ejemplos distintos y se mantuvo confusor L1. Reporte en full_100/REPORT_V10C.md.
- **V11:** 5 pares tras 4000 actualizaciones con L1 común=.0001, 100% val. La brecha de resistencia A−B de −11.16 pp se redujo a −0.48 pp. Continuar sin L1 causó pérdida de generalización incluso sin lesión en algunos controles.
- **V11C:** 100 reconstrucciones, con L1=.0001 común mantenida, grupos elegibles. AUC de déficit A−B media −3.48, dirección heterogénea 2 de 5 favorable a A y 3 favorable a B, p exploratorio 0.6875. No se detectó ventaja regenerativa persistente reproducible (full_100/REPORT_V11.md).
- **V12 en GALEXY_TRAVEL:** partición nueva seed20261110, diez parejas iniciales semillas 10–19, cinco elegibles según historia y meseta (11,12,13,14,18); exclusiones registradas antes de lesiones. Todos los elegibles mantuvieron 100% train/val tras 4000 pasos de L1 común=.0001. Con 100 máscaras de 90/300 neuronas por modelo, la diferencia media de daño A−B pasó de **−10.378 pp a −0.961 pp**, replicando la convergencia. Los cambios A−B fueron positivos en las cinco parejas (p bilateral signflip exploratoria 0.0625).
- **V12B:** 100 reconstrucciones adicionales (5 pares × 2 condiciones × 10 máscaras nuevas de 90/300), 500 actualizaciones, L1 común=.0001 conservada en dañadas e intactas; controles intactos permanecen en 100% val. AUC media A 37.083, B 18.622; diferencia A−B +18.461, pero A favorable solo en 2/5 semillas y B en 3/5, p signflip=0.3125. El promedio desfavorable a A está fuertemente influido por semilla11, y no representa evidencia robusta de peor reconstrucción por grokking. Entre lesiones con daño >2pp se alcanzó umbral en A35/41 y B37/37, sin considerar máscaras independientes.
- **Test reservado V12:** se consultó una vez después de cerrar selección y análisis validación; las 20 evaluaciones de los checkpoints 6000 y10000, de ambos grupos en cinco parejas, conservaron 100% en 2000 casos de test. No se usó test para decidir selección de redes, máscaras, dosis o hiperparámetros.

## Conclusión defendible
**La ventaja inicial de resistencia a las lesiones asociada a las condiciones que producen grokking tardío se atenúa casi completamente cuando se comparte un periodo final de entrenamiento y regularización. No se ha encontrado una ventaja regenerativa persistente de signo consistente en dos cohortes de reconstrucción.** La robustez depende de la organización funcional presente, y la regularización L1 es una explicación causal rival fuerte. No se ha demostrado que el grokking cause o deje de causar resiliencia en sentido general; grupo B es aprendizaje rápido según criterio operativo, no ausencia demostrada de todas las transiciones internas.

## Lectura al reanudar
1. full_100/REPORT_V12.md (informe y gráficos integrados).
2. full_100/PREREG_V12.md y full_100/PREREG_V12B.md (protocolo antes de resultados).
3. full_100/V12_GATES.json, V12_ROBUSTNESS.json, V12B_ANALYSIS.json, V12_TEST_AUDIT.json.
4. full_100/REPORT_V11.md, full_100/REPORT_V10C.md y PRIOR_ART_20261109.md.
5. ARCHIVE_MANIFEST.json (inventario SHA-256, incluidos checkpoints nuevos y originales).

Las curvas y pesos V12 residen en full_100/v12_runs; las 100 reconstrucciones y controles están en full_100/v12b_repair. Los scripts V12 están en full_100/v12_*.py y el informe se genera con v12_make_report.py (las figuras son SVG generados sin librerías gráficas externas).

## Siguiente hipótesis y pruebas necesarias
Para identificar algo más próximo a un efecto causal de historia, diseñar un factorial que varíe independientemente el calendario de aprendizaje, la magnitud y cronología de L1, y la arquitectura/tarea, sin selección por test; introducir más semillas independientes y lesiones con severidad igualada ex ante. Medir márgenes, identidad de errores, redundancia, gradientes y tratamiento de neuronas sustitutas. Una réplica técnica en otro PC con las mismas semillas no sería replicación estadística; V12 sí incluyó semillas y datos nuevos, pero heredó hipótesis y tratamientos explorados previamente.

**Epistemología:** el estudio aún no acredita novedad científica, superioridad de un método AB, causalidad ni nivel CT2 validado. Preservar exclusiones, resultados negativos, confusores y datos crudos. La rama no debe fusionarse a main sin revisión.
