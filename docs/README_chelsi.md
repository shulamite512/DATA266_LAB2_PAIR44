> **Chelsi's original repository README** (from before the merge). Paths inside it refer to the combined layout as follows:
> - `notebooks/Chelsi/p2_finetune.ipynb`: now `notebooks/p2_finetune.ipynb` (selected Part 2).
> - `notebooks/Chelsi/{p1_rag,p1_eval,p3_agents}.ipynb`: now `notebooks/alternatives/chelsi/`.
> - `notebooks/Chelsi/human_eval_results.ipynb`: now `notebooks/evaluation/chelsi_human_eval_results.ipynb`.
> - `part2/Chelsi/`: now `eval/p2_results/`.
> - `part1/Chelsi/` and `part3/Chelsi/`: now `eval/alternatives/chelsi/p1_results/` and `p3_results/`. Her Part 3 traces are in `traces/alternatives/chelsi/`.
> - `eval/p1_*` and `eval/p3_*` (her files): now `eval/alternatives/chelsi/`. Her code reads these at fixed `eval/` paths, so copy them back to re-run her Part 1/3 evaluation.
> - `eval/p2_human_ratings.csv`, `src/`, `prompts/`, `tools/` and `requirements.txt`: unchanged.
>
> The README for the combined repository is the root `README.md`.

# DATA 266 Lab 2 - Pair 44

Three systems built on one 16 GB GPU (Kaggle or Colab Tesla T4), seed 266 throughout:

1. **Part 1 - Multimodal RAG** over three economics PDFs (text, tables and figures), entered in the class Kaggle competition.
2. **Part 2 - Stable Diffusion 1.5 LoRA fine-tuning** on Naruto-style images, two runs compared with automatic and human evaluation.
3. **Part 3 - A five-agent image system** (Planner, Vision, Prompt Engineering, Generator, Critique) with a Gradio app, scenario tests and red-team tests.

All numbers below come from the executed notebooks in `notebooks/Chelsi/` and the files in `part1/`, `part2/`, `part3/` and `eval/`.


## Final graded implementations (team decision, Pair_Programming_Team_44)

| Part | Selected implementation | Notebook with saved outputs | Evaluation evidence |
|---|---|---|---|
| 1 | **Parth**: P1-KAGGLE-V14-R1 (Kaggle Tesla T4) | [`Parth/notebooks/p1_rag.ipynb`](Parth/notebooks/p1_rag.ipynb) | `Parth/eval/p1_submission.csv` (40 rows, validator valid), `Parth/eval/p1_golden_set.csv`, `Parth/requirements-p1.txt`, `Parth/docs/part1/` |
| 2 | **Chelsi**: Naruto LoRA, run 1 (rank 8) final | [`notebooks/Chelsi/p2_finetune.ipynb`](notebooks/Chelsi/p2_finetune.ipynb) | `part2/Chelsi/`, `eval/p2_human_ratings.csv`, `notebooks/Chelsi/human_eval_results.ipynb`, `prompts/`, Hugging Face links in `links.txt` |
| 3 | **Parth**: P3-EXP-003 | [`Parth/notebooks/p3_agents.ipynb`](Parth/notebooks/p3_agents.ipynb) | `Parth/eval/p3_*` (frozen scenarios, red-team cases, freezes, P3-EXP-003 summaries, evaluator files), `Parth/traces/P3-EXP-003/` |

**Alternative implementations (kept, not selected):**
- Chelsi's Part 1 is in `notebooks/Chelsi/p1_rag.ipynb` and `p1_eval.ipynb`.
- Chelsi's Part 3 is in `notebooks/Chelsi/p3_agents.ipynb`.
- Parth's Part 2 is in `Parth/notebooks/p2_finetune.ipynb` and `Parth/notebooks/p2_finetune_REPORT_ONLY_human_eval.ipynb`.

Each member's evaluations belong to that member's implementation. They are not mixed.

**Part 3 depends on Parth's Part 2 adapter, not on the selected Part 2.** Parth's P3-EXP-003 ran with Parth's own Pokémon LoRA A (P2-EXP-001, rank 4, sha256 `20d8d671…`). Its domain-style scenarios and rubrics assume that style. It does **not** use the selected Naruto LoRA. Reproduction instructions are in `Parth/README.md`: the Docker setup is in `Parth/docker/`, the paths there are relative to `Parth/`, and the LoRA is produced by `Parth/notebooks/p2_finetune.ipynb`.

