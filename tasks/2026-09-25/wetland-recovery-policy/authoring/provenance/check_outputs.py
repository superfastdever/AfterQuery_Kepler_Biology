"""Prototype sealed content checker. Does not execute or import agent artifacts.

Claude must package it with trusted reference.json and reference_arrays.npz in /tests,
wrap in pytest/CTRF and a fail-closed reward script, and test through Harbor.
"""
import json
import sys
from pathlib import Path
import numpy as np

SCENARIOS=['early','late','persistent']

def require(ok,message):
    if not ok:
        raise ValueError(message)

def strict_load(path):
    def pairs(items):
        result={}
        for key,val in items:
            require(key not in result,'Duplicate JSON key')
            result[key]=val
        return result
    def invalid(value):
        raise ValueError('Nonfinite JSON literal')
    return json.loads(path.read_text(),object_pairs_hook=pairs,parse_constant=invalid)

def integers(values):
    return isinstance(values,list) and all(type(x) is int for x in values)

def numeric(value):
    if isinstance(value,list):
        return all(numeric(x) for x in value)
    return type(value) in (int,float) and np.isfinite(value)

def probability(value,shape):
    require(numeric(value),'Probability must be finite numeric data, not strings or booleans')
    a=np.asarray(value,dtype=float)
    require(a.shape==shape,'Incorrect array shape')
    require(np.all((a>=-1e-12)&(a<=1+1e-12)),'Probability outside [0,1]')
    return a

def close(actual,expected,tol=1e-6):
    require(np.max(np.abs(np.asarray(actual)-np.asarray(expected)))<=tol,'Scientific numeric mismatch')

def evaluate(folder,truth):
    gold=strict_load(truth/'reference.json')
    with np.load(truth/'reference_arrays.npz',allow_pickle=False) as loaded:
        arrays={k:loaded[k] for k in loaded.files}
    roots={r['id']:r for r in gold['roots']}
    gold['roots_by_id']=roots
    post=strict_load(folder/'posterior.json'); policy=strict_load(folder/'policy.json'); audit=strict_load(folder/'audit.json')
    w=probability(post['hypothesis_weights'],(6,))
    q=probability(post['selection_probability'],(6,))
    joint=probability(post['focal_joint'],(6,32))
    close(w.sum(),1,1e-8); close(joint.sum(),1,1e-8); close(joint.sum(axis=1),w,1e-8)
    close(w,gold['hypothesis_weights']); close(q,gold['selection_probability']); close(joint,arrays['focal_joint'])
    r=policy['initial_restored_mask']; survey=policy['survey']
    require(type(r) is int and r in [0,1,2,4,8],'Illegal initial restoration')
    require(survey in ['basic','intensive'],'Unknown survey')
    key=f'{r}-{survey}'; root=roots[key]
    require(isinstance(policy['second_stage'],list) and len(policy['second_stage'])==32,'Need 32 policy branches')
    decision={}
    for branch in policy['second_stage']:
        o,a=branch['observation_code'],branch['added_mask']
        require(type(o) is int and 0<=o<32 and o not in decision,'Duplicate or invalid observation')
        require(type(a) is int and a in root['additions'],'Infeasible second-stage action')
        decision[o]=root['additions'].index(a)
    C=arrays[key+'-loss']
    risk=C[:,np.arange(32),[decision[o] for o in range(32)]].sum(axis=1)
    reported=probability([policy['scenario_risk'][s] for s in SCENARIOS],(3,))
    worst=probability(policy['worst_risk'],())
    close(reported,risk); close(worst,float(max(risk)))
    require(max(risk)<=gold['best']['worst_risk']+1e-5,'Policy is outside optimality tolerance')
    mix=probability(policy['scenario_weights'],(3,))
    close(mix.sum(),1,1e-8)
    bound=float(sum(np.min(np.einsum('k,kj->j',mix,C[:,o,:])) for o in range(32)))
    require(bound>=gold['roots_by_id'][key]['relaxation_bound']-1e-9,
            'Scenario weights do not attain the best available lower bound')
    require(isinstance(audit['roots'],list) and len(audit['roots'])==10,'Need all ten audit roots')
    seen=set()
    for item in audit['roots']:
        ar,sv=item['initial_restored_mask'],item['survey']
        require(type(ar) is int and ar in [0,1,2,4,8] and sv in ['basic','intensive'],'Invalid audit root')
        k=f'{ar}-{sv}'
        require(k not in seen,'Duplicate audit root'); seen.add(k)
        adds=item['added_masks']
        require(integers(adds) and adds==roots[k]['additions'],'Missing or misordered feasible additions')
        for si,s in enumerate(SCENARIOS):
            branch=probability(item['scenarios'][s]['branch_probability'],(32,))
            loss=probability(item['scenarios'][s]['joint_collapse'],(32,len(adds)))
            close(branch.sum(),1,1e-8)
            require(np.all(loss<=branch[:,None]+1e-8),'Joint loss exceeds branch probability')
            close(branch,arrays[k+'-mass'][si]); close(loss,arrays[k+'-loss'][si])
    return {'reward':1,'evaluated_risk':risk.tolist(),'worst_risk':float(max(risk))}

if __name__=='__main__':
    base=Path(__file__).resolve().parent
    try:
        result=evaluate(Path(sys.argv[1]),base/'results')
    except Exception as error:
        result={'reward':0,'reason':f'{type(error).__name__}: {error}'}
    print(json.dumps(result))
    sys.exit(0 if result['reward'] else 1)
