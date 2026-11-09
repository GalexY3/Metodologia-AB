# V15 — recuperación postlesión con estado de AdamW conservado frente a reiniciado

**9 de noviembre de 2026, registrado tras V14B y antes de V15.** V14B observó que reiniciar AdamW tras alcanzar 100% de precisión produce cambios sustanciales en robustez durante un entrenamiento adicional de 4000 pasos. Los pilotos de recuperación V10–V13 siempre usaron AdamW nuevo para ambos grupos. V15 pregunta si **conservar el estado adaptativo original** de AdamW durante la reparación altera la velocidad de recuperación y las diferencias entre historias.

## Modelos y exactitud computacional

Se parte de los cinco pares de V12, seeds 11,12,13,14,18, MLP 300 unidades ocultas, XOR de los primeros 3/30 bits y mismo split 20261110. Checkpoint elegido: step10000 después de 4000 pasos con L1 final común=.0001; todos train/val=100%. El checkpoint V12 step10000 contiene pesos pero NO estado del optimizador, así que no inventar momentos: **reconstruir exclusivamente el entrenamiento final desde checkpoint V12 step6000** (que sí contiene pesos), con un AdamW nuevo y λ=.0001 durante exactamente 4000 actualizaciones, guardando los momentos en step10000. Comparar tensor a tensor con V12 ck10000. Si la diferencia máxima de pesos >1e-6, **no usar ese checkpoint para el contraste** hasta investigar la divergencia; no ocultarla.

## Diseño de tratamiento tras lesión

Cada modelo verificado tiene dos ramas de reconstrucción desde **idénticos pesos** y misma lesión, misma función CE+L1=.0001 y 500 ejemplos train, LR=.001, wd=0, máximo 500 pasos y evaluación train/val cada10.

- **FRESH:** inicializar AdamW con momentos cero y contador cero.
- **RESUMED:** cargar exactamente el estado de AdamW que estaba activo al final del entrenamiento de L1 común en step10000; conservar momentos, contador y parametrización (sin desviaciones en LR, wd).

La única intervención intra-red es el estado del optimizador al comenzar el reaprendizaje. Controles intactos bajo cada modo, para medir déficit vs sus propias evoluciones no lesionadas. Máscaras nuevas, fijadas antes de probar: 4501,4502,4503,4504. Dosis predefinidas: 90/300 (30%), 180/300 (60%) y 270/300 (90%), obtenidas por prefijos anidados de una misma permutación. Dentro de cada pareja de redes, los mismos índices por dosis y máscara. 5 seeds ×2 historias ×2 modos de optimizador ×3 dosis ×4 máscaras = 240 reconstrucciones, más controles.

## Variables y análisis

- Daño funcional inicial: cae igual dentro de cada modelo al comparar FRESH y RESUMED, antes de actualizar parámetros; comprobarlo exactamente en la auditoría.
- Recuperación: primer paso con dos mediciones consecutivas de validación>=.99, censura si no ocurre antes de500.
- Déficit acumulado AUC = integral del acierto del control intacto menos del lesionado desde paso0 a500.
- Efecto causal computacional del optimizer state dentro del mismo modelo/máscara: AUC_FRESH−AUC_RESUMED, primero por máscara, después media por red, posteriormente por los cinco pares de semillas. **Mayor valor** significa que restaurar AdamW produjo menor déficit.
- Sensibilidad solo para lesión efectiva inicial>2pp en ambos modos y cuando los dos controles intactos conservan rendimiento; registrar fallos y censura.
- Comparar A y B separadamente bajo FRESH y RESUMED para ver si el resultado acerca/aleja grupos. Esta comparación entre historias sigue **confundida por L1 inicial distinta**; no atribuir grokking causal.
- Reportar en cada dosis el recuento de casos recuperados por modo y grupo, y la distribución por semilla. Múltiples dosis son exploratorias, n independiente sigue siendo cinco pares, no cientos de máscaras.
- Test no consultado para seleccionar ni recuperar; los 2000 casos de test V12 ya habían sido auditados previamente, pero no participan en V15.

Interpretación: V15 puede establecer un efecto del estado de AdamW sobre recuperabilidad **dentro de la misma red**, manteniendo pesos y lesión constantes. No demuestra que el estado de AdamW sea un sustituto de memoria social ni que el grokking cause el efecto observado.
