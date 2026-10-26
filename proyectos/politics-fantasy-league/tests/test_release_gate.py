import unittest
from politics_fantasy.release_gate import decide_release,GATES,CURRENT_DOCUMENTARY_EVIDENCE
class ReleaseGate(unittest.TestCase):
 def test_current_six_gates_fail_closed(self):
  d=decide_release(CURRENT_DOCUMENTARY_EVIDENCE)
  self.assertFalse(d.release_allowed)
  self.assertFalse(d.person_scoring_allowed)
  self.assertEqual(d.failing,GATES)
 def test_empty_evidence_fails_closed(self):self.assertEqual(len(decide_release({}).failing),6)
 def test_malicious_bare_flags_not_accepted(self):self.assertFalse(decide_release({g:True for g in GATES}).release_allowed)
 def test_partial_bypass_denied(self):
  complete={g:{'approved':True,'evidence_ref':'audit/trace/valid'} for g in GATES}
  for one in GATES:
   sub={g:v.copy() for g,v in complete.items()};sub[one]['approved']=False
   self.assertFalse(decide_release(sub).release_allowed)
 def test_missing_receipt_rejected(self):
  d={g:{'approved':True,'evidence_ref':'audit'} for g in GATES}
  d['stable_person_ids_verified'].pop('evidence_ref')
  self.assertFalse(decide_release(d).person_scoring_allowed)
 def test_aggregate_can_be_documented_without_scoring(self):
  self.assertFalse(decide_release(CURRENT_DOCUMENTARY_EVIDENCE).person_scoring_allowed)
