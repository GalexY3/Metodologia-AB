"""Social preference ablation; alpha=0.1 mixes food_i and mean food at TRAINING ONLY.

Public global food is *observed* by the actor if --observation public;
a reward's alpha is a separate treatment from what the actor can see.
All ten occupations remain symmetric. No message semantics or oracle.
"""
import sys,json
from pathlib import Path
import village, micro_agent
def main():
    cli=sys.argv[1:]
    i=cli.index("--alpha")
    alpha=float(cli[i+1]);del cli[i:i+2]
    assert 0<=alpha<=1
    if "--name" not in cli:raise ValueError("--name required")
    name=cli[cli.index("--name")+1]
    dest=Path(village.ROOT)/"runs"/name;dest.mkdir(parents=True,exist_ok=True)
    metadata={"alpha_global_reward":alpha,"reward_formula":"(1-alpha)*personal_food + alpha*mean_actual_food",
              "global_report_to_actor":"only if --observation public"}
    f=dest/"SOCIAL.json"
    if f.exists() and json.loads(f.read_text(encoding="utf8"))!=metadata:raise ValueError("Social setup mismatch")
    f.write_text(json.dumps(metadata,indent=2),encoding="utf8")
    orig=village.rollout
    def augmented(*args,**kwargs):
        out=orig(*args,**kwargs)
        if kwargs.get("with_grad",True) and out["logprobs"]:
            food=out["rewards"]
            out["rewards"]=(1-alpha)*food+alpha*food.mean(dim=2,keepdim=True)
        return out
    village.rollout=augmented
    sys.argv=[sys.argv[0]]+cli
    micro_agent.main()
if __name__=="__main__":main()
