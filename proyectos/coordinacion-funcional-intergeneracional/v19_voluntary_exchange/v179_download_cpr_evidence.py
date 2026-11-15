"""Retrieve the published anonymized China monitoring replication archive.

Source: Buntaine, Zhang and Hunnicutt (2021), PNAS, OSF 8fzmq.
Only downloads and inventories; it never executes authors' analysis scripts.
"""
import hashlib
import json
from pathlib import Path
from datetime import datetime,timezone
import urllib.request
import zipfile

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'datos_humanos/metaketa_china_2021'
API='https://api.osf.io/v2/nodes/8fzmq/files/osfstorage/'


def fetch(url):
    with urllib.request.urlopen(url,timeout=45) as response:return response.read()


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    metadata=fetch(API);listing=json.loads(metadata)
    matches=[f for f in listing['data'] if f['attributes']['name']=='Buntaine_Zhang_Hunnicutt_PNAS_2021_replication.zip']
    assert len(matches)==1;item=matches[0]
    path=OUT/item['attributes']['name'];url=item['links']['download']
    assert not path.exists(),'Preserve the existing original; do not re-download over it.'
    part=path.with_suffix('.zip.part')
    with urllib.request.urlopen(url,timeout=45) as response,part.open('xb') as target:
        while block:=response.read(1024*1024):target.write(block)
    assert part.stat().st_size==item['attributes']['size']
    part.replace(path)
    with zipfile.ZipFile(path) as z:
        bad=z.testzip();assert bad is None,bad
        inventory=[dict(name=i.filename,size=i.file_size,compressed=i.compress_size) for i in z.infolist()]
    manifest=dict(retrieved_utc=datetime.now(timezone.utc).isoformat(),metadata_api=API,
        published_data_statement='https://pmc.ncbi.nlm.nih.gov/articles/PMC8307295/',
        osf_project='https://osf.io/8fzmq/',download_url=url,
        original_file=str(path.relative_to(ROOT)),bytes=path.stat().st_size,
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),crc_verified=True,files=inventory,
        human_data_claim='Published anonymized replication archive; privacy/grain still to be audited.',
        third_party_code_executed=False,independent_confirmation_of_our_hypotheses=False)
    (OUT/'OSF_METADATA.json').write_bytes(metadata)
    (OUT/'DOWNLOAD_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
    print(json.dumps({k:v for k,v in manifest.items() if k!='files'}),flush=True)
    print('FILES',json.dumps(inventory),flush=True)


if __name__=='__main__':main()
