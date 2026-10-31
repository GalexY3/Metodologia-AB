import { requireThat, snapshot } from './types.ts';
import type { Config, People, Shocks, Emit, Pair, State, Track } from './types.ts';
import { compatibility, edges, validatePeople } from './compatibility.ts';
import { initial, hazard, dissolve } from './state.ts';
import { exposureScore, select } from './selection.ts';
import { sigmoid, utilities, feedback } from './decision.ts';
import { matching, candidateEdges } from './blossom_matching.mjs';
import type { MatchingLimits } from './matching.ts';
import { result } from './metrics.ts';
export function replay(p: People, shocks: Shocks, c: Config, seed: number, scenario: string, steps: number, k: number,
  emit: Emit = () => {}, maxMatchStates: number | MatchingLimits = 1_000_000,
  traceLimits: { maxEvents?: number; maxBytes?: number } = {}) {
  validatePeople(p); requireThat(Number.isSafeInteger(steps) && steps > 0, 'INVALID_STEPS');
  requireThat(Number.isFinite(c.same_pref) && Number.isFinite(c.hazard_mult) && c.hazard_mult >= 0, 'INVALID_CONFIG');
  requireThat(['random', 'same_norm', 'popular', 'balance'].includes(c.policy), 'INVALID_POLICY');
  const n = p.genders.length, eligible = compatibility(p, c.compat), s = initial(n), track: Track[] = [];
  const u: Shocks = (kind, t, i, j) => { const x = shocks(kind, t, i, j); requireThat(Number.isFinite(x) && x >= 0 && x < 1, 'INVALID_SHOCK'); return x; };
  let seq = 0, traceEvents = 0, traceBytes = 0;
  const maxEvents = traceLimits.maxEvents ?? 200_000, maxBytes = traceLimits.maxBytes ?? 67_108_864;
  requireThat(Number.isSafeInteger(maxEvents) && maxEvents >= 0 && Number.isSafeInteger(maxBytes) && maxBytes >= 0,
    'INVALID_TRACE_BUDGET');
  const record = (t: number, stage: string, i: number | null, j: number | null, pre: State, observed: unknown,
    shock?: number, prob?: number, solverMeta?: Record<string, unknown>) => {
    const event = { schema_version: 'TRACE_SCHEMA_1' as const, seq, seed, scenario, t, stage,
      sender: i, receiver: j, pre_state: pre, observed,
      ...(shock === undefined ? {} : { u: shock }), ...(prob === undefined ? {} : { p: prob }),
      ...(solverMeta === undefined ? {} : { solver_meta: solverMeta }) };
    const bytes = Buffer.byteLength(JSON.stringify(event)) + 1;
    if (traceEvents + 1 > maxEvents || traceBytes + bytes > maxBytes)
      throw new Error(`TRACE_RESOURCE_LIMIT:PARTIAL_STOP:events=${traceEvents}:bytes=${traceBytes}:next=${stage}`);
    emit(event); seq++; traceEvents++; traceBytes += bytes;
  };
  for (let t = 0; t < steps; t++) {
    for (let i = 0; i < n; i++) {
      const j = s.partner[i]; if (j <= i) continue;
      const pre = snapshot(s), h = hazard(p, i, j, c.hazard_mult), shock = u('u_hazard', t, i, j), did = shock < h;
      const duration = did ? dissolve(s, t, i, j) : null;
      record(t, 'dissolution', i, j, pre, { dissolve: did, duration }, shock, h);
    }
    const available = s.partner.flatMap((x, i) => x < 0 ? [i] : []), risk = edges(eligible, available).length;
    record(t, 'available', null, null, snapshot(s), { available, risk_edges: risk });
    let impressions = 0, proposals = 0; const mutual: Pair[] = [];
    for (const i of available) {
      const candidates = available.filter(j => eligible[i][j]); if (!candidates.length) continue;
      const scores = candidates.map(j => exposureScore(u('u_expose', t, i, j), c.policy, p.norm[i] === p.norm[j], p.q[j], s.seen[j]));
      const selection = select(candidates, scores, k);
      record(t, 'selection', i, null, snapshot(s), { candidates, scores, ...selection });
      requireThat(!selection.blocking, `EXPOSURE_TIE_BLOCKING:${selection.diagnostic}`);
      for (const j of selection.picks) {
        let pre = snapshot(s);
        s.listed++; s.seen[j]++; s.received_by_norm[p.norm[j]]++; s.norm_exposure_denom++; s.norm_exp += Number(p.norm[i] === p.norm[j]); impressions++;
        record(t, 'exposure', i, j, pre, { seen: s.seen[j] });
        const util = utilities(p, s, c, i, j), prob = sigmoid(util.send), shock = u('u_send', t, i, j);
        pre = snapshot(s); const proposes = shock < prob;
        if (proposes) { s.proposals++; proposals++; s.approvals[i]++; s.requests_received[j]++; s.sent_by_norm[p.norm[i]]++; }
        record(t, 'proposal', i, j, pre, { utility: util.send, proposes }, shock, prob);
        if (!proposes) continue;
        const replyP = sigmoid(util.reply), replyU = u('u_reply', t, j, i), accepted = replyU < replyP;
        pre = snapshot(s);
        if (accepted) { s.requests_accepted++; mutual.push([i, j]); }
        record(t, 'response', i, j, pre, { utility: util.reply, accepted, tensor_index: [t, j, i] }, replyU, replyP);
        if (!accepted) { pre = snapshot(s); feedback(s, c, i); record(t, 'feedback', i, j, pre, { private_bias: s.private_bias[i], public_score: s.public_score[i] }); }
      }
    }
    const graph = candidateEdges(mutual, eligible, (i, j) => u('u_match', t, i, j));
    record(t, 'matching_graph', null, null, snapshot(s), { available, accepted_directed: mutual, edges: graph });
    const optimum = matching(available, graph, maxMatchStates);
    const { pairs: chosenPairs, cardinality, ...solverMeta } = optimum;
    record(t, 'matching', null, null, snapshot(s), { pairs: chosenPairs, cardinality }, undefined, undefined, solverMeta);
    // A primal-dual equality certifies optimal value; it does NOT generally certify uniqueness.
    // We retain the selected optimal pair set and mark uniqueness as unknown in solver metadata.
    requireThat(optimum.certified_optimality, 'UNVERIFIED_MATCHING_OPTIMUM');
    const pre = snapshot(s);
    for (const [i, j] of optimum.pairs) {
      requireThat(s.partner[i] === -1 && s.partner[j] === -1 && eligible[i][j], 'INVALID_FORMATION');
      s.partner[i] = j; s.partner[j] = i; s.start[i] = s.start[j] = t; s.formed++; s.new_norm += Number(p.norm[i] === p.norm[j]);
    }
    // Formation is one canonical unordered pair set, never a causally ordered NetworkX iteration.
    record(t, 'formation', null, null, pre, { pairs: optimum.pairs });
    const row: Track = { t, singles: available.length, risk_edges: risk, impressions, proposals, reciprocals: mutual.length,
      new_pairs: optimum.cardinality, active_pairs: s.partner.filter(j => j >= 0).length / 2 };
    requireThat(s.formed - s.dissolved === row.active_pairs && row.new_pairs <= row.reciprocals && row.reciprocals <= row.proposals && row.proposals <= impressions, 'BALANCE_FAILURE');
    requireThat(s.partner.every((j, i) => j < 0 || s.partner[j] === i), 'PARTNER_ASYMMETRY');
    track.push(row); record(t, 'track', null, null, snapshot(s), { track: row, state: snapshot(s) });
  }
  return { result: result(p, s, track, eligible, seed, scenario, steps), state: s,
    censored_durations: s.partner.flatMap((j, i) => j > i ? [steps - s.start[i]] : []) };
}
