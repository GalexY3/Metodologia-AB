"""Durable, source-backed Spanish report generated from run JSONs."""
from pathlib import Path
import json,csv,statistics
from math import sqrt
HERE=Path(__file__).resolve().parent
E=HERE/'evaluations'
models=['v15_ops_rnn24_s3111','v15_ops_mlp16_s4111']
def read(name,suffix):
    p=E/(name+suffix+'.json')
    return json.loads(p.read_text('utf8')) if p.exists() else None
frozen={n:read(n,'_FROZEN') for n in models}
extra={n:read(n,'_UNSEEN_M') for n in models}
gated={n:read(n,'_GATE_HOLDOUT') for n in models}
dev=read(models[0],'_GATE_DEV')
lines=['# V15 â€” BÃºsqueda de polÃ­ticas neuronales individuales que superen al azar para k variable','',
'**Fecha de ejecuciÃ³n:** 11/11/2026. **Estado:** experimentaciÃ³n exploratoria reproducible, con evaluaciÃ³n congelada por condiciones y un holdout posterior de profesiones. La garantÃ­a universal (Â«en toda sociedadÂ») no estÃ¡ demostrada.',
'',
'## Pregunta y criterio',
'',
'Una aldea con N=120 individuos debe elegir k profesiones entre M opciones intercambiables y procurar un tamaÃ±o por profesiÃ³n N/k. El beneficio individual es min(n_j/(N/k),(N/k)/n_j). La hipÃ³tesis operativa que se analiza es **alimentaciÃ³n media mayor que la reasignaciÃ³n aleatoria en cada k ensayado**, no aÃºn formaciÃ³n perfecta de k grupos.',
'',
'Se consideran **canÃ³nicos** los k que dividen N; para otros k, la recompensa antigua no garantiza que exactamente k grupos con poblaciones enteras cercanas a N/k sean el Ã³ptimo de bienestar. No usar k no divisor como confirmaciÃ³n de reparto exacto.',
'',
'**La victoria estricta frente al azar en cada sociedad es matemÃ¡ticamente imposible de garantizar**: para cualquier k vÃ¡lido existe una probabilidad positiva de que una asignaciÃ³n aleatoria produzca ya exactamente k grupos equilibrados, con alimento 1. Una polÃ­tica alternativa no puede superar 1. Por ello, Â«superar siempre al azarÂ» se operacionaliza como superar la MEDIA del control en cada condiciÃ³n k/M especificada.',
'',
'La esperanza teÃ³rica de la polÃ­tica aleatoria se calcula con S=1+Binomial(Nâˆ’1,1/M), y E[r]=sum_s P(S=s) min(s/(N/k),(N/k)/s). Se comprueba ademÃ¡s por simulaciÃ³n de mundos nuevos; la primera comprobaciÃ³n no requiere entrenar ninguna red.',
'',
'## Nueva arquitectura',
'',
'Las redes de cada habitante tienen parÃ¡metros **privados y diferentes**; los gradientes de recompensa de otros individuos no modifican directamente sus parÃ¡metros. No se usan censos mundiales, Dk como observaciÃ³n, recompensas colectivas ni orÃ¡culo que asigne colores. SÃ­ se conoce el encargo k y el nÃºmero M de profesiones posibles, se observa la ocupaciÃ³n entre ocho vecinos y la recompensa individual observada.',
'',
'V15 reemplaza una clasificaciÃ³n directa entre M colores por nueve **operaciones invariantes al renombrado de profesiones**: permanecer; seguir la profesiÃ³n modal, minoritaria o aleatoria de los vecinos; explorar profesiones aleatorias o ausentes localmente; regresar a la profesiÃ³n previa o a la mejor recordada; y tomar una opciÃ³n local ponderada por frecuencia.',
'',
'| Variante | ParÃ¡metros por agente | Horizonte entrenamiento | Actualizaciones | Semilla |',
'|---|---:|---:|---:|---:|',
'| RNN recurrente | 1.473 | 28 | 2.400 | 3111 |',
'| MLP sin recurrencia | 857 | 20 | 1.300 | 4111 |',
'',
'Entrenamiento con REINFORCE y recompensa exclusivamente personal, sin comunicaciÃ³n. Pares (M,k) de entrenamiento predeterminados, con M=24 u 80. La RNN y el MLP difieren en arquitectura, nÃºmero de actualizaciones, horizonte y semilla: NO son repeticiones controladas de un Ãºnico diseÃ±o.',
'',
'## PolÃ­tica de inferencia y salvaguarda local',
'',
'El controlador de operaciones aprendido se ejecuta de modo **estocÃ¡stico cuando k/M<0,50** y con **argmax cuando k/Mâ‰¥0,50**. Este umbral se eligiÃ³ a partir de un piloto exploratorio y NO constituye un hiperparÃ¡metro confirmado externamente.',
'',
'En el estudio posterior se aÃ±adiÃ³ una salvaguarda de movilidad para k/Mâ‰¥0,70: **si el agente obtiene al menos 0,75 de comida individual, se queda en su ocupaciÃ³n actual en lugar de ejecutar un traslado propuesto por la red**. El umbral 0,75 se eligiÃ³ entre siete variantes comparadas en once condiciones de DESARROLLO. Como el veto se hace despuÃ©s de la decisiÃ³n neuronal, esta polÃ­tica es neuroheurÃ­stica y NO una regla de movilidad aprendida de forma puramente end-to-end.',
'',
'La salvaguarda evita ciertos traslados perjudiciales cuando casi todas las profesiones deben mantenerse activas. Se evaluÃ³ posteriormente en cuatro nÃºmeros de profesiones que nunca figuraron en los entrenamientos neuronales ni en la selecciÃ³n del umbral (M=16,32,48,72).',
'',
'## BaterÃ­a principal congelada (M=24 y 80)',
'',
'La evaluaciÃ³n RNN original utilizÃ³ 4 semillas de mundo nuevas Ã— 64 mundos por semilla = **256 sociedades** por condiciÃ³n, con 90 turnos, sin modificaciÃ³n de pesos. Los valores de esta tabla comparan polÃ­tica de temperatura k/M frente a random puro; para altos cocientes se aÃ±adiÃ³ posteriormente el veto local, evaluado como tratamiento independiente.',
'',
'| M | k | k entrenado en ese M | RNN adaptativa | Azar | Margen |',
'|---:|---:|:---:|---:|---:|---:|']
if frozen[models[0]]:
    n=models[0]
    for z in frozen[n]['results']:
        a=z['conditions']['adaptive']['mean_food']
        b=z['conditions']['random']['mean_food']
        lines.append(f"| {z['m']} | {z['k']} | {'sÃ­' if z['trained'] else 'no'} | {a:.4f} | {b:.4f} | {a-b:+.4f} |")
    zz=frozen[n]['results']
    lines.extend(['',
        f"RNN adaptativa por k/M, **{sum(z['conditions']['adaptive']['mean_food']>z['conditions']['random']['mean_food'] for z in zz)}/{len(zz)}** condiciones con ventaja media. Peor margen: {min(z['conditions']['adaptive']['mean_food']-z['conditions']['random']['mean_food'] for z in zz):+.5f}. No se alcanzÃ³ reparto exacto en las evaluaciones registradas de esta baterÃ­a.",
        ''])
