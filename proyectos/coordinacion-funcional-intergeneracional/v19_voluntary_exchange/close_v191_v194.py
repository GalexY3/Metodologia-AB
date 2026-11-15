"""Synthesize the positive, causal negative and missing-control result."""
from pathlib import Path
import hashlib
import json
import re
import shutil

B=Path(__file__).resolve().parent
R=B/'results'


def read(path):return json.loads((R/path).read_text(encoding='utf-8'))


def polish(text):
    units='símbolos|colores|archivos|contrastes|historias|contextos|evaluaciones|actualizaciones|parejas|pares|pasos|bloques|semillas|registros|interacciones|hilos|redes|aprendices|pagos|pagosobservados|comprobaciones|CPU|GPU'
    text=re.sub(r'(\d)(?=(?:'+units+r')\b)',r'\1 ',text)
    for a,b in [('histórico61','histórico 61'),('test1.0','test 1.0'),('test1','test 1'),('train1.0','train 1.0'),
                ('RNGexactamente','RNG exactamente'),('h_Fdel','h_F del'),('Uextraída','U extraída'),('q_Ucomo','q_U como'),
                ('en100%','en 100%'),('al100%','al 100%'),('alcanza100%','alcanza 100%'),('alcanza99','alcanza 99'),
                ('es.991','es .991'),('a.032','a .032'),('es.959','es .959'),('tras1100','tras 1100'),
                ('4/4se','4/4 se'),('4/4pares','4/4 pares'),('3/4bloques','3/4 bloques'),('3/4activos','3/4 activos'),
                ('31salidas','31 salidas'),('128unidades','128 unidades'),('weight_decay1','weight_decay 1'),
                ('60000de','60000 de'),('1200se','1200 se'),('5000reproduce','5000 reproduce'),
                ('1100y1200','1100 y 1200'),('14,25,10y0','14, 25, 10 y 0'),('enB','en B'),
                ('y2000','y 2000'),('31pagos','31 pagos'),('convención0','convención 0'),('puntuación,N2','puntuación, N2')]:text=text.replace(a,b)
    text=re.sub(r'Figura([1-4])',r'Figura \1',text)
    text=re.sub(r'(V19[234])`',r'\1 `',text)
    return text


