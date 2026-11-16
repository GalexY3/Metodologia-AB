# Una identidad local del gradiente de pago de LOLA

Derivación posterior al primer resultado COLD V204. No fue H1, no seleccionó eta ni modificó las trayectorias registradas. Se analiza un método conocido y una parametrización concreta. La identidad se ha contrastado numéricamente en n=4 y precisión de señal 0,8; el resto de la familia es una predicción algebraica que requiere comprobación independiente y revisión de prioridad. No se acredita originalidad, ley sociológica o nivel 2/3.

## Supuestos y cantidad que se calcula

Familia del juego V202: n>=2 jugadores, uno crítico y n−1 posibles pagadores ordinarios. GOOD tiene probabilidad pi; las señales son independientes condicionalmente al estado y la señal del crítico acierta con probabilidad kappa. La producción exige participación de todos; un ordinario recibe, respecto a AUTO, b en GOOD y −(Y+L_i) en BAD, antes de su pago. Cada pagador puede dar tau al crítico únicamente en GOOD conjunto. En V204: n=4, pi=0,65, kappa=0,8, b=0,8F, Y=0,25F, tau=0,25, beta=0,95.

La historia pública es el recuento de pagos de la última producción GOOD, más el último resultado AUTO/BAD/GOOD y un recuento START hasta la primera producción GOOD. Los logits están separados por jugador, historia, señal y fase. En el punto estudiado, todos los modos tienen la misma probabilidad nativa u y todos los pagos probabilidad nativa 1/2, independientemente de historia/señal. No se supone esa igualdad durante las trayectorias.

Con mezcla exploratoria epsilon fija en el cálculo, sea

`q=epsilon/2+(1−epsilon)u`, `a_M=(1−epsilon)u(1−u)`, `a_P=(1−epsilon)/4`.

q es la probabilidad conductual de participar, y a_M/a_P son derivadas respecto al logit nativo. Para un pagador i, se suman los componentes de pago de su campo en todas las historias y señales. Esta suma equivale a una derivada direccional al desplazar todos sus logits de pago a la vez. **No es la derivada de una probabilidad media ni prueba el signo de cada coordenada individual.**

Sean D_i la suma del gradiente propio ordinario, C_i la suma de la corrección LOLA sin multiplicar por eta. Se usa la ecuación 4.4 original: el factor grad_j U_i queda detenido en el backward. Los retornos U_i son monetarios netos y normalizados por 1−beta.

## Identidad

Defínase

`I_i=pi²[kappa²+(1−kappa)²](b−tau/2) − 2pi(1−pi)kappa(1−kappa)(Y+L_i)`.

Si d_h es la ocupación descontada normalizada y `S(q)=sum_h d_h²`, entonces

**`D_i=−tau a_P pi q^n`**,

**`C_i=tau a_P I_i S(q) a_M² q^(2n−2)`**.

El coste/pérdida del crítico y las pérdidas de los otros ordinarios no aparecen en C_i bajo estos supuestos. Pueden afectar profundamente a las trayectorias; la cancelación se refiere solo a este punto uniforme y a esta suma direccional.

S(q) también tiene forma cerrada. Escribiendo `g=pi q^n`, `z=(1−pi)q^n`, `r=1−q^n`, `delta=1−beta`, `D0=delta/(delta+beta g)`, `D1=beta g/(delta+beta g)`, se obtiene

`S(q)=(delta+beta r D0)²+(beta z D0)² + choose(2n−2,n−1)/4^(n−1) * beta²[(r²+z²)D1²+g²]`.

La forma de S depende de la parametrización por **recuento** de pagos. Separar logits por identidad de cada pagador modifica los pesos de visita y no permite trasladar esta identidad sin volver a derivarlos. La sensibilidad de LOLA a la parametrización ya tiene antecedentes, entre ellos POLA (2022).

## Demostración

1. Como las políticas no dependen de h, las recompensas medias son constantes entre historias. Bellman da un valor constante. Desplazar uniformemente los pagos de i conserva esa propiedad y solo cambia su transferencia media. La derivada de U_i es exactamente −tau a_P pi q^n, obteniendo D_i.

2. Para cada jugador j, sean w_s y p_s la probabilidad de su señal s y su posterior Pr(GOOD|s). Para j distinto de i, el gradiente del retorno del pagador i respecto a un logit de modo de j es

   `grad_(j,h,s) U_i = d_h w_s a_M q^(n−1) B_i(s)`,

   donde `B_i(s)=p_s(b−tau/2)−(1−p_s)(Y+L_i)` usa la posterior de j. No es necesario que todos los j tengan la misma precisión para la cancelación siguiente. Los gradientes de U_i respecto a pagos de otros ordinarios son cero: no transfieren a i y la continuación es constante.

