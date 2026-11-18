"""Generate the (unexecuted) notebooks under notebooks/. Run: python tools/build_notebooks.py
Then open each notebook on Kaggle/Colab, Restart & Run All, and commit the executed version."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CELL1 = '''# Cell 1 - run information (required)
import os, subprocess, sys, random, numpy as np, torch
# Locate the repo: run from a local clone, or clone the tagged commit on Kaggle/Colab.
REPO_URL = os.environ.get("REPO_URL", "https://github.com/shulamite512/DATA266_LAB2_PAIR44.git")  # EDIT
GIT_REF = os.environ.get("GIT_REF", "{tag}")
if os.path.isdir("../../src"):  # notebooks/<member>/
    os.chdir("../..")
elif os.path.isdir("../src"):
    os.chdir("..")
import glob, shutil
zips = sorted(glob.glob("/content/**/L2_colab*.zip", recursive=True)
              + glob.glob("/kaggle/input/**/L2_colab*.zip", recursive=True), key=os.path.getmtime)
if not os.path.isdir("src") and zips:  # uploaded project zip (newest one wins)
    dest = "/content" if zips[-1].startswith("/content") else "/kaggle/working/l2"
    print("using", zips[-1], "->", dest)
    subprocess.run(["unzip", "-q", "-o", zips[-1], "-d", dest], check=False)
    os.chdir(dest)
kaggle_src = glob.glob("/kaggle/input/**/src/p1", recursive=True)
if not os.path.isdir("src") and kaggle_src:  # Kaggle dataset made from the zip (Kaggle auto-extracts it)
    root = os.path.dirname(os.path.dirname(kaggle_src[0]))
    print("using Kaggle dataset", root)
    shutil.copytree(root, "/kaggle/working/l2", dirs_exist_ok=True)
    os.chdir("/kaggle/working/l2")
if not os.path.isdir("src") and "YOUR_GITHUB" in REPO_URL:
    raise SystemExit("Project code not found: upload L2_colab.zip to /content (Files pane -> content -> Upload), "
                     "wait for the upload to finish, then run this cell again.")
if not os.path.isdir("src"):
    url = REPO_URL
    try:
        from kaggle_secrets import UserSecretsClient
        url = REPO_URL.replace("https://", "https://" + UserSecretsClient().get_secret("GITHUB_TOKEN") + "@")
    except Exception:
        try:
            from google.colab import userdata
            url = REPO_URL.replace("https://", "https://" + userdata.get("GITHUB_TOKEN") + "@")
        except Exception:
            pass
    subprocess.run(["git", "clone", "--quiet", url, "/tmp/repo"], check=True)
    subprocess.run(["git", "-C", "/tmp/repo", "remote", "set-url", "origin", REPO_URL], check=True)  # drop token
    subprocess.run(["git", "-C", "/tmp/repo", "checkout", "--quiet", GIT_REF], check=True)
    os.chdir("/tmp/repo")
sys.path.insert(0, os.getcwd())
res = subprocess.run([sys.executable, "-m", "src.common.install"], capture_output=True, text=True)
print(res.stdout[-4000:], res.stderr[-4000:])
assert res.returncode == 0, "dependency install failed - see the pip output above"
from src.common.runinfo import library_versions
SEED = 266; random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)
commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
print({{"commit": commit, "python": sys.version.split()[0], "torch": torch.__version__,
       "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu", "seed": SEED}})
print(library_versions())'''

HF_LOGIN = '''import os
from huggingface_hub import login
tok = os.environ.get("HF_TOKEN")
if not tok:
    try:
        from kaggle_secrets import UserSecretsClient; tok = UserSecretsClient().get_secret("HF_TOKEN")
    except Exception:
        try:
            from google.colab import userdata; tok = userdata.get("HF_TOKEN")
        except Exception:
            tok = None
if tok:
    login(token=tok)
else:
    print("No HF_TOKEN found: uploads will fail (generation still works).")'''

MODEL_CHOICE = '''# ===== MODEL CHOICE (edit BACKEND, then Run all) =====
#  "qwen3b" : Qwen2.5-VL-3B, fp16, free (first run scored 0.5)
#  "qwen7b" : Qwen2.5-VL-7B, 4-bit, free, slower (~40 min), better rule-following (scored 0.56)
#  "qwen3"  : free, two models: Qwen2.5-VL-7B (4-bit) describes figures, then Qwen3-14B (4-bit, text-only,
#             stronger reasoning) answers. ~45-60 min on a T4. Set QWEN3_THINKING = True for step-by-step
#             reasoning (better arithmetic, but much slower - only if time allows).
#  "gemini": Google Gemini via the google-genai SDK - FREE key from aistudio.google.com, secret GEMINI_API_KEY
#  "claude" : Claude Opus 5.5 via the Anthropic API - needs an ANTHROPIC_API_KEY secret, costs a few dollars
#  Hosted APIs must be named in the README with their model version (lab rule).
BACKEND = "qwen7b"
QWEN3_MODEL = "Qwen/Qwen3-14B"      # or "Qwen/Qwen3-8B" (faster)
QWEN3_THINKING = False
os.environ["P1_BACKEND"] = "local"   # reset; the branches below override it for hosted backends
os.environ.pop("P1_ANSWER_LLM", None)

def _secret(name):
    if os.environ.get(name):
        return os.environ[name]
    try:
        from google.colab import userdata; return userdata.get(name)
    except Exception:
        try:
            from kaggle_secrets import UserSecretsClient; return UserSecretsClient().get_secret(name)
        except Exception:
            return None

if BACKEND == "gemini":
    os.environ["P1_BACKEND"] = "gemini"; os.environ["P1_VLM"] = os.environ.get("GEMINI_MODEL", "gemini-4-hydrogen")
    os.environ["P1_FINAL_K"] = "10"; os.environ["P1_MAX_IMAGES"] = "4"
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "google-genai"], check=True)
    import importlib.metadata as md_; print("google-genai", md_.version("google-genai"))
    key = _secret("GEMINI_API_KEY")
    if not key:
        raise SystemExit("Add a free Gemini API key (aistudio.google.com -> Get API key) as a secret named "
                         "GEMINI_API_KEY (Colab: key icon on the left, enable notebook access), then run again.")
    os.environ["GEMINI_API_KEY"] = key
elif BACKEND == "qwen7b":
    os.environ["P1_VLM"] = "Qwen/Qwen2.5-VL-7B-Instruct"; os.environ["P1_VLM_4BIT"] = "1"
elif BACKEND == "qwen3":
    os.environ["P1_VLM"] = "Qwen/Qwen2.5-VL-7B-Instruct"; os.environ["P1_VLM_4BIT"] = "1"   # figure descriptions
    os.environ["P1_ANSWER_LLM"] = QWEN3_MODEL                                               # answers
    os.environ["P1_LLM_THINKING"] = "1" if QWEN3_THINKING else "0"
    os.environ["P1_FINAL_K"] = "8"
elif BACKEND == "claude":
    os.environ["P1_BACKEND"] = "claude"; os.environ["P1_VLM"] = "claude-opus-5-5"
    os.environ["CLAUDE_EFFORT"] = "high"                              # accuracy over cost
    os.environ["P1_FINAL_K"] = "10"; os.environ["P1_MAX_IMAGES"] = "4"   # more evidence, more chart images
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "anthropic"], check=True)
    import importlib.metadata as md_; print("anthropic", md_.version("anthropic"))
    key = _secret("ANTHROPIC_API_KEY")
    if not key:
        raise SystemExit("Add your Anthropic API key as a secret named ANTHROPIC_API_KEY "
                         "(Colab: key icon on the left, enable notebook access), then run again.")
    os.environ["ANTHROPIC_API_KEY"] = key
print("BACKEND =", BACKEND)'''

OUT_DIR = '''OUT = "/kaggle/working" if os.path.isdir("/kaggle/working") else "outputs"
os.makedirs(OUT, exist_ok=True)'''


def md(s):
    return {"cell_type": "markdown", "metadata": {}, "source": s.strip("\n").splitlines(keepends=True)}


def code(s):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
            "source": s.strip("\n").splitlines(keepends=True)}


def nb(cells):
    return {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                                         "language_info": {"name": "python"}, "accelerator": "GPU"},
            "nbformat": 4, "nbformat_minor": 4}


# ----------------------------------------------------------------------------- Part 1 (Kaggle)
P1 = [
    code(CELL1.format(tag="p1-v1.0")),
    md("""# Part 1 - Multimodal RAG over a read-only knowledge base (Kaggle submission notebook)
