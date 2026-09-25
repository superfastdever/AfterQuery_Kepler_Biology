"""Author reference: exact finite-state inference and deterministic robust policy search.

This is validation support for Claude, not an agent-visible starter solution.
"""
import itertools
import json
import math
import time
from functools import lru_cache
from pathlib import Path
import numpy as np
from scipy.optimize import milp, Bounds, LinearConstraint, linprog
from scipy.special import expit, logit

BASE = Path(__file__).resolve().parents[1]
BITS = np.array([[(x >> i) & 1 for i in range(4)] for x in range(16)])
STATE_X = np.tile(np.arange(16), 2)
STATE_H = np.repeat(np.arange(2), 16)

def dot(a, b):
    # Explicit contraction avoids platform-specific BLAS floating-status warnings.
    if np.ndim(a) == 1 and np.ndim(b) == 1:
        return np.einsum('i,i->', a, b)
    if np.ndim(a) == 1:
        return np.einsum('i,ij->j', a, b)
    if np.ndim(b) == 1:
        return np.einsum('ij,j->i', a, b)
    return np.einsum('ij,jk->ik', a, b)

def cube(a):
    return dot(dot(a, a), a)

class Model:
    def __init__(self, config):
        self.c = config
        self.ms = config['hypotheses']

    def initial(self, m):
        p = expit(logit(np.array(self.c['initial_occupancy'])) + self.ms[m]['initial_shift'])
        return np.concatenate([self.c['initial_hydrology'][h] *
                               np.prod(np.where(BITS, p[h], 1-p[h]), axis=1) for h in range(2)])

    @lru_cache(None)
    def ecological(self, m, restored, h, forecast_shift=(0., 0., 0., 0.)):
        """P(x'|x,h'), marginalize surviving source set BEFORE colonization product."""
        c, hypothesis = self.c, self.ms[m]
        surv = expit(logit(np.array(c['survival'][h])) + hypothesis['survival_shift'] + np.array(forecast_shift) +
                     BITS[restored] * np.array(c['restoration_logodds'][h]))
        links = np.array(c['dispersal']) * hypothesis['dispersal_scale']
        ext = np.array(c['external_colonization'][h])
        colon = 1 - (1-ext)[None, :] * np.prod(1-BITS[:, :, None]*links[None, :, :], axis=1)
        end_p = np.where(BITS, 1.0, colon)
        arrival = np.prod(np.where(BITS[None, :, :], end_p[:, None, :], 1-end_p[:, None, :]), axis=2)
        survive_p = BITS * surv
        source = np.prod(np.where(BITS[None, :, :], survive_p[:, None, :], 1-survive_p[:, None, :]), axis=2)
        return dot(source, arrival)

    @lru_cache(None)
    def transition(self, m, restored, hydro_key, forecast_shift):
        hydro = np.array(hydro_key).reshape(2, 2)
        return np.block([[hydro[h, hp] * self.ecological(m, restored, hp, forecast_shift)
                          for hp in range(2)] for h in range(2)])

    def T(self, m, restored, hydro, forecast_shift=(0., 0., 0., 0.)):
        return self.transition(m, restored, tuple(np.asarray(hydro).ravel()), tuple(forecast_shift))

    def emission(self, m, visits, water=None, intensive=False):
        c = self.c
        p = expit(logit(np.array(c['intensive_detection'] if intensive else c['detection']))
                  + self.ms[m]['detection_shift'])
        fp = c['intensive_false_positive'] if intensive else c['false_positive']
        result = np.ones(32)
        for visit in visits:
            by_weather = []
            for w in range(2):
                # w=0 is good survey weather; all four patches share the same w.
                probs = np.where(BITS, p[w], fp[w])
                factors = np.ones_like(probs)
                for i, y in enumerate(visit):
                    if y is not None:
                        factors[:, i] = probs[:, i] if y == 1 else 1-probs[:, i]
                by_weather.append(factors.prod(axis=1))
            result *= np.concatenate([c['weather_good_probability'][h]*by_weather[0] +
                                      (1-c['weather_good_probability'][h])*by_weather[1] for h in range(2)])
        if water is not None:
            dry = np.repeat(c['water_report_dry_probability'], 16)
            result *= dry if water else 1-dry
        return result

    def selection(self, m):
        zero = self.emission(m, [[0]*4]*2)
        initial_zero = self.initial(m) * zero
        return 1 - dot(dot(initial_zero, self.T(m, 0, self.c['historical_hydrology'])), zero)

    def filter_record(self, m, record):
        b, ll = self.initial(m), 0.0
        for t, obs in enumerate(record['years']):
            if t:
                b = dot(b, self.T(m, 0, self.c['historical_hydrology']))
            b *= self.emission(m, obs['visits'], obs['water'])
            z = b.sum()
            ll += math.log(z)
            b /= z
        return ll, b

    def posterior(self, archive, adjust_selection=True):
        logweights, focal = [], []
        selection = [self.selection(m) for m in range(len(self.ms))]
        for m, hyp in enumerate(self.ms):
            lw = math.log(hyp['prior'])
            for record in archive['records']:
                ll, b = self.filter_record(m, record)
                lw += ll - (math.log(selection[m]) if adjust_selection else 0)
                if record['id'] == archive['focal_id']:
                    focal.append(b)
            logweights.append(lw)
        weights = np.exp(np.array(logweights)-max(logweights))
        weights /= weights.sum()
        return weights, np.array(focal), np.array(logweights), np.array(selection)

    def augmented(self, T):
        """r=0 nonempty last census, r=1 empty last census, r=2 collapse already occurred."""
        A = np.zeros((96, 96))
        for r in range(3):
            for xp in range(32):
                rp = 2 if r == 2 else (min(2, r+1) if STATE_X[xp] == 0 else 0)
                A[r*32:(r+1)*32, rp*32+xp] = T[:, xp]
        return A

    def first_actions(self):
        return [(r, s) for r in [0, 1, 2, 4, 8] for s in ['basic', 'intensive']]

    def additions(self, restored, survey):
        cost = np.array(self.c['project_cost'])
        return [a for a in range(16) if not a & restored and int(BITS[a].sum()) <= 2
                and BITS[a | restored] @ cost + self.c['survey_cost'][survey] <= self.c['budget']]

    def coefficients(self, weights, beliefs, restored, survey, terminal_only=False):
        """C[scenario, observation, addition] is JOINT probability of branch and collapse."""
        adds = self.additions(restored, survey)
        C, mass = np.zeros((3, 32, len(adds))), np.zeros((3, 32))
        final = np.zeros(96)
        if terminal_only:
            final.reshape(3, 32)[:, STATE_X == 0] = 1
        else:
            final[64:] = 1
        for m in range(len(self.ms)):
            start = np.zeros((3, 32))
            for s in range(32):
                start[int(STATE_X[s] == 0), s] = beliefs[m, s]
            obs_matrix = np.array([np.tile(self.emission(m, [BITS[o % 16].tolist()], o//16,
                                                        survey == 'intensive'), 3) for o in range(32)])
            for k, scenario in enumerate(self.c['scenarios']):
                A = self.augmented(self.T(m, restored, scenario['first'], scenario['survival_shift']))
                b = dot(start.ravel(), cube(A))
                branches = obs_matrix * b[None, :] * weights[m]
                mass[k] += branches.sum(axis=1)
                for j, addition in enumerate(adds):
                    A2 = self.augmented(self.T(m, restored | addition, scenario['second'], scenario['survival_shift']))
                    value = dot(cube(A2), final)
                    C[k, :, j] += dot(branches, value)
        return adds, C, mass

