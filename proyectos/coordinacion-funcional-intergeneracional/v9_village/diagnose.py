"""Read-only exploratory verification on new worlds and communication ablation."""
import json,torch
from pathlib import Path
from dataclasses import asdict,replace
from village import Config,IndividualRNN,evaluate,ROOT,atomic_json
def main():
    torch.set_num_threads(3)
    records=[]
    for run in sorted((ROOT/"runs").glob("pilot_*")):
        if not (run/"latest.pt").exists():continue
        setup=json.loads((run/"config.json").read_text(encoding="utf-8"))
        cfg=Config(**setup["config"])
        st=torch.load(run/"latest.pt",map_location="cpu",weights_only=False)
        torch.manual_seed(cfg.seed)
        actor=IndividualRNN(cfg.n,cfg.hidden)
        actor.load_state_dict(st["model"]);actor.eval()
        modes=["stochastic","greedy"]
        if cfg.communication:modes+=["no_messages_stochastic"]
        results={}
        for mode in modes:
            testcfg=replace(cfg,communication=False) if mode=="no_messages_stochastic" else cfg
            results[mode]=[]
            for seed in (660003,760007):
                e=evaluate(actor,testcfg,seed=seed,batch=96,horizon=48,
                  greedy=mode=="greedy",record=False)
                results[mode].append(e["final"])
        row=dict(name=run.name,update=st["update"],config=asdict(cfg),evaluation=results)
        print("VERIFY",run.name,
              [(mode,round(sum(r["food_mean"] for r in rs)/len(rs),4),
                sum(r["exact"] for r in rs)) for mode,rs in results.items()],flush=True)
        records.append(row)
    atomic_json(ROOT/"DIAGNOSTICO_NUEVAS_SEMILLAS.json",dict(
        kind="POSTHOC_DEVELOPMENT_FRESH_WORLD_SEEDS_NOT_SEALED_HOLDOUT",
        seeds=[660003,760007],batch_per_seed=96,horizon=48,
        records=records,notes="Trained models frozen, personal food only. Communication ablation disables messages at test; stochastic RNG consumption changes, so direct pairwise causal comparison needs a controlled intervention."))
if __name__=="__main__":main()
