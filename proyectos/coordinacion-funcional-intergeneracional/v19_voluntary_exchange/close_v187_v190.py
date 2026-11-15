"""Write the scientific synthesis from audited results, without changing them."""
from pathlib import Path
import hashlib
import json
import re
import shutil

B=Path(__file__).resolve().parent
R=B/'results'


def prose_spacing(text):
    units='símbolos|colores|archivos|contrastes|historias|contextos|evaluaciones|actualizaciones|parejas|semillas|registros|interacciones|hilos|CPU|GPU'
    text=re.sub(r'(\d)(?=(?:'+units+r')\b)',r'\1 ',text)
    for old,new in [('histórico61','histórico 61'),('mod31','mod 31'),('seisCPU','seis CPU'),
                    ('unaGPU','una GPU'),('memoriaGPU','memoria GPU'),('%de','% de'),('%memoria','% memoria'),
                    ('PMLR330','PMLR 330'),('Entropy26','Entropy 26')]:text=text.replace(old,new)
    return text


def main():
    audit=json.loads((R/'V187_V190_FINAL_AUDIT.json').read_text(encoding='utf-8'))
    assert not (R/'INFORME_V187_V190_20261115.md').exists()
    assert not audit['V190_primary'],'A positive candidate requires the separate causal follow-up before closing this block.'
    g188=audit['V188_groups'];g190=audit['V190_groups']
    def table(groups,with_support):
        header='| Soporte | Método | Train medio | Test medio | Rango test |' if with_support else '| Método | Train medio | Test medio | Test esperado medio |'
        separator='|---|---|---:|---:|---:|' if with_support else '|---|---:|---:|---:|'
        rows=[header,separator]
        for g in groups:
            m=g['means']
            if with_support:rows.append(f"| {g['support']} | {g['family']} | {100*m['train']:.2f}% | {100*m['test']:.2f}% | {100*g['test_min']:.2f}–{100*g['test_max']:.2f}% |")
            else:rows.append(f"| {g['family']} | {100*m['train']:.2f}% | {100*m['test']:.2f}% | {100*m['test_expected']:.2f}% |")
        return '\n'.join(rows)
    entries=audit['V190_low_private_lossy_entries']
    low=next(g for g in g190 if g['support']=='LOW' and g['family']=='PRIVATE')
    high=next(g for g in g190 if g['support']=='HIGH' and g['family']=='PRIVATE')
    if entries==0:
        decision=('V190 no produjo ninguna entrada en memorización perfecta con código comprimido entre las ocho historias LOW. '
                  'No apareció el régimen previo necesario para estudiar la transición registrada. Se cierra esta arquitectura mínima '
                  '—emisor tabular con feedback binario y receptor neuronal— como vía de identificación de grokking colectivo; '
                  'no se concluye que el fenómeno sea imposible con otros agentes o tareas.')
    else:
        decision=(f'V190 produjo {entries}/8 entradas LOW en memorización comprimida, pero ninguna transición candidata robusta según el criterio registrado. '
                  'Se conserva la diferencia entre alcanzar el régimen y generalizar después; no se rescata el primario mediante nuevas variantes de este algoritmo.')
    outcome=(f"El primario falla: {audit['V190_candidate_count']} candidatos. El control fijo supera .95 en test en "
             f"{audit['V190_positive_counts']['LOW']}/8 historias LOW y {audit['V190_positive_counts']['HIGH']}/8 HIGH. "
             f"El aprendiz privado termina LOW con train {100*low['means']['train']:.2f}% y test {100*low['means']['test']:.2f}%; "
             f"en HIGH, {100*high['means']['train']:.2f}% y {100*high['means']['test']:.2f}%. "
             f"Las entradas LOW en el régimen comprimido son {entries}/8. "
             'No se ejecutan congelaciones condicionadas a un candidato ausente. Estos resultados son un negativo del mecanismo y horizonte examinados, no una demostración de imposibilidad general.')
    if not all(v>=6 for v in audit['V190_positive_counts'].values()):
        outcome+=' Además falla el control positivo: no es interpretable como fracaso específico de la interacción privada.'
    outcome+=(' Igualar marginales controla tamaño y frecuencias; no identifica un efecto puro del número cromático, '
              'porque también difieren otras propiedades conjuntas de los soportes. La comparación V188/V190 cambia semillas, '
              'horizonte y ejemplos: no se usa como estimación causal aislada del soporte.')
    verification=(f"Se verificaron las {audit['V190_capacity_evaluations']} evaluaciones V190 frente a su cota informacional, "
                  f"además de las 9600 de V188. Un evaluador NumPy separado, que no llama al modelo ni al evaluador de entrenamiento, "
                  f"recalculó los pesos finales de las 64 historias V188/V190: {audit['numpy_numeric_checks']} contrastes numéricos, "
                  f"error máximo {audit['numpy_max_error']:.3g}, sin fallos; también coincidieron símbolos y cotas. "
                  'Los cuatro pares de grafos se comprobaron de nuevo por enumeración. Los archivos congelados siguen byte por byte iguales. '
                  'La auditoría técnica inicial V190 tuvo un error de serialización de un booleano NumPy, corregido antes del registro y sin entrenamiento científico; ambos logs se conservan.')
    for d in audit['conditional_code_diagnostics']:
        if d['experiment']==190 and d['family']=='PRIVATE':
            assert d['receivers_at_code_training_ceiling']==8 and d['senders_with_immediate_greedy_improvement']==0
    decision+=(' En las 16 historias privadas V190, el receptor ya alcanza el techo de entrenamiento del código actual '
               'y el emisor no obtiene mejora inmediata cambiando una señal frente a ese receptor fijo. '
               'El sondeo restringe el cuello de botella a una convención compatible y su posible reorganización; no establece un equilibrio global.')
    template=(B/'docs/V187_V190_REPORT_TEMPLATE.md').read_text(encoding='utf-8')
    conditional=[]
    for d in audit['conditional_code_diagnostics']:
        if d['family']=='FIXED_PROTOCOL':continue
        name=f"V{d['experiment']} "+(d['support']+' ' if d['support'] else '')+d['family']
        conditional.append(f"| {name} | {d['receivers_at_code_training_ceiling']}/8 | {d['senders_with_immediate_greedy_improvement']}/8 | {100*d['mean_oracle_train_given_code']:.2f}% |")
    diagnostic=('| Condición | Receptor alcanza techo del código | Emisor puede mejorar cambiando una señal | Techo train medio del código |\n'
                '|---|---:|---:|---:|\n'+'\n'.join(conditional)+
                '\n\nAlcanzar el techo del código significa que entrenar mejor la clasificación manteniendo ese código no puede reparar sus errores. '
                'No hallar un cambio codicioso rentable significa únicamente que el receptor actual no recompensa esa desviación inmediata. '
                'No demuestra un equilibrio de Nash sobre el espacio neuronal, ni descarta exploración estocástica, aprendizaje conjunto o mejoras después de adaptarse. '
                'Los estados de agrupación parcial tienen antecedentes clásicos; este diagnóstico no recibe prioridad teórica nueva.')
    replacements={'__DECISION_V190__':decision,'__TABLE_V188__':table(g188,False),'__TABLE_V190__':table(g190,True),
                  '__OUTCOME_V190__':outcome,'__AUDIT__':verification,'__CODE_DIAGNOSTIC__':diagnostic}
    for key,value in replacements.items():assert key in template;template=template.replace(key,value)
    # Editorial spacing only; no changes to protocols, source or result JSON.
    for old,new in [('16símbolos','16 símbolos'),('17archivos','17 archivos'),('16contrastes','16 contrastes'),
                    ('32historias','32 historias'),('32contextos','32 contextos'),('100actualizaciones','100 actualizaciones'),
                    ('5000','5000'),('31símbolos','31 símbolos'),('2000actualizaciones','2000 actualizaciones'),
                    ('4/8historias','4/8 historias'),('2/3 aún','2/3 aún'),('reivindicación2/3','reivindicación 2/3'),
                    ('PMLR2026','PMLR 2026'),('PDF2025','PDF 2025'),('procesoGPU','proceso GPU')]:template=template.replace(old,new)
    template=prose_spacing(template)
    report=R/'INFORME_V187_V190_20261115.md';report.write_text(template,encoding='utf-8')
    chapter='\n'.join('#'+line if line.startswith('#') else line for line in template.splitlines())
    chapter=chapter.replace('## Convenciones privadas, memoria y generalización: V187–V190',
                            '## Convenciones privadas y límites de la generalización colectiva',1)
    chapter=chapter.replace('](FIG_','](../results/FIG_')
    chapter+='\n'
    (B/'docs/TFM_CAPITULO_CONVENCIONES_V187_V190.md').write_text(chapter,encoding='utf-8')
    parent=(B/'docs/TFM_MANUSCRITO_TRABAJO_V186.md').read_text(encoding='utf-8')
    assert hashlib.sha256((B/'docs/TFM_MANUSCRITO_TRABAJO_V186.md').read_bytes()).hexdigest()=='b1799cf5c203529919b826377d3a1d269608b64c5e21ad1ec828ef66042651a1'
    parent=parent.replace('Manuscrito de trabajo ampliado hasta V186','Manuscrito de trabajo ampliado hasta V190',1)
    parent=parent.replace('las campañas V169–V186','las campañas V169–V190',1)
    parent=parent.replace('## Discusión integrada',chapter+'\n## Discusión integrada',1)
    abstract=('La rama de comunicación contrasta un mecanismo clásico de memoria limitada antes de atribuir originalidad al fracaso del aprendizaje privado. '
              'El mecanismo funciona en el juego clásico y fracasa en su adaptación neuronal. Un contraste de soportes igualados por frecuencias no produce '
              'el régimen previo de memorización necesario para identificar grokking colectivo. Se conservan los límites informacionales y los negativos; '
              'no se extiende su alcance a instituciones o poblaciones humanas.\n\n')
    if entries:abstract=abstract.replace('no produce el régimen previo de memorización necesario para identificar grokking colectivo','no confirma la transición tardía registrada')
    parent=parent.replace('**Palabras clave:**',abstract+'**Palabras clave:**',1)
    parent+='''
### Referencias añadidas para V187–V190

Lyle, C., Sokar, G., György, A. y Pascanu, R. (2026, registro PMLR). *What can grokking teach us about learning under non-stationarity?* PMLR330,635–656. https://proceedings.mlr.press/v330/lyle26a.html. Se conserva la discrepancia con el año y orden de autores del PDF.

Charpenay, N., Le Treust, M. y Roumy, A. (2024). *Side Information Design in Zero-Error Coding for Computing*. Entropy26(4),338. https://doi.org/10.3390/e26040338.
'''
    parent=prose_spacing(parent)
    manuscript=B/'docs/TFM_MANUSCRITO_TRABAJO_V190.md';manuscript.write_text(parent,encoding='utf-8')
    backup=B/'handoff_codex/backups_V190';backup.mkdir(exist_ok=False)
    for p in [B/'INICIO_INVESTIGACION_CIENTIFICA.md',B/'handoff_codex/GOAL_CIENTIFICO_AB_TFM.md']:shutil.copyfile(p,backup/p.name)
    intro=B/'INICIO_INVESTIGACION_CIENTIFICA.md'
    intro.write_text('# Estado actualizado V190 — 15/11/2026\n\n'+decision+'\n\nInforme: results/INFORME_V187_V190_20261115.md. Manuscrito: docs/TFM_MANUSCRITO_TRABAJO_V190.md. Reproducción: REPRODUCE_V187_V190.md. CT2 histórico61, nueva rama sin puntuación; N2=N3=0.\n\n---\n\n'+intro.read_text(encoding='utf-8'),encoding='utf-8')
    with (B/'handoff_codex/GOAL_CIENTIFICO_AB_TFM.md').open('a',encoding='utf-8') as f:
        f.write('\n## Decisión V187–V190, 15/11/2026\n\n'+decision+'\n\n'+outcome+'\n\nEl objetivo científico global sigue activo. Esta arquitectura no debe consumir otra secuencia de ajustes pequeños. La siguiente rama deberá resolver una incertidumbre que este contraste no pueda identificar, con antecedente competente y falsador antes de su campaña. Una curva del sistema no basta para atribuir reorganización a varios cerebros; una institución diseñada no se convierte en aprendida por mejorar el rendimiento.\n')
    entries_ledger=[]
    kinds={187:'registered known-effect calibration',188:'registered transfer falsification',189:'posthoc information audit and excluded prototype',
           '189B':'matched-context construction before neural outcomes',190:'registered exploratory transition test'}
    outcomes={187:'93/100 limited versus0/100 pure >=.99; known-effect gate passed',188:'primary failed;0/8 qualified limited urns;no private memorization',
              189:'9600 capacity checks passed;prototype labels unmatched, excluded before training','189B':'4 paired supports matched on all input/output marginals;chi16 vs31 certified',
              190:f'primary failed;{entries}/8 LOW lossy-memorization entries;0 transition candidates'}
    for v,kind in kinds.items():
        entries_ledger.append(dict(id=f'V{v}',kind=kind,A='uncertainty and estimand specified in report',
            B='classical reinforcement/forgetting, supplied protocol and information limits treated as rivals',
            C='published antecedents restrict originality; no generic signaling or graph-coloring novelty claim',
            D='remote preregistration before training forV187,V188,V190;V189/B explicitly construction/posthoc',
            E='raw histories,weights,contexts,technical fixtures and source hashes preserved',F=outcomes[v],
            G='registered horizon and gates retained;no post-negative variant rescue',
            H='NumPy/Numba/reference checks are technical independence, not independent scientific confirmation',
            I='no new original N1 awarded;N2=N3=0',J='global goal active;architecture closure as specified',new_N1=False,N2=False))
    (R/'V187_V190_AB_LEDGER.json').write_text(json.dumps(entries_ledger,indent=2),encoding='utf-8')
    assert hashlib.sha256((R/'AB_PROGRESO_CT2_CT3.json').read_bytes()).hexdigest()==audit['canonical_progress_sha256']
    evaluation=dict(method='AB3.2.1',date='2026-11-15',canonical_CT2_historical=61,new_branch_score=None,
                    N1='NOT_AUDITED',new_original_N1_awarded=False,N2=0,N3=0,goal_status='active',
                    V187_known_calibration_passed=True,V188_transfer_primary_failed=True,V190_primary_failed=True,
                    V190_low_private_lossy_entries=entries,collective_grokking_accredited=False,
                    learned_institution_accredited=False,canonical_score_file_unchanged=True,
                    manuscript_sha256=hashlib.sha256(manuscript.read_bytes()).hexdigest(),
                    manuscript_words=len(re.findall(r'\S+',parent)),bibliographic_records=96)
    (R/'AB_EVALUACION_V187_V190_20261115.json').write_text(json.dumps(evaluation,indent=2),encoding='utf-8')
    handoff=f'''# Estado final V190 — 15/11/2026

{decision}

{outcome}

El proceso científico V190 terminó; no relanzarlo. Sesión original31818, PID27480. V187/V188 están terminados. Informe en results/INFORME_V187_V190_20261115.md; auditoría en results/V187_V190_FINAL_AUDIT.json; manuscrito integrado docs/TFM_MANUSCRITO_TRABAJO_V190.md. Reproducción en REPRODUCE_V187_V190.md. V189 conserva el prototipo descartado; V189B contiene los cuatro pares usados. Los protocolos y las fuentes congeladas no se editaron.

{verification}

Prerregistros remotos: V187: 368ad29abeae37db9de9aeced4769953ba3e60b8; V188: 0ff3063594136db0959b740ffbbf26568c361fe8; V190: c918d5b326afb6320d7339b94d24c5f21511fba8. Consultar sus recibos y la entrega final en research/V187_V190_20261115/PUBLICATION_RECEIPT.json una vez verificada. No confundir registro previo con publicación posterior de resultados.

Lyle et al. ya relacionan grokking y plasticidad bajo no estacionariedad. Spike et al. son antecedente fuerte para refuerzo y olvido; el repositorio publicado devuelve404, por eso V187 es reimplementación de métodos. El marco de grafos de confusión/coloración es clásico. La búsqueda bibliográfica es exploratoria,96registros con alcance de lectura por entrada. No se concede originalidad por ausencia de coincidencias de búsqueda.

CT2 histórico61 pertenece a otra rama y no es probabilidad. Archivo canónico sin cambios; nueva rama sin puntuación, N2=N3=0. Objetivo global activo. Evitar pequeñas variantes para rescatar esta arquitectura; exigir nueva incertidumbre identificable y rival competente. No afirmar varias abstracciones neuronales a partir de un solo receptor neuronal y un emisor tabular.

Git local HEAD c032a32d2d8d7710a6ad5a88519b0801ea186891, índice del usuario SHA256 0fc87bbef0de6ced68aa787004ef36d3c7934f757f51b5d8505665bd071184a1. Hay cambios ajenos. Publicación por índice separado y lista explícita; verificar blobs mediante ls-tree/cat-file para evitar el límite de rutas Windows. No usar stage-all/reset/pull/merge. No iniciar subagentes sin autorización explícita. No enviar mensajes a terceros. Servicios Python ajenos 3504,15036,15080 se preservan. Recursos: research_resource_limits.py, dos hilos BelowNormal, seisCPU, unaGPU con límite35%memoria y pausas por bloque.
'''
    (B/'handoff_codex/ESTADO_20261115_V190.md').write_text(prose_spacing(handoff),encoding='utf-8')
    reproduction=B/'REPRODUCE_V187_V190.md'
    reproduction.write_text(prose_spacing(reproduction.read_text(encoding='utf-8')),encoding='utf-8')
    print(json.dumps(evaluation),flush=True)


if __name__=='__main__':main()
