# V51 — Aprendizaje privado de cuatro ocupaciones complementarias sobre cooperación estratégica preaprendida

**Preregistro 13/11/2026**, después de V50 y antes de entrenar V51. V50 transfirió políticas cooperativas V47 a tres contactos complementarios simultáneos y reprodujo exactamente el pago de V25, pero las profesiones estaban fijadas exógenamente. V51 somete las ocupaciones a aprendizaje propio y elimina las cuotas profesionales.

## Pregunta

¿Puede una población de48 personas que ya dispone de estrategias privadas de reciprocidad aprender **desde el estado monolítico** una distribución de cuatro profesiones dentro de sus relaciones estables, mediante recompensas alimentarias exclusivamente individuales y sin organizador laboral?

## Mundo

48 agentes distribuidos en **12 equipos disjuntos de4 miembros**, cada equipo con seis enlaces bidireccionales (clique K4); cada persona tiene tres vecinos distintos. La agrupación y conectividad son externas y favorables. Ninguna ocupación se asigna a los cuatro puestos: cada agente escoge libremente uno de cuatro oficios (0–3), con independencia de las elecciones simultáneas de los demás.

Cada ocho rondas cada individuo puede elegir de nuevo su ocupación, pagando0,015 al cambiar. Una sola persona puede ocupar cualquiera de los cuatro oficios; la vida de la sociedad se fija en48 rondas durante entrenamiento y evaluación. No hay sanción por desempleo ni recompensa por balance, y ningún objetivo grupal se incorpora a la optimización.

En cada ronda cada individuo elige si enviar un bien a cada uno de sus tres vecinos con su política V47 congelada (cada donación unilateral cuesta0,04); la última donación recibida de ese mismo vecino sirve como memoria. El pago sigue el del motor V25: comida=0,20+0,55×(número de categorías complementarias recibidas/3)+0,25×indicador de completar las tres−0,04×regalos enviados−0,015×cambio de profesión (solo en el turno de cambio).

La política ocupacional **se aprende desde cero** por cada persona, con parámetros MLP no compartidos, cuatro logitos de elección profesional condicionados a su profesión actual, composición profesional de vecinos, alimento último, etapa temporal y último cambio. Cada actor maximiza únicamente su propio alimento descontado gamma0,995 con REINFORCE y baseline entre mundos, sin compartir gradientes ni parámetros. Adam tasa0,003, 1500 actualizaciones, lote12,48 rondas y entropía0,01. No hay aprendizaje de donaciones en V51: el donante fue entrenado previamente V47 y se congela. Se explicita esta formación secuencial, no simultánea desde cero.

## Diseño factorial

Donante previo: LOLA20 congelado de V47 con semilla3111 o4111, frente a NL congelado de idénticas semillas, sin información de donante compartida. Dos semillas independientes de rol profesional7111 y8111. Se ejecutan ocho poblaciones de aprendizaje ocupacional (2 fuentes ×2 semillas donor ×2 semillas role).

Inicio de entrenamiento mixto: mitad de los mundos tienen las48 ocupaciones iguales a0 y mitad distribución aleatoria; no se impone balance. Desarrollo congelado en mundos monolíticos y aleatorios, puntos u1,300,600,900,1200,1500. El resultado principal se evalúa en el checkpoint final u1500 sin seleccionar pasos anteriores.

## Controles y medidas

Evaluación fuera de muestra con seis semillas ambientales `997101,997107,997109,997121,997131,997137`,24 mundos por semilla y dos inicios (todas las personas oficio0; ocupaciones aleatorias). Se comparan las políticas aprendidas con ocupaciones fijas iniciales y cambios ocupacionales aleatorios (tasas0,15;0,35;0,60 por oportunidad cada ocho rondas), conservando en todos los casos las políticas congeladas de donación. Se calcula alimentación, cobertura de tres tipos, proporción de equipos con los cuatro roles, tasas de donaciones, cambios profesionales y equivalencia del pago físico al motor V25.

La prueba de transferencia reasigna de forma completa los parámetros del actor profesional a otras posiciones dentro de cada grupo de cuatro, sin alterar la red ni la política de donación, y cambia las posiciones grupales mediante permutaciones internas. Se informa si la coordinación depende de convenciones posicionales específicas.

## Hipótesis preregistradas

H51a: al menos3/4 de las condiciones con donante LOLA20 alcanzan ≥50% de equipos con cuatro profesiones y alimentación≥0,55, al final del episodio, comenzando todos con el mismo oficio.

H51b: al menos3/4 de LOLA20 superan por ≥+0,05 el mejor de los tres cambios ocupacionales aleatorios, sobre el mismo inicio monolítico.

H51c: ninguna de las cuatro condiciones con donante NL logra a la vez ≥50% de equipos completos y alimentación≥0,55 (control negativo de cooperación).

H51d: al menos3/4 de las condiciones LOLA20 conservan ≥40% de equipos completos al permutar actores ocupacionales entre posiciones del equipo, sin reentrenar.

No se permitirá usar un umbral alternativo retrospectivo para declarar éxito. La inferencia se condiciona a dos semillas de donante y dos de rol profesional, seis ambientales por condición. Aun un resultado positivo prueba **aprendizaje de división del trabajo condicionado a cooperación preentrenada y conectividad K4 externa**, no surgimiento completo de instituciones en una sociedad abierta.
