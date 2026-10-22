# AB 3.2.1-O2 — Intervenciones y ejecución reproducible

**Fecha:** 22 de octubre de 2026. **Estado: ADOPTADA_NORMATIVAMENTE como ampliación operativa prospectiva**, por autorización del investigador para mejorar AB durante la campaña LARP. Su eficacia metodológica comparada permanece **NO_VALIDADA**. O2 complementa el núcleo 3.2.1 y O1; no constituye AB 3.3 ni modifica priors históricos.

## Cuatro reglas proporcionales al problema

1. **Preprocesado = intervención.** Declarar centrado, escala, umbrales, clipping, orden de operaciones y datos usados para ajustarlos. Estimar esos parámetros solo con entrenamiento cuando el diseño lo requiera. Si se cambian varios componentes, el contraste estima la intervención compuesta. Atribuir el efecto a un componente exige aislarlo o justificar su identificación; una reparación nominal no basta.
2. **Control convencional competente.** Antes de atribuir una mejora a arquitectura o geometría, comparar una pipeline convencional con acceso, preprocesado y presupuesto pertinentes. Igualar parámetros no iguala información. Distinguir cambios de representación, filtrado, estabilidad numérica y nueva información; si procede, auditar rango y condicionamiento del operador. Una transformación invertible puede ser inestable y no implica ventaja funcional.
3. **Freeze–run verificable.** Vincular cada ejecución con commit y hashes del protocolo, fuente, instrumentos comunes e inputs efectivos, o de su especificación y revisión cuando se regeneren. Registrar entorno, seeds, presupuesto y estado del holdout. Comprobar correspondencia antes de ejecutar. Conservar recibos de éxito, fallo, timeout y reparaciones; no convertir una ejecución fallida o incompleta en resultado científico válido.
4. **Portabilidad antes de declarar reproducibilidad.** Dar instrucciones y dependencias suficientes para un clon limpio, rutas relativas o parámetros explícitos y acceso declarado a datos. Identificar cualquier dependencia de archivos, entornos o paquetes locales no versionados. Si no se ha comprobado el clon limpio, declarar `CLEAN_CLONE_NOT_VERIFIED`; una ejecución local satisfactoria no acredita esa portabilidad. No exigir infraestructura nueva si basta una instrucción o comprobación pequeña.

## Evidencia que motiva O2; no valida su eficacia

Fuente fija: [LARP, commit 78269a45bfbc3b8e70428813122b9f648743e9e5](https://github.com/GalexY3/proyecto-LARP/commit/78269a45bfbc3b8e70428813122b9f648743e9e5), campaña `research/AB30_CODEX_20261022`, resultados exploratorios C01–C05.

- [C01](https://github.com/GalexY3/proyecto-LARP/blob/78269a45bfbc3b8e70428813122b9f648743e9e5/research/AB30_CODEX_20261022/cycles/C01/result.json): accuracy bajo ruido de 38,89% en `legacy`, 35,78% en `guard` y 86,44% en `fixed`. Corregir solo la guarda de varianza nula no explicó la fragilidad.
- [C03](https://github.com/GalexY3/proyecto-LARP/blob/78269a45bfbc3b8e70428813122b9f648743e9e5/research/AB30_CODEX_20261022/cycles/C03/result.json): `global` obtuvo 92,44%; frente a `fixed` cambia tanto centrado como escala. No identifica un efecto exclusivo de escala.
- [C04](https://github.com/GalexY3/proyecto-LARP/blob/78269a45bfbc3b8e70428813122b9f648743e9e5/research/AB30_CODEX_20261022/cycles/C04/result.json): el baseline de píxeles con normalización global obtuvo 92,67% bajo ruido frente a 90,81% de MHU, descriptivamente. No es una comparación de arquitecturas completamente convergidas ni evidencia externa independiente.
- [C05](https://github.com/GalexY3/proyecto-LARP/blob/78269a45bfbc3b8e70428813122b9f648743e9e5/research/AB30_CODEX_20261022/cycles/C05/result.json): 17 de 20 operadores tienen rango 64; residuo lineal máximo 8,88e-16. Aumentar a 80 features no crea automáticamente información adicional sobre los 64 píxeles originales.

Los riesgos de ejecución y portabilidad motivan reglas operativas, no constituyen ensayos comparados de metodologías. Costes a vigilar: documentación redundante, integración de comparadores y pruebas innecesarias. Si una regla no puede cambiar la interpretación o decisión, aplicarla de forma más ligera; conservar su limitación, sin afirmar que AB haya mejorado científicamente por adoptarla.

Registro acumulativo: [AB-M023–026 en el observatorio](OBSERVATORIO_AB_MEJORAS_Y_FORTALEZAS.md). Los estados previos y el benchmark de eficacia de AB conservan su interpretación.
