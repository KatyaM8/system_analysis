import json
from typing import Dict, List, Tuple, Any


def _norm_id(s: str) -> str:
    s = s.strip().lower().replace("ё", "е")
    for ch in [" ", "-", "_"]:
        s = s.replace(ch, "")
    return s


def _build_terms_map(var_json: str) -> Dict[str, List[Tuple[float, float]]]:

    data = json.loads(var_json)
    if not isinstance(data, dict) or len(data) == 0:
        raise ValueError("Некорректный json с термами: ожидался объект-словарь")

    first_key = next(iter(data.keys()))
    terms_list = data[first_key]

    terms: Dict[str, List[Tuple[float, float]]] = {}
    for obj in terms_list:
        term_id = _norm_id(obj["id"])
        pts = [(float(x), float(y)) for x, y in obj["points"]]
        pts.sort(key=lambda p: p[0])
        terms[term_id] = pts
    return terms


def _match_term_id(terms_map: Dict[str, Any], raw_id: str) -> str:

    rid = _norm_id(raw_id)
    if rid in terms_map:
        return rid

    for key in terms_map.keys():
        if rid in key or key in rid:
            return key

    return rid


def _mu_piecewise_linear(x: float, points: List[Tuple[float, float]]) -> float:
    if not points:
        return 0.0

    if x <= points[0][0]:
        return float(points[0][1])
    if x >= points[-1][0]:
        return float(points[-1][1])

    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        if x1 <= x <= x2:
            if x2 == x1:
                #на случай одинаковых x
                return float(max(y1, y2))
            k = (y2 - y1) / (x2 - x1)
            y = y1 + k * (x - x1)
            if y < 0:
                y = 0.0
            if y > 1:
                y = 1.0
            return float(y)
    return 0.0


def main(temp_mf_json: str, control_mf_json: str, rules_json: str, t: float) -> float:

    temp_terms = _build_terms_map(temp_mf_json)
    control_terms = _build_terms_map(control_mf_json)

    rules = json.loads(rules_json)
    if not isinstance(rules, list):
        raise ValueError("Некорректный json с правилами: ожидался список")

    mu_temp: Dict[str, float] = {}
    for term_id, pts in temp_terms.items():
        mu_temp[term_id] = _mu_piecewise_linear(float(t), pts)

    all_s = [x for pts in control_terms.values() for (x, _) in pts]
    if not all_s:
        return 0.0
    s_min = float(min(all_s))
    s_max = float(max(all_s))

    step = 0.01
    n_steps = int(round((s_max - s_min) / step)) + 1
    s_grid = [s_min + i * step for i in range(n_steps)]


    agg_mu = [0.0 for _ in s_grid]

    for rule in rules:
        if not (isinstance(rule, list) or isinstance(rule, tuple)) or len(rule) != 2:
            continue

        raw_temp_term, raw_control_term = rule[0], rule[1]
        temp_term = _match_term_id(temp_terms, str(raw_temp_term))
        control_term = _match_term_id(control_terms, str(raw_control_term))

        alpha = mu_temp.get(temp_term, 0.0)
        if alpha <= 0.0:
            continue
        if control_term not in control_terms:
            continue

        control_pts = control_terms[control_term]
        for i, s in enumerate(s_grid):
            mu_out = _mu_piecewise_linear(s, control_pts)
            clipped = min(alpha, mu_out)
            if clipped > agg_mu[i]:
                agg_mu[i] = clipped

    max_mu = max(agg_mu) if agg_mu else 0.0
    for s, mu in zip(s_grid, agg_mu):
        if mu == max_mu:
            return float(s)

    return float(s_min)


