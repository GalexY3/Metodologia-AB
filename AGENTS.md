# Instrucciones portables para agentes de investigación AB

Este repositorio es la autoridad metodológica del protocolo AB del investigador. Antes de crear o revisar campañas, leer **en este orden**:
1. [README](README.md)
2. [AB 3.2.1, base](docs/METODO_AB_3_2_1.md)
3. [O3, DRIFT/BRANCHING](docs/AB_3_2_1_O3_BUCLES_DRIFT.md)
4. [O4, CT2 1–100 y hallazgos 0–3](docs/AB_3_2_1_O4_CONFIANZA_Y_NIVELES.md)
5. [O5, escala DRIFT D0–D5](docs/AB_3_2_1_O5_DISTANCIA_DRIFT.md)
6. **[O6, campañas, gráficos CT2 y solicitudes de 5–15 ciclos](docs/AB_3_2_1_O6_CAMPANAS_INFORMES_CT2_Y_CICLOS.md)**.

## Contrato de experiencia con el usuario

**Directiva vigente (29/10/2026):** bloques nuevos de **5–30 ciclos**, autorizados explícitamente; la campaña PFL 20+10 ya concedida no requiere nueva autorización. **Histórico de 28/10:** bloques 5–15;  ChatRelay en pausa, **no usar por defecto** ni consumir su saldo histórico. Solo proponer reactivarlo si hay evidencia excepcionalmente sólida y nueva decisión del investigador. Esta actualización no reasigna presupuestos anteriores.

- Los experimentos y planificaciones autorizados son **ciclos AB completos A–J**. Ejecutar solo lo efectivamente instrumentado; registrar incompletos, invalidaciones, auditorías post hoc y negativos.
- Mantener CT2 1–100 por **rama concreta**; nunca hacerla subir por obligación. **Mostrar gráfico CT2** de escala 0–100 y vista ampliada al cerrar informes, con puntos respaldados por ledger.
- En cada DRIFT asignar distancia **D0–D5** justificada; ciclos especiales D3–D5 se etiquetan `PLANNING_AB_ONLY`.
- Conservar cada 1/3 **único** en ledger persistente del proyecto, con evidencia, límites, falsador, parentescos y posibles combinaciones; no duplicar por semillas o fuentes. No conceder 2/3 sin contribución novedosa, control fuerte y replicación independiente.
- En el **último párrafo** de cada informe final de campaña, solicitar **entre 5 y 30** nuevos ciclos AB con propósito, cantidad y modo; por ejemplo `SOLICITO BRANCHING 5 CICLOS` o `SOLICITO PIVOT 10 CICLOS`. Los bloques sucesivos pueden autorizarse sin límite total predeterminado, pero cada petición nueva se acota a 5–15. **No** volver a solicitar ciclos ya concedidos y pendientes. Histórico de 20–45 preservado en Git.
- Registrar contratos, hash, prereg antes de ejecutar y guardar JSON por semilla, ledger A–J, prior ledger, auditoría y estado verdadero GitHub.
- La investigación científica es prioritaria al formato: nunca inventar resultados para cubrir cuotas ni afirmar CT2/2/3 favorables sin evidencia.

La metodología **no garantiza** que un modelo de ChatGPT tenga acceso automático al repositorio, los archivos ni las herramientas. Requerir conexión o material aportado por el usuario cuando falte acceso.

**Procedencia y detalle completo:** [O6](docs/AB_3_2_1_O6_CAMPANAS_INFORMES_CT2_Y_CICLOS.md). Su adopción normaliza informes y colaboración, **no demuestra** la eficacia científica de AB.