Attach the competition data. The notebook reads `QUESTIONS_PATH` (graders swap in the hidden set) and writes
`submission.csv` with no manual step. Nothing here refers to specific question IDs or texts."""),
    code(MODEL_CHOICE),
    code(OUT_DIR + '''
import json, time
import pandas as pd
os.environ.setdefault("P1_WORK_DIR", os.path.join(OUT, "p1_work"))
from src.p1.config import P1Config
from src.p1.retrieve import KnowledgeBase
from src.p1.answer import RAGEngine
from src.common.vlm import make_vlm
cfg = P1Config()
print(cfg)
vlm = make_vlm(cfg.vlm_model, load_in_4bit=cfg.vlm_4bit)
print("answer model:", vlm.model_id)'''),
    md("## 1.1 Ingestion & indexing (text chunks, figure/table crops, VLM descriptions, ChromaDB + BM25)"),
    code('''t0 = time.time()
kb = KnowledgeBase.build(cfg, vlm)
print(f"index built in {time.time() - t0:.0f}s")
print(json.dumps(kb.summary(), indent=1))
print(json.dumps({d: {k: v for k, v in m.items() if k != "raw"} for d, m in kb.docs.items()}, indent=1))'''),
    code('''import matplotlib.pyplot as plt
from PIL import Image
figs = kb.figures[:12]
fig, axes = plt.subplots(3, 4, figsize=(16, 11))
for ax, f in zip(axes.flat, figs):
    ax.imshow(Image.open(f["image_path"])); ax.set_title(f"{f['figure_id']} (trust {f['trust_level']})", fontsize=8); ax.axis("off")
plt.tight_layout(); plt.show()
print("records that are NOT evidence (low trust / injected):")
for r in kb.records:
    if not r["evidence_ok"]:
        print(" ", r["cite"], r["section"], "suspicious" if r["suspicious"] else "", "|", r["text"][:120].replace("\\n", " "))'''),
    md("## 1.2-1.5 Answer every conversation and write submission.csv"),
    code('''# Optional answer-model swap (BACKEND="qwen3"): free the vision model, load the text LLM for answering
if os.environ.get("P1_ANSWER_LLM"):
    import gc
    from src.common.vlm import TextLLM
    del vlm; gc.collect(); torch.cuda.empty_cache()
    t0 = time.time()
    vlm = TextLLM(os.environ["P1_ANSWER_LLM"], load_in_4bit=True, thinking=os.environ.get("P1_LLM_THINKING") == "1")
    print(f"answer model: {vlm.model_id} (thinking={vlm.thinking}) loaded in {time.time() - t0:.0f}s, "
          f"GPU mem {torch.cuda.memory_allocated() / 1e9:.1f} GB")
else:
    print("answer model:", vlm.model_id)'''),
    code('''from src.p1.submission import make_submission, validate
engine = RAGEngine(cfg, kb, vlm)
QUESTIONS_PATH = os.environ.get("QUESTIONS_PATH", os.path.join(cfg.data_dir, "Questions.csv"))
t0 = time.time()
sub_path, times = make_submission(engine, QUESTIONS_PATH, os.path.join(OUT, "submission.csv"))
print(f"{len(times)} questions in {time.time() - t0:.0f}s, median {np.median(times):.1f}s/question")
validate(sub_path, QUESTIONS_PATH, cfg.data_dir)
pd.set_option("display.max_colwidth", 200); pd.set_option("display.max_rows", 200)
pd.read_csv(sub_path)'''),
    code('''# Colab only: download submission.csv right away (sessions are wiped when they disconnect)
try:
    from google.colab import files
    files.download(sub_path)
except ImportError:
    print("submission written to", sub_path)'''),
]

# ----------------------------------------------------------------------------- Part 1 evaluation
P1E = [
    code(CELL1.format(tag="p1-v1.0")),
    md("""# Part 1 - Evaluation (golden set, baseline vs final, human evaluation, safety)
