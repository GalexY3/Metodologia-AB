"""V36 factorial: V32 institutional choice trained from scratch with degree 4.

All policy code and rewards are delegated to V32, only neighbor degree changes.
"""
from __future__ import annotations
from targeted_gifts import C as OriginalC
import v32_institution_choice as original

def graph4(*args,**kwargs):
 assert kwargs.get('degree',6)==6
 kwargs['degree']=4
 return OriginalC(*args,**kwargs)

def main():
 parser=original.cli
 def add_degree():
  p=parser()
  p.add_argument('--v36-degree',type=int,choices=(4,),required=True)
  return p
 original.cli=add_degree
 original.C=graph4
 original.main()
if __name__=='__main__':main()
