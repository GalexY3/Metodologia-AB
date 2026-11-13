# V52 — Coaprendizaje privado de reciprocidad y división del trabajo con donaciones adaptables

**Preregistro exploratorio 13/11/2026**, posterior a los resultados V51 y previo a los entrenamientos V52.

## Pregunta

Cuando las personas aprenden simultáneamente qué profesión ocupar y si conviene contribuir a otros, ¿puede emerger una población que sostenga ambas capacidades de forma estable, o la adaptación privada de las donaciones destruye el mecanismo cooperativo heredado?

## Mundo y recompensas

Idéntica economía material de V51: N48,12 cliques K4 exógenas de cuatro personas cada una, tres vecinos por persona, cuatro profesiones seleccionables, donación unilateral a cada vecino, máximo tres por ronda. Cada ocho rondas cada persona puede cambiar de profesión pagando0,015. Alimento estrictamente propio `0,20+0,55×cobertura de tipos recibidos/3+0,25×todos los tres tipos−0,04×regalos enviados−0,015×cambio profesional`. Horizontes48, descuento gamma0,995,12 mundos por actualización, sin información sobre quien entregará en la misma ronda, sin contratos ni recompensas grupales.

## Dos mecanismos de inicialización del donante

**SCRATCH:** la política privada de donar de cinco logitos Bernoulli por agente empieza en ruido N(0;0,05), sin profesiones ni estrategias preentrenadas. El origen usa dos semillas3111 y4111; el actor ocupacional MLP independiente se inicializa con semillas7111 y8111. Cuatro sociedades totalmente desde cero, sin ninguna política social aprendida externamente. Tanto donaciones como profesión se optimizan únicamente con retorno alimentario propio por REINFORCE.

**PRIOR:** los mismos actores ocupacionales se inicializan desde cero, pero los cinco logitos del donante se cargan del checkpoint final LOLA20 de V47 (semillas3111 y4111). **A diferencia de V51**, los logitos se mantienen entrenables durante las1500 actualizaciones de ocupación, con exactamente el mismo REINFORCE propio del brazo SCRATCH. Se estudia si el capital cooperativo estratégico es estable bajo aprendizaje conjunto local. La comparación directa es con el checkpoint V51 del mismo donante y semilla ocupacional, en que los logitos quedaron congelados.

Los ocho modelos usan Adam para donante lr0,003, actor profesional lr0,003, entropía de donación0,005 y profesión0,01. No hay bonificaciones prosociales, ejemplos dirigidos, sanciones ni profesores. Cada agente tiene sus propios logitos y pesos profesionales, sin compartir parámetros ni gradientes entre personas.

## Tiempo, diseños y medición

1500 actualizaciones por sociedad, init de entrenamiento mixto (mitad mundos monolito de profesión0, mitad aleatorios), evaluaciones congeladas en u1,300,600,900,1200,1500. No se selecciona un checkpoint intermedio para declarar éxito.

Seis semillas ambientales reservadas `998101,998107,998109,998121,998131,998137`;24 mundos por semilla en dos inicios monolito y aleatorio. Se informará alimento por persona y ronda, prevalencia de roles complementarios terminal (una ocupación de cada tipo en K4), cobertura material, regalos por persona, gasto privado y rentabilidad causal de forzar un regalo inicial frente a impedirlo. El contraste de causalidad será sobre el primer vínculo dirigido de cada persona en un mundo, usando la misma realización de roles y uniformes en dos ramas, manteniendo libres todas las decisiones posteriores. El retorno causal propio descontado debe ser>0 y en≥24/48 agentes positivos para considerar que la cooperación adaptada también es estable.

Comparadores de ocupaciones fijas y cambios aleatorios0,15/0,35/0,60 permanecen disponibles para lectura de sensibilidad. La comparación central de PRIOR con V51 requiere condiciones ambientales comparables y reportará explícitamente la distinta generación de semillas ambientales.

## Hipótesis preregistradas

H52a: alguna de las cuatro sociedades SCRATCH consigue conjuntamente alimentación media≥0,55, ≥50% de equipos con cuatro profesiones al final y ≥0,50 donaciones por puesto de vínculo.

H52b: ≥3/4 sociedades PRIOR conservan los mismos tres umbrales de alimentación, especialización y donación, indicando estabilidad inicial de habilidades previas durante coaprendizaje REINFORCE.

H52c: el rendimiento alimentario de PRIOR en mundo monolítico queda como máximo0,05 por debajo de la referencia congelada V51 con el mismo donante y semilla de rol en al menos3/4 casos.

H52d: si una condición supera H52a/H52b, al menos una de ellas mantiene retorno causal privado de donar positivo en≥24/48 individuos; el criterio se considerará no aplicable si ninguna condición supera los anteriores.

## Riesgos y validez

El brazo SCRATCH mide aprendizaje experiencial propio sin modelar directamente el gradiente de otro; un resultado nulo no niega la posibilidad de aprender cooperación mediante algoritmos de anticipación más sofisticados. El brazo PRIOR introduce explícitamente una estrategia ya aprendida con conocimiento exacto del gradiente del compañero en V47 y no constituye emergencia desde cero. Incluso si ambos aprenden, el grafo K4 y tamaño de los equipos siguen fijados externamente. V52 no acredita todavía una sociedad abierta de120 agentes, creación institucional propia o normas públicas endógenas. No declarar objetivo general completado sin estas pruebas.