def optimize(C):
    K, O, J = C.shape
    n = O*J
    scale = 1e6
    obj = np.zeros(n+1)
    obj[-1] = 1
    choose = np.zeros((O, n+1))
    for o in range(O):
        choose[o, o*J:(o+1)*J] = 1
    risk = np.column_stack([scale*C.reshape(K, n), -np.ones(K)])
    result = milp(obj, integrality=np.r_[np.ones(n), 0], bounds=Bounds(np.zeros(n+1), np.r_[np.ones(n),scale]),
                  constraints=[LinearConstraint(choose, 1, 1), LinearConstraint(risk, -np.inf, 0)],
                  options={'mip_rel_gap': 1e-10, 'time_limit': 120})
    if not result.success:
        raise RuntimeError(result.message)
    chosen = result.x[:-1].reshape(O, J).argmax(axis=1)
    risks = C[:, np.arange(O), chosen].sum(axis=1)
    return chosen, risks, float(result.mip_dual_bound)/scale, float(result.mip_gap)

def relaxation_bound(C):
    """Best lower bound available from a scenario mixture.

    For any admissible policy, the worst scenario risk is at least any weighted
    average of the three scenario risks, and that average is at least

        L(w) = sum_o min_a sum_k w[k] C[k,o,a].

    The tightest such bound is max over w on the simplex, which is the value of
    the randomized relaxation: the dual of the minimax LP. It sits strictly
    below the deterministic optimum whenever committing to one action per
    observation code costs something, and that difference is the price of
    forbidding randomization.

    Returns the maximizing weights and the bound they achieve.
    """
    K, O, J = C.shape
    n = K + O                                   # w[0..K-1], mu[0..O-1]
    obj = np.zeros(n)
    obj[K:] = -1.0                              # linprog minimizes
    rows = np.zeros((O*J, n))
    r = 0
    for o in range(O):
        for a in range(J):
            rows[r, K+o] = 1.0                  # mu_o
            rows[r, :K] = -C[:, o, a]           # - w . C[:,o,a]
            r += 1
    simplex = np.zeros((1, n))
    simplex[0, :K] = 1.0
    result = linprog(obj, A_ub=rows, b_ub=np.zeros(O*J), A_eq=simplex, b_eq=[1.0],
                     bounds=[(0, None)]*K + [(None, None)]*O, method='highs')
    if not result.success:
        raise RuntimeError(result.message)
    w = np.clip(result.x[:K], 0.0, None)
    w = w/w.sum()
    return w, evaluate_bound(C, w)

