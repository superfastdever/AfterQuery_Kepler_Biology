"""Convert the author reference into exactly the agent-facing artifact format."""
import json
from pathlib import Path
import numpy as np
from reference import BASE

def format_outputs(summary,arrays):
    b=summary['best']
    outputs={
        'posterior.json':{'selection_probability':summary['selection_probability'],
                          'hypothesis_weights':summary['hypothesis_weights'],
                          'focal_joint':arrays['focal_joint'].tolist()},
        'policy.json':{'initial_restored_mask':b['restored'],'survey':b['survey'],
                       'second_stage':[{'observation_code':o,'added_mask':a} for o,a in enumerate(b['policy'])],
                       'scenario_risk':dict(zip(['early','late','persistent'],b['risk'])),
                       'worst_risk':b['worst_risk']},
        'audit.json':{'roots':[]}
    }
    for root in summary['roots']:
        C=arrays[root['id']+'-loss']; mass=arrays[root['id']+'-mass']
        outputs['audit.json']['roots'].append({
            'initial_restored_mask':root['restored'],'survey':root['survey'],'added_masks':root['additions'],
            'scenarios':{s:{'branch_probability':mass[k].tolist(),'joint_collapse':C[k].tolist()}
                         for k,s in enumerate(['early','late','persistent'])}})
    return outputs

def export(destination):
    summary=json.loads((BASE/'author/results/reference.json').read_text())
    arrays=np.load(BASE/'author/results/reference_arrays.npz',allow_pickle=False)
    outputs=format_outputs(summary,arrays)
    destination.mkdir(parents=True,exist_ok=True)
    for name,data in outputs.items():
        (destination/name).write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
    return outputs

if __name__=='__main__':
    export(BASE/'author/oracle_artifacts')
    print('Wrote three author-only oracle artifacts.')
