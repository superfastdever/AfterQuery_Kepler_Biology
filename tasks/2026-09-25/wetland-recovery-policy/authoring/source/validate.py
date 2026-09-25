"""Run independent numerical checks before Claude packages this design for Harbor."""
import copy
import itertools
import json
import math
import time
from pathlib import Path
import numpy as np
from reference import Model, BASE, BITS, STATE_X, dot, optimize, run

def logistic(x):
    return 1/(1+math.exp(-x))

def shifted(p, d):
    return logistic(math.log(p/(1-p))+d)

def scalar_row(c, m, restored, h, x, shift):
    """Scalar subset expansion, independently written without matrix factorization."""
    hyp = c['hypotheses'][m]
    row = []
    for xp in range(16):
        total = 0.
        for s in range(16):
            if s & ~x or s & ~xp:
                continue
            pr = 1.
            for i in range(4):
                if x >> i & 1:
                    p = shifted(c['survival'][h][i], hyp['survival_shift']+shift[i]+
                                ((restored >> i) & 1)*c['restoration_logodds'][h][i])
                    pr *= p if s >> i & 1 else 1-p
            for i in range(4):
                if s >> i & 1:
                    continue
                q = 1-c['external_colonization'][h][i]
                for j in range(4):
                    if s >> j & 1:
                        q *= 1-c['dispersal'][j][i]*hyp['dispersal_scale']
                pr *= (1-q) if xp >> i & 1 else q
            total += pr
        row.append(total)
    return np.array(row)

def scalar_emission(c,m,visits,water,state):
    x, h = state % 16, state//16
    probability = 1.
    for visit in visits:
        visit_p = 0.
        for w in range(2):
            p = c['weather_good_probability'][h] if w == 0 else 1-c['weather_good_probability'][h]
            for i,y in enumerate(visit):
                if y is None:
                    continue
                hit = (shifted(c['detection'][w][i],c['hypotheses'][m]['detection_shift'])
                       if (x>>i)&1 else c['false_positive'][w])
                p *= hit if y else 1-hit
            visit_p += p
        probability *= visit_p
    if water is not None:
        p = c['water_report_dry_probability'][h]
        probability *= p if water else 1-p
    return probability

def independent_forward_loss(model, weights, beliefs, root, chosen_masks):
    """Evaluate chosen policy forward with a dictionary carrying last-empty and ever-failed.

    No reference 96-state augmented matrix or backward recursion is used.
    """
    totals = np.zeros(3)
    for m in range(6):
        for k, scenario in enumerate(model.c['scenarios']):
            T1 = model.T(m, root['restored'], scenario['first'], scenario['survival_shift'])
            dist = {(s, s%16 == 0, False): weights[m]*beliefs[m,s] for s in range(32)}
            def step(dist,T):
                result = {}
                for (s,empty,failed),p in dist.items():
                    for sp in range(32):
                        empty2 = sp%16 == 0
                        key = (sp, empty2, failed or (empty and empty2))
                        result[key] = result.get(key,0.) + p*T[s,sp]
                return result
            for _ in range(3):
                dist = step(dist,T1)
            # Group branches with the same decision, but integrate observations before grouping.
            for added in sorted(set(chosen_masks)):
                codes = [o for o,a in enumerate(chosen_masks) if a == added]
                observation = sum((model.emission(m,[BITS[o%16].tolist()],o//16,
                                                 root['survey']=='intensive') for o in codes),np.zeros(32))
                branch = {key:p*observation[key[0]] for key,p in dist.items()}
                T2 = model.T(m,root['restored']|added,scenario['second'],scenario['survival_shift'])
                for _ in range(3):
                    branch = step(branch,T2)
                totals[k] += sum(p for (s,empty,failed),p in branch.items() if failed)
    return totals