**Part 3 evaluation provenance (Parth).**
- Task success was judged by one human team member and, as a disclosed supplemental second evaluator, an AI model (Claude Opus 5.5).
- 18 disagreements are unresolved.
- See `Parth/HUMAN_EVALUATION.md`, `Parth/AI_USAGE.md` and `Parth/DECISIONS.md` (D-119).

**Layout and tags.**
- `Parth/` contains Parth's complete repository with its full Git history (merged, not rewritten).
- Everything else at the root is Chelsi's repository, unchanged.
- The official tags `p1-v1.0`, `p2-v1.0` and `p3-v1.0` still point to `8a70b1a`, an earlier state of Chelsi's repository. Moving them to the combined commit needs both members' approval (see `links.txt`).

---

## Quick links

| What | Where |
|---|---|
| Executed notebooks | `notebooks/Chelsi/p1_rag.ipynb`, `p1_eval.ipynb`, `p2_finetune.ipynb`, `p3_agents.ipynb` |
| Tags (graded versions) | `p1-v1.0`, `p2-v1.0`, `p3-v1.0` (commits listed in `links.txt`) |
| Final Part 2 LoRA (rank 8) | https://huggingface.co/chels512/data266-lab2-naruto-run1-lora-r8 |
| Second Part 2 LoRA (rank 32) | https://huggingface.co/chels512/data266-lab2-naruto-run2-lora-r32 |
| Part 2 generated images | https://huggingface.co/datasets/chels512/data266-lab2-p2-generations |
| AI tool disclosure | `AI_USAGE.md` |
| Who did what | `CONTRIBUTIONS.md` |

## Models used

All models run locally from the Hugging Face Hub. **No hosted API was used in any submitted run.**

| Purpose | Model |
|---|---|
| Part 1 figure descriptions and answers (final) | `Qwen/Qwen2.5-VL-7B-Instruct`, 4-bit NF4 (bitsandbytes) |
| Part 1 embeddings / reranker | `BAAI/bge-small-en-v1.5` / `BAAI/bge-reranker-base` |
| Part 2 base model | `stable-diffusion-v1-5/stable-diffusion-v1-5` |
| Part 3 planner, vision, prompt and critic agents | `Qwen/Qwen2.5-VL-3B-Instruct`, fp16 |
| Part 3 image edits | `timbrooks/instruct-pix2pix` |
| CLIP score, memorization check, critic | `openai/clip-vit-base-patch16` |
| NSFW output filter | `CompVis/stable-diffusion-safety-checker` |

The Part 1 notebook also has optional backends (`qwen3b`, `qwen3`, `gemini`, `claude`) selected by `BACKEND`; they were
explored during development but the submitted runs use `qwen7b` only.

## Repository layout

```
src/common/   VLM wrapper, CLIP scorer, NSFW checker, dependency installer, run info
src/p1/       manifest, ingestion (text chunks + figure/table crops), Chroma + BM25 retrieval, answering, evaluation
src/p2/       data prep, LoRA training, generation, KID/CLIP/LPIPS/human/memorization evaluation, Hugging Face upload
src/p3/       typed state, five agents, orchestrator, Gradio app, test inputs, evaluation
notebooks/    executed notebooks, one folder per member (Chelsi/, Parth/)
part1-3/      results per part, one folder per member (submission files, figures, result tables, agent traces)
eval/         golden set, scenarios, red-team cases and human rating sheets
prompts/      Part 2 evaluation prompts (fixed before training)
tools/        build_notebooks.py (generates the notebooks), make_zip.py (upload bundle for Colab/Kaggle)
Parth/        Parth's complete implementation (Parts 1-3; selected for Parts 1 and 3) with its own README, eval/, traces/, docker/
```

## How to run

1. On Kaggle or Colab: GPU T4, Internet on. Add `HF_TOKEN` as a secret (needed only for the Part 2 upload).
2. Either attach this repository (Cell 1 clones the tagged commit) or upload the zip from `python tools/make_zip.py`.
3. Run the notebook top to bottom. Cell 1 installs the pinned `requirements.txt` and prints the commit, library
   versions, GPU and seed.

---

## Part 1 - Multimodal RAG

### What we built
* **Ingestion (PyMuPDF).** Text is split into overlapping chunks tagged with document, page and section. Every
  `Figure`/`Table` caption is found and cropped together with its graphics region, so each figure becomes its own
  searchable object. `Figure B-5` and `Figure B-5 (corrected)` are kept as separate objects.
* **Figure understanding.** Each crop is described by the vision-language model; the description plus the text inside
  the crop is what gets indexed.
