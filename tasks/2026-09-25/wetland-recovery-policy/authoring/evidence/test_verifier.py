"""Content-level mutation tests; these are not the Harbor oracle/nop trials."""
import copy
import json
import tempfile
from pathlib import Path
import numpy as np
from reference import BASE,Model,run,dot,BITS
from export_outputs import export,format_outputs
from check_outputs import evaluate

def main():
    original=export(BASE/'author/oracle_artifacts')
    truth=BASE/'author/results'
    checks=[]
    def trial(name,files,expected):
        with tempfile.TemporaryDirectory(prefix='kepler-verifier-') as tmp:
            dest=Path(tmp)
            for name_,data in files.items():
                (dest/name_).write_text(data if isinstance(data,str) else json.dumps(data))
            try:
                evaluate(dest,truth); passed=True
            except Exception:
                passed=False
            assert passed==expected,(name,passed,expected)
            checks.append({'name':name,'expected_reward':int(expected),'observed_reward':int(passed),'passed':True})
    trial('valid reference artifacts',original,True)
    trial('empty output directory',{},False)
    trial('files with empty objects',{k:{} for k in original},False)
    p=copy.deepcopy(original); p['posterior.json']['hypothesis_weights'][0]='0.3'
    trial('numeric strings',p,False)
    p=copy.deepcopy(original); p['posterior.json']['hypothesis_weights'][0]=True
    trial('booleans as probabilities',p,False)
    p=copy.deepcopy(original); p['policy.json']['worst_risk']=float('nan')
    trial('NaN',p,False)
    p=copy.deepcopy(original); p['policy.json']='{"survey":"basic","survey":"intensive"}'
    trial('duplicate JSON keys',p,False)
    p=copy.deepcopy(original); p['policy.json']['second_stage'].pop()
    trial('missing policy branch',p,False)
    p=copy.deepcopy(original); p['policy.json']['second_stage'][1]['observation_code']=0
    trial('duplicate observation branch',p,False)
    p=copy.deepcopy(original); p['policy.json']['second_stage'][0]['added_mask']=15
    trial('infeasible spending and repeated restoration',p,False)
    p=copy.deepcopy(original); p['policy.json']['second_stage']=[{'observation_code':o,'added_mask':0} for o in range(32)]
    trial('do nothing after survey but claim optimal risks',p,False)
    p=copy.deepcopy(original); p['audit.json']['roots'].pop()
    trial('missing counterfactual audit root',p,False)
    p=copy.deepcopy(original); p['audit.json']['roots'][0]['scenarios']['early']['joint_collapse'][0][0] += .001
    trial('plausible but wrong joint loss',p,False)
    model=Model(json.loads((BASE/'public/model.json').read_text()))
    archive=json.loads((BASE/'public/archive.json').read_text())
    w,b,_,_=model.posterior(archive,False)
    p=copy.deepcopy(original); p['posterior.json']['hypothesis_weights']=w.tolist(); p['posterior.json']['focal_joint']=(w[:,None]*b).tolist()
    trial('omit archive selection correction',p,False)
    p=copy.deepcopy(original)
    for root in p['audit.json']['roots']:
        for s in root['scenarios'].values():
            s['joint_collapse']=(np.array(s['joint_collapse'])/np.array(s['branch_probability'])[:,None]).tolist()
    trial('conditional losses substituted for joint losses',p,False)
    # The optimality certificate: a separate derivation from the policy itself.
    p=copy.deepcopy(original); del p['policy.json']['scenario_weights']
    trial('certificate absent',p,False)
    p=copy.deepcopy(original); p['policy.json']['scenario_weights']=[1.0,0.0,0.0]
    trial('certificate concentrated on one scenario',p,False)
    p=copy.deepcopy(original); p['policy.json']['scenario_weights']=[1/3,1/3,1/3]
    trial('uniform scenario weights',p,False)
    p=copy.deepcopy(original); p['policy.json']['scenario_weights']=[0.7,0.4,-0.1]
    trial('negative scenario weight',p,False)
    p=copy.deepcopy(original); p['policy.json']['scenario_weights']=[0.6,0.3,0.0]
    trial('scenario weights not summing to one',p,False)
    p=copy.deepcopy(original)
    _gold=json.loads((truth/'reference.json').read_text())
    other=[r for r in _gold['roots'] if r['id']!=_gold['best']['id']][0]
    p['policy.json']['scenario_weights']=other['scenario_weights']
    trial('certificate from a different initial choice',p,False)

    # Entire internally consistent outputs from plausible but scientifically wrong models.
    class IndependentWeather(Model):
        def emission(self,m,visits,water=None,intensive=False):
            out=super().emission(m,[],water,intensive)
            for visit in visits:
                for i,y in enumerate(visit):
                    one=[None]*4;one[i]=y
                    out*=super().emission(m,[one],None,intensive)
            return out
    class IndependentDestinations(Model):
        def ecological(self,m,restored,h,forecast_shift=(0.,0.,0.,0.)):
            original=super().ecological(m,restored,h,forecast_shift)
            marg=dot(original,BITS)
            return np.prod(np.where(BITS[None,:,:],marg[:,None,:],1-marg[:,None,:]),axis=2)
    class FinalCensusOnly(Model):
        def coefficients(self,weights,beliefs,restored,survey,terminal_only=False):
            return super().coefficients(weights,beliefs,restored,survey,terminal_only=True)
    for label,cls in [('integrate shared survey weather separately for each patch',IndependentWeather),
                      ('factorize dependent destination occupancy after matching marginals',IndependentDestinations),
                      ('optimize final emptiness instead of sustained collapse',FinalCensusOnly)]:
        summary,wrong_arrays=run(cls(model.c),archive)
        trial(label,format_outputs(summary,wrong_arrays),False)
    # An alternate, still admissible near-optimal policy must be accepted.
    gold=json.loads((truth/'reference.json').read_text()); best=gold['best']
    arrays=np.load(truth/'reference_arrays.npz',allow_pickle=False); C=arrays[best['id']+'-loss']
    indices=np.array([best['additions'].index(a) for a in best['policy']])
    alternative=None
    for o in range(32):
        for j,a in enumerate(best['additions']):
            if j==indices[o]:continue
            ii=indices.copy();ii[o]=j
            risk=C[:,np.arange(32),ii].sum(axis=1)
            if max(risk)<=best['worst_risk']+1e-5:
                alternative=(o,a,risk);break
        if alternative:break
    assert alternative is not None
    o,a,risk=alternative
    p=copy.deepcopy(original);p['policy.json']['second_stage'][o]['added_mask']=a
    p['policy.json']['scenario_risk']=dict(zip(['early','late','persistent'],risk.tolist()))
    p['policy.json']['worst_risk']=float(max(risk))
    trial('different feasible policy within stated tolerance',p,True)
    (truth/'verifier_validation.json').write_text(json.dumps({'check_count':len(checks),'checks':checks,
                                                            'scope':'Local artifact checks, not Harbor execution.'},indent=2)+'\n')
    print(f'{len(checks)} artifact checker tests passed, including an alternative valid policy.')

if __name__=='__main__':main()
