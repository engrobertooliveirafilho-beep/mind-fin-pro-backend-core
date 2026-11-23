"""Behavioral reconstruction transcribed from the four Drive source texts.
Not claimed byte-identical to the Drive originals; retained only as a test fixture.
"""
from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional
from datetime import datetime, timezone
KnowledgeStatus=Literal["active","deprecated"]
@dataclass
class KnowledgeItem:
 key:str;version:int;status:KnowledgeStatus;payload:Dict[str,Any]
class KnowledgeLifecycleManager:
 def __init__(self)->None:self._items:Dict[str,List[KnowledgeItem]]={}
 def _get_list(self,key:str)->List[KnowledgeItem]:return self._items.setdefault(key,[])
 def create(self,key:str,payload:Dict[str,Any])->KnowledgeItem:
  lst=self._get_list(key);version=1 if not lst else max(i.version for i in lst)+1
  item=KnowledgeItem(key=key,version=version,status="active",payload=dict(payload));lst.append(item);return item
 def revise(self,key:str,payload:Dict[str,Any])->KnowledgeItem:return self.create(key,payload)
 def deprecate(self,key:str,version:Optional[int]=None)->None:
  for item in self._get_list(key):
   if version is None or item.version==version:item.status="deprecated"
 def get_latest_active(self,key:str)->Optional[KnowledgeItem]:
  lst=[i for i in self._get_list(key) if i.status=="active"]
  return max(lst,key=lambda i:i.version) if lst else None
CanonStatus=Literal["experimental","canon"]
@dataclass
class CanonEntry:
 key:str;version:int;status:CanonStatus;payload:Dict[str,Any]
class CanonBuilder:
 def __init__(self)->None:self._entries:Dict[str,List[CanonEntry]]={}
 def _get_list(self,key:str)->List[CanonEntry]:return self._entries.setdefault(key,[])
 def add_experimental(self,key:str,payload:Dict[str,Any])->CanonEntry:
  items=self._get_list(key);version=1 if not items else max(e.version for e in items)+1
  entry=CanonEntry(key=key,version=version,status="experimental",payload=dict(payload));items.append(entry);return entry
 def promote_to_canon(self,key:str,version:Optional[int]=None)->Optional[CanonEntry]:
  items=self._get_list(key)
  if not items:return None
  target=max(items,key=lambda e:e.version) if version is None else next((e for e in items if e.version==version),None)
  if target is None:return None
  for e in items:
   if e is target:e.status="canon"
   elif e.status=="canon":e.status="experimental"
  return target
 def get_latest_canon(self,key:str)->Optional[CanonEntry]:
  items=[e for e in self._get_list(key) if e.status=="canon"]
  return max(items,key=lambda e:e.version) if items else None
@dataclass
class Treaty:
 parties:List[str];terms:Dict[str,Any]
@dataclass
class TreatyResult:
 status:Literal["accepted","rejected"];reason:str;agreed_terms:Dict[str,Any]
 def to_dict(self):return {"status":self.status,"reason":self.reason,"agreed_terms":self.agreed_terms}
class CognitiveTreatyProtocol:
 def negotiate(self,parties:List[str],proposal:Dict[str,Any])->TreatyResult:
  topics=[str(t).lower() for t in proposal.get("topics",[])];mode=str(proposal.get("mode","cooperation")).lower()
  if any(t in ("aggression","unbounded_access") for t in topics):return TreatyResult("rejected","Proposta contem topicos proibidos (aggression/unbounded_access).",{})
  if mode=="cooperation":
   agreed={"mode":"cooperation","max_data_sensitivity":proposal.get("max_data_sensitivity",5),"shared_topics":topics,"parties":list(parties)}
   return TreatyResult("accepted","Tratado de cooperacao aceito dentro dos limites basicos.",agreed)
  return TreatyResult("rejected","Modo de tratado nao suportado neste STEP.",{})
@dataclass
class EthicalReviewItem:
 item_id:str;payload:Dict[str,Any];status:Literal["pending","approved","rejected"];created_at:datetime
 reviewed_at:Optional[datetime]=None;reviewer:Optional[str]=None;notes:Optional[str]=None
class EthicalReviewBoard:
 def __init__(self)->None:self._items:Dict[str,EthicalReviewItem]={};self._counter=0
 def _now(self):return datetime.now(timezone.utc)
 def _next_id(self):self._counter+=1;return f"ERB-{self._counter}"
 def submit(self,payload):
  item_id=self._next_id();item=EthicalReviewItem(item_id,dict(payload),"pending",self._now());self._items[item_id]=item;return item
 def list_pending(self):return [i for i in self._items.values() if i.status=="pending"]
 def _set_status(self,item_id,status,reviewer,notes):
  item=self._items.get(item_id)
  if item is None:return None
  item.status=status;item.reviewer=reviewer;item.notes=notes;item.reviewed_at=self._now();return item
 def approve(self,item_id,reviewer,notes=None):return self._set_status(item_id,"approved",reviewer,notes)
 def reject(self,item_id,reviewer,notes=None):return self._set_status(item_id,"rejected",reviewer,notes)
