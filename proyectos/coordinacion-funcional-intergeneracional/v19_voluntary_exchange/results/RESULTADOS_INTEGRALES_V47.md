# V47. Reciprocidad privada aprendida ante cambios continuos de compañero entre experiencias

Las48 políticas individuales aprendieron desde cero, con parámetros no compartidos, valores materiales y horizonte idénticos a V46. En cada una de1000 actualizaciones, las24 parejas se reconstituyeron al azar, con un generador independiente y sin preservar la identidad previa. No existen contratos, sanciones programadas, preferencias prosociales ni recompensas colectivas. La optimización NL y LOLA es exclusivamente del retorno esperado privado.

## Todos los resultados, al final de1000 actualizaciones, sobre12 emparejamientos nuevos

| Semilla | Método | Alimento | Donaciones | Mutuas | Retorno propio causal | Personas positivas | Reemparejamientos exitosos |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 3111 | NL 0 | 0.2002 | 0.0017 | 0.0000 | -0.0311 | 0.0/48 | 0.00% |
| 3111 | LOLA 5 | 0.3427 | 0.9956 | 0.9914 | +0.0142 | 48.0/48 | 100.00% |
| 3111 | LOLA 20 | 0.3428 | 0.9965 | 0.9935 | +0.3416 | 48.0/48 | 100.00% |
| 4111 | NL 0 | 0.2002 | 0.0017 | 0.0000 | -0.0309 | 0.0/48 | 0.00% |
| 4111 | LOLA 5 | 0.3427 | 0.9956 | 0.9913 | +0.0142 | 47.0/48 | 100.00% |
| 4111 | LOLA 20 | 0.3428 | 0.9965 | 0.9935 | +0.3412 | 48.0/48 | 100.00% |
| 5111 | NL 0 | 0.2002 | 0.0017 | 0.0000 | -0.0310 | 0.0/48 | 0.00% |
| 5111 | LOLA 5 | 0.3427 | 0.9956 | 0.9914 | +0.0143 | 48.0/48 | 100.00% |
| 5111 | LOLA 20 | 0.3428 | 0.9965 | 0.9935 | +0.3422 | 48.0/48 | 100.00% |
| 6111 | NL 0 | 0.2002 | 0.0017 | 0.0000 | -0.0310 | 0.0/48 | 0.00% |
| 6111 | LOLA 5 | 0.3427 | 0.9956 | 0.9914 | +0.0144 | 48.0/48 | 100.00% |
| 6111 | LOLA 20 | 0.3428 | 0.9965 | 0.9935 | +0.3420 | 48.0/48 | 100.00% |

El retorno causal es el valor privado de forzar un regalo en t0 frente a prohibirlo y dejar que ambos sigan sus políticas privadas; usa cadena Markov exacta. Se evalúan al menos24 personas de48 con retorno positivo y>0,25 mutualidad en9/12 reemparejamientos reservados, no en los mismos episodios usados para entrenar.

## Contraste de aprendizaje y control negativo

El gradiente NL de corto alcance y el algoritmo LOLA utilizan el mismo conocimiento exacto de recompensas, el mismo espacio de cinco parámetros por persona y Adam lr0,03; solo LOLA calcula cómo su acción cambiaría la actualización neuronal prevista del otro. Los resultados preservan la comparación de V46, incluso con cambios de interlocutor entre actualizaciones. Se conserva el camino histórico en METRICAS_V47.json y los pesos al final; no se seleccionó un punto óptimo a posteriori.

| Criterio preregistrado | Resultado |
| --- | --- |
| H47_5 | cumple |
| H47_20 | cumple |
| H47b | cumple |
| H47d | cumple |

## Validación externa y límites

Para cada política congelada se evaluaron12 nuevas parejas completas (semillas declaradas previamente) y para dos de ellas6 semillas ambientales con128 mundos cada una mediante Monte Carlo independiente del evaluador exacto. Todas las discrepancias agregadas alimento, regalos y mutualidad cumplen la tolerancia<0,015.

[Inferencia] La transferencia a personas diferentes sugiere que se han aprendido convenciones de respuesta general, sin requerir historia de un interlocutor particular. Sin embargo, la interacción todavía es diádica y la pareja no cambia en mitad del episodio. Los roles profesionales son exógenos y complementarios; no se prueba todavía coordinación funcional en redes con múltiples socios.

La infraestructura de inferencia de gradientes ajenos se proporciona por el laboratorio, no se aprende mediante observaciones sociales limitadas. Un éxito en V47 no implica emergencia endógena de instituciones.

## Reproducción y hashes

Preregistro, motor de matching por actualización, 12 checkpoints de1000 pasos con Adam, evaluador y simulación independiente, tests y datos JSON originales, CSV, métricas y trayectorias.
PREREG_V47_PARTNER_TURNOVER.md: e4ad7d39118f6f62998d29ca84a36ad723aaed97d46066438d4f85855c1023ad
v47_partner_turnover.py: 1737740d1e95631d04be6f7b123195730651861a74495bfa037a84f1d50d2d9a
v47_frozen_audits.py: af347d6e02a0130206a1426315c0f4eccca8cb67379052a66999f21cd9c84d46
v47_batch_audit.py: 27683934bf6e093abd0bdecd5c42a58a44df1cbabb3a8b2830c03cd4f7b3853b
v47_summarize.py: 0d8fdf75d57f0c39d9891667df3314c6b4ce9ba38029b5fb13e5623ba00ff714
test_v47_partner_turnover.py: 33df8bb3932046882f7c1775c6291b6bc5cdc6b017ba165412769bb673b41419
test_v47_frozen_audits.py: 95c35033bd410264257a6659bb283938facdc03a4c3006fac1a46428cb4178f6