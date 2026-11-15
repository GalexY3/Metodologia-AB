"""Preserve parent artifacts, register actual sources, integrate the TFM draft."""
import hashlib
import json
from pathlib import Path
import re
import runpy
import shutil

ROOT=Path(__file__).resolve().parent


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    backup=ROOT/'research/V175_V180_20261115/before_integration';backup.mkdir(parents=True,exist_ok=False)
    for name in ('literatura/references_verified.json','literatura/references.bib',
                 'literatura/BIBLIOGRAFIA_ACUMULATIVA_20261114.md','INICIO_INVESTIGACION_CIENTIFICA.md'):
        path=ROOT/name;shutil.copy2(path,backup/(path.stem+'_'+sha(path)[:12]+path.suffix))
    p=ROOT/'literatura/references_verified.json';data=json.loads(p.read_text(encoding='utf8'))
    common=dict(checked_on='2026-11-15',full_text_reviewed=False)
    refs=[
      dict(id='AkiyamaKaneko2000DynamicalGames',authors='Akiyama, Eizo; Kaneko, Kunihiko',year=2000,
        title='Dynamical systems game theory and dynamics of games',container='Physica D147(3–4):221–258',
        doi='10.1016/S0167-2789(00)00157-3',url='https://www.sciencedirect.com/science/article/pii/S0167278900001573',theme='EVOLUCION',
        contribution='Marco de juegos que modifican dinámicamente su entorno mediante decisiones de sus agentes.',
        our_experiments='V173–V180: antecedente del generador ecológico',
        novelty_constraint='No reclamar como nuevo el enfoque de juegos de sistemas dinámicos',
        verification='primary publisher metadata, abstract and section snippets; one-person demonstrations distinguished from multiplayer sequel'),
      dict(id='AkiyamaKaneko2002DynamicalGamesII',authors='Akiyama, Eizo; Kaneko, Kunihiko',year=2002,
        title='Dynamical systems game theory II',container='Physica D167(1–2):36–71',
        doi='10.1016/S0167-2789(02)00402-5',url='https://www.researchgate.net/publication/239621558_Dynamical_systems_game_theory_II',theme='EVOLUCION',
        contribution='Cooperación, diferenciación temporal y formación de normas en el dilema de leñadores.',
        our_experiments='V173–V180: antecedente adversarial de normas y turnos',
        novelty_constraint='La existencia de normas sin poder externo en juegos dinámicos tiene precedentes anteriores a2025',
        verification='original paper hosted on author ResearchGate page: abstract and relevant decision-rule/multiplayer passages; not full proof audit'),
      dict(id='HamonNisiotiMoulinFrier2023EcoEvo',authors='Hamon, Gautier; Nisioti, Eleni; Moulin-Frier, Clément',year=2023,
        title='Eco-evolutionary Dynamics of Non-episodic Neuroevolution in Large Multi-agent Environments',
        container='GECCO2023 Companion',doi='10.1145/3583133.3590703',url='https://arxiv.org/html/2302.09334',theme='EVOLUCION',
        contribution='Neuroevolución recurrente con observaciones locales y recursos, sin reinicios generacionales.',
        our_experiments='V175–V180: rival conceptual de memoria privada y sostenibilidad',
        novelty_constraint='No atribuir prioridad a forrajeo sostenible por agentes recurrentes con información local',
        verification='primary paper: architecture, observations, ecology, evaluation and reported failed seeds reviewed; code not independently re-executed'),
      dict(id='SchmidEtAl2022StrategySpaces',authors='Schmid, Laura; Hilbe, Christian; Chatterjee, Krishnendu; Nowak, Martin A.',year=2022,
        title='Direct reciprocity between individuals that use different strategy spaces',container='PLoS Computational Biology18(6):e1010149',
        doi='10.1371/journal.pcbi.1010149',url='https://pmc.ncbi.nlm.nih.gov/articles/PMC9197081/',theme='RECIPROCIDAD',
        contribution='Competencia entre espacios de estrategia con capacidades de memoria distintas y posibles dilemas entre ellos.',
        our_experiments='V177,V178,V180: antecedente de capacidad y conflicto de incentivos',
        novelty_constraint='Espacios mayores no garantizan cooperación; no presentar esa observación general como nueva',
        verification='primary journal abstract and directly relevant results; no independent replication of evolutionary algorithms'),
      dict(id='Alqithami2026RecallBraess',authors='Alqithami, Saad',year=2026,
        title='Endogenous Information in Routing Games: Memory-Constrained Equilibria, Recall Braess Paradoxes, and Memory Design',
        container='arXiv preprint2604.11733v2,24September2026',doi=None,url='https://arxiv.org/abs/2604.11733v2',theme='METODOLOGIA',
        contribution='Memoria endógena y perjuicios de mejorar recuerdo en juegos de rutas.',
        our_experiments='V177: revisión adversarial del enunciado genérico de memoria perjudicial',
        novelty_constraint='Preprint sin validación editorial; contexto distinto, pero limita la reivindicación genérica de prioridad',
        verification='primary arXiv metadata and abstract only; no theorem audit'),
      dict(id='SloughEtAl2021CommunityMonitoring',authors="Slough, Tara; Rubenson, Daniel; Levy, Ro'ee; others",year=2021,
        title='Adoption of community monitoring improves common pool resource management across contexts',
        container='PNAS118(29):e2015367118',doi='10.1073/pnas.2015367118',url='https://pmc.ncbi.nlm.nih.gov/articles/PMC8307849/',theme='EMPIRICO',
        contribution='Ensayos armonizados en seis países sobre monitoreo comunitario iniciado externamente.',
        our_experiments='V179: búsqueda de evidencia externa y selección de la réplica china',
        novelty_constraint='No confundir monitoreo promovido por instituciones existentes con institución emergente aprendida',
        verification='primary paper: design, mechanisms and data availability inspected; six-country meta-analysis not independently re-estimated'),
      dict(id='BuntaineZhangHunnicutt2021Waterways',authors='Buntaine, Mark T.; Zhang, Bing; Hunnicutt, Patrick',year=2021,
        title='Citizen monitoring of waterways decreases pollution in China by supporting government action and oversight',
        container='PNAS118(29):e2015175118',doi='10.1073/pnas.2015175118',url='https://escholarship.org/uc/item/7c94j310',theme='EMPIRICO',
        contribution='Ensayo factorial por160vías sobre difusión de monitoreo a autoridades y al público.',
        our_experiments='V179: reproducción Python de coeficientes,CR2,Satterthwaite y10000permutaciones de la especificación principal',
        novelty_constraint='Evidencia humana existente; contraste gobierno−público añadido tieneCI95que incluye0 y no valida el simulador ecológico',
        verification='original institutional paper, OSF archive and selected source code inspected; main full-sample water-quality regression independently reconstructed, not all article outcomes')]
    ids={r['id'] for r in data['references']}
    for ref in refs:
        assert ref['id'] not in ids;ref.update(common);data['references'].append(ref)
    data['number_verified']=len(data['references']);data['review_date']='2026-11-15'
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    runpy.run_path(str(ROOT/'literatura/generate_bibliography.py'))
    parent=ROOT/'docs/TFM_MANUSCRITO_TRABAJO_V174.md';parent_hash=sha(parent)
    manuscript=parent.read_text(encoding='utf8')
    manuscript=manuscript.split('## Discusión ampliada tras V174')[0].rstrip()+'\n'
    old_intro='Manuscrito de trabajo ampliado hasta V174 para un TFM de Ciencia de Datos aplicada a las Ciencias Sociales. Integra V128–V140 y V169–V174; la síntesis V141–V167 se conserva en informes separados y está pendiente de integración editorial.'
    new_intro='Manuscrito de trabajo ampliado hasta V180 para un TFM de Ciencia de Datos aplicada a las Ciencias Sociales. Integra las fases V128–V140, la validación posterior V141–V150D, la síntesis de disponibilidad funcional V153–V167 y las campañas V169–V180. Las líneas paralelas de afiliación V150–V154 conservan sus informes y requieren integración más completa. Los identificadores de experimentos reutilizados se desambiguan mediante nombre de archivo y hash.'
    assert old_intro in manuscript;manuscript=manuscript.replace(old_intro,new_intro,1)
    addition='Los nuevos contrastes separan el uso causal de recurrencia de su capacidad de aprendizaje y muestran dependencia de la formación respecto al espacio de políticas: una representación afín que rara vez organiza cooperación desde cero puede conservarla tras una historia cooperativa. Varias hipótesis fuertes fallan sus criterios prospectivos. Un ensayo humano de monitoreo se reproduce numéricamente, pero no establece una diferencia precisa entre destinatarios de información ni confirma el simulador.\n\n'
    manuscript=manuscript.replace('**Palabras clave:**',addition+'**Palabras clave:**',1)
    def chapter(name):return re.sub(r'^(#+) ',r'#\1 ',(ROOT/'docs'/name).read_text(encoding='utf8'),flags=re.M)
    old_chapter=(ROOT/'docs/TFM_CAPITULO_INSTITUCIONES_Y_MEMORIA_BORRADOR.md').read_text(encoding='utf8').splitlines()[0]
    old_marker='#'+old_chapter
    assert manuscript.count(old_marker)==1,old_marker
    expansion=chapter('TFM_CAPITULO_VALIDACION_AMPLIADA_V141_V150.md')+'\n\n'+chapter('TFM_CAPITULO_DISPONIBILIDAD_Y_ESTABILIDAD.md')+'\n\n'
    manuscript=manuscript.replace(old_marker,expansion+old_marker,1)
    marker='## Discusión integrada';assert manuscript.count(marker)==1
    manuscript=manuscript.replace(marker,chapter('TFM_CAPITULO_MEMORIA_REPRESENTACION_Y_CONTRASTE_HUMANO.md')+'\n\n'+marker,1)
    old_limit='La comparación generativa humana dispone actualmente de una sola red completamente libre. Falta repetirla en redes excluidas con selección anidada, revisar sensibilidad de especificaciones y estudiar dependencia contemporánea de acciones. Los scripts originales de los autores se inspeccionaron, pero no se reprodujo toda su cadena analítica. La matriz completa de competidores MARL tampoco está implementada.'
    new_limit='La fase inicial solo examinó una red completamente libre; V141 amplió el contraste a las tres redes de ese tratamiento y V144 añadió otra fuente humana. Persisten límites de tamaño, supuestos de dependencia y selección de preguntas tras conocer datos. V179 reconstruye una especificación principal publicada; no toda la cadena de sus autores. La matriz completa de competidores MARL continúa pendiente y los datos humanos no identifican las ecuaciones ocupacionales o ecológicas.'
    assert old_limit in manuscript;manuscript=manuscript.replace(old_limit,new_limit,1)
    manuscript=manuscript.replace('El documento no declara publicación del repositorio ni revisión externa ya realizadas.',
        'Los protocolosV175–V180 se congelaron en una rama pública separada antes de sus pruebas. Esa publicación proporciona trazabilidad temporal; no es revisión científica independiente. El manuscrito sigue siendo un borrador académico.',1)
    conclusions='''## Conclusiones ampliadas hasta V180

Los resultados separan cuatro propiedades que no pueden darse por equivalentes: representar una organización funcional, llegar a ella desde cero, mantener una trayectoria y disponer de una función mediante renovación de microestados. Las identidades de equilibrio y renovación son condicionales al juego diseñado; los agentes que reciben un protocolo de contrato o un observador contable no han inventado esas instituciones.

La evidencia reciente cierra interpretaciones prometedoras que no superaron sus falsadores. La recurrencia privada ayuda frente a un MLP particular, pero no acredita alta eficiencia ni supera de manera demostrada un rival privado sencillo. La ganancia grupal de borrar memoria colectiva rara vez es una mejora de Pareto. Añadir un intercepto perjudica la formación desde cero, pero no destruye de manera generalizada a poblaciones ya organizadas. La búsqueda preespecificada de un sesgo invasor común tampoco confirma esa explicación del fracaso.

La ampliación humana demuestra capacidad de reproducción estadística y obliga a distinguir un efecto detectable de una diferencia entre efectos. El ensayo de monitoreo no valida el generador multiagente por cercanía temática. Las comparaciones de predicción y generación tampoco autorizan una ley universal sobre complejidad: sus rankings cambian por población y por indicador.

El TFM aporta un laboratorio reproducible, mecanismos explícitos, diagnósticos causales y resultados negativos conservados. La afirmación de originalidad queda limitada a candidatas específicas pendientes de contraste frente a antecedentes y de confirmación independiente. CT2 histórico permanece 61/100; no se concede 2/3 ni 3/3. La finalización académica requiere revisión integral de las referencias centrales, unidad editorial y adecuación a las normas universitarias; este archivo no sustituye esos pasos.

'''
    manuscript=manuscript.replace('## Referencias seleccionadas',conclusions+'## Referencias seleccionadas',1)
    # Remove a duplicate ODD2020 entry in the copied selected-reference list.
    paragraphs=manuscript.split('\n\n');seen_odd=False;out=[]
    for paragraph in paragraphs:
        if paragraph.startswith('Grimm, Volker;') and 'The ODD protocol' in paragraph:
            if seen_odd:continue
            seen_odd=True
        out.append(paragraph)
    manuscript='\n\n'.join(out).rstrip()+'\n\n'
    for ref in refs:
        manuscript+=f"{ref['authors']} ({ref['year']}). *{ref['title']}*. {ref['container']}. [Fuente primaria]({ref['url']}).\n\n"
    target=ROOT/'docs/TFM_MANUSCRITO_TRABAJO_V180.md';assert not target.exists();target.write_text(manuscript,encoding='utf8')
    assert sha(parent)==parent_hash
    sources=['results/INFORME_V175_V180_20261115.md','results/V175_V180_FINAL_AUDIT.json',
             'REPORT_V153_V156_PIVOT_AFTER_CT2_55.md','REPORT_V157_V167_MICRO_MACRO_INSTITUTIONAL_RENEWAL.md',
             'results/V141_CROSS_NETWORK_GENERATIVE.json','results/V142_CALIBRATION_DRIFT_DECOMPOSITION.json',
             'results/V144_EXTERNAL_HUMAN_MICRO_MACRO.json','results/V144B_PAIR_BOOTSTRAP_10000.json',
             'results/V148_PIVOTALITY_FLEXIBLE_RIVAL_CV.json','results/V149_PIVOTALITY_2P4P_COMPARISON.json',
             'results/V150D_UNIQUE_RESCUER_FULL_RIVAL.json']
    build=dict(parent_manuscript_sha256=parent_hash,new_manuscript_sha256=sha(target),words=len(manuscript.split()),
               bibliography_count=len(data['references']),parent_preserved=True,not_complete_approved_tfm=True,
               not_accredited_2of3=True,source_hashes={name:sha(ROOT/name) for name in sources})
    (ROOT/'results/TFM_V180_BUILD.json').write_text(json.dumps(build,indent=2),encoding='utf8')
    entry=ROOT/'INICIO_INVESTIGACION_CIENTIFICA.md'
    entry.write_text('# Estado vigente hasta V180 — 15/11/2026\n\nLeer `handoff_codex/ESTADO_20261115_V180.md`. Informe nuevo: `results/INFORME_V175_V180_20261115.md`. Manuscrito integrado: `docs/TFM_MANUSCRITO_TRABAJO_V180.md`. Se ejecutaron66evoluciones y una reproducción humana con10000reasignaciones;464comprobaciones técnicas. Se conservaron negativos y se cancelóM16 al fallar su gate. CT2 histórico61/100 sin aumento;N2=N3=0. Objetivo científico ACTIVO;TFM todavía borrador. Ningún entrenamiento pendiente. Los bloques previos se conservan debajo.\n\n'+entry.read_text(encoding='utf8'),encoding='utf8')
    print('V180_INTEGRATED',json.dumps(build),flush=True)


if __name__=='__main__':main()
