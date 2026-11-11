"""Freeze and evaluate public-goods agents with the same V19 test grid."""
import audit
import public_goods
audit.advance=public_goods.advance
if __name__=='__main__':audit.run(audit.parse())
