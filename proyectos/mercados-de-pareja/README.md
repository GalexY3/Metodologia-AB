# Mercados de pareja: homogamia emergente sin preferencia por semejanza

**Proyecto AB-R (autoría de investigación: Alejandro Panera Pascual)**. Proyecto hermano de `proyectos/politics-fantasy-league/`, deliberadamente más ligero. **Estado: piloto exploratorio, sin hallazgo 2/3 ni calibración empírica.** Rama de trabajo: `research/ab-r-mercados-pareja-20261028`. Corte: 28/10/2026.

## Pregunta
¿Puede aparecer similitud en valor relacional de los integrantes de una pareja a partir de búsqueda individual de la mejor opción alcanzable, aceptación bilateral y salida del mercado, aunque nadie prefiera directamente la semejanza? ¿En qué condiciones la búsqueda, el estatus dinámico, la población elegible y la fragmentación modifican esa estructura?

**Valor**: deseabilidad según el sexo opuesto. En el piloto las mujeres ponderan estatus 0,6 y belleza 0,4; los hombres, estatus 0,4 y belleza 0,6. Son **supuestos**; los agentes son binarios y heterosexuales en este prototipo, nunca una descripción exhaustiva de España. `Status` y `looks` sintéticos están en [0,1]; no se emplean datos personales reales.

## Orientación metodológica
- [Contrato previo, 10 ciclos](research/ABR_MATE10_20261028/PREREG.json): `3fce00eb`, antes del código/resultados.
- [Código congelado antes de ejecutar](research/ABR_MATE10_20261028/experiment.py.gz.b64): commit `a5ca4215`; SHA-256 del **Python descomprimido** `ca792b6c685beb075153659b862475425ed9a4ead74ad4e36e65729ceef6df7e`.
- [Resultados por condición](research/ABR_MATE10_20261028/SUMMARY.csv), [ledger A–J](research/ABR_MATE10_20261028/LEDGER.json), [informe](research/ABR_MATE10_20261028/REPORT.md), [estado](CURRENT.md).
- Contrato AB 3.2.1 R1–R5, O2 freeze-run y O4 niveles 0–3. Cuatro ciclos `PLANNING_AB_ONLY` basados en fuentes; seis `EXPERIMENTAL_AB` sintéticos; **no se intercambian**.
- Es imprescindible contrastar contra la literatura, especialmente Hitsch et al. (2010), que ya documenta sorting derivado de preferencias. Originalidad aún **NO_ACREDITADA**.

## Reproducir
El archivo congelado es gzip + base64 debido a la interfaz de conservación remota. Descifrarlo y ejecutar desde el directorio de la campaña:
```bash
base64 -d experiment.py.gz.b64 | gzip -dc > experiment.py
sha256sum experiment.py  # esperado: ca792b6c685beb075153659b862475425ed9a4ead74ad4e36e65729ceef6df7e
python -m pip install numpy pandas scipy
python experiment.py
```
Produce `RUNS.csv`, `SUMMARY.csv` y `NULLS.csv`. `CLEAN_CLONE_NOT_VERIFIED`; la ejecución comprobada se realizó en un contenedor local, no en un clon limpio. El script implementa swipes **simultáneos**, no Tinder asincrónico; los candidatos pueden reaparecer entre rondas. La regla de pérdida de estatus `delta` se aplica solo después de rechazo unilateral y es globalmente visible a todos los candidatos.

## Mapa de preguntas
```mermaid
flowchart TD
    R["Homogamia de valor emergente"]
    R --> M["Mecanismo y rivales"]
    R --> D["Datos y validez española"]
    R --> E["Contrastes internos"]
    M --> C01["C01: Estado del arte"]
    D --> C02["C02: Elegibilidad"]
    D --> C03["C03: Medida de estatus"]
    D --> C04["C04: Validez externa"]
    E --> C05["C05: Feedback"]
    E --> C06["C06: Preferencias"]
    E --> C07["C07: Pools locales"]
    E --> C08["C08: Pérdida real estatus"]
    E --> C09["C09: Gusto idiosincrático"]
    E --> C10["C10: Sexo y nulos"]
```
Las relaciones son de agenda/investigación, **no** de causalidad demostrada.

## Límites éticos y epistémicos
Las ponderaciones de género son convenciones experimentales sin validación normativa ni empírica. «Belleza» no se aplica a seres humanos reales. Las simulaciones sintéticas no identifican efectos sociales causales ni justifican puntuación individual de personas. Antes de probar sectores españoles, definir usuarios elegibles, consentimiento, cohortes y variables con fuente, sesgos y restricciones.

