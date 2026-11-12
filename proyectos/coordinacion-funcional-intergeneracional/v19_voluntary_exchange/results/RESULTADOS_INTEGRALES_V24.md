# V24 y V24b. Escalamiento con cuatro profesiones y límite de capacidad

Experimentos del 12/11/2026 sobre redes circulares de grado seis. Dos profesiones no implican cuatro: cada individuo necesita tres categorías complementarias, pero en V24 cada donante solo puede emitir un regalo por ronda. Actores privados, entrenamiento simultáneo sin preentrenamiento y costo final 0,12.

## Resultados finales congelados en escenarios de desarrollo

| Política | N | Actualizaciones | Alimento | Donaciones | Cobertura realizada | Cobertura potencial | Plenitud | Cota de alimento por tasa real de donaciones |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v24_K4_N48_s3111 | 48 | 1000 | 0.1998 | 0.036% | 0.0001 | 0.9647 | 0.0000 | 0.2001 |
| v24_K4_N48_s4111 | 48 | 1000 | 0.1998 | 0.036% | 0.0001 | 0.9769 | 0.0000 | 0.2001 |
| v24_K4_N120_s3111 | 120 | 1000 | 0.1998 | 0.043% | 0.0001 | 0.9366 | 0.0000 | 0.2001 |
| v24_K4_N120_s4111 | 120 | 1000 | 0.1998 | 0.041% | 0.0001 | 0.9468 | 0.0000 | 0.2001 |
| v24B_K4_N48_s3111 | 48 | 1800 | 0.1998 | 0.040% | 0.0001 | 1.0000 | 0.0000 | 0.2001 |
| v24B_K4_N48_s4111 | 48 | 1800 | 0.1998 | 0.043% | 0.0001 | 0.9983 | 0.0000 | 0.2001 |

Las cuatro condiciones V24 (N48 y N120, dos inicializaciones por tamaño) colapsan a prácticamente ninguna donación. La capacidad de red para acceder a roles complementarios sigue alta y la cobertura material efectiva se aproxima a cero. La cota ajustada a la tasa real de donaciones permite comprobar que el colapso de alimento es compatible con la contabilidad material del modelo.

## V24b — Intento preregistrado después del fracaso exploratorio a u200

Protocolo alternativo: precio 0,002 hasta u800, elevación lineal hasta 0,12 entre u800 y u1100, después precio fijo hasta u1800; N48 y dos semillas. El archivo v24b_protocol.json documenta la excepción a la configuración heredada V24. Evaluación siempre con precio final 0,12.

| Modelo | Actualización | Coste al entrenar | Alimento evaluado a coste alto | Donaciones a coste alto | Cobertura efectiva |
| --- | --- | --- | --- | --- | --- |
| v24B_K4_N48_s3111 | 1 | 0.0020 | 0.2035 | 0.5118 | 0.1202 |
| v24B_K4_N48_s3111 | 300 | 0.0020 | 0.2082 | 0.2231 | 0.0642 |
| v24B_K4_N48_s3111 | 600 | 0.0020 | 0.2079 | 0.1824 | 0.0546 |
| v24B_K4_N48_s3111 | 900 | 0.0413 | 0.2022 | 0.0546 | 0.0163 |
| v24B_K4_N48_s3111 | 1200 | 0.1200 | 0.1998 | 0.0020 | 0.0005 |
| v24B_K4_N48_s3111 | 1500 | 0.1200 | 0.1998 | 0.0006 | 0.0002 |
| v24B_K4_N48_s3111 | 1800 | 0.1200 | 0.1998 | 0.0004 | 0.0001 |
| v24B_K4_N48_s4111 | 1 | 0.0020 | 0.2049 | 0.4982 | 0.1199 |
| v24B_K4_N48_s4111 | 300 | 0.0020 | 0.2115 | 0.2877 | 0.0839 |
| v24B_K4_N48_s4111 | 600 | 0.0020 | 0.2113 | 0.2573 | 0.0770 |
| v24B_K4_N48_s4111 | 900 | 0.0413 | 0.2027 | 0.0686 | 0.0203 |
| v24B_K4_N48_s4111 | 1200 | 0.1200 | 0.1998 | 0.0021 | 0.0006 |
| v24B_K4_N48_s4111 | 1500 | 0.1200 | 0.1998 | 0.0007 | 0.0002 |
| v24B_K4_N48_s4111 | 1800 | 0.1200 | 0.1998 | 0.0004 | 0.0001 |

Un periodo barato prolongado retiene donaciones moderadas y alimento ligeramente por encima del baseline durante etapas tempranas, pero ambas políticas vuelven a dejar de donar cuando se impone el coste elevado. No se observa conservación estable de reciprocidad.

## Interpretación matemática: factibilidad y límites

Teorema en V24_TEOREMA_FACTIBILIDAD.md, comprobado con regresiones en test_v24_feasibility.py. Si G es la cantidad de regalos emitidos y cada donante puede hacer como máximo uno, la cantidad de necesidades distintas satisfecha no supera G; cada destinatario completamente abastecido requiere k-1 bienes. Por tanto, con g=G/N se verifica plenitud media ≤g/(k-1), y alimentación media ≤0,20+g(0,80/(k-1)−c), antes de costes de cambio de profesión.

Para k=4 y c=0,12, el máximo de alimento medio para todas las políticas posibles es 0,3467 (q=1), y la plenitud máxima por ronda es un tercio. No se debe evaluar la calidad de estos experimentos comparándolos con alimentos de 0,7 de la sociedad k=2, pues ese valor es materialmente imposible bajo la capacidad de producción de V24. Para k≥8, regalar unidades a coste 0,12 jamás puede elevar la alimentación social media sobre 0,2 en este modelo unitario, por el límite de beneficio incremental por categoría.

## Próximo contraste V25

Abrir tres decisiones voluntarias de donación por persona y por ronda, manteniendo la posibilidad de rechazo y el aprendizaje privado. Dos condiciones: precio 0,12 por unidad y precio 0,04 por unidad. La primera prueba el aumento de capacidad con precio unitario idéntico; la segunda controla el gasto máximo total a 0,12. El oráculo determinista de pleno abastecimiento (0,64 y 0,88) solo verifica factibilidad matemática, no constituye una política aprendida.

## Reproducibilidad

Entrenador v24_k4_joint.py, protocolo de coste v24b_delayed.py, artefactos runs/v24_K4_N*/ y runs/v24B_K4_N48_*, especificaciones, logs, checkpoints y scripts de test. Las pruebas de integridad del laboratorio superan 50 casos.

Hashes SHA256:
v24_k4_joint.py: fc006193518a27f007505c3b58db1781a88e83ddbdd96d7464b7ebe4dd4d1b6b
v24b_delayed.py: 15bbed1e80914b5c894f5c248a450ba5239c7f6ba0eb010e64be747cab2ae352
test_v24_k4.py: 846e1ca8ca2fb1ba4cbf9d0d2c51cf2778e8d0611ad1602f101d3db14035fd13
test_v24_feasibility.py: cbe5b2741484d5910c50709f34830b78535c74d2908a874c7a5b0ad032a643dc
V24_TEOREMA_FACTIBILIDAD.md: 77417f353b2f55656c7c26cb07eede228cca323898212f8686c34f0162b0f2f3
PREREG_V24_SCALING_K4.md: 3153c1d1edd27d7242f477a59ed5a0b73ed9ec0472c77e5556977c553565e8aa
PREREG_V24B_DELAYED_COST.md: c7f97ea93f063424fea43c088e804c2a85f1e441ab9c2ca1e918f6f4410a0d0c