def main():
    assert not (R/'INFORME_V191_V194_20261115.md').exists()
    audit=read('V191_V194_FINAL_AUDIT.json');s192=read('V192_DUAL_NEURAL_LEARNING/SUMMARY.json')
    s193=read('V193_FROZEN_PEER/SUMMARY.json');s194=read('V194_ORACLE_BANDIT/SUMMARY.json')
    assert s193['ongoing_coadaptation_necessity_refuted'] and s194['bandit_component_competence_passed']
    # Independently recompute the candidate rule used to label the four cases.
    full=[r for r in s192['runs'] if r['family']=='PRIVATE_FULL']
    assert sum(r['t_gen']>=5*r['t_mem'] and r['t_gen']-r['t_mem']>=2000 and r['final']['train_joint_greedy']>=.99 and r['final']['test_joint_greedy']>=.95 for r in full)==4
    timing=['| Semilla | t_mem | t_gen | Desfase aprendido A | Test final |','|---|---:|---:|---:|---:|']
    for r in full:timing.append(f"| {r['seed']} | {r['t_mem']} | {r['t_gen']} | {r['final']['train_chosen_gauge_A']} | {100*r['final']['test_joint_greedy']:.1f}% |")
    freezing=['| Compañero congelado | Red activa con test local >=.95 | Test activo medio | Test conjunto medio |','|---|---:|---:|---:|']
    for arm,label,field in [('FREEZE_A','A','test_B'),('FREEZE_B','B','test_A')]:
        rows=[r for r in s193['runs'] if r['arm']==arm]
        freezing.append(f"| {label} | {sum(r['final'][field]>=.95 for r in rows)}/4 | {100*sum(r['final'][field] for r in rows)/4:.2f}% | {100*sum(r['final']['test_joint_greedy'] for r in rows)/4:.2f}% |")
    capability=['| Semilla | t_mem | t_gen | Test conjunto final |','|---|---:|---:|---:|']
    for r in s194['runs']:capability.append(f"| {r['seed']} | {r['t_mem']} | {r['t_gen']} | {100*r['final']['test_joint_greedy']:.2f}% |")
    report=(B/'docs/V191_V194_REPORT_TEMPLATE.md').read_text(encoding='utf-8')
    for key,value in [('__TIMING_TABLE__','\n'.join(timing)),('__FREEZE_TABLE__','\n'.join(freezing)),('__CAPABILITY_TABLE__','\n'.join(capability))]:
        assert key in report;report=report.replace(key,value)
    report=polish(report).replace('un receptor FULL fijo','un agente FULL fijo')
    (R/'INFORME_V191_V194_20261115.md').write_text(report,encoding='utf-8')
    chapter='\n'.join('#'+line if line.startswith('#') else line for line in report.splitlines())
    chapter=chapter.replace('## De la convención a la generalización: dos aprendices neuronales privados',
                            '## De la convención aprendida a la generalización individual',1)
    chapter=chapter.replace('](FIG_','](../results/FIG_')+'\n'
    (B/'docs/TFM_CAPITULO_DOS_REDES_V191_V194.md').write_text(chapter,encoding='utf-8')
    parent_path=B/'docs/TFM_MANUSCRITO_TRABAJO_V190.md'
    assert hashlib.sha256(parent_path.read_bytes()).hexdigest()=='ab0a5e30e951d295f1d70429d0613097847c89c5d70d34c97ea1e835b9f8c49e'
    manuscript=parent_path.read_text(encoding='utf-8')
    manuscript=manuscript.replace('Manuscrito de trabajo ampliado hasta V190','Manuscrito de trabajo ampliado hasta V194',1)
    manuscript=manuscript.replace('las campañas V169–V190','las campañas V169–V194',1)
    manuscript=manuscript.replace('## Discusión integrada',chapter+'\n## Discusión integrada',1)
    discussion=('La nueva prueba con dos redes distingue una convención aprendida de la necesidad de seguir coadaptándose. '
                'Los pares privados generalizan tarde, pero la red activa mantiene incluso los mismos pesos que en la trayectoria conjunta al congelar al compañero desde la primera memorización. '
                'El fallo del test conjunto congelado mide también el componente detenido y no identifica una incapacidad del que continúa. '
                'Esta diferencia refuerza el principio común del programa: una regularidad del sistema no basta para identificar el proceso que la produce.\n\n')
    manuscript=manuscript.replace('## Discusión integrada\n\n','## Discusión integrada\n\n'+discussion,1)
    abstract=('La ampliación a dos aprendices neuronales obtiene convenciones privadas y generalización tardía de entradas locales nuevas de ambos. '
              'La congelación causal desde la primera memorización conserva la generalización local e incluso los pesos y momentos de las redes activas. '
              'El resultado no requiere coadaptación continua en esa fase. Un control adicional demuestra que el aprendiz binario puede resolver la tarea con un interlocutor correcto; '
              'la dificultad observada depende del origen del feedback bajo este algoritmo y presupuesto. La infraestructura contrafactual sigue impuesta y no se acredita originalidad2/3.\n\n')
    manuscript=manuscript.replace('**Palabras clave:**',abstract+'**Palabras clave:**',1)
    manuscript+='''
### Referencias añadidas para V191–V194

Klein, E., Mislovaty, R., Kanter, I., Ruttor, A. y Kinzel, W. (2004). [Synchronization of neural networks by mutual learning and its application to cryptography](https://proceedings.neurips.cc/paper/2004/hash/5a45828dead8c065099cb653a2185df1-Abstract.html). Advances in Neural Information Processing Systems17.

Ciosek, K. y Whiteson, S. (2020). [Expected Policy Gradients for Reinforcement Learning](https://www.jmlr.org/papers/v21/18-012.html). Journal of Machine Learning Research21(52),1–51. Los apuntes iniciales citaban su preprint2018; se adopta el registro editorial2020.

Kakade, S. M., Shalev-Shwartz, S. y Tewari, A. (2008). [Efficient bandit algorithms for online multiclass prediction](https://doi.org/10.1145/1390156.1390212). ICML,440–447.
'''
    manuscript_path=B/'docs/TFM_MANUSCRITO_TRABAJO_V194.md';manuscript_path.write_text(manuscript,encoding='utf-8')
    backup=B/'handoff_codex/backups_V194';backup.mkdir(exist_ok=False)
    for p in [B/'INICIO_INVESTIGACION_CIENTIFICA.md',B/'handoff_codex/GOAL_CIENTIFICO_AB_TFM.md']:shutil.copyfile(p,backup/p.name)
    state=('V192 obtiene cuatro candidatos de generalización tardía en dos redes privadas. V193 refuta necesidad de coadaptación continua después de memorizar: '
           'congelar cualquiera de los compañeros conserva test local1.0 y pesos/momentos activos idénticos. V194 confirma capacidad binaria con oráculos, '
           'test medio.991778 frente a.032169con compañeros aprendientes. No se acredita institución material ni AB2/3.')
    intro=B/'INICIO_INVESTIGACION_CIENTIFICA.md'
    intro.write_text('# Estado actualizado V194 — 15/11/2026\n\n'+state+'\n\nInforme: results/INFORME_V191_V194_20261115.md. Manuscrito: docs/TFM_MANUSCRITO_TRABAJO_V194.md. Reproducción: REPRODUCE_V191_V194.md. CT2 histórico61, rama nueva sin puntuación, N2=N3=0.\n\n---\n\n'+intro.read_text(encoding='utf-8'),encoding='utf-8')
    with (B/'handoff_codex/GOAL_CIENTIFICO_AB_TFM.md').open('a',encoding='utf-8') as f:
        f.write('\n## Resultado V191–V194 y decisión, 15/11/2026\n\n'+state+'\n\nEl objetivo global sigue activo. La incertidumbre siguiente es presupuesto igualado de feedback y origen de la señal: roles informativos fijos o rotativos con exactamente un vector contrafactual y un pago binario por interacción. No se ha ejecutado ese contraste. Una asignación informativa exógena no sería especialización emergente. Antes de originalidad, contrastar heterogeneidad de ruido/tasas y precondicionamiento Adam; antes de2/3, formular predicción discriminante y confirmación independiente.\n')
    ledger=[]
    rows=[('V191','TECHNICAL_IDENTITY_AND_DATA_AUDIT','Expected-gradient identity and private-gradient isolation; no scientific cohort'),
          ('V192','PREREGISTERED_DISCOVERY','4/4 private FULL late candidates;0/4 bandit; positive oracle control passed'),
          ('V193','PREREGISTERED_CAUSAL_FALSIFICATION','Both peer freezes preserve local generalization4/4 and active weights/moments bitwise'),
          ('V194','PREREGISTERED_CAPABILITY_CONTROL','Oracle bandit passes4/4; same estimator can generalize with correct peers')]
    for name,kind,outcome in rows:
        ledger.append(dict(id=name,kind=kind,DRIFT='D2: mechanism and architecture within the authorized collective-learning question',
            A='Distinguish system-level late accuracy from need for continuing coadaptation',
            B='Individual grokking after convention, feedback richness and bandit capacity are explicit rivals',
            C='Marginalization, importance sampling, mutual neural learning and binary classification have prior art',
            D='Sources/data frozen before scientific training; technical replay is historical validation only',
            E='Original metrics, weights, optimizer moments, RNG and context masks retained',F=outcome,
            G='Full horizons, predefined thresholds, no post-negative rescue; interaction magnitude labeled posthoc',
            H='192 distinct NumPy metric checks are technical independence, not new scientific replicas',
            I='No new original N1 awarded; N2=N3=0',J='Global goal active; next uncertainty is equal-budget feedback allocation',new_N1=False,N2=False))
    (R/'V191_V194_AB_LEDGER.json').write_text(json.dumps(ledger,indent=2),encoding='utf-8')
    evaluation=dict(method='AB3.2.1',date='2026-11-15',canonical_CT2_historical=61,new_branch_score=None,
        N1='NOT_AUDITED',new_original_N1_awarded=False,N2=0,N3=0,goal_status='active',
        V192_descriptive_late_candidate=True,V193_ongoing_coadaptation_necessity_refuted=True,V194_bandit_capability_passed=True,
        collective_grokking_causally_accredited=False,material_institution_learning_accredited=False,
        original_canonical_score_file_unchanged=True,manuscript_sha256=hashlib.sha256(manuscript_path.read_bytes()).hexdigest(),
        manuscript_words=len(re.findall(r'\S+',manuscript)),bibliographic_records=99)
    (R/'AB_EVALUACION_V191_V194_20261115.json').write_text(json.dumps(evaluation,indent=2),encoding='utf-8')
    assert hashlib.sha256((R/'AB_PROGRESO_CT2_CT3.json').read_bytes()).hexdigest()==audit['canonical_score_sha256']
    handoff=f'''# Estado final V194 — 15/11/2026

{state}

V192,V193,V194 terminados. No relanzar sesiones51396,45605,80478. Informe results/INFORME_V191_V194_20261115.md; auditoría results/V191_V194_FINAL_AUDIT.json; manuscrito docs/TFM_MANUSCRITO_TRABAJO_V194.md; reproducción REPRODUCE_V191_V194.md. Archivo y recibo final en research/V191_V194_20261115. Consultar PUBLICATION_RECEIPT.json después de verificación para el estado remoto real, no asumirlo de este texto.

V192:4/4 PRIVATE_FULL tardíos,4/4controlORACLE_FULL,0/4PRIVATE_BANDIT_IS. DesfasesA14,25,10,0. V193:ocho continuaciones de cuatro raíces; ambos brazos activos testlocal1.0;24checkpoints con pesos,momentos y RNG idénticos a continuación conjunta. No necesidad de adaptación continua después de primera memorización; no se prueba que la historia anterior fuera innecesaria. V194:4/4ORACLE_BANDIT_IS, media.991778; privado binario.032169. El2x2completo distingue feedback de interlocutor ya competente frente a aprendiente; su diferencia-en-diferencias.959609es descriptiva posterior, sin umbral confirmatorio propio.

Prerregistros: V192 babedeedbf604d9a05f134f80a1eb82383bcd402; V193 2b2adb035e0826dff0c7a75981bea290c3e3a339; V194 9b0d9ffd13d7ad353fb06fe45357c7279c988329. Último árbol antes de entrega5163c29ed346d8ba1c79dfc199cf593f96442610. Fuentes congeladas no se editaron. V193replay histórico hasta5000 bit idéntico; no es nueva ciencia. Datos originales y borradores fallidos preservados.192checks NumPy únicos:96V192y96combinedV193/V194; no duplicar64V193ya incluidos.

Modelo: dos redes cuadráticas128,31acciones, AdamW.001/wd1,epsilon-greedy.1,60000pasos. Cada red observa un par local y su feedback, no estado ajeno ni etiqueta local verdadera. FULL es un oráculo contrafactual externo31pagos; BANDIT un pago. MSEfull eIS tienen el mismo gradiente esperado condicionado al otro, pero Adam puede diferir. El juego e intereses comunes están impuestos. Precisión desplegada codiciosa100% no es pago exploratorio100%; techo conepsilon.1es.816129. No institución material aprendida ni ley humana.

Siguiente incertidumbre prometedora aún no ejecutada: un agente FULL y otro BANDIT fijos frente a rotar el receptor FULL por interacción, con exactamente una tabla y un pago escalar en ambas asignaciones. La competencia binaria con oráculo ya está demostrada. Fijar hipótesis y falsador antes de correr; tratar asignación como exógena, no división autónoma del trabajo. Rivales importantes: ruido/heterogeneidad de tasas, respuesta no lineal de Adam, sincronización por aprendizaje mutuo y experimentación estratégica clásica. No reclamar originalidad de una linealización genérica ni de reducción de varianza. Si no promete una predicción discriminante, volver a otra incertidumbre material del programa; no encadenar ajustes para rescatar una etiqueta.

Bibliografía99registros con lectura parcial declarada, no revisión sistemática. COMAya existía; añadidos Klein etal.NIPS2004, Ciosek/WhitesonJMLR2020(preprint2018) y Kakade etal.ICML2008Banditron. Sus programas no se ejecutaron. No inferir prioridad por búsquedas sin coincidencias.

CT2 histórico61, nueva rama sin puntuación,N1noauditado,N2=N3=0. Objetivo global activo. Git local HEADc032a32d2d8d7710a6ad5a88519b0801ea186891; índice del usuario SHA2560fc87bbef0de6ced68aa787004ef36d3c7934f757f51b5d8505665bd071184a1; canonicalscore SHA2560db038a35ee828a59c96de2a9e5e071545b26213ed692a29e79ad68f26778047. No stage-all/reset/pull/merge. Publicación por lista explícita e índice aislado; verificar blobs con ls-tree/cat-file, no git show con rutas largas. No subagentes ni mensajes a terceros. Preservar servicios3504,15036,15080. UnaGPU,doshilos,BelowNormal,seisCPU,max35%memoriaGPU y descansos.
'''
    (B/'handoff_codex/ESTADO_20261115_V194.md').write_text(polish(handoff),encoding='utf-8')
    for name in ['ESTADO_V192_EN_CURSO_20261115.md','ESTADO_V192_TERMINADO_V193_PENDIENTE_20261115.md','ESTADO_V194_TERMINADO_PENDIENTE_ENTREGA_20261115.md']:
        p=B/'handoff_codex'/name;text=p.read_text(encoding='utf-8')
        p.write_text('> Estado histórico. Consultar ESTADO_20261115_V194.md para el resultado final y su recibo de entrega.\n\n'+text,encoding='utf-8')
    print(json.dumps(evaluation),flush=True)


if __name__=='__main__':main()
