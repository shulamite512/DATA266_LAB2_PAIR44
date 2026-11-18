# DATA 266 Lab 2 - Pair 44

Multimodal RAG (Part 1), Stable Diffusion LoRA fine-tuning (Part 2) and a five-agent image system (Part 3).
Everything runs on **one 16 GB GPU** (Kaggle T4/P100 or Colab T4). Seed = 266 everywhere.

## Models and services used
| Purpose | Model (version) | Where |
|---|---|---|
| Part 1 VLM (figure descriptions + answers), **final submission** | `Qwen/Qwen2.5-VL-7B-Instruct` (local, 4-bit NF4, `BACKEND = "qwen7b"`) | Hugging Face Hub |
| Part 3 VLM (planner, vision, prompts, critic) | `Qwen/Qwen2.5-VL-3B-Instruct` (local, fp16) | Hugging Face Hub |
| Part 1 text embeddings | `BAAI/bge-small-en-v1.5` | local |
| Part 1 reranker (bonus) | `BAAI/bge-reranker-base` | local |
| Part 2 base model | `stable-diffusion-v1-5/stable-diffusion-v1-5` | local |
| Part 2/3 CLIP score, memorization, critic | `openai/clip-vit-base-patch16` | local |
| NSFW output filter | `CompVis/stable-diffusion-safety-checker` | local |
| Part 3 edits | `timbrooks/instruct-pix2pix` | local |

Part 1 answer-model options (selected by `BACKEND` in the notebook; keep only the one used for the final submission):
| BACKEND | Model | Where |
|---|---|---|
| `qwen3b` | `Qwen/Qwen2.5-VL-3B-Instruct` (fp16) | local |
| `qwen7b` | `Qwen/Qwen2.5-VL-7B-Instruct` (4-bit NF4, bitsandbytes) | local |
| `qwen3` | `Qwen/Qwen2.5-VL-7B-Instruct` (4-bit) for figure descriptions + `Qwen/Qwen3-14B` (4-bit NF4, non-thinking) for answers | local |
| `gemini` | **Hosted API:** Google Gemini API via `google-genai`, model `gemini-4-hydrogen` (or the version printed in the notebook), temperature 0 | Google AI Studio |
| `claude` | **Hosted API:** Anthropic Messages API, model `claude-opus-5-5`, effort `medium`, server-side refusal fallback on (`fallbacks: "default"`) | Anthropic API |

## Repository layout
```
src/common/   VLM wrapper, CLIP scorer, NSFW checker, installer
src/p1/       manifest, ingestion (text + figure crops), Chroma+BM25 retrieval, answering, conversation memory, eval
src/p2/       data prep, LoRA training, generation, KID/CLIP/LPIPS/human/memorization eval, HF upload
src/p3/       typed state, 5 agents, orchestrator, Gradio app, test inputs, eval
notebooks/    Chelsi/: p1_rag.ipynb (Kaggle submission), p1_eval.ipynb, p2_finetune.ipynb, p3_agents.ipynb (executed)
eval/         golden set, scenarios, red-team cases, human rating sheets (committed BEFORE running)
prompts/      Part 2 prompts
part1/        Chelsi/: Part 1 results (Kaggle submission file)
part2/        Chelsi/: Part 2 results (data report, human-eval key, sample grid and failure-mode figures)
part3/        Chelsi/: Part 3 results (scenario and red-team result tables, per-request agent traces)
              (each of notebooks/, part1/, part2/, part3/ has one folder per member: Chelsi/ and Parth/)
tools/        build_notebooks.py (regenerates the unexecuted notebooks), make_zip.py (Colab/Kaggle upload zip)
```

## Setup
1. Secrets (Kaggle: *Add-ons -> Secrets*; Colab: *Secrets*): `GITHUB_TOKEN` (read access to this private repo) and `HF_TOKEN` (write).
2. Edit `REPO_URL` in Cell 1 of each notebook (`python tools/build_notebooks.py` regenerates them) and `HF_USER` in `src/p2/config.py`.
3. Cell 1 clones the tagged commit, installs `requirements.txt` (skipping packages preinstalled on Kaggle/Colab) and prints commit, versions, GPU and seed.
4. Turn **Internet on** (model downloads).

## Part 1 - Multimodal RAG (Kaggle)
* Attach the competition data. `P1Config` finds `kb_manifest.json` under `/kaggle/input` automatically (or set `P1_DATA_DIR`).
* `notebooks/Chelsi/p1_rag.ipynb`: builds the index (about 10-15 min including VLM figure descriptions), answers `QUESTIONS_PATH`
  (default `<data>/Questions.csv`) and writes `/kaggle/working/submission.csv`, then runs `validate_submission.py`.
* `notebooks/Chelsi/p1_eval.ipynb`: baseline (dense only) vs final (hybrid) vs final+reranker on `eval/p1_golden_set.csv`;
  Recall@5, citation accuracy, median seconds, human groundedness (`eval/p1_human_ratings.csv`) and safety comparisons.
* Design: PyMuPDF text chunks (doc, page, section); every `Figure`/`Table` caption is cropped with its graphics region
  (`Figure B-5` and `Figure B-5 (corrected)` are separate objects); figures are made searchable with VLM descriptions
  plus the text inside the crop; ChromaDB stores `doc_id, page, figure_id, trust_level, section, evidence_ok`.
  Retrieval = bge dense + BM25 fused with RRF. A named label is routed to that exact object, and other look-alike
  figures are dropped. Low-trust sections (Appendix C) and chunks that contain prompt-injection patterns are never
  passed as evidence. Conversation memory is a per-`conversation_id` Python object (never written to the vector DB).
* No question IDs or question texts appear anywhere in the code.

## Part 2 - LoRA fine-tuning
`notebooks/Chelsi/p2_finetune.ipynb`: data prep (corrupt/duplicate removal, 90/10 split, 512x512), writes
`prompts/p2_prompts.json` (**commit it before training ends**), trains `run1_lora_r8` and `run2_lora_r32`
(1500 steps, effective batch 4, LR 1e-4, roughly 30-45 min each on a T4), generates 3 models x 20 prompts x 2 seeds,
computes KID/CLIP/LPIPS, makes 25 blinded pairs (`outputs/p2/human_eval/`), runs the memorization check and pushes
both adapters, the model card and the image dataset to Hugging Face. Raters fill `eval/p2_human_ratings.csv`
(`rater,pair_id,style_choice,prompt_choice` with A/B) without opening `key.csv`; then re-run the last cells.

## Part 3 - Multi-agent system
`notebooks/Chelsi/p3_agents.ipynb` (set `P3_LORA_REPO` to your final Part 2 adapter). Put a consenting team member's photo at
`data/p3/inputs/person.jpg` for the real-person red-team cases. The notebook runs the 15 scenarios with and without the
critique loop, the 10 red-team cases, exports critic decisions to `eval/p3_critic_labels.csv` for labelling, and launches
the Gradio app (`share=True`). Locally: `python -m src.p3.app`. Traces are written to `outputs/p3/traces/<id>.json`.

## Tags
`git tag p1-v1.0 && git tag p2-v1.0 && git tag p3-v1.0 && git push --tags` (before Nov 17, 11:59 PM PT).
