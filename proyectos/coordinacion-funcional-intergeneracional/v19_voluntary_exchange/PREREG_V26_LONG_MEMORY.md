# V26 — Memoria relacional persistente para donaciones voluntarias multiunidad

**Preregistro del 12-11-2026.** Se presenta después de completar V25, cuyas cuatro políticas no conservaron retornos causales positivos. Las hipótesis y condiciones se establecen antes de ejecutar entrenamientos V26.

## Problema

En V25 cada persona podía producir y enviar voluntariamente tres bienes por ronda en sociedades de cuatro profesiones. Se eliminó la barrera física de una unidad, pero las políticas aprendieron a cesar los regalos cuando aumentó el coste. Sus señales de cooperación seguían siendo muy efímeras: `trust` recordaba solo si cada vecino había dirigido algún regalo al actor en la ronda anterior. Con cuatro profesiones, los beneficios pueden acumularse en retornos individuales después de varias rondas de interacciones distribuidas. El olvido inmediato puede impedir descubrir consecuencias diferidas de un gesto de ayuda.

## Tratamiento causal experimental

V26 sustituye la regla de memoria directa de recepción `trust_{i←j}(t+1) = incoming_{j→i}(t)` por `trust_{i←j}(t+1) = max(incoming_{j→i}(t), δ trust_{i←j}(t))`, con δ∈{0,0,94,0,99}. Las políticas neuronales son las mismas de V25 y observan esa señal en sus entradas locales; no cambian ni el espacio de acciones (0–3 donaciones), ni el costo personal, el grafo, los beneficios materiales, el algoritmo de retorno individual ni los parámetros privados. El dato de memoria es un historial individual, no una reputación pública compartida por toda la red, y no garantiza que los actores lo interpreten de forma recíproca.

δ=0 reproduce V25 con exactitud y sirve como control histórico previamente completado. δ=0,94 representa recuerdo prolongado con semivida aproximada de once rondas. δ=0,99 representa persistencia mayor con semivida aproximada de 69 rondas, superior al horizonte de 48 rondas de las trayectorias. Esos horizontes se infieren de `log(0.5)/log(δ)`; constituyen parámetros experimentales exógenos. Comparar ambos valores permite comprobar si la duración del crédito relacional presenta una relación no monótona con la sostenibilidad de donaciones voluntarias.

## Protocolos congelados antes del entrenamiento

Sociedad N=48, k=4, grado seis, anillo fijo de entrenamiento; dos semillas neuronales 3111 y 4111. Cuatro entrenamientos V26 de 1000 actualizaciones por tratamiento: δ=0,94 (dos semillas) y δ=0,99 (dos semillas). Coste final de contribución = 0,04 por unidad, capacidad máxima de tres regalos por ronda y gasto máximo por agente 0,12. Misma ventana barata de V25: 0,002 hasta la actualización 500, transición hasta 0,04 en la actualización 800 y coste fijo hasta la actualización 1000. Mismos lotes de 12 mundos, horizonte 48, gamma 0,995, parámetros de optimización y arquitecturas.

Los controles históricos V25 sin memoria tienen las mismas condiciones y semillas. La comparación primaria empleará el alimento fuera de muestra y el retorno causal de donar en cada uno de los 48 individuos a coste final. También medir tasa de donaciones, cobertura de categorías y reciprocidad condicional, con redes reconectadas, sociedades monolíticas, ocupaciones aleatorias y ocupaciones equilibradas.

## Criterio y falsadores

H1: ambos tratamientos con memoria permiten mayor retorno causal medio que δ=0 en la misma semilla. H2: al menos un tratamiento preserva un alimento medio materialmente superior al baseline de 0,20 al final de las 1000 actualizaciones, y una fracción apreciable de actores muestra retorno individual de donación positivo. H3: la señal relacional influye causalmente; al eliminar la memoria social en la evaluación congelada deben desaparecer las ventajas que dependan de ella.

Si las políticas vuelven a abandonar donaciones, se reportará como evidencia negativa: la memoria prolongada tampoco es suficiente. No introducir recompensas altruistas ni maestros con patrones de donación. El posible fracaso indicará que hacen falta cambios adicionales de arquitectura, crédito temporal, estructura relacional o costo de coordinación, no que la cooperación humana sea imposible.

## Auditoría y reproducibilidad

Se documentará el código exacto que inyecta la nueva regla de memoria sin modificar el entrenador original V25, se guardarán especificaciones completas y checkpoints por semilla y se evaluarán las políticas congeladas con todas las personas. Las pruebas unitarias deben demostrar que δ=0 equivale a V25 y que δ>0 conserva el recuerdo dentro de la trayectoria.
