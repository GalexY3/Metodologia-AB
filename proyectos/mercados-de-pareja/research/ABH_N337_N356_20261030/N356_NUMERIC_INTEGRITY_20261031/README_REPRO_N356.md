# N356: instrucciones de reproducción

Este ciclo investiga exclusivamente la exactitud del campo numérico full_units_in_2_power_minus52; no ejecuta el estudio de personas reales ni reproduce las 60 trayectorias históricas.

Prerregistro congelado antes de outcomes: dec8fa73876a0ac80b4add10b91d71e48bea3a04. Reparación del oráculo Python congelada antes de su segunda ejecución: b4f8d831a9e682a9b51483595b63d520fea33465.

Entorno original: Node.js 24.16.0 y Python 3.14.3, desde C:\Users\Nitropc\CoS-Prueba\ESBM_ABH_N339_N356_20261031.

Para reproducirlo en una carpeta nueva, crear instrument/, work/src/, vendor/ y outcomes/. Copiar a instrument/ el archivo n356_numeric_precision_boundary.mjs y la versión reparada n356_independent_bigint_oracle_REPAIR_V2.py renombrada n356_independent_bigint_oracle.py. Copiar a work/src/ los archivos blossom_matching_RUNTIME_FROZEN.mjs, matching_RUNTIME_DEPENDENCY.ts y types_RUNTIME_DEPENDENCY.ts, con nombres de destino blossom_matching.mjs, matching.ts y types.ts. Copiar blossom_with_state_RUNTIME_FROZEN.cjs a vendor/blossom_with_state.cjs. Todos se incluyen en esta carpeta de GitHub, junto con la licencia MIT del proveedor.

Ejecutar, por orden: (1) node instrument/n356_numeric_precision_boundary.mjs ; (2) py -3 instrument/n356_independent_bigint_oracle.py.

Los scripts se niegan a sobrescribir los outcomes previos. El primer instrumento crea doce grafos disjuntos nuevos con pesos IEEE-754, ejecuta Blossom y calcula una referencia BigInt. Python reconstruye independientemente los pesos con Fraction.from_float y comprueba dos mutantes. Resultado esperado: doce matching certificados; nueve objetivos auxiliares inexactos; tres correctos; un único campo safe integer.

SHA256 JS 5b85db6726abe41e8920f8ad2f90a851a198023e10d6623109ed09a92162df74; Python V2 2e09792bc1843a59103cc27a7483a1890d8903a31adf548b2ae9d78872148aa3; wrapper Blossom 9b6fd317dd05229c45fa5ee60bf71af226dd307fa2a558c1abb332b93017b19d; backend 1b6f24f1b2aba321ec8c1a14cd045a7f673cfacf60ac4fe456666d31ee5806a2.

Resultados archivados: JS SHA256 8ecf9395834ee96c98c9cb5c39ec692eea0f3944895b464515d9e6e7c9e2fef5; oráculo SHA256 eee65d33af9b7a4ec0af62953235d9c45254d934ad09d55edc5ed4201bf17f08.

Un error numérico en este campo auxiliar no invalida por sí mismo las parejas elegidas ni constituye evidencia humana. CT2 7/100 y STOP_R5 siguen activos.
