"""Exploratory clean-branch internal organization measures for V7 checkpoints."""
from pathlib import Path
import torch,math,json,statistics
from gated_v6 import GatedNet,build_data
torch.set_num_threads(4)
ROOT=Path(__file__).resolve().parent
study=json.loads((ROOT/"V7_ANALYSIS.json").read_text(encoding="utf-8"))
metrics=[]
for seed in (0,1,2):
 for wd in (1.0,2.5):
  label=f"cleanWD{wd}_noiseWD0.05_init1.0_s{seed}_train0.55"
  path=ROOT/"gated_runs"/label/"ck_022000.pt"
  ck=torch.load(path,map_location="cpu",weights_only=False)
  c=ck["config"]
  m=GatedNet(c["p"],c["dim"],c["branch_hidden"])
  m.load_state_dict(ck["model"])
  x,y,ids=build_data(c["p"],c["noise_total"],c["train_frac"],c["valid_frac"],c["split_seed"])
  with torch.no_grad():
   xi=x[ids["clean_train"]][:,:2]
   e=m.clean.emb(xi).reshape(len(xi),-1)
   h=torch.relu(m.clean.fc(e)).double()
   centered=h-h.mean(0,keepdim=True)
   singular=torch.linalg.svdvals(centered)
   pvals=singular.square()
   pvals=pvals/(pvals.sum()+1e-12)
   eff_rank=float(torch.exp(-(pvals*torch.log(pvals+1e-12)).sum()))
   participation=float(1/(pvals.square().sum()+1e-12))
   std=centered.std(0)
   normalized=centered/(std+1e-9)
   corr=normalized.T@normalized/(len(h)-1)
   mask=~torch.eye(len(corr),dtype=torch.bool)
   mean_abs_corr=float(corr[mask].abs().mean())
   act_zero=float((h==0).double().mean())
   out_norm=m.clean.out.weight.detach().double().norm(dim=0)
   contribution=(h.abs().mean(0)*out_norm).cpu()
   shares=contribution/contribution.sum()
   idx=torch.argsort(shares,descending=True)
   top15=float(shares[idx[:15]].sum());top30=float(shares[idx[:30]].sum())
   wnorm=float(torch.sqrt(sum((w.double()**2).sum() for w in m.clean.parameters())))
   info={"seed":seed,"wd":wd,"effective_rank":eff_rank,"participation_rank":participation,"mean_abs_corr":mean_abs_corr,"relu_sparsity":act_zero,"top15_importance_share":top15,"top30_importance_share":top30,"clean_weight_l2":wnorm}
   ref=next(x for x in study["by_network"] if x["seed"]==seed and x["wd"]==wd)
   info.update({"mean_damage_clean_pp":ref["mean_initial_damage_pp"],"mean_auc_clean":ref["mean_auc"]})
   metrics.append(info)
   print(json.dumps(info),flush=True)
(ROOT/"V7_MECHANISM_EXPLORATORY.json").write_text(json.dumps(metrics,indent=2),encoding="utf-8")
