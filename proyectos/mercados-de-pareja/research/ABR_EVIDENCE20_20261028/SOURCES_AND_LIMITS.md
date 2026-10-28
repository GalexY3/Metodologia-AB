# Fuentes externas verificadas · AB-R EVIDENCE20 · 28/10/2026

## N21 · Funcas y ESS 2024 (hallazgo externo descriptivo, no confirmación de nuestro modelo)

Se leyó y **se inspeccionó visualmente la figura 3, página impresa 7** (índice PDF 6) de [Funcas, *Focus on Spanish Society*, diciembre 2025](https://www.funcas.es/wp-content/uploads/2025/12/2512-Focus_final.pdf). Muestra: países UE participantes en ESS ronda 11 (2024), **personas de 25–50 años que conviven con su pareja**, ponderación `pspwght`. El documento presenta:
- Entre **hombres españoles universitarios convivientes**, 76 % viven con pareja universitaria.
- Entre **mujeres españolas universitarias convivientes**, 53 % viven con pareja universitaria, frente al 64 % de promedio europeo *de mujeres universitarias*.
- Entre **hombres españoles no universitarios convivientes**, 30 % viven con pareja universitaria.
- Entre **mujeres españolas no universitarias convivientes**, 12 % viven con pareja universitaria.
- Por separado, convivencia en España, 25–29 años 27 % frente a media de UE 42 %, 30–35 España 58 % frente a UE 64 % (figura 1). Es **convivencia**, no proporción con pareja, soltería ni app.
- No se descargaron microdatos de ESS, ni se calcularon intervalos, márgenes o matrices. Prohibido usar 53 % como tasa general de homogamia de todas las parejas españolas, o deducir aspiración de género directamente de composición.
- Son **porcentajes condicionales por sexo y nivel educativo propio**, denominadores diferentes. La asimetría puede tener componentes de composición educativa del pool y selección por convivencia.

Un condicionamiento clave: si hombres y mujeres convivientes perteneciesen a un conjunto de parejas heterosexuales completo, medido con pesos compatibles, `0.53 N_mujeres_universitarias = 0.76 N_hombres_universitarios`; sería una restricción algebraica aproximada, no un valor demográfico directamente observado. No calculamos esas poblaciones por falta de microdatos y ponderaciones consistentes.

## N22 · Disponibilidad real de datasets de dating

- [Josué Ortega, *Rational Inattention in Online Dating* (Universidad de Essex, 2018)](https://researchdata.essex.ac.uk/85/): experimento de campo en Londres y Essex (mayo–agosto 2018), aprobación ética y prerregistro AEA RCT 2247. Ficha explícita de archivo `AnonymizedData.xlsx` 67 kB, CC BY 4.0, acceso público. **Se abrió la ficha pero el Excel no se descargó** mediante web ni container; contenido/columnas/suficiencia para aristas diádicas **NO VERIFICADOS**. Fuente potencial, no dato analizado.
- [SwipeStats, página de investigación](https://www.swipestats.io/research): el proveedor dice disponer de perfiles y recuentos de swipes/matches diarios de usuarios que aportaron sus exportaciones; se comprobaron metadatos y sample visible, pero **no se descargó su dataset** ni se verificó su representatividad. Una fila por usuario y estadísticos agregados no permite reconstruir las parejas `(i,j)` y rasgos de ambos ni las exposiciones bilaterales, salvo contrato de datos de tipo distinto.
- [Hitsch, Hortaçsu y Ariely (2010), AER](https://doi.org/10.1257/aer.100.1.130): estudio precedente con registros de sitio de citas, estima preferencias y predice matching estable que reproduce sorting observado. Su existencia afecta directamente a la novedad científica. No se descargó un dataset de replicación completo.
- [Ershov, Fong y Yildirim (2026), NBER WP 34757](https://www.nber.org/papers/w34757): análisis de mercados matrimoniales estadounidenses, diferencias entre dating desktop/móvil y sorting por educación, empleo y raza. **No valida** causalidad o coeficientes sobre España; sugiere que tecnología no tiene un efecto homogéneo en todos los atributos.
- [Hu y Markowitz (2026)](https://doi.org/10.1177/02654075261429319): dos experimentos preregistrados de elección entre 31 o 6 perfiles (N=193 y N=342); ya estudia relación entre tamaño del conjunto, valoración y persecución relacional, con datos OSF declarados. **No se descargaron sus datos** y su tarea experimental no equivale a un matching bilateral real. Prior art adicional.

## N26 · «Pérdida de estatus» vs resultados psicológicos de rechazo

- [Campaioli et al., *New Media & Society* (2025/2026)](https://doi.org/10.1177/14614448251336437): estudio de diario de un mes con 8 participantes; señales de actividad, vigilancia y seguridad tras rechazo; no estima una pérdida cuantificable de reputación *ante terceros por cada swipe negativo*.
- [*Swipe, Chat, Unmatch*, 2026](https://doi.org/10.1080/15213269.2026.2633228): dos experimentos preregistrados de unmatch y conversación, efectos psicológicos de rechazo; no demuestra la difusión automática a terceros de cada swipe.
- Constructos a mantener separados: `R_private` historial individual de rechazo, `R_public` evaluación por espectadores informados, `S_material` renta/educación/ocupación; ninguna de estas variables equivale a otra por definición.
- Prueba que sí discriminaría: medir señal reputacional observable a un tercero y variación de su valoración bajo exposición aleatorizada ética, preservando historial de candidatos y consentimiento. La caída del score impuesta en un agente simulado es una intervención de software, no evidencia social.

## Límites comunes
La ficha bibliográfica no equivale al archivo de datos; los porcentajes de cohabitación no equivalen al universo de usuarios activos. Las correlaciones de valor de nuestros simuladores no se pueden enfrentar directamente a una probabilidad condicional de educación sin definir rasgos, cohortes, selección y exposición.
