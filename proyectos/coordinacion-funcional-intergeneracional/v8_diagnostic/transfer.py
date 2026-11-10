"""Exploratory transfer of N=324 acceptance policies trained ONLY on k=4.

Not a sealed test: k values are examined post-hoc to design later studies.
Policies are frozen during evaluation on k=2,3,4,6,9 and new world seeds.
"""
import json, hashlib
from pathlib import Path
import numpy as np
from learn_acceptance import train,trial
ROOT=Path(__file__).resolve().parent
N=324
SEED=681104
TRAIN_BATCH=48
TRAIN_EPISODES=60
TRAIN_EPOCHS=2
LR=.5
EVAL_EPOCHS=40
EVAL_WORLDS=64
rows=[]
modeldir=ROOT/"models"
modeldir.mkdir(exist_ok=True)
for rep in range(3):
    train_seed=SEED+100101*N+600000*rep
    theta,h=train(N,4,TRAIN_BATCH,TRAIN_EPISODES,TRAIN_EPOCHS,LR,train_seed)
    file=modeldir/f"acceptance_n324_k4_rep{rep}.npz"
    np.savez_compressed(file,theta=theta,training_seed=train_seed,k_train=4,
                        training_batch=TRAIN_BATCH,episodes=TRAIN_EPISODES,
                        epochs=TRAIN_EPOCHS,learning_rate=LR)
    hash=hashlib.sha256(file.read_bytes()).hexdigest()
    metrics=[]
    for k in (2,3,4,6,9):
        seed=train_seed+15_000_000+7307*k
        arms={}
        for label in ("trained","untrained","scripted"):
            policy=(theta if label=="trained" else np.zeros_like(theta)).copy()
            arms[label]=trial(N,k,EVAL_WORLDS,EVAL_EPOCHS,seed,policy,
                              mode="scripted" if label=="scripted" else "policy")
        metrics.append(dict(k=k,seed=seed,arms=arms))
        print("TRANSFER",rep,k,
            [(name,round(v["final_D"],4),v["exact"]) for name,v in arms.items()],
            flush=True)
    rows.append(dict(rep=rep,train_seed=train_seed,sha256=hash,
                     model=str(file.relative_to(ROOT)),rows=metrics))
out=dict(kind="POSTHOC_TRANSFER_DIAGNOSTIC_NOT_HOLDOUT",
         trained_for_k=4,eval_ks=[2,3,4,6,9],population=N,
         train_episodes=TRAIN_EPISODES,train_epochs=TRAIN_EPOCHS,
         lr=LR,eval_epochs=EVAL_EPOCHS,eval_worlds=EVAL_WORLDS,
         initial_train_seed=SEED,replicates=rows)
(ROOT/"RESULTS_V8_TRANSFER.json").write_text(
    json.dumps(out,indent=2,ensure_ascii=False),encoding="utf-8")
print("TRANSFER_COMPLETE")
