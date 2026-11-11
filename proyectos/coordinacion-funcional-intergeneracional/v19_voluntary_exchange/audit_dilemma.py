"""Frozen causal audit in the unilateral costly-donation game."""
import audit
import public_goods_dilemma
audit.advance=public_goods_dilemma.advance
if __name__=='__main__':audit.run(audit.parse())