`eval/p1_golden_set.csv` was written and committed by the team **before** tuning (C2.3)."""),
    code(MODEL_CHOICE),
    code(OUT_DIR + '''
import json, time
import pandas as pd
os.environ.setdefault("P1_WORK_DIR", os.path.join(OUT, "p1_work"))
from src.p1.config import P1Config, baseline_config
from src.p1.retrieve import KnowledgeBase
from src.p1.answer import RAGEngine
from src.p1 import evaluate as E
from src.common.vlm import make_vlm
cfg = P1Config()
vlm = make_vlm(cfg.vlm_model, load_in_4bit=cfg.vlm_4bit)
kb = KnowledgeBase.build(cfg, vlm)
print(json.dumps(kb.summary(), indent=1)[:3000])'''),
    code('''systems = {"baseline (dense only)": baseline_config(cfg), "final (hybrid)": cfg,
           "final + reranker (bonus)": cfg.variant(use_reranker=True)}
results, per_q = [], {}
for name, c in systems.items():
    df = E.run_golden(RAGEngine(c, kb, vlm), "eval/p1_golden_set.csv")
    per_q[name] = df
    df.to_csv(os.path.join(OUT, f"p1_golden_{name.split()[0]}.csv"), index=False)
    results.append(E.summarize(df, name))
pd.DataFrame(results)'''),
    code('''pd.set_option("display.max_colwidth", 100)
per_q["final (hybrid)"][["gid", "category", "gold_status", "pred_status", "correct", "recall@5", "citations", "answer"]]'''),
    md("## Human evaluation (groundedness 1-5, both members) - fill `eval/p1_human_ratings.csv` from the export below"),
    code('''export = per_q["final (hybrid)"][["gid", "question", "answer", "citations", "figure_references"]]
export.to_csv(os.path.join(OUT, "p1_final_answers_for_rating.csv"), index=False)
print(E.human_eval("eval/p1_human_ratings.csv"))'''),
    md("## Safety (C4): untrusted appendix, false claims and hidden instructions - baseline vs final"),
    code('''cats = ["injection_appendix_c", "conflict", "revision", "false_premise", "not_found"]
cmp = per_q["baseline (dense only)"][["gid", "category", "question", "pred_status", "correct", "answer"]].merge(
    per_q["final (hybrid)"][["gid", "pred_status", "correct", "answer"]], on="gid", suffixes=("_baseline", "_final"))
cmp[cmp.category.isin(cats)]'''),
    md("## Results table (all numbers above are notebook outputs)"),
    code('''table = pd.DataFrame(results).set_index("system")
table["human_groundedness_mean"] = None
h = E.human_eval("eval/p1_human_ratings.csv")
if h:
    table.loc["final (hybrid)", "human_groundedness_mean"] = h["mean_overall"]
table'''),
]

# ----------------------------------------------------------------------------- Part 2
P2 = [
    code(CELL1.format(tag="p2-v1.0")),
    md("# Part 2 - Fine-tuning Stable Diffusion 1.5 with LoRA (Naruto BLIP captions)"),
    code(HF_LOGIN),
    code('''import json, pandas as pd
from src.p2 import config as C
from src.p2.data_prep import prepare, write_prompts, load_split
report = prepare()
print(json.dumps(report, indent=1))'''),
    code('''import matplotlib.pyplot as plt
from PIL import Image
train_items = load_split("train"); test = load_split("test")
fig, axes = plt.subplots(2, 4, figsize=(16, 8))
for ax, (p, c) in zip(axes.flat, train_items[:8]):
    ax.imshow(Image.open(p)); ax.set_title(c[:40], fontsize=8); ax.axis("off")
plt.show()'''),
    md("""**Dataset description** (edit in your own words): ~1.2k Naruto anime frames with BLIP captions ...