3. Introducir un escalar lambda que desplaza todos los logits de pago de i. Para un j ordinario distinto de i, la derivada respecto a lambda de su ventaja de modo es cero. Para el crítico es `tau a_P p_s q^(n−1)`. La derivada del gradiente también incluye `partial_lambda d_h` por el cambio de visitas. En el producto LOLA todas esas contribuciones de visita contienen el factor común `sum_h d_h partial_lambda d_h`.

4. Ese factor es cero en el punto de pagos 1/2. La ocupación de START no depende de lambda. En las historias con producción previa, la ocupación para recuento k es un factor de resultado físico por `w_k=choose(n−1,k)/2^(n−1)`. La derivada de w_k al variar un único pagador es antisimétrica bajo k -> n−1−k, mientras w_k es simétrica. Luego `sum_k w_k partial_lambda w_k=0`. Desaparecen los términos de visita, incluidos los que contienen preparación y pérdidas del crítico u otros jugadores.

5. Solo queda el efecto directo del pago sobre la actualización de modo del crítico:

   `C_i=tau a_P S(q) a_M² q^(2n−2) sum_s w_s² p_s B_i(s)`.

   Usando `w_s p_s=pi Pr(s|GOOD)` y Bayes, la última suma es I_i. Para una señal binaria simétrica, `sum_s Pr(s|GOOD)²=kappa²+(1−kappa)²` y `sum_s Pr(s|GOOD)Pr(s|BAD)=2kappa(1−kappa)`.

6. Para obtener S, antes de la primera producción GOOD la masa descontada es D0; después, D1. Las dos ocupaciones START son `delta+beta r D0` y `beta z D0`. Para cada k, las ocupaciones AUTO/BAD/GOOD son `w_k beta r D1`, `w_k beta z D1`, `w_k beta g`. Se suman sus cuadrados y se aplica `sum_k choose(n−1,k)²=choose(2n−2,n−1)`.

## Consecuencias acotadas y predicciones pendientes

Sin exploración, u=q y S(q)->1 cuando q->0. Por tanto D_i tiene orden q^n y C_i orden q^(2n), si I_i no es cero. Para n=4 son q^4 y q^8. Para eta finito la corrección relativa desaparece como q^n. La suma direccional de pagos queda dominada localmente por el coste. **Esto no demuestra que toda coordenada caiga, que no aparezca dependencia de historias o que LOLA sea universalmente incapaz de cooperar.**

El signo de C_i es el de I_i. Si `A=pi(b−tau/2)>0`, `B=(1−pi)(Y+L_i)>A`, el cero de la corrección en kappa>=1/2 es

`kappa_*=(1+sqrt(1−2A/(A+B)))/2`.

En la calibración actual, la predicción algebraica es 0,765164734 para L_i=1 y 0,956829311 para L_i=7. Es un umbral del **término local de enseñanza**, no del éxito de aprendizaje, bienestar o cooperación. Hace una predicción diferenciable frente al gradiente propio: este último siempre resta el coste de dar, mientras el término LOLA cambia de signo al variar la calidad informativa del destinatario. Falta validarla con otra implementación que permita cambiar esa calidad y el tamaño de grupo; no se ha observado una transición de trayectorias en esos valores.

## Comprobaciones realizadas

El certificado contrasta 57 componentes con el autodiff del modelo de cuatro agentes: nueve probabilidades uniformes sin exploración, seis combinaciones adicionales de probabilidad/mezcla y variaciones de pérdidas de otros jugadores, incluida pérdida crítica 0 y 100. Error relativo máximo 1,79e−13. No se ajustó la fórmula a esos valores: la identidad predice su coeficiente, signo y factor de ocupación. En el punto COLD real, u=1/2 y epsilon=0,20, eta*C_i/|D_i|=0,001743 para el pagador L=1: el término favorable compensa solo aproximadamente 0,1743% del término directo agregado. No es una estimación causal del porcentaje de fracaso de toda la trayectoria.

`certify_v204_uniform_payment.py` y `results/V204_CLOSED_FORM_CERTIFICATE.json` contienen ecuaciones, verificaciones, hashes y límites. Es un resultado algebraico interno posterior al negativo, con prioridad pendiente y sin confirmación externa. No cambia la evaluación AB ni rescata H1.

Antecedentes primarios: [LOLA, ecuación 4.4](https://arxiv.org/pdf/1709.04326), [POLA, NeurIPS 2022](https://proceedings.neurips.cc/paper_files/paper/2022/hash/a882dab38011264d2ca8dba3cca9faf1-Abstract-Conference.html), [SOS, ICLR 2019](https://arxiv.org/abs/1811.08469).
