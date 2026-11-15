"""Create immutable V195 summaries and a new manuscript version, not scores."""
from pathlib import Path
import hashlib
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

B = Path(__file__).resolve().parent
R = B / 'results'
ROOT = R / 'V195_WITHDRAW_COUNTERFACTUAL'


def main():
    out = R / 'V195_WITHDRAW_ANALYSIS.json'
    assert not out.exists()
    audit = json.loads((R/'V195_WITHDRAW_NUMPY_FINAL_AUDIT.json').read_text(encoding='utf-8'))
    assert not audit['failures'] and audit['conditional_control_execution_matches_preregistration']
    summary = json.loads((ROOT/'SUMMARY.json').read_text(encoding='utf-8'))
    assert summary['withdrawal_primary_passed']
    rows, curves = [], {k: [] for k in ['FULL', 'BANDIT', 'WITHDRAW']}
    for seed in range(192115, 192119):
        full = json.loads((R/f'V192_DUAL_NEURAL_LEARNING/PRIVATE_FULL/metrics_s{seed}.json').read_text(encoding='utf-8'))
        bandit = json.loads((R/f'V192_DUAL_NEURAL_LEARNING/PRIVATE_BANDIT_IS/metrics_s{seed}.json').read_text(encoding='utf-8'))
        withdrawal = json.loads((ROOT/f'BOTH_BANDIT/metrics_s{seed}.json').read_text(encoding='utf-8'))
        cut = withdrawal['switch_step']
        prefix = [r for r in full['history'] if r['step'] <= cut]
        curves['FULL'].append(full['history'])
        curves['BANDIT'].append(bandit['history'])
        curves['WITHDRAW'].append(prefix+withdrawal['history'])
        entries = 31*cut+(60000-cut)
        rows.append(dict(seed=seed, cut=cut, full_test=full['final']['test_joint_greedy'],
            binary_from_scratch_test=bandit['final']['test_joint_greedy'],
            withdrawal_train=withdrawal['final']['train_joint_greedy'],
            withdrawal_test=withdrawal['final']['test_joint_greedy'],
            full_t_gen=full['t_gen'], withdrawal_t_gen=withdrawal['first_post_switch_sustained_test_step'],
            minimum_observed_post_switch_train=withdrawal['minimum_observed_post_switch_train_joint'],
            payoff_entries_per_local_training_input=entries,
            continuous_full_payoff_entries_per_local_training_input=31*60000,
            payoff_entry_reduction_fraction=1-entries/(31*60000)))
    analysis = dict(rows=rows, mean_withdrawal_test=float(np.mean([r['withdrawal_test'] for r in rows])),
        mean_binary_from_scratch_test=float(np.mean([r['binary_from_scratch_test'] for r in rows])),
        primary_passed=True, primary_pass_count=4,
        median_deficit=summary['arms'][0]['median_deficit_against_FULL'],
        counterfactual_feedback_needed_throughout_training_refuted_in_this_model=True,
        autonomous_binary_formation_from_scratch_demonstrated=False,
        payoff_entries_are_not_Shannon_information_or_physical_query_cost=True,
        new_independent_roots=0, N2=0, N3=0, CT2_historical=61, new_branch_score=None)
    out.write_text(json.dumps(analysis, indent=2), encoding='utf-8')
    colors = dict(FULL='#1769aa', WITHDRAW='#b44e18', BANDIT='#555555')
    labels = dict(FULL='FULL continuo', WITHDRAW='FULL inicial → BANDIT', BANDIT='BANDIT desde cero')
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.7), gridspec_kw={'width_ratios': [1.2, 1.2, 1]})
    for ax, field, title in zip(axes[:2], ['train_joint_greedy', 'test_joint_greedy'],
                               ['Memorización conjunta', 'Generalización conjunta']):
        for family in ['FULL', 'WITHDRAW', 'BANDIT']:
            maps = [{r['step']: r[field] for r in history} for history in curves[family]]
            common = sorted(set.intersection(*(set(d) for d in maps)))
            values = np.array([[d[t] for t in common] for d in maps])
            ax.plot(common, values.mean(0), color=colors[family], label=labels[family], lw=2)
            ax.fill_between(common, values.min(0), values.max(0), color=colors[family], alpha=.12)
        ax.axvspan(1100, 1200, color='black', alpha=.16)
        ax.set(xlabel='Actualizaciones totales', ylabel='Precisión codiciosa', title=title, ylim=(-.025, 1.04))
        ax.grid(alpha=.18)
    for family, key in [('FULL', 'full_test'), ('WITHDRAW', 'withdrawal_test'), ('BANDIT', 'binary_from_scratch_test')]:
        axes[2].plot(range(1, 5), [r[key] for r in rows], 'o-', color=colors[family], label=labels[family], lw=1.5)
    axes[2].set(title='Test final: cuatro historias pareadas', xlabel='Bloque parental', ylabel='Precisión conjunta',
                xticks=range(1, 5), ylim=(-.025, 1.04))
    axes[2].grid(alpha=.18)
    axes[0].legend(fontsize=8, loc='lower right')
    fig.suptitle('V195 neural: el apoyo contrafactual se retira antes de generalizar', fontsize=14)
    fig.text(.5, .01, 'Bandas: mínimo–máximo de cuatro raíces reutilizadas; no intervalos de confianza. Corte elegido solo con entrenamiento.',
             ha='center', fontsize=9)
    fig.tight_layout(rect=(0, .035, 1, .94))
    fig.savefig(R/'FIG_V195_WITHDRAW_COUNTERFACTUAL.png', dpi=180)
    plt.close(fig)
    table = '\n'.join(f"|{r['seed']}|{r['cut']}|{r['full_test']:.4f}|{r['binary_from_scratch_test']:.4f}|{r['withdrawal_test']:.4f}|{r['withdrawal_t_gen']}|" for r in rows)
    report = f'''# V195 neural: un apoyo informativo transitorio basta después de memorizar

15/11/2026. Experimento `WITHDRAW_COUNTERFACTUAL`, distinto de V195 de votación privada. Terminado, auditado, cuatro historias parentales reutilizadas. El objetivo científico global sigue abierto. CT2 histórico61sin cambios, rama neuronal sin puntuación, N2=N3=0.

## Resultado y contraste decisivo

Retirar las31recompensas contrafactuales después de la primera memorización permite seguir generalizando con pagos realizados solamente. Ambos agentes conservan aprendizaje y momentos AdamW. El punto final60000alcanza train conjunto1en4/4y test medio{analysis['mean_withdrawal_test']:.8f}. Pasa el criterio registrado:4/4con train>=.99/test>=.95y mediana del déficit frente a FULL {analysis['median_deficit']:.8f}<=.02. Los dos controles condicionales de compañero congelado se cancelan como NO EJECUTADOS, según protocolo.

| Semilla parental | Corte FULL→BANDIT | FULL continuo | BANDIT desde cero | Apoyo transitorio | Primer test>=.95 sostenido |
|---:|---:|---:|---:|---:|---:|
{table}

El último campo exige cinco evaluaciones consecutivas cada100pasos. No se utiliza para escoger el resultado principal. La última columna de precisión corresponde al punto final, no al máximo de la curva. El test usa productos cartesianos de577entradas locales retenidas por agente. No es un test formado solo con combinaciones nuevas de entradas locales vistas.

![Retirada del feedback contrafactual](FIG_V195_WITHDRAW_COUNTERFACTUAL.png)

## Qué cambia en la explicación

V192 FULL privado aprendía convenciones compatibles y después generalizaba. V193 conservaba la generalización local al congelar un compañero, incluso con igualdad bit a bit de los estados activos frente a la continuación conjunta. V194 demostraba capacidad del estimador binario frente a compañeros correctos suministrados. Faltaba retirar la información privilegiada de ambos aprendices reales sin reiniciar su historia.

V195 refuta, en este modelo y desde estos padres, la necesidad de mantener FULL durante toda la fase tardía. La dificultad de BANDIT desde cero no se extiende a BANDIT después de una formación asistida. No prueba que cualquier corte temprano funcione, ni qué parte exacta de los primeros1100–1200pasos resulta indispensable. Tampoco prueba necesidad de coadaptación: las políticas parentales ya memorizan las entradas de entrenamiento, por lo que sus compañeros proporcionan un problema local informativo bajo un desfase aprendido. No es una nueva capacidad colectiva demostrada por una curva conjunta.

Los aprendices reciben exclusivamente su pago realizado después del corte. El mundo conserva la función de pago programada; no construye una tabla contrafactual en esa fase. Las reglas, los intereses comunes, los grupos, la arquitectura y el apoyo inicial siguen suministrados externamente. La retirada posterior no convierte la formación en una institución inventada ni en cooperación surgida desde cero bajo información binaria.

## Coste y comparación justa

La arquitectura, epsilon.1, AdamW.001, weight_decay1, betas(.9,.98), datos y presupuesto total son los originales. Se conservan pesos, momentos y estados aleatorios. Los cortes1100requieren100pasos BANDIT registrados para alinear el reloj batch4a1200; las copias técnicas de ese prefijo no son semillas científicas.

Contando entradas de pago reveladas por entrada local de entrenamiento, FULL continuo usa1.860.000y la retirada usa93.000o96.000. Es una reducción contable del94.84–95.00%. No son bits de Shannon ni coste físico de consultas: la tabla one-hot puede codificarse con una etiqueta y el simulador suministra ese vector de forma privilegiada. Esta cifra no establece eficiencia informacional universal. Tampoco iguala las historias tempranas de FULL y BANDIT desde cero.

## Auditoría y originalidad

Registro remoto anterior a entrenar: `7d519eb122a99108955f3f5b105e19e1da998c82`, con20archivos HTTP comparados byte a byte y seis padres binarios fijados por hash. El replay histórico previo5000→10000coincidió bit a bit en pesos, momentos y RNG;408pagos de fixtures coincidieron con enumeración. Son pruebas técnicas, no nuevas réplicas científicas.

El forward NumPy separado y la enumeración cartesiana final verifican48métricas con error máximo{audit['max_error']:.3g}. Comprueban también conservación de padres no alineados, relojes del optimizador, consumo aleatorio, criterios y cancelación de controles. Cuatro raíces reutilizadas siguen siendo cuatro raíces; no se reclama confirmación independiente.

La información privilegiada disponible durante aprendizaje tiene antecedentes sólidos: [Vapnik e Izmailov, JMLR2015](https://www.jmlr.org/papers/v16/vapnik15b.html). Ese trabajo estudia mecanismos distintos, no reproduce este experimento. Impide presentar la idea general de ayuda informativa transitoria como nueva. La relación entre grokking y adaptación también tiene antecedentes: [Lyle y colaboradores, PMLR2026](https://proceedings.mlr.press/v330/lyle26a.html). Sus algoritmos no se ejecutan aquí. Se consultaron metadatos/resúmenes de los primeros y las secciones principales del segundo en la campaña anterior; no se afirma una lectura integral de todos sus apéndices.

## Evaluación y continuidad

Este control resuelve una dependencia causal, no el déficit de originalidad2/3. No se modifica la evaluación canónica ni se concede un nuevo1/3por una semilla o una auditoría. La referencia siguiente corresponde a la rama histórica, no puntúa esta línea.

![CT2 histórico, sin incremento](FIG_CT2_V175_V180.png)

La línea paralela de votación V194–V196 conserva sus propios protocolos y resultados: en ella retirar pulsos de exploración conjunta sí deteriora políticas aprendidas durante adaptación. No son réplicas de este juego. Antes de combinar sus conclusiones se debe comprobar la estabilidad privada y la exactitud de la evaluación de políticas, incluyendo cómo se resuelven empates numéricos. La prioridad es resolver esa incertidumbre y contrastar mecanismos fuertes, sin acumular arquitecturas por acumular experimentos.
'''
    (R/'INFORME_V195_WITHDRAW_COUNTERFACTUAL_20261115.md').write_text(report, encoding='utf-8')
    chapter = report.replace('](FIG_', '](../results/FIG_')
    (B/'docs/TFM_CAPITULO_RETIRADA_FEEDBACK_V195.md').write_text(chapter, encoding='utf-8')
    previous = B/'docs/TFM_MANUSCRITO_TRABAJO_V194.md'
    manuscript = previous.read_text(encoding='utf-8').replace('ampliado hasta V194', 'ampliado hasta V195 neural', 1)
    manuscript = manuscript.replace('**Palabras clave:**',
        'Un control posterior retira el feedback contrafactual en la primera memorización y conserva generalización conjunta con pagos binarios en cuatro historias. El apoyo inicial continúa siendo externo y no se acredita institución aprendida ni originalidad2/3.\n\n**Palabras clave:**', 1)
    target = B/'docs/TFM_MANUSCRITO_TRABAJO_V195.md'
    assert not target.exists()
    target.write_text(manuscript+'\n\n'+chapter, encoding='utf-8')
    ledger = dict(experiment='V195 neural WITHDRAW_COUNTERFACTUAL', branch='dual_neural_private_feedback',
        A='Continual counterfactual support versus transient support after memorization',
        B='V192 failure from scratch; V193 freeze and V194 oracle capability do not test withdrawal',
        C='Preserve exact parental state; change feedback only after training-selected cuts',
        D='Four reused roots, matched 60000 total updates, no test-selected rescue',
        E='Frozen protocol and code published before intervention prefixes',
        F='Technical replay, direct payoffs, NumPy forward and Cartesian evaluation',
        G='Final train>=.99/test>=.95 in>=3/4 and median FULL deficit<=.02',
        H=dict(criterion_passed=True, roots_passed=4, mean_test=analysis['mean_withdrawal_test']),
        I='Ongoing FULL necessity refuted for this task and these histories; initial support remains imposed',
        J='Audit stability and independent incentives before a new institutional mechanism',
        DRIFT_distance='D0', unique_new_N1_awarded=False, N2=0, N3=0,
        CT2_historical=61, new_branch_score=None, canonical_progress_file_edited=False,
        parent_manuscript_sha256=hashlib.sha256(previous.read_bytes()).hexdigest(),
        manuscript_sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    (R/'V195_WITHDRAW_AB_LEDGER.json').write_text(json.dumps(ledger, indent=2), encoding='utf-8')
    (B/'handoff_codex/ESTADO_20261115_V195_WITHDRAW.md').write_text(
        '# Estado: V195 neuronal completado\n\n'+
        f"Retirada de FULL después de memorizar pasa4/4, test medio{analysis['mean_withdrawal_test']:.8f}, train1. NumPy48checks sin fallos. "
        'Controles congelados cancelados según protocolo. Mismas cuatro raíces, no confirmación independiente. N2=N3=0; CT2 histórico61sin editar. '
        'Leer INFORME_V195_WITHDRAW_COUNTERFACTUAL_20261115.md y el manuscrito nuevo V195. Archivos anteriores no se sobrescriben. '
        'La línea paralela V194–V196 de votación se desambigua por sus nombres; requiere auditar la ley de desempates usada por su evaluador antes de nuevas conclusiones. '
        'El objetivo científico global permanece activo. No quedan procesos V195 en entrenamiento.\n', encoding='utf-8')
    print(json.dumps(dict(**analysis, manuscript_sha256=ledger['manuscript_sha256']), indent=2), flush=True)


if __name__ == '__main__':
    main()