* **Retrieval.** Dense search (bge-small, ChromaDB) and keyword search (BM25) fused with reciprocal rank fusion. When a
  question names a figure or table, that exact object is retrieved and its look-alikes are dropped.
* **Trust and safety.** The knowledge-base manifest marks Appendix C (DOC3 p7, reader-submitted, low trust); those
  records and any chunk containing prompt-injection patterns are never passed to the model as evidence.
* **Answering.** The model gets the evidence plus rules for the five statuses (answered, not_found, conflict,
  false_premise, session_override) and the citation format. Post-processing checks every citation against the
  validator's patterns and keeps only real labels and pages.
* **Conversation memory** is a per-conversation Python object (never written to the vector store), so follow-up
  questions and user-supplied values ("assume growth was 3%") work within one conversation only.

### Results
| | Value |
|---|---|
| Indexed | 212 text chunks, 36 figures/tables; 3 records excluded (Appendix C) |
| Kaggle public score | 0.50 (Qwen 3B), **0.56** (Qwen 7B), about 0.50 (Qwen 7B, final notebook run) |
| Speed | 40 questions in 285 s, median 6.6 s per question |

Evaluation on our own 25-question golden set (`eval/p1_golden_set.csv`, written by the team):

| System | Correct /25 | Recall@5 | Citation accuracy | Median s/question |
|---|---|---|---|---|
| Baseline (dense only) | 13 | 0.870 | 0.565 | 7.82 |
| **Final (hybrid)** | **16** | 0.870 | 0.525 | 7.22 |
| Final + reranker | 16 | 0.957 | 0.588 | 7.60 |

* **Human groundedness** (2 raters, 1-5): **3.52**, raters within 1 point on 88% of answers. Strongest on named
  figures, corrections and "not found"; weakest on conflicts, two-source questions and false premises.
* **Safety:** asked about the Appendix C reader sentiment index, the baseline answered "45" from the untrusted figure;
  the final system answered "not found".

### Difficulties and how we solved them
| Problem | Fix |
|---|---|
| Sentences such as "Table A-1 sets the forecasts..." were detected as captions, creating duplicate figures | Caption detector rejects reference sentences (lowercase continuation, reference verbs) |
| Some DOC1 captions picked up axis tick labels instead of the title | Title taken from the text block geometrically just below a label-only caption |
| Near-identical figures (A-2/A-3, A-4/A-5, A-6/A-7) were confused | Exact-label routing: a named figure is fetched directly and its look-alikes are removed from the evidence |
| Colab moved to Python 3.13; several pinned packages failed to install and the error was hidden | Installer captures and prints pip output, falls back per package; pins updated (chromadb 1.0.12, gradio 5.29.0, bitsandbytes 0.48.2 for CUDA 13) |
| ChromaDB rejected the collection name `kb` (needs 3+ characters) | Renamed to `kb_lab2` |
| A hosted model's free tier allowed only 20 requests a day, too few for 40 questions plus 36 figure descriptions | Stayed with local Qwen models; moved from 3B to 7B in 4-bit to fit the T4 |
| Score stayed around 0.5-0.56: retrieval was good, but the model mixed up forecasts and outturns and made arithmetic errors | Clearer document roles and status rules in the prompt; reported honestly as the main remaining weakness |
| Two golden-set answers contradicted the documents' own rules (a DOC1 forecast later replaced by a DOC2 outturn; a forecast/outturn difference labelled "conflict" although DOC2 resolves it) | Checked every row against the PDFs; G03 now asks for the DOC1 value explicitly, G20 uses a real unresolved conflict (China 2012 growth: 7.7% in DOC2, 7.8% in DOC3) |

---

## Part 2 - LoRA fine-tuning (Naruto style)

### What we did
* **Data:** `lambdalabs/naruto-blip-captions`, 1,221 images; checked for corrupt files, missing captions and exact or
  near duplicates (none found); 90/10 split (1,099 train / 122 test); resized to 512x512.
* **Two runs, same data and budget:** LoRA rank 8 vs rank 32 on the UNet attention layers; 1,500 steps, effective batch 4,
  learning rate 1e-4 with cosine schedule, fp16.
* **Evaluation:** 20 prompts (10 in-domain from test captions, 5 out-of-domain, 5 compositional) x 2 seeds x 3 models.

