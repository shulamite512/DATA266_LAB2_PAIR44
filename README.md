# DATA 266 Lab 2 — Team `[TEAM ## — TO BE FILLED]`

Repository for DATA 266 (Fall 2026) Lab 2. GitHub name: `data266-lab2-team[##]`.

| Part | Topic | Notebook | Status |
|------|-------|----------|--------|
| 1 | Multimodal RAG over a read-only knowledge base (Kaggle) | `notebooks/p1_rag.ipynb` | Skeleton only |
| 2 | Fine-tuning diffusion models | `notebooks/p2_finetune.ipynb` | Full pipeline implemented (training, 120 images, metrics, human-eval materials, HF staging). **Not yet executed**: no adapter, image or metric exists yet |
| 3 | Multimodal multi-agent system | `notebooks/p3_agents.ipynb` | Real-model pipeline, integration run, full evaluation and Gradio implemented. **Not yet executed**: depends on the Part 2 adapter |

Engineering decisions and experiments are logged chronologically in [`DECISIONS.md`](DECISIONS.md) (Parts 2/3 implementation: D-089 onwards).

## Data location

Course data is **not** stored in this repository.

- **Local:** the Part 1 files are expected at `../DATA266_Lab2_Part1/`, relative to this repository's root, which is the professor-provided folder next to `implementation/`.
- **Kaggle:** attach the competition data. The notebook finds it under `/kaggle/input/`.
- **Parts 2/3:** the dataset and all models are downloaded from Hugging Face at run time into the persistent cache (`hf_cache`, below). Adapters, generated images, checkpoints and results live in the work directory, **outside** the repository.

## How to run

### Part 1
_Pending: implementation not started._ The notebook will be run top to bottom with **Restart & Run All** on a Kaggle GPU. It reads `QUESTIONS_PATH` (default `Questions.csv`) and writes `submission.csv`.

### GPU environment for Parts 2 and 3 (Docker, D-089)

`docker/` contains the reproducible environment: `Dockerfile` (base `pytorch/pytorch:2.14.1-cuda13.0-cudnn9-runtime`; torch/torchvision/triton/CUDA wheels protected by a constraints file), `compose.yaml`, `requirements-p2p3.in` (top-level) and `requirements-p2p3.lock.txt` (exact versions). `docker/.env` (git-ignored) holds `LAB2_WORK_DIR` and a random `JUPYTER_TOKEN`.

| Container path | Host path | Holds |
|---|---|---|
| `/app/implementation` | this repository | notebooks, `eval/`, `traces/` |
| `/app/data266_lab2_work/p2` | `$LAB2_WORK_DIR/p2` | checkpoints, adapters, 120 images, metrics, human-eval packet, HF staging |
| `/app/data266_lab2_work/p3` | `$LAB2_WORK_DIR/p3` | `inputs/` (team photos), evaluation results, traces, integration/demo evidence |
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
- `REPORT_ONLY`: no training or generation; scores real ratings from `eval/p2_human_ratings.csv` and rebuilds the report.

Dataset `reach-vb/pokemon-blip-captions` (CC BY-NC-SA 4.0, copyrighted characters: non-commercial research only). Base model Stable Diffusion 1.5 (CreativeML OpenRAIL-M). Uploads stay off unless `UPLOAD_TO_HF = True` **and** `HF_UPLOAD_AUTHORIZATION = "UPLOAD AUTHORIZED BY TEAM"`.

### Part 3

Set `MODE`, then **Run All**: `SETUP_ONLY` (default; no weights) → `INTEGRATION_RUN` (three real end-to-end requests with the Part 2 LoRA; LoRA ON/OFF verified) → `FULL_EVALUATION` (15 scenarios × critique on/off + 10 red-team cases; resumable) → `RESCORE_ONLY` (real human judgements, no model re-run) → `DEMO` (local Gradio).

- Five agents (Planner, Vision, Prompt, Generation, Critique) share one pydantic `AgentState`; ≤ 2 revisions; one JSON trace per request (copied to `traces/<EXPERIMENT_ID>/`).
- Models: `Qwen/Qwen3-VL-4B-Instruct` (fallback `Qwen/Qwen2.5-VL-3B-Instruct`, recorded if used), SD 1.5 + the **Part 2 adapter read from `SELECTED_FINAL_ADAPTER.json`** (hash-verified; domain style is blocked, never served by base SD, when it is missing), `timbrooks/instruct-pix2pix` (documented fallback), CLIP ViT-L/14.
- Text inside images is untrusted data and is never followed; generation/edit requests on images with instruction-like text are refused.

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

Clear notebook outputs before committing code changes (outputs change the notebook hash recorded in run manifests). Push only after team approval.

### Manual inputs (never generated by code)

- **Team photos** in `$LAB2_WORK_DIR/p3/inputs/`: `team_photo_01` (scene with ≥ 3 objects), `team_photo_02` (indoor or outdoor scene with a clear main subject), `team_photo_03` (a photo suitable for sketch/enhance), `team_photo_04` (scene with plants/trees, also used for the Pokémon-style transfer), `team_person_01` (a consenting team member; red-team real-person cases). `.jpg/.jpeg/.png/.webp`. Missing files → their items are `NOT_RUN`.
- **Part 2 human ratings** → `eval/p2_human_ratings.csv` (≥ 3 raters; template and rater packet in the work directory).
- **Part 3 judgements** → `eval/p3_human_judgements.csv` and `eval/p3_critic_human_agreement.csv` (templates next to the results).

## 16 GB GPU compatibility

All stages are designed for one 16 GB GPU: one visible GPU (`CUDA_VISIBLE_DEVICES=0`), an optional PyTorch allocator cap at 16,384 MB (`ENFORCE_VRAM_CAP`), a memory probe that picks the micro-batch / gradient checkpointing, sequential model residency in Part 2, and in Part 3 the VLM + SD + CLIP co-resident with SD moved to the CPU while instruct-pix2pix runs (`RESIDENCY = "offload"` as a lower-memory alternative). **The allocator cap on the RTX 5090 is only a preliminary check; it does not prove real T4/16 GB compatibility.** Not yet tested on real 16 GB hardware: peak memory and speed of training, IP2P edits next to the VLM, and the fp16 (no bf16) path of the VLM on a T4.

## Dependencies

`requirements.txt` holds the initial cross-part compatibility constraints (`DECISIONS.md` D-040). Parts 2 and 3 use the Docker environment above; its exact versions are in `docker/requirements-p2p3.lock.txt` (resolved by a pip dry run, `pip check`: no broken requirements).

## Hosted APIs

None used. All models run locally; their exact Hub revisions are recorded in each experiment manifest.