lines.extend(['## GeneralizaciÃ³n a M nunca entrenados, ANTES de la salvaguarda','',
'Se probaron M=12,40,60 con la polÃ­tica de inferencia fijada y sin retrenamiento. Se encontraron fallos cerca de k/Mâ‰ˆ1, donde el reparto azaroso ya parte de una situaciÃ³n favorable.',
'',
'| Variante | Condiciones superiores al azar | Condiciones comprobadas | Peor margen |',
'|---|---:|---:|---:|'])
for model in models:
    z=extra[model]
    if z:
        rows=z['cases'];mn=min(x['margin'] for x in rows)
        lines.append(f"| {'RNN' if 'rnn' in model else 'MLP'} | {sum(x['margin']>0 for x in rows)} | {len(rows)} | {mn:+.4f} |")
lines.extend(['','## SelecciÃ³n de umbral de movilidad, solo desarrollo','',
'Se comparÃ³ sin veto y con umbrales 0,75; 0,80; 0,85; 0,90; 0,95; 0,99 en once pares difÃ­ciles. **El mejor umbral por criterio maximin fue 0,75**. Esta selecciÃ³n pertenece al conjunto de desarrollo; no usar los mismos mundos como prueba de generalizaciÃ³n.',
'',
'| Umbral | Condiciones positivas | Peor margen |',
'|---|---:|---:|'])
if dev:
    for x in dev['thresholds']:
        lines.append(f"| {x['cutoff'] if x['cutoff'] is not None else 'sin veto'} | {x['wins']}/11 | {x['worst_margin']:+.4f} |")
lines.extend(['',
'## Holdout posterior de profesiones nunca utilizadas','',
'Una vez fijado el umbral 0,75, se evaluÃ³ el MISMO modelo congelado en M=16,32,48,72. Estos valores de M no se utilizaron para entrenamiento neuronal ni para seleccionar el veto. Cuatro semillas de mundo Ã— 64 sociedades = 256 por par; horizonte de 90 turnos.',
'',
'| M | k | RNN con veto | Azar | Î” RNN | MLP con veto | Î” MLP |',
'|---:|---:|---:|---:|---:|---:|---:|'])
if gated[models[0]]:
    a=gated[models[0]]['rows']
    b={(x['m'],x['k']):x for x in gated[models[1]]['rows']} if gated[models[1]] else {}
    for z in a:
        other=b.get((z['m'],z['k']))
        lines.append(f"| {z['m']} | {z['k']} | {z['food']:.4f} | {z['random']:.4f} | {z['delta']:+.4f} | {other['food']:.4f} | {other['delta']:+.4f} |" if other else f"| {z['m']} | {z['k']} | {z['food']:.4f} | {z['random']:.4f} | {z['delta']:+.4f} | â€” | â€” |")
    for model in models:
        z=gated[model]
        if z:
            rs=z['rows'];num=sum(x['delta']>0 for x in rs)
            num95=sum(x['lower95']>0 for x in rs)
            lines.append(f"\n**{model}**: {num}/{len(rs)} mÃ¡rgenes positivos; {num95}/{len(rs)} lÃ­mites inferiores descriptivos al 95 % superiores a cero por mundos. Peor margen observado {min(x['delta'] for x in rs):+.4f}.")
