"""Fail-closed release eligibility; NEVER a politician rating."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping
GATES=('rights_and_privacy_audited','first_public_at_timestamp_proven','stable_person_ids_verified','historical_group_timeline_verified','real_person_scoring_validated','multiuser_security_tested')
@dataclass(frozen=True)
class GateDecision:
 release_allowed:bool
 person_scoring_allowed:bool
 failing:tuple[str,...]
 audit_complete:bool
def decide_release(evidence:Mapping[str,object],*,trusted_receipts:Mapping[str,str]|None=None)->GateDecision:
 # trusted_receipts must originate independently from server-owned verified registry.
 # Passing it from the same caller as evidence would violate trust boundary.
 if trusted_receipts is None:return GateDecision(False,False,tuple(GATES),False)
 failing=[]
 for gate in GATES:
  item=evidence.get(gate)
  if not isinstance(item,dict) or item.get('approved') is not True or not isinstance(item.get('evidence_ref'),str) or not item['evidence_ref'].strip() or trusted_receipts.get(gate)!=item['evidence_ref']:failing.append(gate)
 ok=not failing
 return GateDecision(ok,ok,tuple(failing),ok)
CURRENT_DOCUMENTARY_EVIDENCE={
 'rights_and_privacy_audited':{'approved':False,'evidence_ref':'2026-10-26/C19_RESULT'},
 'first_public_at_timestamp_proven':{'approved':False,'evidence_ref':'2026-10-26/C15_RESULT'},
 'stable_person_ids_verified':{'approved':False,'evidence_ref':'2026-10-26/C16_RESULT'},
 'historical_group_timeline_verified':{'approved':False,'evidence_ref':'2026-10-26/C18_RESULT'},
 'real_person_scoring_validated':{'approved':False,'evidence_ref':'NONE'},
 'multiuser_security_tested':{'approved':False,'evidence_ref':'NONE'}
}
