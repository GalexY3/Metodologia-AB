"""Verify published blob bytes and optionally stream the public remote archive."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import urllib.request
import zipfile

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[2]
PREFIX=ROOT.relative_to(REPO).as_posix()+'/'
OUT=ROOT/'research/V175_V180_20261115'


def main():
    p=argparse.ArgumentParser();p.add_argument('--commit',required=True);p.add_argument('--label',required=True)
    p.add_argument('--download',action='store_true');args=p.parse_args()
    text=(ROOT/'publish_v175_v180.ps1').read_text(encoding='utf8')
    section=text.split('$taskFiles = @(',1)[1].split('\n)',1)[0]
    paths=re.findall(r"'([^']+)'",section);mismatches=[]
    for relative in paths:
        try:remote=subprocess.check_output(['git','cat-file','blob',args.commit+':'+PREFIX+relative],cwd=REPO,stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            mismatches.append(dict(path=relative,remote_missing=True));continue
        expected=(ROOT/relative).read_bytes()
        if remote!=expected:mismatches.append(dict(path=relative,local_sha256=hashlib.sha256(expected).hexdigest(),git_blob_sha256=hashlib.sha256(remote).hexdigest()))
    archive=OUT/'EVIDENCE.zip'
    with zipfile.ZipFile(archive) as z:manifest_equal=z.read('EVIDENCE_SHA256.json')==(OUT/'SHA256.json').read_bytes()
    result=dict(commit=args.commit,paths_checked=len(paths),direct_blob_mismatches=mismatches,
         outer_manifest_matches_embedded_bytes=manifest_equal,
         local_archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest())
    if args.download:
        url='https://raw.githubusercontent.com/GalexY3/Metodologia-AB/'+args.commit+'/'+PREFIX+'research/V175_V180_20261115/EVIDENCE.zip'
        h=hashlib.sha256();size=0
        with urllib.request.urlopen(url,timeout=45) as stream:
            while block:=stream.read(1024*1024):h.update(block);size+=len(block)
        assert size==archive.stat().st_size and h.hexdigest()==result['local_archive_sha256']
        result.update(remote_archive_url=url,remote_archive_bytes=size,remote_archive_sha256=h.hexdigest(),remote_stream_verified=True)
    path=OUT/('REMOTE_DELIVERY_'+args.label+'.json');assert not path.exists()
    path.write_text(json.dumps(result,indent=2),encoding='utf8')
    print('DELIVERY_AUDIT',json.dumps(result),flush=True)


if __name__=='__main__':main()