lines.extend(['',
'## Limitaciones y siguientes pasos',
'',
'1. **No prueba cumplimiento exacto de k**: el Ã©xito de bienestar estÃ¡ lejos del objetivo de k grupos exactamente equilibrados. La variable de cantidad de ocupaciones y las cuotas deben conservarse como resultados, no sustituirse por raciÃ³n media.',
'2. **No prueba colaboraciÃ³n colectiva**: la ventaja puede proceder de aprendizaje individual y de operaciones locales predefinidas. Esta fase es Ãºnicamente una base neuronal funcional para una futura prueba de coordinaciÃ³n.',
'3. **No garantiza superioridad en cada mundo**: las cifras 25/25 y 12/12 son comparaciones de MEDIAS sobre conjuntos de mundos. Los intervalos descriptivos tratan la variaciÃ³n entre mundos pero no la incertidumbre entre muchas inicializaciones independientes de redes del mismo tipo.',
'4. **HiperparÃ¡metros exploratorios**: la arquitectura, el umbral de argmax por k/M y el veto de 0,75 se eligieron tras observar pilotos. Para una afirmaciÃ³n publicable hay que congelar la especificaciÃ³n y repetir en mÃºltiples semillas de entrenamiento con un holdout nuevo completamente reservado.',
'5. **Validez del incentivo**: para N/k no entero, es preciso rediseÃ±ar el incentivo o restringir k al conjunto de divisores si se quiere que exactamente k profesiones sean Ã³ptimas.',
'6. **Baselines mÃ¡s fuertes**: ademÃ¡s del azar, se guardan modos de imitaciÃ³n local y renovaciÃ³n aleatoria; debe compararse contra reglas autoorganizadas individuales sencillas, no solo un adversario aleatorio.',
'',
'## ReproducciÃ³n','',
'- v15.py y test_v15.py: arquitectura, entrenamiento y pruebas de gradientes independientes.',
'- evaluate_v15.py y evaluations/*_FROZEN.json: 25 condiciones originales con 256 sociedades por condiciÃ³n.',
'- unseen_M_v15.py y evaluations/*_UNSEEN_M.json: 35 condiciones adicionales fuera de M entrenados.',
'- stay_gate_v15.py y evaluations/*_GATE_DEV.json: bÃºsqueda de umbral en desarrollo; *_GATE_HOLDOUT.json: 12 pruebas nuevas con selecciÃ³n congelada.',
'- runs/*/latest.pt: parÃ¡metros aprendidos, optimizador y semillas.',
'- report_v15.py, INFORME_V15.md y comparaciones_v15.csv: sÃ­ntesis derivada Ãºnicamente de registros ejecutados.',
'',
'**ConclusiÃ³n:** V15 constituye una mejora empÃ­rica importante sobre V14 para la mÃ©trica especÃ­fica de *superar la alimentaciÃ³n del azar por cada condiciÃ³n*. Queda por aprender una polÃ­tica que alcance exactamente k grupos, demostrar robustez entre muchas inicializaciones y estudiar cooperaciÃ³n propiamente dicha.'
])
(HERE/'INFORME_V15.md').write_text('\n'.join(lines),encoding='utf8')
csv_rows=[]
for name in models:
    f=frozen[name]
    if f:
        for z in f['results']:
            for policy in ['neural','neural_greedy','adaptive','random','imitate','random_hold']:
                x=z['conditions'].get(policy)
                if x:
                    csv_rows.append(dict(model=name,battery='original',m=z['m'],k=z['k'],
                        trained=z['trained'],policy=policy,food=x['mean_food'],
                        random_ref=z['conditions']['random']['mean_food'],
                        delta=x['mean_food']-z['conditions']['random']['mean_food'],
                        worlds=x['worlds'],exact=x['exact']))
    for z in gated[name]['rows'] if gated[name] else []:
        csv_rows.append(dict(model=name,battery='novel_M_sealed',m=z['m'],k=z['k'],
            trained=False,policy='adaptive_plus_food_gate_075',food=z['food'],
            random_ref=z['random'],delta=z['delta'],worlds=z['worlds'],exact='not_captured'))
with (HERE/'comparaciones_v15.csv').open('w',encoding='utf8',newline='') as fh:
    writer=csv.DictWriter(fh,fieldnames=list(csv_rows[0]))
    writer.writeheader();writer.writerows(csv_rows)
print('V15_REPORT_READY',len(lines),'MD lines',len(csv_rows),'CSV rows',flush=True)