### Results
| | Base | **Rank 8 (final)** | Rank 32 |
|---|---|---|---|
| Trainable parameters | - | 1.59 M | 6.38 M |
| GPU-hours / peak memory | - | 0.67 h / 3.7 GB | 0.67 h / 3.7 GB |
| KID vs test set (lower is better) | 0.103 | **0.036** | 0.045 |
| CLIP score, in-domain | 30.14 | 28.66 | 27.15 |
| LPIPS diversity | 0.719 | 0.721 | 0.693 |
| Images flagged by the NSFW filter (of 40) | 0 | 2 | 4 |

* **Human evaluation** (25 blinded pairs, final vs base, 2 raters): the fine-tuned model was preferred for **style in
  64%** of judgements (raters agreed 76% of the time) and for **prompt match in 50%**. Style improved; prompt
  adherence did not, which matches the lower CLIP score.
* **Rank 8 was chosen** for the best KID, highest diversity and the smaller loss in prompt adherence.
* **Memorization check:** the closest generated-vs-training pair has CLIP cosine 0.88; no near-copies.
* **Failure modes:** out-of-domain prompts are pulled into anime style; compositional prompts get colours and positions wrong.

### Difficulties and how we solved them
| Problem | Fix |
|---|---|
| The memorization cell failed (`'function' object is not iterable`): the training list was shadowed by the imported `train` function | Renamed the list to `train_items` |
| After an interrupted run, `import torch` failed with a circular-import error | Restarted the Python session (not the whole runtime) so the trained models on disk were kept, then reloaded results without retraining |
| Upload to Hugging Face failed with 403 because the repository name still used a placeholder user | Read the real username from the token (`whoami`) and rebuilt the repository names before pushing |
| The NSFW filter flagged a few harmless anime images | Kept the filter on (safer default) and counted flagged images in the results |

---

## Part 3 - Five-agent image system

### What we built
`Planner -> Vision -> Prompt Engineering -> Generator -> Critique`, sharing one typed state object.
* **Planner:** input safety (unsafe requests, prompt injection, deceptive edits) and routing (caption/question, style
  change, edit, Naruto-style generation, clarification).
* **Vision:** describes the uploaded image and answers questions about it.
* **Prompt Engineering:** turns the request plus the image description into a generation or edit prompt.
* **Generator:** img2img with the Part 2 LoRA (loaded from Hugging Face), instruct-pix2pix for edits, text-to-image.
* **Critique:** output safety (NSFW filter) and quality (CLIP similarity plus VLM check); asks for up to 2 revisions.
* Broken inputs (empty, unreadable, too small) are rejected with a clear message. Every request writes a trace.

### Results
| | No critique loop | **With critique loop** |
|---|---|---|
| Automatic rubric, 15 scenarios | 13/15 | 13/15 |
| Median seconds per request | 13.2 | 24.7 |

* **Human judgement** (2 raters, disagreements resolved): **12/15** tasks done correctly; raters agreed on 80%. The
  automatic rubric passed one case (pencil sketch) that both raters judged a failure after discussion.
* **Critic vs human:** 79% agreement on 19 decisions. The critic never accepted an image the raters rejected; all
  disagreements were the critic asking for another attempt on images the raters found good enough (too strict, not unsafe).
* **Red team (10 cases):** unsafe text requests and broken files were all handled. 3 prompt-injection images failed the
  automatic rubric, but in none of them was the hidden instruction followed. 2 real-person cases were not run because
  no consenting photo was added.
* **Known failures:** reading the text on a sign (S03); one harmless anime image blocked by the NSFW filter (S11).

### Difficulties and how we solved them
| Problem | Fix |
|---|---|
| Browser uploads to Colab kept stalling and the runtime disconnected | Ran on Kaggle instead, with the project uploaded as a Kaggle dataset; Cell 1 finds it automatically |
| GPU option unavailable on Kaggle | Account phone verification enabled the GPU |
| The red-team summary printed an impossible "-13/8" | The two skipped rows made the pass column non-boolean, so `~` did integer negation; fixed by casting to bool (`src/p3/evaluate.py`). Correct result: 3 of 8 failed the rubric |
| Human-agreement code counted only rows with a filled `resolved` column | `resolved` is now used only where raters disagreed; elsewhere the shared verdict counts |

---

## Repository and workflow issues
| Problem | Fix |
|---|---|
| `git push` failed with a TLS error (`SEC_E_MESSAGE_ALTERED`) on a 16 MB push | Larger HTTP buffer, OpenSSL backend and HTTP/1.1 for this repository |
| Re-generating notebooks could overwrite executed ones | `tools/build_notebooks.py` now refuses to overwrite existing notebooks unless `--force` is given |
| Executed notebooks were moved into member folders | Cell 1 now finds `src/` from `notebooks/<member>/` as well |
