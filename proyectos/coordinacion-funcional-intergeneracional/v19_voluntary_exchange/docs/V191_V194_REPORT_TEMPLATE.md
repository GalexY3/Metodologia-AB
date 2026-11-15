# De la convención a la generalización: dos aprendices neuronales privados

Informe V191–V194, 15 de noviembre de 2026. Resultados, fuentes y controles conservados. Las afirmaciones se refieren a este juego computacional; no se acredita una institución material aprendida ni una contribución AB2/3.

## Resultado principal

Dos redes con observaciones separadas pueden aprender una convención desde inicializaciones nuevas, memorizar sus interacciones conocidas y generalizar mucho después a entradas locales retenidas de ambas. En los cuatro pares PRIVATE_FULL de V192, el test conjunto codicioso termina en100%. La fase tardía no requiere que las dos redes sigan adaptándose: congelar cualquiera de ellas desde su primera memorización permite que la otra alcance100%local. Sus pesos y momentos coinciden bit a bit con la continuación conjunta en todos los checkpoints comparados.

La dificultad del feedback binario aparece en la formación con interlocutores aprendientes. PRIVATE_BANDIT_IS termina cerca del azar, pero el mismo aprendiz alcanza99,18%medio con interlocutores ya correctos. El control evita atribuir su fracaso anterior a incapacidad general de aprender con un pago binario.

Estos resultados separan formación de la convención y generalización posterior. El candidato descriptivo de dos redes no supera la prueba de necesidad causal de coadaptación continua. Las ventajas genéricas del feedback contrafactual y de reducir varianza tienen antecedentes; no se reclaman como nuevas.

## Por qué cambiar el experimento

V190 tenía un emisor tabular y un único receptor neuronal. Todos los valores locales del emisor aparecían en entrenamiento, mientras que las combinaciones nuevas llegaban al receptor. Por eso no identificaba abstracción de varios aprendices. Además, sus códigos defectuosos impedían memorizar perfectamente. Esa arquitectura se retiró para esta pregunta.

El nuevo juego exige que cada red resuelva entradas locales nuevas. La pregunta causal permanece ligada al programa de organización: distinguir una estructura ya formada de los procesos necesarios para crearla o mantenerla. El cambio se registra como DRIFT D2 de mecanismo y arquitectura dentro de cooperación computacional; no se transfiere el resultado a ocupaciones materiales o instituciones humanas.

## Juego, información y unidad de análisis

Cada participante observa x_i=(a_i,b_i), con valores en Z31, y elige u_i. Ambos reciben1si `u_A+u_B=f(x_A)+f(x_B) mod31`, donde f(a,b)=a+b mod31. Un par puede resolver el juego mediante desfases opuestos g y −g; no tiene que escoger el convenio0. En la condición privada, ninguno recibe la observación ajena, la suma local verdadera ni gradientes del otro. Cada red tiene parámetros y optimizador propios.

Los intereses comunes, la pertenencia al par, la recompensa y la tecnología de feedback son exógenos. FULL proporciona todos los pagos de acciones alternativas propias, fijando la acción realizada del interlocutor. Es un oráculo contrafactual externo: en este juego contiene una única acción correcta. Esa acción depende del error del compañero y no es necesariamente la etiqueta local verdadera. BANDIT proporciona únicamente el pago de la acción elegida. No se denomina institución aprendida al oráculo suministrado.

Hay cuatro bloques que varían conjuntamente datos e inicialización. Cada participante tiene384pares locales de entrenamiento y577retenidos; el test conjunto combina los conjuntos retenidos de ambos. Se incluyen las dos orientaciones de cada par en una misma partición y se retienen las diagonales. La selección de datos se condiciona a cubrir todos los valores marginales y etiquetas. Un candidato omitía un valor y se rechazó antes de entrenar; permanece guardado. No se seleccionaron soportes según resultados neuronales.

Las24redes de las tres condiciones V192 no son24réplicas independientes: son12trayectorias de pares correspondientes a cuatro bloques emparejados. V193 añade ocho continuaciones de esas raíces. V194 reutiliza los mismos cuatro bloques para completar el control. Tampoco los ejemplos cartesianos, checkpoints o pasos de entrenamiento se cuentan como réplicas del algoritmo.

## Dos estimadores con el mismo gradiente esperado

Cada red estima sus pagos Q(x,u) mediante128unidades cuadráticas, embeddings para las dos entradas y31salidas. Se mantiene AdamW .001, weight_decay1 y betas(.9,.98), durante60000actualizaciones completas. La política de aprendizaje es epsilon-greedy con epsilon=.1.

