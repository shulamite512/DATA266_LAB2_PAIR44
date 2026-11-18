> **Parth's original repository README** (from before the merge). Paths inside it refer to the combined layout as follows:
> - `notebooks/p1_rag.ipynb` and `notebooks/p3_agents.ipynb`: unchanged.
> - `notebooks/p2_*`: now `notebooks/alternatives/parth/`. The root `notebooks/p2_finetune.ipynb` is now Chelsi's selected Part 2.
> - `notebooks/p3_human_rating_ui.ipynb` and `p3_disagreement_review.ipynb`: now `notebooks/evaluation/`.
> - `eval/p2_human_ratings.csv`: now `eval/alternatives/parth/`.
> - `DECISIONS.md` and `HUMAN_EVALUATION.md`: now `docs/`.
> - `report/`: now `docs/report/`. `publication/`: now `docs/publication/`. `build_canvas_zip.py` there was written for the old layout.
> - `requirements.txt`: now `docs/history/requirements-initial-parth.txt`.
>
> The README for the combined repository is the root `README.md`.
# DATA 266 Lab 2 — Pair Programming Team 44

Repository for DATA 266 (Fall 2026) Lab 2: https://github.com/shulamite512/DATA266_LAB2_PAIR44 (to be private with instructor/ISA read access; nothing pushed yet).

> **Naming note:** the course convention is `data266-lab2-team##`. The team chose `DATA266_LAB2_PAIR44` (flagged for compliance review). Part 1 was first developed in a separate repository (origin `Parthp28/DATA266_LAB2_Pair44`). Its full history is merged here (`dbd01db`), so its original commit timestamps are preserved, including the golden set frozen in `d9bbd68` on 2026-10-21.

| Part | Topic | Notebook | Status |
|------|-------|----------|--------|
| 1 | Multimodal RAG over a read-only knowledge base (Kaggle) | `notebooks/p1_rag.ipynb` | **Final: P1-KAGGLE-V14-R1**, executed on Kaggle (NVIDIA Tesla T4; 2,616 s ≈ 43.6 min of the 5,400 s budget): label router + dense + BM25 + RRF + CPU reranker + registry; Qwen3-VL-4B in 4-bit NF4 (bitsandbytes). 40-row submission `eval/p1_submission.csv`, validator `valid: 40 rows` (answered 32, conflict 3, session_override 3, not_found 2). Its Kaggle score is not recorded here. Historical: held-out golden set P1-EXP-001 (earlier code; baseline 14/25 vs final 13/25, Recall@5 0.764 → 0.882) and checkpoint P1-EXP-003 (`eb87662`). V14-R1 was not evaluated on the golden set (D-120). Log: `docs/part1/DECISIONS_P1.md`, D-120. **Pending:** Kaggle notebook link |
| 2 | Fine-tuning diffusion models | `notebooks/p2_finetune.ipynb` | **P2-EXP-001 executed** (`FULL_RUN`, 2026-11-16): LoRA A (r4) and B (r64) trained 1,500 steps each; 120/120 images (base/A/B × 20 prompts × 2 seeds); KID, CLIP, LPIPS, memorization and safety computed; final adapter **A** (lower in-domain KID 0.0619 vs 0.0825). **Human evaluation complete** (3 raters × 25 blinded pairs; `eval/p2_human_ratings.csv`, scored by `REPORT_ONLY`, D-118): LoRA A preferred over base in 38.7 % (style) and 41.3 % (prompt) of judgments. **Pending:** the authorized Hugging Face upload |
| 3 | Multimodal multi-agent system | `notebooks/p3_agents.ipynb` | P3-EXP-001 (preliminary, 22/40 executed) and P3-EXP-002 (v2, 40/40 executed, six `FAILED_MODEL` vision records) archived; **P3-EXP-003 executed** (40/40; the D-113 token-limit repair did not fix S02–S04: confirmed repetition loop, proposed fix D-114 not implemented); task success judged by one human + one AI evaluator (supplemental, D-119) |

Engineering decisions and experiments are logged chronologically in [`DECISIONS.md`](DECISIONS.md) (Parts 2/3 implementation: D-089 onwards). The Part 1 log is [`docs/part1/DECISIONS_P1.md`](docs/part1/DECISIONS_P1.md); its D-numbers after D-088 are a **separate namespace**, because the two logs diverged.

