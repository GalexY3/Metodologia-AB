# V36 — Adopción endógena de contratos y escasez de vecinos complementarios

Preregistro 12/11/2026, posterior a las evaluaciones V32 y V34, y anterior a entrenamientos V36. La hipótesis combina dos mecanismos explorados por separado, **por lo que es una prueba exploratoria condicionada a los resultados anteriores**, no una confirmación estadística ciega.

## Pregunta y teoría

V32 mostró que los individuos N48/k4 en redes de seis vecinos podían aprender privadamente a elegir un régimen contractual voluntario sobre donaciones unilaterales (adopción contractual final >99,9%, retorno causal positivo para los 48 individuos de cuatro modelos) y ganar entre 0,022 y 0,039 raciones frente a movilidad ocupacional aleatoria. V34 mostró que una red más escasa de cuatro vecinos podía hacer mayor la ventaja ocupacional bajo contratos exclusivamente disponibles, de 0,031 a 0,034 raciones, comparada con aproximadamente 0,011 en grado6. V36 ensaya si **ambas presiones juntas** producen una distribución de profesiones verdaderamente ventajosa.

## Diseño

N48, k4, anillo de grado4, 48 rondas, 12 mundos por actualización, 1000 actualizaciones, cuatro inicializaciones de parámetros desde cero: semillas 3111 y 4111 con predisposición contractual logit0 (50% inicial) y logit−2 (12% inicial). Todos los demás parámetros, precios, horizonte, entropías y programa de entrenamiento se mantienen iguales que en V32: costo c=0,002 hasta actualización400, incremento a0,04 entre u400 y u650, precio fijo0,04 hasta u1000; gamma0,995, coste de cambio de profesión0,015, elección de profesión cada ocho rondas, tres políticas privadas por persona con parámetros independientes. La **única modificación de entorno** respecto a V32 es el grado4 en vez de grado6, y la **única diferencia principal respecto a V34** es permitir a cada individuo que elija unilateralidad frente al modo contractual en vez de forzar siempre el contractual.

Los agentes pueden decidir declinar ofertas, proponer cada uno hasta tres veces por turno, seleccionar el receptor y cambiar oficio. Un contrato bilateral solo se liquida si ambas partes escogen el modo contractual y se envían propuestas recíprocas en la misma ronda. No hay recompensa de grupo ni maestro ni cuotas profesionales. La regla de liquidación es estructuralmente exógena; su adopción es aprendida.

## Evaluación, baselines y objetivos

Seis semillas ambientales no vistas, doce mundos por semilla, sociedades iniciales monolíticas y aleatorias, y red reconectada. Intervenciones de modo forzado unilateral, siempre contrato, modo aleatorio50/50, rol fijo, cambio de profesión aleatorio a tasas 0,15, 0,35 y 0,60, bloqueo total de ofertas, historial social ausente, personas permutadas. Auditoría causal a todas las 48 personas forzando su modo institucional en la primera ronda, manteniendo las decisiones privadas del resto.

Criterios H36a: adopción contractual media final >90% y retorno causal positivo por adoptar para ≥40/48 individuos en ambas semillas con predisposición inicial rare y neutral. H36b: la ventaja del reparto profesional aprendido respecto al **mejor** de los tres controles de movilidad aleatoria ≥+0,05 de alimento en al menos tres de las cuatro inicializaciones. H36c: mayor ventaja laboral que la de V32 con grado6 para los cuatro pares de semilla y sesgo. No seleccionaremos un checkpoint intermedio mejor: solo actualización1000.

Aunque se verifiquen estos criterios a N48, faltará replicar la estructura en N120, robustez de la diferencia ocupacional ante conexiones cambiantes y integración de nuevos agentes. Por tanto V36 aislado no establece el objetivo general ni aparición espontánea de las reglas contractuales.

## Sesgos e incertidumbre

La decisión de investigar grado4 es posterior a observar que grado4 produjo más comida y mayor ventaja laboral en V34, lo cual supone selección exploratoria de mecanismo. Las cuatro políticas neuronales son observaciones independientes de entrenamiento dentro de los dos niveles de predisposición. Las 72 trayectorias de mundo por condición no son 72 semillas neuronales.
