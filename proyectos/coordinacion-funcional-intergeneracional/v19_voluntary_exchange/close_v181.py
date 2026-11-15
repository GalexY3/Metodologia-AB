"""Close the matched-budget falsification without changing V175–V180."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from research_resource_limits import apply_limits
from v178_private_affine_rival import generation

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[2]
PREFIX=ROOT.relative_to(REPO).as_posix()+'/'
OUT=ROOT/'research/V181_20261115'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write(path,data):
    p=ROOT/path;assert not p.exists(),path
    p.write_bytes(data.encode('utf8') if isinstance(data,str) else data)


def save(path,data):write(path,json.dumps(data,ensure_ascii=False,indent=2)+'\n')


def main():
    limits=apply_limits(3);s=json.loads((ROOT/'results/v181_matched_budget/SUMMARY.json').read_text())
    freeze_path=ROOT/'results/v181_matched_budget/FREEZE.json';freeze=json.loads(freeze_path.read_text());checks=[]
    def check(name,value):assert value,name;checks.append(dict(name=name,passed=True))
    for name,key in (('v181_matched_budget.py','source_sha256'),('PREREG_V181_MATCHED_BUDGET_AND_BIAS_RESET.md','protocol_sha256')):
        check('frozen_'+name,sha(ROOT/name)==freeze[key])
        remote=subprocess.check_output(['git','cat-file','blob',freeze['prereg_commit']+':'+PREFIX+name],cwd=REPO)
        check('remote_bytes_'+name,remote==(ROOT/name).read_bytes())
    epoch=int(subprocess.check_output(['git','show','-s','--format=%ct',freeze['prereg_commit']],cwd=REPO))
    check('remote_before_local_freeze',epoch<=freeze_path.stat().st_mtime)
    for r in s['results']:
        directory=ROOT/f"results/v181_matched_budget/{r['arm']}_{r['seed']}"
        curve=json.loads((directory/'CURVE.json').read_text());pop=np.load(directory/'FINAL_POPULATION.npz')
        label=r['arm']+'_'+str(r['seed'])
        check(label+'_complete',len(curve)==3000 and curve[-1]['total_generations']==6000)
        check(label+'_Q',np.mean([t['Q'] for t in curve[-500:]])==r['Q_tail'])
        check(label+'_replay',np.array_equal(generation(pop['theta'].reshape(100,5,3),pop['y0'],3)[0],pop['fit']))
        check(label+'_checkpoints',len(list(directory.glob('CHECKPOINT_*.npz')))==6)
        check(label+'_limits',r['limits']['priority']=='BelowNormal' and r['limits']['affinity']==16515072 and r['limits']['numba_threads']==3)
    p=s['paired'];warm=np.array([r['warm'] for r in p]);continuation=np.array([r['continue_affine'] for r in p]);reset=np.array([r['reset_bias'] for r in p])
    check('primary_gate_matches',s['primary_gate']==all(np.median(warm-a)>=.2 and np.sum(warm>a)>=6 for a in (continuation,reset)))
    check('primary_gate_passed',s['primary_gate'])
    prior_zip=ROOT/'research/V175_V180_20261115/EVIDENCE.zip'
    check('prior_archive_preserved',sha(prior_zip)=='a3ce5625692f949f5adf70ad7080c2965f088de776e0d51c7e0a133640cb254d')
    rng=np.random.default_rng(181900);indices=rng.integers(0,8,(10000,8));contrasts={}
    for name,a in (('CONTINUE',continuation),('RESET_BIAS',reset)):
        delta=warm-a
        contrasts[name]=dict(mean_advantage=float(delta.mean()),median_advantage=float(np.median(delta)),
                paired_bootstrap_mean_CI95=np.quantile(delta[indices].mean(1),[.025,.975]).tolist(),
                positive_pairs=int(np.sum(delta>0)))
    stats=dict(mean_warm=float(warm.mean()),mean_continue=float(continuation.mean()),mean_reset=float(reset.mean()),
               paired=p,contrasts=contrasts,bootstrap_unit='original paired evolutionary history; n=8',
               bootstrap_status='post-hoc descriptive uncertainty; not a new external confirmatory sample')
    save('results/V181_REVIEWED_STATISTICS.json',stats)
    save('results/V181_FINAL_AUDIT.json',dict(checks=checks,passed=len(checks),limits=limits,
             additional_continuations=16,independent_original_histories=8,prior_control_reused=True,
             primary_gate_passed=True,external_confirmation=False,N2=0,CT2_historical=61))
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(11,4.5),layout='constrained')
    for i in range(8):axes[0].plot([0,1,2],[warm[i],continuation[i],reset[i]],'o-',lw=.9,alpha=.7,color='#267ca8')
    axes[0].set_xticks([0,1,2],['Preparar FULL\ny abrir','Afín continua\ndesde cero','Afín y reinicio\ndel intercepto'])
    axes[0].set_ylabel('Q: riqueza total media');axes[0].set_ylim(-.02,1);axes[0].grid(axis='y',alpha=.18)
    axes[0].set_title('Todos: 6.000 generaciones totales')
    for j,(label,a) in enumerate((('Continuar',continuation),('Reiniciar sesgo',reset))):
        axes[1].scatter(np.full(8,j)+np.linspace(-.08,.08,8),warm-a,color='#267ca8',s=32)
        axes[1].hlines(np.median(warm-a),j-.2,j+.2,color='#25313d',lw=2)
    axes[1].axhline(0,color='#555',lw=1);axes[1].axhline(.2,color='#b26438',ls='--',lw=1)
    axes[1].set_xticks([0,1],['Frente a continuar','Frente a reiniciar'])
    axes[1].set_ylabel('Ventaja de la historia preparada');axes[1].set_ylim(-.05,.85);axes[1].grid(axis='y',alpha=.18)
    axes[1].set_title('Ocho historias emparejadas; barras: medianas')
    fig.suptitle('V181: la diferencia persiste al igualar presupuesto y reinicio',fontsize=13)
    fig.text(.5,-.03,'Control preparado reutilizado de V180; 16 continuaciones nuevas. Currículo externo, no institución aprendida.\nEl umbral de mediana es prospectivo; no acredita prioridad ni confirmación independiente.',ha='center',fontsize=9)
    image=ROOT/'results/FIG_V181_MATCHED_BUDGET.png';assert not image.exists();fig.savefig(image,dpi=220,bbox_inches='tight');plt.close(fig)
    table='\n'.join(f"| {r['seed']} | {r['warm']:.6f} | {r['continue_affine']:.6f} | {r['reset_bias']:.6f} |" for r in p)
    report=f'''# V181 — Historia con presupuesto total y reinicio controlados

15/11/2026. Control prospectivo motivado por una limitación detectada después de V180. **CT2 histórico61/100 sin aumento;N2=N3=0.** Los originalesV175–V180 y sus paquetes permanecen intactos.

El criterio preregistrado se cumple frente a los dos rivales. Con6000generaciones totales, la historia FULL→OPEN tieneQmedia{warm.mean():.6f}, mientras AFFINE_FULL→AFFINE_FULL tiene{continuation.mean():.6f} y reiniciar solo el intercepto de AFFINE_FULL tiene{reset.mean():.6f}. La diferencia no desaparece por añadir las3000generaciones que faltaban al comparador o por reiniciar ese gen.

## Diseño y alcance

La comparación secundaria anterior mezclaba3000generaciones afines desde cero con3000de preparaciónFULL y otras3000OPEN. Aquí se continúan las ocho poblaciones afines de V178 durante3000generaciones más. CONTINUE conserva sus tres genes;RESET_BIAS pone únicamente el intercepto a0 antes de continuar y después permite que vuelva a mutar. Ambos comparten la cinta aleatoria de continuación de los OPEN correspondientes deV180. El kernel, la física, la selección privada y el número de genes mutados se conservan.

Se reutilizan ocho controles anteriores y se ejecutan dieciséis continuaciones nuevas. Las réplicas son ocho historias originales emparejadas, no24poblaciones independientes. Ninguna ronda, persona o checkpoint se cuenta como réplica del algoritmo. El protocolo y el código se congelaron en `{freeze['prereg_commit']}` antes de continuar; se verificaron sus bytes remotos y su fecha frente alFREEZE local.

| Semilla de continuación | Preparada, V180 | Afín continuada | Afín con reinicio de sesgo |
|---|---:|---:|---:|
{table}

El primario exigía mediana de ventaja≥0,20 y ventaja positiva en al menos6/8pares, frente a AMBOS controles. Las medianas son{contrasts['CONTINUE']['median_advantage']:.6f} y{contrasts['RESET_BIAS']['median_advantage']:.6f};hay8/8y7/8signos positivos. Se conserva la historia180117: la preparación también colapsó y no tiene ventaja frente al reinicio.

Los intervalos bootstrap descriptivos de la ventaja media, remuestreando las ocho historias sin reentrenar, son{contrasts['CONTINUE']['paired_bootstrap_mean_CI95']} y{contrasts['RESET_BIAS']['paired_bootstrap_mean_CI95']}. Se calculan después de la prueba como incertidumbre interna; no equivalen a validación externa.

![Control de presupuesto](FIG_V181_MATCHED_BUDGET.png)

## Qué descarta y qué no identifica

El resultado descarta que la ventaja observada de esa historia se deba únicamente a disponer de3000generaciones extra o a poner el intercepto a0al comenzar la segunda fase, bajo estas poblaciones y este optimizador. La clase afín puede conservar rendimiento que no alcanza desde cero con igual presupuesto total. No se ha identificado aún una explicación única:trayectoria selectiva, valores deS/A, escalas de mutación y cuencas del sistema siguen vinculados al historial.

La secuencia de clases está impuesta por el investigador. Los agentes NO aprendieron a crear esa secuencia, a restringir su espacio de políticas, a negociar una constitución o a implantar monitoreo. Es un mecanismo de acceso a políticas bajo un currículo externo. Los antecedentes de aprendizaje por etapas y dependencia de espacios de estrategia impiden atribuir novedad general a esa idea. La candidata específica debe discriminarse frente a ellos y confirmarse independientemente antes de aspirar a2/3.

V181 no rescata los criterios fallados deV175,V177,V178oV180:capacidad de memoria genérica, trampa de Pareto, ventaja privada afín, destrucción generalizada de mantenimiento e invasión destructiva siguen fallados. La condición de alta eficiencia0,70tampoco se cumple en todas las historias preparadas. El efecto es de acceso y desempeño condicionado, sin ley sociológica acreditada.

## Evidencia y reproducción

`results/V181_FINAL_AUDIT.json` contiene{len(checks)}comprobaciones, incluidos los16puntos finales reejecutados exactamente. `results/v181_matched_budget` conserva curvas completas, RNG, seis checkpoints por continuación y poblaciones. La primera generación de los ocho controles V180 se reprodujo antes de ejecutar para comprobar la cinta aleatoria. El informe previo y el ensayo humano conservan su alcance.

En una carpeta con los insumos originales: `python v181_matched_budget.py --audit-only`, después `python v181_matched_budget.py --prereg-commit {freeze['prereg_commit']}`. No sobrescribir los resultados ya existentes. El nuevo paquete incluye los insumos mínimos de V178/V180 y el kernel congelado;el archivo humano no es necesario.
'''
    write('results/INFORME_V181_PRESUPUESTO_Y_REINICIO_20261115.md',report)
    section=f'''### V181: igualar presupuesto y reiniciar el sesgo

La comparación de V178 desde cero con V180 preparado tenía una limitación adicional: la primera historia recibía 3.000 generaciones y la segunda 6.000 en dos fases. V181 se preregistró después de detectar ese problema y antes de ejecutar los controles. Se continuaron las ocho poblaciones afines hasta 6.000 generaciones, tanto conservando sus genes como reiniciando únicamente el intercepto antes de la continuación.

Con igual presupuesto, la historia preparada conserva Q media={warm.mean():.4f}, frente a {continuation.mean():.4f} de la afín continuada y {reset.mean():.4f} con reinicio del intercepto. La mediana de ventaja es {contrasts['CONTINUE']['median_advantage']:.4f} y {contrasts['RESET_BIAS']['median_advantage']:.4f}; los signos positivos aparecen en ocho y siete de ocho historias. Se cumple el criterio prospectivo frente a ambos rivales. El control preparado se reutiliza; las dieciséis continuaciones no constituyen una nueva muestra independiente de toda la campaña.

Este contraste refuerza la instancia de dependencia histórica y descarta dos explicaciones simples: tiempo adicional y reinicio de ese gen por sí solos. No identifica de manera única la trayectoria selectiva, la escala de mutaciones o las cuencas de la dinámica. Tampoco demuestra aparición autónoma de una institución: el currículo de representación se impuso externamente. Un antecedente cooperativo sigue sin garantizar alta eficiencia en todas las historias; una de las ocho colapsa.

![Presupuesto total controlado](../results/FIG_V181_MATCHED_BUDGET.png)

La originalidad y la confirmación independiente siguen pendientes. El positivo no borra los criterios fallados anteriores ni aumenta automáticamente CT2. Véase el [informe V181](../results/INFORME_V181_PRESUPUESTO_Y_REINICIO_20261115.md) para el protocolo, los pares y las comprobaciones.

'''
    parent=ROOT/'docs/TFM_MANUSCRITO_TRABAJO_V180.md';manuscript=parent.read_text(encoding='utf8')
    manuscript=manuscript.replace('ampliado hasta V180','ampliado hasta V181',1).replace('campañas V169–V180','campañas V169–V181',1)
    marker='### Contraste humano: información y destinatarios institucionales';assert manuscript.count(marker)==1
    manuscript=manuscript.replace(marker,section+marker,1)
    manuscript=manuscript.replace('## Conclusiones ampliadas hasta V180','## Conclusiones ampliadas hasta V181',1)
    manuscript=manuscript.replace('Varias hipótesis fuertes fallan sus criterios prospectivos.',
        'Varias hipótesis fuertes fallan sus criterios prospectivos. La ventaja de una historia de representación restringida persiste al igualar el presupuesto total y frente al reinicio del intercepto, bajo un currículo impuesto por el investigador.',1)
    write('docs/TFM_MANUSCRITO_TRABAJO_V181.md',manuscript)
    save('results/TFM_V181_BUILD.json',dict(parent_sha256=sha(parent),new_sha256=sha(ROOT/'docs/TFM_MANUSCRITO_TRABAJO_V181.md'),
               words=len(manuscript.split()),bibliography_records=87,parent_preserved=True,not_complete_approved_tfm=True,CT2_historical=61,N2=0))
    handoff=f'''# Continuación científica hasta V181 —15/11/2026

Objetivo ACTIVO. Leer primero `results/INFORME_V181_PRESUPUESTO_Y_REINICIO_20261115.md` y después el handoffV180. Manuscrito vigente:`docs/TFM_MANUSCRITO_TRABAJO_V181.md`. CT2 histórico61/100,N2=N3=0 sin incremento.

V181 resuelve un confusor de presupuesto en el contraste secundario deV180. Se ejecutaron16continuaciones nuevas (dos por cada una de8historias afines), usando las mismas semillas de continuación que los8OPENprevios. Todas las historias tienen6000generaciones totales. Preparada media{warm.mean():.6f};afín continuada{continuation.mean():.6f};afín con reinicio del intercepto{reset.mean():.6f}. Primario pasa frente a ambos controles:medianas{contrasts['CONTINUE']['median_advantage']:.6f}/{contrasts['RESET_BIAS']['median_advantage']:.6f},8/8y7/8signos positivos. La historia180117se conserva negativa frente aRESET. Se reejecutaron16puntos finales exactamente;{len(checks)}comprobaciones finales. No quedan entrenamientos propios activos.

Preregistro remoto verificado:{freeze['prereg_commit']}. La fuente principal es `v181_matched_budget.py`;no cambió el kernelV178. Los resultadosV175–V180, sus siete criterios fallados y sus fuentes permanecen intactos. El paqueteV175–V180 revisión2 tieneSHAa3ce5625692f949f5adf70ad7080c2965f088de776e0d51c7e0a133640cb254d;su commit de resultados exactos esbfe3e23f171d70f530ddfe7372f4ac49451249e9. Su primera publicación9404824721694a3d91c81dddb9f49aa46afd3284 normalizó saltos de línea;se preservó, corrigió con--no-filters y verificó transmisiónHTTPdelZIP. El manifiesto exterior ahora coincide byte por byte con el interior;1159archivos científicos son idénticos entre revisiones. Recibos están enresearch/V175_V180_20261115.

El positivo es una instancia controlada de acceso mediante historia de representación;NO es una institución aprendida:el currículo lo impusimos. No separa aún escala de mutación, genotipos deS/A, cuencas y selección. No afirmar novedad genérica de currículo ni elevarABpor más semillas. La independencia externa pertinente sigue faltando. No ampliar automáticamente variantes de arquitectura;una continuación debe discriminar un mecanismo o contrastar una predicción nueva frente a antecedentes sólidos. La afiliación endógena y otros comparadores siguen pendientes para un TFM final.

Publicación V181: consultar `research/V181_20261115/PUBLICATION_RECEIPT.json` si existe. Mantener rama localc032a32d2d8d7710a6ad5a88519b0801ea186891 e índice ajenos preservados;remoto correctoGalexY3/Metodologia-AB,rama propiaresearch/aldea-memory-v175-20261115. Usar siempre índice aislado yhash-object--no-filterspara artefactos conhashes. No pedir nuevas cuotas ni marcar objetivo completo por cerrar un bloque.
'''
    write('handoff_codex/ESTADO_20261115_V181.md',handoff)
    entry=ROOT/'INICIO_INVESTIGACION_CIENTIFICA.md';previous=entry.read_bytes()
    backup=ROOT/'research/V181_20261115/INICIO_BEFORE_V181.md';OUT.mkdir(parents=True,exist_ok=True);backup.write_bytes(previous)
    entry.write_bytes(('# Estado vigente hasta V181 —15/11/2026\n\nLeer `handoff_codex/ESTADO_20261115_V181.md`. Control de6000generaciones y reinicio del intercepto ejecutado:criterio de ventaja histórica pasa frente aambos rivales. Manuscrito:`docs/TFM_MANUSCRITO_TRABAJO_V181.md`. CT2histórico61sin aumento;N2=N3=0. Currículo externo,no institución aprendida. Objetivo ACTIVO. Se conservan los bloques anteriores.\n\n').encode('utf8')+previous)
    save('research/V181_20261115/LEDGER_A_J.json',dict(study='V181',distance='D1',
         A='Resolve total-generation and bias-reset confounds in the V180 history comparison.',
         B='Extra training or bias reinitialization may suffice without FULL pretraining.',
         C='8matched histories,16new continuations,all6000generations total;prior warm control reused.',
         D='Frozen kernel;first warm generation exact;remote source/protocol bytes and timing checked.',
         E='All16continuations completed with6checkpoints and exact final replays.',
         F='Retain seed180117 and all prior failed gates;no checkpoint selection.',
         G='Primary median/sign gate passed against both rivals.',
         H='Keep specific representational-history candidate;do not claim autonomous institution.',
         I='Internal evidence,externally imposed curriculum,novelty and independent confirmation pending.',
         J=dict(prereg=freeze['prereg_commit'],audit='results/V181_FINAL_AUDIT.json',CT2_historical=61,N2=0)))
    selected={ROOT/name for name in ['v181_matched_budget.py','close_v181.py','PREREG_V181_MATCHED_BUDGET_AND_BIAS_RESET.md',
       'v178_private_affine_rival.py','research_resource_limits.py','results/V181_PRE_RUN_AUDIT.json','results/V181_FINAL_AUDIT.json',
       'results/V181_REVIEWED_STATISTICS.json','results/TFM_V181_BUILD.json','results/FIG_V181_MATCHED_BUDGET.png',
       'results/INFORME_V181_PRESUPUESTO_Y_REINICIO_20261115.md','docs/TFM_MANUSCRITO_TRABAJO_V181.md',
       'handoff_codex/ESTADO_20261115_V181.md','results/v180_open_policy_space/MAINTENANCE.json']}
    selected.update(p for p in (ROOT/'results/v181_matched_budget').rglob('*') if p.is_file())
    for seed,parent_seed in zip(range(180115,180123),range(178115,178123)):
        for mode in ('FULL','AFFINE_FULL'):selected.add(ROOT/f'results/v178_private_affine_M5/{mode}_{parent_seed}/FINAL_POPULATION.npz')
        selected.add(ROOT/f'results/v180_open_policy_space/maintenance/OPEN_{seed}/CURVE.json')
    selected.update(p for p in OUT.iterdir() if p.is_file())
    manifest=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(selected)]
    encoded=(json.dumps(manifest,indent=2)+'\n').encode('utf8');write('research/V181_20261115/SHA256.json',encoded)
    archive=OUT/'EVIDENCE.zip';assert not archive.exists()
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for r in manifest:z.write(ROOT/r['path'],r['path'])
        z.writestr('EVIDENCE_SHA256.json',encoded)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None and z.read('EVIDENCE_SHA256.json')==encoded
        for r in manifest:assert hashlib.sha256(z.read(r['path'])).hexdigest()==r['sha256']
    save('research/V181_20261115/PACKAGE_RECEIPT.json',dict(bytes=archive.stat().st_size,sha256=sha(archive),
          payload_files=len(manifest),every_member_verified=True,CRC_verified=True,prior_archive_preserved=True,
          human_data_included=False,additional_continuations=16,histories=8,CT2_historical=61,N2=0))
    print('V181_CLOSED',json.dumps(dict(stats=stats,checks=len(checks),archive_bytes=archive.stat().st_size,archive_sha256=sha(archive))),flush=True)


if __name__=='__main__':main()
