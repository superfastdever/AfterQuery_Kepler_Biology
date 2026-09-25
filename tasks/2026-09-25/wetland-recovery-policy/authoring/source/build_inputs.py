"""Deterministic, original synthetic benchmark inputs. Author-only: never COPY into agent image."""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
PUBLIC = BASE / 'public'

def build():
    PUBLIC.mkdir(parents=True, exist_ok=True)
    model = {
        'version': '1.0', 'synthetic': True,
        'sites': ['Alder', 'Birch', 'Cedar', 'Dogwood'],
        'historical_hydrology': [[0.73, 0.27], [0.38, 0.62]],
        'initial_hydrology': [0.62, 0.38],
        'initial_occupancy': [[0.42, 0.32, 0.36, 0.25], [0.16, 0.29, 0.14, 0.30]],
        'survival': [[0.80, 0.53, 0.73, 0.49], [0.24, 0.61, 0.31, 0.66]],
        'restoration_logodds': [[0.35, 1.00, 0.50, 0.85], [1.45, 0.40, 1.10, 0.45]],
        'external_colonization': [[0.030, 0.020, 0.040, 0.015], [0.006, 0.018, 0.004, 0.022]],
        'dispersal': [[0, 0.36, 0.12, 0.03], [0.14, 0, 0.25, 0.09],
                      [0.06, 0.18, 0, 0.32], [0.03, 0.10, 0.21, 0]],
        'weather_good_probability': [0.76, 0.34],
        'detection': [[0.74, 0.68, 0.79, 0.63], [0.29, 0.25, 0.34, 0.22]],
        'false_positive': [0.012, 0.035],
        'intensive_detection': [[0.95, 0.93, 0.96, 0.92], [0.76, 0.71, 0.80, 0.69]],
        'intensive_false_positive': [0.003, 0.008],
        'water_report_dry_probability': [0.16, 0.83],
        'hypotheses': [
            {'id': 'M0', 'prior': .18, 'survival_shift': -.25, 'dispersal_scale': .65, 'detection_shift': -.20, 'initial_shift': -.35},
            {'id': 'M1', 'prior': .16, 'survival_shift': -.25, 'dispersal_scale': 1.35, 'detection_shift': .20, 'initial_shift': .25},
            {'id': 'M2', 'prior': .18, 'survival_shift': .20, 'dispersal_scale': .65, 'detection_shift': .20, 'initial_shift': -.35},
            {'id': 'M3', 'prior': .16, 'survival_shift': .20, 'dispersal_scale': 1.35, 'detection_shift': -.20, 'initial_shift': .25},
            {'id': 'M4', 'prior': .17, 'survival_shift': -.05, 'dispersal_scale': 1.00, 'detection_shift': -.35, 'initial_shift': .45},
            {'id': 'M5', 'prior': .15, 'survival_shift': .05, 'dispersal_scale': 1.00, 'detection_shift': .35, 'initial_shift': -.45}
        ],
        'scenarios': [
            {'id': 'early', 'first': [[.56, .44], [.24, .76]], 'second': [[.86, .14], [.65, .35]],
             'survival_shift': [-.30, .30, -.35, .25]},
            {'id': 'late', 'first': [[.89, .11], [.67, .33]], 'second': [[.36, .64], [.12, .88]],
             'survival_shift': [.05, -.65, .00, -.70]},
            {'id': 'persistent', 'first': [[.70, .30], [.40, .60]], 'second': [[.70, .30], [.40, .60]],
             'survival_shift': [-.05, -.05, -.05, -.05]}
        ],
        'project_cost': [2, 3, 2, 3], 'survey_cost': {'basic': 0, 'intensive': 1},
        'budget': 7, 'first_project_limit': 1, 'second_project_limit': 2,
        'planning_years': 6, 'decision_year': 3,
        'archive_selection': 'At least one positive patch detection across both visits in years 0 and 1.',
        'selection_prior_semantics': 'Draw one hypothesis from the stated prior, then independently rejection-sample each complete network record until its selection event holds. No count of rejected records is observed.'
    }
    (PUBLIC / 'model.json').write_text(json.dumps(model, indent=2) + '\n')
    return model

if __name__ == '__main__':
    build()
