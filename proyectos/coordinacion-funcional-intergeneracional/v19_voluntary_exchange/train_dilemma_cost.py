"""Controlled cost-and-discount sweep. No shared collective reward."""
import argparse,dataclasses,sys
import train,public_goods_dilemma
p=argparse.ArgumentParser(add_help=False)
p.add_argument('--donor-cost',type=float,default=.03)
p.add_argument('--discount',type=float,default=.97)
args,remaining=p.parse_known_args()
assert 0<args.donor_cost<=.2
assert 0<args.discount<=1.
sys.argv=[sys.argv[0]]+remaining
base=train.Config
def config_cost(**kw):
    return dataclasses.replace(base(**kw),cost=args.donor_cost,gamma=args.discount)
train.Config=config_cost
train.rollout=public_goods_dilemma.rollout
if __name__=='__main__':train.main()
