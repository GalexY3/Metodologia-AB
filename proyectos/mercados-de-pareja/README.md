# Mercados de pareja · acceso estable

**Estado 30/10/2026.** Esta entrada en `main` es documentación estable, **no una fusión** de ramas experimentales.

## Último cierre AB-H PIVOT N317–N336

- [Informe técnico completo en main](informes/ABH_N317_N336_20261030.md) y [versión canónica, prerregistro A–J, recibos y auditoría](https://github.com/GalexY3/Metodologia-AB/tree/research/ab-h-esbm-decentralized-n317-n336-20261030/proyectos/mercados-de-pareja/research/ABH_N317_N336_20261030).
- **20/20 ejecuciones técnicas, 20 PASS locales, 0 plazas restantes; ninguna prueba humana confirmatoria.** A–J y código congelados antes de outcomes: commits `f69b629c404b3325817b569d7e0dd0f0acdae375` y `c94fc50ef83a45edae2108c4088c808212ef44c8`. La auditoría posterior se preregistró antes de ejecutarla en commit `f11e92f848cbdec72c1d95143057e2f111730db9`.
- **Hallazgo operacional del modo de asignación:** N317, en 18/20 mercados artificiales n8+8, el maximizador central de utilidad conjunta produjo parejas bloqueantes aunque DA fue estable por construcción; no es una muestra de personas ni una comparación causal del mundo real. N322 top-1 ofertas dejó bloqueantes en 20/20; N325 dinámica de bloqueos aleatorios alcanzó estabilidad en 20/20 dentro del límite pero revisó cinco estados; N326 ganancia marginal requirió 20,5 cambios menos de media que selección aleatoria. N327–N329 mostraron restricciones sintéticas de visibilidad y normas; N328 Gini se concentró **por diseño**, no como descubrimiento. N335 obtuvo 20/20 coincidencias de oráculos independientes DP, MILP HiGHS y NetworkX n7; N336, transformar cardinalmente pesos sin alterar orden individual cambió el óptimo central en 15/20, preservando DA.
- **34 archivos íntegros** en `ESBM_ABH_N317_N336_RESULTS_AND_AUDITS.zip`, SHA256 `f5a2fb3f7811030d20864d11db06513fef3f7cb52b7a174c2ccb5c6c2c3e52bf`, Biblioteca `/Mercados-de-pareja/ABH-N317-N336/`. Fuentes pre-outcome ZIP SHA `d4687db70c1b79801b0d4b27c38363184f3ef9f4ea4be9903e41ab1c4c65a93d`. La Biblioteca no implica que los ZIP brutos estén en GitHub.
- **114 SOURCES, 35 PRIORS** (nuevo `P-ALLOCATION-RULE`) y **208 UPDATES** (U205–U208). SRC001 Gale–Shapley y SRC114 Echenique et al. ya estaban registrados: no se duplicaron; SRC114 se enriqueció con cifras de laboratorio **no romántico** 75/85 mercados estables. No se obtuvo evidencia real romántica con dos votos nativos más oportunidades y derechos acreditados. **CT2 científica 7/100; STOP_R5 humano activo; grado humano nuevo 0/3**. Madurez previa 44,10% no reestimada.
- El ESBM Python original conserva su SHA256 `f7e6b84000720cbdf2ee0800c2b10d136185facd00e4622756cbb5f8d8254d0b`; SRC104 intacto; esta campaña introdujo simulaciones bipartitas separadas, **no** reejecutó el antiguo TypeScript ni validó parámetros del ESBM original. Sin SSJY, Codex, aceptación de licencias, contactos de autores ni CI costosa.

## Histórico, tarea futura inactiva y gobernanza

[Informe N297–N316](informes/ABH_N297_N316_20261030.md) · [N277–N296](informes/ABH_N277_N296_20261030.md) · [N257–N276](informes/ABH_N257_N276_20261030.md) · [carpeta de tareas archivadas para Codex](tareas_codex/README.md) · [propuesta de ejecución futura inactiva](tareas_codex/08_FUTURA_N337_VALIDACION_Y_NEGOCIACION.md).

**R5 manda:** un presupuesto para nuevas simulaciones no representa validación externa ni obliga a ejecutar sin evidencia discriminante. Cualquier campaña posterior necesita autorización nueva y congelación A–J y SHA antes de outcomes. No fusionar ramas científicas en `main`.
