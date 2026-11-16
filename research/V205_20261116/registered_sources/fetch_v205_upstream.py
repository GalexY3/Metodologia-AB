"""Reproduce source acquisition without redistributing third-party source files."""
from pathlib import Path
import hashlib
import urllib.request

B=Path(__file__).resolve().parent
TARGET=B/'literatura/ADVALIGN2025_AUDIT_20261116'
SHA={'train.py':'995b645c05103957855abfe1420e80cb0ac5e3f24ed9ee399081578019348c61',
     'utils.py':'7f0e0e019e4b47aa9c7077676bb1ae950fb69d1c4a3cf06c291f5664e0657f66'}


def main():
    TARGET.mkdir(parents=True,exist_ok=True)
    for name,digest in SHA.items():
        p=TARGET/name
        if p.exists():assert hashlib.sha256(p.read_bytes()).hexdigest()==digest;continue
        url=f'https://raw.githubusercontent.com/jduquevan/advantage-alignment/2065e43c0c36694965cf4476dc692512e3892dcc/{name}'
        with urllib.request.urlopen(url,timeout=40) as response:raw=response.read()
        assert hashlib.sha256(raw).hexdigest()==digest,name
        p.write_bytes(raw)
    print('Pinned source bytes verified; files have not been imported or run')


if __name__=='__main__':main()
