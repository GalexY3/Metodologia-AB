"""Audit public author SPSS file; return aggregate facts only, never raw IDs.
This is documentary source inspection, not a new AB-H cycle.
"""
import hashlib
import json
import pathlib
import sys

ROOT=pathlib.Path(__file__).resolve().parent.parent
HERE=ROOT/'HUMAN_OSF_VZX6Q_PUBLIC_INSPECTION'
sys.path.insert(0,str((HERE/'readstat_lib').resolve()))
import pyreadstat

DATA=HERE/'Speed_Dating.sav'
CODE=HERE/'2023-12-speed.R'
OUTPUT=HERE/'AGGREGATE_ONLY_R5_GATE.json'
HUMAN_DATA_SHA='3de995b8f8abc24908244d770009e600207d6b7940b4a91ff0b82573e45c9f01'
R_SCRIPT_SHA='de0d558c79a4e530070006575534d8be2b922c05e5acd0700a63e21a649ed67a'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    if OUTPUT.exists():raise SystemExit('OUTPUT_ALREADY_EXISTS')
    assert sha(DATA)==HUMAN_DATA_SHA and sha(CODE)==R_SCRIPT_SHA
    df,metadata=pyreadstat.read_sav(str(DATA),apply_value_formats=False)
    assert all(x in df.columns for x in ['Subject','Partner','Gender','Match','Subject_Choice','Partner_Choice'])
    assert len(df)==240 and len(df.columns)==31
    assert len(df[['Subject','Partner']].drop_duplicates())==240
    assert df['Subject'].nunique()==60 and df['Partner'].nunique()==8
    assert df.groupby('Subject').size().eq(4).all()
    assert df.groupby('Partner').size().eq(30).all()
    assert not df[['Subject_Choice','Partner_Choice','Match']].isna().any().any()
    assert set(df['Subject_Choice'].unique())=={1.,2.}
    assert set(df['Partner_Choice'].unique())=={1.,2.}
    assert set(df['Match'].unique())=={0.,1.}
    assert ((df['Subject_Choice'].eq(1)&df['Partner_Choice'].eq(1))==df['Match'].eq(1)).all()
    order_cols=[c for c in df.columns if any(x in c.lower() for x in
       ['round','timestamp','sequence','order','session','trial','wave','clock','datetime'])]
    choice_table={}
    for a in [1,2]:
      for b in [1,2]:
        choice_table[str(a)+'_'+str(b)]=int((df['Subject_Choice'].eq(a)&df['Partner_Choice'].eq(b)).sum())
    missing={}
    for k in ['MutualEyeGaze_duration','Subject_eyes_duration',
              'Partner_eyes_duration','Subject_Attractiveness','Partner_Attractiveness']:
      missing[k]=int(df[k].isna().sum())
    output={
      'schema':'R5_PUBLIC_HUMAN_OSF_VZX6Q_AGGREGATE_ONLY_V1',
      'audit_date':'2026-10-31','experiment':'Dual Eye-Tracking Speed Dating Study',
      'repository':'https://osf.io/vzx6q/',
      'article_doi':'https://doi.org/10.1007/s10508-023-02806-0',
      'public_original_data_sha256':sha(DATA),
      'original_R_analysis_source_sha256':sha(CODE),
      'downloaded_original_bytes':DATA.stat().st_size,
      'source_R_bytes':CODE.stat().st_size,
      'file_type':'IBM SPSS SAV version 27 $FL2',
      'participant_rows':int(len(df)),
      'observed_distinct_encounters':int(len(df[['Subject','Partner']].drop_duplicates())),
      'columns':list(df.columns),
      'n_main_subjects':int(df['Subject'].nunique()),
      'n_assigned_partner_people':int(df['Partner'].nunique()),
      'dates_per_main_subject':4,'dates_per_assigned_partner':30,
      'two_native_binary_dyad_votes_present':True,
      'Subject_Choice_yes_1':int(df['Subject_Choice'].eq(1).sum()),
      'Subject_Choice_no_2':int(df['Subject_Choice'].eq(2).sum()),
      'Partner_Choice_yes_1':int(df['Partner_Choice'].eq(1).sum()),
      'Partner_Choice_no_2':int(df['Partner_Choice'].eq(2).sum()),
      'both_yes_and_match_1':int(df['Match'].eq(1).sum()),
      'vote_cross_tab_subject_partner':choice_table,
      'native_bilateral_match_logic_exact':True,
      'choice_missing':0,
      'selected_predictor_missing':missing,
      'explicit_temporal_order_columns':order_cols,
      'native_sequence_within_each_4date_subject_verified':False,
      'candidate_set':'Assigned four real encounters per subject; denominator observed FOR assigned encounters, NOT all feasible partners',
      'detailed_opportunity_schedule_published_in_data':False,
      'reusable_data_license_verified':False,
      'OSF_public_access_not_equivalent_to_reuse_license':True,
      'R5_strict_admission':'BLOCKED_NO_VERIFIED_NATIVE_ROUND_OR_TIME_AND_NO_DATA_LICENSE_VERIFIED',
      'human_R5_STOP':True,'scientific_CT2':7,
      'human_independent_cohort_novel':True,
      'predictive_model_estimated':False,'raw_human_rows_published_to_GitHub':False,
      'no_original_ids_or_rows_in_output':True,
      'scope_caveat':'No DA stable-allocation or strategic-offer test without participant ordinal full preference schedules and allocation exclusivity. The raw dataset measures choice following scheduled dates, not the matching institution.'
    }
    OUTPUT.write_text(json.dumps(output,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    print('R5_AGGREGATE_AUDIT',output['participant_rows'],'rows,',
      output['both_yes_and_match_1'],'mutual,',
      output['R5_strict_admission'],'SHA',sha(OUTPUT))
if __name__=='__main__':main()
