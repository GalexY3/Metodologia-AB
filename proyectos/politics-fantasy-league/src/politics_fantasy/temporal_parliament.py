"""Strict source-scoped parliamentary events: no inferred canonical identities or time of first publication.

Safety contract for ingestion, NOT a political scoring system.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date,datetime
from enum import Enum
class Kind(str,Enum):
 SEAT='PLENO_SEAT'
 GROUP='PARLIAMENTARY_GROUP'
 INTERNAL='INTERNAL_ORGAN'
class Change(str,Enum):
 ENTER='ENTER'
 EXIT='EXIT'
@dataclass(frozen=True)
class ParliamentaryEvent:
 source_id:str
 event_id:str
 source_scoped_person_key:str
 kind:Kind
 change:Change
 effective_date:date
 published_date:date|None
 source_url:str
 group_code:str|None=None
 canonical_person_id:str|None=None
 first_public_at:datetime|None=None
 def __post_init__(self):
  if not all([self.source_id.strip(),self.event_id.strip(),self.source_scoped_person_key.strip()]):raise ValueError('source keys required')
  if not self.source_url.startswith('https://www.congreso.es/'):raise ValueError('unverified Congress URL')
  if self.kind is Kind.GROUP and not self.group_code:raise ValueError('group code required')
  if self.kind is not Kind.GROUP and self.group_code is not None:raise ValueError('group code belongs to another event')
  if self.first_public_at is not None:raise ValueError('no certified first-public timestamp')
  if self.canonical_person_id is not None:raise ValueError('name does not prove legal identity')
 @property
 def key(self):return (self.source_id,self.event_id)
 def applicable_on(self,when:date)->bool:return self.effective_date<=when
 def evidenced_by(self,when:date)->bool:return self.published_date is not None and self.published_date<=when
 @property
 def is_score_eligible(self)->bool:return False
def apply_events(events:list[ParliamentaryEvent],*,effective_at:date,document_as_of:date)->dict[tuple[str,str],dict[Kind,set[str]]]:
 keys=[x.key for x in events]
 if len(set(keys))!=len(keys):raise ValueError('duplicate original event key')
 per_target={}
 for e in events:
  target=e.group_code if e.kind is Kind.GROUP else e.kind.value
  key=(e.source_id,e.source_scoped_person_key,e.kind,target,e.effective_date)
  old=per_target.setdefault(key,e.change)
  if old!=e.change:raise ValueError('opposing same-day events; legal order unresolved')
 view={}
 for e in sorted(events,key=lambda z:(z.effective_date,z.source_id,z.event_id)):
  if not (e.applicable_on(effective_at) and e.evidenced_by(document_as_of)):continue
  person=view.setdefault((e.source_id,e.source_scoped_person_key),{k:set() for k in Kind})
  target=e.group_code if e.kind is Kind.GROUP else e.kind.value
  if e.change is Change.ENTER:person[e.kind].add(target)
  else:person[e.kind].discard(target)
 return view
