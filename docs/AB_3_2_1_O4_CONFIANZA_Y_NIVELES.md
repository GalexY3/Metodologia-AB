# AB 3.2.1-O4 — Confianza de trayectoria 2/3 y contabilidad 0–3

**Adopción solicitada:** 24 de octubre de 2026. Anexo a AB 3.2.1/O1/O2/O3. Es un instrumento de decisión, no una escala validada empíricamente. No sustitute al dictamen multidimensional I ni a las puertas de novedad.

## A. Escala CT2 (1–100)
Pregunta operacional: «Dado el estado de la evidencia, las alternativas publicadas, el acceso a instrumentos y la ruta verificable siguiente, ¿cuánta confianza tengo en que prolongar esta línea específica conduzca a un descubrimiento defendible **2/3**?».

- **1–10:** palos de ciego, sin mecanismo ni predicción distintiva.
- **11–25:** pregunta identificada pero antecedentes fuertes, escaso acceso a evidencia nueva o controles.
- **26–45:** mecanismo discriminable y experimentos claros; independencia o singularidad científica inciertas.
- **46–65:** resultados propios positivos ante controles, adversarios fuertes pendientes o nueva fuente sin verificar.
- **66–85:** aportación posiblemente original, evidencias y controles fuertes reproducidos; falta replicación externa o prioridad documental.
- **86–99:** reivindicación específica altamente plausible, casi todo verificado salvo confirmación crítica delimitada.
- **100:** la trayectoria hacia 2/3 parece completamente especificada; **solo resta ejecutar/verificar una comprobación delimitada**, no descubrir cuál es el mecanismo. No equivale a 2/3 acreditado.

**CT2 es un juicio ordinal interno, NO P(descubrimiento)**; registrar siempre `score`, fecha, línea, confianza de la propia evaluación (alta/media/baja), antecedente adversarial, observación que subiría/bajaría la puntuación y coste de la siguiente evidencia. No subir CT2 por más semillas, más ciclos o mejoras frente a un rival incompetente. Tras un PIVOT, redefinir CT2 para la nueva línea, preservando el histórico.

## B. Niveles 0–3 y contador N1
- **0/3:** reproducción trivial, hallazgo invalidado, empate de tratamientos, resultado explicable por supuesto impuesto o sin evidencia distinguible.
- **1/3:** hallazgo técnico/empírico EXPLORATORIO bien especificado, replicable computacionalmente, utilidad local o contradicción informativa que ajusta el programa; puede tener antecedente conocido; no afirmar novedad científica.
- **2/3:** predicción discriminante novedosa contrastada con fuentes/prior art, rival fuerte y **confirmación independiente** pertinente; relevancia suficiente, no confundir cambios artificiales con fenómenos naturales.
- **3/3:** descubrimiento de elevada trascendencia, robusto, transferible, formalizado y confirmado externamente, que supere exigencias 2/3.
El recuento `N1_campaign` incluye SOLO 1/3 concedidos explícitamente tras revisión de evidencia; una misma idea no puede contarse múltiples veces por datasets/seeds/bloques. Distinguir `N1_portfolio` histórico solo si se hace auditoría exhaustiva de campañas previas; por defecto `NOT_AUDITED` y no inventar total. Contadores N2/N3 separados. Anotar `duplicate_of` y `prior_art`.

## C. Puerta de interpretación
Registrar una trayectoria por rama y en el cierre de cada ciclo: `CT2_before`, `CT2_after`, `reason_change`, `grade_0_3`, `counted_n1_id_or_null`, `prereg_commit`, `result_commit`, `falsifier`, `external_replication`. Los 30 ciclos pueden ser obligatorios por encargo del investigador: permitir CONTINUE/BRANCH/PIVOT dentro del bloque, sin fabricar efectos ni saltarse AB A–J. El imperativo operativo de ejecutar el cupo no autoriza elevar grados ni eludir fallos y preregs.

**Estado de validación de O4:** NO_VALIDADO. Esta puntuación no tiene calibración frecuentista ni bayesiana; es gobernanza trazable, no prueba de eficacia de AB.
