# V48 — Resiliencia de reciprocidad aprendida ante reorganización dentro de la relación

**Preregistro 13/11/2026, antes de ejecutar V48.** Se parte de los12 checkpoints finales de V47, entrenados durante1000 actualizaciones con cambio de compañero **entre** episodios; se mantienen congelados. V48 intenta falsar que esas políticas resuelvan ya cooperación generalizable ante cambios de interlocutor **dentro del episodio**.

## RQ48

¿Los individuos con respuestas contingentes aprendidas por LOLA siguen encontrando beneficios privados de dar cuando los contactos sociales se reorganizan entre rondas, o necesitan continuidad de una misma contraparte para que su contribución inicial desencadene ayuda futura?

## Mundo y reglas sin alteraciones materiales

48 personas; 24 oficios de tipo0 y24 de tipo1, asignados exógenamente para garantizar que cada pareja sea profesionalmente complementaria. La sociedad forma, en cada ronda, un emparejamiento completo bipartito entre ambos oficios. Cada persona solo puede donar a la contraparte actual y recibir de ella, según una decisión Bernoulli privada. La alimentación propia mantiene exactamente la fórmula de V44/V46, `0,20 + (0,55/3)·recibe − 0,04·envía`. Hay probabilidad por sociedad q0,95 de sobrevivir entre rondas y un límite máximo48, gamma0,995. **No hay contratos, profesor ni reparto de recompensas.**

Los emparejamientos se reorganizan en cada ronda viva con probabilidad `r∈{0, 0,05, 0,25, 0,60, 1,00}`. En cada reorganización se sortea un matching bipartito uniforme de las24+24 personas. Es un cambio **dentro** del episodio; r0 mantiene la pareja durante toda la relación, r1 reempareja en todas las rondas. Las mismas secuencias exógenas de vidas, permutaciones y números aleatorios se comparten entre políticas y controles en cada semilla, aunque cada checkpoint tenga pesos diferentes.

Se contrastan dos condiciones de observación: `carry` mantiene la última donación observada en la contraparte del turno previo (aunque cambie su identidad) y `reset` anula esa señal solo cuando se cambia de pareja, conservando la memoria de la propia decisión. Se distingue por tanto la aplicación de una regla de reciprocidad **generalizada** de la dependencia de la misma contraparte. Una tercera condición `public` (si se audita por separado) proporcionaría la donación previa del actual compañero a su anterior pareja; no es información que el mundo original permita observar y deberá rotularse como información pública añadida por el experimentador. No se utilizará como prueba primaria.

## Evaluación

Para cada uno de12 checkpoints V47 (NL, LOLA5, LOLA20 × cuatro semillas), se evaluarán cinco tasas de cambio × dos modos de memoria, seis semillas ambientales nuevas y128 mundos por semilla, 48 rondas máximas. **Las semillas reservadas** son `994101,994107,994109,994121,994131,994137`; todas distintas de entrenamiento y desarrollo. Métricas descriptivas: alimentación por persona-ronda viva, tasa de regalos, tasa de donación mutua, duración efectiva y cambio en la cobertura de contactos distintos.

La métrica primaria de incentivos se evalúa forzando o impidiendo la donación inicial de cada individuo por separado, con la política y reacciones posteriores libres. Se emparejan estrictamente vida, matchings y uniformes de acción entre los dos contrafactuales. Se usarán ocho mundos por cada una de las seis semillas para cada condición y modelo (8×48 contrafactuales individuales por semilla). Resultado: retorno privado descontado, diferencia respecto a r0 y número de personas con retorno causal positivo, promediando las seis semillas ambientales. El coste inmediato propio debe ser exactamente−0,04. La inferencia debe reconocer que una sociedad y su ciclo de pares son unidades ambientales de referencia, no los48 individuos como entrenamientos independientes.

## Criterios preregistrados

H48a: en LOLA20/carry, al menos3/4 semillas neuronales conservan ≥24 personas con incentivo causal privado positivo y mutualidad≥0,25 bajo r=0,25.

H48b: bajo cambio continuo r=1,00 y memoria carry, al menos3/4 LOLA20 conservan 24 individuos con incentivo positivo y mutualidad≥0,25 (hipótesis exigente de transferencia).

H48c: al menos en3/4 semillas LOLA20, la memoria carry supera a reset en el incentivo privado medio por ≥+0,025 cuando r=0,60.

H48d: la política NL sigue sin generar incentivos privados positivos para al menos24 personas en las cuatro semillas bajo r=0 y r=0,60.

Se documentará cualquier falsación. En particular, una alta mutualidad con incentivos causales negativos indica cooperación aparente material, no reciprocidad que beneficia a cada donante.

## Limitaciones

La sociedad conserva relaciones exclusivamente diádicas en cada ronda (una sola contraparte), y los oficios son asignados y siempre complementarios; no ha surgido división del trabajo. Los compañeros nuevos se asignan por un mecanismo exógeno de matching que no optimizan ni negocian los agentes. Las políticas fueron aprendidas previamente con expectativa exacta del gradiente ajeno, por lo que el experimento de transferencia no demuestra aprendizaje continuado en una red dinámica ni acceso realista a los mecanismos del oponente.

Los resultados positivos serían evidencia de transferencia de estrategias, no de una institución o sociedad plenamente emergente. Si falla, V49 debería modificar el entrenamiento para que incluya cambios intraperíodo, sin ajustar retrospectivamente los umbrales anteriores.
