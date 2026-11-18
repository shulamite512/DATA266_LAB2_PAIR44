"""1.4 evaluation on the team's golden set (eval/p1_golden_set.csv).

Columns of the golden set:
  gid, conversation_id, turn, category, question, gold_answer, gold_numbers, gold_status, gold_sources
  - gold_numbers: numbers that must appear in the answer, separated by ';' (matched within +-1%)
  - gold_sources: supporting sources separated by ';', e.g. DOC2:p4;DOC1:Figure 1-1
"""
import os
import re
import statistics
import time

import pandas as pd

NUM_RE = re.compile(r"-?\d+(?:,\d{3})*(?:\.\d+)?")


def numbers(text):
    return [float(x.replace(",", "")) for x in NUM_RE.findall(str(text))]


def number_match(gold, pred_text, tol=0.01):
    preds = numbers(pred_text)
    for g in gold:
        if not any(abs(p - g) <= (tol * abs(g) if g else 1e-6) for p in preds):
            return False
    return True


def _split(s):
    return [x.strip() for x in str(s).split(";") if x.strip()]


def source_match(cite, gold_sources, corpus_pages):
    """A cite supports the answer if it is a gold source, or lies on a gold page."""
    if cite in gold_sources:
        return True
    page = corpus_pages.get(cite, cite)
    return page in gold_sources or any(corpus_pages.get(g) == page for g in gold_sources)


def run_golden(engine, golden_path="eval/p1_golden_set.csv"):
    g = pd.read_csv(golden_path, dtype=str, keep_default_na=False)
    g = g[g["question"].str.strip() != ""]
    pages = {r["cite"]: f"{r['doc_id']}:p{r['page']}" for r in engine.kb.records}
    rows = []
    for conv_id, turns in g.groupby("conversation_id", sort=False):
        chat = engine.new_conversation()
        for _, r in turns.sort_values("turn", key=lambda t: t.astype(int)).iterrows():
            t0 = time.time()
            a = chat.answer(r["question"])
            sec = time.time() - t0
            dbg = chat.last_debug
            gold_src = _split(r["gold_sources"])
            gold_nums = [float(x) for x in _split(r["gold_numbers"])]
            status_ok = a["status"] == r["gold_status"].strip()
            nums_ok = number_match(gold_nums, a["answer"]) if gold_nums else True
            top5 = dbg["retrieved"][:5] + dbg["retrieved_pages"][:5]
            recall = (any(source_match(c, gold_src, pages) for c in top5) if gold_src else None)
            cit_ok = [source_match(c, gold_src, pages) for c in a["citations"]] if gold_src else []
            rows.append({"gid": r["gid"], "category": r["category"], "question": r["question"],
                         "gold_status": r["gold_status"], "pred_status": a["status"], "answer": a["answer"],
                         "citations": ",".join(a["citations"]), "figure_references": ",".join(a["figure_references"]),
                         "correct": bool(status_ok and nums_ok), "status_ok": status_ok, "numbers_ok": nums_ok,
                         "recall@5": recall, "citation_hits": sum(cit_ok), "citation_total": len(cit_ok),
                         "seconds": sec, "retrieved_top5": ",".join(dbg["retrieved"][:5])})
    return pd.DataFrame(rows)


def summarize(df, name):
    rec = df["recall@5"].dropna()
    tot = df["citation_total"].sum()
    return {"system": name,
            "answer_correct (/%d)" % len(df): int(df["correct"].sum()),
            "recall@5": round(float(rec.astype(float).mean()), 3) if len(rec) else None,
            "citation_accuracy": round(float(df["citation_hits"].sum() / tot), 3) if tot else None,
            "median_sec_per_question": round(statistics.median(df["seconds"]), 2)}


def human_eval(path="eval/p1_human_ratings.csv"):
    """Ratings file: gid, rater_A, rater_B (1-5 groundedness for the final system)."""
    if not os.path.exists(path):
        return None
    h = pd.read_csv(path)
    h = h.dropna(subset=["rater_A", "rater_B"])
    if h.empty:
        return None
    a, b = h["rater_A"].astype(float), h["rater_B"].astype(float)
    return {"n": len(h), "mean_A": round(a.mean(), 2), "mean_B": round(b.mean(), 2),
            "mean_overall": round(((a + b) / 2).mean(), 2),
            "agree_within_1": round(float(((a - b).abs() <= 1).mean()), 3)}
