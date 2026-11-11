"""Independent RL for unilateral public goods, no teacher or global reward."""
import train
import public_goods
train.rollout=public_goods.rollout
if __name__=='__main__':train.main()