def main():
    start = time.perf_counter()
    c=json.loads((BASE/'public/model.json').read_text())
    archive=json.loads((BASE/'public/archive.json').read_text())
    model=Model(c)
    checks=[]
    def record(name,error,tolerance):
        error=float(error)
        assert np.isfinite(error) and error <= tolerance,(name,error,tolerance)
        checks.append({'name':name,'max_error':error,'tolerance':tolerance,'passed':True})
    # Every input probability/scale combination must be valid.
    assert all(np.max(np.array(c['dispersal'])*m['dispersal_scale']) < 1 for m in c['hypotheses'])
    rowerr,scalarerr=0.,0.
    for m in range(6):
        for r in range(16):
            for h in range(2):
                P=model.ecological(m,r,h)
                assert np.isfinite(P).all() and P.min() >= 0
                rowerr=max(rowerr,np.max(abs(P.sum(axis=1)-1)))
                for x in (0,1,5,15):
                    scalarerr=max(scalarerr,np.max(abs(P[x]-scalar_row(c,m,r,h,x,[0]*4))))
        for k in c['scenarios']:
            P=model.ecological(m,5,1,tuple(k['survival_shift']))
            scalarerr=max(scalarerr,np.max(abs(P[11]-scalar_row(c,m,5,1,11,k['survival_shift']))))
    record('all historical transition rows normalized',rowerr,2e-14)
    record('786 ecological rows checked against independent scalar expansion',scalarerr,2e-14)
    # Sum over all 32 complete observation codes; independently handle missing observations.
    err=0.
    for m in range(6):
        for intensive in (False,True):
            summed=sum((model.emission(m,[BITS[o%16].tolist()],o//16,intensive) for o in range(32)),np.zeros(32))
            err=max(err,np.max(abs(summed-1)))
    record('observation probability normalized for both surveys',err,2e-14)
    record('missing survey and water are marginalized',np.max(abs(model.emission(2,[[None]*4],None)-1)),1e-14)
    e=model.emission(3,[[1,None,0,1],[0,0,None,1]],1)
    independent=np.array([scalar_emission(c,3,[[1,None,0,1],[0,0,None,1]],1,s) for s in range(32)])
    record('shared-weather observation scalar expansion',np.max(abs(e-independent)),2e-14)
    # Brute-force hidden state paths for a three-year record, independently of forward recursion.
    sample=copy.deepcopy(archive['records'][0]); sample['years']=sample['years'][:3]
    m=2; init=model.initial(m); T=model.T(m,0,c['historical_hydrology'])
    E=[model.emission(m,o['visits'],o['water']) for o in sample['years']]
    brute=sum(init[a]*E[0][a]*T[a,b]*E[1][b]*T[b,d]*E[2][d]
              for a,b,d in itertools.product(range(32),repeat=3))
    ll,_=model.filter_record(m,sample)
    record('three-year forward likelihood versus 32768 state paths',abs(math.exp(ll)-brute),1e-16)
    # Explicit selection sum over two hidden states.
    z=[scalar_emission(c,m,[[0]*4]*2,None,s) for s in range(32)]
    select=1-sum(init[a]*z[a]*T[a,b]*z[b] for a,b in itertools.product(range(32),repeat=2))
    record('selection probability versus 1024 state pairs',abs(select-model.selection(m)),1e-14)
    # Small robust integer policy optimization checked by enumerating every feasible table.
    fixture=np.array([[[.10,.14],[.04,.03],[.15,.09],[.07,.08]],
                      [[.16,.09],[.02,.05],[.07,.14],[.08,.06]],
                      [[.12,.13],[.04,.02],[.12,.10],[.05,.09]]])
    chosen,risks,lb,gap=optimize(fixture)
    exact=min(max(fixture[:,np.arange(4),p].sum(axis=1)) for p in itertools.product(range(2),repeat=4))
    record('robust MILP versus all 16 policies on independent fixture',abs(max(risks)-exact),1e-12)
    summary,arrays=run(model,archive)
    weights,beliefs,_,_=model.posterior(archive)
    record('posterior joint normalized',abs(arrays['focal_joint'].sum()-1),1e-14)
    for root in summary['roots']:
        C=arrays[root['id']+'-loss']; mass=arrays[root['id']+'-mass']
        assert (C >= 0).all() and (C <= mass[:,:,None]+1e-14).all()
        record(root['id']+' branch masses normalized',np.max(abs(mass.sum(axis=1)-1)),2e-14)
        record(root['id']+' certified optimization gap',root['worst_risk']-root['lower_bound'],1e-9)
    best=summary['best']
    forward=independent_forward_loss(model,weights,beliefs,best,best['policy'])
    record('full chosen-policy forward path-risk versus backward calculation',np.max(abs(forward-best['risk'])),2e-13)
    # Structural checks that distinguish valid risk objectives from common shortcuts.
    T=model.T(0,0,c['historical_hydrology']); A=model.augmented(T)
    record('already-collapsed mass remains collapsed',np.max(abs(A[64:,64:].sum(axis=1)-1)),1e-14)
    assert T[0,1:].sum()>0, 'Immigration must permit recovery after zero occupancy.'
    _,C,mass=model.coefficients(weights,beliefs,best['restored'],best['survey'])
    _,terminal,_=model.coefficients(weights,beliefs,best['restored'],best['survey'],terminal_only=True)
    adds=best['additions']; idx=[adds.index(a) for a in best['policy']]
    terminal_risk=terminal[:,np.arange(32),idx].sum(axis=1)
    unadjusted,_,_,_=model.posterior(archive,False)
    clairvoyant_bound=C.min(axis=2).sum(axis=1).max()
    branch_worst_policy=np.max(C,axis=0).argmin(axis=1)
    wrong_branch_risks=C[:,np.arange(32),branch_worst_policy].sum(axis=1)
    # Outcomes under scenario-specific policies are not implementable as one table.
    diagnostics={
        'posterior_L1_error_without_retention_correction':float(abs(weights-unadjusted).sum()),
        'terminal_empty_probability_for_chosen_policy':terminal_risk.tolist(),
        'sustained_collapse_probability_for_chosen_policy':forward.tolist(),
        'clairvoyant_scenario_specific_lower_bound':float(clairvoyant_bound),
        'nonanticipativity_gap':float(best['worst_risk']-clairvoyant_bound),
        'branchwise_worst_joint_loss_policy_risks':wrong_branch_risks.tolist(),
        'best_initial_choice':best['id'],
        'distinct_second_stage_actions':len(set(best['policy'])),
        'best_worst_risk':best['worst_risk'],
        'next_initial_choice_gap':sorted(r['worst_risk'] for r in summary['roots'])[1]-best['worst_risk']
    }
    assert diagnostics['posterior_L1_error_without_retention_correction'] > .01
    assert max(abs(terminal_risk-forward)) > .01
    assert diagnostics['nonanticipativity_gap'] > 1e-5
    assert diagnostics['distinct_second_stage_actions'] > 1
    report={'status':'passed','check_count':len(checks),'checks':checks,'diagnostics':diagnostics,
            'elapsed_seconds':time.perf_counter()-start,
            'not_run':['Docker/Harbor oracle','Docker/Harbor nop','Harbor quality check',
                       'platform anti-cheat probe','frontier-agent difficulty trials','human review'],
            'scope':'Local scientific prototype validation, not submission acceptance.'}
    (BASE/'author/results').mkdir(exist_ok=True)
    (BASE/'author/results/validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'checks':len(checks),'seconds':report['elapsed_seconds'],'diagnostics':diagnostics},indent=2))

if __name__=='__main__':
    main()
