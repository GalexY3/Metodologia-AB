# V31 — Escalabilidad del intercambio contractual de 48 a 120 agentes y cuatro profesiones

Fecha: 12/11/2026. Preregistro exploratorio basado en los resultados preliminares de V30 alrededor de u280–420, antes de iniciar entrenamientos V31 y antes de saber los resultados finales de V30.

## Intervención

Conservar inalterados el actor neuronal de propuestas dirigidas voluntarias V25 (parámetros privados por individuo), el actor privado ocupacional categórico, los incentivos propios y la regla de aceptación mutua de V30. Aumentar el tamaño de la sociedad de N48 a **N120**, manteniendo k=4 profesiones y grado social 6. No existe trasferencia de pesos N48→N120; ambas redes se inicializan desde cero para cada uno de los 120 individuos, por lo que la comparación es de protocolos, no generalización neuronal directa. La arquitectura del motor sigue igual y el crecimiento de parámetros privados es lineal con N.

Dos semillas neuronales fijadas: 3111 y 4111, y dos precios finales por unidad 0,04 y 0,12. Cuatro entrenamientos independientes en total, todos bajo contratos voluntarios. Entrenamiento de 700 actualizaciones por corrida, lote 8 sociedades, horizonte de 48 turnos, programa de costo 0,002 hasta u300, ascenso al precio final entre u300 y u500, costo final fijo hasta u700; gamma 0,995; movilidad profesional cada ocho turnos a coste 0,015. Mundo inicial mezcla por lotes sociedades monolíticas y ocupaciones aleatorias. Evaluación de desarrollo en semilla fija, con precio final, checkpoints de u1,140,280,420,560,700.

## Comparadores

Referencia histórica V30 N48 con las mismas dos semillas a precio 0,04; se añade la condición de 0,12 como test de robustez a incentivos más exigentes. Controles en evaluación congelada: no contratos, movilidad ocupacional fija o aleatoria, ausencia de señales sociales, reconfiguración de red, sociedad de ocupaciones inicialmente aleatorias y sociedad monolítica. La regla de contrato requiere mutuo consentimiento para que cada donación ejecutada y cobrada exista; no hay regalos automáticos ni cuotas centralizadas de profesiones.

## Hipótesis

H31a: al menos algunas políticas aprendidas N120 logran alimentación material >0,25 a costo final e intercambios efectivamente consensuados, con ventaja sobre bloqueo de ofertas y reparto ocupacional exógeno fijo.

H31b: la elección voluntaria de ofertas tiene retorno causal individual positivo para una mayoría de los 120 individuos cuando los compañeros han aprendido a acordarlas; esto debe probarse con auditoría de primera oferta forzada, no inferirse de la tasa global.

H31c: la ventaja aparece con más de un precio unitario, y no depende exclusivamente del coste reducido 0,04. El costo final 0,12 puede destruir intercambios incluso cuando una transferencia bilateral útil es materialmente positiva.

## Importante distinción conceptual

V31 es una **institución de contrato recíproco programada como posibilidad**. Sus reglas de liquidación son externas; los agentes aprenden a usarla y a especializarse, no la inventan. Cumplir V31 demuestra coaprendizaje en un entorno institucional descentralizado, no emergencia de instituciones sin affordances. Seguirá pendiente replicación entre más inicializaciones, cambio de socios, escala y ausencia de contratos para alcanzar el objetivo general en sentido estricto.