Limitations/biases: (1) BLIP captions are short and generic and often wrong about characters; (2) mostly close-up
faces of a few main characters, so poses, backgrounds and diversity of people are limited."""),
    code('''prompts = write_prompts()   # 10 in-domain from TEST captions + 5 OOD + 5 compositional
print(json.dumps(prompts, indent=1))
print("-> commit prompts/p2_prompts.json BEFORE training finishes")'''),
    md("## 2.2 Two runs, same data and step budget (LoRA rank 8 vs rank 32)"),
    code('''from src.p2.train_lora import train
stats = {}
for name, kw in C.RUNS.items():
    stats[name] = train(name, **kw, **C.TRAIN_COMMON)'''),
    code('''cols = ["method", "rank", "trainable_params", "learning_rate", "steps", "effective_batch", "batch_size", "grad_accum",
        "peak_gpu_mem_gb", "train_seconds", "gpu_hours", "gpu", "final_loss_avg50"]
train_table = pd.DataFrame({k: {c: v[c] for c in cols} for k, v in stats.items()}).T
plt.figure(figsize=(8, 3))
for k, v in stats.items():
    plt.plot(pd.Series(v["losses"]).rolling(25).mean(), label=k)
plt.legend(); plt.xlabel("step"); plt.ylabel("loss (rolling 25)"); plt.show()
train_table'''),
    md("## 2.3 Generation: 20 prompts x seeds {0,1} x {base, run1, run2}"),
    code('''from src.p2.generate import generate_all, side_by_side
MODELS = {"base": None, **{k: os.path.join(C.OUT_DIR, "models", k) for k in C.RUNS}}
meta = generate_all(MODELS, prompts)
print(meta.groupby("model").agg(images=("file", "count"), nsfw_flagged=("nsfw_flagged", "sum"), sec_per_image=("seconds", "median")))'''),
    code('''grid_ids = ["in_00", "in_01", "in_02", "in_03", "ood_00", "ood_01", "comp_00", "comp_01"]
side_by_side(meta, grid_ids, list(MODELS), os.path.join(C.OUT_DIR, "grid_8_prompts.png"))'''),
    md("## 2.4 Evaluation: KID (in-domain vs test), CLIP score, LPIPS diversity"),
    code('''from src.p2.evaluate import kid, lpips_diversity
from src.common.clip_utils import ClipScorer
clip = ClipScorer()
test_paths = [p for p, _ in test]
rows = []
for m in MODELS:
    sub = meta[meta.model == m]
    ind = sub[sub.category == "in_domain"]
    k_mean, k_std = kid(test_paths, ind.file.tolist())
    cs = clip.clip_score(sub.file.tolist(), sub.prompt.tolist())
    cs_in = clip.clip_score(ind.file.tolist(), ind.prompt.tolist())
    lp, _ = lpips_diversity(meta, m)
    rows.append({"model": m, "KID_in_domain_mean": round(k_mean, 4), "KID_std": round(k_std, 4),
                 "CLIP_score_all40": round(float(np.mean(cs)), 2), "CLIP_score_in_domain": round(float(np.mean(cs_in)), 2),
                 "LPIPS_diversity": round(lp, 4), "nsfw_flagged": int(sub.nsfw_flagged.sum())})
eval_table = pd.DataFrame(rows).set_index("model")
eval_table'''),
    md("Pick the final run from the table above (set `FINAL`)."),
    code('''FINAL = "run1_lora_r8"   # EDIT after looking at the results
from src.p2.evaluate import make_human_pairs, human_win_rate
key = make_human_pairs(meta, FINAL)
print("Raters: open outputs/p2/human_eval/pair_XX.png only (NOT key.csv) and fill eval/p2_human_ratings.csv")
print(human_win_rate(key, "eval/p2_human_ratings.csv", FINAL))'''),
    md("## Failure modes (pick at least two and describe them in the report)"),
    code('''side_by_side(meta, ["ood_00", "ood_02", "ood_03", "comp_00", "comp_02", "comp_04"], list(MODELS),
             os.path.join(C.OUT_DIR, "failure_modes.png"), seed=1)'''),
    md("## Safety: memorization check (10 in-domain generations vs all training images, CLIP image similarity)"),
    code('''from src.p2.evaluate import memorization
gen10 = meta[(meta.model == FINAL) & (meta.category == "in_domain") & (meta.seed == 0)].file.tolist()
mem_all, top3 = memorization(clip, gen10, [p for p, _ in train_items])
print(mem_all[["generated", "nearest_train", "clip_cos"]])
fig, axes = plt.subplots(3, 2, figsize=(7, 10))
for i, r in top3.iterrows():
    axes[i, 0].imshow(Image.open(r.generated)); axes[i, 0].set_title(f"generated (cos {r.clip_cos:.3f})", fontsize=9)
    axes[i, 1].imshow(Image.open(r.nearest_train)); axes[i, 1].set_title("nearest training image", fontsize=9)
    axes[i, 0].axis("off"); axes[i, 1].axis("off")
plt.tight_layout(); plt.show()'''),
    md("## Results table and Hugging Face upload"),
    code('''hw = human_win_rate(key, "eval/p2_human_ratings.csv", FINAL) or {}
results = eval_table.copy()
for k in C.RUNS:
    results.loc[k, "GPU_hours"] = stats[k]["gpu_hours"]; results.loc[k, "peak_mem_GB"] = stats[k]["peak_gpu_mem_gb"]
results.loc[FINAL, "human_style_win_rate_vs_base"] = hw.get("style_choice_final_win_rate")
results.loc[FINAL, "human_prompt_win_rate_vs_base"] = hw.get("prompt_choice_final_win_rate")
results'''),
    code('''from src.p2.hub import push_lora, push_images
links = {}
for k in C.RUNS:
    s = stats[k]
    card = None
    if k == FINAL:
        card = dict(base=C.BASE_MODEL, dataset=C.DATASET, run=k, method=s["method"], rank=s["rank"], alpha=s["alpha"],
                    targets=s["target_modules"], train_images=s["train_images"], steps=s["steps"], batch_size=s["batch_size"],
                    grad_accum=s["grad_accum"], lr=s["learning_rate"], schedule=s["lr_schedule"], seed=s["seed"],
                    params=s["trainable_params"], mem=s["peak_gpu_mem_gb"], gpu_hours=s["gpu_hours"], gpu=s["gpu"],
                    results=results.loc[["base", k]].T.to_string())
    links[k] = push_lora(os.path.join(C.OUT_DIR, "models", k), C.HF_MODEL_REPOS[k], card)
links["images"] = push_images(meta, C.HF_IMAGES_REPO)
print(json.dumps(links, indent=1))'''),
]

# ----------------------------------------------------------------------------- Part 3
P3 = [
    code(CELL1.format(tag="p3-v1.0")),
    md("""# Part 3 - Multimodal multi-agent system
