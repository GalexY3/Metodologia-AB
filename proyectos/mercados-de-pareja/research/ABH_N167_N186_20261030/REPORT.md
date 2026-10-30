# AB-H N167–N186 — Predicción diferencial adversarial, etapas y depuración de fuentes

**Cierre 2026-10-30.** Desde HEAD autorizado `d7da22a8926ee0c05c1e2ef6bd84e19dd4463ee8`; rama `research/ab-h-esbm-adversarial-benchmark-20261030`, **sin fusionar ninguna rama ni PR anterior**. 20/20 fichas A–J ejecutadas: **17 verificaciones técnicas/computacionales PASS**, **3 auditorías documentales negativas/no-go válidas** (N182–N184), cero ciclos completos inválidos o meramente de planificación, dos intentos instrumentales fallidos y preprerregistradamente reparados (N167 y N185). Ninguna validación externa humana, ningún dato humano nuevo descargado, original ESBM v2 y SRC104 sin alterar. **CT2 ordinal científica 7/100, STOP_R5 humano activo, grado científico nuevo 0/3.**

## 1. Congelación prospectiva y alcance

Verificados `AGENTS.md`, AB3.2.1/O1–O7, `CURRENT.md`, N147–N166, protocolo histórico de rivales y fuente original Python SHA256 `f7e6b84000720cbdf2ee0800c2b10d136185facd00e4622756cbb5f8d8254d0b`.

| Bloque / ciclos | Prerregistro A–J GitHub **antes del outcome** | Fuente exacta congelada antes del outcome |
|---|---|---|
| A N167–N171 | `613bfa643fc6cff8b86ff6bb2d82c5635eb20417` | `CODE_FREEZE_A.json` commit `dcf9f8b5b230424a0aded31f9a9cd8786aede980`; reparación por silencio sin propuesta `N167_REPAIR_PREREG.md` `b94bb3afd1b5075a10bd9d718eb3406d7b2ed315`, `CODE_FREEZE_A_REPAIR.json` `db4b418cf61286f19e7b89a4d82356f2d247ce95` |
| B N172–N176 | `fd0caaffa5289cb47192f83e9e017ff133503db4` | `CODE_FREEZE_B.json` commit `6ed9b848c3ddf8cd496ef04120f90625d41458ed` |
| C N177–N181 | `3b9e12c81d3413b1221af286d6e4d65848b24afe` | `CODE_FREEZE_C.json` commit `e9935bd5aefbe7ed2e0cad57cebc4fb82fea3b98` |
| D N182–N186 | `44aee165ac418682972e2faa81b57e699c408842` | Documento `CODE_FREEZE_DOCUMENTARY.md` commit `7cb470b6e78ea19480d2cb22cf951fc0a4f29d3`; dashboard `CODE_FREEZE_D.json` commit `ca7215696684a9b0e52d9e5cd1957b95c960a52c`; reparación Chromium `N185_REPAIR_PREREG.md` commit `027810fe367840b3136f06795ac2d7c5c88d9325`, `CODE_FREEZE_D_REPAIR.json` `00bd6515eae4a7884c0b571a0d0a17ee53bc445a` |

Los cinco scripts y sus SHA256 exactos están en [RESULTS_INDEX.json](RESULTS_INDEX.json) y ZIP reproducible **de esta conversación**, no se afirma que el código binario del ZIP esté subido a GitHub. [LEDGER_A.json](LEDGER_A.json), [B](LEDGER_B.json), [C](LEDGER_C.json) y [D](LEDGER_D.json) contienen las 20 fichas A–J y sus resultados. Recibos íntegros por semilla `RESULTS_A/B/C.json`, documento `RESULTS_D_DOCUMENT.json` y `RESULTS_D_UI.json` están en el ZIP con hashes; los informes GitHub no los sustituyen.

## 2. N167–N171: predicción de propuestas, no votos humanos

El motor Python sintético se ejecutó para **60 semillas de entrenamiento 7100–7159** y **40 semillas nuevas 8100–8139**, con cohortes completas bloqueadas entre entrenamiento y evaluación. Variables de predicción congeladas **antes** de cada exposición: coincidencia normativa, brecha edad, calidad latente artificial q de cada agente, tick, número anterior de exposiciones, estado de feedback anterior. Resultado: **propuesta emitida por un agente frente a un encuentro programado** (no dos sí/no nativos de personas).

