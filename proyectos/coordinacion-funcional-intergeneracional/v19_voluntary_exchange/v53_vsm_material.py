"""V53 material cybernetics stress test — explicit resource conservation.

This tests COSTED, LIMITED regulatory proxies inspired by Beer/Ashby.
It DOES NOT instantiate or test necessity/sufficiency of the full VSM.
The S1 material economy is the fully cooperative, balanced four-role
upper-bound of V25: b+.55 coverage+.25 complete-.04 gifts.
"""
from __future__ import annotations
import argparse,hashlib,json,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
N=48;TEAMS=12;K=4;T=96;SUBSISTENCE=.75;INITIAL=1.20;CAPACITY=2.20
B=.20;C=.04;V=.55;FULL=.25
TRANSFER_LOSS=.05
SEEDS=(999101,999107,999109,999121,999131,999137)
ENVIRONMENTS={
 "QUIET":dict(local_p=0.,local_length=4,global_p=0.,global_length=4),
 "PATCHY":dict(local_p=.09,local_length=4,global_p=0.,global_length=4),
 "SYSTEMIC":dict(local_p=0.,local_length=4,global_p=.11,global_length=5),
 "HEAVY":dict(local_p=.16,local_length=5,global_p=.035,global_length=4)}
GOVERNANCE={
 "NONE":dict(local=False,global_help=False,forecast=False,placebo=False,policy=False),
 "LOCAL":dict(local=True,global_help=False,forecast=False,placebo=False,policy=False),
 "GLOBAL":dict(local=False,global_help=True,forecast=False,placebo=False,policy=False),
 "LOCAL_GLOBAL":dict(local=True,global_help=True,forecast=False,placebo=False,policy=False),
 "FORECAST":dict(local=True,global_help=True,forecast=True,placebo=False,policy=False),
 "PLACEBO":dict(local=True,global_help=True,forecast=True,placebo=True,policy=False),
 "POLICY":dict(local=True,global_help=True,forecast=False,placebo=False,policy=True),
 "FULL_PROXY":dict(local=True,global_help=True,forecast=True,placebo=False,policy=True)}
FEES=dict(local=.004,global_help=.008,forecast=.008,policy=.003)

def shocks(seed,worlds,scenario):
 """All sequences precomputed independently of regulation and outcomes."""
 assert scenario in ENVIRONMENTS
 c=ENVIRONMENTS[scenario]
 rng=np.random.default_rng(seed*27011+532)
 outages=np.zeros((T,worlds,TEAMS,K),dtype=bool)
 remains=np.zeros((worlds,TEAMS,K),dtype=np.int16)
 for t in range(T):
  remains=np.maximum(remains-1,0)
  if c["local_p"]:
   occurrences=rng.random((worlds,TEAMS))<c["local_p"]
   chosen=rng.integers(0,K,(worlds,TEAMS))
   w,g=np.nonzero(occurrences)
   remains[w,g,chosen[w,g]]=np.maximum(remains[w,g,chosen[w,g]],c["local_length"])
  if c["global_p"]:
   systemic=rng.random(worlds)<c["global_p"]
   chosen=rng.integers(0,K,(worlds,TEAMS))
   w=np.flatnonzero(systemic)
   if len(w):
    g=np.broadcast_to(np.arange(TEAMS),(len(w),TEAMS)).ravel()
    ww=np.repeat(w,TEAMS)
    role=chosen[ww,g]
    remains[ww,g,role]=np.maximum(remains[ww,g,role],c["global_length"])
  outages[t]=remains>0
 return outages

def material_food(alive,outage):
 """Four distinct occupations guaranteed; absent agents send nothing.

 Each operational person gifts each living teammate once and pays for it.
 One temporarily disabled worker consumes, but cannot produce/send.
 """
 assert alive.shape==outage.shape and alive.shape[-2:]==(TEAMS,K)
 operating=alive&(~outage)
 production=operating.sum(axis=-1,keepdims=True)
 received=production-operating
 consumers=alive.astype(np.float64)
 sent=operating*(alive.sum(-1,keepdims=True)-1)
 gross=consumers*(B+V*received/3+FULL*(received==3))-C*sent
 return gross,received

