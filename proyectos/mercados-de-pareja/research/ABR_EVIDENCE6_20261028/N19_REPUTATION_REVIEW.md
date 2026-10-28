# N19 · Rechazo privado, autoestima y reputación ante terceros: revisión discriminante

**28/10/2026 · AB-R documental.** Pregunta: ¿el rechazo en una aplicación de citas puede representarse como pérdida de estatus que los demás observadores incorporan en sus evaluaciones? El nuevo mecanismo planteado por el investigador es **pérdida efectiva de estatus** después de rechazo, no disminución del propio autoconcepto o descenso arbitrario de q. Para que ese efecto sea causal social en un modelo fiel a una app, hay que identificar el canal de información observable.

## Evidencia accesible y estimando de cada fuente
1. **Thomas, Binder y Matthes (2024)**, *The psychological influence of dating app matches: The more matches the merrier?*, New Media & Society, DOI https://doi.org/10.1177/14614448231161598. El texto establece que la aplicación notifica el match positivo; el swipe negativo no se notifica directamente, y el rechazo suele inferirse cuando persiste la falta de reciprocidad. **Apoya la distinción rechazo privado/inferencia individual; no mide pérdida pública de estatus.**
2. **van der Zanden y Schokkenbroek (2024)**, *Multiple Facets of Rejections in Online Dating: Exploring Types, Reasons, and Impact*, Cyberpsychology, Behavior, and Social Networking 27(8), 582–587. DOI https://doi.org/10.1089/cyber.2023.0751, PMID 38963768. Dos encuestas transversales; en estudio 1 n=177, ghosting fue la forma de rechazo más frecuente. Examina tipos, motivos y dolor subjetivo. **No estima penalización de posición de mercado reconocida por terceros.**
3. **Campaioli, Zamperini y Cecchinato**, publicado online el 19/05/2025 y en volumen 2026 de *New Media & Society*, *‘Now you’re home’: Awareness cues, rejection and post-digital safety on mobile dating apps*, DOI https://doi.org/10.1177/14614448251336437. Diario mensual de ocho participantes, estudia señales de actividad, incertidumbre y vigilancia. **Describe canales de observabilidad y riesgos de vigilancia; no cuantifica caídas automáticas de prestigio por rechazo.**
4. **Swipe, Chat, Unmatch: The Psychological Consequences of Being Rejected on Dating Apps** (2026), DOI https://doi.org/10.1080/15213269.2026.2633228. Dos experimentos preregistrados entre sujetos sobre unmatching, N=252 y 259; hallaron consecuencias en necesidades psicosociales y afecto negativo. **Rechazo afecta bienestar subjetivo; no prueba descenso del estatus evaluado por potenciales parejas no presentes en la interacción.**

## Modelo causal que conserva distinciones
```text
Swipe negativo privado de j hacia i
  -> NO notificación automática al resto del mercado (según affordance descrita)
  -> ausencia de reciprocidad observada por i -> posible ajuste de aspiraciones
  -> si existe comunicación pública verificable / chisme en red:
        señal compartida -> observadores terceros actualizan valoración de i
        -> cambio de probabilidad de aceptación / oportunidades
  -> si NO existe difusión: la evaluación de otros sigue inalterada
```
Una pérdida efectiva de capital relacional podría ocurrir a través de un mecanismo reputacional extraplataforma, pero [HIPÓTESIS NO VERIFICADA] cada interacción debe generar un evento público medible. No introducir `S_i(t+1)=S_i(t)-δ` como una ley de comportamiento humano ni igualar daño en autoestima con pérdida de status observable por terceros.

## Requisitos para falsar
- Separar rechazo privado observable solo por i; rechazo notificado a i; rechazo comunicado a terceros concretos; rechazo conocido por mercado amplio.
- Medir probabilidad y alcance de exposición de la señal, memoria/fiabilidad del observador, estado inicial de percepción y dirección del juicio de terceros.
- Estimando: `E[juicio_tercero | señal de rechazo visibilizada]-E[juicio_tercero | sin señal]` sobre muestra consentida y diseño minimizador de daño, no ranking real de personas.
- Comparador: señal falsa o neutral ética/equivalente, y controles de actividad visible, exposición y reputación previa; revisar confusores y no provocar estigmatización.
- Si no hay datos directos de tercero, **NO_IDENTIFIED**. Los datos cualitativos sobre vigilancia o encuestas de dolor no validan `δ` como estimador.

**Resultado N19:** existe base documental para separar mecanismos privados y señales observables. **No se encontró una estimación externa transferible de disminución automática de estatus de terceros por swipe privado.** Grade 0/3 para el mecanismo global actual, posible programa de investigación si se obtiene evidencia de difusión.

**R5:** parar el supuesto de penalización global como interpretación realista por defecto. Puede conservarse únicamente como contrafactual sintético etiquetado.
