import unittest
from hashlib import sha256
from politics_fantasy.source_guard import verify_pinned_bytes
ORIGINAL='https://www.congreso.es/webpublica/opendata/votaciones/Leg15/Sesion034/20240409/Votacion001/VOT_20240409210631.json'
class SourceIntegrity(unittest.TestCase):
 def test_known_original_sha_rejects_fake_payload(self):
  with self.assertRaisesRegex(ValueError,'differ'):verify_pinned_bytes(b'not real Congress JSON',ORIGINAL,'c8de1b79f50085e2148d3d9e30d766446c67b43f53d2c213a372fa4c36ce168e')
 def test_synthetic_pinned_fixture_allowed_but_not_certified(self):
  payload=b'{"fictional":true}'
  record=verify_pinned_bytes(payload,ORIGINAL,sha256(payload).hexdigest())
  self.assertFalse(record['provider_signature_verified'])
  self.assertFalse(record['rights_verified'])
 def test_changed_bytes_rejected(self):
  raw=b'{"one":1}'
  with self.assertRaises(ValueError):verify_pinned_bytes(b'{"one":2}',ORIGINAL,sha256(raw).hexdigest())
 def test_host_trick_rejected(self):
  with self.assertRaises(ValueError):verify_pinned_bytes(b'test','https://www.congreso.es.evil.com/webpublica/a',sha256(b'test').hexdigest())
