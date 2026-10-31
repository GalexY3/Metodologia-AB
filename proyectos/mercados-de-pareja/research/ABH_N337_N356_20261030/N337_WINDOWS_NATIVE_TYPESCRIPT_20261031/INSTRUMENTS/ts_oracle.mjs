// Independent TypeScript ESBM implementation from original local N207 package.
// No modification of its TypeScript modules. This is NOT the N237 Boost wrapper.
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { replay } from './installer_review/unpacked/windows-replica/src/engine.ts';
import { scenarios } from './installer_review/unpacked/windows-replica/src/types.ts';
const root = dirname(fileURLToPath(import.meta.url));
const seeds = [101, 211, 307, 401, 503, 601];
const names = [
  'mixed_random', 'heterosexual_restricted', 'institutional_segregation',
  'explicit_norm_preference', 'popularity_ranking', 'visibility_balancing',
  'private_rejection_learning', 'public_rejection_signal',
  'longer_partnerships', 'shorter_partnerships',
];
const dest = join(root, 'N337_TS_N207.json');
if (existsSync(dest)) throw new Error('OUTPUT_ALREADY_EXISTS_FAIL_CLOSED');
const runs = [];
for (const seed of seeds) {
  const source = JSON.parse(readFileSync(join(root, 'inputs', `seed_${seed}.json`), 'utf8'));
  for (const name of names) {
    const formation = [], firstEvents = [], matchingStatus = [];
    try {
      const out = replay(source.people,
        (kind, t, i, j) => source.shocks[kind][t][i][j],
        scenarios[name], seed, name, 6, 3,
        event => {
          if (event.stage === 'formation') formation.push(event.observed.pairs.map(([a,b]) => [Math.min(a,b),Math.max(a,b)]).sort((a,b) => a[0]-b[0] || a[1]-b[1]));
          if (event.stage === 'matching') matchingStatus.push(event.solver_meta?.status ?? null);
          if (firstEvents.length < 4) firstEvents.push({ stage: event.stage, sender: event.sender, receiver: event.receiver, seq: event.seq });
        }, { maxStates: 50000, maxComponentNodes: 8, maxWallMs: 2500, maxHeapBytes: 268435456 },
        { maxEvents: 10000, maxBytes: 8388608 });
      runs.push({ seed, scenario: name, status: 'EXECUTED', result: out.result,
        formation_pairs_by_tick: formation, matching_status: matchingStatus,
        first_events: firstEvents });
    } catch (error) {
      runs.push({ seed, scenario: name, status: 'EXECUTED_EXCEPTION', error: String(error),
        formation_pairs_by_tick: formation, matching_status: matchingStatus, first_events: firstEvents });
    }
  }
}
writeFileSync(dest, JSON.stringify({ schema: 'N337_TS_N207_SHARED_INPUTS', runs }, null, 2) + '\n', { flag: 'wx' });
console.log('TS_INDEPENDENT_EXECUTED', runs.length, 'exceptions', runs.filter(x=>x.status!=='EXECUTED').length);
