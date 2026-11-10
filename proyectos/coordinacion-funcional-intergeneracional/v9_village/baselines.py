"""Fixed-seed baselines and untrained individual RNN for village experiments."""
import json,torch
from pathlib import Path
from dataclasses import asdict
from village import Config,IndividualRNN,evaluate,ROOT,atomic_json
def run():
    torch.set_num_threads(3)
    records=[]
    for n in (36,324):
        for degree in (2,5,8):
            cfg=Config(n=n,degree=degree,batch=32,horizon=30,hidden=12,seed=1411)
            for baseline in ("random","frozen","imitate","untrained_neural"):
                if baseline=="untrained_neural":
                    torch.manual_seed(cfg.seed)
                    actor=IndividualRNN(cfg.n,cfg.hidden).to(cfg.device)
                    b="model"
                else:
                    actor=None;b=baseline
                result=evaluate(actor,cfg,seed=450001,batch=64,horizon=48,
                                baseline=b,greedy=False,record=False)
                row=dict(n=n,degree=degree,arm=baseline,initial=result["initial"],
                         final=result["final"])
                print("BASELINE",n,degree,baseline,"food",
                      round(row["final"]["food_mean"],4),"D4",
                      round(row["final"]["D4"],4),"exact",
                      row["final"]["exact"],"hunger",
                      round(row["final"]["hunger_fraction"],3),flush=True)
                records.append(row)
    atomic_json(ROOT/"BASELINES.json",dict(kind="development_baselines",
                 seed=450001,batch=64,horizon=48,records=records))
if __name__=="__main__":run()
