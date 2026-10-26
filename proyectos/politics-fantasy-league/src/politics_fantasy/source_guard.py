"""Pinned-byte verifier; digests are NOT provider signatures or reuse grants."""
from hashlib import sha256
from urllib.parse import urlsplit
import re
def verify_pinned_bytes(raw:bytes,original_uri:str,independently_pinned_sha256:str)->dict:
 addr=urlsplit(original_uri)
 if addr.scheme!='https' or addr.hostname!='www.congreso.es' or addr.username or addr.password or addr.port or not addr.path.startswith(('/es/','/webpublica/','/public_oficiales/')):raise ValueError('not recognized Congress original URI')
 if not isinstance(independently_pinned_sha256,str) or not re.fullmatch('[0-9a-f]{64}',independently_pinned_sha256):raise ValueError('invalid source digest')
 digest=sha256(raw).hexdigest()
 if digest!=independently_pinned_sha256:raise ValueError('source bytes differ from pinned digest')
 return {'original_uri':original_uri,'sha256':digest,'bytes':len(raw),'provider_signature_verified':False,'rights_verified':False}
