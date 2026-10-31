"""Freeze all six ESBM original people(seed) populations and PCG64 tensor bytes.

This instrument generates ONLY inputs. It does not execute ESBM.simulate, read
historical RUNS or measure a model outcome. Original Python source stays intact.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import sys
import numpy as np

ROOT=Path(__file__).resolve().parent.parent
ORIG=ROOT.parent/'ESBM_AUDIT_N337_20261031'/'esbm_dynamic.py'
OLD_MANIFEST=ROOT.parent/'ESBM_AUDIT_N337_20261031'/'N338_INPUT_MANIFEST.json'
DIR=ROOT/'official_inputs_60'
NAMES=['u_send','u_reply','u_hazard','u_expose','u_match']
SEEDS=[101,211,307,401,503,601]

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if DIR.exists() or (ROOT/'N341_INPUT_MANIFEST.json').exists():
        raise SystemExit('INPUTS_OR_MANIFEST_ALREADY_EXIST')
    assert sha(ORIG)=='f7e6b84000720cbdf2ee0800c2b10d136185facd00e4622756cbb5f8d8254d0b'
    old=json.loads(OLD_MANIFEST.read_text(encoding='utf8'))
    assert sha(OLD_MANIFEST)=='075900f243f31e0306d7a72c2075a45818782fcbc860cd1a5c07a46439c2b994'
    spec=importlib.util.spec_from_file_location('ESBM_ORIGINAL_INPUTS_ONLY_N341',ORIG)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert (module.N,module.STEPS,module.K)==(144,16,7)
    DIR.mkdir()
    rows=[]
    for seed in SEEDS:
        p=module.people(seed)
        path=DIR/f'people_{seed}.json'
        people={k:p[k].tolist() for k in ['genders','scopes','norm','q','age']}
        path.write_text(json.dumps(people,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n',encoding='utf8')
        entry={'seed':seed,'people':{'path':path.name,'sha256':sha(path),'bytes':path.stat().st_size},'tensors':{}}
        for kind in NAMES:
            a=p[kind]
            assert a.shape==(16,144,144) and a.dtype==np.float64
            t=DIR/f'{kind}_{seed}.bin'
            t.write_bytes(a.tobytes(order='C'))
            entry['tensors'][kind]={'path':t.name,'sha256':sha(t),'bytes':t.stat().st_size,'shape':[16,144,144],'dtype':'float64LE'}
        if seed==101:
            assert entry['people']['sha256']==old['files']['people']['sha256']
            for kind in NAMES:assert entry['tensors'][kind]['sha256']==old['files'][kind]['sha256']
        rows.append(entry)
    manifest={'schema':'ABH_N341_ORIGINAL_INPUTS_FROZEN',
       'original_ESBM_sha256':sha(ORIG),'input_generator_sha256':sha(__file__),
       'python':sys.version.split()[0],'numpy':np.__version__,'platform':platform.platform(),
       'n':144,'t':16,'k':7,'seed_order':SEEDS,'scenario_order':list(module.SCENARIOS),
       'provenance':'6 ORIGINAL people(seed) call results, 5 shocks tensors per seed; NO simulation outcomes created',
       'seed101_byte_equal_to_preexisting_N338':True,'rows':rows}
    target=ROOT/'N341_INPUT_MANIFEST.json'
    target.write_text(json.dumps(manifest,indent=2,allow_nan=False)+'\n',encoding='utf8')
    print('N341_INPUTS_ONLY',len(rows),'arrays',len(rows)*5,'bytes',sum(x['people']['bytes']+sum(y['bytes'] for y in x['tensors'].values()) for x in rows),'manifest_sha',sha(target))

if __name__=='__main__':main()
