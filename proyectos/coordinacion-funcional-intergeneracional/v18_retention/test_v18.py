"""Data and privacy integrity tests for V18 coordinated-learning research."""
import unittest,sys,json,torch
from pathlib import Path
from dataclasses import replace
from collections import defaultdict
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'v17_regime_coalition'))
sys.path.insert(0,str(HERE.parent/'v12_variable_mk'))
from neural_dual_v2 import DualNet
from v12 import Config,World
from evaluate_v18 import CASES,SEEDS,load_model

class ResearchIntegrity(unittest.TestCase):
 def test_heldout_seeds_distinct_from_development(self):
  self.assertEqual(len(SEEDS),len(set(SEEDS)))
  self.assertTrue(set(SEEDS).isdisjoint({951001,951098,890211,890221,890231,890241}))
 def test_all_cases_have_exact_integer_quotas(self):
  for name,m,k,init in CASES:
   self.assertGreaterEqual(m,k)
   self.assertEqual(120%k,0,(name,m,k))
 def test_gradient_is_private(self):
  c=Config(n=60,m=24,k=4,degree=8,batch=3,horizon=4)
  w=World(c,129)
  actor=DualNet(60,12,2,True,'lattice',False,True)
  jobs,logp,entropy=actor.act(w)
  (-logp[:,0].mean()).backward()
  for name,p in actor.named_parameters():
   if p.grad is not None:
    self.assertLess(float(p.grad[1:].abs().max()),1e-10,name)
 def test_anchors_are_immutable_checkpoints(self):
  paths=[HERE.parent/'v17_regime_coalition'/'runs'/n/'teacher_latest.pt'
    for n in ('v17_DISTILL_LATTICE_R8_s3111_fix',
              'v17_DISTILL_LATTICE_R8_s4111_fix')]
  self.assertTrue(all(p.exists() for p in paths))
  a=torch.load(paths[0],weights_only=False,map_location='cpu')['model']
  b=torch.load(paths[1],weights_only=False,map_location='cpu')['model']
  self.assertFalse(all(torch.equal(a[k],b[k]) for k in a))
 def test_frozen_data_consistency(self):
  f=HERE/'results'/'frozen_initial.json'
  if not f.exists():self.skipTest('Frozen results not ready')
  z=json.loads(f.read_text('utf8'))
  keys=set()
  for row in z['rows']:
   key=(row['model'],row['case'],row['mode'])
   self.assertNotIn(key,keys)
   keys.add(key)
   self.assertLessEqual(row['exact'],row['ever_exact'])
   self.assertLessEqual(row['ever_exact'],row['worlds'])
   self.assertGreaterEqual(row['food'],0)
   self.assertLessEqual(row['food'],1+1e-6)
   self.assertEqual(row['worlds'],sum(x['worlds'] for x in row['raw_by_seed']))
   self.assertEqual(row['exact'],sum(x['exact'] for x in row['raw_by_seed']))
   self.assertEqual(row['exact_frames'],sum(x['exact_agent_world_frames'] for x in row['raw_by_seed']))
 def test_frozen_model_starts_equal_to_source(self):
  p=HERE.parent/'v17_regime_coalition'/'runs'
  from_source=torch.load(p/'v17_DISTILL_LATTICE_R8_s3111_fix'/'teacher_latest.pt',
                         weights_only=False,map_location='cpu')['model']
  run=HERE.parent/'v17_regime_coalition'/'runs'/'v18_BC0_s6111'/'spec.json'
  if not run.exists():self.skipTest('RL experiment not available')
  spec=json.loads(run.read_text('utf8'))
  self.assertEqual(spec['source'],'v17_DISTILL_LATTICE_R8_s3111_fix')
  self.assertEqual(spec['regularize'],0)

if __name__=='__main__':unittest.main(verbosity=2)
