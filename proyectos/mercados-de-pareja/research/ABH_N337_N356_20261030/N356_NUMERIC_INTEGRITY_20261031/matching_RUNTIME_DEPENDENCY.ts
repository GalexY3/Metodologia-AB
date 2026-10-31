import { requireThat } from './types.ts';
import type { Pair } from './types.ts';
export type Edge = { pair: Pair; weight: number };
type Choice = { cardinality: number; weight: bigint; witnesses: Pair[][] };
export type MatchingLimits = { maxStates?: number; maxComponentNodes?: number; maxWallMs?: number; maxHeapBytes?: number };

// Independent exact subset recurrence, not a port of Python/NetworkX or a greedy heuristic.
// All binary64 weights are compared as exact integer multiples of 2^-1074.
// Exponential in connected-component size. Budget exhaustion is STOP, never an approximate result.
function units(x: number): bigint {
  requireThat(Number.isFinite(x) && x >= 0, 'INVALID_MATCH_WEIGHT');
  const v = new DataView(new ArrayBuffer(8)); v.setFloat64(0, x, false);
  const bits = v.getBigUint64(0, false), exponent = Number((bits >> 52n) & 2047n), fraction = bits & ((1n << 52n) - 1n);
  return exponent === 0 ? fraction : ((1n << 52n) | fraction) << BigInt(exponent - 1);
}
export function canonical(pairs: Pair[]): Pair[] {
  return pairs.map(([i, j]): Pair => i < j ? [i, j] : [j, i]).sort((a, b) => a[0] - b[0] || a[1] - b[1]);
}
function retain(options: Choice[]): Choice[] {
  const card = Math.max(...options.map(x => x.cardinality));
  const sorted = options.filter(x => x.cardinality === card).sort((a, b) => a.weight > b.weight ? -1 : a.weight < b.weight ? 1 : 0);
  const out: Choice[] = [];
  for (const x of sorted) {
    let found = out.find(y => y.weight === x.weight);
    if (!found) { if (out.length === 2) break; found = { ...x, witnesses: [] }; out.push(found); }
    for (const witness of x.witnesses) {
      const normalized = canonical(witness), key = JSON.stringify(normalized);
      if (found.witnesses.length < 2 && !found.witnesses.some(w => JSON.stringify(w) === key)) found.witnesses.push(normalized);
    }
  }
  return out;
}
function combine(left: Choice[], right: Choice[]): Choice[] {
  return retain(left.flatMap(a => right.map(b => ({ cardinality: a.cardinality + b.cardinality, weight: a.weight + b.weight,
    witnesses: a.witnesses.flatMap(x => b.witnesses.map(y => [...x, ...y])) }))));
}
export function matching(nodes: number[], edges: Edge[], limits: number | MatchingLimits = {}) {
  const opts = typeof limits === 'number' ? { maxStates: limits } : limits;
  const maxStates = opts.maxStates ?? 1_000_000, maxComponentNodes = opts.maxComponentNodes ?? 22;
  const maxWallMs = opts.maxWallMs ?? 10_000, maxHeapBytes = opts.maxHeapBytes ?? 1_073_741_824;
  requireThat(Number.isSafeInteger(maxStates) && maxStates > 0 && Number.isSafeInteger(maxComponentNodes) && maxComponentNodes > 0 &&
    Number.isFinite(maxWallMs) && maxWallMs >= 0 && Number.isSafeInteger(maxHeapBytes) && maxHeapBytes > 0,
    'INVALID_MATCH_RESOURCE_LIMITS');
  const start = process.hrtime.bigint();
  const guard = (stage: string, states: number, component: number) => {
    if (Number(process.hrtime.bigint() - start) / 1e6 >= maxWallMs)
      throw new Error(`MATCH_RESOURCE_LIMIT:WALL:${stage}:states=${states}:component=${component}`);
    if (process.memoryUsage().heapUsed >= maxHeapBytes)
      throw new Error(`MATCH_RESOURCE_LIMIT:HEAP:${stage}:states=${states}:component=${component}`);
  };
  guard('start', 0, 0);
  requireThat(new Set(nodes).size === nodes.length && nodes.every(x => Number.isSafeInteger(x) && x >= 0), 'INVALID_MATCH_NODES');
  const weights = new Map<string, bigint>(), adjacent = new Map(nodes.map(i => [i, new Set<number>()]));
  for (const { pair: [a, b], weight } of edges) {
    requireThat(a !== b && adjacent.has(a) && adjacent.has(b), 'INVALID_MATCH_EDGE');
    const [i, j] = a < b ? [a, b] : [b, a], key = `${i},${j}`, w = units(weight);
    requireThat(!weights.has(key) || weights.get(key) === w, 'DUPLICATE_WEIGHT_CONFLICT');
    weights.set(key, w); adjacent.get(i)!.add(j); adjacent.get(j)!.add(i);
  }
  const components: number[][] = [], visited = new Set<number>();
  for (const node of nodes) if (!visited.has(node)) {
    const stack = [node], component: number[] = []; visited.add(node);
    while (stack.length) { const i = stack.pop()!; component.push(i); for (const j of adjacent.get(i)!) if (!visited.has(j)) { visited.add(j); stack.push(j); } }
    components.push(component.sort((a, b) => a - b));
  }
  let states = 0, combined: Choice[] = [{ cardinality: 0, weight: 0n, witnesses: [[]] }];
  for (const component of components) {
    if (component.length > maxComponentNodes)
      throw new Error(`MATCH_RESOURCE_LIMIT:COMPONENT:${component.length}>${maxComponentNodes}:states=${states}`);
    guard('component', states, component.length);
    const memo = new Map<bigint, Choice[]>(), bit = (a: number) => 1n << BigInt(a);
    const adjacencyMasks = component.map(i => component.reduce((mask, j, b) => adjacent.get(i)!.has(j) ? mask | bit(b) : mask, 0n));
    const solve = (mask: bigint): Choice[] => {
      if (mask === 0n) return [{ cardinality: 0, weight: 0n, witnesses: [[]] }];
      const old = memo.get(mask); if (old) return old;
      ++states;
      requireThat(states <= maxStates, `MATCH_RESOURCE_LIMIT:STATES:${states}>${maxStates}:component=${component.length}`);
      guard('search', states, component.length);
      // Re-factor disconnected residual graphs, which commonly arise when removing sparse edges.
      let remaining = mask; const pieces: bigint[] = [];
      while (remaining) {
        let frontier = remaining & -remaining, piece = 0n;
        while (frontier) {
          piece |= frontier; let next = 0n;
          for (let b = 0; b < component.length; b++) if ((frontier & bit(b)) !== 0n) next |= adjacencyMasks[b];
          frontier = next & mask & ~piece;
        }
        pieces.push(piece); remaining &= ~piece;
      }
      if (pieces.length > 1) {
        let best: Choice[] = [{ cardinality: 0, weight: 0n, witnesses: [[]] }];
        for (const piece of pieces) best = combine(best, solve(piece));
        memo.set(mask, best); return best;
      }
      let a = -1, degree = Infinity;
      for (let b = 0; b < component.length; b++) if ((mask & bit(b)) !== 0n) {
        const d = component.reduce((count, _, k) => count + Number((adjacencyMasks[b] & mask & bit(k)) !== 0n), 0);
        if (d < degree) { a = b; degree = d; }
      }
      const i = component[a], rest = mask & ~bit(a);
      const options = [...solve(rest)]; // i remains unmatched
      for (let b = 0; b < component.length; b++) if ((rest & bit(b)) !== 0n && adjacent.get(i)!.has(component[b])) {
        const j = component[b], w = weights.get(`${Math.min(i, j)},${Math.max(i, j)}`)!;
        for (const c of solve(rest & ~bit(b))) options.push({ cardinality: c.cardinality + 1, weight: c.weight + w,
          witnesses: c.witnesses.map(p => [...p, [i, j] as Pair]) });
      }
      const best = retain(options); memo.set(mask, best); return best;
    };
    const local = solve((1n << BigInt(component.length)) - 1n);
    combined = combine(combined, local);
    guard('merge', states, component.length);
  }
  const best = combined[0], unique = best.witnesses.length === 1;
  return { pairs: best.witnesses[0], cardinality: best.cardinality, unique, witnesses: best.witnesses,
    status: unique ? 'UNIQUE_OPTIMUM' : 'MATCH_TIE_DIAGNOSTIC_NOT_EXACT_PAIR_ACCEPTANCE',
    exact_weight_units: best.weight.toString(), unit: '2^-1074',
    next_distinct_weight_units: combined[1]?.weight.toString() ?? null,
    uniqueness_margin_units: unique ? (combined[1] ? (best.weight - combined[1].weight).toString() : null) : '0',
    proof: 'EXHAUSTIVE_MEMOIZED_RECURRENCE_BY_COMPONENT', states, component_sizes: components.map(c => c.length) };
}
export function candidateEdges(accepted: Pair[], eligible: boolean[][], u: (i: number, j: number) => number): Edge[] {
  const out = new Map<string, Edge>();
  for (const [a, b] of accepted) {
    const [i, j] = a < b ? [a, b] : [b, a];
    requireThat(i !== j && eligible[i]?.[j], 'INELIGIBLE_MATCH_EDGE');
    const shock = u(i, j); requireThat(Number.isFinite(shock) && shock >= 0 && shock < 1, 'INVALID_MATCH_SHOCK');
    out.set(`${i},${j}`, { pair: [i, j], weight: 1 + 1e-4 * shock });
  }
  return [...out.values()].sort((a, b) => a.pair[0] - b.pair[0] || a.pair[1] - b.pair[1]);
}
