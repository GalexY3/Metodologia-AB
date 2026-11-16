"""Bounded public-source priority check; no contact with authors or reviewers."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib
import json
import sys
import urllib.request

B=Path(__file__).resolve().parent
F=B/'literatura/ADVALIGN2025_AUDIT_20261116'


def main():
    attempt=sys.argv[1] if len(sys.argv)>1 else 'INITIAL'
    assert attempt in ['INITIAL','NETWORK_RETRY']
    suffix='' if attempt=='INITIAL' else '_NETWORK_RETRY'
    out=F/f'PRIORITY_DISCUSSION_RECEIPT{suffix}.json'
    assert not out.exists()
    url='https://api2.openreview.net/notes?forum=QFO1asgas2&limit=1000'
    record=dict(checked_at_utc=datetime.now(timezone.utc).isoformat(),url=url,
        search_scope='Public OpenReview forum notes plus bounded title/Nash/counterexample/erratum web queries',
        priority_established=False,external_confirmation=False,
        limitations=['A bounded search cannot establish absence of prior art.',
                    'No author or independent researcher has reviewed our counterexample.'])
    try:
        request=urllib.request.Request(url,headers={'User-Agent':'AB-TFM-research-audit/1.0'})
        with urllib.request.urlopen(request,timeout=30) as response:
            raw=response.read();record['HTTP_status']=response.status
        data=json.loads(raw)
        record.update(downloaded_sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),
            public_notes=len(data.get('notes',[])),total_count=data.get('count'))
        (F/'OPENREVIEW_PUBLIC_NOTES_LOCAL_ONLY.json').write_bytes(raw)
        records=[]
        for note in data.get('notes',[]):
            content=note.get('content',{});fields={}
            for key,value in content.items():
                value=value.get('value') if isinstance(value,dict) and 'value' in value else value
                if isinstance(value,str):fields[key]=value
            text='\n'.join(fields.values())
            terms=['nash','orthonormal','marginal','counterexample','theorem 3','erratum']
            hits=[term for term in terms if term in text.lower()]
            records.append(dict(id=note['id'],invitations=note.get('invitations'),
                fields=list(fields),hits=hits))
        record['note_inventory']=records
    except Exception as exc:
        record.update(access_status='UNAVAILABLE',error_type=type(exc).__name__,error=str(exc))
    out.write_text(json.dumps(record,indent=2),encoding='utf-8')
    print(json.dumps(record,indent=2))


if __name__=='__main__':main()
