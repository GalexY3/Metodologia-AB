"""Explicit social prehistory (not policy training or enforced reciprocity).

A fraction of neighbors happened to exchange a directed gift in the preceding
period. A neural policy can observe the consequences and decide freely now.
Compare with identical networks begun with zero exchange history.
"""
import argparse,dataclasses,sys,json
import train_targeted as trainer
p=argparse.ArgumentParser(add_help=False)
p.add_argument('--warm',type=float,default=.5)
opts,argv=p.parse_known_args()
assert 0<opts.warm<=1
sys.argv=[sys.argv[0]]+argv
c=trainer.C
def make(**kw):return dataclasses.replace(c(**kw),warm=opts.warm)
trainer.C=make
if __name__=='__main__':
    trainer.main()
