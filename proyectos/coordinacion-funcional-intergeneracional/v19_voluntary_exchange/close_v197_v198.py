"""Preserve the tie-law correction and mean-drift causal diagnostic."""
from pathlib import Path
import hashlib
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

B = Path(__file__).resolve().parent
R = B/'results'


def main():
    result_path = R/'V198_EXPECTED_DRIFT_ANALYSIS.json'
    assert not result_path.exists()
    tie = json.loads((R/'V197_TIE_POLICY_AUDIT.json').read_text(encoding='utf-8'))
    drift = json.loads((R/'V198_VOTING_EXPECTED_DRIFT/SUMMARY.json').read_text(encoding='utf-8'))
    audit = json.loads((R/'V198_NUMPY_FINAL_AUDIT.json').read_text(encoding='utf-8'))
    assert not audit['failures'] and drift['retention75_counts'] == {'MEAN_EPS08': 6, 'MEAN_EPS00': 6}
    comparisons = []
    for run in drift['results']:
        counterpart = 'PLASTIC_NO_PULSE_EPS08' if run['epsilon'] else 'PLASTIC_NO_PULSE_EPS00'
        original = next(r for r in tie['rows'] if r['study'] == 'V196_voting' and r['k'] == run['k']
                        and r['rule'] == run['rule'] and r['arm'] == counterpart)
        comparisons.append(dict(k=run['k'], rule=run['rule'], epsilon=run['epsilon'],
            sampled_final_welfare=original['corrected_expected_welfare'],
            mean_drift_final_welfare=run['history'][-1]['mean_welfare'],
            sampled_retention_ratio=original['corrected_retention_ratio'],
            mean_drift_retention_ratio=run['final_retention_ratio']))
    result = dict(comparisons=comparisons, mean_drift_retention75_counts=drift['retention75_counts'],
        sampled_retention75_counts={str(eps): sum(r['sampled_retention_ratio'] >= .75 for r in comparisons if r['epsilon'] == eps)
                                    for eps in [.08, 0.]},
        independent_new_roots=0, mean_operator_is_oracle_diagnostic=True,
        institutions_cannot_be_inferred_from_this_result=True, CT2_historical=61, new_branch_score=None, N2=0, N3=0)
    result_path.write_text(json.dumps(result, indent=2), encoding='utf-8')
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.1), sharey=True)
    for ax, epsilon in zip(axes, [.08, 0.]):
        rows = [r for r in comparisons if r['epsilon'] == epsilon]
        x = np.arange(len(rows))
        ax.bar(x-.18, [r['sampled_retention_ratio'] for r in rows], width=.36, color='#b44e18', label='Actualización privada muestreada')
        ax.bar(x+.18, [r['mean_drift_retention_ratio'] for r in rows], width=.36, color='#1769aa', label='Deriva media condicional (oráculo)')
        ax.axhline(.75, color='#333333', ls='--', lw=1.3, label='Criterio registrado: 75%')
        ax.set(xticks=x, xticklabels=[('U' if r['rule'] == 'UNANIMITY' else 'M')+str(r['k']) for r in rows],
               title=f'Exploración epsilon = {epsilon:.2f}', xlabel='Regla y tamaño nominal k', ylim=(0, 2.3))
        ax.grid(axis='y', alpha=.2)
        ax.set_axisbelow(True)
    axes[0].set_ylabel('Bienestar final / bienestar parental')
    axes[0].legend(fontsize=8, loc='upper left')
    fig.suptitle('V198: retirar las fluctuaciones de Q evita el deterioro en la dinámica media', fontsize=13)
    fig.text(.5, .02, 'U: unanimidad; M: mayoría; k−1 votantes. Cociente de medias de 32 mundos reutilizados; no nuevos grupos independientes.', ha='center', fontsize=9)
    fig.tight_layout(rect=(0, .05, 1, .93))
    fig.savefig(R/'FIG_V198_MEAN_VS_SAMPLED_PRIVATE_Q.png', dpi=180)
    plt.close(fig)
    errata_table = '\n'.join(f"|{r['k']}|{r['rule']}|{r['corrected_initial']:.8f}|{r['corrected_no_pulse_end']:.8f}|{100*r['corrected_retention_ratio']:.3f}%|" for r in tie['retention'])
    errata = f'''# Fe de erratas V197: ley de desempate de los evaluadores V195–V196 de votación

15/11/2026. Auditoría posterior; ningún nuevo entrenamiento. Los originales se conservan íntegros. No afecta V195 neuronal `WITHDRAW_COUNTERFACTUAL`, que utiliza argmax sin ese jitter y tiene su propia auditoría.

Los entrenadores de votación eligen `argmax(Q + U[0,1e-12])` con un ruido independiente por acción. Los evaluadores V195A/V196 trataban todo margen de magnitud<=1e−12como un empate de probabilidad1/2. Para un margen d=(Q_yes−Q_no)/1e−12la probabilidad continua correcta es0si d<=−1; `(1+d)^2/2` si −1<d<0; `1−(1−d)^2/2` si0<=d<1;1si d>=1. Por ejemplo d=.5produce.875, no.5. La derivación es la CDF de la diferencia de dos uniformes, no una nueva ley científica.

Se revisaron72arrays de políticas guardadas,645120entradas de estado contadas entre arrays, incluyendo controles repetidos.30arrays presentan discrepancias numéricas en alguna entrada. No son645120réplicas. La diferencia de probabilidad por acción puede acercarse a.5, pero la corrección máxima del bienestar medio entre las72políticas es {tie['maximum_absolute_welfare_correction']:.10f}. Se reconstruye la evaluación antigua con error máximo{tie['maximum_reproduction_error_for_previous_evaluator']:.3g}. La fórmula continua no pretende reproducir cada redondeo de coma flotante del generador.

| k | Regla | Valor inicial corregido | Final sin pulso epsilon.08 | Retención corregida |
|---:|---|---:|---:|---:|
{errata_table}

La conclusión principal V196 permanece:0/6alcanza75%de retención. Los seis intervalos bootstrap pareados del beneficio de mantener el pulso siguen siendo positivos al recalcularlos con32mundos y10000remuestreos. Son nuevos remuestreos, por lo que sus últimos decimales no tienen por qué coincidir con los previos. Los puntos intermedios de V196 no se recalculan: las Q de esos instantes no quedaron guardadas. Se corrigen los extremos para los que sí existen pesos. La expresión anterior «valor exacto» debe entenderse respecto a la aproximación de empate usada; esta fe de erratas la reemplaza para esos extremos.

El efecto pequeño no excusa mantener una ley de selección incorrecta. Tampoco acredita originalidad, confirmación externa o aumento de61. Fuentes, Q, JSON y reporte previos permanecen como historial; la referencia corregida es `V197_TIE_POLICY_AUDIT.json`.
'''
    (R/'ERRATA_V195_V196_TIE_POLICY_20261115.md').write_text(errata, encoding='utf-8')
    table = '\n'.join(f"|{r['k']}|{r['rule']}|{r['sampled_retention_ratio']:.4f}|{r['mean_drift_retention_ratio']:.4f}|" for r in comparisons if r['epsilon'] == .08)
    report = f'''# V198: el deterioro privado no identifica por sí solo incentivos destructivos

15/11/2026. Diagnóstico terminado y auditado. Doce continuaciones deterministas de seis poblaciones existentes;32mundos×20grupos por escenario. No hay nuevas raíces de entrenamiento ni una institución aprendida. CT2 histórico61sin cambios, rama nueva sin puntuación, N2=N3=0.

## Resultado causal que cambia la interpretación

Sustituir cada incremento aleatorio de Q por su esperanza condicional, preservando la frecuencia esperada de visitas y alpha.10, conserva al menos75%del bienestar parental en6/6escenarios con epsilon.08y en6/6con epsilon0. Las actualizaciones privadas muestrales originales, corregidas por V197, conservan75%en0/6para ambas tasas de exploración. El control se registró después de conocer los fracasos muestrales y antes de integrar las dinámicas medias parentales.

| k | Regla | Retención muestral epsilon.08 | Retención con deriva media epsilon.08 |
|---:|---|---:|---:|
{table}

Retención es el cociente entre bienestar medio final y bienestar medio inicial, no la media de cocientes por grupo. El punto final es8000, sin selección de máximos. Puede superar1cuando el operador mejora la política. En unanimidad k12, el valor medio pasa de.140297a.292549bajo deriva media epsilon.08; la continuación muestral acaba en.000354. En epsilon0, la dinámica media de ese caso conserva99.82%, frente a43.99%en la muestral. No se usa la ausencia de exploración para afirmar ausencia de ruido en el retorno.

![Deriva media y actualizaciones muestrales](FIG_V198_MEAN_VS_SAMPLED_PRIVATE_Q.png)

## Intervención y límites de identificación

Para cada estado privado s y acción a se integra el incremento `alpha*Pr(s)*pi_i(a|s)*(E[r_i|s,do(a),pi_-i]−Q_i(s,a))`, con las políticas anteriores a la actualización. Las probabilidades de estado/señal y las acciones ajenas se marginalizan usando la regla de ratificación y las pérdidas individuales. Los valores alternativos no se actualizan con una tasa artificialmente igual: se pondera su cobertura esperada de visitas. Los objetivos de cada individuo conservan su utilidad privada, aunque su cálculo requiere el modelo y los otros perfiles.

El operador es ORÁCULO y contrafactual. No es un agente que pueda calcular esos objetivos usando solo su pago realizado. Iterar esperanzas condicionales tampoco es tomar la esperanza de la trayectoria estocástica completa: el cambio de política es no lineal. El resultado demuestra suficiencia de esta sustitución para evitar el deterioro bajo estas condiciones; no identifica una solución descentralizada realizable ni garantiza un equilibrio estable a horizonte infinito.

V196 demostraba que sus Q concretas no se sostienen sin el pulso mientras continúan actualizándose. V198 restringe una interpretación más fuerte: ese fracaso, incluso con epsilon0, no basta para inferir que los incentivos medios destruyan necesariamente la cooperación, ni que una institución externa permanente sea intrínsecamente necesaria. Al retirar las fluctuaciones de actualización el mismo punto de partida permanece productivo o mejora durante el horizonte fijado. Sigue abierta la interacción entre tamaño de paso constante, discontinuidades de política, no estacionariedad e incentivos privados.

Las oportunidades de desviación unilateral detectadas por V195A no desaparecen de la evidencia. Una política puede durar bajo un algoritmo sin ser un equilibrio bayesiano. Tampoco se confunde estabilidad del perfil codicioso evaluado con bienestar de la conducta que explora.

## Controles, antecedentes y siguiente rival fuerte

El código/protocolo se congeló en GitHub `aef89672df24c52bb39d50a7fa777505d9c9cd9e` antes de integrar las trayectorias; nueve archivos se verificaron mediante bytes HTTP y siete padres/contextos se fijaron por hash. La validación previa comprueba1000objetivos condicionales en50fixtures contra enumeración explícita, error máximo1.78e−15. El evaluador final independiente por convolución reproduce768valores mundo/extremo, error máximo{audit['maximum_error']:.3g}; los doce estados iniciales corresponden exactamente a sus padres. Es independencia técnica de cálculo, no confirmación científica externa.

Los problemas de coordinación entre aprendices y la tolerancia a malos retornos ya se estudian en [Panait, Tuyls y Luke2008](https://www.jmlr.org/papers/v9/panait08a.html). La actualización asimétrica de errores tiene un rival directo en [Matignon, Laurent y Le Fort-Piat2007](https://doi.org/10.1109/IROS.2007.4399095). La selección estratégica por pivotalidad tiene antecedentes clásicos en [Feddersen y Pesendorfer1998](https://doi.org/10.2307/2585926). Se consultaron resúmenes/metadatos y, para el último, introducción y formulación del modelo; no se afirma lectura de todas las pruebas. Sus algoritmos originales no se ejecutaron en V198.

El paso científico siguiente debe enfrentar el mecanismo a aprendices privados competentes, empezando por hysteretic/lenient Q y estimación de menor varianza, con protección contra aprobar acuerdos perjudiciales. Si un algoritmo conocido conserva la cooperación, no hay base para inventar una institución para solucionar ese fallo ni para atribuir originalidad a hacerlo. Si persiste frente a esos rivales, tendría sentido estudiar compromisos y financiación voluntaria bajo incentivos auditados. Ninguna de esas pruebas se cuenta como realizada aquí.

## Evaluación AB y preservación

V197 corrige los extremos de la línea de votación sin borrar sus negativos. V195 neuronal demuestra apoyo contrafactual transitorio suficiente después de memorizar; V198 de votación diagnostica dependencia del procedimiento de actualización. Son tareas distintas, sin una ley social común demostrada. Se preservan fuentes, pesos, momentos, políticas iniciales/finales y fallos, y se prepara un manuscrito nuevo manteniendo las versiones anteriores.

![Referencia histórica CT2](FIG_CT2_V175_V180.png)

La figura de CT2 corresponde a la rama histórica y no puntúa esta nueva línea. No se añade un hallazgo1/3por una comprobación numérica ni se eleva el61por completar estos controles. La originalidad y la confirmación independiente siguen sin acreditarse. El objetivo global permanece activo.
'''
    (R/'INFORME_V197_V198_RUIDO_Y_DERIVA_20261115.md').write_text(report, encoding='utf-8')
    chapter = (errata+'\n\n'+report).replace('](FIG_', '](../results/FIG_')
    (B/'docs/TFM_CAPITULO_DERIVA_Y_RUIDO_V197_V198.md').write_text(chapter, encoding='utf-8')
    previous = B/'docs/TFM_MANUSCRITO_TRABAJO_V195.md'
    manuscript = previous.read_text(encoding='utf-8').replace('ampliado hasta V195 neural', 'ampliado hasta V198', 1)
    manuscript = manuscript.replace('**Palabras clave:**',
        'Una auditoría de votación corrige la ley de desempate y conserva el fracaso de mantenimiento privado observado. Un diagnóstico posterior evita ese deterioro al reemplazar las actualizaciones aleatorias por su deriva media, incluso sin exploración de acciones. Esto distingue la dinámica de aprendizaje de una supuesta imposibilidad por incentivos, sin proponer el operador oráculo como institución realizable.\n\n**Palabras clave:**', 1)
    target = B/'docs/TFM_MANUSCRITO_TRABAJO_V198.md'
    assert not target.exists()
    target.write_text(manuscript+'\n\n'+chapter, encoding='utf-8')
    ledger = dict(experiment='V198 expected private-Q drift', DRIFT_distance='D1',
        A='Sampling noise versus mean incentive drift after coordinated-pulse removal',
        B='V196 stochastic losses known; epsilon0 does not remove payoff noise',
        C='Integrate exact one-step conditional drift with original visitation frequencies',
        D='Six reused populations, two epsilons, fixed8000 horizon, no new scientific roots',
        E='Public preregistered source hashes and real HTTP verification',
        F='1000 pre-run payoff fixtures and768 independent final-world comparisons',
        G='Retain75%in>=4/6 versus mean-drift failure in>=4/6; mixed3/3 left unresolved',
        H=dict(mean_epsilon08_passed=6, mean_epsilon00_passed=6, sampled_epsilon08_passed=0, sampled_epsilon00_passed=0),
        I='Noise-free conditional drift avoids deterioration; not a realizable private learner or Nash-equilibrium proof',
        J='Known hysteretic/lenient private learners before an institutional originality claim',
        new_unique_N1_awarded=False, N2=0, N3=0, CT2_historical=61, new_branch_score=None,
        parent_manuscript_sha256=hashlib.sha256(previous.read_bytes()).hexdigest(),
        manuscript_sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    (R/'V198_AB_LEDGER.json').write_text(json.dumps(ledger, indent=2), encoding='utf-8')
    (B/'handoff_codex/ESTADO_20261115_V198.md').write_text(
        '# V195 neuronal, V197 y V198 completados\n\n'
        'V195_WITHDRAW:4/4test final medio.99480069tras retirar FULL al memorizar. V197:ley triangular de desempate corrige72políticas; '
        'máximo cambio de bienestar.000101166, fallo V1960/6se conserva. V198:deriva media conserva75%en6/6con epsilon.08y6/6con0; '
        'muestral anterior0/6en ambas. NumPy/convolución768checks pasan; V19548checks pasan. '
        'No confundir diagnósticos oráculo con aprendices privados ni estabilidad algorítmica con equilibrio. '
        'Siguiente prioridad: rivales privados hysteretic/lenient Q y menor varianza antes de nuevas instituciones. '
        'Todos los entrenamientos de este bloque terminaron; no hay que relanzarlos. CT261sin editar; N2=N3=0. '
        'Fuentes y resultados paralelos antiguos intactos. Objetivo científico global activo. Leer reportesV195_WITHDRAWyV197_V198y manuscritoV198.\n', encoding='utf-8')
    references = [
        dict(id='VapnikIzmailov2015', title='Learning Using Privileged Information: Similarity Control and Knowledge Transfer',
             authors='Vladimir Vapnik; Rauf Izmailov', year=2015, journal='JMLR16(61):2023–2049',
             url='https://www.jmlr.org/papers/v16/vapnik15b.html', read_scope='Publisher metadata and abstract; not full27pages',
             constraint='Transient privileged learning information is established; our algorithm is not SVM+ or its exact implementation'),
        dict(id='PanaitTuylsLuke2008', title='Theoretical Advantages of Lenient Learners: An Evolutionary Game Theoretic Perspective',
             authors='Liviu Panait; Karl Tuyls; Sean Luke', year=2008, journal='JMLR9(13):423–457',
             url='https://www.jmlr.org/papers/v9/panait08a.html', read_scope='Publisher metadata and abstract; full dynamics/proofs not read',
             constraint='Lenience and dynamical basins are known; original algorithm not executed here'),
        dict(id='MatignonLaurentLeFortPiat2007', title='Hysteretic Q-Learning: an algorithm for Decentralized Reinforcement Learning in Cooperative Multi-Agent Teams',
             authors='Laetitia Matignon; Guillaume J. Laurent; Nadine Le Fort-Piat', year=2007, doi='10.1109/IROS.2007.4399095',
             url='https://gjlaurent.github.io/assets/papers/Matignon2007hysteretic.pdf', read_scope='Indexed original abstract/introduction and author publication metadata; direct PDF open failed',
             constraint='Mandatory strong private-learner rival before claiming a new noise-tolerance institution; not yet implemented'),
        dict(id='FeddersenPesendorfer1998', title='Convicting the Innocent: The Inferiority of Unanimous Jury Verdicts under Strategic Voting',
             authors='Timothy Feddersen; Wolfgang Pesendorfer', year=1998, doi='10.2307/2585926', journal='APSR92(1):23–35',
             url='https://www.haverford.edu/sites/default/files/FeddersenPesendorfer-ConvictingTheInnocent.pdf',
             read_scope='Original abstract, introduction and model, PDFpages1–2ofarticle; proofs not all read',
             constraint='Private-signal pivotality and strategic voting are not new discoveries of our simulator')]
    (B/'literatura/V195_V198_REFERENCIAS_Y_LIMITES.json').write_text(json.dumps(dict(
        additive_supplement_not_replacement_of_archived_bibliography=True, records=references), indent=2), encoding='utf-8')
    print(json.dumps(dict(mean_counts=result['mean_drift_retention75_counts'], sampled_counts=result['sampled_retention75_counts'],
        manuscript_sha256=ledger['manuscript_sha256'], original_score_file_edited=False), indent=2), flush=True)


if __name__ == '__main__':
    main()
