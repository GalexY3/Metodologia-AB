# N91 · Relabeling de agentes: falla de invariancia en visibility_balancing
**Ejecución real:** 180 simulaciones de Python original SHA-verificado. Contrato A–J y gzip de código congelados en commit `8bf3838f2858948f9201e8d25d89178c92eed64a` **antes de la ejecución**. Script SHA256 `2ea5b39520f86dd35d760f6d29ddac26ff839afa1289aebbb034cf3ceeb2e791`; original SHA256 `f7e6b84000720cbdf2ee0800c2b10d136185facd00e4622756cbb5f8d8254d0b`. [Contrato](PREREG_N91.md), [código](n91_relabel_audit.py.gz), [datos agregados por semilla](RESULTS_N91_COMPACT.json), [ledger](LEDGER_N91.json).

**Estimando:** manteniendo exactamente los mismos 144 agentes, preferencias, scopes, atributos, matrices de shocks y pesos de pareja, permutar etiquetas de identidad arbitrarias no debería cambiar las estadísticas del modelo si la institución no depende del orden de indexado. Las matrices de hazard y matching se simetrizan tomando el upper triangle efectivo que el script original consultaba para cada par, de modo que las mismas parejas experimentan el mismo shock tras cambiar ID. Se comprueba inversa de todos los tensores y ejecución original idéntica para las 36 identidades.

| Política artificial | Formaciones cambiadas / 18 permutaciones | Δ medio formadas | Δ medio Gini |
|---|---:|---:|---:|
| mixed_random | 0/18 | 0.000 | 0.0000 |
| popularity_ranking | 0/18 | 0.000 | 0.0000 |
| institutional_segregation | 0/18 | 0.000 | 0.0000 |
| private_rejection_learning | 0/18 | 0.000 | 0.0000 |
| public_rejection_signal | 0/18 | 0.000 | 0.0000 |
| visibility_balancing | 18/18 | -8.056 | 0.0119 |

**Resultado adversarial:** solo `visibility_balancing` cambia número de uniones en **18/18 relabelings**: Δ medio **−8,056** (mín −32, máximo +19; 14 negativos y 4 positivos), y Δ Gini medio +0.01192. Los cinco controles negativos tienen **90/90 resultados de formación invariantes**. En 9 corridas de private y 3 de public, el diccionario de salida no fue exactamente idéntico exclusivamente por diferencias de último bit en medias de `private_bias` o `public_score` al sumar valores flotantes en nuevo orden; comprobación POST HOC independiente, no predicción de resultado humano. Las cantidades de parejas y exposición permanecieron iguales.

**Interpretación:** se detecta un artefacto de indexado en un modelo con política dependiente de historial de `seen` actualizado dentro del período. N91 aún no aísla causalmente ese punto: otras causas como el desempate de NetworkX se contrastarán con intervención en N92. Esto es validación de una propiedad de software y estructura interna, **no nueva teoría sociológica**, 0/3 y sin nuevos datos humanos.

**R1–R5:** Outcomes solo artificiales, identidad sintética y shocks exactos; control de paridad por permutación, no inferencia de efectos humanos; las seis seeds ya usadas no son muestra humana independiente; STOP_R5 de causalidad externa, CT2 ordinal 7. U143 P-PLATFORM-RANKING y U144 P-ACTION-SEMANTICS no cambian estado. Registros: 97 fuentes, 30 priors, 144 UPDATES; 25/40 válidos, N92 única liberada, N93–N106 catorce reservadas. Madurez 40.95%, aumenta solo simulator+QA. No licencias, autores, SSJY, microdatos ni merge main.