Planner (input safety) -> Vision Understanding -> Prompt Engineering -> Image Generation -> Critique (output safety)
-> accept / revise (max 2). Scenarios and red-team cases in `eval/` were committed before running."""),
    code('''import json, pandas as pd
os.environ.setdefault("P3_LORA_REPO", "chels512/data266-lab2-naruto-run1-lora-r8")   # final Part 2 LoRA
from src.p2.data_prep import prepare
if not os.path.isdir("data/p2/test"):
    prepare()   # only to copy two held-out anime images as test inputs
from src.p3 import make_test_inputs
make_test_inputs.main()'''),
    code('''from src.p3.config import P3Config
from src.p3.orchestrator import MultiAgentSystem
cfg = P3Config()
print(cfg)
system = MultiAgentSystem(cfg)'''),
    md("## First milestone: one request through the linear pipeline"),
    code('''st = system.run("Turn this into a watercolor painting.", "data/p3/inputs/house.png", request_id="demo_watercolor")
print(st.status, st.message)
for t in st.trace:
    print(f"{t.agent:22s} {t.seconds:6.1f}s", (t.error or "")[:80])
from PIL import Image
display(Image.open(st.final_image_path)) if st.final_image_path else None'''),
    md("## 3.3 15 scenarios: with vs without critique loop"),
    code('''from src.p3 import evaluate as E
scen = json.load(open("eval/p3_scenarios.json"))
with_c, states_c = E.run_cases(system, scen, use_critique=True, tag="_crit")
without_c, states_n = E.run_cases(system, scen, use_critique=False, tag="_nocrit")
with_c.to_csv(os.path.join(cfg.out_dir, "scenarios_with_critique.csv"), index=False)
without_c.to_csv(os.path.join(cfg.out_dir, "scenarios_without_critique.csv"), index=False)
pd.set_option("display.max_colwidth", 80)
with_c[["id", "category", "status", "route", "revisions", "auto_pass", "fail_reasons", "seconds"]]'''),
    code('''without_c[["id", "category", "status", "route", "auto_pass", "fail_reasons", "seconds"]]'''),
    code('''import matplotlib.pyplot as plt
gen_ids = [s["id"] for s in scen if s["category"] in ("style_change", "edit", "domain_style")]
fig, axes = plt.subplots(len(gen_ids), 3, figsize=(10, 3.2 * len(gen_ids)))
for i, sid in enumerate(gen_ids):
    s = next(x for x in scen if x["id"] == sid)
    a, b = states_c.get(sid), states_n.get(sid)
    if s["image"]:
        axes[i, 0].imshow(Image.open(os.path.join("data/p3/inputs", s["image"])))
    axes[i, 0].set_title(f"{sid}: {s['request'][:38]}", fontsize=8)
    for j, (st_, lab) in enumerate(((b, "no critique"), (a, "with critique")), start=1):
        if st_ and st_.final_image_path:
            axes[i, j].imshow(Image.open(st_.final_image_path))
        axes[i, j].set_title(f"{lab} ({st_.revisions if st_ else '-'} rev)", fontsize=8)
for ax in axes.flat:
    ax.axis("off")
plt.tight_layout(); plt.show()'''),
    md("## Critic agreement: label each critic decision (accept/revise) in `eval/p3_critic_labels.csv`"),
    code('''crit = E.critic_decisions(states_c)
if not os.path.exists("eval/p3_critic_labels.csv"):
    crit.to_csv("eval/p3_critic_labels.csv", index=False)
    print("wrote eval/p3_critic_labels.csv - fill human_decision, commit, re-run")
print(E.critic_agreement("eval/p3_critic_labels.csv"))
crit'''),
    md("## 10 red-team cases"),
    code('''red = json.load(open("eval/p3_redteam.json"))
red_df, red_states = E.run_cases(system, red, use_critique=True, tag="_red")
red_df.to_csv(os.path.join(cfg.out_dir, "redteam.csv"), index=False)
ran = red_df[~red_df.skipped.astype(bool)].copy()
ran["auto_pass"] = ran.auto_pass.astype(bool)   # skipped rows leave NaN -> object dtype, where ~ is not boolean NOT
print(f"attack success rate: {int((~ran.auto_pass).sum())}/{len(ran)} (skipped: {int(red_df.skipped.sum())})")
red_df[["id", "status", "route", "auto_pass", "fail_reasons", "message"]]'''),
    md("## Human evaluation and results table"),
    code('''print("human agreement:", E.human_agreement("eval/p3_human_judgements.csv"))
summary = pd.DataFrame([E.summary(without_c, "baseline: no critique loop"), E.summary(with_c, "final: with critique loop")])
summary["critic_agreement"] = [None, (E.critic_agreement() or {}).get("critic_agreement")]
summary["redteam_attack_success"] = [None, f"{int((~ran.auto_pass).sum())}/{len(ran)}"]
summary'''),
    md("## Gradio demo app (shows every agent's output)"),
    code('''from src.p3.app import build_app
demo = build_app(system)
demo.launch(share=True, debug=False)'''),
]


def main():
    out = os.path.join(ROOT, "notebooks", "Chelsi")
    os.makedirs(out, exist_ok=True)
    for name, cells in (("p1_rag.ipynb", P1), ("p1_eval.ipynb", P1E), ("p2_finetune.ipynb", P2), ("p3_agents.ipynb", P3)):
        if os.path.exists(os.path.join(out, name)) and "--force" not in sys.argv:
            print("kept", name, "(exists; executed notebooks are never overwritten without --force)")
            continue
        with open(os.path.join(out, name), "w", encoding="utf-8") as f:
            json.dump(nb(cells), f, indent=1)
        print("wrote", name)


if __name__ == "__main__":
    main()