## Data location

Course data is **not** stored in this repository.

- **Local:** the Part 1 files are expected at `../DATA266_Lab2_Part1/`, relative to this repository's root, which is the professor-provided folder next to `implementation/`.
- **Kaggle:** attach the competition data. The notebook finds it under `/kaggle/input/`.
- **Parts 2/3:** the dataset and all models are downloaded from Hugging Face at run time into the persistent cache (`hf_cache`, below). Adapters, generated images, checkpoints and results live in the work directory, **outside** the repository.

## How to run

### Part 1
- `notebooks/p1_rag.ipynb` is the **final** Part 1 notebook, **P1-KAGGLE-V14-R1**, executed on Kaggle (one NVIDIA Tesla T4) with its saved outputs. Its generated 40-row submission is `eval/p1_submission.csv` (validator: `valid: 40 rows`; D-120).
- Run it on Kaggle with the competition data attached, a T4 GPU and Internet on (it installs its libraries at start), then **Run All**. It finds `Questions.csv` under `/kaggle/input/` (or `QUESTIONS_PATH`), writes `/kaggle/working/submission.csv` and `run_report.json`, and runs the professor's `validate_submission.py`. The saved run took 2,616 s of its 5,400 s budget.
- Environment recorded by the run: Python 3.13.16, torch 2.11.0+cu130, transformers 5.16.1, bitsandbytes 0.49.0 (Qwen3-VL-4B in 4-bit NF4), sentence-transformers 5.7.0, chromadb 1.5.9, pymupdf 1.28.2, rank-bm25 0.2.2, accelerate 1.14.0, numpy 2.1.3 (`requirements-p1.txt`). Model revisions are **not pinned**.
- History: P1-EXP-001 (the held-out golden-set run, `0adebfa`) and the P1-EXP-003 checkpoint (`eb87662`, local RTX 5090; `docs/part1/P1_EXP003_CHECKPOINT_MANIFEST.md`) are earlier versions kept in Git history. P1-EXP-004 and earlier Kaggle versions are not in this repository. V14-R1 was **not** evaluated on the golden set.

### GPU environment for Parts 2 and 3 (Docker, D-089)

`docker/` contains the reproducible environment: `Dockerfile` (base `pytorch/pytorch:2.14.1-cuda13.0-cudnn9-runtime`; torch/torchvision/triton/CUDA wheels protected by a constraints file), `compose.yaml`, `requirements-p2p3.in` (top-level) and `requirements-p2p3.lock.txt` (exact versions). `docker/.env` (git-ignored) holds `LAB2_WORK_DIR` and a random `JUPYTER_TOKEN`.

| Container path | Host path | Holds |
|---|---|---|
| `/app/implementation` | this repository | notebooks, `eval/`, `traces/` |
| `/app/data266_lab2_work/p2` | `$LAB2_WORK_DIR/p2` | checkpoints, adapters, 120 images, metrics, human-eval packet, HF staging |
| `/app/data266_lab2_work/p3` | `$LAB2_WORK_DIR/p3` | `inputs/v2/` (staged, hash-verified evaluation inputs), `experiments/<ID>/` results + report, integration/demo evidence, `hf_staging/`, `archive/` |
| `/app/data266_lab2_work/hf_cache`, `torch_cache` | same | model/dataset downloads (persist across containers) |

Start / stop (PowerShell, from `implementation\docker`):

```powershell
docker compose up -d            # builds on first use; Jupyter on http://127.0.0.1:8888 (local only)
docker compose logs lab2        # shows the Jupyter URL
docker compose down             # stops the container; all outputs stay in the mounted folders
```

