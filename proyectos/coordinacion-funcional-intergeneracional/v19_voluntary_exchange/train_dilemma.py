"""Independent own-reward MARL with truly unilateral costly public goods."""
import train
import public_goods_dilemma
train.rollout=public_goods_dilemma.rollout
if __name__=='__main__':train.main()
