"""Build and execute notebooks/Chelsi/human_eval_results.ipynb (CPU only).

Computes every human-evaluation number of the lab from the committed rating files, using the same functions as the
GPU notebooks, so that each number in the report is a notebook output (C2.2).
Run from the repo root: python tools/build_human_eval_notebook.py
"""
import os

import nbformat
from nbclient import NotebookClient

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "notebooks", "Chelsi", "human_eval_results.ipynb")

CELL1 = '''# Cell 1 - run information (required)
import os, subprocess, sys, random, numpy as np
if os.path.isdir("../../src"):
    os.chdir("../..")
sys.path.insert(0, os.getcwd())
SEED = 266; random.seed(SEED); np.random.seed(SEED)
try:
    import torch; torch.manual_seed(SEED); tv = torch.__version__
    gpu = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu"
except ImportError:
    tv, gpu = "not installed (CPU-only analysis notebook)", "cpu"
commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
import pandas as pd
print({"commit": commit, "python": sys.version.split()[0], "torch": tv, "gpu": gpu, "seed": SEED})
print({"pandas": pd.__version__, "numpy": np.__version__})'''

cells = [
    nbformat.v4.new_code_cell(CELL1),
    nbformat.v4.new_markdown_cell(
        "# Human evaluation results (Parts 1-3)\n"
        "The GPU notebooks wrote the answers and images to be rated; both members then filled the rating sheets in "
        "`eval/`. This notebook computes every human-evaluation number from those committed files with the same "
        "functions the GPU notebooks use (`src/p1/evaluate.py`, `src/p2/evaluate.py`, `src/p3/evaluate.py`). "
        "No GPU is needed."),
    nbformat.v4.new_markdown_cell("## Part 1 - groundedness of the 25 final answers (1-5, both members)"),
    nbformat.v4.new_code_cell('''from src.p1 import evaluate as E1
h = pd.read_csv("eval/p1_human_ratings.csv")
print(E1.human_eval("eval/p1_human_ratings.csv"))
print("exact agreement:", round(float((h.rater_A == h.rater_B).mean()), 3))
g = pd.read_csv("eval/p1_golden_set.csv")[["gid", "category"]]
h = h.merge(g, on="gid"); h["mean"] = (h.rater_A + h.rater_B) / 2
h.groupby("category")["mean"].mean().round(2).sort_values()'''),
    nbformat.v4.new_markdown_cell("## Part 2 - blinded pairs, final run (rank 8) vs base model"),
    nbformat.v4.new_code_cell('''from src.p2.evaluate import human_win_rate
key = pd.read_csv("part2/Chelsi/human_eval_key.csv")
print(human_win_rate(key, "eval/p2_human_ratings.csv", "run1_lora_r8"))
r = pd.read_csv("eval/p2_human_ratings.csv").merge(key[["pair_id", "left_model", "prompt_id"]], on="pair_id")
for c in ("style_choice", "prompt_choice"):
    r[c + "_final"] = (r[c].str.upper() == "A") == (r.left_model == "run1_lora_r8")
w = r.pivot(index="pair_id", columns="rater", values=["style_choice", "prompt_choice"])
raters = sorted(r.rater.unique())
if len(raters) >= 2:
    print("pairwise agreement:", {c: round(float((w[c][raters[0]] == w[c][raters[1]]).mean()), 3)
                                  for c in ("style_choice", "prompt_choice")})
r["category"] = r.prompt_id.str.split("_").str[0]
pd.concat([r.groupby("rater")[["style_choice_final", "prompt_choice_final"]].mean(),
           r.groupby("category")[["style_choice_final", "prompt_choice_final"]].mean()]).round(3)'''),
    nbformat.v4.new_markdown_cell("## Part 3 - scenario judgements, critic agreement and results table"),
    nbformat.v4.new_code_cell('''from src.p3 import evaluate as E3
print("human agreement:", E3.human_agreement("eval/p3_human_judgements.csv"))
print("critic agreement:", E3.critic_agreement("eval/p3_critic_labels.csv"))
d = pd.read_csv("eval/p3_critic_labels.csv")
norm = lambda s: "accept" if str(s).lower().startswith("acc") else "revise"
pd.crosstab(d.critic_decision.map(norm), d.human_decision.map(norm), rownames=["critic"], colnames=["human"])'''),
    nbformat.v4.new_code_cell('''with_c = pd.read_csv("part3/Chelsi/scenarios_with_critique.csv")
without_c = pd.read_csv("part3/Chelsi/scenarios_without_critique.csv")
red = pd.read_csv("part3/Chelsi/redteam.csv")
ran = red[~red.skipped.astype(bool)].copy(); ran["auto_pass"] = ran.auto_pass.astype(bool)
hj = pd.read_csv("eval/p3_human_judgements.csv", keep_default_na=False)
human_pass = sum((r.resolved or r.rater_A).startswith("p") for r in hj.itertuples())
table = pd.DataFrame([E3.summary(without_c, "baseline: no critique loop"), E3.summary(with_c, "final: with critique loop")])
table["human_task_success (resolved)"] = [None, f"{human_pass}/{len(hj)}"]
table["critic_agreement"] = [None, E3.critic_agreement("eval/p3_critic_labels.csv")["critic_agreement"]]
table["redteam_rubric_failures"] = [None, f"{int((~ran.auto_pass).sum())}/{len(ran)} (skipped {int(red.skipped.astype(bool).sum())})"]
table'''),
    nbformat.v4.new_code_cell('''red[["id", "category", "status", "auto_pass", "skipped", "fail_reasons", "message"]]'''),
]

nb = nbformat.v4.new_notebook(cells=cells, metadata={"kernelspec": {"name": "python3", "display_name": "Python 3",
                                                                   "language": "python"}})
os.makedirs(os.path.dirname(OUT), exist_ok=True)
NotebookClient(nb, timeout=300, kernel_name="python3", resources={"metadata": {"path": os.path.dirname(OUT)}}).execute()
nbformat.write(nb, OUT)
print("wrote", OUT)
