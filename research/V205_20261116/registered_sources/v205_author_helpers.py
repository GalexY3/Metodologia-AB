"""Execute reviewed, unmodified upstream helper bodies on our small fixture.

Upstream files are local study copies, not redistributed. This is a loss
function audit, not reproduction of the authors' networks or benchmarks.
"""
from pathlib import Path
from functools import lru_cache
from types import SimpleNamespace
import ast
import hashlib
import numpy as np
import torch
from v205_two_stage_game import trajectories,state_values,sigmoid,best_responses_p

B=Path(__file__).resolve().parent
UPSTREAM=B/'literatura/ADVALIGN2025_AUDIT_20261116'
EXPECTED={'train.py':'995b645c05103957855abfe1420e80cb0ac5e3f24ed9ee399081578019348c61',
          'utils.py':'7f0e0e019e4b47aa9c7077676bb1ae950fb69d1c4a3cf06c291f5664e0657f66'}


class Config(dict):
    __getattr__=dict.__getitem__


@lru_cache(maxsize=1)
def helpers():
    namespace={'torch':torch,'Dict':dict,'TrajectoryBatch':SimpleNamespace}
    digests={}
    for filename,names in [('utils.py',['compute_gae_advantages']),
                           ('train.py',['aa_terms','aa_loss','actor_losses'])]:
        raw=(UPSTREAM/filename).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==EXPECTED[filename]
        text=raw.decode('utf-8');tree=ast.parse(text)
        for name in names:
            matches=[node for node in ast.walk(tree) if isinstance(node,ast.FunctionDef) and node.name==name]
            node=max(matches,key=lambda x:x.lineno)  # concrete actor_losses, not abstract declaration
            segment=ast.get_source_segment(text,node)
            digests[name]=dict(source_file=filename,line=node.lineno,end_line=node.end_lineno,
                sha256_source_segment=hashlib.sha256(segment.encode('utf-8')).hexdigest())
            module=ast.Module(body=[node],type_ignores=[])
            exec(compile(module,str(UPSTREAM/filename),'exec'),namespace)
    return namespace,digests


def original_helper_probe(coupling,loss_mode,proximal,normalize,lmbda,dtype_name):
    namespace,digests=helpers()
    dtype=torch.float64 if dtype_name=='float64' else torch.float32
    torch.set_default_dtype(dtype)
    gamma=.9;beta=.3;alpha=.1
    theta=torch.zeros((2,3),dtype=dtype,requires_grad=True)
    paths=list(trajectories(np.full((2,3),.5),gamma,coupling=coupling))
    rewards=[];actions=[];states=[];players=[]
    for path in paths:
        for i in range(2):
            rewards.append([*path['rewards'][i],0.])
            actions.append([*path['actions'][i],0])
            states.append(path['states']);players.append(i)
    rewards=torch.tensor(rewards,dtype=dtype);actions=torch.tensor(actions,dtype=torch.long)
    actor=SimpleNamespace(batch_size=16,num_agents=2,sum_rewards=False,
        train_cfg=Config(num_on_policy_agents=2,actor_loss_mode=loss_mode,gamma=gamma,lmbda=lmbda,
            proximal=proximal,clip_range=.2,center_rewards=False,normalize_advantages=normalize,aa_weight=beta),
        main_cfg=Config(use_full_maps=False,run_single_agent=False),
        agents=[SimpleNamespace(train=lambda:None),SimpleNamespace(train=lambda:None)])
    actor.aa_terms=lambda a:namespace['aa_terms'](actor,a)
    actor.aa_loss=lambda a,l,o:namespace['aa_loss'](actor,a,l,o)
    def get_values(*args):
        p=sigmoid(theta.detach().numpy());v=state_values(p,gamma,coupling)
        out=torch.tensor([[v[i,h[0]],v[i,h[1]],0.] for i,h in zip(players,states)],dtype=dtype)
        return out,out
    def get_logs(*args):
        p=torch.sigmoid(theta);logs=[];entropy=[]
        for row,(i,hs) in enumerate(zip(players,states)):
            xx=[];ee=[]
            for t,h in enumerate(hs):
                pp=p[i,h];a=actions[row,t]
                xx.append(torch.log(pp) if a else torch.log(1-pp))
                ee.append(-pp*torch.log(pp)-(1-pp)*torch.log(1-pp))
            logs.append(torch.stack([*xx,theta.new_zeros(())]))
            entropy.append(torch.stack([*ee,theta.new_zeros(())]))
        return torch.stack(logs),torch.stack(entropy)
    actor.get_trajectory_values=get_values;actor.get_trajectory_log_ps=get_logs
    fixture=SimpleNamespace(data=dict(obs=torch.zeros((32,3,1),dtype=dtype),rewards=rewards,actions=actions))
    loss=namespace['actor_losses'](actor,fixture,None)
    gradient=torch.autograd.grad(-loss['losses'].sum(),theta)[0].detach().numpy().astype(float)
    after=best_responses_p(sigmoid(alpha*gradient),gamma,coupling)
    torch.set_default_dtype(torch.float64)
    return dict(coupling=coupling,loss_mode=loss_mode,proximal=proximal,normalize_advantages=normalize,
        lmbda=lmbda,dtype=dtype_name,gradient=gradient.tolist(),after_step=after,
        field_changes_player1_terminal=bool(np.min(gradient[0,1:])>1e-6),
        post_step_exploitable=bool(after['max_gain']>1e-8),
        source_bodies_unmodified=True,source_functions=digests,
        upstream_commit='2065e43c0c36694965cf4476dc692512e3892dcc',
        source_file_sha256=EXPECTED,fixture='All 16 equiprobable action paths; independent tabular policies; exact critic')
