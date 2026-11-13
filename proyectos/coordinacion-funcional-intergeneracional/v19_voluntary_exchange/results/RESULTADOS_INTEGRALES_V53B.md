# V53B — ¿En qué condiciones materiales compensa la regulación inspirada en Beer?

Se replicó exactamente la condición BASE de V53 frente a los datos originales, incluyendo **todos los mundos y semillas**, y se realizaron nueve perturbaciones paramétricas especificadas antes de ejecutar el barrido: costes de administración mitad/cero/doble, transferencias sin pérdidas o con pérdida20%, consumo de subsistencia0,68 u0,82, reservas iniciales/capacidad limitadas o ampliadas. Se mantuvieron los mismos ocho mecanismos de regulación, dos entornos PATCHY/SYSTEMIC y seis semillas ambientales nuevas del experimento V53, con128 mundos por semilla y condición: **122.880 sociedades adicionales**.

## Frontera material PATCHY: supervivencia al final de96 rondas

| Parámetro | Sin gestión | Ayuda local | Local+entre equipos | Con pronóstico | Proxy completo |
| --- | --- | --- | --- | --- | --- |
| BASE | 0.0796 | 0.3364 | 0.9148 | 0.8050 | 0.7445 |
| HALF_ADMIN | 0.0796 | 0.3493 | 0.9597 | 0.9349 | 0.9168 |
| ZERO_ADMIN | 0.0796 | 0.3650 | 0.9835 | 0.9857 | 0.9830 |
| DOUBLE_ADMIN | 0.0796 | 0.3105 | 0.7245 | 0.3553 | 0.2411 |
| FREE_TRANSFER | 0.0796 | 0.3506 | 0.9422 | 0.8563 | 0.7984 |
| LOSS20 | 0.0796 | 0.2951 | 0.7520 | 0.6090 | 0.5202 |
| LOW_SUBSISTENCE | 0.3526 | 0.8215 | 1.0000 | 1.0000 | 1.0000 |
| HIGH_SUBSISTENCE | 0.0098 | 0.0375 | 0.0228 | 0.0132 | 0.0111 |
| SHORT_BUFFER | 0.0149 | 0.0427 | 0.3313 | 0.2105 | 0.1816 |
| LONG_BUFFER | 0.2360 | 0.6167 | 0.9973 | 0.9813 | 0.9626 |

## Entorno de perturbaciones sistémicas

| Parámetro | Sin gestión | Local+entre equipos | Proxy completo |
| --- | --- | --- | --- |
| BASE | 0.0062 | 0.0341 | 0.0241 |
| HALF_ADMIN | 0.0062 | 0.0382 | 0.0347 |
| ZERO_ADMIN | 0.0062 | 0.0499 | 0.0495 |
| DOUBLE_ADMIN | 0.0062 | 0.0219 | 0.0072 |
| FREE_TRANSFER | 0.0062 | 0.0357 | 0.0261 |
| LOSS20 | 0.0062 | 0.0278 | 0.0148 |
| LOW_SUBSISTENCE | 0.0440 | 0.2701 | 0.2086 |
| HIGH_SUBSISTENCE | 0.0000 | 0.0016 | 0.0000 |
| SHORT_BUFFER | 0.0000 | 0.0032 | 0.0029 |
| LONG_BUFFER | 0.0293 | 0.1060 | 0.0710 |

## Contrastes causales de costes y predicción

| Parámetro | Δ multinivel−local | Δ pronóstico−multinivel | Δ aviso real−aviso falso |
| --- | --- | --- | --- |
| BASE | 0.5785 | -0.1099 | 0.0147 |
| HALF_ADMIN | 0.6104 | -0.0248 | 0.0163 |
| ZERO_ADMIN | 0.6186 | 0.0022 | 0.0091 |
| DOUBLE_ADMIN | 0.4140 | -0.3692 | -0.0094 |
| FREE_TRANSFER | 0.5916 | -0.0859 | 0.0156 |
| LOSS20 | 0.4569 | -0.1430 | 0.0212 |
| LOW_SUBSISTENCE | 0.1785 | 0.0000 | 0.0000 |
| HIGH_SUBSISTENCE | -0.0147 | -0.0096 | -0.0004 |
| SHORT_BUFFER | 0.2886 | -0.1208 | 0.0331 |
| LONG_BUFFER | 0.3806 | -0.0161 | 0.0079 |

El indicador primario es la fracción de personas que continúa viva al final, no el promedio de alimento únicamente entre supervivientes. Costes de regulación y pérdidas de transporte se deducen del almacén material, y la muerte de un productor retira de forma irreversible una especialidad del equipo K4.

## Preguntas preregistradas

| Pregunta / comprobación | Estado |
| --- | --- |
| Q53b1_local_global_positive_vs_local_in_at_least_8of10_PATCHY | cumple |
| Q53b2_zero_admin_forecast_more_viable_in_patchy | cumple |
| Q53b3_full_proxy_strictly_best_in_any_setting | no cumple |
| Q53b4_forecast_beats_placebo_in_all_settings | no cumple |

La pregunta Q53b4 se formuló como examen abierto de cambio de signo, no como predicción de signo invariable; el resumen booleano `all` es solo un indicador exploratorio, no un criterio de éxito preregistrado. Una señal pronosticadora correcta puede tener más información que una señal falsa y, sin embargo, no justificar su coste. La diferencia entre ambos mensajes, con idénticos costes, separa parcialmente valor informativo de rentabilidad neta de la capa regulatoria.

## Discusión e implicaciones

[Inferencia] Los mecanismos de apoyo multinivel poseen una región amplia de utilidad positiva, pero hay límites materiales donde no bastan para conservar la viabilidad, especialmente cuando el consumo mínimo se aproxima a la producción máxima0,88. El coste administrativo puede invertir la ventaja de mecanismos anticipatorios: disponer de información del futuro no significa que transformarla en regulación sea rentable.

[Inferencia] Esto es compatible con una lectura condicionada del Modelo de Sistema Viable, según la cual la gestión de variedad y la recursividad pueden resultar funcionales en ambientes heterogéneos, pero las capacidades organizacionales específicas y su precio determinan si compensan. **No prueba ni refuta la afirmación universal de necesidad y suficiencia de Beer**: los modelos simulados contienen solo proxies de regulación y una economía de producción cooperativa ya impuesta.

Para estudiar la **emergencia** de estos mecanismos hará falta permitir a los propios agentes escoger quién contribuye a regular, qué información comprar y cuándo abandonar instituciones costosas, midiendo el retorno de cada individuo y del grupo frente a competidores policéntricos o descentralizados.

## Validación, fuentes y replicación

V53B utiliza el motor V53 original sin modificar su código: en cada escenario se cambia temporalmente un parámetro del módulo, se restauran los valores BASE y se confrontan por igualdad exacta los mundos originales BASE. Se guardan los mundos por semilla y todos los escenarios, CSV, contrastes con bootstrap pareado de seis semillas y hashes:
PREREG_V53B_SENSITIVITY.md: 81de0cd5dbaedbbd8c8693795924da3ed4248184475007bb0582ace35bbd861c
v53b_sensitivity.py: 006e31a541c9a359912ddb1828091c4e437d38f5585071bf2607746833118453
test_v53b_sensitivity.py: f32b78172d606f19f98b29e6d8e678c51638e92f4b1a39b2e95ffc8b2fceb4b8
v53b_summarize.py: 7adfb8f2935fc3d34451137e6b29d125f4ddbef20d8a602b869c7ebf74249a1c