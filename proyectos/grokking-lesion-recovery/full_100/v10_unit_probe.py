"""V10B unit-level causal leave-one-out metrics and importance concentration.
Diagnostic only; the L1 treatment remains a rival explanation.
"""
from pathlib import Path
import torch,json,statistics
from parity_v10 import MLP,data,measure
torch.set_num_threads(4)
ROOT=Path(__file__).resolve().parent
res=[]
x,y,ids=data(20261109,500,1000,2000)
xv=x[ids["val"]];yv=y[ids["val"]]
for seed in range(5):
 for lam in (1e-5,.001):
  path=ROOT/"parity_runs"/f"lambda{lam:g}_seed{seed}_lr0.001_width300_nt500"/"ck_008000.pt"
  ck=torch.load(path,map_location="cpu",weights_only=False)
  net=MLP(300);net.load_state_dict(ck["model"])
  with torch.no_grad():
   h=torch.relu(net.a(xv))
   logits=net.b(h)
   base=float((logits.argmax(1)==yv).float().mean())
   w=net.b.weight.detach()
   contributions=(h.abs().mean(0)*torch.linalg.vector_norm(w,dim=0))
   mass=contributions/(contributions.sum()+1e-12)
   sorted_mass=torch.sort(mass,descending=True).values
   count_effective=float(1/(mass.square().sum()+1e-12))
   # Exact ablation of each neuron: subtract that unit's contribution.
   altered=logits[:,None,:] - h[:,:,None]*w.T[None,:,:]
   accuracy=(altered.argmax(-1)==yv[:,None]).float().mean(0)
   damage=(base-accuracy)*100.
   orig_loss=float(torch.nn.functional.cross_entropy(logits,yv))
   # Cross entropy for every ablated j; flattened before reduction
   losses=torch.nn.functional.cross_entropy(altered.reshape(-1,2),yv[:,None].expand(-1,300).reshape(-1),reduction="none").reshape(len(yv),300).mean(0)
   lossdelta=losses-orig_loss
   row={"seed":seed,"lambda":lam,"base_val":base,
        "effective_contributors":count_effective,
        "top5_contribution_share":float(sorted_mass[:5].sum()),
        "top10_contribution_share":float(sorted_mass[:10].sum()),
        "top30_contribution_share":float(sorted_mass[:30].sum()),
        "top60_contribution_share":float(sorted_mass[:60].sum()),
        "active_relu_units_>1pct_samples":int(((h>0).float().mean(0)>.01).sum()),
        "units_causing_>=1pp_accuracy_loss":int((damage>=1-1e-6).sum()),
        "units_causing_>=5pp_accuracy_loss":int((damage>=5-1e-6).sum()),
        "max_one_unit_accuracy_damage_pp":float(damage.max()),
        "mean_one_unit_accuracy_damage_pp":float(damage.mean()),
        "max_one_unit_loss_increase":float(lossdelta.max()),
        "base_val_crossentropy":orig_loss}
   res.append(row)
   print("UNIT",json.dumps(row,ensure_ascii=False),flush=True)
(ROOT/"V10_UNIT_MECHANISM.json").write_text(json.dumps(res,indent=2),encoding="utf-8")
