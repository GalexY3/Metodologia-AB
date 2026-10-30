# N280 · Auditoría prospectiva posterior al resultado (NO NUEVO CICLO)

El ciclo N280, bajo contrato A–J congelado en commit `4d92e8002bc24af3dfe6009603e1bc95d2b806ca`, observó dos diferencias en el objetivo exacto codificado entre NetworkX maxcardinality float64 y NetworkX maxcardinality integer: gap 2 y 3 unidades (respectivamente, cardinalidad 71 en n143).

## Pregunta posterior (conoce resultado N280)
¿Coincide el solucionador independiente Boost C++ con la solución de objetivo entero de NetworkX en ambos grafos n143 cercanos a empates, o revela fallo de implementación/recurso?

## Instrumentos
- Código original sin cambios `experiment.py` SHA256 `89d9d5c125c9153ca8a641267a983e71c0427e1600a45faf03d6f3761b125dfe`, `trace_engine.py` SHA256 `c0c92061100a689ab59698a46e22a96e96d7bb3bd99a21ec292d7aaa30e4415a`, binario Boost SHA256 `96087f807c3845193da871aa8a8f83092c095a0dcf2ab0862ace85b76eebf995`.
- Exactamente dos fixtures deterministicamente generados por `make_edges(143,.28,10280,'near')` y `make_edges(143,.28,10281,'near')`, construidos con el runner ya congelado. Registrar SHA del stream de aristas, tamaño n/m.
- Ejecutar `matching_compare(143,e,boost=True,limit=5.0)` por fixture; max 5s de subprocess cada uno. Comprobar estado `PASS`/timeout/error, exact objective, aristas iguales o diferentes, pero no exigir identidad ante empates. No afirmar reproducción literal histórica N242.
- Guardar JSON con `n,` `seed,` `graph_sha,` `boost_state,` `boost_integer_objective_agree,` `floats_gap,` códigos de error y tiempos. Sin reparaciones en el mismo ciclo.
- Cualquier salida posterior es `POST_HOC_DIAGNOSTIC`, NO nueva plaza N277–N296 ni confirmación independiente humana. Conserva R5 humano STOP, CT2 7/100, ESBM original/SRC104 intocados.

**Congelar este documento en GitHub antes de ejecutar Boost contra estos grafos.**
