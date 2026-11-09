"""Regression test: PyTorch optimizer load must not alias original stored state.
This test records unsafe sharing in the direct-load case and verifies that
deepcopy before load prevents cross-lesion state contamination.
"""
import torch,copy
from pathlib import Path
from parity_v10 import MLP
ROOT=Path(__file__).resolve().parent
p=torch.load(ROOT/"v15_optimizer_states"/"seed11_prior1e-05"/"ck_010000_with_optimizer.pt",
             map_location="cpu",weights_only=False)
def count_alias(use_copy):
 model=MLP(300)
 model.load_state_dict(p["model"])
 opt=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=0.)
 supplied=copy.deepcopy(p["optimizer"]) if use_copy else p["optimizer"]
 opt.load_state_dict(supplied)
 count=0
 for k,(_,state) in zip(p["optimizer"]["state"].keys(),opt.state.items()):
  for name,v in p["optimizer"]["state"][k].items():
   if isinstance(v,torch.Tensor) and v.data_ptr()==state[name].data_ptr():
    count+=1
 return count
unsafe=count_alias(False)
safe=count_alias(True)
print("V15_OPTIMIZER_ALIAS_REGRESSION unsafe_shared_tensors=",unsafe,
      "independent_shared_tensors=",safe,flush=True)
assert unsafe>0,"Unexpectedly no alias in direct load; record version difference"
assert safe==0,"deepcopy failed to isolate original optimizer state"
print("PASS: V15 repair will use deepcopy before every optimizer state load",flush=True)
