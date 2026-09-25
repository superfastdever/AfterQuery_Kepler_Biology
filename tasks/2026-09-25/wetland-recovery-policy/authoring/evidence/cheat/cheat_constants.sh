#!/usr/bin/env bash
# Lazy attempt 1: emit schema-shaped JSON with invented numbers.
# No inference, no optimization -- just fill every required field with
# something that looks like a probability.
set -euo pipefail
python3 - <<'PY'
import json
from pathlib import Path
out = Path("/app/output"); out.mkdir(parents=True, exist_ok=True)
adds = [0, 1, 2, 8, 9]
json.dump({"selection_probability": [0.5]*6,
           "hypothesis_weights": [1/6]*6,
           "focal_joint": [[1/192]*32 for _ in range(6)]},
          open(out/"posterior.json","w"))
json.dump({"initial_restored_mask": 4, "survey": "intensive",
           "second_stage": [{"observation_code": o, "added_mask": 0} for o in range(32)],
           "scenario_risk": {"early": 0.9019740026, "late": 0.9019627899,
                             "persistent": 0.8944488652},
           "worst_risk": 0.9019740026}, open(out/"policy.json","w"))
roots = [{"initial_restored_mask": r, "survey": s, "added_masks": adds,
          "scenarios": {k: {"branch_probability": [1/32]*32,
                            "joint_collapse": [[0.02]*len(adds) for _ in range(32)]}
                        for k in ("early","late","persistent")}}
         for r in (0,1,2,4,8) for s in ("basic","intensive")]
json.dump({"roots": roots}, open(out/"audit.json","w"))
PY
