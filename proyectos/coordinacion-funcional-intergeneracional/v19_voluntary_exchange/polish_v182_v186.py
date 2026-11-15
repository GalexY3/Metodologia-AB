"""One editorial revision; preserve the first narrative and all scientific bytes."""
from pathlib import Path
import hashlib
import json
import shutil

BASE = Path(__file__).resolve().parent


def read(relative):
    return json.loads((BASE/relative).read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def science_hashes():
    roots = ['V182_YAMAN_ARCHIVE_AUDIT','V182_OCTAVE_VALIDATION','V183_HAZARD_TIMING',
             'V184_PASTURE_REPLAY','V185_COLLECTIVE_GROKKING','V186_INFORMATION_BOTTLENECK']
    return {p.relative_to(BASE).as_posix():sha(p) for root in roots
            for p in sorted((BASE/'results'/root).rglob('*')) if p.is_file()}


def main():
    before = science_hashes()
    revision = BASE/'results/editorial_revision_1_V182_V186'
    revision.mkdir(exist_ok=False)
    paths = ['results/INFORME_V182_V186_20261115.md','docs/TFM_CAPITULO_REPRODUCCION_Y_GROKKING.md',
             'docs/TFM_MANUSCRITO_TRABAJO_V186.md','results/AB_EVALUACION_V182_V186_20261115.json',
             'handoff_codex/ESTADO_20261115_V186.md','close_v182_v186.py']
    for path in paths:
        shutil.copy2(BASE/path,revision/Path(path).name)
    audit=read('results/V182_V186_FINAL_AUDIT.json')
    timing=read('results/V183_HAZARD_TIMING/SUMMARY.json')
    pasture=read('results/V184_PASTURE_REPLAY/SUMMARY.json')
    pilot=read('results/V185_COLLECTIVE_GROKKING/SUMMARY.json')
    causal=read('results/V186_INFORMATION_BOTTLENECK/SUMMARY.json')
    ptable='\n'.join(f"| {r['seed']} | {r['condition']} | {100*r['final']['train']:.2f}% | {100*r['final']['test']:.2f}% | {r['t_mem']} | {r['t_gen']} |" for r in pilot['runs'])
    ctable='\n'.join(f"| {g['seed']} | {100*g['scores']['CONTINUE_JOINT']:.2f}% | {100*g['scores']['FROZEN_ORIGINAL']:.2f}% | {100*g['scores']['BIJECTIVE_REPAIR']:.2f}% | {g['gate_passed']} |" for g in causal['gates'])
    report=(BASE/'docs/V182_V186_REPORT_TEMPLATE.md').read_text(encoding='utf-8').format(
        audit=audit,effect=timing['primary_effect'],ci=timing['hierarchical_bootstrap_CI95'],
        pasture=pasture,ptable=ptable,ctable=ctable,causal=causal)
    (BASE/paths[0]).write_text(report,encoding='utf-8')
    chapter=report.replace('# V182–V186: reproducción adversarial y límites del grokking entre agentes',
                          '## Código publicado, riesgo material y generalización entre agentes',1)
    chapter=chapter.replace('\n## ','\n### ').replace('(FIG_','(../results/FIG_')
    (BASE/paths[1]).write_text(chapter,encoding='utf-8')
    parent=(BASE/'docs/TFM_MANUSCRITO_TRABAJO_V181.md').read_text(encoding='utf-8')
    manuscript=parent.replace('ampliado hasta V181','ampliado hasta V186',1).replace('las campañas V169–V181','las campañas V169–V186',1)
    manuscript=manuscript.replace('[Yaman et al., preprint de 2022](https://arxiv.org/html/2208.05568v3)',
                                  '[Yaman et al. (2023)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10598450/)')
    manuscript=manuscript.replace('\n## Discusión integrada','\n'+chapter+'\n## Discusión integrada',1)
    refs=read('literatura/references_verified.json')['references']
    old={r['id'] for r in read('literatura/backups/V182_V186_20261115/references_verified.json')['references']}
    fresh=[r for r in refs if r['id'] not in old]
    assert len(fresh)==7
    manuscript+='\n\n### Referencias añadidas para V182–V186\n\n'+'\n\n'.join(
        f"{r['authors']} ({r['year']}). *{r['title']}*. {r['container']}. [Fuente primaria]({r['url']})." for r in fresh)+'\n'
    target=BASE/paths[2]
    target.write_text(manuscript,encoding='utf-8')
    evaluation=read(paths[3])
    evaluation.update(manuscript_sha256=sha(target),manuscript_words=len(manuscript.split()),editorial_revision=2)
    (BASE/paths[3]).write_text(json.dumps(evaluation,indent=2),encoding='utf-8')
    handoff=f'''# Estado V186 — 15 de noviembre de 2026

El objetivo sigue ACTIVO, incluido el grokking colectivo solicitado por el investigador. CT2 histórico:61. Nueva rama sin puntuación. N2=N3=0. No se acredita originalidad por repetir simulaciones o reparar externamente un protocolo.

Leer `results/INFORME_V182_V186_20261115.md` y `docs/TFM_MANUSCRITO_TRABAJO_V186.md`. El manuscrito de trabajo tiene {evaluation['manuscript_words']} palabras y la base contiene94 fichas con alcance de lectura explícito. No es el TFM final aprobado.

V182: archivo CC0 original de Yaman,1.200 ajustes auditados. Dos discrepancias del código de pastura ejecutadas en Octave; los datos reconstruyen L0 correctamente. Port físico de ambos entornos con51 comprobaciones contra el original. No se reproduce el GA de pastura corregido.

V183:4.800 vidas nuevas. Efecto temporal0.0548931,IC95[0.0142699,0.1005942],por debajo del margen previo0.25. Hipótesis principal fallida y cerrada. V184:1.680 vidas únicas; RMSE0.8426 del código frente a4.0267 de la asignación intercambiada. Cooperación alta en varias condiciones; reproducción aproximada.

V185: diccionario fijo, generalización tardía2/2; pares privados sin memorizar toda la tarea2/2. Canceladas cuatro congelaciones porque no se cumplió su condición. Los protocolos finales usan24/28 símbolos; máximos de test85.89%/93.38%. El emisor no dispone de un cambio unilateral que mejore su acierto inmediato frente al receptor final. Esto no prueba un Nash general.

V186: mismo presupuesto total60000. Test al continuar conjuntamente35.19%/71.25%; diccionario aprendido fijo8.89%/22.30%; reparación externa98.78%/100%. Pasa el criterio prospectivo en ambas historias, pero la reparación es un oráculo. Se reutilizan dos historias, no seis estudios independientes. El replay de5000 pasos por historia reprodujo exactamente pesos,baseline y RNG. El siguiente rival necesario es aprendizaje privado competente de convenciones(Roth–Erev y mecanismos documentados contra ambigüedad),no más semillas del mismo REINFORCE. También falta una transición que necesite reorganización de varios aprendices. No confundir agrupación parcial conocida con novedad.

Todos los jobs de este bloque terminaron. Hay backups bibliográficos, manuscritos anteriores y una primera redacción conservada. El cambio editorial no altera ningún archivo de resultados científicos. Un helper de restauración RNG enV185 habría fallado al cargar enCUDA; no se llamó porque las congelaciones se cancelaron. V186 corrige ese detalle y verifica el replay. Los originales permanecen intactos.

Git local: rama research/aldea-v19-voluntary-exchange-20261111,HEAD c032a32d2d8d7710a6ad5a88519b0801ea186891. Índice de usuario SHA2560fc87bbef0de6ced68aa787004ef36d3c7934f757f51b5d8505665bd071184a1 preservado. Rama remota propia research/aldea-memory-v175-20261115; preregistro más reciente4164292c0d32adcb58c2d9ce4e944427578b8da2. Consultar el recibo de publicación para el commit final de resultados; no suponer que el preregistro contiene esos resultados.

Octave portátil:C:/Programación/tools/octave-11.3.0. Archivo original Yaman en literatura/original_code/Yaman2023. No subagentes,ChatRelay ni mensajes a terceros. Máximo dos workers con recursos sensatos,seisCPU y BelowNormal. No marcar el objetivo completo,pausado o bloqueado por falta de novedad.
'''
    (BASE/paths[4]).write_text(handoff,encoding='utf-8')
    # Replace the unused first prose draft in the one-shot closure source.
    source=BASE/'close_v182_v186.py'
    text=source.read_text(encoding='utf-8')
    first=text.index("    report=f'''# V182")
    end=text.index("    (RESULTS/'INFORME_V182_V186_20261115.md')",first)
    replacement="    report=(BASE/'docs/V182_V186_REPORT_TEMPLATE.md').read_text(encoding='utf-8').format(audit=audit, effect=effect, ci=ci, pasture=pasture, ptable=ptable, ctable=ctable, causal=causal)\n"
    source.write_text(text[:first]+replacement+text[end:],encoding='utf-8')
    after=science_hashes()
    assert before==after
    record=dict(reason='Correct readable Spanish narrative and document-relative figure paths',
                scientific_result_files=len(before),all_scientific_bytes_identical=True,
                manuscript_sha256=sha(target),manuscript_words=evaluation['manuscript_words'])
    (BASE/'results/V182_V186_EDITORIAL_REVISION.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    print(json.dumps(record),flush=True)


if __name__=='__main__':
    main()
