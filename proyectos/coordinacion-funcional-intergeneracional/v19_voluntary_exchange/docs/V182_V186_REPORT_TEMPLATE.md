# V182–V186: reproducción adversarial y límites del grokking entre agentes

15 de noviembre de 2026. La investigación continúa activa. El CT2 histórico permanece en 61; la nueva rama de comunicación no recibe una puntuación automática. No se acredita una contribución 2/3.

## Qué queda establecido

Este bloque ejecutó el código original de un antecedente, contrastó un simulador independiente y evaluó 6.480 vidas nuevas. Una hipótesis sobre protección material falló su criterio prospectivo. La cooperación publicada se reproduce aproximadamente en varias condiciones, con discrepancias que se conservan. En la nueva línea de grokking, el control individual generaliza tarde, mientras dos agentes con aprendizaje separado quedan atrapados en códigos que pierden información. Una intervención externa sobre esos códigos permite distinguir el problema comunicativo de la capacidad del receptor.

Son resultados de modelos y de auditoría computacional. No establecen leyes sociológicas ni demuestran que agentes con intereses contrapuestos hayan inventado una institución.

## V182: código y resultados de Yaman

Se revisó el texto principal de [Yaman y colaboradores (2023)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10598450/) y el suplemento de 13 páginas. Los autores explicitan que las normas se seleccionan mediante fitness de grupo y que los individuos no pueden decidir unilateralmente si las cumplen. Aprender papeles bajo ese régimen y crear privadamente el propio régimen son problemas distintos.