Open the notebooks in one of two ways (kernel: **Python 3 (ipykernel)** — the container's Python 3.12):

1. **Recommended:** JupyterLab in the browser at `http://127.0.0.1:8888/lab?token=<JUPYTER_TOKEN from docker/.env>`, then `implementation/notebooks/…`. The kernel then starts in `notebooks/`, so the professor's run-information cell prints the Git commit.
2. VS Code: *Select Kernel → Existing Jupyter Server →* `http://127.0.0.1:8888/?token=<JUPYTER_TOKEN>` → **Python 3 (ipykernel)**. All notebook paths come from container environment variables (`LAB2_REPO_DIR`, `P2_WORK_DIR`, `P3_WORK_DIR`), so outputs land in the right place; only cell 1's `git rev-parse` depends on the kernel's working directory (the commit is recorded independently in every run manifest).

Gradio is published on `http://127.0.0.1:7860` only.

`HF_TOKEN` is never stored in files: set it in the PowerShell session before `docker compose up -d` (`$env:HF_TOKEN = "..."`) only when an authorized upload or a gated download is needed.

### Part 2

Set `MODE` in the configuration cell, then **Run All**:

- `SETUP_ONLY` (saved default): environment record, dataset download/clean/split (`eval/p2_split_manifest.json`), creates/verifies the frozen `eval/p2_prompts.csv` (+ `eval/p2_eval_freeze.json`), pins model revisions, self-checks. No model weights.
- `FULL_RUN`: trains run A (rank 4) and run B (rank 64) — identical data, batch order, noise/timestep RNG, optimizer, schedule and micro-batch plan; checkpoints every 250 steps; resumes after interruption; never retrains a completed run — then generates the 120 images (resumable), computes KID/CLIP/LPIPS/memorization, selects the final adapter by the pre-registered rule, prepares the blinded human evaluation, writes report tables/figures and stages Hugging Face folders. It **stops before training if `eval/` is not committed** (`REQUIRE_COMMITTED_EVAL_FILES`, D-045).
- `REPORT_ONLY`: no training or generation; scores real ratings from `eval/p2_human_ratings.csv` and rebuilds the report. The scoring run with the real ratings is saved as `notebooks/p2_finetune_REPORT_ONLY_human_eval.ipynb`: a headless copy whose only difference is the `MODE` line. `notebooks/p2_finetune.ipynb` keeps the `FULL_RUN` outputs (D-118).

Dataset `reach-vb/pokemon-blip-captions` (CC BY-NC-SA 4.0, copyrighted characters: non-commercial research only). Base model Stable Diffusion 1.5 (CreativeML OpenRAIL-M). Uploads stay off unless `UPLOAD_TO_HF = True` **and** `HF_UPLOAD_AUTHORIZATION = "UPLOAD AUTHORIZED BY TEAM"`.

### Part 3

Keep `EXPERIMENT_ID = "P3-EXP-003"`, set `MODE`, then **Run All**: `SETUP_ONLY` (default; no weights; stages + verifies inputs against the v2 freeze, writes the P3-EXP-003 freeze) → `INTEGRATION_RUN` (three real end-to-end requests with the Part 2 LoRA; LoRA ON/OFF verified) → `FULL_EVALUATION` (15 scenarios × critique on/off + 10 red-team cases; resumable; report) → `RESCORE_ONLY` (real human judgements, no model re-run) → `DEMO` (local Gradio, any valid image).

- Five agents (Planner, Vision, Prompt, Generation, Critique) share one pydantic `AgentState`; ≤ 2 revisions; one JSON trace per request (copied to `traces/<EXPERIMENT_ID>/`).
- Models: `Qwen/Qwen3-VL-4B-Instruct` (fallback `Qwen/Qwen2.5-VL-3B-Instruct`, recorded if used), SD 1.5 + the **Part 2 adapter read from `SELECTED_FINAL_ADAPTER.json`** (hash-verified; domain style is blocked, never served by base SD, when it is missing), `timbrooks/instruct-pix2pix` (documented fallback), CLIP ViT-L/14 — all pinned to the revisions used in P3-EXP-001.
- Text inside images is untrusted data and is never followed; generation/edit requests on images with instruction-like text (in any transcribed line, the joined transcription or the VLM description) are refused.
- **Evaluation versions:** `P3-EXP-001` = preliminary run with the v1 files (`eval/p3_scenarios.csv`, `eval/p3_redteam.csv`, `eval/p3_eval_freeze.json`); 18/40 records `NOT_RUN` (missing team photos). Archived and read-only. `P3-EXP-002` = post-preliminary amendment v2 (`eval/p3_scenarios_v2.csv`, `eval/p3_redteam_v2.csv`, `eval/p3_input_manifest_v2.csv`, `eval/p3_eval_freeze_v2.json`; DECISIONS.md D-105 – D-112): 40/40 executed, six `FAILED_MODEL` vision records (S02–S04, both conditions); archived and read-only. `P3-EXP-003` = the same v2 files and inputs after one disclosed configuration repair motivated by those failures (D-113: vision `max_new_tokens` 450 → 1024 plus generation diagnostics; freeze `eval/p3_eval_freeze_v2_P3-EXP-003.json`), so it is **not** an untouched hold-out. **No personal photographs are needed.**
- **Inputs (v2):** 3 held-out Part 2 TEST images (`p2_test:2/32/34`), 5 Wikimedia Commons photographs (CC BY / CC BY-SA / public domain, attribution in the manifest), 3 code-drawn injection posters, 4 deliberately broken files. Staged into `$LAB2_WORK_DIR/p3/inputs/v2/` and verified by SHA-256 before every use; nothing is ever substituted.

#### Part 3 — evaluation P3-EXP-003, step by step

1. **Input verification + freeze:** `MODE = "SETUP_ONLY"` → Run All. It re-verifies the staged inputs in `$LAB2_WORK_DIR/p3/inputs/v2/` against `eval/p3_eval_freeze_v2.json` (bytes must be identical), checks that the v2 CSVs are unchanged, runs the self-checks (including the D-113 truncation check) and writes `eval/p3_eval_freeze_v2_P3-EXP-003.json`. If an input must be re-downloaded and Wikimedia answers HTTP 429, open the failing file's page (URL in the error), use *Download → Original file*, save it under `inputs/v2/originals/<name shown in the error>` and Run All again.
2. **Freeze in Git** (commands below).
3. **Full evaluation:** `MODE = "FULL_EVALUATION"` → Run All (stops if either freeze or a v2 file is not committed unchanged, or if the code changed after the freeze; resumable). All 40 requests run again into `$LAB2_WORK_DIR/p3/experiments/P3-EXP-003/`; traces go to `traces/P3-EXP-003/`.
4. **Human rescoring:** follow `$LAB2_WORK_DIR/p3/experiments/P3-EXP-003/human_packet/JUDGING_INSTRUCTIONS.txt`, save the filled files as `eval/p3_human_P3-EXP-003_*.csv`, then `MODE = "RESCORE_ONLY"` → Run All.
5. **Demo:** `MODE = "DEMO"` → Run All → `http://127.0.0.1:7860`.

### Freeze the pre-experiment state (run these yourself)

The extracted ZIP has no `.git`. Git is installed in the container (the host has none):

```powershell
docker exec -it data266-lab2 bash
```
```bash
cd /app/implementation
git init -b main
git config user.name  "<your name>"; git config user.email "<your email>"
git status --short            # review: no datasets, weights, .env or tokens
git add -A && git commit -m "P2/P3 implementation + frozen Part 3 evaluation files (pre-experiment)"
# after Part 2 SETUP_ONLY and Part 3 SETUP_ONLY have created eval/p2_* and eval/p3_eval_freeze.json:
git add eval/ && git commit -m "Freeze Part 2 prompts/split and Part 3 evaluation hashes before any experiment"
git log --oneline -3
```

Clear notebook outputs before committing code changes (outputs change the notebook hash recorded in run manifests). Push only after team approval. Exception: `notebooks/p3_agents.ipynb` is committed with the outputs of the P3-EXP-003 `FULL_EVALUATION` run (`MODE = "FULL_EVALUATION"`; code fingerprint identical to the freeze, because the fingerprint ignores outputs and the `MODE` line). The `SETUP_ONLY`, `INTEGRATION_RUN` and DEMO-verification runs are archived in `$LAB2_WORK_DIR/p3/archive/P3-EXP-003/`.

**Part 3 v2 freeze (before P3-EXP-002):**

```bash
cd /app/implementation
git status --short                       # expect: notebooks/p3_agents.ipynb, eval/*_v2.csv, README/DECISIONS/AI_USAGE, traces/P3-EXP-001/
git add traces/P3-EXP-001                # preliminary evidence, unchanged
git commit -m "Archive preliminary Part 3 evaluation traces (P3-EXP-001)"
git add notebooks/p3_agents.ipynb eval/p3_scenarios_v2.csv eval/p3_redteam_v2.csv eval/p3_input_manifest_v2.csv README.md DECISIONS.md AI_USAGE.md
git commit -m "Part 3 v2: post-preliminary amendment (dataset-sourced inputs, D-105..D-112); code freeze before P3-EXP-002"
# now run MODE="SETUP_ONLY" (creates eval/p3_eval_freeze_v2.json), then:
git add eval/p3_eval_freeze_v2.json
git commit -m "Freeze Part 3 v2 evaluation inputs and configuration before P3-EXP-002"
git log --oneline -4
```

`notebooks/p2_finetune.ipynb` is also modified (Part 2 run outputs); commit it separately if the team wants those outputs in the repository.

**P3-EXP-003 freeze (D-113):** the v2 freeze commands above are historical (P3-EXP-002, commit `ddbd4f4`); do not re-run them.

```bash
cd /app/implementation
git status --short          # expect: .gitignore, AI_USAGE.md, DECISIONS.md, README.md, notebooks/p3_agents.ipynb,
                            #         notebooks/p2_finetune.ipynb, traces/P3-EXP-002/ (no traces/*.jpg: now ignored)
git add traces/P3-EXP-002   # P3-EXP-002 evidence, unchanged
git commit -m "Preserve P3-EXP-002 traces (v2 evaluation, 40/40 executed)"
git add .gitignore notebooks/p3_agents.ipynb README.md DECISIONS.md AI_USAGE.md
git commit -m "P3-EXP-003: vision max_new_tokens 450->1024 + generation diagnostics (D-113); code freeze"
# now run MODE="SETUP_ONLY" with EXPERIMENT_ID="P3-EXP-003" (creates eval/p3_eval_freeze_v2_P3-EXP-003.json), then:
git add eval/p3_eval_freeze_v2_P3-EXP-003.json
git commit -m "Freeze P3-EXP-003 evaluation configuration (v2 files and inputs unchanged)"
git log --oneline -4
```

### Manual inputs (never generated by code)

- **No photographs are needed for Part 3** (v2 uses dataset-sourced, licensed inputs; D-105, D-109). The former `team_photo_*` / `team_person_01` inputs are retired.
- **Part 2 human ratings** → `eval/p2_human_ratings.csv` (**done**: 3 raters, 150 rows, committed in `e53130b` before scoring).
- **Part 3 judgements (P3-EXP-003).** `member_a` completed all 52 judgements in the rating UI. `member_b` did not complete. A supplemental AI evaluation was added (D-119). The `eval/p3_human_*` files that `RESCORE_ONLY` reads were not created, because only one member judged. The P3-EXP-002 packet stays in its own directory, unchanged.

## Submission documents

- **Final evidence:** `SUBMISSION_CHECKLIST.md` lists readiness (COMPLETE / PENDING / BLOCKED / NOT VERIFIED), Hugging Face upload steps, and GitHub/Canvas steps. Final automated evidence is P2-EXP-001 and P3-EXP-003 (D-115).
- `HUMAN_EVALUATION.md`: instructions for the 3 Part 2 raters and the 2 Part 3 judges, file formats, merging, disagreement resolution, `REPORT_ONLY` / `RESCORE_ONLY`.
- `report/data266_lab2_report.tex`: IEEE draft for Parts 1–3 (Overleaf, IEEEtran; figures in `report/figures/`). The Part 2 human results (D-118) and the Part 3 human/AI evaluator results (D-119) are filled in. Repository access, UI screenshots, Hugging Face publication and contributions are still marked `PENDING`.
- `links.txt`: links required for the Canvas ZIP (GitHub URL known; tags, Hugging Face uploads and the Kaggle link are pending).
- `publication/`: `HF_PUBLICATION_PLAN.md` and `hf_publication_manifest.json` (Hugging Face approval manifest with hashes; nothing uploaded) and `build_canvas_zip.py` (deterministic Canvas ZIP; refuses the final name while items are missing).

## Results recorded so far (report evidence)

Machine-generated values copied from the saved records. Sources: `$LAB2_WORK_DIR/p2/results/P2-EXP-001/report_summary.json`, `$LAB2_WORK_DIR/p3/experiments/P3-EXP-00{2,3}/evaluation_summary.json`. Part 2 human ratings and the Part 3 human + AI evaluations are below.

**Part 1** (final notebook P1-KAGGLE-V14-R1; the golden-set numbers are historical, from earlier code):
- Final submission (V14-R1, Kaggle T4): 40 rows, validator `valid: 40 rows`; statuses answered 32, conflict 3, session_override 3, not_found 2; 2 rows retried, 0 fallbacks; runtime 2,616 s. Its Kaggle score is not recorded in this repository. Not evaluated on the golden set.
- Golden set of 25 questions. P1-EXP-001 is the only held-out run (saved output `0adebfa`):

  | | baseline | final |
  |---|---|---|
  | correct | 14/25 | 13/25 |
  | Recall@5 | 0.764 | 0.882 |
  | citation accuracy | 0.64 | 0.84 |
  | figure-reference F1 | 0.627 | 0.793 |
  | median s/question | 1.77 | 2.03 |

- P1-EXP-003 final mode (historical development measurement, log only): 14/25.
- Kaggle public leaderboard of historical runs: 0.636 (P1-EXP-002) and 0.832 (P1-EXP-003). These scores do not belong to the final V14-R1 submission.

**Part 2 (P2-EXP-001, 20 prompts × 2 seeds per model; KID subset size 20, high variance, see the std):**

| model | KID ± std | CLIP all / in-domain / out-of-domain / compositional | LPIPS seed diversity | NSFW-flagged images | peak train GPU MB | GPU-h |
|---|---|---|---|---|---|---|
| base SD 1.5 | 0.0823 ± 0.0111 | 28.87 / 27.25 / 29.69 / 31.28 | 0.834 | 1 | — | — |
| LoRA A (r4) — **selected** | 0.0619 ± 0.0092 | 27.92 / 26.75 / 30.03 / 28.13 | 0.744 | 3 | 6,307 | 0.067 |
| LoRA B (r64) | 0.0825 ± 0.0089 | 26.04 / 24.71 / 30.18 / 24.54 | 0.711 | 8 | 6,542 | 0.069 |

Memorization (CLIP image cosine of top-1 training neighbour, 10 in-domain generations): base mean 0.644, A 0.723 (max 0.826), B 0.753 (max 0.867). The real test-vs-train reference is 0.892 (max 0.953), so no generation exceeds the natural similarity level.

**Part 2 human evaluation (`HUMAN_EVALUATION_COMPLETE`).** These are human preferences, separate from the automated KID/CLIP/LPIPS scores above. 25 blinded pairs of LoRA A vs base SD 1.5, each judged by RATER_1–3 on two criteria (left/right, no ties); 75 judgments per criterion. Win rate = share of judgments preferring LoRA A.

| criterion | all judgments | majority vote per pair | RATER_1 / 2 / 3 | unanimous pairs (A / base) | Fleiss' κ (post-hoc) |
|---|---|---|---|---|---|
| domain_style | 29/75 = 38.7 % | 10/25 = 40 % | 9 / 13 / 7 of 25 | 12 (3 / 9) | 0.27 |
| prompt_match | 31/75 = 41.3 % | 10/25 = 40 % | 9 / 12 / 10 of 25 | 18 (7 / 11) | 0.62 |

- Raters preferred the **base** model more often on both criteria, so the KID-based selection of A is not confirmed by human preference. The selection is not changed.
- Post-hoc and not pre-registered: majority-vote Wilson 95 % CI 23–59 %, exact binomial p = 0.42 against 50 %. With 25 pairs the result cannot be distinguished from no preference.
- Pair H22 has a safety-blacked A image. Without it the rates are 40.3 % / 43.1 %.
- Sources: `report_summary.json` → `human` (official); `$LAB2_WORK_DIR/p2/audit/report_only_human_20261118T030113Z/` (post-hoc statistics, hash audit). See D-118.

**Part 3 (automated diagnostics, not task success; P3-EXP-003 is a disclosed post-evaluation correction, not a hold-out):**

| metric | P3-EXP-002 (vision limit 450) | P3-EXP-003 (vision limit 1024) |
|---|---|---|
| executed / NOT_RUN / runner failures | 40 / 0 / 0 | 40 / 0 / 0 |
| `FAILED_MODEL` records | 6 (S02–S04 × 2) | 6 (S02–S04 × 2) |
| Vision-agent JSON failures (of 22 vision calls) | 6 (raw replies not saved) | 6 (all at 1024/1024 tokens, no EOS: repetition loop) |
| automated checks with / without critique | 12/15, 11/15 | 12/15, 11/15 |
| mean revisions with critique | 0.8 | 0.8 |
| median latency all / with / without / red-team (s) | 8.13 / 11.43 / 8.41 / 1.53 | 7.96 / 14.10 / 8.25 / 1.54 |
| red-team confirmed attack successes / defended / pending human | 0 / 8 / 2 | 0 / 8 / 2 |
| scenario success judged on the blinded packet | — | Evaluator 1: 20/30 (11 / 9 with / without critique); Evaluator 2: 10/30 (6 / 4); see below |

**Part 3 task-success evaluation (P3-EXP-003; supplemental, D-119).**
- **Evaluators.** Evaluator 1 is one human team member (`member_a`), who completed all 52 judgements. Evaluator 2 is an **AI** (Claude Opus 5.5), disclosed in `AI_USAGE.md`. The written requirement of two team members is not met; the team reports a verbal instructor allowance for AI judging, which is not confirmed in writing.
- **Scenarios.** 20/30 agree, Cohen's κ = 0.40. All 10 disagreements are human PASS / AI FAIL.
- **Critic attempts.**

  | comparison | agreement | κ |
  |---|---|---|
  | Evaluator 1 vs Evaluator 2 | 14/20 | 0.29 |
  | Evaluator 1 vs Critique agent | 16/20 | 0.55 |
  | Evaluator 2 vs Critique agent | 18/20 | 0.62 |

  ACCEPT counts: agent 4, Evaluator 1 8, Evaluator 2 2.
- **Red team R01/R02.** The human marked both attacks as followed; the AI marked both as not followed. The saved records show R01 REFUSED and R02 transcribing the sign as untrusted data, with no image and no Generation agent in either case. The attack-success count is 0/8 for the automatically decided cases, and 0/10 or 2/10 overall depending on the unresolved R01/R02 verdicts.
- **Disagreements.** 18 of 52 items. They are **unresolved**: no adjudicated or combined score is reported.
- **Sources:**
  - `eval/p3_ai_judge_P3-EXP-003_*` (AI files and provenance);
  - `eval/p3_ai_vs_human_P3-EXP-003_{REPORT.md,comparison.json}`;
  - the human file `eval/p3_member_a_judgements_P3-EXP-003.csv`, a byte-identical copy of `$LAB2_WORK_DIR/p3/human_eval_ui/P3-EXP-003/member_a_completed.csv` (sha256 `0b7bb9db…`);
  - the frozen P3-EXP-003 summaries, copied unchanged: `eval/p3_P3-EXP-003_{evaluation_summary.json,experiment_manifest.json,report_summary.md,system_card.md,*.csv}`.

## 16 GB GPU compatibility

All stages are designed for one 16 GB GPU: one visible GPU (`CUDA_VISIBLE_DEVICES=0`), an optional PyTorch allocator cap at 16,384 MB (`ENFORCE_VRAM_CAP`), a memory probe that picks the micro-batch / gradient checkpointing, sequential model residency in Part 2, and in Part 3 the VLM + SD + CLIP co-resident with SD moved to the CPU while instruct-pix2pix runs (`RESIDENCY = "offload"` as a lower-memory alternative). **The allocator cap on the RTX 5090 is only a preliminary check; it does not prove real T4/16 GB compatibility.** Not yet tested on real 16 GB hardware: peak memory and speed of training, IP2P edits next to the VLM, and the fp16 (no bf16) path of the VLM on a T4.

## Dependencies

`requirements.txt` holds the initial cross-part compatibility constraints (`DECISIONS.md` D-040). Parts 2 and 3 use the Docker environment above; its exact versions are in `docker/requirements-p2p3.lock.txt` (resolved by a pip dry run, `pip check`: no broken requirements).

## Hosted APIs

None used. All models run locally; their exact Hub revisions are recorded in each experiment manifest.
