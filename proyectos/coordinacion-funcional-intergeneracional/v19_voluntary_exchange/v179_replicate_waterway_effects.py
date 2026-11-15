"""Independent Python reconstruction of the published water-quality analysis.

No household data and no third-party R execution. This reproduces existing
human evidence; it does not confirm the ecological simulator's hypotheses.
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
import hashlib
import io
import json
from pathlib import Path
import zipfile
import numpy as np
import pandas as pd
from scipy.stats import f as f_distribution,t as t_distribution
from research_resource_limits import apply_limits

ROOT=Path(__file__).resolve().parent
ZIP=ROOT/'datos_humanos/metaketa_china_2021/Buntaine_Zhang_Hunnicutt_PNAS_2021_replication.zip'
PREFIX='UrbanWaterways_replication/'


def cr2(X,y,clusters,contrasts):
    """OLS, Bell-McCaffrey cluster CR2 and Satterthwaite contrast df.

    OLS working covariance is identity; Ai=(I-Hii)^(-1/2). No survey weights.
    Definitions: estimatr mathematical notes, cluster-robust variance section.
    """
    q,r=np.linalg.qr(X,mode='reduced');inv_r=np.linalg.inv(r);bread=inv_r@inv_r.T
    beta=np.linalg.solve(r,q.T@y);e=y-X@beta;hat=q@q.T;residual=np.eye(len(y))-hat
    groups=[np.flatnonzero(clusters==g) for g in np.unique(clusters)]
    meat=np.zeros((X.shape[1],X.shape[1]));adjustments=[]
    for ii in groups:
        block=np.eye(len(ii))-hat[np.ix_(ii,ii)]
        eigen,vectors=np.linalg.eigh(block);assert eigen.min()>1e-12
        a=(vectors*(1/np.sqrt(eigen)))@vectors.T
        score=X[ii].T@a@e[ii];meat+=np.outer(score,score);adjustments.append(a)
    covariance=bread@meat@bread;rows=[]
    for label,c in contrasts.items():
        estimate=float(c@beta);se=float(np.sqrt(c@covariance@c))
        p=np.column_stack([residual[:,ii]@a@X[ii]@bread@c for ii,a in zip(groups,adjustments)])
        gram=p.T@p;df=float(np.trace(gram)**2/np.sum(gram*gram))
        crit=float(t_distribution.ppf(.975,df));pv=float(2*t_distribution.sf(abs(estimate/se),df))
        rows.append(dict(contrast=label,estimate=estimate,se_CR2=se,df_Satterthwaite=df,
                         ci95=[estimate-crit*se,estimate+crit*se],p_two_sided=pv))
    return beta,covariance,rows


def main():
    limits=apply_limits(3);assert hashlib.sha256(ZIP.read_bytes()).hexdigest()=='e67848f5759d2ed8d3746a4d9dc1ce2192e977b22f0f86ae3ce12e9ec8182ffa'
    with zipfile.ZipFile(ZIP) as z:
        def read(name,**kwargs):return pd.read_csv(io.BytesIO(z.read(PREFIX+name)),**kwargs)
        d=read('04_Processed Data/h2o.quality_analysis.csv')
        raw=read('04_Processed Data/h2o_noimpute.csv')
        exported=read('06_Results/output_ATEresults.csv')
        assert not d.duplicated(['wway_id','audit']).any()
        assert d.groupby('wway_id').size().eq(2).all() and d.wway_id.nunique()==160
        assert d.groupby('wway_id')[['treat_g','treat_p','i.block']].nunique().eq(1).all().all()
        assert not raw.duplicated(['wway_id','audit']).any()
        joined=d[['wway_id','audit']].merge(raw,on=['wway_id','audit'],how='left',validate='one_to_one',indicator=True)
        assert joined['_merge'].eq('both').all()
        used=['m1_qual.noDO','m1b_qual','c1_pre.a_m1','c2_pre.b_m1','c3_temp_m1']
        missing={c:int(joined[c].isna().sum()) for c in used}
        assert d[used].notna().all().all()
        y=d['m1_qual.noDO'].to_numpy(float)
        controls=['m1b_qual','c1_pre.a_m1','c2_pre.b_m1','c3_temp_m1']
        C=np.c_[np.ones(len(d)),d[controls].to_numpy(float),pd.get_dummies(d['audit'],drop_first=True).to_numpy(float)]
        treatments=d[['treat_g','treat_p']].to_numpy(float)
        X0=np.c_[np.ones(len(d)),treatments,C[:,1:]]
        cities=pd.get_dummies(d['city'],drop_first=True).to_numpy(float)
        X=np.c_[X0,cities]
        b0=np.linalg.lstsq(X0,y,rcond=None)[0];bb=np.linalg.lstsq(X,y,rcond=None)[0]
        rss0=np.sum((y-X0@b0)**2);rss=np.sum((y-X@bb)**2)
        df1=X.shape[1]-X0.shape[1];df2=len(y)-X.shape[1]
        fstat=float(((rss0-rss)/df1)/(rss/df2))
        wrong=float(f_distribution.cdf(.95,df1,df2));right=float(f_distribution.ppf(.95,df1,df2))
        assert fstat>right and fstat>wrong,'Read the actual specification selection before proceeding.'
        contrasts={}
        for label,coefs in (('government',(1,0)),('public',(0,1)),('government_minus_public',(1,-1))):
            c=np.zeros(X.shape[1]);c[1:3]=coefs;contrasts[label]=c
        beta,covariance,estimates=cr2(X,y,d['wway_id'].to_numpy(),contrasts)
        original=exported[(exported['hypothesis']=='H1')&(exported['outcome_var']=='M1')&
                          (exported['parameter']=='AME')&(exported['subset']=='full')]
        checks=[]
        for label,trt in (('government',"gov't"),('public','public')):
            e=next(r for r in estimates if r['contrast']==label);r=original[original['treatment']==trt].iloc[0]
            point_error=abs(e['estimate']-float(r['estimate']));se_error=abs(e['se_CR2']-float(r['se']))
            ci_error=max(abs(e['ci95'][0]-float(r['ci_95_lower'])),abs(e['ci95'][1]-float(r['ci_95_upper'])))
            assert point_error<=.00005 and se_error<=.00005 and ci_error<1e-8,(label,point_error,se_error,ci_error)
            checks.append(dict(contrast=label,published_estimate_4dp=float(r['estimate']),point_error=point_error,
                               published_se_4dp=float(r['se']),se_error=se_error,ci_max_error=ci_error))
        # Reuse the authors' exact 10,000 blocked assignment permutations.
        perm=read('04_Processed Data/treat_permutations.csv',dtype={'wway_id':np.int32,'perm':np.int16,'i.block':np.int16,'treat':'category'})
        assert not perm.duplicated(['perm','wway_id']).any()
        assert perm.groupby('perm').size().eq(160).all() and perm['perm'].nunique()==10000
        pivot=perm.pivot(index='wway_id',columns='perm',values='treat')
        assert set(pivot.index)==set(d.wway_id)
        assert pivot.notna().all().all()
        labels=pivot.to_numpy();gov=np.isin(labels,['govt','both']);pub=np.isin(labels,['public','both'])
        assert np.all(gov.sum(0)==60) and np.all(pub.sum(0)==60) and np.all((gov&pub).sum(0)==40)
        positions=pivot.index.get_indexer(d.wway_id);Tg=gov[positions].astype(float);Tp=pub[positions].astype(float)
        nuisance=np.c_[C,cities];q,_=np.linalg.qr(nuisance,mode='reduced');yr=y-q@(q.T@y)
        qg=q.T@Tg;qp=q.T@Tp
        gg=(Tg*Tg).sum(0)-(qg*qg).sum(0);pp=(Tp*Tp).sum(0)-(qp*qp).sum(0)
        gp=(Tg*Tp).sum(0)-(qg*qp).sum(0);yg=yr@Tg;yp=yr@Tp;det=gg*pp-gp*gp
        assert np.all(det>0)
        permutation_b_g=(yg*pp-yp*gp)/det;permutation_b_p=(yp*gg-yg*gp)/det
        ri=[]
        for label,tape,index,trt in (('government',permutation_b_g,1,"gov't"),('public',permutation_b_p,2,'public')):
            p_greater=float(np.mean(tape>beta[index]));p_two=float(np.mean(abs(tape)>abs(beta[index])))
            published=float(original[original['treatment']==trt]['p_ri'].iloc[0])
            assert abs(p_greater-published)<1e-12,(label,p_greater,published)
            ri.append(dict(contrast=label,permutations=len(tape),p_one_sided_greater=p_greater,p_two_sided_sharp_null=p_two,
                           published_p_one_sided=published,assignment_unit='waterway',rows=320,clusters=160))
        result=dict(study='V179_EXISTING_HUMAN_RESULT_REPLICATION',source='https://pmc.ncbi.nlm.nih.gov/articles/PMC8307295/',
             original_zip_sha256=hashlib.sha256(ZIP.read_bytes()).hexdigest(),source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             limits=limits,grain=dict(rows=320,waterways=160,audits_per_waterway=2,duplicate_keys=0,
                 treatment_changed_within_waterway=False,arm_counts=[dict(government=int(g),public=int(p),waterways=int(n)) for (g,p),n in d.drop_duplicates('wway_id').groupby(['treat_g','treat_p']).size().items()],
                 raw_rows=len(raw),raw_waterways=int(raw.wway_id.nunique()),raw_missing_in_used_variables=missing,
                 covariate_imputation='Authors use city means for missing covariates; outcomes not filled by our code.'),
             estimates=estimates,exact_export_checks=checks,randomization=ri,
             code_quality=dict(issue='Authors f_test uses pf(.95,df1,df2) instead of qf(.95,df1,df2) as the F critical value.',
                 F=fstat,cdf_threshold=wrong,quantile_threshold=right,selection_changed_for_this_outcome=False,
                 scope='Only the main full-sample water-quality specification checked; do not infer impact on other outcomes.'),
             original_R_executed=False,household_microdata_read=False,new_human_sample=False,
             ecological_simulator_validated=False,novel_prediction_confirmed=False,CT2_change=0)
        path=ROOT/'results/V179_HUMAN_POINT_AND_RANDOMIZATION_REPLICATION.json';assert not path.exists()
        path.write_text(json.dumps(result,indent=2),encoding='utf8')
        print('V179_ESTIMATES',json.dumps(estimates),flush=True)
        print('V179_RI',json.dumps(ri),flush=True)
        print('V179_GRAIN',json.dumps(result['grain']),flush=True)
        print('V179_CHECKS',json.dumps(checks),flush=True)


if __name__=='__main__':main()