Con feedback completo se minimiza `L_F=(1/P)sum_u(Q_u−R_u)^2`. Con una acción Uextraída de q y pago r se usa `L_B=(Q_U−r)^2/(P*q_U)`, tratando q_Ucomo constante al actualizar. Condicionado a la acción ajena, la expectativa de L_B y de su gradiente coincide con L_F. Son identidades conocidas de muestreo por importancia y marginalización. La auditoría V191 las verifica por enumeración exacta, junto con las tablas de pago y el aislamiento de redes. Las trayectorias de Adam no tienen por qué coincidir: cambia la distribución del gradiente y su precondicionamiento adaptativo.

Se igualan inicializaciones, episodios y actualizaciones; no se iguala información recibida. FULL revela31pagos por cada pago BANDIT. La comparación no demuestra eficiencia de consultas. COMA ya utiliza contrafactuales con un crítico centralizado, y Expected Policy Gradients ya estudia marginalización y reducción de varianza. Nuestros regresores no ejecutan ni superan esos algoritmos por esta prueba. [COMA](https://ojs.aaai.org/index.php/AAAI/article/view/11794), [EPG](https://www.jmlr.org/papers/v21/18-012.html).

Las métricas principales usan despliegue codicioso, separado de la exploración durante aprendizaje. Aun con funciones perfectas, epsilon=.1 limita el pago exploratorio esperado a `.81+.19/31=.816129`;100%de precisión codiciosa no significa100%de aciertos durante episodios exploratorios.

## V192: una convención seguida de generalización tardía

Se registraron fuente, datos y criterios antes de entrenar. Primero ORACLE_FULL comprobó capacidad: cada aprendiz recibía feedback de un interlocutor virtual correcto con la misma exploración. Es una convención suministrada a un control, no formación privada. Al pasar4/4se ejecutaron completas PRIVATE_FULL y PRIVATE_BANDIT_IS.

La memorización operativa requería cinco evaluaciones consecutivas con precisión conjunta de entrenamiento>=.99. El primer checkpoint se guardaba sin mirar test. La generalización requería cinco evaluaciones test>=.95. El candidato tardío exigía razón temporal>=5, al menos2000pasos de separación y mantener train>=.99 y test>=.95 al final. PRIVATE_FULL debía cumplirlo en al menos3/4bloques.

__TIMING_TABLE__

Los cuatro pares PRIVATE_FULL cumplen el criterio. Aprenden desfases A14,25,10y0, con los opuestos enB. La convención concreta emerge dentro del juego; el canal de feedback y los incentivos comunes siguen programados. Los cuatro pares BANDIT no memorizan ni generalizan en este horizonte. El resultado es específico de este estimador y presupuesto.

![Origen del feedback y riqueza informativa](FIG_V192_V194_FEEDBACK_FACTORIAL.png)

Figura1. Trayectorias completas de las cuatro condiciones. Líneas claras: los cuatro bloques; líneas gruesas: medias descriptivas. La fila oráculo usa interlocutores virtuales ya correctos. La condición binaria con oráculo se ejecutó después como control V194, con su propio registro previo. Las condiciones están emparejadas; no son cuatro muestras independientes de poblaciones distintas.

## V193: una prueba causal que refuta la interpretación fuerte

El candidato motivó una intervención registrada desde los primeros checkpoints de memorización. FREEZE_A fijaA y continúaB; FREEZE_B hace lo contrario. Se conserva la exploración del interlocutor y el presupuesto total de60000pasos. Los cortes1100y1200se alinean para ejecutar lotes, manteniendo cada compañero congelado desde su corte original. La reanudación histórica hasta5000reproduce pesos, momentos y RNGexactamente; no cuenta como nueva evidencia científica.

__FREEZE_TABLE__

Ambos brazos pasan el criterio causal: al menos3/4activos con test local>=.95 y déficit mediano frente a su continuación conjunta<=.02. En realidad pasan4/4y el déficit es0. En cada uno de los12checkpoints por brazo, pesos y momentos activos son idénticos bit a bit a los originales; la aleatoriedad también coincide. Se verificó aparte que los parámetros congelados permanecen iguales a sus cortes parentales.

El test conjunto del par congelado es bajo. Esto no demuestra que la otra red deje de generalizar. Para una distribución de error retenido h_Fdel compañero fijo, `Acc_joint<=max_g h_F(g)`. El activo puede resolver su función y seguir limitado por los errores del compañero. La cota es algebraica y conocida, no un descubrimiento.

![Congelación y generalización local](FIG_V193_FROZEN_PEER_CAUSAL.png)

Figura2. Las curvas de la red activa con compañero congelado y con compañero que aprende se superponen. La caída del resultado conjunto se explica por el componente congelado. La intervención conserva la historia conjunta anterior a memorizar; no establece que esa historia fuera innecesaria.

## V194: el control de capacidad que faltaba

El contraste FULL/BANDIT no bastaba para localizar un problema colectivo: un regresor binario incapaz incluso con interlocutores correctos sería un rival débil. Se registró ORACLE_BANDIT_IS sin cambiar tasa, red, regularización o presupuesto. Los interlocutores virtuales usan la misma ley y secuencia de acciones que en ORACLE_FULL; el aprendiz recibe solamente su pago observado.

__CAPABILITY_TABLE__

Los cuatro bloques superan el umbral final .95. La media es.991778, frente a.032169con dos interlocutores aprendientes. El resultado rechaza una incapacidad general de ese aprendiz bajo el presupuesto examinado. No separa por sí solo calidad, sesgo y no estacionariedad del feedback ajeno.

Las cuatro condiciones completan un diseño2×2. La diferencia descriptiva entre la ventaja FULL sobre BANDIT con interlocutores aprendientes y con oráculo es.959609en promedio. Ese valor no tenía un umbral confirmatorio numérico registrado: se reporta como interacción exploratoria, sin convertir cuatro bloques en una muestra grande ni añadir un p-valor oportunista.

Banditron ya demuestra aprendizaje con feedback de corrección bajo sus supuestos. No se ejecutó aquí ni se aplican sus garantías lineales a nuestras redes. Su antecedente impide una afirmación genérica de imposibilidad binaria. [Fuente primaria](https://doi.org/10.1145/1390156.1390212).

## Composición y mecanismo

La precisión del par satisface `Acc_joint=sum_g h_A(g)h_B(−g)`. Bajo el desfase escogido en entrenamiento se puede separar el producto de aciertos locales y las compensaciones entre errores. Las2400evaluaciones PRIVATE_FULL verifican la descomposición. Una curva conjunta puede cambiar por ambas contribuciones; por sí sola no identifica una nueva capacidad compartida.

![Descomposición de la precisión conjunta](FIG_V192_JOINT_DECOMPOSITION.png)

Figura3. La generalización final coincide con que ambos componentes acierten sus funciones bajo una convención compatible. La descomposición es una identidad del juego. La prueba causal, no la forma de la curva, permite rechazar la necesidad de adaptación conjunta posterior a memorizar.

El aprendizaje mutuo entre redes ya tenía análisis de sincronización en trabajos de Klein y colaboradores. Este juego añade entradas locales retenidas y una prueba de congelación, pero no se infiere originalidad por esa combinación ni por no hallar una expresión exacta en un buscador. [Antecedente primario](https://proceedings.neurips.cc/paper/2004/hash/5a45828dead8c065099cb653a2185df1-Abstract.html).

## Integridad, alcance social y siguiente incertidumbre

Las fuentes se congelaron antes de sus entrenamientos: V192`babedeedbf604d9a05f134f80a1eb82383bcd402`, V193`2b2adb035e0826dff0c7a75981bea290c3e3a339`, V194`9b0d9ffd13d7ad353fb06fe45357c7279c988329`. Se descargaron por HTTPS los archivos registrados y se compararon sus bytes. V193fijó también los hashes de los estados parentales que ahora se entregan completos. Se preservan los borradores técnicos fallidos anteriores al registro.

Un evaluador NumPy separado recalcula los pesos y enumera explícitamente productos cartesianos. Pasan192comparaciones únicas de métricas de V192–V194, error máximo6.66e−16. Las64comprobaciones V193 incluidas en la auditoría combinada no se vuelven a sumar. Son independencia técnica de cálculo, no confirmación científica independiente de una predicción social original.

El juego no contiene profesión material, poder de negociación, costes de información endógenos o un dilema distributivo. No se usa su test como ley de cooperación humana. El hallazgo positivo es una convención aprendida y generalización tardía del sistema bajo una infraestructura informativa diseñada. El negativo causal restringe la interpretación colectiva de esa fase. CT2 histórico61permanece sin cambios; nueva rama sin puntuación, N2=N3=0.

La incertidumbre siguiente es el reparto de información con presupuesto igualado: un receptor FULL fijo y otro BANDIT frente a rotar cuál recibe FULL en cada interacción. Esa prueba aún no está realizada. La asignación de roles informativos sería exógena y exigiría rivales sobre heterogeneidad, ruido y precondicionamiento Adam antes de una reivindicación original. El control binario de capacidad ya permite investigarla sin basarse en un componente incapaz.

![Referencia histórica CT2](FIG_CT2_V175_V180.png)

Figura4. Referencia ordinal histórica de otra rama. No representa probabilidad de éxito ni asigna puntos a la nueva línea por completar entrenamientos.

Consultar `REPRODUCE_V191_V194.md`, los registros A–J y los manifiestos de `research/V191_V194_20261115`. El manuscrito ampliado sigue siendo un borrador académico que requiere revisión integral y adaptación al formato universitario.
