# Metodología AB — propuesta AB-M031 (NO adoptada)

**Fecha 2026-10-22.** Fuente LARP gate `research/EVIDENCE_GATE_20261022`, con scripts y resultados.

**Problema:** se habían medido mejoras de integración para un estimador fijo mientras un selector condicionado por covarianzas buscaba minimizar error bajo predictor aprendido. Diseñar para un estimador y juzgar para otro invalida la atribución algorítmica directa. La comparación se vuelve también asimétrica si las restricciones efectivas de candidatos difieren de su etiqueta: GP con parámetro `candidates=144` utilizaba `Sobol.random_base2(7)`, máximo 128 coordenadas antes de eliminar duplicados.

**Propuesta:** añadir `READOUT_AND_CANDIDATE_PARITY_AUDIT` al observatorio: registrar 
(1) estimando, (2) diseño de adquisición, (3) predictor real, (4) número efectivo de ubicaciones candidatas por tipo, (5) parámetros y coste pareados; ejecutar el readout común antes de atribuir la ventaja al posicionamiento. Una prueba adicional después de abrir holdout es REPAIR exploratorio; no renueva su independencia.

**Prueba favorable:** Nuevo benchmark de escenas 2D monocromas, canales derivados, mismo predictor Ridge o media fija para cinco diseños; invierte la interpretación: COSI mejora con Ridge, no con media fija. Un selector gaussiano con pool completo sigue peor en las escenas disponibles, pero no representa todo el estado del arte.

**Evidencia contra la necesidad de nueva regla:** AB-M021, AB-M024 y AB-M030 ya contemplan paridad informativa y alineación estimador. Esto puede ser una especificación operativa de una regla existente, no un principio nuevo. Coste de auditar candidatos efectivo bajo modelos enormes; aplicar con proporcionalidad.

**Estado:** PROPUESTA; no modificar núcleo AB 3.2.1 ni priors metodológicos A01–A21 por esta sola campaña.
