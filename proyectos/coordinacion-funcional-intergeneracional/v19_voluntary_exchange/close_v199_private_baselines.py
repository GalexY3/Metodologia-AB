"""Preserve primary failures, strong controls, distributional harm and scope."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

B = Path(__file__).resolve().parent
R = B/'results'
ROOT = R/'V199_PRIVATE_BASELINES'


def polish(text):
    # Editorial spacing only; preserve identifiers, links and decimal values.
    words = 'escenarios|mundos|sesiones|oportunidades|registros|comprobaciones|valores|personas|raíces|brazos|con|sin|en|de|del|por|para|y|si|al'
    return re.sub(r'(?<=\d)(?=(?:'+words+r')\b)', ' ', text)


def main():
    output = R/'V199_SCIENTIFIC_SYNTHESIS.json'
    assert not output.exists()
    audit = json.loads((R/'V199_PRIVATE_BASELINES_AUDIT.json').read_text(encoding='utf-8'))
    analysis = json.loads((R/'V199_PRIVATE_BASELINES_ANALYSIS.json').read_text(encoding='utf-8'))
    summary = json.loads((ROOT/'SUMMARY.json').read_text(encoding='utf-8'))
    mechanism = json.loads((R/'V199B_EXPECTILE_AUDIT/SUMMARY.json').read_text(encoding='utf-8'))
    assert not audit['failures'] and not analysis['H1_hysteretic_maintenance_passed'] and not analysis['H2_hysteretic_formation_passed']
    runs = {}
    for row in summary['runs']:
        key = (row['cohort'], row['k'], row['rule'], row['method'])
        runs[key] = json.loads((ROOT/f"{row['cohort']}_k{row['k']}_{row['rule']}/{row['method']}.json").read_text(encoding='utf-8'))
    names = ['IQL_JITTER', 'IQL_EXACT', 'IQL_SLOW', 'HYSTERETIC', 'RUNNING_MEAN', 'LMRL2', 'FROZEN', 'IQL_MIN']
    table = []
    for name in names:
        formation = [r for key, r in runs.items() if key[0] == 'FORMATION' and key[3] == name]
        useful = sum(r['history'][8]['greedy_mean_welfare'] >= .05 and r['history'][8]['greedy_low_payoff'] >= 0
                     and r['history'][8]['greedy_high_payoff'] >= 0 for r in formation)
        table.append(dict(method=name, maintenance75=summary['maintenance_counts'].get(name),
            formation_useful_count=useful if formation else None,
            adaptation_maintenance=summary['adaptation_counts']['MAINTENANCE'].get(name),
            adaptation_formation=summary['adaptation_counts']['FORMATION'].get(name)))
    synthesis = dict(method_table=table, primary_H1_passed=False, primary_H2_passed=False,
        primary_counts=analysis['primary_counts'], new_formation_world_roots=192,
        lower_variance_private_learners_form_and_maintain_without_pulses_in_six=True,
        those_two_controls_fail_reversal_in_all_six=True,
        no_method_meets_adaptation_in_at_least_four=True,
        voting_without_exit_is_not_voluntary_participation=True,
        expectile_diagnostic_is_posthoc_not_a_rescued_primary=True,
        CT2_historical=61, new_branch_score=None, N2=0, N3=0)
    output.write_text(json.dumps(synthesis, indent=2), encoding='utf-8')
    # Per-world records preserve the inference grain; paired methods are not
    # counted as independent roots and maintenance reuses its old parents.
    records = R/'V199_WORLD_RECORDS'; records.mkdir(exist_ok=False)
    for cohort in ['MAINTENANCE', 'FORMATION']:
        for k in [4, 8, 12]:
            for rule in ['UNANIMITY', 'MAJORITY']:
                chosen = [r for key, r in runs.items() if key[:3] == (cohort, k, rule)]
                for w in range(32):
                    methods = []
                    for run in chosen:
                        histories = [{field: value[w] if field.endswith('world_welfare') or field in
                            ['greedy_world_low_payoff', 'greedy_world_high_payoff'] else value
                            for field, value in row.items() if field in ['step', 'accuracy', 'method',
                                'greedy_world_welfare', 'native_world_welfare', 'greedy_world_low_payoff', 'greedy_world_high_payoff']}
                                     for row in run['history']]
                        methods.append(dict(method=run['method'], history=histories,
                            observed_phase_world_welfare=[r['world_welfare'][w] for r in run['observed_private_payoffs']]))
                    record = dict(cohort=cohort, k=k, rule=rule, world=w, groups_per_world=20,
                        is_new_training_root=cohort == 'FORMATION', methods_paired_within_world=True,
                        seed_entropy_base=[199, int(cohort == 'FORMATION'), k, int(rule == 'MAJORITY'), w],
                        streams=dict(losses=0, environment=1, actions=2),
                        maintenance_loss_and_Q_parent_is_V195=cohort == 'MAINTENANCE', methods=methods)
                    record['loss_stream_used_only_for_formation'] = True
                    (records/f'{cohort}_k{k}_{rule}_w{w:02d}.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
    cases = [(k, rule) for k in [4, 8, 12] for rule in ['UNANIMITY', 'MAJORITY']]
    labels = [('U' if rule == 'UNANIMITY' else 'M')+str(k) for k, rule in cases]
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.2))
    for cohort, color, offset in [('MAINTENANCE', '#1769aa', -.08), ('FORMATION', '#b44e18', .08)]:
        rows = [next(r for r in analysis['contrasts'] if r['cohort'] == cohort and r['k'] == k and r['rule'] == rule
                     and r['method'] == 'HYSTERETIC') for k, rule in cases]
        values = np.array([r['mean_advantage_against_IQL_EXACT'] for r in rows])
        lo = np.array([r['six_contrast_family_CI991667'][0] for r in rows]); hi = np.array([r['six_contrast_family_CI991667'][1] for r in rows])
        axes[0].errorbar(np.arange(6)+offset, values, yerr=[values-lo, hi-values], fmt='o', capsize=3,
                         color=color, label='Mantenimiento' if cohort == 'MAINTENANCE' else 'Formación nueva')
    axes[0].axhline(0, color='black', lw=1); axes[0].axhline(.02, color='gray', ls=':', lw=1)
    axes[0].set(title='Hysteretic frente a IQL_EXACT, paso8000', ylabel='Diferencia de bienestar', xticks=np.arange(6), xticklabels=labels)
    axes[0].legend(fontsize=8)
    for method, field, color, marker, label in [
        ('HYSTERETIC', 'greedy_low_payoff', '#d8812d', 'o', 'Hysteretic: pérdida1'),
        ('HYSTERETIC', 'greedy_high_payoff', '#a92e2e', 'x', 'Hysteretic: pérdida7'),
        ('IQL_SLOW', 'greedy_low_payoff', '#62a9c8', 'o', 'Tasa lenta: pérdida1'),
        ('IQL_SLOW', 'greedy_high_payoff', '#1769aa', 'x', 'Tasa lenta: pérdida7')]:
        values = [runs['FORMATION', k, rule, method]['history'][8][field] for k, rule in cases]
        axes[1].plot(np.arange(6), values, marker=marker, color=color, lw=1.5, label=label)
    axes[1].axhline(0, color='black', lw=1)
    axes[1].set(title='Retorno por tipo de riesgo: formación', ylabel='Pago privado esperado', xticks=np.arange(6), xticklabels=labels)
    axes[1].legend(fontsize=8)
    for ax in axes:
        ax.grid(alpha=.2); ax.set_xlabel('Regla y tamaño nominal k (k−1votantes)')
    fig.suptitle('V199: el optimismo no beneficia a todos los miembros ni a todas las reglas', fontsize=13)
    fig.text(.5, .015, 'IC bootstrap con ajuste Bonferroni nominal por seis contrastes, familias separadas. Patrón por regla: interpretación descriptiva posterior.', ha='center', fontsize=8)
    fig.tight_layout(rect=(0, .04, 1, .93)); fig.savefig(R/'FIG_V199_RIVAL_AND_PRIVATE_RISK.png', dpi=180); plt.close(fig)
    colors = dict(IQL_EXACT='#555555', IQL_SLOW='#1769aa', HYSTERETIC='#bd6c1c', RUNNING_MEAN='#9225a7', FROZEN='#128478')
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.2), sharey=True)
    for ax, rule in zip(axes, ['UNANIMITY', 'MAJORITY']):
        inverse = json.loads((ROOT/f'MAINTENANCE_k12_{rule}/INVERSION_WITHOUT_LEARNING.json').read_text(encoding='utf-8'))
        inverse = {r['method']: r['greedy_mean_welfare'] for r in inverse}
        for method, color in colors.items():
            history = runs['MAINTENANCE', 12, rule, method]['history']
            x, y = [], []
            for row in history:
                x.append(row['step']); y.append(row['greedy_mean_welfare'])
                if row['step'] == 8000:
                    x.append(8000); y.append(inverse[method])
            ax.plot(x, y, color=color, label=method, lw=1.7)
        ax.axvline(8000, color='black', ls='--', lw=1)
        ax.axhline(0, color='gray', lw=.8)
        ax.set(title='Unanimidad, k12' if rule == 'UNANIMITY' else 'Mayoría, k12', xlabel='Nuevas oportunidades', ylim=(-1.55, .65))
        ax.grid(alpha=.15)
    axes[0].set_ylabel('Bienestar codicioso esperado'); axes[0].legend(fontsize=8, loc='lower left')
    fig.suptitle('V199: conservar experiencia puede dificultar la adaptación a señales invertidas', fontsize=13)
    fig.text(.5, .015, 'Corte8000: precisión.8→.2sin aviso. El salto inmediato se calcula con la política intacta. Todas las condiciones están en los JSON.', ha='center', fontsize=9)
    fig.tight_layout(rect=(0, .04, 1, .93)); fig.savefig(R/'FIG_V199_STABILITY_AND_REVERSAL.png', dpi=180); plt.close(fig)
    method_table = '\n'.join('|'+r['method']+'|'+ '|'.join('—' if r[f] is None else str(r[f])+'/6' for f in
        ['maintenance75', 'formation_useful_count', 'adaptation_maintenance', 'adaptation_formation'])+'|' for r in table)
    form_table = '\n'.join(f"|{k}|{rule}|"+'|'.join(f"{runs['FORMATION',k,rule,m]['history'][8]['greedy_mean_welfare']:.5f}" for m in
        ['IQL_EXACT', 'IQL_SLOW', 'HYSTERETIC', 'RUNNING_MEAN', 'LMRL2'])+'|' for k, rule in cases)
    harm = [r for r in mechanism['records'] if r['cohort'] == 'FORMATION' and r['rule'] == 'MAJORITY' and r['peer_epsilon'] == 0]
    harm_table = '\n'.join(f"|{r['k']}|{r['private_types'][1]['best_unilateral_expected_payoff']:.5f}|{100*r['private_types'][1]['fraction_people_with_negative_best_response_value']:.2f}%|" for r in harm)
    report = f'''# V199: cooperación privada, ruido y límites de voluntariedad

Campaña completada, dos hipótesis principales fallidas. La conservación sin pulsos sí es posible con controles privados conocidos. El nuevo límite decisivo es sostener adaptación útil y ofrecer una salida real a los miembros expuestos a pérdidas. CT2 histórico61sin modificar; rama nueva sin puntuación, N2=N3=0.

## Resultados que cambian la decisión

Reducir la tasa simétrica a.01o usar una media acumulada permite conservar>=75%del valor parental en6/6escenarios, con retornos esperados medios no negativos para ambos tipos de pérdidas. Esos mismos procedimientos producen políticas útiles desde cero sin pulsos colectivos en6/6escenarios de192mundos nuevos. Son controles de aprendizaje conocidos, no una institución inventada. Refutan la necesidad general de un programador que fuerce ensayos colectivos para estas condiciones; no prueban suficiencia en todos los entornos o aprendices.

Las hipótesis principales estaban fijadas sobre HYSTERETIC frente a IQL_EXACT: mantenimiento y formación debían pasar al menos4/6escenarios, con utilidad privada, mejora>=.02e intervalos simultáneos positivos. Ambas pasan3/6y FALLAN. Los tres positivos corresponden a unanimidad; los de mayoría fallan. La interpretación del patrón opuesto por regla es posterior y descriptiva, no una hipótesis general rescatada por seleccionar subgrupos.

| Método | Mantiene75% | Forma política útil | Se adapta: padres | Se adapta: formación |
|---|---:|---:|---:|---:|
{method_table}

Formación útil en esta tabla significa bienestar>=.05y retornos medios>=0para pérdida1y7al paso8000; es un resumen secundario y no equivale a superar la hipótesis inferencial H2. FROZEN no es un aprendiz. Adaptación exige un precursor útil y recuperar>=75%de su valor después de invertir señales, con pagos no negativos para ambos tipos. Ningún método pasa adaptación en>=4/6.

## Formación nueva y pagos privados

| k | Regla | IQL_EXACT | Tasa.01 | Hysteretic | Media acumulada | LMRL2 |
|---:|---|---:|---:|---:|---:|---:|
{form_table}

Cada celda es bienestar codicioso esperado al paso8000, integrado sobre estados y señales nuevos, no recompensa de un máximo de entrenamiento. Se conservan también conducta nativa mientras exploran y retornos físicos realmente cobrados. Por ejemplo, en formación k12mayoría, RUNNING_MEAN obtiene valor codicioso.52661y conducta nativa.48117; su retorno realizado medio durante las8000sesiones es.40862. Al invertir señales, el retorno realizado medio de las4000sesiones siguientes cae a−1.27379. La estabilidad no evita daño durante un cambio.

![Rivales y distribución del riesgo](FIG_V199_RIVAL_AND_PRIVATE_RISK.png)

No basta contar acuerdos. En formación con mayoría k12, HYSTERETIC tiene bienestar codicioso medio.14001, pero las personas de pérdida7reciben−.14850y las de pérdida1+.41418, promediando primero dentro de cada mundo. El rendimiento medio positivo oculta un reparto perjudicial para un tipo de miembro. Con tasa.01, los dos tipos reciben+.43053y+.51320. La regla de mayoría y el método son suministrados; no se atribuye al grupo una preferencia institucional aprendida.

## Conservación y adaptación son pruebas distintas

Las dos cohortes afrontan8000oportunidades originales y4000después de invertir precisión de señal.8→.2sin aviso. El contenido informativo disponible y la física no cambian: intercambiar las etiquetas de señal de cualquier política recuperaría exactamente su valor anterior. La inversión es un falsador impuesto por el investigador, no una sorpresa social empíricamente observada.

Tasa lenta y media acumulada retienen experiencia, pero no superan la recuperación registrada en ningún escenario. Hysteretic se adapta en tres escenarios, sin resolver sus daños bajo mayoría. IQL rápido se adapta en tres o dos, según cohorte y desempate, sin pasar la conservación previa. El control congelado conserva antes del cambio y fracasa después. No existe aquí un vencedor global entre los métodos examinados y sus parámetros fijados.

![Conservación y reversión](FIG_V199_STABILITY_AND_REVERSAL.png)

El fracaso original de IQL no se elimina al sustituir el jitter por desempates exactos: ambos pasan0/6en mantenimiento. Algunas trayectorias y criterios secundarios sí cambian; no se declara irrelevancia universal del desempate. La comparación comparte monedas y mundos, no acciones idénticas cuando las políticas difieren.

## Auditoría posterior: optimismo y ausencia de salida

V199B se diseñó DESPUÉS de ver la campaña y no rescata H1/H2. Con compañeros congelados se calcula el retorno esperado de cada acción propia y la mejor respuesta unilateral. Hay una limitación constitutiva: bajo mayoría, votarNOno permite evitar una decisión ratificada por otros. La tarea no incluye salida, exclusión de costes ni retirada del proyecto. La libertad de votar no equivale a participación voluntaria.

En los perfiles de formación HYSTERETIC con compañeros codiciosos, la siguiente auditoría describe a las personas de pérdida7. Estos valores agrupan personas; no son la media de32medias por tipo usada arriba. No son intervalos confirmatorios.

| k, mayoría | Mejor respuesta unilateral: pago medio | Personas con mejor respuesta de valor negativo |
|---:|---:|---:|
{harm_table}

Por tanto, en esos perfiles parte del daño no se corrige cambiando unilateralmente la política binaria con los compañeros fijos. Esto no demuestra imposibilidad de influir en su aprendizaje futuro ni un equilibrio estable. Bajo unanimidad, en cambio, NOgarantiza0por construcción. La diferencia de poder de rechazo está programada y restringe cualquier afirmación de cooperación voluntaria.

La regla hysteretic también cambia el objetivo estadístico: su deriva escalar con alpha.1/beta.01apunta a un expectil10/11del retorno, no a su media. La derivación y las1000comprobaciones de residuo son álgebra conocida, coherente con la pérdida asimétrica de [Rowland y colaboradores2019, sección3.1](https://proceedings.mlr.press/v97/rowland19a.html). No se ejecuta EDRL ni se reclama teorema original. Los rankings expectiles concuerdan mejor con parte de las decisiones observadas bajo unanimidad; esa explicación no mejora el ajuste en todos los perfiles de mayoría. No se fuerza un mecanismo único ni se confunde el cero de deriva con la media estacionaria exacta de Q con ganancia constante.

## Diseño, rivales y validez

MAINTENANCE reutiliza32mundos parentales por escenario y Q asistidas de V195: no son nuevas raíces. FORMATION incorpora192raíces nuevas,32por cada combinación k/regla, con20grupos por mundo. Los métodos están apareados dentro del mundo; los84brazos de método/escenario/cohorte no son84experimentos científicos independientes. Se guardan384JSONpor mundo, de los que192son registros nuevos y192reutilizan padres. No son datos humanos ni réplicas de laboratorios externos.

Se implementó la actualización [hysteretic de Matignon y colaboradores2007](https://doi.org/10.1109/IROS.2007.4399095) y la regla [LMRL2 de Wei y Luke2016](https://www.jmlr.org/papers/v17/15-417.html), con parámetros publicados y ecuaciones inspeccionadas visualmente. LMRL2 se adapta a decisiones contextuales terminales, gamma0y sin difusión a futuros estados; usa su selección nativa y Q inicial−L_i. IQL_MIN controla esa inicialización en formación. No es reproducción de sus benchmarks originales ni comparación exhaustiva con parámetros tuneados. Su fracaso por defecto no demuestra inferioridad general frente a un nuevo método nuestro.

RUNNING_MEAN usa9pseudobservaciones de prior por celda, no los verdaderos conteos históricos de los padres, que no se conservaron. Todos los algoritmos, reglas de voto y grupos son exógenos. Se aprende conducta bajo esas instituciones, no su invención. Esta campaña tabular no es una prueba de grokking neuronal ni revoca la falsación de coadaptación continua de V193.

El registro `a0113021889e89b729e4513adafee1081cde48b2` congeló también el código del análisis antes de entrenar. Nueve archivos se verificaron por HTTP y seis padres por hash. La validación técnica comprueba elecciones, actualizaciones, física del kernel, visitas e independencia de grupos. Un motor separado verifica32256valores, error máximo{audit['maximum_error']:.3g},336invariantes de memoria y24reconstrucciones de retornos privados a partir de las medias. Son auditorías de cálculo, no confirmación de una contribución social original.

Las hipótesis H1/H2 utilizan20000remuestreos por32mundos e intervalos bootstrap con ajuste Bonferroni nominal de99.1667%por contraste dentro de seis casos. Las dos cohortes constituyen familias declaradas por separado, sin cobertura95%conjunta prometida. Los contrastes de los otros métodos son secundarios. No se seleccionan máximos ni se cambian umbrales al observar.

## Decisión científica y evaluación AB

Queda refutada una interpretación general de necesidad de pulsos externos: controles privados simples forman y conservan cooperación útil en los seis escenarios originales. La dificultad pendiente combina plasticidad y riesgo distribuido. Antes de nuevas afirmaciones institucionales debe existir opción efectiva de no participar, con costes y compensaciones auditados. Ajustar más tasas sin esa salida mantendría un problema de validez conceptual.

La prueba siguiente debe examinar participación o compromisos realmente rechazables con aprendices competentes y rivales contractuales fuertes. Una opción de salida o un contrato suministrado será una regla programada; habrá que medir por separado su adopción y mantenimiento aprendidos. No se cuenta esa prueba como realizada. La investigación material de profesiones y donaciones y el contraste empírico humano siguen formando parte del objetivo global.

![Referencia histórica CT2](FIG_CT2_V175_V180.png)

CT2 histórico61permanece intacto. La nueva rama no recibe puntuación; no se adjudica un1/3por número de semillas ni se acredita2/3. Los resultados negativos y las versiones anteriores permanecen íntegros. El objetivo científico sigue activo.
'''
    report = polish(report)
    (R/'INFORME_V199_APRENDICES_PRIVADOS_20261115.md').write_text(report, encoding='utf-8')
    chapter = report.replace('](FIG_', '](../results/FIG_')
    (B/'docs/TFM_CAPITULO_APRENDICES_PRIVADOS_V199.md').write_text(chapter, encoding='utf-8')
    previous = B/'docs/TFM_MANUSCRITO_TRABAJO_V198.md'
    text = previous.read_text(encoding='utf-8').replace('ampliado hasta V198', 'ampliado hasta V199', 1)
    text = text.replace('campañas V169–V194.', 'campañas V169–V199.', 1)
    text = text.replace('**Palabras clave:**',
        'La comparación posterior con aprendices privados conocidos obtiene formación sin pulsos colectivos en192mundos nuevos y conservación en una cohorte parental, pero no adaptación robusta a señales invertidas. El optimismo beneficia unanimidad y puede imponer pérdidas a miembros bajo mayoría. Una auditoría de mejores respuestas identifica que el modelo carece de salida: votar no no garantiza evitar el acuerdo. Las hipótesis principales de superioridad hysteretic fallan y se mantiene pendiente la validación de participación realmente voluntaria.\n\n**Palabras clave:**', 1)
    manuscript = B/'docs/TFM_MANUSCRITO_TRABAJO_V199.md'; assert not manuscript.exists()
    manuscript.write_text(polish(text)+'\n\n'+chapter, encoding='utf-8')
    ledger = dict(experiment='V199 private known learners plus V199B posthoc audit', DRIFT_distance='D1',
        A='Can competent private learners replace oracle mean updates and sustain adaptation?',
        B='V198 oracle mean dynamics preserved cooperation; private comparators missing',
        C='Known hysteretic/LMRL2 rules, symmetric slow and running-mean controls, strict-tie ablation',
        D='Six scenarios,192new formation worlds, parent maintenance cohort, fixed signal reversal',
        E='Protocol, technical proof, analysis source publicly frozen before training',
        F='32256independent metric checks,336memory invariants,24private-return reconstructions',
        G='H1/H2require>=4/6with private-utility and simultaneous-CI gates; adaptation separately fixed',
        H=dict(primary_counts=analysis['primary_counts'], H1_passed=False, H2_passed=False,
               private_lower_variance_maintenance_counts=6, private_lower_variance_adaptation_counts=0),
        I='Permanent pulse necessity refuted under competent known learners; absence of exit limits voluntary-cooperation claims',
        J='Audit participation/exit and rejectable commitments before institutional originality',
        V199B_is_posthoc=True, V199B_does_not_rescue_primary_failures=True,
        new_unique_N1_awarded=False, N2=0, N3=0, CT2_historical=61, new_branch_score=None,
        parent_manuscript_sha256=hashlib.sha256(previous.read_bytes()).hexdigest(),
        manuscript_sha256=hashlib.sha256(manuscript.read_bytes()).hexdigest())
    (R/'V199_AB_LEDGER.json').write_text(json.dumps(ledger, indent=2), encoding='utf-8')
    (B/'handoff_codex/ESTADO_20261115_V199.md').write_text(
        '# V199 y V199B terminados\n\n'
        'Leer INFORME_V199_APRENDICES_PRIVADOS_20261115.md y manuscritoV199. H1/H2fallan3/6. '
        'IQL_SLOWyRUNNING_MEAN forman y conservan utilidad en6/6sin pulsos; ambos fallan adaptación0/6. '
        'Ningún método pasa adaptación>=4/6; hysteretic conserva/adapta unanimidad3/6pero daña alto riesgo bajo mayoría. '
        'V199Bposthoc: una parte de los de pérdida7tiene mejor respuesta unilateral negativa con compañeros fijos porque '
        'NOno evita costes aprobados por mayoría y no hay salida. No calificar esa participación de voluntaria. '
        'El análisis expectil es conocido y no explica todos los perfiles; no rescata H1/H2. '
        '192raíces nuevas de formación,384registros por mundo incluyendo192parentales; no multiplicar independencia por métodos. '
        'Audit32256sin fallos,memoria336yretornos24. Fuentes registradas a0113021889e89b729e4513adafee1081cde48b2. '
        'Siguiente cuello de botella: participación realmente rechazable, luego adopción/mantenimiento de compromisos con '
        'incentivos materiales privados; comparar contratos/MATE conocidos. Evitar más tuning sin corregir esa carencia. '
        'No relanzar V199: terminado. CT261sin editar,N2=N3=0. Objetivo global activo; ningún proceso de esta campaña queda ejecutándose.\n', encoding='utf-8')
    print(json.dumps(dict(primary_counts=analysis['primary_counts'], method_table=table,
        world_records=384, new_world_roots=192, manuscript_sha256=ledger['manuscript_sha256']), indent=2), flush=True)


if __name__ == '__main__':
    main()