def rescue_local(balance,alive):
 """Transfer only if deficits can be fully rescued, with conservation."""
 b=balance.copy()
 deficits=np.maximum(-b,0)*alive
 needs=deficits.sum(axis=2)
 supply=np.maximum(b-.05,0)*alive
 available=supply.sum(axis=2)
 viable=(needs>1e-8)&(available*(1-TRANSFER_LOSS)>needs+1e-6)
 send_amount=np.where(viable,needs/(1-TRANSFER_LOSS)+1e-7,0.)
 send=np.divide(supply,available[:,:,None],
   out=np.zeros_like(supply),where=available[:,:,None]>0)*send_amount[:,:,None]
 received=np.divide(deficits,needs[:,:,None],
   out=np.zeros_like(deficits),where=needs[:,:,None]>0)*(
   send_amount*(1-TRANSFER_LOSS))[:,:,None]
 b=b-send+received
 lost=float(send.sum())*TRANSFER_LOSS
 assert np.all(send>=-1e-10)
 return b,lost,float(send.sum())

def schedule_global(stock,alive,current_shock,future_shock,gov):
 """Time-delayed shipment; horizon one. Forecast is optional and costly.

 Needs target from information available to the regulator. No future foods
 may arrive before the next step; all shipments debit donor stock NOW.
 """
 W=stock.shape[0]
 alive_count=alive.sum(-1)
 safe_n=np.maximum(alive_count,1)
 team_avg=stock.sum(-1)/safe_n
 risk=(future_shock if gov["forecast"] else current_shock).sum(-1)
 if gov["forecast"] and gov["placebo"]:
  risk=np.roll(risk,shift=1,axis=1)
 # A costly threshold shared across teams: a limited S5-like risk rule.
 if gov["policy"]:
  observed=float(current_shock.mean())
  sender_min=1.1+.30*min(1.,4.*observed)
  need_target=.65+.40*min(1.,4.*observed)+.50*risk
 else:
  sender_min=1.20
  need_target=.67+.52*risk
 needs=np.maximum(need_target-team_avg,0)*alive_count
 supply=np.maximum(team_avg-sender_min,0)*alive_count
 total_need=needs.sum(1)
 total_supply=supply.sum(1)
 volume=np.minimum(total_need,total_supply)
 # Maximum physically transportable per team in one round.
 donors=(np.divide(supply,total_supply[:,None],
  out=np.zeros_like(supply),where=total_supply[:,None]>1e-12)
  *volume[:,None])
 recipients=(np.divide(needs,total_need[:,None],
  out=np.zeros_like(needs),where=total_need[:,None]>1e-12)
  *volume[:,None]*(1-TRANSFER_LOSS))
 b=stock.copy()
 # Donors pay in proportion to actually stored, nonnegative food.
 # Equal debits would illegitimately force a poor group member below zero.
 available_stored=stock.sum(axis=2,keepdims=True)
 debit=np.divide(stock,available_stored,
   out=np.zeros_like(stock),where=available_stored>1e-12)*donors[:,:,None]
 b-=debit
 assert np.all(b[alive]>=-1e-8),"cannot send unavailable stock"
 return b,recipients,float(donors.sum())*TRANSFER_LOSS,float(donors.sum())

