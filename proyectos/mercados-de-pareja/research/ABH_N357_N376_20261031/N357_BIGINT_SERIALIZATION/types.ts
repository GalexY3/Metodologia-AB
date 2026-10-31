export type Pair = [number, number];
export type People = { genders: string[]; scopes: string[]; norm: number[]; q: number[]; age: number[] };
export type Config = { compat: 'general' | 'FM_only'; policy: 'random' | 'same_norm' | 'popular' | 'balance'; same_pref: number; private: boolean; public: boolean; hazard_mult: number };
export type Shocks = (kind: string, t: number, i: number, j: number) => number;
export type State = {
  partner: number[]; start: number[]; seen: number[]; requests_received: number[];
  approvals: number[]; private_bias: number[]; public_score: number[];
  formed: number; dissolved: number; listed: number; proposals: number; requests_accepted: number;
  sent_by_norm: number[]; received_by_norm: number[]; norm_exp: number; norm_exposure_denom: number;
  new_norm: number; completed_duration: number[];
};
export type Track = { t: number; singles: number; risk_edges: number; impressions: number; proposals: number; reciprocals: number; new_pairs: number; active_pairs: number };
export type Trace = {
  seed: number; scenario: string; t: number; stage: string; sender: number | null; receiver: number | null;
  seq?: number; schema_version?: 'TRACE_SCHEMA_1'; pre_state: unknown; observed: unknown; u?: number; p?: number;
  solver_meta?: Record<string, unknown>;
};
export type Emit = (event: Trace) => void;
export const shockNames = ['u_send', 'u_reply', 'u_hazard', 'u_expose', 'u_match'] as const;
export const base: Config = { compat: 'general', policy: 'random', same_pref: 0, private: false, public: false, hazard_mult: 1 };
export const scenarios: Record<string, Config> = {
  mixed_random: { ...base }, heterosexual_restricted: { ...base, compat: 'FM_only' },
  institutional_segregation: { ...base, policy: 'same_norm' }, explicit_norm_preference: { ...base, same_pref: 1.3 },
  popularity_ranking: { ...base, policy: 'popular' }, visibility_balancing: { ...base, policy: 'balance' },
  private_rejection_learning: { ...base, private: true }, public_rejection_signal: { ...base, public: true },
  longer_partnerships: { ...base, hazard_mult: .4 }, shorter_partnerships: { ...base, hazard_mult: 1.75 }
};
export function requireThat(ok: unknown, message: string): asserts ok { if (!ok) throw new Error(message); }
export function finite(x: number): number { requireThat(Number.isFinite(x), 'NONFINITE_NUMBER'); return x; }
export function snapshot(s: State): State { return structuredClone(s); }
