"""Retrieve the CC0 original Yaman et al.2023 code and published raw runs."""
import hashlib
import json
from pathlib import Path
import shutil
import time
import urllib.request
import zipfile

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'literatura/original_code/Yaman2023'
API='https://zenodo.org/api/records/8401555'


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    with urllib.request.urlopen(API,timeout=45) as s:raw=s.read()
    meta=json.loads(raw);assert meta['metadata']['license']['id']=='cc-zero'
    item=next(f for f in meta['files'] if f['key']=='evolution-of-social-sanctions.zip')
    target=OUT/item['key'];assert not target.exists()
    assert shutil.disk_usage(OUT).free>2_000_000_000
    part=target.with_suffix('.zip.part');assert not part.exists()
    start=time.perf_counter();n=0;last=0;md5=hashlib.md5();sha=hashlib.sha256()
    with urllib.request.urlopen(item['links']['self'],timeout=60) as src,part.open('xb') as dst:
        while block:=src.read(1024*1024):
            dst.write(block);n+=len(block);md5.update(block);sha.update(block)
            if n-last>=16*1024*1024:
                last=n;print('DOWNLOAD_BYTES',n,'elapsed',round(time.perf_counter()-start,1),flush=True)
    assert n==item['size'] and 'md5:'+md5.hexdigest()==item['checksum']
    part.replace(target)
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        files=[dict(path=i.filename,bytes=i.file_size) for i in z.infolist()]
        for i in z.infolist():
            if i.filename.endswith('.m') and '__MACOSX' not in i.filename:
                relative=Path(i.filename)
                assert '..' not in relative.parts and not relative.is_absolute()
                p=OUT/'source'/relative;p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();p.write_bytes(z.read(i))
    (OUT/'ZENODO_METADATA.json').write_bytes(raw)
    manifest=dict(doi='10.5061/dryad.dv41ns24r',zenodo_record=8401555,license='CC0-1.0 as registered in Zenodo metadata',
          url=item['links']['self'],bytes=n,md5=md5.hexdigest(),sha256=sha.hexdigest(),CRC_verified=True,
          files=files,original_scripts_executed=False,not_new_human_data=True,
          elapsed=time.perf_counter()-start)
    (OUT/'DOWNLOAD_MANIFEST.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode('utf8'))
    print('YAMAN_ORIGINAL_DOWNLOADED',json.dumps({k:v for k,v in manifest.items() if k!='files'}),flush=True)
    print('MATLAB_SOURCES',json.dumps([r for r in files if r['path'].endswith('.m') and '__MACOSX' not in r['path']]),flush=True)


if __name__=='__main__':main()