def simulate(seed,worlds,scenario,mechanism):
 """Closed material stocks and starvation deaths, paired exogenous shocks."""
 assert mechanism in GOVERNANCE
 gov=GOVERNANCE[mechanism]
 outage=shocks(seed,worlds,scenario)
 alive=np.ones((worlds,TEAMS,K),dtype=bool)
 stock=np.full((worlds,TEAMS,K),INITIAL,dtype=np.float64)
 pending=np.zeros((worlds,TEAMS),dtype=np.float64)
 fee=(FEES["local"]*gov["local"]+
  FEES["global_help"]*gov["global_help"]+
  FEES["forecast"]*gov["forecast"]+
  FEES["policy"]*gov["policy"])
 accumulated=dict(raw=0.,admin=0.,transfer_losses=0.,
  transfers=0.,net=0.,consumed=0.,spilled=0.,total_life=0.)
 histories=[]
 for t in range(T):
  life_before=int(alive.sum())
  if pending.any():
   n=np.maximum(alive.sum(2),1)
   stock+=(pending/n*1.)[:,:,None]*alive
   pending.fill(0.)
  if life_before==0:
   histories.append(dict(t=t,alive=0))
   continue
  food,received=material_food(alive,outage[t])
  gross=float(food.sum())
  admin=fee*life_before
  before=stock+food-SUBSISTENCE*alive-fee*alive
  lost=0.;transfer_volume=0.
  if gov["local"]:
   before,localloss,localvolume=rescue_local(before,alive)
   lost+=localloss;transfer_volume+=localvolume
  deaths=alive&(before< -1e-8)
  alive=alive&~deaths
  before=np.where(alive,np.maximum(before,0),0.)
  if gov["global_help"] and t<T-1 and alive.any():
   future=outage[t+1]
   before,pend,ship_loss,ship_volume=schedule_global(before,alive,
      outage[t],future,gov)
   pending+=pend
   lost+=ship_loss;transfer_volume+=ship_volume
  # finite storage can spill food, but no storage can create calories.
  spilling=np.maximum(before-CAPACITY,0.)
  spilled=float(spilling.sum())
  stock=np.clip(before,0,CAPACITY)
  accumulated["raw"]+=gross
  accumulated["admin"]+=admin
  accumulated["transfer_losses"]+=lost
  accumulated["transfers"]+=transfer_volume
  accumulated["net"]+=gross-admin-lost
  accumulated["consumed"]+=SUBSISTENCE*life_before
  accumulated["spilled"]+=spilled
  accumulated["total_life"]+=life_before
  histories.append(dict(t=t,alive=int(alive.sum()),
    operational=int((alive&(~outage[t])).sum())))
 # Arrivals sent in last actionable step not physically counted as consumption.
 # We stop shipments before the last step, so pending resources arriving at T
 # are recorded in escrow and not counted as additional consumable stock.
 last_alive=alive.sum(axis=(1,2))
 teams_complete=alive.all(axis=2).sum(axis=1)
 return dict(seed=seed,scenario=scenario,mechanism=mechanism,worlds=worlds,
  survival=float(last_alive.mean()/N),
  all_alive_fraction=float((last_alive==N).mean()),
  viable_teams=float(teams_complete.mean()/TEAMS),
  mean_net_food_per_living=accumulated["net"]/max(1.,accumulated["total_life"]),
  mean_gross_food_per_living=accumulated["raw"]/max(1.,accumulated["total_life"]),
  admin_per_living=accumulated["admin"]/max(1.,accumulated["total_life"]),
  transfer_loss_per_living=accumulated["transfer_losses"]/max(1.,accumulated["total_life"]),
  transfers_per_living=accumulated["transfers"]/max(1.,accumulated["total_life"]),
  total_spillage=accumulated["spilled"],total_alive_agent_rounds=accumulated["total_life"],
  end_alive_worlds=(last_alive/N).tolist(),
  end_viable_teams_worlds=(teams_complete/TEAMS).tolist(),
  pending_food_at_horizon=float(pending.sum()),
  last_live_headcount=int(last_alive.sum()))

def run(ready,worlds=128):
 out=ROOT/"results";out.mkdir(exist_ok=True)
 records=[]
 start=time.perf_counter()
 for case in ENVIRONMENTS:
  for mechanism in GOVERNANCE:
   seeds=[]
   for seed in SEEDS:
    m=simulate(seed,worlds,case,mechanism)
    seeds.append(m)
   keys=("survival","all_alive_fraction","viable_teams",
     "mean_net_food_per_living","mean_gross_food_per_living",
     "admin_per_living","transfer_loss_per_living","transfers_per_living")
   record=dict(environment=case,mechanism=mechanism,
     n_worlds=len(SEEDS)*worlds,
     **{k:float(np.mean([p[k] for p in seeds])) for k in keys},
     by_seed=seeds)
   records.append(record)
   print("V53",case,mechanism,
    "survival",round(record["survival"],4),
    "teams",round(record["viable_teams"],4),
    "netfood",round(record["mean_net_food_per_living"],4),
    "lost",round(record["transfer_loss_per_living"],4),
    "seconds",round(time.perf_counter()-start,1),flush=True)
 assert len(records)==len(ENVIRONMENTS)*len(GOVERNANCE)==32
 payload=dict(preregister="PREREG_V53_VSM_MATERIAL.md",
  n_worlds_per_seed=worlds,environment_seeds=SEEDS,
  scenarios=ENVIRONMENTS,governance=GOVERNANCE,costs=FEES,
  t=T,n_agents=N,subsistence=SUBSISTENCE,storage_initial=INITIAL,
  storage_capacity=CAPACITY,donation_cost=C,transfer_loss=TRANSFER_LOSS,
  material_upper_bound=.88,
  no_policy_learning=True,governance_exogenous=True,
  rows=records,elapsed_seconds=time.perf_counter()-start)
 (out/"v53_material_raw.json").write_text(json.dumps(payload,indent=1),encoding="utf8")
 print("V53_FINISHED",len(records),"SCENARIOS",flush=True)
 return payload

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--worlds",type=int,default=128)
 a=ap.parse_args()
 run(True,a.worlds)
if __name__=="__main__":main()