def evaluate_bound(C, w):
    """L(w), evaluated directly rather than read off the solver."""
    K, O, J = C.shape
    return float(sum(np.min(dot(np.asarray(w, dtype=float), C[:, o, :])) for o in range(O)))


def run(model, archive):
    weights, beliefs, logweights, selection = model.posterior(archive)
    roots, arrays = [], {}
    for restored, survey in model.first_actions():
        adds, C, mass = model.coefficients(weights, beliefs, restored, survey)
        chosen, risks, bound, gap = optimize(C)
        weights_mix, relaxed = relaxation_bound(C)
        key = f'{restored}-{survey}'
        roots.append({'id': key, 'restored': restored, 'survey': survey, 'additions': adds,
                      'policy': [adds[x] for x in chosen], 'risk': risks.tolist(),
                      'worst_risk': float(max(risks)), 'lower_bound': bound, 'mip_gap': gap,
                      'scenario_weights': weights_mix.tolist(), 'relaxation_bound': relaxed,
                      'determinism_price': float(max(risks)) - relaxed})
        arrays[key + '-loss'] = C
        arrays[key + '-mass'] = mass
    best = min(roots, key=lambda x: x['worst_risk'])
    summary = {'hypothesis_weights': weights.tolist(), 'selection_probability': selection.tolist(),
               'log_unnormalized_weights': logweights.tolist(), 'roots': roots, 'best': best}
    arrays['focal_conditional'] = beliefs
    arrays['focal_joint'] = weights[:, None]*beliefs
    return summary, arrays

if __name__ == '__main__':
    started = time.perf_counter()
    model = Model(json.loads((BASE/'public/model.json').read_text()))
    archive = json.loads((BASE/'public/archive.json').read_text())
    summary, arrays = run(model, archive)
    summary['elapsed_seconds'] = time.perf_counter()-started
    dest = BASE/'author/results'
    dest.mkdir(exist_ok=True)
    (dest/'reference.json').write_text(json.dumps(summary, indent=2)+'\n')
    np.savez_compressed(dest/'reference_arrays.npz', **arrays)
    print(json.dumps({'seconds': summary['elapsed_seconds'], 'weights': summary['hypothesis_weights'],
                      'best': summary['best']}, indent=2))
