# DATA 266 Lab 2 — Pair Programming Team 44

**Members:** Parth Patel ([@Parthp28](https://github.com/Parthp28)) · Chelsi Shulamite ([@shulamite512](https://github.com/shulamite512))

This repository contains the three Lab 2 systems:
- **Part 1:** multimodal RAG over three economics PDFs, entered in the class Kaggle competition.
- **Part 2:** LoRA fine-tuning of Stable Diffusion 1.5.
- **Part 3:** a five-agent multimodal image system.

Both members built complete, independent implementations of all three parts. The team selected the strongest implementation for each part. The other implementations are kept as alternatives, and both members' full Git histories are preserved.

## Final selected notebooks (graded)

| Part | Selected implementation | Notebook (executed, outputs saved) | Main evidence |
|---|---|---|---|
| 1 | **Parth** · P1-KAGGLE-V14-R1 | [`notebooks/p1_rag.ipynb`](notebooks/p1_rag.ipynb) | `eval/p1_submission.csv`, `eval/p1_golden_set.csv`, `requirements-p1.txt` |
| 2 | **Chelsi** · Naruto LoRA, run 1 (rank 8) | [`notebooks/p2_finetune.ipynb`](notebooks/p2_finetune.ipynb) | `eval/p2_results/`, `eval/p2_human_ratings.csv`, [`notebooks/evaluation/chelsi_human_eval_results.ipynb`](notebooks/evaluation/chelsi_human_eval_results.ipynb), `prompts/` |
| 3 | **Parth** · P3-EXP-003 | [`notebooks/p3_agents.ipynb`](notebooks/p3_agents.ipynb) | `eval/p3_*`, `traces/P3-EXP-003/` |

> **Part 3 uses Parth's own Part 2 adapter, not the selected Part 2 model.**
> - P3-EXP-003 ran with Parth's **Pokémon LoRA A**: rank 4, sha256 `20d8d671…`, from his Part 2 experiment P2-EXP-001.
> - Its domain-style scenarios and rubrics assume the Pokémon style.
> - It was **not** run with Chelsi's selected Naruto LoRA, and the two adapters are not interchangeable.

## Overview of the selected implementations

**Part 1: Multimodal RAG (Parth, P1-KAGGLE-V14-R1).**
- **Ingestion:** PyMuPDF extracts text, figures and tables. A trust manifest flags low-trust content, so Document 3's Appendix C is indexed but never used as evidence.
- **Retrieval:** a label router; `bge-large-en-v1.5` dense retrieval and BM25, fused with RRF (k = 60); the `bge-reranker-v2-m3` cross-encoder on the CPU (20 → 6); a revision and conflict registry.
- **Answers:** Qwen3-VL-4B-Instruct, loaded in 4-bit NF4, writes JSON answers with greedy decoding. Conversation memory is kept per conversation.
- **Final run:** on a Kaggle Tesla T4, 2,616 s out of a 5,400 s budget. The 40-row submission passed the course validator (`valid: 40 rows`). Statuses: answered 32, conflict 3, session_override 3, not_found 2.
- **Not recorded:**
  - The Kaggle score of this V14-R1 submission is not recorded in the repository.
  - V14-R1 itself was not evaluated on the golden set.
  - The held-out golden-set results of earlier versions are documented in `docs/DECISIONS.md` and `docs/part1/`.

**Part 2: Stable Diffusion 1.5 LoRA (Chelsi, Naruto).**
- **Data:** `lambdalabs/naruto-blip-captions`, 1,221 images, 1,099 train / 122 test, 512×512.
- **Training:** two LoRA runs, rank 8 and rank 32. Each ran 1,500 steps with effective batch 4 and learning rate 1e-4 on a T4, peak 3.7 GB.
- **Generation:** 3 models × 20 prompts × 2 seeds.
- **Automated metrics** (base / rank 8 / rank 32):

  | Metric | Base | Rank 8 | Rank 32 |
  |---|---|---|---|
  | KID, in-domain | 0.1030 | 0.0359 | 0.0451 |
  | CLIP, in-domain | 30.14 | 28.66 | 27.15 |
  | LPIPS diversity | 0.7187 | 0.7210 | 0.6925 |
  | NSFW-flagged images | 0 | 2 | 4 |

- **Human evaluation:** 25 blinded pairs, final model vs base, 2 raters. The final model won 64% of style judgements and 50% of prompt-match judgements.
- **Final model:** run 1 (rank 8). A memorization check is included.

**Part 3: Five-agent system (Parth, P3-EXP-003).**
- **Agents:** Planner, Vision, Prompt, Generation and Critique, sharing one typed state, with at most 2 revisions and a JSON trace for every request.
- **Models:** Qwen3-VL-4B, SD 1.5 with Parth's LoRA A, InstructPix2Pix and CLIP.
- **Runs:** 15 scenarios with and without critique, plus 10 red-team cases; 40/40 executed.
- **Automated checks:** 12/15 with critique and 11/15 without.
- **Red team:** no confirmed attack success among the 8 cases decided automatically.
- **Known failure:** six FAILED_MODEL records, caused by a confirmed vision-model repetition loop.
- **Latency (median):** 7.96 s overall; 14.10 s with critique and 8.25 s without.
- **Task success:** judged by one human team member and, as a disclosed supplemental second evaluator, an AI model (Claude Opus 5.5). They agreed on 20/30 scenarios (Cohen's κ = 0.40). 18 disagreements, including R01/R02, are reported **unresolved**.
- **Details:** `docs/HUMAN_EVALUATION.md`, `docs/DECISIONS.md` (D-119, D-121).

## Repository guide

```
notebooks/                 the three selected, executed notebooks (p1_rag, p2_finetune, p3_agents)
  evaluation/              human-evaluation notebooks: chelsi_human_eval_results (Part 2 + Chelsi's alternatives),
                           p3_human_rating_ui and p3_disagreement_review (Parth's Part 3 judging tools)
  alternatives/parth/      Parth's Part 2 (Pokemon LoRA, P2-EXP-001) + its human-evaluation notebooks
  alternatives/chelsi/     Chelsi's Part 1 (p1_rag, p1_eval) and Part 3 (p3_agents)
eval/                      evaluation data and evidence
  p1_*                     Part 1 (Parth): golden set (25 questions, frozen before any code), final submission
  p2_human_ratings.csv     Part 2 (Chelsi): blinded human ratings
  p2_results/              Part 2 (Chelsi): data report, training runs, KID/CLIP/LPIPS, memorization, human-eval key/results, figures
  p2_prompts.csv, p2_split_manifest.json, p2_eval_freeze.json
                           Parth's Part 2 freezes; kept here because Parth's Part 3 verifies them
  p3_*                     Part 3 (Parth): frozen scenarios, red-team cases, input manifest, freezes, P3-EXP-003 summaries,
                           human evaluator file, AI-evaluator files and the human-vs-AI comparison
  alternatives/chelsi/     Chelsi's Part 1 and Part 3 evaluation files and results
  alternatives/parth/      Parth's Part 2 human ratings
traces/                    Part 3 per-request JSON traces (P3-EXP-002/003); traces/alternatives/chelsi/ = Chelsi's Part 3 traces
src/                       Chelsi's Python package (common, p1, p2, p3) used by her notebooks, including the selected Part 2
prompts/                   Part 2 evaluation prompts (Chelsi; fixed before training)
tools/                     Chelsi's notebook builders and upload-zip script
docker/                    Parth's Docker environment and dependency lock file (Part 3)
docs/                      decision log, human-evaluation protocol, Part 1 history, IEEE report source, HF publication plan,
                           each member's original README (README_chelsi.md, REPRODUCE_PARTH.md), detailed AI-use log
requirements.txt           pinned dependencies for Chelsi's notebooks (selected Part 2)
requirements-p1.txt        versions recorded by the final Part 1 Kaggle run
links.txt                  Canvas links file
CONTRIBUTIONS.md, AI_USAGE.md
```

## Installation and reproduction

**Part 1: `notebooks/p1_rag.ipynb`, on Kaggle.**
1. Attach the competition data.
2. Choose a T4 GPU and turn Internet on; the notebook installs its libraries at start.
3. Run All. The notebook finds `Questions.csv` under `/kaggle/input/`, writes `/kaggle/working/submission.csv` and `run_report.json`, and runs `validate_submission.py`.

Versions are in `requirements-p1.txt`: Python 3.13.16, torch 2.11.0+cu130, transformers 5.16.1, bitsandbytes 0.49.0. Model revisions are not pinned.

**Part 2: `notebooks/p2_finetune.ipynb`, on Colab or Kaggle with a T4 and Internet on.**
1. Cell 1 clones this repository at its tag, installs the pinned `requirements.txt`, and prints the commit, versions, GPU and seed (266). Set `REPO_URL` there; set `HF_USER` in `src/p2/config.py` and an `HF_TOKEN` secret only for the upload.
2. The notebook runs data preparation, both training runs, generation, KID/CLIP/LPIPS, the blinded pairs and the memorization check.
3. The raters fill `eval/p2_human_ratings.csv`.
4. Human-evaluation numbers: `notebooks/evaluation/chelsi_human_eval_results.ipynb`. Because of the repository reorganization, that notebook's Part 2 cell reads the rating key from `part2/Chelsi/human_eval_key.csv`, which is now `eval/p2_results/human_eval_key.csv`.

**Part 3: `notebooks/p3_agents.ipynb`, in Parth's Docker environment on one GPU.**
1. From `docker/`, set `LAB2_WORK_DIR` in `docker/.env` and run `docker compose up -d`. This mounts the repository root as `/app/implementation`.
2. Open the notebook with the container's Jupyter kernel.
3. Set `MODE`, then Run All. The modes are `SETUP_ONLY`, `INTEGRATION_RUN`, `FULL_EVALUATION`, `RESCORE_ONLY` and `DEMO` (local Gradio).

The notebook reads `eval/p3_*` and writes traces to `traces/<experiment>/`. It needs Parth's LoRA A, which is produced by `notebooks/alternatives/parth/p2_finetune.ipynb` (`FULL_RUN`, in the same environment) and has not been published to Hugging Face. Full details: [`docs/REPRODUCE_PARTH.md`](docs/REPRODUCE_PARTH.md).

**Environments:**

| Part | Environment | Dependencies |
|---|---|---|
| 1 | Kaggle | `requirements-p1.txt` |
| 2 | Colab / Kaggle | `requirements.txt` |
| 3 | Docker | `docker/requirements-p2p3.lock.txt` (207 pins) |

**Alternative notebooks:**
- Their saved outputs are complete as committed.
- Chelsi's code reads fixed `eval/` paths. To re-run her Part 1/Part 3 evaluation, copy the files from `eval/alternatives/chelsi/` back to `eval/`. Path mapping: `docs/README_chelsi.md`.
- Parth's Part 2 `REPORT_ONLY` scoring reads `eval/p2_human_ratings.csv`. His ratings are in `eval/alternatives/parth/`.

## Links

| What | Link |
|---|---|
| Part 2 model, run 1 (final, rank 8) | https://huggingface.co/chels512/data266-lab2-naruto-run1-lora-r8 |
| Part 2 model, run 2 (rank 32) | https://huggingface.co/chels512/data266-lab2-naruto-run2-lora-r32 |
| Part 2 generated images | https://huggingface.co/datasets/chels512/data266-lab2-p2-generations |
| Chelsi's Kaggle notebook (alternative Part 1) | https://www.kaggle.com/code/chelsi512/notebookde18a5542e |

The Kaggle URL of the selected Part 1 notebook (V14-R1) and the Part 3 input-image dataset are not yet recorded; see `links.txt`.

## Contributions and AI use
- [`CONTRIBUTIONS.md`](CONTRIBUTIONS.md): who built and evaluated what.
- [`AI_USAGE.md`](AI_USAGE.md): AI tools, including the AI evaluator used in Part 3.
- Detailed logs: [`docs/DECISIONS.md`](docs/DECISIONS.md), [`docs/AI_USAGE_LOG_parth.md`](docs/AI_USAGE_LOG_parth.md).
