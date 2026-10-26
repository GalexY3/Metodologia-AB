import unittest
from politics_fantasy.typed_refs import InstitutionalRef as R,same_institutional_record,certify_same_person,scoring_enabled
class TestTypedRefs(unittest.TestCase):
 def test_equal_record(self):
  a=R("Congreso","XV","005","408")
  self.assertTrue(same_institutional_record(a,a))
 def test_asset_interest_namespace_collision(self):
  self.assertFalse(same_institutional_record(R("Congreso","XV","005","408"),R("Congreso","XV","007","408")))
 def test_credential_asset_namespace_collision(self):
  self.assertFalse(same_institutional_record(R("Congreso","XV","credential","409"),R("Congreso","XV","005","409")))
 def test_cross_term(self):
  self.assertFalse(same_institutional_record(R("Congreso","XIV","005","408"),R("Congreso","XV","005","408")))
 def test_cross_institution(self):
  self.assertFalse(same_institutional_record(R("Senado","XV","005","408"),R("Congreso","XV","005","408")))
 def test_unsigned_fake_crosswalk_rejected(self):
  a,b=R("Congreso","XV","005","408"),R("Congreso","XV","007","409")
  self.assertFalse(certify_same_person(a,b,attested_crosswalk={"claimed":True}))
 def test_blank_field_rejected(self):
  with self.assertRaises(ValueError):R("Congreso","XV","","408")
 def test_scoring_disabled(self):
  self.assertFalse(scoring_enabled(R("Congreso","XV","005","408")))
if __name__=="__main__": unittest.main()
