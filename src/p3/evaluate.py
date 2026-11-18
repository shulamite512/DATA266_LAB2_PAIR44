"""3.3 evaluation: run the 15 scenarios (with and without critique) and the 10 red-team
cases, apply each case's automatic rubric, and compute the four measurements."""
import json
import os
import statistics

import pandas as pd

INPUTS = os.environ.get("P3_INPUTS", "data/p3/inputs")


def _resolve(img):
    return os.path.join(INPUTS, img) if img else None


def check_rubric(case, st):
    """Automatic part of the rubric. Returns (pass, reasons)."""
    r, fails = case.get("auto", {}), []
    if "expect_status" in r and st.status not in r["expect_status"]:
        fails.append(f"status {st.status} not in {r['expect_status']}")
    if "expect_route" in r and st.route not in r["expect_route"]:
        fails.append(f"route {st.route} not in {r['expect_route']}")
    text = (st.message + " " + json.dumps(st.vision)).lower()
    for kw_group in r.get("answer_contains_any", []):
        if not any(k.lower() in text for k in kw_group):
            fails.append(f"answer missing one of {kw_group}")
    prompts = " ".join(p["prompt"] + " " + p["edit_instruction"] for p in st.prompts).lower()
    for bad in r.get("prompt_must_not_contain", []):
        if bad.lower() in prompts:
            fails.append(f"prompt contains '{bad}'")
    if "min_clip" in r and st.critiques:
        best = max(c["clip_cosine"] for c in st.critiques)
        if best < r["min_clip"]:
            fails.append(f"CLIP {best:.3f} < {r['min_clip']}")
    if any(t.error for t in st.trace) and st.status != "error":
        fails.append("an agent raised an error")
    return (not fails), fails


def run_cases(system, cases, use_critique=True, tag=""):
    rows, states = [], {}
    for case in cases:
        img = _resolve(case.get("image"))
        if case.get("requires_input") and img and not os.path.exists(img):
            rows.append({"id": case["id"], "skipped": True, "reason": f"missing {img}"})
            continue
        st = system.run(case["request"], img, use_critique=use_critique, request_id=f"{case['id']}{tag}")
        ok, why = check_rubric(case, st)
        states[case["id"]] = st
        rows.append({"id": case["id"], "category": case["category"], "request": case["request"],
                     "image": case.get("image", ""), "status": st.status, "route": st.route, "revisions": st.revisions,
                     "auto_pass": ok, "fail_reasons": "; ".join(why), "seconds": st.total_seconds,
                     "final_image": st.final_image_path, "message": st.message[:300], "skipped": False})
    return pd.DataFrame(rows), states


def critic_decisions(states):
    rows = []
    for sid, st in states.items():
        for c in st.critiques:
            g = st.generations[c["attempt"]]
            rows.append({"scenario": sid, "attempt": c["attempt"], "image": g["image_path"], "prompt": g["prompt"],
                         "critic_decision": c["decision"], "clip_cosine": c["clip_cosine"], "human_decision": ""})
    return pd.DataFrame(rows)


def critic_agreement(labels_path="eval/p3_critic_labels.csv"):
    if not os.path.exists(labels_path):
        return None
    d = pd.read_csv(labels_path, keep_default_na=False)
    d = d[d["human_decision"].str.strip() != ""]
    if d.empty:
        return None
    norm = lambda s: "accept" if s.strip().lower().startswith("acc") else "revise"
    agree = (d["critic_decision"].map(norm) == d["human_decision"].map(norm))
    return {"n_decisions": len(d), "critic_agreement": round(float(agree.mean()), 3)}


def human_agreement(path="eval/p3_human_judgements.csv"):
    """columns: id, rater_A (pass/fail), rater_B (pass/fail), resolved (pass/fail), resolution_note"""
    if not os.path.exists(path):
        return None
    h = pd.read_csv(path, keep_default_na=False)
    h = h[(h.rater_A != "") & (h.rater_B != "")]
    if h.empty:
        return None
    norm = lambda s: s.strip().lower().startswith("p")
    a, b = h.rater_A.map(norm), h.rater_B.map(norm)
    # `resolved` is only filled where the raters disagreed; elsewhere both raters' verdict stands
    res = [norm(r) if str(r).strip() else x for r, x in zip(h.resolved, a)] if "resolved" in h else list(a & b)
    res = pd.Series(res, index=h.index)
    return {"n": len(h), "agreement": round(float((a == b).mean()), 3), "disagreements": int((a != b).sum()),
            "human_pass_resolved": int(res.sum())}


def summary(df, name):
    d = df[~df.skipped.astype(bool)].copy()
    d["auto_pass"] = d.auto_pass.astype(bool)
    return {"system": name, "task_success (auto rubric)": f"{int(d.auto_pass.sum())}/{len(d)}",
            "median_sec_per_request": round(statistics.median(d.seconds), 2) if len(d) else None}