El [archivo original CC0](https://zenodo.org/records/8401555) contiene código MATLAB y resultados. Tiene 252.169.955 bytes y SHA256 `{audit[source_archive_SHA256]}`. Se conservaron los originales sin modificaciones.

La ejecución en Octave confirma dos discrepancias en el código de *common pasture*: el optimizador cambia `socialNorm`, pero el simulador lee `genotype`; además, el regularizador suma signos en lugar de contar reglas. Por ello, una regla negativa puede recibir una bonificación. En el fixture ejecutado, el fitness resulta 3,718757254918, frente a 3,318757254918 con la penalización L0.

Sin embargo, los 1.200 ajustes archivados reconstruyen la fórmula L0 con error máximo {audit[maximum_original_fitness_L0_residual]:.3g}. También emplean nombres de campos anteriores a los del código. La conclusión es una desalineación del paquete publicado. No demuestra que el artículo utilizara el código defectuoso ni que su resultado cooperativo sea falso.

El port en Numba conserva la física, los órdenes aleatorios, los presupuestos sin deuda y la actualización individual de valores. Superó 51 comprobaciones contra seis fixtures del MATLAB original ejecutado en Octave. Los archivos de replay solo cambian nombres de función y proveedores de aleatoriedad. V183 añadió otras 63 comprobaciones. Esta paridad es técnica; no sustituye una confirmación científica externa.

## V183: una explicación causal que no supera su falsador

[Preregistro c1ecde0](https://github.com/GalexY3/Metodologia-AB/commit/c1ecde092d02140c18b13c54498b7477232a3d52). Se estudiaron las 300 normas de *settlement maintenance* con regularización 0 o 0,2, sin seleccionar éxitos. Ocho vidas nuevas por norma y dos órdenes temporales produjeron 4.800 evaluaciones. Las normas permanecieron fijas y los papeles se aprendieron de nuevo.

La intervención trasladó los ataques antes de las transferencias. La hipótesis era que redistribuir primero pudiera proteger recursos, además de alterar el aprendizaje. Para ingresos r, transferencias netas delta y supervivencia A, el efecto material inmediato es `sum(A*delta)`. Su esperanza condicional es `p*sum(P*delta)`, donde P indica protección y la suma de delta es cero. Es una identidad de conservación, no un nuevo teorema sobre seguros ni una descomposición del efecto de toda la trayectoria.

El efecto primario ORIGINAL − ATTACK_FIRST fue **{effect:.6f}**, con intervalo bootstrap jerárquico del 95% **[{ci[0]:.6f}, {ci[1]:.6f}]**. Queda por debajo del margen previo de **0,25**: el criterio principal falla. El remuestreo respeta los 30 bloques originales reutilizados entre contextos y las ocho semillas de vida. Las 4.800 evaluaciones no se tratan como estudios independientes.

Los controles sin ataques coinciden. El error máximo de conservación es {audit[maximum_transfer_conservation_error]:.3g} y el de la identidad condicional, {audit[maximum_conditional_identity_error]:.3g}. Se cierra la propuesta de una gran ventaja debida a este orden temporal en estas normas; no se ejecutan reoptimizaciones para rescatarla.

![Auditoría temporal y reproducción](FIG_V182_V184_REPRODUCTION.png)

## V184: reproducción de pastura y correspondencia de parámetros

[Preregistro d359009](https://github.com/GalexY3/Metodologia-AB/commit/d359009eb01363a2404b71c7d799acc23dd42021). Se reevaluaron 300 normas con cuatro vidas nuevas y 5.000 pasos. El intercambio de crecimiento natural y crecimiento por trabajadores no cambia tres de los cinco entornos: esas celdas se reutilizan. Hay **1.680 vidas únicas**, frente a 2.400 celdas tabuladas.

En las 120 normas de entornos asimétricos, la asignación del código da un RMSE de **{pasture[RMSE_release]:.6f}** frente al valor archivado; la asignación intercambiada da **{pasture[RMSE_swapped]:.6f}**. La diferencia media absoluta entre asignaciones es {pasture[mean_absolute_mapping_difference]:.6f}. Se cumple el criterio descriptivo de correspondencia.

La cooperación sigue siendo elevada en varias condiciones. La reproducción es aproximada: no identifica de manera única el generador histórico ni reproduce el GA de pastura corregido. La selección de normas a partir de vidas ruidosas y las diferencias de versión son explicaciones posibles de la discrepancia residual.

## V185: separar grokking individual y generalización entre agentes

[Preregistro 662da03](https://github.com/GalexY3/Metodologia-AB/commit/662da03333d936ad71e941fef3f5bec885a0bc34). El emisor observa a; el receptor observa b y un mensaje. Deben producir `(a+b) mod 31`. El emisor aprende mediante REINFORCE desde su acierto binario; el receptor aprende con la etiqueta del resultado. Sus parámetros y gradientes están separados. El interés cooperativo, el canal y las funciones de emisor y receptor son exógenos.

Hay 387 pares de entrenamiento y 574 de test. Cada par y su inversión pertenecen al mismo conjunto. Se ejecutaron 30.000 actualizaciones por condición en dos semillas de descubrimiento, sin detener el entrenamiento por el resultado en test.

| Semilla | Condición | Train final | Test final | t_mem | t_gen |
|---|---|---:|---:|---:|---:|
{ptable}

El receptor con diccionario fijo cumple el criterio previo de generalización tardía en ambas historias. Los pares independientes no alcanzan el 99% de entrenamiento. Por ello, las cuatro congelaciones condicionales previstas se cancelaron: no son controles ejecutados ni resultados negativos de esas congelaciones.

Los emisores terminan casi deterministas, usando 24 o 28 símbolos. En todos los pares uniformes, sus techos de acierto son 24/31 y 28/31; sobre el soporte concreto de test, son 85,89% y 93,38%. Estos límites son informacionales y clásicos.

El análisis posthoc muestra que los receptores ya alcanzan el acierto de entrenamiento óptimo para sus diccionarios codiciosos y que ninguna sustitución unilateral de símbolo mejora el acierto actual del emisor. Es una afirmación restringida sobre esos estados finales, no una prueba de equilibrio de Nash en todo el espacio de políticas neuronales.

Intercambiar interlocutores entre semillas o permutar mensajes preservando sus marginales reduce el rendimiento cerca del azar. Esto apoya el uso causal de convenciones específicas; no acredita por sí mismo grokking colectivo.

![Curvas de generalización](FIG_V185_DELAYED_GENERALIZATION.png)

## V186: reparación del código frente a más entrenamiento

[Preregistro 4164292](https://github.com/GalexY3/Metodologia-AB/commit/4164292c0d32adcb58c2d9ce4e944427578b8da2). Cada historia recibe otras 30.000 actualizaciones en tres brazos: continuación conjunta, diccionario aprendido congelado y reparación biyectiva externa. Todos parten del mismo receptor y de su optimizador.

La reparación conserva una asignación por símbolo y reasigna las colisiones a símbolos libres, por orden fijo. Cambia siete o tres asignaciones, sin consultar etiquetas o test. Es un control oráculo impuesto; no un mecanismo que los agentes hayan aprendido. Ambos brazos con diccionario fijo son deterministas.

| Historia | Continúa conjunto | Código aprendido fijo | Reparación externa | Criterio previo |
|---|---:|---:|---:|---|
{ctable}

El criterio de suficiencia específica exige al menos un 95% con reparación y una ventaja mínima de diez puntos frente a cada rival, en ambas historias. **Resultado: {causal[primary_passed]}.** Las seis continuaciones reutilizan dos historias; no son seis réplicas independientes.

La intervención demuestra que reparar estas asignaciones permite recuperar generalización bajo el presupuesto fijado cuando el aprendizaje conjunto o el diccionario perdido no lo consiguen. No explica todavía cómo lograrían los agentes esa reparación autónomamente. Tampoco demuestra una nueva transición colectiva: el receptor puede seguir aprendiendo con un código fijado desde fuera.

![Intervención sobre las colisiones](FIG_V186_CAUSAL_BOTTLENECK.png)

## Originalidad, integridad y decisión

[LIO](https://proceedings.neurips.cc/paper_files/paper/2020/hash/ad7ed5d47b9baceb12045a929e7e2f66-Abstract.html) ya aprende incentivos privados. [Power y colaboradores](https://arxiv.org/abs/2201.02177) establecen grokking individual; [Chaabouni y colaboradores](https://aclanthology.org/2020.acl-main.407/) estudian generalización comunicativa. [Lowe y colaboradores](https://ifaamas.org/Proceedings/aamas2019/pdfs/p693.pdf) exigen controles causales para inferir comunicación. La agrupación parcial de significados tiene antecedentes en [juegos de señales](https://pmc.ncbi.nlm.nih.gov/articles/PMC4113927/), y [Spike y colaboradores](https://pmc.ncbi.nlm.nih.gov/articles/PMC5412673/) comparan mecanismos conocidos de olvido y presión contra la ambigüedad. Nuestro diagnóstico no se presenta como descubrimiento de esos principios.

El siguiente rival necesario es un aprendiz privado competente de convenciones, basado en esos antecedentes. Además, una candidatura colectiva deberá demostrar que la transición depende de la reorganización de varios aprendices y no solo de la generalización del receptor. Repetir este REINFORCE con más semillas no resuelve esas dos incertidumbres.

Se preservan el parser inicial invalidado y el problema de restauración del estado RNG de un helper de V185 que no llegó a ejecutarse. V186 corrige la restauración como ByteTensor en CPU. Antes de las nuevas continuaciones, el replay de 5.000 actualizaciones históricas por semilla reprodujo exactamente pesos, baseline y RNG. Esas 10.000 actualizaciones no se contabilizan como evidencia nueva ni garantizan identidad entre equipos.

Los protocolos, hashes, fuentes, estados, curvas y negativos se conservan. El índice y el HEAD locales del usuario no se reasignan. **N2 y N3 siguen en cero.** El gráfico mantiene la referencia histórica; no asigna puntos ficticios a la nueva rama ni convierte avances técnicos en originalidad acreditada.

![Referencia CT2 histórica](FIG_CT2_V175_V180.png)
