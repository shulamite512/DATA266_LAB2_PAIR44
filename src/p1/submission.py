"""1.5 Kaggle submission: reads QUESTIONS_PATH, answers each conversation turn by turn
with a fresh memory, and writes submission.csv in the required format."""
import os
import subprocess
import sys
import time

import pandas as pd


def make_submission(engine, questions_path=None, out_path="submission.csv"):
    questions_path = questions_path or os.environ.get("QUESTIONS_PATH", "Questions.csv")
    q = pd.read_csv(questions_path, dtype=str, keep_default_na=False)
    rows, timings = [], []
    for conv_id, turns in q.groupby("conversation_id", sort=False):
        chat = engine.new_conversation()  # empty memory for this conversation
        for _, r in turns.sort_values("turn", key=lambda t: t.astype(int)).iterrows():
            t0 = time.time()
            a = chat.answer(r["question"])
            timings.append(time.time() - t0)
            print(f"  answered {len(timings)}/{len(q)} ({timings[-1]:.0f}s) status={a['status']}", flush=True)
            rows.append({"id": r["id"], "conversation_id": conv_id, "question_id": r["question_id"],
                         "answer": " ".join(a["answer"].split()),
                         "figure_references": ",".join(a["figure_references"]) or "NONE",
                         "citations": ",".join(a["citations"]) or "NONE", "status": a["status"]})
    pd.DataFrame(rows).set_index("id").loc[q["id"]].reset_index().to_csv(out_path, index=False)
    return out_path, timings


def validate(submission_path, questions_path, data_dir):
    script = os.path.join(data_dir, "validate_submission.py")
    if not os.path.exists(script):
        print("validate_submission.py not found in", data_dir)
        return None
    res = subprocess.run([sys.executable, script, submission_path, questions_path], capture_output=True, text=True)
    print(res.stdout, res.stderr)
    return res.returncode
