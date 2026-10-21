# DATA 266 Lab 2 — Team `[TEAM ## — TO BE FILLED]`

Repository for DATA 266 (Fall 2026) Lab 2. GitHub name: `data266-lab2-team[##]`.

| Part | Topic | Notebook | Status |
|------|-------|----------|--------|
| 1 | Multimodal RAG over a read-only knowledge base (Kaggle) | `notebooks/p1_rag.ipynb` | Skeleton only |
| 2 | Fine-tuning diffusion models | `notebooks/p2_finetune.ipynb` | Architecture and local smoke-test harness complete; GPU validation and training pending |
| 3 | Multimodal multi-agent system | `notebooks/p3_agents.ipynb` | Architecture and local smoke-test harness complete; GPU validation and full pipeline pending |

Engineering decisions and experiments are logged chronologically in [`DECISIONS.md`](DECISIONS.md).

## Data location

Course data is **not** stored in this repository.

- **Local:** the Part 1 files are expected at `../DATA266_Lab2_Part1/`, relative to this repository's root, which is the professor-provided folder next to `implementation/`.
- **Kaggle:** attach the competition data. The notebook finds it under `/kaggle/input/`.

## How to run

### Part 1
_Pending: implementation not started._ The notebook will be run top to bottom with **Restart & Run All** on a Kaggle GPU. It reads `QUESTIONS_PATH` (default `Questions.csv`) and writes `submission.csv`.

### Part 2
_Architecture and local smoke-test harness complete; GPU validation and training pending._

- Dataset: `reach-vb/pokemon-blip-captions` (833 images, CC BY-NC-SA 4.0), downloaded from Hugging Face at run time. Base model: Stable Diffusion 1.5. Run A uses LoRA rank 4 and run B uses LoRA rank 64; everything else is identical.
- Smoke test: set `RUN_SMOKE_TEST = True` in the configuration cell. The P2-L\* stages run on CPU; the P2-S\* stages need a CUDA GPU.
- `RUN_TRAINING` and `RUN_EVALUATION` must stay `False`: real training and evaluation are not implemented yet.
- Adapters, generated images and caches are written outside the repository (`$P2_WORK_DIR`, default `~/data266_lab2_work/p2`). Uploads use `$HF_TOKEN`.

### Part 3
_Architecture and local smoke-test harness complete; GPU validation and full pipeline pending._

- Five agents (Planner, Vision, Prompt, Generation, Critique) are plain Python functions sharing one pydantic `AgentState`. The critique loop allows at most 2 revisions. Each request produces a JSON trace.
- Models: the VLM shared with Part 1 (Qwen3-VL-4B candidate) and Stable Diffusion 1.5. Edits use instruct-pix2pix (a candidate), with a deterministic fallback. The Part 2 LoRA is used only when `GENERATOR_MODE = "p2_lora"` and its real Hugging Face repository is configured.
- Text found inside an image is treated as untrusted data and is never followed. Generation or edit requests on images containing instruction-like text are refused.
- Smoke test: set `RUN_SMOKE_TEST = True`. The P3-L\* stages use mock models on CPU; the P3-S\* stages need a CUDA GPU.
- Demo: set `RUN_PIPELINE = True`, then run `launch_app(build_app())`. It runs locally only (`share=False`).

## Dependencies

`requirements.txt` holds **initial compatibility constraints**, not final pins (`DECISIONS.md` D-040). Install it on Kaggle without changing the preinstalled torch build:

```bash
pip install -r requirements.txt "torch==$(python -c 'import torch; print(torch.__version__)')"
```

Exact versions will be taken from the successful Kaggle environment and verified before the first Git commit.

## Hosted APIs

None used so far. Any hosted LLM, VLM or image-generation API will be listed here with its exact model version.