N167 instrumento: **3.608 exposiciones de entrenamiento y 2.365 de evaluación**, 28,8 % y 28,3 % de propuestas. Un intento inicial INVALID_INSTRUMENTAL falló al no cerrar exposición sin propuesta; se documentó y corrigió con SHA frozen **antes de volver a ejecutar**; no constituye ciclo adicional.

N168 evaluó misma muestra y etiquetas con log-loss/Brier:

| Modelo operativo | Log-loss 40 semillas | Advertencia |
|---|---:|---|
| B0 constante | 0,5957 | No es B0 compuesto con riesgo completo |
| B1 edad/norma | 0,5945 | **No equivale** a B1 actor-target SRM |
| B2 q, edad, norma | 0,5746 | Usa q artificial conocido |
| B4 temporal/exposición | 0,5747 | Ranking/fatiga/capacidad históricos incompletos |
| B6 boosting flexible | 0,5806 | No es B6* historia saturada |
| ESBM oráculo | 0,5741 | Conoce parámetros de la verdadera ley generadora |

N169 comparación por semilla B2−oráculo **+0,000526** media, ventaja del oráculo en **23** cohortes y pérdida en **17**. N170 permutación negativa dentro de semilla y tick, train+test por separado: ESBM oráculo **0,6070** frente a B0 **0,5957**, sin superioridad general; N171 red reordenada holdout **2.412 exposiciones** B2 0,5780, oracle 0,5765: presupuesto de oportunidades distinto, no intervención causal de red.

## 3. N172–N176: replicación por nuevas semillas, generadores hostiles y SRM limitado

N172 añadió **80 semillas completamente nuevas 9100–9179**, n=4.796 propuestas posibles, y bootstrap por semilla (4.000 remuestras RNG 1720, congelado antes): log-loss ESBM 0,5600, B2 0,5608, B6 0,5665 y B0 0,5811. **Diferencia media por semilla B2−oráculo +0,00099, intervalo interno 95 % [−0,000227, +0,002346] incluye cero**. No es intervalo de población humana ni evidencia de originalidad.

N173, DGP adversarial donde la calidad q atrae con **signo opuesto**: el oráculo original (sin cambiar sus coeficientes) **0,6468** y B2 entrenado para DGP nuevo **0,5799**. N174, DGP iid Bernoulli 0,28: oráculo **0,6163** y B0 **0,5976**. Ambos son generadores artificiales, controles de falsación y sensibilidad de especificación, no eventos humanos.

N175 segmentó receptor de propuesta según etiquetas F/M/X ficticias, n=2.108/1.913/775, sin atribuir desigualdad real a ninguna categoría. N176 estimó un baseline SRM **parcial** de efectos sender/receiver mediante suavizado empírico Bayes (historia t0–t2 de la misma cohorte) y predijo t3 sobre n=539: SRM 0,5872; B0 0,5866; B2 0,5625. No equivale a SRM multinivel actor–partner–díada ni prueba injustamente rendimiento fuera de cohorte.

## 4. N177–N181: separación estricta de medición bilateral

N177–N181 reconstruyeron de las trazas **propuesta unilateral**, **respuesta positiva si hubo propuesta** y **evento conjunto**. 60 semillas 7200–7259 para entrenar, 80 nuevas 9400–9479 para evaluar: 3.537 y 4.789 exposiciones; 992 y 1.300 propuestas; 284 y 381 respuestas positivas, respectivamente. El oráculo predice `P(propuesta)×P(respuesta positiva|propuesta)` del programa. **NO es un par de dos votos humanos autónomos y no mide relaciones persistentes por sí mismo**.

N178 evento conjunto sobre 4.789 exposiciones: ESBM **0,26606**, B2 **0,26623**, B6 **0,26863**, B0 **0,27769** (log-loss). N179 respuesta condicional (solo 1.300 propuestas): ESBM **0,58843**, B2 **0,58917**, B0 **0,60498**. N180 red reordenada contra red anular, n=4.764: ESBM **0,26353**, B2 **0,26346** (B2 ligeramente mejor). N181 bootstrap de semilla de este evento conjunto: media B2−oráculo +0,000236 con **intervalo [−0,000251,+0,000747]**, 39 signos a favor de oracle, 41 contrarios. No se identifica ventaja robusta.

## 5. N182–N184: hallazgos documentales negativos y puerta legal

[DOCUMENTARY_AUDIT.md](DOCUMENTARY_AUDIT.md) registra el contrato adversarial:

- **N182**: entre 107 registros previos, 61 `canonical_url` contenían DOI, **58 únicos y tres pares duplicados**: `SRC003/SRC075`, `SRC029/SRC093`, `SRC087/SRC107`. La anterior afirmación de «nueva fuente SRC107» era incorrecta: **SRC087 ya contenía el mismo paper Ogushi et al. DOI 10.3389/fcomp.2026.1893669**. Se ha rectificado preservando IDs. No se deduce independencia de los otros 46 sin DOI.
- **N183**: tras leer las definiciones históricas B0/B1/SRM/B2/B4/B6, se rechaza **equivalencia completa** con proxies de esta campaña: B1 implementado como edad/norma no es SRM, B4 omite orden/fatiga/capacidad completos y B6 HistGradientBoosting finito no es el B6* saturado/histórico. **No se afirma una victoria contra baselines históricamente competentes**.
- **N184**: nuevo registro bibliográfico `SRC108`, depósito de replicación [Harvard Dataverse DOI 10.7910/DVN/27893](https://doi.org/10.7910/DVN/27893), que el catálogo NLM marca CC0; artículo original Bhargava–Fisman 2014 confirma que deriva de las **mismas sesiones Columbia 2002–2004**, ya incluidas en SRC016/SRC082. URL primaria de Dataverse inaccesible, licencia por fichero/bytes/clave no verificados y ningún caso original leído. **No constituye cohorte independiente** ni desbloquea R5.

La lista suma **108 entradas bibliográficas**, pero con al menos tres DOI duplicados y varias publicaciones sobre la misma cohorte. No representa 108 estudios independientes. El hallazgo científico previo de «novedad SRC107» se retracta como dato documental, no se elimina su registro histórico.

## 6. N185–N186: producto y verificación

N185: nueva interfaz web **HTML autocontenida** construida desde los resultados reales A/B/C, con selector de **siete escenarios**, comparación explícita log-loss y Brier e identificación visible de oráculo/controles y límites. HTML **8.759 bytes**, SHA256 `099c0435fef63cf25494477dceefa5a994e0447d8bde567ba542cb15634ef568`. Prueba de browser: **7/7 selecciones reales en Chromium /usr/bin/chromium**, cero errores JavaScript, cero peticiones HTTP externas, captura PNG dentro del ZIP. Un primer intento falló porque faltaba el ejecutable Playwright bundled; se registró y reparó con nuevo prereg/commit SHA antes de la prueba válida.

N186: cálculo de log-loss en un **subproceso Python aislado**, implementación aritmética nueva con `math.fsum` y `log1p` (no usa `sklearn.metrics`) aplicado a las mismas predicciones de seis modelos; **máximo error absoluto 2,22e−16** contra recibos originales. Subproceso en el **mismo OS y bibliotecas instaladas**, no replicación independiente por autor o máquina.

## 7. Cierre O7, priors, madurez

[RESULTS_INDEX.json](RESULTS_INDEX.json) y cuatro LEDGER contienen 20 resultados, controles, falsadores, SHA y decisiones A–J; el ZIP conserva los recibos íntegros y código. **108 SOURCES/34 PRIORS** (+`P-SOURCE-DEDUP`, solo control documental) **/187 UPDATES** (U183 corrección de duplicados; U184–U187 `NO_CHANGE_WITH_REASON` sobre rivales, novedad, acceso diádico y oportunidades). Nunca se accedió a los microdatos humanos de SRC104, ningún SSJY, no se aceptaron licencias, no se contactó a autores.

**CT2 científico 7/100, grado empírico nuevo 0/3 y STOP_R5**. Madurez ponderada subjetiva **43,60→43,70 %** (+0,10 puntos), exclusivamente QA 72→73, por auditoría duplicados, aritmética independiente y visor probado; sin subir simulador estructural, teoría, originalidad, evidencia real, validación ni manuscrito. No premiar volumen de ciclos.

**Decisión AB-DECIDE:** campaña 20/20 cerrada y STOP humano R5. Siguiente salto científico requiere datos **legalmente reutilizables de otra cohorte**, oportunidades observadas, dos decisiones nativas no condicionadas, información pre-outcome equivalente para **SRM y B6 histórico real**, y diseño anticipado de falsación ESBM. Sin ellos el programa sigue siendo simulación formal, no explicación causal exterior demostrada. No fusionar `main` ni PR existentes.
