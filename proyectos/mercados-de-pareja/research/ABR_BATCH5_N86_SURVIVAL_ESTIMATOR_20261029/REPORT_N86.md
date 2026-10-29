# N86 · Componente de supervivencia: código Python congelado y probado

**Ciclo técnico válido, no confirmación científica.** Freeze 6b04d12e4b699f8203982a728076bc17c71b86b3 anterior a ejecución. Los archivos survival_metrics.py y test_survival_metrics.py se ejecutaron localmente exactamente iguales a los blobs de GitHub fuente 580895c7f0a00217664ffdc437d722a6bb045c3b y tests 88b692bf2e5686ec991dfcb89ae0e3fb76e74f10. SHA256 local fuente a6726cf8dd0c6d0342cce6eb2b4b6845242a830433c8044bc5835f97e4b02e88; tests 5e0275f9aee89766bd764f25c27b8bde9d7930f1cbd9862720d164d71a9de944.

## Contrato A–J y pruebas realmente realizadas

A–C: RMST discreta Kaplan–Meier para (duración,event 0/1,censura administrativa, horizon), no media libre ni verdadera duración de relaciones humanas. D–E: Python estándar sin dependencias, congelado y cargado desde copia de bytes local cuya SHA1 Git es idéntica a la versión prerregistrada; ninguna ejecución del ESBM original. F–G: comando python -m unittest -v test_survival_metrics.py, **9 tests ejecutados y 9 superados**, incluidas soluciones manuales RMST=2.75 y 10/3, todos censurados, todos rotos a t1, evento/censura simultáneo, banderas inválidas, evento en horizonte, falta de soporte a horizonte y equivalencia del adaptador. No se editaron scripts después de ver los resultados.

H: el módulo no reescribe esbm_dynamic.py, no integra histórico RUNS.json y no demuestra supervivencia sin sesgo bajo riesgo heterogéneo, entrada escalonada o censura dependiente de formación. Hay que registrar además start_tick y tiempo a evento por pareja, reejecutar el simulador real y realizar una auditoría de efectos de calendario. I: U135 P-UNION-DURATION no cambia estado. Originalidad 0/3, sin nueva fuente, ni causalidad o validación externa humana. J: N86 solo válido como test técnico; N87 pendiente y R5 mantiene STOP para evidencia externa.

## Estado

20 ciclos válidos / 40 autorizados, 20 pendientes; N87 (1) liberado, N88–N106 (19) reservados. 97 SOURCES, 30 PRIORS, 135 UPDATES. CT2 ordinal 7/100 sin subir; madurez 39.05% por +1 punto de QA de ingeniería, sin variación de originalidad ni validación. No autor contactado, licencia aceptada, SSJY, OSF/Essex/Stanford/Gist, datos publicados, ni merge main.