## Segunda campaña · BRANCH8 (28/10/2026)

**Autorización expresamente concedida, ocho ciclos completos A–J en sus alcances**, de los cuales cinco fueron experimentos sintéticos exploratorios y tres ciclos documentales/de planificación. Informe [BRANCH8](research/ABR_BRANCH8_20261028/REPORT.md), [ledger](research/ABR_BRANCH8_20261028/LEDGER.json), [contrato previo](research/ABR_BRANCH8_20261028/PREREG.json), [métricas por semilla](research/ABR_BRANCH8_20261028/RUNS_COMPACT.csv), [gráficas CT2](research/ABR_BRANCH8_20261028/CT2_TRAJECTORY.svg). Las dos implementaciones observadas se diferencian por hashes y no se cuentan como campañas adicionales. El resultado N03 sobre tamaño local fue inconcluso por baja cobertura; N08 no ejecutó una confirmación humana. Ningún nuevo hallazgo 2/3.

**Prioridad actual**: baseline Gale-Shapley con paridad, similitud de oportunidades de exposición, calibración sociodemográfica por población elegible y observación reputacional bajo condiciones éticas. [Estado vigente](CURRENT.md). [Próximos 6 ciclos propuestos, sin autorización](NEXT_6_PROPOSAL.md). El visor HTML es una vista estática del mapa piloto, no un replay canónico certificado; consultar `ab_atlas/seed.json` para el grafo más reciente.

## Tercera campaña autorizada · EVIDENCE6

[Prerregistro](research/ABR_EVIDENCE6_20261028/PREREG.json), [informe N15–N20](research/ABR_EVIDENCE6_20261028/REPORT.md), [ledger A–J](research/ABR_EVIDENCE6_20261028/LEDGER.json), [fuente Python congelada](research/ABR_EVIDENCE6_20261028/experiment.py) y [CSV por semilla](research/ABR_EVIDENCE6_20261028/RUNS.csv). Se cerraron **6 ciclos** con alcance limitado (2 pruebas sintéticas, 3 documentales y 1 planificación), sin 2/3 y sin calibración humana externa. La equivalencia exacta de sincrónico/asíncrono con q fijo es un control negativo construido, no un descubrimiento sociológico. Se conserva la no-derivación de población soltera desde censos y el bloqueo de acceso a las tablas 59583 y 60268. [Estado canónico](CURRENT.md), CT2 [escala 0–100 y ampliada](research/ABR_EVIDENCE6_20261028/CT2_TRAJECTORY.svg). R5 detiene nuevos ciclos sintéticos hasta evidencia externa pertinente.

## Quinta campaña · EVIDENCE20: siete ciclos ejecutados, trece no iniciados por R5

El investigador autorizó **hasta 20 ciclos BRANCHING AB-R**. Se realizaron **siete ciclos A–J** N21–N27 (dos revisiones documentales de fuentes y una adicional sobre rechazo, una prueba formal, un experimento sintético, un reanálisis y una planificación), sin invalidaciones registradas. Los trece restantes **no fueron ejecutados ni consumidos**, en aplicación de R5; la autorización no equivale a resultados. [Estado](CURRENT.md), [informe](research/ABR_EVIDENCE20_20261028/REPORT.md), [ledger](research/ABR_EVIDENCE20_20261028/LEDGER.json), [prerregistro](research/ABR_EVIDENCE20_20261028/PREREG.json), [código Python](research/ABR_EVIDENCE20_20261028/audit.py), [CSV sintético 5 semillas](research/ABR_EVIDENCE20_20261028/SEGMENT_NULLS.csv), [CT2 doble escala](research/ABR_EVIDENCE20_20261028/CT2_TRAJECTORY.svg).

Hallazgos de corrección: (1) rankings comunes implican matching estable rank-rank bajo condiciones especiales y no requieren homofilia; (2) la mera segmentación puede generar r≈.92 global incluso si el apareamiento intragrupo es aleatorio, por lo que los nulos deben preservar el grafo de oportunidad; (3) Funcas publica datos ESS 2024 de educación de convivientes españoles, **no swipes ni valor romántico**; (4) la ficha pública del experimento de citas de Essex 2018 declara un Excel anonimizado pero la descarga y columnas permanecen sin verificar. Ningún descubrimiento 2/3 ni validación causal real.
