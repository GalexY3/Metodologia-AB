# AB-H · Modelización formal de instituciones de oportunidades, dependencias y matching

**Proposición y limitaciones, 2026-10-29.** Esto es un resultado matemático dentro de un universo sintético muy pequeño, no un descubrimiento de comportamiento humano. La literatura registrada SRC017, SRC054, SRC098 ya estudia oportunidades, asignación y congestión; no atribuimos prioridad histórica a la tesis general.

## Definiciones

Sean cuatro agentes ficticios A0, A1, B0, B1 y el conjunto de cuatro aristas elegibles `E={(A0,B0),(A0,B1),(A1,B0),(A1,B1)}`. Una **institución de programación** establece una distribución `π(S)` sobre subconjuntos de oportunidades efectivas `S ⊆ E`. Una arista programada produce **dos consentimientos simultáneamente positivos** con probabilidad condicional `p` (esto NO es la probabilidad unilateral individual, cuya multiplicación requeriría dos votos). Las variables binarias de sí/sí son independientes *condicionalmente al calendario S*, un supuesto artificial explícito.

Defina `C⊆S` como el conjunto de aristas sí/sí, `g(C)` como un matching de máxima cardinalidad con desempate predefinido, `M=|g(C)|` como parejas exclusivas formadas. La ley del conjunto de consentimientos es:

`Pπ(C)=Σ_{S⊇C} π(S) p^{|C|}(1−p)^{|S|−|C|}`.

La ley de parejas observadas es la suma de `Pπ(C)` sobre todos los C cuyo matching produce el mismo outcome. Si se conoce solo `q_e=P(e∈C)=Pπ(e∈S)p`, no se conoce la distribución conjunta de C cuando las exposiciones están correlacionadas. Incluso con las mismas probabilidades marginales e idénticos dos consentimientos por arista, una política puede cambiar las parejas finales por quién comparte las oportunidades simultáneamente.

## Proposición 1. Mismas probabilidades marginales + mismo presupuesto, resultados diferentes

- **Rotación disjunta R:** `S={00,11}` o `{01,10}`, cada una con probabilidad 1/2; ninguna persona participa en más de una cita.
- **Asignación adyacente A:** `S={00,01}`, `{00,10}`, `{01,11}` o `{10,11}`, cada una con probabilidad 1/4; ambas citas comparten una persona.
- **Dos aristas uniformes U:** una de las 6 parejas posibles de aristas, uniforme.

En R, A y U, `|S|=2` con probabilidad 1 y `P(e∈S)=1/2` para cada arista. Por tanto, la esperanza de aristas de sí/sí es `2p` en las tres instituciones. Sin embargo, `E[M|R]=2p`, `E[M|A]=2p-p²`, `E[M|U]=(2/6)(2p)+(4/6)(2p-p²)=2p-(2/3)p²`.

A `p=1/2`, el resultado exacto es `E[M|R]=1`, `E[M|U]=5/6`, `E[M|A]=3/4`. La diferencia `R−A=p²=1/4` no necesita supuestos psicológicos distintos: surge exclusivamente de la estructura de concurrencia y matching exclusivo que estipula el ejemplo. Una comparación sin igualar presupuesto puede además mezclar varianza de exposiciones y congestión; N95/N96 incluyen el control de 2 citas fijas.

## Proposición 2. Distribuciones completas, no solo medias

La probabilidad de dos parejas simultáneas en R es `p²`; en A es 0; en U es `p²/3`. Con `p=1/2`:

| Política | P(M=0) | P(M=1) | P(M=2) | E[M] |
|---|---:|---:|---:|---:|
| R | 1/4 | 1/2 | 1/4 | 1 |
| U | 1/4 | 2/3 | 1/12 | 5/6 |
| A | 1/4 | 3/4 | 0 | 3/4 |

Una rotación con `p=0.4` y una política adyacente con `p=1−√0.2≈0.552786` tienen ambas `E[M]=0.8` pero diferentes leyes de M (`P(M=2)` igual a .16 frente a 0). Una sola tasa media de parejas no identifica ni preferencias ni instituciones.

## Proposición 3. La institución de desempate también es una variable

Si las cuatro aristas ofrecen sí/sí, existen dos matchings de cardinalidad 2: `{00,11}` (ambas intragrupo bajo etiquetas ficticias) y `{01,10}` (ambas cruzadas). Un algoritmo que ante empate elige el primer matching puede observar dos parejas intragrupo; otro algoritmo de desempate uniforme espera una pareja intragrupo y una cruzada, **con exactamente dos parejas en ambos casos**. Los mecanismos de desempate no son consecuencias psicológicas del consentimiento; son instituciones algorítmicas. Este contraste NO demuestra que una regla sea justa para personas reales, ni que las normas sociales se reduzcan a categorías binarias.

## Proposición 4. Qué mediciones discriminarían los mecanismos

A `p=0.5`, R e institución de exposición por arista independiente `P(e∈S)=.5` tienen el mismo `q_e=.25` en cada arista, pero la covarianza de los sí/sí en `00` y `11` es `+.0625` bajo R y 0 bajo exposición independiente. Observar la estructura conjunta de oportunidades permite distinguir mecanismos que las probabilidades marginales no identifican.

La comparación interna N105 fija dos distribuciones con **soporte común**: 90 % de R y 10 % de U frente a 90 % de A y 10 % de U. Con `p=.5`, la divergencia `KL(π_R||π_A)` sobre calendarios es **2.931780966 nats**, mientras la divergencia de las **distribuciones de M** es **0.590738360 nats**. El sentido de la comparación es un ejemplo de pérdida de información por proyección, coherente con la desigualdad de procesamiento de datos. No son medidas empíricas de datos sobre humanos, ni prueba de que esa magnitud se generalice.

## Supuestos que invalidarían la interpretación general

Este universo omite heterogeneidad, identidad real, orientación y relaciones no exclusivas, consentimiento con historia, costes de tiempo, falta de atención, algoritmos adaptativos, sesgo endógeno de exposición, interferencia entre eventos, capacidad real de múltiples citas, filtrado por agencia, calidad de vínculo, duración, censura y bienestar. Si las oportunidades modifican preferencias, `p` deja de ser constante y el estimando cambia; si se comparan políticas en poblaciones no intercambiables, el contraste no identifica causalidad. No afirmamos que todos los regímenes de rotación reales mejoren las parejas o la satisfacción.

El siguiente instrumento empírico mínimamente relevante debería registrar: (1) lista de personas elegibles por evento, (2) calendario de oportunidades realmente completadas y la ausencia de exposición, (3) dos votos nativos por encuentro, no el match agregado, (4) algoritmo de resolución de múltiples sí/sí, (5) unidades de interferencia y oportunidades no vistas, y (6) seguimiento temporal si el outcome es duración. Requiere condiciones de uso, consentimiento y derechos verificados, un estimando y comparadores competentes, además de predicción novedosa y validación fuera de muestra para nivel 2/3.

**Estado de originalidad:** Este argumento tiene valor como contraejemplo explícito y control de software; el mecanismo de congestión ya se entiende en modelos de matching y los precedentes del repositorio limitan las reivindicaciones. Grado científico nuevo 0/3. **STOP_R5 externo permanece.**
