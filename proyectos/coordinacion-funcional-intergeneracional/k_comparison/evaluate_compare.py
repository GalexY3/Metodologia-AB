"""Post-hoc development evaluation of frozen k2/k4 policies; not a sealed test."""
from pathlib import Path
import json,torch
from dataclasses import asdict
from village import Config,IndividualRNN,evaluate,atomic_json,ROOT
torch.set_num_threads(3)
v9=ROOT.parent/"v9_village"
models=[]
for k in (2,4):
    for seed in (1411,2522,3533):
        if k==2:
            run=ROOT/"runs"/f"k2_n36_d5_seed{seed}"
        else:
            run=v9/"runs"/f"pilot_d5_c0_seed{seed}"
        models.append((k,run))
for k in (2,4):
    if k==2:
        run=ROOT/"runs"/"k2_n324_continue240_seed1411"
    else:
        run=ROOT/"runs"/"k4_n324_continue240_seed1411"
    models.append((k,run))
records=[]
for k,run in models:
    cfgdict=json.loads((run/"config.json").read_text(encoding="utf-8"))["config"]
    cfgdict["k"]=k
    cfg=Config(**cfgdict)
    st=torch.load(run/"latest.pt",map_location="cpu",weights_only=False)
    torch.manual_seed(cfg.seed)
    model=IndividualRNN(cfg.n,cfg.hidden)
    model.load_state_dict(st["model"]);model.eval()
    e={}
    for mode in ("stochastic","greedy"):
        e[mode]=[]
        for seed in (660003,760007):
            result=evaluate(model,cfg,seed=seed,batch=96,horizon=48,
                            record=False,greedy=(mode=="greedy"))
            e[mode].append(result["final"])
    records.append(dict(k=k,n=cfg.n,run=run.name,update=st["update"],results=e))
    print("EVAL",k,cfg.n,run.name,
          "food",[(mode,round(sum(r["food_mean"] for r in rr)/len(rr),4),
                   "D",round(sum(r["Dk"] for r in rr)/len(rr),4),
                   "exact",sum(r["exact"] for r in rr)) for mode,rr in e.items()],
          flush=True)
baselines=[]
for k in (2,4):
    for n in (36,324):
        cfg=Config(n=n,k=k,degree=5)
        for mode in ("random","frozen","imitate"):
            rows=[]
            for seed in (660003,760007):
                result=evaluate(None,cfg,seed=seed,batch=96,horizon=48,
                                baseline=mode,record=False)
                rows.append(result["final"])
            summary=dict(k=k,n=n,baseline=mode,results=rows)
            baselines.append(summary)
            print("BASELINE",k,n,mode,round(sum(r["food_mean"] for r in rows)/2,4),flush=True)
atomic_json(ROOT/"COMPARACION_POSTHOC.json",dict(
    kind="EXPLORATORY_POSTHOC_NOT_SEALED",seeds=[660003,760007],
    worlds_per_seed=96,horizon=48,trained=records,baselines=baselines))
