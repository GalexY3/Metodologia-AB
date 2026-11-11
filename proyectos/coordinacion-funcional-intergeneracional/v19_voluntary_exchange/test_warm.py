import unittest,torch
from targeted_gifts import C,create,PrivateGiftActor,simulate
class Warmup(unittest.TestCase):
 def test_initial_history_respects_directed_edges(self):
  c=C(n=24,k=2,degree=2,device='cpu',batch=100,warm=.7)
  w=create(c,17)
  self.assertGreater(float(w['prev_gift'].mean()),.55)
  self.assertGreater(float(w['incoming'].mean()),0)
  # Each gift can be consumed by only the recipient.
  self.assertAlmostEqual(float(w['incoming'].sum()),float(w['prev_gift'].sum()))
 def test_no_warm_preserves_original_no_history(self):
  c=C(n=24,k=2,degree=2,device='cpu',batch=10,warm=0)
  w=create(c,17)
  self.assertEqual(float(w['incoming'].sum()),0)
  self.assertEqual(float(w['prev_gift'].sum()),0)
 def test_a_prehistory_does_not_force_future_gifts(self):
  c=C(n=24,k=2,degree=2,device='cpu',batch=6,horizon=3,warm=.8)
  a=PrivateGiftActor(24,12,2)
  w=create(c,71)
  dest,gifts,_,_=a.act(c,w)
  self.assertTrue(bool((gifts>=0).all() and (gifts<=1).all()))
if __name__=='__main__':unittest.main(verbosity=2)
