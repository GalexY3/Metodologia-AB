"""Private decaying identity memory for who helped whom, not teacher action."""
import argparse,dataclasses,sys
import train_targeted as trainer
p=argparse.ArgumentParser(add_help=False)
p.add_argument('--decay',type=float,default=.85)
p.add_argument('--warm',type=float,default=0.)
opts,remaining=p.parse_known_args()
assert 0<=opts.decay<1
assert 0<=opts.warm<=1
sys.argv=[sys.argv[0]]+remaining
original=trainer.C
def make(**kw):return dataclasses.replace(original(**kw),
          memory_decay=opts.decay,warm=opts.warm)
trainer.C=make
if __name__=='__main__':trainer.main()
