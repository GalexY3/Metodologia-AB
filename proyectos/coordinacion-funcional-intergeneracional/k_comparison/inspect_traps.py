"""Read-only audit of late-stage frozen k=2/k=4 checkpoint trajectories."""
import torch,json
from dataclasses import replace
from village import Config,IndividualRNN,Village,measures
torch.set_num_threads(3)
rows=[]
for k in (2,4):
    name=f"k{k}_n324_continue240_seed1411"
    root=__import__("pathlib").Path(__file__).resolve().parent
    checkpoint=torch.load(root/"runs"/name/"latest.pt",map_location="cpu",weights_only=False)
    config=json.loads((root/"runs"/name/"config.json").read_text(encoding="utf-8"))["config"]
    cfg=Config(**config)
    model=IndividualRNN(cfg.n,cfg.hidden)
    model.load_state_dict(checkpoint["model"]);model.eval()
    for greedy in (True,False):
        ecfg=replace(cfg,batch=24,horizon=40)
        with torch.no_grad():
            env=Village(ecfg,660003)
            model.reset(24,"cpu")
            for t in range(ecfg.horizon):
                new,msg,_,_=model.choose(env.observations(),env.colors,ecfg.communication,greedy)
                env.advance(new,msg)
        food=env.food.detach()
        cnt=env.counts.detach()
        print("AUDIT",k,"GREEDY" if greedy else "STOCH",
              "meanFood",float(food.mean()),
              "topCountsFirst",sorted([int(x) for x in cnt[0].tolist()],reverse=True),
              "occupiedMean",float((cnt>0).sum(1).float().mean()),
              flush=True)
        rows.append(dict(k=k,mode="greedy" if greedy else "stochastic",
                         food=float(food.mean()),
                         first_world_counts=cnt[0].int().tolist(),
                         occupations=[int(sum(v>0 for v in x)) for x in cnt.int().tolist()],
                         first_world_food=food[0].tolist()))
(root/"AUDIT_TRAPS.json").write_text(json.dumps(rows,indent=2),encoding="utf-8")
