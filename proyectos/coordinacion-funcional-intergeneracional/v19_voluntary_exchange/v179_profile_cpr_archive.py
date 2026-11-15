"""Scoped quality audit of waterway outcomes, without household microdata."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import hashlib
import io
import json
from pathlib import Path
import zipfile
import pandas as pd
from research_resource_limits import apply_limits

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'datos_humanos/metaketa_china_2021'
PREFIX='UrbanWaterways_replication/'
FILES=('04_Processed Data/h2o.quality_analysis.csv',
       '04_Processed Data/h2o_noimpute.csv',
       '04_Processed Data/h2o.quality_meta.analysis.csv')


def main():
    limits=apply_limits(3)
    archive=DATA/'Buntaine_Zhang_Hunnicutt_PNAS_2021_replication.zip'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()=='e67848f5759d2ed8d3746a4d9dc1ce2192e977b22f0f86ae3ce12e9ec8182ffa'
    profiles=[]
    with zipfile.ZipFile(archive) as z:
        for name in FILES:
            content=z.read(PREFIX+name);df=pd.read_csv(io.BytesIO(content),low_memory=False)
            columns=[]
            for c in df:
                s=df[c];n=int(s.nunique(dropna=True))
                col=dict(name=c,dtype=str(s.dtype),nulls=int(s.isna().sum()),
                         null_fraction=float(s.isna().mean()),distinct=n)
                if pd.api.types.is_numeric_dtype(s):
                    col.update(minimum=None if s.dropna().empty else float(s.min()),
                               maximum=None if s.dropna().empty else float(s.max()))
                # Categories of aggregate treatment/period columns only.
                if n<=8 and any(token in c.lower() for token in ('treat','round','time','assign','wave')):
                    col['counts']={str(k):int(v) for k,v in s.value_counts(dropna=False).items()}
                columns.append(col)
            profile=dict(archive_member=PREFIX+name,sha256=hashlib.sha256(content).hexdigest(),
                         rows=len(df),column_count=len(df.columns),exact_duplicate_rows=int(df.duplicated().sum()),columns=columns)
            profiles.append(profile)
            print('V179_PROFILE',json.dumps({k:v for k,v in profile.items() if k!='columns'}),flush=True)
            print('V179_COLUMNS',json.dumps(list(df.columns)),flush=True)
        for remote,local in (
                ('05_Analysis Code/UrbanWaterways_analysis.R','Buntaine2021_UrbanWaterways_analysis.R'),
                ('04_Processed Data/UrbanWaterways_datacompile.R','Buntaine2021_UrbanWaterways_datacompile.R')):
            path=ROOT/'literatura/original_code'/local;content=z.read(PREFIX+remote)
            if path.exists():assert path.read_bytes()==content
            else:path.write_bytes(content)
    output=ROOT/'results/V179_WATERWAY_DATA_PROFILE.json';assert not output.exists()
    output.write_text(json.dumps(dict(study='V179_DATA_QUALITY_ONLY',limits=limits,profiles=profiles,
               provenance='Published Buntaine et al.2021 anonymized archive; ZIP preserved.',
               household_data_read=False,third_party_R_code_executed=False,
               confirms_our_mechanisms=False,CT2_change=0),indent=2),encoding='utf8')


if __name__=='__main__':main()
