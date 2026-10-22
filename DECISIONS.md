# DECISIONS — Chronological Engineering Record

## How this log works

- Entries are **append-only** and in the order they were made. An old entry is never edited to change what was decided.
- When a decision changes, a **new** entry is appended that names the earlier entry ID and gives the previous decision, the evidence, the new decision and the reason. The old entry gets a one-line `Superseded by D-xxx` marker and nothing else changes.
- Entry IDs: `D-###` for decisions and observations, and `P1-EXP-###`, `P2-EXP-###`, `P3-EXP-###` for experiments.
- **Hidden-set rule (see D-006):** this file must never contain question IDs, conversation IDs or question text from `Questions.csv`. Failures are described by category.

### Experiment entry template

```
### P#-EXP-### — <short title>   (YYYY-MM-DD)
- Objective:
- Architecture / configuration:
- Exact important parameters:
- Change from previous experiment:
- Git commit:
- Environment / GPU:
- Random seed:
- Smoke-test result:
- Full-run result:
- Required evaluation metrics:
- Kaggle result (if applicable):
- Observed failures:
- Conclusion:
- Verdict: KEEP / MODIFY / REJECT
- Next planned experiment:
```

---

## Log

### D-001 — Repository root is `implementation/` (2026-10-17)
- **Decision:** `LAB 2/implementation/` is the Git repository root. It corresponds to the GitHub repository `data266-lab2-team##`, which has not been created yet. The professor-provided material stays in `LAB 2/`, outside the repository.
- **Reason:** the expected folder structure (Requirements PDF and lecture slides) places `README.md`, `requirements.txt`, `notebooks/` and the other files at the repository root. Keeping the PDFs and CSVs physically outside the repository makes it impossible to commit them, which the assignment forbids ("never commit PDFs, datasets, API keys or tokens").
- **Detail:** local `git init` only. The initial branch is `main`, renamed from Git's default `master` before any commit to match GitHub's default. No remote, commit or tag exists.

### D-002 — Notebook-first, minimal-file policy (2026-10-17)
- **Decision:** one notebook per part (`notebooks/p1_rag.ipynb`, and later `p2_finetune.ipynb` and `p3_agents.ipynb`). No `src/`, `scripts/`, helper modules, config files or per-experiment notebook copies. Experiments are preserved through Git history. Any additional file needs explicit team approval and a technical justification.
- **Expected future exceptions, each driven by an assignment requirement and created only when that work begins:** `eval/` (the Part 1 golden set must be committed before tuning, and the human ratings must be readable by the notebook), and `traces/` (Part 3 JSON traces).

### D-003 — Professor-provided material is read-only (2026-10-17)
- **Decision:** the files in `DATA266_Lab2_Part1/` and both Lab 2 PDFs are never modified, moved, renamed or copied. The notebook reads them through one data-directory setting in the configuration cell: `../../DATA266_Lab2_Part1` locally (relative to `notebooks/`), or auto-discovered under `/kaggle/input/` on Kaggle.
- `validate_submission.py` is executed from its original location, not copied into the repository.

### D-004 — Observed dataset facts: citation format and trust metadata (2026-10-17)
- **Observation:** in the citation format `DOC#:p#`, the page number is the **1-based PDF page index**, not the printed book page number. Evidence: `sample_submission.csv` pairs `DOC1:Figure 1-2` with `DOC1:p3`, and Figure 1-2 is on PDF page 3, whose printed page number is 6. DOC1's printed page numbers differ from its PDF indices throughout. For DOC2 and DOC3, the printed page number equals the PDF index.
- **Observation:** `kb_manifest.json` gives the trust levels (DOC1 high, DOC2 high, DOC3 medium) and a section override (DOC3 Appendix C, PDF page 7: low). It also gives the precedence policy: an explicit revision or erratum beats the earlier value, an outturn beats a forecast, a high/medium disagreement with no revision note gives `conflict` with the higher-trust value preferred, and low-trust content is never used as evidence.
- **Observation:** DOC2 contains exactly one explicit revision: U.S. output growth for 2010. DOC3 contains one erratum: Figure B-5 and Figure B-5 (corrected) are separate figures. Near-identical figure pairs are A-2/A-3 (data vintage), A-4/A-5 (index base date), A-6/A-7 (year), B-1/B-2 (sample period), B-3/B-4 (comparison series) and B-5/B-5 (corrected).
- **Observation:** `validate_submission.py` accepts `Figure C-1` syntactically. The validator therefore does not protect against citing low-trust content, so the system must enforce that exclusion itself.
- **Decision:** the citation page convention is the 1-based PDF index. Trust levels are read from the manifest, never hard-coded.

### D-005 — Observed dataset constraint: figures are stored differently across documents (2026-10-17)
- **Observation** (from `pypdf` raster-image inspection of every page):
  - **DOC1** (`Document.pdf`, 37 pp): its numbered figures (1-1 to 1-6, 2-1 to 2-7) are **vector graphics drawn on the page, not embedded images**. Only PDF pages 16 and 23 contain any raster image. Its tables (1-1 to 1-4) are extractable text.
  - **DOC2** (7 pp): charts are **embedded raster images** (one on p2, two each on p4, p5 and p6). Tables A-1 to A-3 are extractable text.
  - **DOC3** (7 pp): charts are **embedded raster images** (p2, p3, two on p4, p5, p6, and p7, which is Figure C-1 in the low-trust appendix). Tables B-1 and B-2 are extractable text.
- **Implication (constraint, not yet a design):** extracting embedded images alone would miss every DOC1 figure. Figure extraction must handle vector figures, for example by rendering the page region located from the caption or label. Pages with two images need each image matched to the correct label. This will be decided under the pending "figure/table extraction" decision (D-010).

### D-006 — Hidden-set integrity and no question-specific logic (2026-10-17)
- **Decision:** no committed file (notebooks, `DECISIONS.md`, README, evaluation files) contains question IDs, conversation IDs or question text from `Questions.csv`. There are no rules keyed to specific questions or answers. The pipeline must generalise to reworded hidden questions.
- **Reason:** graders search the repository for question IDs and text, and hard-coded answers or question-specific rules score 0 for Tasks 1.3 and 1.5.
- **Decision:** the Part 1 golden set (25 questions) will be written independently of `Questions.csv` and committed **before** any tuning (the Git timestamp is checked).

### D-007 — Reproducibility conventions (2026-10-17)
- **Decision:** cell 1 of every notebook is the professor's run-information cell, **verbatim**, with `SEED = 266`. Because the assignment requires that cell to come first, the notebook's title and the central configuration cell come after it.
- **Decision:** cell 2 is the only place for the experiment ID and all tunable parameters. Later cells read from it and never redefine parameters.
- **Known issue (open):** on Kaggle the notebook does not run inside a Git checkout, so `git rev-parse` in cell 1 will print an empty commit. A strategy for showing the `p1-v1.0` commit on Kaggle must be decided before the final submission. The run-information cell itself will not be modified.
- **Known issue:** cell 1 imports `torch`, which is not installed in the current local environment. Locally the cell will fail until the dependencies are chosen (D-009).

### D-008 — Compute and environment assumptions (2026-10-17)
- **Decision:** all required work runs on one 16 GB GPU (Kaggle T4 or P100). The Part 1 end-to-end submission run must finish in **under 90 minutes** on Kaggle with no manual step.
- **Decision:** local machine (macOS, Python 3.10.2, no GPU libraries installed) is used only for implementation, syntax and import checks, path validation and tiny-sample smoke tests. No full GPU experiments run locally.
- Any hosted API (LLM, VLM or image) must be named in the README with its model version. None is used so far.

### D-009 — Dependencies: pending, no `requirements.txt` yet (2026-10-17)
- **Decision:** `requirements.txt` is **deferred until the Part 1 architecture and its dependencies have been selected** (D-010). Exact versions will be pinned from a **verified working Kaggle environment**, using the versions actually printed by a successful run and not guessed, **before the reproducible experiment is finalized**.
- _(Wording clarified on 2026-10-17 at the team's request. The substance of the decision is unchanged.)_
- _Partially superseded by D-040._

### D-010 — Part 1 architecture: candidates recorded, nothing selected (2026-10-17)
- **Decision:** the professor's suggested starter stack is recorded as **candidate/reference components only**. It is **not** selected.
  - Candidates from the assignment: PyMuPDF (text and figure crops), `sentence-transformers` with `BAAI/bge-small-en-v1.5` (dense text), `rank_bm25` (keyword), ChromaDB (vector DB), `Qwen/Qwen2.5-VL-3B-Instruct` (VLM for figure description and answering) or a declared hosted API, and optionally a reranker (+2 bonus if shown on the golden set).
- **Selection criteria:** fits one 16 GB Kaggle GPU; end-to-end under 90 minutes; reproducible (fixed seeds, deterministic decoding where possible); generalises to the hidden set; no question-specific hard-coding; maximises the Kaggle score (0.40 answer correctness within ±1%, 0.20 status, 0.20 figure-reference F1, 0.20 citations).
- **Pending decisions**, each to be logged as its own chronological entry **before P1-EXP-001**:
  1. PDF/text extraction
  2. Figure/table extraction (must satisfy D-005)
  3. Chunking (size, overlap, unit)
  4. Dense embedding model
  5. BM25 configuration and tokenisation
  6. Fusion strategy (dense + BM25)
  7. Reranker (whether to use one, and which)
  8. Figure representation and retrieval (CLIP embeddings vs VLM descriptions)
  9. Exact figure/table routing for questions that name a label
  10. Vector database
  11. Trust and revision resolution (manifest precedence, erratum, outturn vs forecast, conflict, Appendix C exclusion)
  12. Conversation memory (per `conversation_id`, session overrides, refusing permanent edits)
  13. VLM/LLM (local model vs hosted API)
  14. Structured output and schema validation

### D-011 — Deferred files (2026-10-17)
- **Decision:** not created until their work begins: `notebooks/p2_finetune.ipynb`, `notebooks/p3_agents.ipynb`, `eval/` (created only when the Part 1 golden set is ready to be written and committed), `traces/`, `requirements.txt` (D-009) and `links.txt` (Canvas zip).
- Meeting recordings will be kept outside the Git repository and listed in `CONTRIBUTIONS.md`. Their storage location is to be decided.

### D-012 — AI assistant usage declared (2026-10-17)
- **Decision:** Claude Code (Claude Opus 5.5, VS Code extension) is declared in `AI_USAGE.md` from the first day. That file is updated cumulatively as usage grows.

---

> **Part 1 architecture review (2026-10-17).** Entries D-013 to D-035 record the team-approved P1-EXP-001 architecture. They resolve the pending items listed in D-010. Nothing below has been implemented or measured yet.

### D-013 — Status labels used from here on (2026-10-17)
- **DECIDED**: approved by the team for P1-EXP-001.
- **CANDIDATE**: proposed choice that still has to pass a named test before it is DECIDED.
- **TUNE**: initial value. It must be adjusted using `Questions.csv` and the public leaderboard only (D-034).
- **ESTIMATE**: unmeasured runtime or memory figure. It is not a result.
- **OPEN**: no responsible choice is possible yet; the missing information is named.
- Measured values will appear only in later entries labelled **RESULT**, with the run and Git commit that produced them.

### D-014 — Deterministic-first architectural principle — DECIDED (2026-10-17)
- Wherever a sub-problem is deterministic, it is solved in code: label lookup, trust levels, supersession, conversation isolation, output format and citation syntax. Models are used only where semantic understanding is genuinely needed: relevance ranking, chart reading, follow-up interpretation, value matching across sources, and answer composition.
- **Reason:** code is reproducible, auditable and cannot be argued out of a rule by document content. That matters for prompt-injection resistance and for the hidden set.

### D-015 — One notebook, `MODE = "baseline" | "final"` — DECIDED (2026-10-17)
- Both modes live in `notebooks/p1_rag.ipynb`. The mode is selected in the configuration cell.
- **Baseline** has the same ingestion, chunks, dense embedding model, generator and output validator as final. Retrieval is **dense only**. Disabled in baseline: BM25, RRF, reranker, exact-reference router, and the cross-document revision/conflict retrieval logic (D-029).
- **The evidence filter is active in both modes.** Appendix C and every `evidence_ok=False` object are excluded even in baseline, because this is a mandatory safety rule and not a retrieval enhancement.
- **Final** is the complete architecture in this log.
- **P1-EXP-001 is the first full (final-mode) architecture.** Baseline is an evaluation mode, not an experiment ID.

### D-016 — PDF/text extraction: PyMuPDF — DECIDED (2026-10-17)
- `page.get_text("dict")` gives blocks and lines with bboxes and font information. The same library provides embedded-image bboxes and vector drawings (`get_drawings()`), which caption-anchored figure extraction needs (D-017). Page numbers are 1-based PDF indices (D-004).
- **Rejected:** pypdf (no layout or bboxes); Docling, Marker and Unstructured (heavier, less transparent, extra models).
- **Exact package version:** OPEN, to be set by the Kaggle smoke test (D-009).

### D-017 — Figure extraction: caption-anchored region rendering — DECIDED (2026-10-17)
- A caption detector (regex on text blocks: `Figure|Table <label>` with an optional ` (corrected)`) finds each label's caption bbox. The figure region is then located:
  - **DOC1 (vector):** cluster the `get_drawings()` bboxes between the caption and the next text block or caption.
  - **DOC2/DOC3 (raster):** pair each embedded-image bbox with its nearest caption. This handles pages that contain two figures.
- The region is rendered as a PNG through a page clip and stored with its label, caption and source note. `Figure B-5` and `Figure B-5 (corrected)` are separate objects.
- **Checks:** an inventory assertion that every label mentioned anywhere in the text has exactly one object, and a printed contact sheet of all crops for visual inspection.
- Implements the constraint recorded in D-005.
- **Render DPI:** 200 (TUNE). Whether the clustering works on DOC1 is OPEN until the smoke test.

### D-018 — Table extraction and representation — DECIDED (2026-10-17)
- **Extraction:** PyMuPDF `find_tables()`, with a structure check (expected header row and year columns, numeric cells). If extraction fails, the fallback is VLM transcription of the rendered table crop, marked as `extraction_method="vlm"`.
- **Each table object keeps:**
  1. the original table markdown/text,
  2. the rendered table crop (PNG),
  3. **normalized structured rows where feasible:** `entity, variable, year, value, unit, kind (forecast | outturn | revised), doc_id, page, table_id`.
- `kind` is derived deterministically: a `*` marker means forecast, an outturn column means outturn, and an explicit revision notice means revised.
- These representations are **internal** to the notebook's in-memory index. **No additional data file is created.**
- **Purpose:** to reduce numerical hallucination and make forecast/outturn/revision reasoning deterministic where possible.
- **Entity/variable normalization:** OPEN. Names are mapped from row and column headers; the rules depend on how the tables actually parse.

### D-019 — Chunking — DECIDED (structure) / TUNE (sizes) (2026-10-17)
- **DECIDED:** paragraph-aware chunks that never cross a page boundary. Each chunk is prefixed with `[doc_id | p# | section heading]`. Tables, figures, revision notices and errata are separate atomic objects that are never split.
- **Metadata on every object:** `doc_id, page, object_type (text|table|figure), figure_id/label, caption, section, trust_level, evidence_ok, superseded_by, contains_forecast`.
- **TUNE:** target ~220 words, maximum 350 words, overlap ~40 words (within a page only).

### D-020 — Dense embedder: `BAAI/bge-large-en-v1.5` — CANDIDATE (2026-10-17)
- Proposed for P1-EXP-001. It is subject to the first Kaggle compatibility test (load, encode, memory, latency).
- **Reason:** the KB is small, so indexing cost does not constrain model size, and a stronger embedder helps with reworded hidden questions. The same model is used in baseline mode.
- **Alternatives kept for ablation:** `bge-small-en-v1.5` (the professor's suggestion) and `Qwen3-Embedding-0.6B`.
- **Query prefix:** `"Represent this sentence for searching relevant passages: "` (model convention).
- **Memory and latency:** ESTIMATE only. To be measured.

### D-021 — BM25: `rank_bm25` `BM25Okapi` — DECIDED (2026-10-17)
- The tokenizer preserves figure/table labels (`a-3`, `1-2`), years, decimals and `%`. It lowercases and removes stopwords, with no stemming.
- **TUNE:** k1 = 1.5, b = 0.75 (library defaults); stemming on/off.

### D-022 — Vector database: ChromaDB — DECIDED (2026-10-17)
- In-memory client rebuilt every run. We supply our own embeddings (Chroma's built-in embedding function is not used). Cosine space.
- Metadata `where` filters enforce `evidence_ok` and doc constraints.
- **Fallback if it fails to install on Kaggle:** Qdrant local mode (that would get its own new entry).

### D-023 — Fusion: Reciprocal Rank Fusion — DECIDED (method) / TUNE (k) (2026-10-17)
- RRF over the dense and BM25 rank lists. **k = 60** initially (TUNE).
- **TUNE:** dense top-k 20, BM25 top-k 20.
- **Reason:** the two score scales are not comparable, and RRF needs no score normalization.

### D-024 — Reranker: `BAAI/bge-reranker-v2-m3` — CANDIDATE (2026-10-17)
- Proposed for P1-EXP-001. It is subject to the first Kaggle compatibility test.
- It reranks the fused top-24 and keeps 8 (both TUNE). Router-pinned objects bypass the reranker.
- **VRAM and latency: MEASURE.** The earlier ~1.1 GB figure was an ESTIMATE and is not recorded as fact.
- A reranker on/off ablation is planned. It is also the evidence needed for the +2 bonus.

### D-025 — Model residency: no co-residency requirement — DECIDED (2026-10-17)
- Model loading is designed so that the embedder, reranker and VLM **do not need to be resident on the GPU at the same time**. Each model's device (`cuda`/`cpu`) is a configuration-cell parameter, and models can be loaded, used and released by stage. For example: embed the corpus, then free the embedder or move it to CPU for query encoding, then load the VLM.
- **Reason:** reliable execution within 16 GB matters more than keeping every model loaded. The KB is tiny, so CPU query encoding and reranking are likely acceptable (ESTIMATE).
- **Default device per model:** OPEN until the smoke test measures memory and latency.
- Only one GPU is used: all models are pinned to `cuda:0`, even if Kaggle offers two T4s.

### D-026 — Figure representation and search — DECIDED (2026-10-17)
- Each figure is indexed as **text** in both dense and BM25: label, caption, source note, the paragraphs that reference the label, and a structured VLM description (chart type, axes, series, units, vintage/base date/year, per-x values).
- At answer time, the **image itself** is also passed to the VLM for the selected figures (at most 2 per question, TUNE).
- **Rejected for P1-EXP-001: CLIP image embeddings.** The near-identical pairs (A-2/A-3, A-4/A-5, A-6/A-7, B-1/B-2, B-3/B-4, B-5/B-5 corrected) differ in vintage, base date, year or series. Those differences are stated in captions and text, not visible in overall image appearance. CLIP may be ablated later to document this.
- Low-trust figures (Figure C-1) are **never** described by the VLM and never sent to it.

### D-027 — Exact-reference router — DECIDED (final mode only) (2026-10-17)
- A deterministic regex detects references such as `Figure A-3`, `Fig. A3`, `figures A-6 and A-7` and `Figure B-5 (corrected)`, plus document references (`Document N`, `DOC N`, and document titles from the manifest).
- Labels are normalized to canonical form and looked up in the **inventory built from the documents**, never from the questions.
- **Hit:**
  - pin the named objects;
  - exclude every other figure image from the context;
  - add same-page text and the paragraphs that reference the label;
  - if a superseding object exists, attach it marked "supersedes".
- **Unknown label:** flag it for the validator (evidence for `not_found` or `false_premise`).
- **No reference:** hybrid semantic retrieval.

### D-028 — Trust and evidence filtering — DECIDED (both modes) (2026-10-17)
- `trust_level` comes from `kb_manifest.json`, including the section/page override that makes DOC3 p7 low trust. `evidence_ok = (trust_level != "low")`.
- Objects with `evidence_ok=False` stay in the index (so the safety analysis can inspect them) but are removed from every context passed to the generator. The validator rejects any citation of them. This applies in **baseline and final**.
- Evidence is passed to the generator in delimited blocks marked as data. Instructions found in documents or images are never executed.

### D-029 — Revision, forecast/outturn and conflict resolution — DECIDED (structure) (2026-10-17)
- **Deterministic:**
  - The supersession registry is built at ingestion: `X (corrected)` supersedes `X`; the explicit revision notice supersedes the revised value; `*` cells are forecasts; DOC2 outturns supersede DOC1 forecasts for the same variable and year. Per-document data vintages come from the manifest.
  - Every evidence item carries `doc | page | label | trust | vintage | forecast/outturn/revised` headers.
- **Cross-document evidence is sought deliberately, not by quota.** In final mode, when retrieved structured rows (D-018) have counterparts in other documents with the same `(entity, variable, year)`, or a retrieved object is superseded or superseding, the counterparts are fetched and added. This gives the generator exactly the evidence needed for revision, forecast/outturn and conflict reasoning. It is disabled in baseline.
- **Model-based:** deciding whether two values describe the same quantity when they are not in structured rows, and choosing `conflict` vs `answered` vs `false_premise`, using the manifest precedence rules stated in the prompt.
- **Deterministic post-checks:** citations must be a subset of the evidence shown; a superseded value must not be the sole cited source when its superseding object was in the context.
- **Not used:** a mandatory source-diversity quota (D-033).

### D-030 — Conversation memory: `ConversationState` — DECIDED (2026-10-17)
- **Fields:** `conversation_id`; `turns` (user text, standalone query, answer JSON, evidence IDs); `focus` (entities, variables, years, doc_ids, labels from the last answered turn); `overrides` (entity, variable, year, value, unit, source turn, raw text); `refused_kb_edits`.
- A new empty state is created for each `conversation_id` and discarded after its last turn.
- Follow-ups are rewritten into standalone queries by the VLM, using only that conversation's turns (`max_new_tokens` 64, TUNE).
- Overrides enter the prompt as "user-supplied, this conversation only", separate from the evidence. Requests to change the knowledge base permanently are refused.
- **Immutable base index:** nothing is written to the index after ingestion. An index fingerprint (object count plus a hash of the IDs and contents) is asserted unchanged at the end of the run.
- **Expected status for a refused KB-edit turn:** OPEN. To be calibrated on the public leaderboard.

### D-031 — Answer VLM — CANDIDATE (not locked) (2026-10-17)
- **Primary candidate:** `Qwen/Qwen3-VL-4B-Instruct` (fp16, greedy decoding).
- **Fallback candidate:** `Qwen/Qwen2.5-VL-3B-Instruct`.
- **Final selection requires a Kaggle smoke test measuring:** model load success, `transformers` compatibility, peak GPU memory, one text-only answer, one figure answer, JSON/schema reliability, and latency.
- **Rejected for now:** 7–8B VLMs, because they only fit a T4 in 4-bit (slower; quantization risks fine chart reading); gated models; hosted APIs.
- **TUNE:** `max_new_tokens` answer 320, figure description 512; `max_pixels` ≈ 1024×28×28.
- **Known risks to test:** fp16 numerical stability on a T4 (Qwen models are trained in bf16); no FlashAttention-2 on Turing GPUs, so SDPA attention is used.

### D-032 — Structured output and validation — DECIDED (2026-10-17)
- The VLM is prompted for JSON. Its output is parsed, then validated against a pydantic schema.
- **Deterministic rule checks:**
  - status is in the allowed set;
  - the answer is non-empty and ≤120 words;
  - figure labels and citations match the `validate_submission.py` grammar;
  - figure labels exist in the inventory;
  - citations are a subset of the evidence shown, with no low-trust citations;
  - `not_found` has no citations;
  - an override that was used gives `session_override`.
- **On failure:** one repair retry, then a deterministic fallback answer.
- **Submission:** lists are joined with commas and no spaces, `NONE` is written for empty lists, and `validate_submission.py` runs from its original location as the final cell of the submission section.
- **Rejected for P1-EXP-001:** constrained-decoding libraries (fragile with HF VLM generation; they remain a possible ablation).

### D-033 — Source-diversity quota — REJECTED for P1-EXP-001; future ablation only (2026-10-17)
- **Previous proposal (architecture analysis, not adopted):** force at least one item from every eligible document into each context.
- **Decision:** not used. Retrieval returns evidence by relevance. Cross-document evidence is sought only when the query requires comparison, conflict or revision reasoning (D-029).
- **Reason:** a mandatory quota injects irrelevant evidence into single-source questions and can provoke false `conflict` statuses.

### D-034 — Evaluation data policy — DECIDED (2026-10-17)
- The 25-question golden set is **evaluation only** and is never used for tuning. TUNE parameters are adjusted only with `Questions.csv` and the public leaderboard (consistent with D-006).
- The submission section runs and writes `submission.csv` before the evaluation sections, behind a `RUN_EVAL` configuration flag, so the submission stays within the 90-minute limit.
- **Runtime target:** under 90 min end to end. The current figure of ~25–55 min to `submission.csv` is an ESTIMATE, not a result. Stage timers will be printed.
- **Hidden-set size:** OPEN.

### D-035 — Open items blocking final selection (2026-10-17)
- **OPEN:** whether the grader's hidden-set run allows internet access. If not, models must be attached as Kaggle Models/Datasets, which may change D-031 and D-020/D-024.
- **OPEN:** Kaggle image package versions (D-009).
- **OPEN:** scoring conventions: the status for a refused KB edit; `figure_references` when a question names the original of a corrected figure; citation granularity and whether extra citations are penalized.
- **OPEN:** the commit hash on Kaggle (D-007).
- **OPEN:** whether charts have printed data labels or need visual value estimation (affects ±1% correctness).

### D-036 — Pre-experiment smoke-test harness lives gated inside `p1_rag.ipynb` — DECIDED (2026-10-17)
- **Decision:** the Kaggle infrastructure/model smoke test is one clearly separated section, "Pre-Experiment Kaggle Infrastructure Smoke Test", inside `notebooks/p1_rag.ipynb`. It runs only when `RUN_SMOKE_TEST = True`; the default is `False`, and then every smoke cell prints one skip line and does nothing else. No separate notebook or Python file.
- **Reason:** reproducibility and auditability. The harness code is versioned in Git, and its executed Kaggle output is the evidence for later RESULT entries. (The alternative, a throwaway Kaggle-only notebook, was rejected: the evidence would exist only on Kaggle.)
- **This is not an experiment** and has no P1 experiment ID. It validates the infrastructure and the CANDIDATE choices (D-020, D-024, D-031) before P1-EXP-001.
- **Scope:**
  - S0: environment report (preinstalled versions first; packages are installed only if `SMOKE_PIP_INSTALL = True`, and then only missing or too-old ones, never changing torch).
  - S1: PyMuPDF label inventory over all pages (text only), and crops/tables on 7 probe pages shown inline.
  - S2: embedder. S3: reranker. S4: ChromaDB `evidence_ok` filter and the BM25 tokenizer.
  - S5: primary VLM. S6: fallback VLM, only if S5 fails.
  - S7: sequential-residency verification (D-037).
- **Constraints:**
  - `Questions.csv` is never read, and no question text is used. Probe questions are generic and target Table B-1, Table A-1 and Figure A-1, which `Questions.csv` does not ask about.
  - Nothing is written to disk.
  - Every measurement is printed by code as `RESULT <key>: <value>`.
  - VLM ground truth is read programmatically from the extracted tables, never typed in.
- **Results:** none yet. The harness has not been run on Kaggle. Only local syntax and failure-path checks have been done (no GPU stack installed locally).

### D-037 — Sequential GPU residency is the intended strategy; the smoke test measures release — DECIDED (strategy) (2026-10-17)
- **Context:** the architecture analysis had proposed an S7 that would load the embedder, reranker and VLM on the GPU together. That proposal was **replaced before implementation**: it contradicted D-025 and does not match the intended architecture.
- **Decision:** models are resident on `cuda:0` **one at a time**: load embedder → probe → move to CPU / delete → `gc.collect()` + `torch.cuda.empty_cache()` → verify VRAM released → load reranker → probe → release → verify → load VLM → probe → record final and peak VRAM → release. The three models are never intentionally co-resident.
- **What the smoke test measures:** a GPU snapshot (allocated, reserved, peak, device-used MB) before each model, after load, at peak and after release. It reports the VRAM left behind after each release (pass threshold `SMOKE_RELEASE_TOLERANCE_MB`), whether each model was released before the next one loaded, each model's resident size, and the overall peak.
- **Implementation note:** the lifecycle is enforced by the stage order S2 → S3 → S5 (→ S6); S7 verifies and summarises those snapshots. The VLM is not loaded a second time just for S7, to avoid a duplicate multi-GB load.
- **Results:** none yet (not run on Kaggle).

### D-038 — Configuration values introduced with the harness (2026-10-17)
- All values live only in the central configuration cell; a local AST check confirmed that no other cell reassigns them.
- **Smoke-test criteria (DECIDED for the smoke test only):** `SMOKE_RELEASE_TOLERANCE_MB = 64`, `SMOKE_MAX_PEAK_VRAM_MB = 14336`, `SMOKE_MIN_VALID_JSON = 4` (of 5), `SMOKE_VLM_FALLBACK = "auto"`, `SMOKE_PIP_INSTALL = False`.
- **CANDIDATE:** `DEVICE = "cuda:0"`, `GPU_DTYPE = "float16"`, and the model IDs from D-020, D-024 and D-031. `VLM_MIN_TRANSFORMERS = "4.57.0"`, the believed first `transformers` release with Qwen3-VL support, to be verified by S0/S5. `VLM_ATTN_IMPL = "sdpa"`.
- **TUNE (new):** `RERANK_MAX_LENGTH = 512`, `TABLE_STRATEGIES = ("lines", "text")`, `BM25_TOKEN_PATTERN` and `BM25_STOPWORDS`.
- **Previously logged values, now placed in the config:** D-019 chunk sizes, D-021 BM25 k1/b, D-023 top-k and RRF k, D-024 rerank 24 → 8, D-031 `max_pixels` and `max_new_tokens`, D-015 `MODE`.
- **Format constants (DECIDED):** `ALLOWED_STATUS`, `MAX_ANSWER_WORDS = 120`, `ANSWER_NUMERIC_TOLERANCE = 0.01`, `LABEL_PATTERN`, `CITATION_PATTERN`. These mirror the grammar of `validate_submission.py`; a local check showed the same accept/reject decision on all 40 `sample_submission.csv` rows. The original validator still runs as the final check (D-032).
- **Local unit-check observation (not a Kaggle result):** the BM25 tokenizer keeps `a-3`, `1-2`, `2000`/`2012` and `2.4%` as intended, but splits `U.S.` into `u` and `s`. Recorded as a TUNE item for the retrieval implementation.

### D-039 — Pre-commit workflow: no Git commit until P1-EXP-001's first successful GPU run — DECIDED (2026-10-17)
- **Decision:** no `git add`, commit, push or tag until **P1-EXP-001 has completed its first successful real GPU run and its outputs and results have been saved**. Until then the local repository stays uncommitted.
- **Pre-commit loop:** local implementation → local checks → package `implementation/` as one ZIP → save the ZIP to Drive → use it on Kaggle → install requirements → run → record results and failures here → modify the same implementation → replace the ZIP → repeat.
- **ZIP:** `LAB 2/data266_lab2_implementation.zip`, outside the repository so it can never be committed, and **replaced in place** on every update. It contains only the repository's working files. Excluded: `.git/`, caches, checkpoints, model caches, generated crops, indexes, `submission.csv`, secrets, professor PDFs/data and OS metadata.
- **No copies:** no experiment copies of the repository or notebook. `DECISIONS.md` remains the chronological record of every decision, smoke-test result, parameter change and failure.
- **Consequences recorded:**
  1. D-036's rationale ("the harness code is versioned in Git") is deferred. Until the first commit, smoke-test evidence is preserved by the saved Kaggle notebook versions and outputs, the Drive ZIP, and the RESULT entries in this file.
  2. Cell 1 prints an empty Git commit on Kaggle; D-007 remains OPEN.
  3. **Constraint carried from D-006:** the golden set must be committed **before any tuning**, and the Git timestamp is checked. So between the first P1-EXP-001 run and the first commit, no TUNE parameter may be changed on the basis of results. The golden set must be written and included in, or committed immediately after, the first commit, before tuning starts.
- _Commit timing superseded by D-045._

### D-040 — Initial `requirements.txt` with compatibility constraints, created before the GPU smoke test (2026-10-17)
- **Previous decision (D-009):** defer `requirements.txt` until the dependencies were selected, then pin exact versions from a verified Kaggle environment.
- **New evidence and reason:** the D-039 workflow (unpack ZIP → install dependencies → run notebook) needs a requirements file **before** the smoke test can run on Kaggle.
- **New decision:** create an initial `requirements.txt` listing **only** packages the approved Part 1 architecture and the smoke test import: transformers, accelerate, sentence-transformers, pymupdf, rank-bm25, chromadb, pydantic, numpy, pandas, pillow, packaging. **Lower-bound compatibility constraints only, not verified pins:**
  - `transformers>=4.57.0,<5`: Qwen3-VL support (CANDIDATE). Capped below 5 because the harness uses the v4 APIs `torch_dtype=` and `AutoModelForVision2Seq`.
  - `pymupdf>=1.24.0`: `find_tables().to_markdown()`.
  - `pydantic>=2.0`: `field_validator`.
  - `rank-bm25==0.2.2`: its latest release.
  - All others are loose lower bounds, so the preinstalled Kaggle versions are kept when they satisfy them.
- **Deliberately excluded:** `torch` and `torchvision` (CUDA-matched Kaggle builds must not be reinstalled; the install command pins torch to the preinstalled version), and IPython/Jupyter (provided by the runtime).
- **Not yet verified:** that these constraints resolve together on the current Kaggle image (OPEN, checked by S0 and the install log). **Exact final versions will be taken from the successful Kaggle environment and verified before the first Git commit**, and will replace these constraints.
- **Overlap noted:** the smoke test's `SMOKE_PIP_INSTALL` option (D-036) installs missing packages itself. With `requirements.txt` installed first, it should stay `False`; S0 then only reports versions.

### D-041 — Local Mac smoke test first; GPU validation and P1-EXP-001 deferred until GPU-machine access — DECIDED (2026-10-17)
- **Workflow:** the Part 1 smoke test runs **locally on the Mac first** (CPU only). Architecture and code changes are made on the basis of the local results. Full model/GPU validation (S2, S3, S5, S6, S7) and **P1-EXP-001 are deferred until GPU-machine access**. The **first Git commit remains deferred until the first successful full GPU run** (D-039 unchanged).
- _Commit timing superseded by D-045._
- **Local scope:** everything that does not need the GPU models: paths/config, data discovery, the manifest, text extraction, label inventory, vector and raster crops, multi-figure pages, tables, `*` markers, normalized rows, BM25 tokenizer, Chroma plumbing, the `evidence_ok` filter, label/citation grammar, the pydantic schema, JSON parsing, `ConversationState`, immutable-index checks, leakage and persistent-file hygiene.
- **GPU stages without CUDA** print `SKIPPED_LOCAL` and remain pending. **A skipped stage is never recorded as PASS.**
- **Local environment:** a Python 3.11 venv at `implementation/.venv` (git-ignored, excluded from the ZIP). No VLM, embedder or reranker weights are downloaded locally. CPU `torch` is installed only because the verbatim run-information cell imports it.
- **`requirements.txt` (updates D-040):** the active lines are now the local smoke-test scope, plus `ipykernel`/`nbclient` for local notebook execution. The GPU-run packages (`transformers`, `accelerate`, `sentence-transformers`) are kept as commented lines to be enabled for the GPU run. Versions remain unverified constraints, not pins.
- **Notebook structure change:**
  - The smoke test moved to an **appendix at the end** of `p1_rag.ipynb`, so it can validate helpers defined in the sections above it.
  - Validated helpers now live where the pipeline will use them: Section 1 (captions, figure/table location, rendering, table normalization, trust, data vintage, index fingerprint) and Section 4 (`ConversationState`). No retrieval, answering or submission logic is implemented.
  - New stages: **S8** (output control), **S9** (conversation state + immutable index), **S10** (hygiene). S2, S3, S5, S6 and S7 are GPU-only.
  - Locally, S4 uses a deterministic hashing substitute for embeddings, clearly labelled `LOCAL_SUBSTITUTE`. It tests index plumbing only and says nothing about retrieval quality.

### D-042 — RESULT: local Mac smoke test (2026-10-17)
- **Environment (RESULT, printed by S0):** macOS arm64; Python 3.11.14; CPU only (`cuda_available: False`); pymupdf 1.28.2, rank-bm25 0.2.2, chromadb 1.5.9, pydantic 2.14.1, numpy 2.4.6, pandas 3.0.6, pillow 13.0.0, packaging 26.3, torch 2.14.1 (CPU), ipykernel 7.4.0, nbclient 0.11.0. `transformers`, `accelerate` and `sentence-transformers` are not installed (GPU-run only). Hugging Face is reachable.
- **Execution:** `nbclient` run of `p1_rag.ipynb` with `RUN_SMOKE_TEST = True` set in memory only (the saved notebook keeps the default `False` and no outputs). Completed in 9.0 s, with 0 error outputs, 39 checks, 0 failed, 14 crops and 7 tables displayed inline.
- **Stage status (RESULT):** S0 INFO · **S1 PASS** · S2 SKIPPED_LOCAL · S3 SKIPPED_LOCAL · **S4 PASS** · S5 SKIPPED_LOCAL · S6 SKIPPED_LOCAL · S7 SKIPPED_LOCAL · **S8 PASS** · **S9 PASS** · **S10 PASS**.
- **S1 (RESULT):**
  - Manifest: 3 documents; page counts 37/7/7 match the manifest; every page has text (142,965 characters).
  - Trust: DOC3 p7 is low, the rest as in the manifest. Data vintage years: DOC1 2011, DOC2 2014, DOC3 none.
  - Captioned objects: DOC1 13 figures + 4 tables; DOC2 7 figures + 3 tables; DOC3 6 figures (including `Figure B-5 (corrected)`) + `Figure C-1` + 2 tables. Exactly one caption per label; the corrected figure is a separate object.
  - All 14 captions on the 9 probe pages were located. DOC1 figures are `vector`, DOC2/DOC3 figures are `raster`, and objects on multi-object pages do not overlap.
  - Ground truth parsed from normalized table rows: Table A-1 World 2012 outturn 2.4; Table A-1 advanced 2013 outturn 1.1; Table B-1 Euro area slope −0.31; Table B-1 U.S. 1961-2013 growth needed 2.9.
- **S4 (RESULT, hashing substitute embeddings):** 83-item collection with 7 low-trust items. Low-trust hits: 3 unfiltered → **0 with `evidence_ok` filter**. Queries did not change the index fingerprint. The BM25 tokenizer keeps `a-3`, `1-2`, `2000`/`2012` and `2.4%`, but splits `U.S.` into `u`, `s` (TUNE, open).
- **S8 (RESULT):** our label/citation grammar matches the validator's own `FIG`/`CIT` regexes on 51 figure-reference and 49 citation cases (all 40 `sample_submission.csv` rows plus edge cases). The schema accepts the valid answer and rejects all 5 invalid ones. JSON extraction 5/5. `NONE` formatting is valid. ±1% tolerance check correct.
- **S9 (RESULT):** a new conversation is empty; an override is visible only in its own conversation; history is per conversation; the turn number and the refusal are recorded; the latest override wins; override records are immutable. Index fingerprint `(83, ccdd4a84…dcd81)` is identical before and after the conversations.
- **S10 (RESULT):** no question/conversation ID patterns in the 6 repository text files; no new, deleted or modified files under `DATA266_Lab2_Part1/` or `implementation/`; no `submission.csv`. The full question-text leakage scan, run outside the notebook (the notebook never reads `Questions.csv`), found none.
- **Failures in the first local run and fixes (same day):**
  1. `S1.uncaptioned_mentions_are_external_sources` **FAILED**. The check assumed external labels appear only on `Source` lines, but DOC1 p26 cites `Table B-3` in body text (DOC1 p5 cites `Table B-79` on a Source line), both tables of the *Economic Report of the President*. **Fix:** the check was removed as an incorrect assumption. Uncaptioned labels are now reported as a WARN.
  2. `S1.star_markers_preserved` **FAILED**. PyMuPDF `to_markdown()` wraps bold cells in `**…**`, which the marker count picked up (28 vs 2 for Table 1-1). **Fix:** `**` is removed before counting. After the fix, page text = cells = markdown for every table (Table 1-1: 2; Table A-1: 2; others 0).
- **Fixes made during local development, before the first recorded run** (found by inspecting the PDFs and rendered crops):
  - `TABLE_STRATEGIES` changed from `("lines", "text")` to `("lines",)`. The `text` strategy produced a page-sized false table on every table page; `lines` found all 9 numbered tables.
  - The DOC1 vector-figure logic was redesigned. DOC1 places the figure label, title and source in a **left/right margin column** next to the chart, so the planned "drawings in the band below the caption" rule (D-017) would have captured body text. It now uses drawing clusters nearest the caption, plus the narrow margin blocks stacked under the caption, plus axis-label text inside the padded figure box. Icons smaller than `MIN_RASTER_FIGURE_PT` are ignored.
  - The caption-chain rule was limited to narrow margin blocks (`MARGIN_COLUMN_MAX_FRAC`). In DOC2/DOC3 it had pulled full-width body paragraphs into table crops.
  - Footnote/source lines starting at the object's bottom edge are now attached (they were cut in half).
  - Table normalization detects orientation once per table and handles average-period columns. The main values in Table A-2 are classed as `outturn` from its caption.

### D-043 — Design consequences of the local smoke test (2026-10-17)
- **Forecast flag (refines D-018 and D-029), DECIDED:** `*` markers alone are insufficient. **Only DOC1 Table 1-1 marks 2011/2012 with `*`. Tables 1-2, 1-3 and 1-4 show 2011/2012 without `*`**, although they are fall-2011 forecasts (DOC1 data vintage September 2011; Figure 1-4's source note also says "Values for 2011 and 2012 are estimates"). The normalized rows therefore set `kind = forecast` when there is a `*`/"forecast" marker **or** when the year is at or after the document's data vintage year from the manifest. Locally this gives 6 forecast rows in each DOC1 table.
- **Bracketed values, DECIDED:** in Table A-2 the value in brackets is the fall-2011 forecast (stated in its caption). It is kept as a separate `forecast` record next to the `outturn` record (27 outturn + 18 forecast rows).
- **Router safety (refines D-027), DECIDED:** labels that match the validator grammar but are not knowledge-base objects exist (`Table B-3`, `Table B-79`, which look like DOC3's `B-` series). The router must resolve labels **only against the caption inventory**, never by the label pattern alone, and an unknown label must go to the `unknown_label` path.
- **Table evidence formatting, OPEN:** PyMuPDF `to_markdown()` adds `Col2…ColN` headers from title rows, bold `**` markup, and repeats merged footnote cells in every column. Generator evidence should be rendered from the cleaned rows instead (to decide during P1-EXP-001 implementation).
- **Chart observations (visual inspection of the crops, not a measurement):** many DOC2/DOC3 charts print data labels on points or bars (e.g. A-2/A-3 end points, A-6/A-7 bars, B-5 vs B-5 (corrected) for 2012). DOC1 charts have none, and DOC1 Figures 1-3, 1-5 and 1-6 are maps with data call-out boxes. **Figure C-1 contains injected instruction text drawn inside the chart image.** This confirms that low-trust images must never reach the VLM (D-026).
- **New crop-geometry parameters (all TUNE, in the config cell):** `MIN_RASTER_FIGURE_PT = 50`, `FIGURE_CAPTION_MAX_GAP_PT = 40`, `DRAWING_CLUSTER_PAD_PT = 6`, `FIGURE_CONTEXT_PAD_PT = 30`, `CAPTION_CHAIN_MAX_GAP_PT = 18`, `MARGIN_COLUMN_MAX_FRAC = 0.35`.
- **Still pending the GPU machine:** S2 (embedder), S3 (reranker), S5 (Qwen3-VL-4B), S6 (fallback, if needed), S7 (sequential residency), and installing/verifying the GPU-run requirements. D-020, D-024 and D-031 remain CANDIDATE.

### D-044 — Clarification: local smoke-test changes are fixes, not tuning (2026-10-17)
- The code and parameter changes recorded in D-042 and D-043 are classified as **bug, compatibility and extraction fixes**: the `TABLE_STRATEGIES` change, the DOC1 vector-figure crop redesign, the caption-chain limit, the footnote attachment, table orientation, the forecast/outturn classification, and the corrected smoke-test checks. They were driven by the structure of the provided PDFs and by the smoke-test checks themselves. The crop-geometry values (D-043) were set by visually inspecting the rendered crops of the knowledge-base documents.
- **No model, retrieval or parameter tuning based on evaluation results has occurred.** No question set has been answered, no golden set exists, and no retrieval or answer metric has been computed.
- **Tuning remains blocked until the golden set has been created and committed** (D-006, D-034, D-039).

---

> **Part 2 preparation (2026-10-17).** Entries D-045 to D-063 cover the commit-policy change and the approved Part 2 architecture, which was reviewed and corrected by the team. Nothing has been trained. GPU stages are prepared but untested.

### D-045 — Commit and evaluation-artifact policy (supersedes the commit timing in D-039 and D-041) — DECIDED (2026-10-17)
- **Previous decision (D-039, D-041):** no Git commit until P1-EXP-001's first successful GPU run.
- **Evidence:** the assignment requires test questions and prompts to be **written before tuning and committed**, with the Git timestamp checked (C2.3; Part 2 rubric 2.3.1). The blanket rule conflicts with this for both the Part 1 golden set and the Part 2 prompts.
- **New policy:**
  - Local smoke testing, GPU compatibility smoke testing, and bug/compatibility fixes may all happen before the first commit.
  - **No retrieval, model or training hyperparameter tuning based on evaluation results may happen before the required evaluation artifacts are committed.**
  - **Before the first real Part 1 or Part 2 tuning/training experiment:** create `eval/p1_golden_set.csv` and `eval/p2_prompts.csv`, then make the **first Git commit**, containing those evaluation artifacts and the current implementation.
  - **No push** until the team explicitly approves it.
- `eval/` is **not created yet**.

### D-046 — Part 2 notebook structure and flags — DECIDED (2026-10-17)
- **One notebook:** `notebooks/p2_finetune.ipynb`, created now. No other files: no `src/`, scripts, configs or experiment notebooks.
- **Cell order:**
  - Cell 1: the professor's run-information cell, verbatim.
  - Cell 2: the central configuration cell.
  - Sections 1–6: data, fine-tuning, generation, evaluation, Hugging Face artifacts, safety.
  - Appendix: the smoke test.
- **Flags:** `RUN_SMOKE_TEST`, `RUN_TRAINING` and `RUN_EVALUATION`, all `False` by default. Setting `RUN_TRAINING` or `RUN_EVALUATION` to `True` raises `NotImplementedError` until real runs are implemented.
- **Experiment IDs:** the smoke stages (P2-L\* CPU, P2-S\* GPU) are **not experiments** and have no ID. **P2-EXP-001 begins only with a real training run.**
- **What is implemented:** helper functions (data cleaning, split, preprocessing, loader, LoRA attach, loss, optimizer step, adapter save, pipeline/generation, metric wrappers, human-eval pairing, model card) are implemented and validated. No training, generation or evaluation run exists.

### D-047 — Dataset: Naruto BLIP captions stays CANDIDATE; license OPEN (2026-10-17)
- **RESULT (verified from the Hugging Face Hub API, README, `dataset_infos.json` and parquet footers on 2026-10-17):**
  - **Naruto:** the professor's ID `lambdalabs/naruto-blip-captions` **has been renamed** and redirects to `lambda/naruto-blip-captions`.
    - Available: not gated, not disabled.
    - **1,221 rows** (one `train` split; 2 parquet files of 611 + 610 rows, about 668 MB; each file is a single row group).
    - Fields: `image` (Image), `text` (string). All 1,221 captions are non-empty (967 unique).
    - The HF dataset viewer is disabled.
    - **No license is stated:** no card metadata, no license tag, an empty `license` field in `dataset_infos.json`, and nothing in the README. The README credits the images to narutopedia.com with BLIP-generated captions.
  - **Pokémon:** `reach-vb/pokemon-blip-captions` is available, has **833 rows**, fields `image`/`text`, one parquet file (about 95 MB), and its card states **`cc-by-nc-sa-4.0`**.
- **Assessment (OPEN):** the Requirements PDF lists Naruto and Pokémon by name and then allows "another captioned set of at least 500 images **with a stated license**". Whether a stated license is also required for the two named datasets is ambiguous. Read strictly, **Naruto does not meet a stated-license requirement; Pokémon does.** Both depict copyrighted characters, so the result is non-commercial research only either way (C4).
- **Decision:** `DATASET_ID = "lambda/naruto-blip-captions"` remains **CANDIDATE**, not locked. `DATASET_ALTERNATIVE_ID = "reach-vb/pokemon-blip-captions"` is recorded. **The dataset is not changed without a team decision.**
- _Superseded by D-064 (Pokémon selected)._

### D-048 — Cleaning and deduplication — DECIDED (thresholds TUNE) (2026-10-17)
- Images are loaded undecoded (`Image(decode=False)`) so corrupted files can be counted.
- Each image is decoded with a `verify()` + `load()` pass, EXIF orientation is applied, transparency is composited on white, and the result is converted to RGB.
- Removed, with reasons counted: missing image, decode error, smaller than `MIN_IMAGE_SIDE = 256` (TUNE), missing or empty caption, exact duplicate (SHA-256 of decoded pixels), and near duplicate (64-bit dHash Hamming ≤ `NEAR_DUP_HAMMING_MAX = 4`, TUNE). The first occurrence of a duplicate is kept.
- **Deduplication happens before the split**, so near-duplicates cannot leak across train/test (which would bias KID and the memorization check).

### D-049 — Split — DECIDED (2026-10-17)
- A 90/10 split of the **cleaned** rows with `numpy.random.default_rng(266)`, taken over dataset order. For 1,221 rows that gives 1,099 train and 122 test.
- Test images are used **only** for evaluation: KID reference images, and in-domain prompts drawn from test captions.

### D-050 — Preprocessing — DECIDED (2026-10-17)
- The short side is resized to 512 (Lanczos), then center-cropped to 512×512. **No augmentation** (no flip, no random crop): Naruto images contain asymmetric details, and determinism is needed for caching.
- Tensors are float32 CHW in [-1, 1]. The data loader is seeded, with `num_workers=0`.

### D-051 — Base model — DECIDED (2026-10-17)
- `stable-diffusion-v1-5/stable-diffusion-v1-5`, fp16 weights variant, 512×512. The **same base model** is used for both runs.
- Rejected: SDXL (much higher cost for training and 120 generations); SD3.5 / FLUX (fp16 risk on a T4, and too large). Part 3 reuses this LoRA in SD 1.5 img2img.

### D-052 — Method — DECIDED (2026-10-17)
- **LoRA through PEFT/diffusers**, applied to the **UNet attention projections only** (`to_q`, `to_k`, `to_v`, `to_out.0`). The **text encoder is frozen.** Gaussian LoRA init, dropout 0.
- **Precision:** frozen weights in fp16, LoRA parameters in fp32, fp16 autocast with GradScaler on the GPU, **subject to smoke-test validation** (P2-S4).

### D-053 — Run A vs Run B: the single controlled variable — DECIDED (2026-10-17)
- **Run A:** LoRA rank 4, alpha 4. **Run B:** LoRA rank 64, alpha 64.
- **Everything else is identical:** dataset, split, base model, target modules, learning rate, scheduler, optimizer, effective batch, training steps, generation settings and evaluation.
- **RESULT (local, exact from the real SD 1.5 UNet config on the meta device, no weights):**
  - Run A: 797,184 trainable parameters (0.0927% of 860,318,148).
  - Run B: 12,754,944 trainable parameters (1.4623% of 872,275,908); 16× Run A.
  - The local configuration check shows the two runs differ only in `rank`, `alpha` and the run name.

### D-054 — Training hyperparameters (shared by both runs) (2026-10-17)
- **DECIDED:** AdamW (β 0.9/0.999, weight decay 1e-2, eps 1e-8), gradient clipping 1.0, seed 266.
- **TUNE:**
  - learning rate 1e-4
  - cosine schedule with 5% warmup
  - `max_train_steps = 1500`
  - effective batch 4, with micro-batch 4 × accumulation 1 (the split falls back to 2×2 or 1×4 if memory requires)
  - gradient checkpointing off
- The TUNE values are **fixed once, from P2-S4 timing and memory measurements, before P2-EXP-001**. They are never adjusted from evaluation results (D-045, D-044 principle). The final checkpoint is used; checkpoints are never selected by test metrics.

### D-055 — Latent and text-embedding handling (2026-10-17)
- **Text-embedding caching: DECIDED.** The text encoder is frozen, so its outputs are cached and the text encoder is released from the GPU.
- **VAE latent caching: CANDIDATE.** The notebook supports three `latent_mode` values:
  - `online`: normal VAE encoding with a fresh posterior sample each step. This is the **current default**.
  - `cached_moments`: the posterior mean and std are cached and **a fresh sample is drawn every step**, which matches the online distribution.
  - `cached_mean`: the deterministic posterior mean.
- **No single stochastic posterior sample is ever frozen.** An unknown mode raises an error.
- P2-S4 measures seconds per step for `online` vs `cached_moments` and records whether caching is needed for the runtime budget. The choice is then made explicitly.

### D-056 — Generation and NSFW filter — DECIDED (steps TUNE) (2026-10-17)
- DPMSolver++ (`DPMSolverMultistepScheduler`), 30 steps (TUNE), guidance 7.5, 512×512, seeds 0 and 1 on a device generator, LoRA scale 1.0, no negative prompt. Identical for base, A and B.
- **NSFW filter:** the SD 1.5 pipeline's built-in safety checker, kept on; flagged counts are reported.
- **Prompts:** 20 = 10 in-domain (test captions drawn with seed 266) + 5 out-of-domain + 5 compositional. They will be stored in `eval/p2_prompts.csv` (not created yet; D-045).

### D-057 — Metric implementations (2026-10-17)
- **DECIDED:**
  - KID: `torchmetrics` `KernelInceptionDistance` (requires `torch-fidelity`) on uint8 NCHW, 20 in-domain generations vs the about 122 test images. Subset size = min(set sizes) = 20, 100 subsets, reported as mean ± std **with a noise caveat**.
  - LPIPS: AlexNet backbone, inputs in [-1, 1], seed 0 vs seed 1 per prompt.
  - Memorization: CLIP image embeddings of 10 in-domain final-run images vs all training images; top-1 cosine; 3 closest pairs shown.
  - CLIP score: the torchmetrics definition (100 · max(cos, 0)), computed from one loaded CLIP model.
- **CANDIDATE:** CLIP model `openai/clip-vit-large-patch14`. It is the same family as SD 1.5's text encoder, which is a bias to note in the report.
- **OPEN:** an extended KID over all test captions (extra GPU time).

### D-058 — Human evaluation protocol (2026-10-17)
- **DECIDED:** 25 (prompt, seed) pairs drawn with seed 266 from the 40 per model; final-vs-base side randomised per pair with seed 266. At least 3 raters (both members plus one outside person) judge `domain_style` and `prompt_match`; win rate per criterion.
- **OPEN:** the ratings file `eval/p2_human_ratings.csv` is required so the notebook can compute the win rate (C2: every number computed in the notebook). It will be created only after approval.

### D-059 — Checkpoints and artifacts — DECIDED (2026-10-17)
- Adapters, generated images and caches go to `P2_WORK_DIR` (default `~/data266_lab2_work/p2`, or `/kaggle/working/p2_work` on Kaggle), **outside the repository**. Smoke-test adapters go to system temporary directories and are deleted.
- Adapters are saved in diffusers LoRA format. **Both adapters, all images (with prompt, seed and model metadata) and the model card go to Hugging Face, never to GitHub.**
- The HF token is read from `$HF_TOKEN` only. HF repo names are **OPEN**.

### D-060 — Reproducibility — DECIDED (2026-10-17)
- Seed 266 for the split, data loader, training noise/timestep generator and in-domain prompt draws; generation seeds 0/1; versions and GPU printed.
- Bit-exact results across different GPUs are **not** guaranteed (cuDNN kernels); this is documented, not hidden.

### D-061 — Runtime and VRAM — ESTIMATE (2026-10-17)
- **ESTIMATES, none measured:**
  - SD 1.5 fp16 inference: about 3–4 GB, 3–5 s per image on a T4.
  - LoRA training at micro-batch 4 without checkpointing: about 7–11 GB.
  - 1,500 steps: about 35–60 min per run on a T4.
  - Whole lab session: about 2–3 h.
- These are replaced by P2-S4 measurements before the step budget is fixed. Every peak must stay ≤ 16,384 MB, even on a GPU with more memory.

### D-062 — `requirements.txt` for Part 2 — CANDIDATE (2026-10-17)
- **Added as active** (needed by the local smoke test, without any model weights): `datasets>=2.19`, `transformers>=4.57.0,<5`, `diffusers>=0.32`, `peft>=0.13`, `accelerate>=0.26.0`.
- **Added as commented GPU-run lines:** `torchmetrics>=1.0`, `torch-fidelity>=0.3`, `lpips>=0.1.4`.
- **Observed side effect:** `transformers<5` caps `huggingface-hub` below 1.0, so pip downgraded it locally from 2.2.0 to 0.36.2. The Part 1 local smoke test was re-run afterwards with unchanged statuses (S1, S4, S8, S9 and S10 PASS; GPU stages SKIPPED_LOCAL). `pip check`: no broken requirements.
- These are constraints, **not verified pins**. Final versions come from the GPU machine.

### D-063 — RESULT: Part 2 local Mac smoke test (2026-10-17)
- **Environment:** macOS arm64, Python 3.11.14, CPU only. torch 2.14.1, datasets 5.0.1, pyarrow 26.0.0, transformers 4.57.6, diffusers 0.39.0, peft 0.21.2, accelerate 1.15.0, huggingface-hub 0.36.2. torchmetrics, torch-fidelity and lpips are not installed (GPU run only).
- **Execution:** `nbclient` run with `RUN_SMOKE_TEST = True` set in memory only. The saved notebook keeps the default flags and no outputs. Final run: completed in 13.6 s with 0 errors. A default run with all flags `False` produced 0 errors and 5 skip lines.
- **Stage status:** P2-L0 to P2-L9 all **PASS**. **P2-S0 to P2-S7 SKIPPED_LOCAL** (not tested; pending the GPU machine).
- **Key local results:**
  - **L1:** of the 24 synthetic rows, exactly the 6 planted problems were removed (2 decode errors, 1 exact duplicate, 1 near duplicate, 1 missing caption, 1 too small). First occurrences were kept. The minimum dHash distance between kept images is 19.
  - **L2:** the Naruto card facts in D-047. Captions were read via column projection only (18,216 bytes; no images downloaded): 1,221 non-empty, mean 8.93 words, max 41.
  - **L3:** 1,099/122 for 1,221 rows; deterministic, disjoint, seed-sensitive; no near-duplicate across the split.
  - **L4:** six input aspect ratios → 512×512 RGB; tensor [-1, 1]; batch (4, 3, 512, 512); seeded loader order.
  - **L5:** CLIP tokenizer limit 77. Real Naruto captions: max 43 tokens, mean 11.0, **0 truncated**.
  - **L6:** the two runs differ only in rank, alpha and run name; prompt table 10/5/5 drawn deterministically from test captions; wrong group counts are rejected.
  - **L7:** KID subset-size rules; uint8 NCHW input; CLIP-score definition (100/0/0); memorization nearest neighbour; 25 unique, deterministic, side-randomised human-eval pairs (final model on the left in 14 of 25); win-rate arithmetic.
  - **L9:** exact LoRA sizes (D-053); a tiny random UNet ran 2 optimizer steps with gradient accumulation (finite loss and gradients; LoRA parameters updated; frozen parameters unchanged); the adapter saved with all 64 tensors and its temp directory was removed; latent modes behave as specified.
  - **L8:** results, run-table, model-card and image-metadata schemas. No repository or professor-data file was new, deleted or modified. No `eval/` and no work directory were created.
- **Outside the repo:** the only downloads were SD 1.5 tokenizer files and `unet/config.json` (about 1.5 MB in the HF cache), plus parquet footers and the caption column.
- **Failure and fix (compatibility/data handling, not tuning; D-044 principle):** the first run reported `caption_column_bytes` of 96 (Naruto) and 48 (Pokémon). The arrow field index of `text` was used as a parquet column index, but the `image` struct occupies two physical columns, so it pointed at `image.path`. **Fix:** look the column up by its parquet path. Re-run: 18,216 and 13,433 bytes. The captions themselves were always read correctly by name.
- **Addition beyond the approved local plan, flagged:** **P2-L9** (exact LoRA sizes from the real UNet config + tiny random-UNet plumbing). It was added so the training-step code is exercised before the lab instead of being debugged there. It downloads no weights.

### D-064 — Part 2 dataset: Pokémon BLIP captions selected; Naruto rejected for EXP-001 — DECIDED (2026-10-17)
- **Previous decision (D-047):** `lambda/naruto-blip-captions` as CANDIDATE, with its license OPEN.
- **Evidence (D-047 RESULT, re-verified by P2-L2 in D-067):**
  - Pokémon: `reach-vb/pokemon-blip-captions` has **833 images** (meets ≥500), fields `image`/`text`, and an **explicit stated license, `cc-by-nc-sa-4.0`**.
  - Naruto: still available, but its current HF card states **no license**.
- **Decision:** the Part 2 dataset is **`reach-vb/pokemon-blip-captions`**.
- **Naruto: CONSIDERED / REJECTED FOR EXP-001** solely because its current HF card has no stated license, which creates unnecessary rubric and license risk. **The rejection is not about dataset quality.**
- **Configuration changes in `p2_finetune.ipynb`:**
  - `DATASET_ID = "reach-vb/pokemon-blip-captions"` and `DATASET_LICENSE = "cc-by-nc-sa-4.0"` (P2-L2 now checks the live card against this value).
  - `DATASET_ALTERNATIVE_ID` replaced by `DATASET_REJECTED_ID = "lambda/naruto-blip-captions"`, which is recorded only, for the audit trail.
  - The P2-L3 split check uses the selected dataset's real row count instead of a fixed 1,221.
  - The P2-L8 model-card check uses `DATASET_LICENSE`.
- **Consequences:**
  - The split becomes **750 train / 83 test** before cleaning (exact sizes after cleaning: OPEN until P2-S1). KID's reference set shrinks to about 83 test images; the subset size stays limited by the 20 in-domain generations (D-057).
  - D-050's "no augmentation" decision stands. Its asymmetric-detail rationale was Naruto-specific, but the decision rests on determinism and exact latent caching, which still apply.
  - **License follow-ups (OPEN):** CC BY-NC-SA 4.0 requires **attribution** (BY), **non-commercial use** (NC), and **ShareAlike** (SA). The license to declare for the trained adapters and the generated-image dataset still has to be decided; it must stay compatible with SA, alongside the base model's CreativeML OpenRAIL-M. The model card must credit the dataset. The characters remain copyrighted, so use is non-commercial research only (C4).
- The full dataset (about 95 MB of parquet) was **not** downloaded. The local check reads only the card, the parquet footers and the caption column (13,433 bytes).

### D-065 — P2-L9 retained as a pre-GPU training-code smoke test — DECIDED (2026-10-17)
- P2-L9 is kept exactly as implemented. It validates on CPU:
  - **LoRA-only updates:** only the LoRA parameters are trainable (fp32) and they change.
  - **Frozen base weights unchanged:** compared tensor by tensor.
  - **Forward, backward and the optimizer step**, including gradient accumulation, gradient clipping and the scheduler step.
  - **Adapter save and reload:** diffusers-format save; the reloaded file holds every LoRA tensor; the temp directory is removed.
  - The latent-mode semantics (D-055), and exact LoRA sizes from the real SD 1.5 UNet *config* on the meta device.
- **It is not P2-EXP-001** and **uses no pretrained diffusion weights**: it uses a tiny randomly initialised UNet, plus only `unet/config.json` to compute the parameter counts.

### D-066 — Status: no tuning has occurred; GPU-only checks pending (2026-10-17)
- **No tuning has occurred** in Part 1 or Part 2. Every change so far is an architecture decision, a dataset decision, or a bug/compatibility/data-handling fix (D-044, D-063). No evaluation result exists, and no TUNE value has been changed from results.
- **Pending the GPU machine (untested):**
  - Part 2: P2-S0 to P2-S7 (environment, real-image batch, base generation, adapter sizes, 3-step training per run and latent mode, adapter reload, metric plumbing, memory release).
  - Part 1: S2, S3, S5, S6 and S7.
- Before any tuning or real training: create `eval/p1_golden_set.csv` and `eval/p2_prompts.csv`, then make the first commit (D-045). `eval/p2_human_ratings.csv` is created only when the human-evaluation phase begins.

### D-067 — RESULT: Part 2 local smoke test after the dataset switch (2026-10-17)
- **Execution:** `nbclient` run with `RUN_SMOKE_TEST = True` set in memory only. Completed in 16.0 s with 0 errors. A default run with all flags `False` produced 0 errors and 5 skip lines.
- **Stage status:** P2-L0 to P2-L9 all **PASS**; P2-S0 to P2-S7 **SKIPPED_LOCAL**.
- **P2-L2 (selected dataset):**
  - `reach-vb/pokemon-blip-captions` is available (not gated, disabled or private), with 833 rows, columns `image`/`text`, and 1 parquet file.
  - **The stated license `cc-by-nc-sa-4.0` matches `DATASET_LICENSE` (PASS).**
  - Captions, read by column projection (13,433 bytes): 833 non-empty, 736 unique, mean 9.29 words, max 16.
  - The rejected Naruto card was recorded with `license_stated: None` and 1,221 rows.
- **P2-L3:** 833 rows → 750 train / 83 test; deterministic, disjoint, seed-sensitive.
- **P2-L5:** Pokémon captions have a maximum of 18 tokens, mean 11.4, **0 truncated** at 77.
- **P2-L8:** no repository or professor-data files new, deleted or modified; no `eval/`; no work directory.
- **The other stages are unchanged from D-063**, including P2-L9's exact LoRA sizes (A 797,184; B 12,754,944).

---

> **Part 3 preparation (2026-10-17).** Entries D-068 to D-088 record the team-approved Part 3 architecture and the local smoke-test results. No real agent model has been run and no GPU stage has been executed. P3-EXP-001 has not started.

### D-068 — Part 3 notebook, flags and smoke-test status — DECIDED (2026-10-17)
- **One notebook:** `notebooks/p3_agents.ipynb`, created now. No `src/`, modules, configs, scripts, extra notebooks, `eval/` or `traces/`.
- **Cell order:** run-information cell first; one central configuration cell; typed schemas/state; backends; Planner, Vision, Prompt, Generation and Critique helpers; orchestrator + traces; Gradio; evaluation helpers; safety placeholder; local and GPU smoke-test appendix.
- **Flags:** `RUN_SMOKE_TEST`, `RUN_PIPELINE` and `RUN_EVALUATION` default to `False`; `ENABLE_CRITIQUE = True`. `RUN_EVALUATION = True` raises `NotImplementedError`.
- **The smoke stages (P3-L\*, P3-S\*) are not experiments.** P3-EXP-001 starts only with a real evaluation run.

### D-069 — Orchestration — DECIDED (2026-10-17)
- Plain Python functions plus an explicit state machine, with one shared pydantic `AgentState`. **LangGraph rejected:** the flow is linear with one bounded loop, so it would add a dependency without a structural benefit.
- Typed errors (`AgentFailure` → `AgentError` + a final status). Deterministic transitions. `run_request` never raises.

### D-070 — Shared state schema — DECIDED (2026-10-17)
- `AgentState` (strict: unknown fields are rejected and assignments are validated): request id, timestamps, request, image reference (hash/size only), `phase`, `status`, `plan`, `vision`, `injection`, `prompt_specs`, `attempts`, `critiques`, `revision_count` (0 to 2, enforced on assignment), final message/answer/image reference, errors, trace, config snapshot.
- **Statuses:** PENDING, ANSWERED, COMPLETED, ACCEPTED, MAX_REVISIONS, REFUSED, NEEDS_CLARIFICATION, FAILED_INPUT, FAILED_MODEL, FAILED_GENERATION, BLOCKED_UNSAFE_OUTPUT, FAILED_INTERNAL.
- **Phases and transitions:** created → input_checked → planned → (vision_done) → gated → prompted → generated → critiqued → prompted …, with `final` terminal. Illegal transitions raise. `state_invariants()` is checked at the end of every request.

### D-071 — Planner — DECIDED (2026-10-17)
- **Request phase (before Vision):** deterministic screens (unsafe keyword patterns; requests to follow the image's text; the SD safety checker on the **input** image), then the VLM's intent classification, validated against the schema. Intents: caption_question, style_change, edit, enhance (part of the rubric's "edit or enhancement" class), domain_style, unsupported.
- Invalid planner output becomes NEEDS_CLARIFICATION. An image-requiring intent without an image becomes NEEDS_CLARIFICATION. Unsupported requests become REFUSED.
- **Post-vision gate (deterministic):** the injection rule (D-073) and the real-person rule (D-078). Caption/question requests stop after Vision with status ANSWERED.

### D-072 — Shared VLM — CANDIDATE (2026-10-17)
- Part 1's VLM is reused for planner semantics, vision, prompt rewriting and critic judgement: primary `Qwen/Qwen3-VL-4B-Instruct`, fallback `Qwen/Qwen2.5-VL-3B-Instruct`.
- **It stays CANDIDATE until the shared GPU smoke test succeeds.** If Part 1 moves to the fallback, Part 3 moves with it unless measured evidence requires a different model.

### D-073 — Image text and prompt-injection policy — DECIDED (2026-10-17)
- **Any text observed inside an image is untrusted data and never an instruction.**
- **Enforced in code:**
  - `UntrustedText` is frozen and its trust label is fixed. The Vision agent re-wraps whatever the model returns, so the model cannot upgrade trust.
  - Image text reaches a model only inside a delimited `<UNTRUSTED_IMAGE_TEXT>` block.
  - A deterministic quarantine removes image text from model-written prompts, unless the user's own request quotes it.
  - **If any instruction-like pattern appears in a model-written prompt or critic revision instruction, that entire model output is discarded** and a deterministic template (the user's request plus the trusted caption) is used instead.
- **Caption/question routes:** the image text may be reported (labelled "reported as data, not followed") and the user's genuine question is still answered.
- **Generation/edit routes:** if instruction-like image text is detected, `injection_detected = True` and the **generation/edit action is refused safely**. The refusal is recorded in the trace. This aligns with the rubric's "refuse instructions hidden in the image".

### D-074 — Generation — DECIDED (2026-10-17)
- **Base model:** SD 1.5. txt2img and img2img share **one component set** (no extra memory).
- **Style change:** img2img.
- **Domain style:** img2img + Part 2 LoRA when an input image is present, otherwise txt2img + Part 2 LoRA.
- **`GENERATOR_MODE = "base"`** until the real Part 2 adapter exists; `P2_ADAPTER_REPO = None`. A request needing the adapter in base mode is recorded as `adapter: none`. Requesting `p2_lora` without a loaded adapter fails with FAILED_MODEL. **No adapter is ever fabricated or substituted.**
- Model, prompt, seed, steps, strength and guidance are recorded for every attempt. Seeds are `seed + attempt − 1`.

### D-075 — Edit model — CANDIDATE (2026-10-17)
- **Primary edit candidate:** `timbrooks/instruct-pix2pix`, loaded on demand. **It is not DECIDED until P3-S5 succeeds on the GPU.**
- **Fallback:** deterministic enhancement (autocontrast, sharpness, colour) + low-strength SD 1.5 img2img guided by the edit instruction.
- Both paths are prepared. The edit backend is passed explicitly (`generation_request(..., edit_backend=...)`) and recorded in `model_id`; the generator branches on the request, not on a global. **IP2P weights are not downloaded locally.**

### D-076 — Critique — DECIDED (structure) / TUNE (τ) (2026-10-17)
- **Inputs:** CLIP ViT-L/14 similarity (the same model as Part 2), a short VLM judgement (ok / goal_met / preserved / reason / revision instruction), and an output safety check (the pipeline's NSFW flag + the SD safety checker).
- **The orchestrator owns the ACCEPT/REVISE decision and the loop limit, not the VLM.**
- **Intent-aware rule:** generation/style intents require CLIP ≥ τ plus goal met; edit/enhance require goal met and preservation, with CLIP not required. Unsafe outputs always revise. An invalid critic output is treated as REVISE (bounded).
- **τ = `CLIP_ACCEPT_THRESHOLD = 25.0` is TUNE and will not be tuned before `eval/p3_scenarios.csv` is committed (D-045).**

### D-077 — Revision loop — DECIDED (2026-10-17)
- At most **2 revisions** (3 attempts). ACCEPT ends the loop immediately. At the limit, the best **safe** attempt is returned with status MAX_REVISIONS; if no safe attempt exists, BLOCKED_UNSAFE_OUTPUT is returned and no image is shown.
- With the critique loop disabled, the status is COMPLETED (the rubric's comparison condition).

### D-078 — Safety router and real-person policy — DECIDED (2026-10-17)
- **Screens:** unsafe-request patterns; requests to obey the image's text; the SD safety checker on input and output images; the VLM's unsafe flag.
- **Real-person policy (team decision):**
  - **Refused:** deceptive edits, identity-altering deceptive manipulation, impersonation/misrepresentation, unsafe transformations.
  - **Allowed:** benign style changes, benign enhancement, clearly non-deceptive transformations.
  - **Mechanism:** refusal when Vision reports `real_person_likely` **and** the request is deceptive (deterministic deception patterns, or the planner VLM's `deceptive_intent` flag).
- **Pattern lists (TUNE wording; reviewed with the red-team set):** `UNSAFE_PATTERNS`, `DECEPTION_PATTERNS`, `INJECTION_PATTERNS`, `OBEY_IMAGE_PATTERNS`.

### D-079 — JSON traces — DECIDED (2026-10-17)
- One trace step per agent call (`input_guard`, `planner`, `vision`, `prompt`, `generation`, `critique`), plus orchestrator decision steps (gate, revise, accept, limit). Each step records its number, timestamp, elapsed time, status, input/output summaries and a note.
- The trace record carries request id, route, intent, status, revision count, injection report, final message and image reference, errors and a config snapshot.
- **Redaction:** images are stored as sha256 + size, never pixels; strings are truncated; `hf_…` tokens, `token=`/`api_key=`/`password=` values and any `*TOKEN` environment value are replaced with `[REDACTED]`.
- During smoke tests traces go **only** to a system temporary directory, which is deleted. Real traces go to `traces/` later.

### D-080 — Failure handling — DECIDED (2026-10-17)
- Missing image (for an image route) → NEEDS_CLARIFICATION.
- Corrupt, empty, missing-path, out-of-range image, empty or invalid request → FAILED_INPUT.
- Model unavailable or invalid model output → FAILED_MODEL.
- Generation error → FAILED_GENERATION.
- Unexpected exception → FAILED_INTERNAL.
- Every outcome has a user-facing message and a trace.

### D-081 — Gradio — DECIDED (2026-10-17)
- `gr.Blocks` with per-agent JSON panels (Planner, Vision, Prompt, Generation, Critique), the result image and the JSON trace.
- `gradio_callback` is a pure function that never raises, and reset clears every panel.
- **`share=False`** and `server_name="127.0.0.1"`; no public link is ever relied on. The app is launched manually (`launch_app(build_app())`) once `RUN_PIPELINE = True`. Real models load only when `RUN_PIPELINE` is True.

### D-082 — Residency, VRAM and latency — ESTIMATE / TUNE (2026-10-17)
- **ESTIMATES:** Qwen3-VL-4B about 9 GB; SD 1.5 set about 2.6 GB; IP2P about 2.2 GB; CLIP-L about 0.9 GB. All co-resident is about 15 GB plus activations, **not safe on 16 GB**.
- **Policy `RESIDENCY = "co_resident"` (TUNE):** VLM + SD 1.5 + CLIP resident; IP2P loaded on demand and released. `"offload"` uses diffusers CPU offload. P3-S9 measures both sequential and co-resident behaviour **without ever forcing VLM + SD + IP2P to be co-resident**.
- **Latency ESTIMATE:** about 30–90 s median per request on a T4.

### D-083 — Generation parameters — TUNE (2026-10-17)
- 30 steps, guidance 7.5, 512×512, seed 266.
- img2img strength: 0.60 (style change), 0.70 (domain style).
- IP2P: 20 steps, guidance 7.5, image guidance 1.5.
- Enhancement: autocontrast cutoff 1, sharpness 1.3, colour 1.05, img2img strength 0.25.
- Shared negative prompt.
- Not tuned before the scenario files are committed.

### D-084 — Part 3 evaluation artifacts — OPEN (2026-10-17)
- **Later (not created now):** `eval/p3_scenarios.csv` (15 = 3 per category, each with a pass/fail rubric, committed before tuning), `eval/p3_redteam.csv` (10 cases covering image instructions, unsafe requests, real-person edits, broken/empty files), `eval/p3_human_judgements.csv` (both members' independent pass/fail plus disagreement resolutions), and `traces/*.json`.
- The ~25 input images go to a Hugging Face dataset (`P3_INPUTS_HF_REPO`, OPEN).
- The evaluation helpers already implement the schemas, success rate, judge agreement, critic agreement, attack success, median latency and the with-vs-without-critique table.

### D-085 — `requirements.txt` for Part 3 — CANDIDATE (2026-10-17)
- **Added:**
  - `gradio>=5,<6`. gradio 6.30 requires `huggingface-hub>=1`, which is incompatible with `transformers<5`; gradio 5.50.0 resolves with hub 0.36.2.
  - `kubernetes>=28.1.0,<37`. This is a transitive dependency of chromadb: 37.x requires `pydantic>=2.13.5`, which conflicts with gradio 5's pydantic cap. 36.x has no pydantic requirement, and chromadb's in-memory client does not import kubernetes.
- **RESULT (local):** the install resolved pandas 3.0.6→2.3.3, pillow 13.0.0→11.3.0, pydantic 2.14.1→2.12.3 (all within existing bounds) and kubernetes 37.0.1→36.0.3. `pip check`: no broken requirements. A dry run of `requirements.txt` installs nothing new.
- **Regression RESULT:** the Part 1 local smoke test (S1, S4, S8, S9, S10 PASS) and the Part 2 local smoke test (P2-L0 to P2-L9 PASS) were re-run after the downgrades with unchanged statuses.
- **No LangGraph.**

### D-086 — Mock backends are impossible in real runs — DECIDED (2026-10-17)
- `MockVLM`, `MockGenerator` and `MockClip` can be constructed **only** when `RUN_SMOKE_TEST` is `True` and both `RUN_PIPELINE` and `RUN_EVALUATION` are `False`. `Backends(...)` and `run_request(...)` re-check this. P3-L0 verifies that every mock raises `MockNotAllowed` when either real-run flag is set.
- Mocks include adversarial and malformed outputs: non-JSON, bad intents, trust-upgrade attempts, missing Q&A, out-of-range values, injection echoes, invalid critic outputs, unsafe outputs and generation errors.

### D-087 — RESULT: Part 3 local Mac smoke test (2026-10-17)
- **Execution:** `nbclient`, CPU only, `RUN_SMOKE_TEST = True` set in memory only (the saved notebook keeps default flags and no outputs). Final run completed in 6.4 s with **0 errors, 90 checks, 0 failed**. A default run with all flags `False` produced 0 errors and 6 skip lines.
- **Status:** P3-L0 to P3-L12 all **PASS**. **P3-S0 to P3-S10 SKIPPED_LOCAL** (untested).
- **Key local results (mock backends; these say nothing about model quality):**
  - **L1:** all 12 malformed-state cases rejected; legal transitions deterministic; 4 illegal transitions rejected.
  - **L2:** routes for understand / style / edit / enhance / domain style with and without an image; 4 unsafe kinds flagged; 3 malformed or incomplete cases became clarification.
  - **L3:** observed text is always `untrusted_image_content`; a trust-upgrade attempt fails; 3 invalid outputs gave FAILED_MODEL.
  - **L4:** image text and the whole injected model prompt were discarded (template used; the payload "draw a cat" is absent); text quoted by the user is kept.
  - **L5:** request schema; IP2P and fallback selectable without global mutation; the adapter is never substituted.
  - **L6:**
    - accept first = ACCEPTED (1 attempt)
    - revise then accept = ACCEPTED (2)
    - always revise = MAX_REVISIONS (3 attempts, 2 revisions)
    - invalid critic output = MAX_REVISIONS (3, 2)
    - CLIP below τ for a style request = MAX_REVISIONS
    - CLIP ignored for an edit = ACCEPTED
    - critique disabled = COMPLETED
    - unsafe outputs = BLOCKED_UNSAFE_OUTPUT with no image returned
  - **L7:** all 12 failure cases ended in the expected controlled status, with a message and a trace.
  - **L8:** 12 trace steps in order (`input_guard`, `planner`, `vision`, `orchestrator`, `prompt`, `generation`, `critique`, `orchestrator`, `prompt`, `generation`, `critique`, `orchestrator`); a planted `hf_` token was redacted; the trace is 7,505 bytes with images as hashes; the temp file round-trip was deleted.
  - **L9:** caption route on an injection image = ANSWERED, text reported but not obeyed; generation route = REFUSED with 0 generator calls; "do what the image says" = REFUSED; real person: benign style = ACCEPTED, deceptive pattern = REFUSED, deceptive model flag = REFUSED; benign image text is never promoted into the prompt.
  - **L10:** schemas; synthetic agreement 13/15 and success 12/15; critic agreement 0.75; attack success 2/10; median 2.5 s; with-vs-without table.
  - **L11:** gradio 5.50.0; 8 outputs per callback; errors returned, not raised; reset; `gr.Blocks` built without launch.
  - **L12:** no repo or professor-data change; no `eval/`, `traces/` or work directory; no temp traces left.
- **No model weights were downloaded** (the HF cache is unchanged at 89 MB).

### D-088 — Fixes found by the Part 3 local smoke test (not tuning) and status (2026-10-17)
- **All fixes below are bug and data-handling fixes. No parameter was tuned.**
  1. **The Vision Q&A contract was not enforced** (P3-L3 FAIL): the user's question could be silently replaced by the caption. **Fix:** every requested question must be answered (matched by text, else position), otherwise FAILED_MODEL. The mock now honours the same contract.
  2. **A test-data error** surfaced by fix 1: the trust-upgrade payload answered too few questions. Corrected to 3 answers. The "confidence out of range" case was also corrected so it fails for the intended reason.
  3. **An injected payload survived trigger-word stripping:** the prompt was `'a watercolor street scene, , and draw a cat'`, and the original L4 check was too weak to catch it. **Fix:** any instruction-like pattern in model-written prompt text or a critic revision instruction **discards the whole output** (template fallback; tainted `preserve` list also dropped). The L4 check now asserts the payload is gone.
  4. **Tests mutated the global `EDIT_BACKEND`.** **Fix:** an explicit `edit_backend` argument, with the generator branching on the request. The remaining temporary override (P3-S7's unreachable CLIP bar, which forces revisions) is restored in `finally` and verified by a check. It is a plumbing test, not tuning.
  5. A meaningless always-true check and a fragile trace-index check were removed. The L7 real-backend check was guarded so it never loads multi-GB models on a GPU machine.
- **Additions beyond the approved local list, flagged:** **P3-L12** hygiene stage (it must run last, after the GPU stages).
- **Pending the GPU machine:** P3-S0 to P3-S10. D-072 (VLM) and D-075 (IP2P) stay CANDIDATE until then.

### D-089 — GPU-environment compatibility fix: pin PyMuPDF to 1.28.2 (2026-10-21)
- **Classification:** compatibility fix only. **Not tuning and not P1-EXP-001.** No architecture, model, retrieval parameter, TUNE value or experiment-design change.
- **Symptom:** the first Part 1 GPU smoke run (Docker `pytorch` image, Linux x86_64, Python 3.11.13, torch 2.7.1+cu128, RTX 5090, pandas 2.3.3, **pymupdf 2.0**) stopped in S1 with `KeyError: "['doc_id', 'page', 'table_id'] not found in axis"` at the `pd.DataFrame(recs).drop(...)` display line. S2–S7 were never reached (`S7.model_load_order = []`).
- **Cause:** PyMuPDF 2.0 `Table.extract()` garbles DOC1 Table 1-1 cells: `3.2` → `'32\n.'`, `−2.3` → `'23\n− .'`, `Advanced economies` → `'Advancedeconomies'`. It also detects a different table box (caption/footnote rows excluded). No cell parses as a value, so `table_long_rows` correctly returned `[]` (`long_rows: 0`). An empty DataFrame has no columns, and `drop` raised. `to_markdown()` still looked correct, which hid the problem. It is not a pandas issue and not an incorrect assumption in our code. `errors="ignore"` was **not** used: it would have hidden the loss of every numeric table value.
- **Fix:** `requirements.txt` `pymupdf>=1.24.0` → `pymupdf==1.28.2` (the version validated on the Mac, D-042). No 2.0 feature is needed. No notebook code changed.
- **RESULT (GPU smoke after the fix, nbconvert in the container, saved notebook untouched):** S0 INFO · **S1 PASS** · **S2 PASS** · **S3 PASS** · **S4 PASS** · **S5 PASS** · S6 not run (`SMOKE_VLM_FALLBACK = 'auto'`, S5 passed) · **S7 PASS** · **S8 PASS** · **S9 PASS** · **S10 PASS**.
  - S1: Table 1-1 has 18 long rows (6 forecast, 12 reported) and 2 star markers. Table 1-2: 6 forecast. Table A-2: 27 outturn + 18 forecast. Ground truth parsed (A-1 2.4 / 1.1; B-1 −0.31 / 2.9), the same as D-042.
  - Models (all downloaded during this run, so `load_s` includes the download): `BAAI/bge-large-en-v1.5` (1.3 GB cache), `BAAI/bge-reranker-v2-m3` (2.2 GB), `Qwen/Qwen3-VL-4B-Instruct` (8.3 GB).
  - S2 embedder: load 15.0 s; 640 MB resident, peak allocated 1,339 MB; dim 1024; query encode 7.5 ms GPU vs 420 ms CPU; fp16 GPU vs fp32 CPU cosine 0.99998.
  - S3 reranker: load 23.2 s; 1,083 MB resident, peak 1,163 MB; 24 pairs in 19.2 ms GPU vs 2.09 s CPU; top-1 matches CPU fp32.
  - S5 VLM: load 97.8 s; 8,467 MB resident, peak allocated 8,779 MB (device used 10,766 / 32,607 MB). 5/5 valid JSON; median answer 1.35 s; 32–47 tokens/s; figure description 4.42 s. Text, figure and unanswerable probes correct.
  - S7: load order S2 → S3 → S5, each released before the next (0–8 MB left); max peak allocated 8,779 MB.
- **Note:** S4 low-trust hits unfiltered are 5 with the real embedder (3 with the local hashing substitute). The filtered count is 0 in both.

### D-090 — GPU smoke-harness fixture and reporting fixes for Part 3 (2026-10-21)
- **Classification:** smoke-harness fixture and reporting fixes only. **Not tuning and not P3-EXP-001.** No change to architecture, safety policy, the SD safety checker, model choices, critique thresholds, generation parameters or any TUNE value.
- **First Part 3 GPU smoke run (same container as D-089):** every real model loaded, and every stage passed except P3-S6 and P3-S7. Both ended `REFUSED` in the planner (S6 trace `['input_guard', 'planner']`; S7 0 attempts, 0 revisions). The real SD safety checker had flagged their synthetic **input** fixtures (`synth_image(31)`, `synth_image(32)`; diffusers printed "Potential NSFW content was detected"). Generation and critique were never reached. This was a fixture problem, not a pipeline failure.
- **Fixes (notebook cells `p3-smoke-01` and `p3-smoke-06` only):**
  1. **Fixture:** S6 and S7 now use `synth_image(34)` (`SMOKE_BENIGN_FIXTURE_SEED`, a test input), the colored-ovals image that P3-S10 already ran through the real input safety check.
  2. **Precondition:** `benign_fixture_is_safe`. The fixture is re-checked with the unchanged `generator.safety` before use. If it is flagged, the stage records `fixture_error` and reports status `FIXTURE_ERROR`, never a pipeline FAIL.
  3. **S6:** new check `downstream_path_ran` (planner → vision → prompt → generation in the trace, no critique step).
  4. **S7:** revisions are still forced **only** by the existing mechanism (CLIP bar 101 for this call only, restored in `finally`). New checks:
     - `generation_occurred`
     - `critic_requested_revisions` (3 × REVISE)
     - `revisions_forced_by_clip_bar_not_safety` (every critique `safe=True`)
     - `hard_stop_by_orchestrator` (2 × `revise` + 1 × `revision_limit_reached`)
     - `policy_restored` now compares the whole `CRITIQUE_POLICY` with a deep copy taken before the override.
  5. **`vram_released` reporting:** `run_stage` measured `after − baseline`. A stage that releases models loaded by earlier stages (S2, S5, S9) ends below its baseline, so it reported negative MB (S9: `-12754 MB left allocated`). The reported value is now `max(delta, 0)`, plus "also freed N MB held before the stage". The pass condition is mathematically unchanged, and so is the residency policy.
- **RESULT (targeted GPU rerun):** fresh kernel; all cells except the S0–S5 cell (`p3-smoke-05`). The executed copy is in the container, and the saved notebook's outputs were not updated.
  - P3-L0 … L11 PASS.
  - **P3-S6 PASS:** fixture safe; trace `input_guard, planner, vision, orchestrator, prompt, generation`; COMPLETED; pipeline 7.75 s; co-resident load 12,752 MB, peak allocated 13,371 MB.
  - **P3-S7 PASS:** fixture safe; MAX_REVISIONS after 3 attempts and 2 revisions; CLIP scores 22.665 / 21.396 / 23.067; decisions REVISE ×3; all outputs safe; orchestrator notes `planner_gate, revise, revise, revision_limit_reached`; 15.0 s; policy restored.
  - P3-S8 PASS · P3-S10 PASS.
  - **P3-S9 PASS:** VLM 8,466 MB and SD 2,638 MB resident, each with 0 MB left after release; max peak 13,371 MB; `vram_released: 0 MB left allocated (also freed 12753 MB held before the stage)`.
  - P3-L12 PASS.
- **P3-S0 to P3-S5** were not rerun; they passed in the first GPU run. Their earlier negative `vram_released` figures (S2 −8,467, S5 −2,639) came from the same reporting arithmetic and will print correctly on the next full run.

---

> **Evaluation artifacts frozen (2026-10-21).** The GPU smoke tests for Parts 1, 2 and 3 have passed. Entries D-091 to D-093 record the pre-tuning evaluation artifacts. `eval/` is created now (the exception anticipated in D-002 and D-011). Nothing has been committed.

### D-091 — Part 2 fixed prompt set: `eval/p2_prompts.csv` — FROZEN (2026-10-21)
- **20 prompts:** 10 in-domain, 5 out-of-domain and 5 compositional (D-056). Columns `prompt_id, group, prompt, source_idx`, written with the notebook's own `build_prompt_table` (which rejects wrong group counts).
- **In-domain (P01–P10):** drawn by the notebook's own code on the GPU machine:
  - `load_records` → `clean_records` → `split_train_test` (seed 266) → `draw_in_domain_prompts` (seed 266), executed from the notebook's definition cells.
  - Cleaning kept 822 of 833 rows (11 near-duplicates removed; no other removals). Split: 740 train / 82 test, disjoint.
  - All 10 captions come from TEST rows; `source_idx` is the dataset row index. The draw is deterministic (two draws identical).
  - **Noted, not changed:** the caption of P02 is also the caption of a different training image. The dataset has 736 unique captions among 833 images, and this caption-level overlap is a dataset property. The draw was not repeated, to keep it deterministic and unselected. Test images are not used for training.
- **Out-of-domain (P11–P15):** realistic, non-cartoon scenes (city street, food, landscape, object, coast).
- **Compositional (P16–P20):** attribute binding (colour to object), a count, and spatial relations (on top of, next to, left/right).
- The out-of-domain and compositional prompts are fixed now. **They will not be rewritten based on generated-image quality.** No image has been generated.

### D-092 — Part 1 golden set: `eval/p1_golden_set.csv` — FROZEN (2026-10-21)
- **25 questions in the professor-required distribution:**

  | Category | Count |
  |---|---|
  | Facts and tables | 5 |
  | Figures, including near-identical figures | 6 |
  | Questions needing two sources | 3 |
  | Multi-turn conversations with a user-supplied value | 5 (2 conversations: 2 + 3 turns) |
  | Conflicts and revisions | 3 |
  | Unanswerable / false premise / injection | 3 |

- **Written independently of `Questions.csv`.** It was built only from the three KB PDFs, `kb_manifest.json` and the lab requirements. The assistant that drafted the set never opened `Questions.csv`; its only contact with that file was the automated leakage scan below. IDs are `G01`–`G25`, and conversations are `GCONV-A`, `GCONV-B` and `GSOLO-<id>`. None matches the `[QC]###` pattern (D-006).
- **Behaviours covered:**
  - text, table and exact-figure retrieval;
  - DOC1 vector figures and DOC2/DOC3 raster figures;
  - near-identical pairs: vintage A-2/A-3, base date A-4/A-5, year A-6/A-7, comparison series B-3/B-4, sample B-1/B-2, and the B-5 erratum;
  - forecast vs outturn; the explicit revision; a high/medium cross-document conflict (`conflict`, higher trust preferred);
  - `not_found`, including an entity that the KB mentions but gives no value for;
  - `false_premise` built on a low-trust claim; the Appendix C prompt injection;
  - session overrides (`session_override`), and a follow-up turn checking that the override did not change the base KB.
  - Refused permanent KB edits are **not** included, because their expected status is still OPEN (D-030, D-035).
- **Schema** (lists comma-separated, no spaces; `NONE` when empty; the same conventions as the submission):
  - identity: `golden_id, category, conversation_id, turn, question`
  - answer: `expected_answer, answer_type (numeric | text | status_only), expected_value, also_acceptable_values, value_unit, answer_keywords, expected_status, expected_figure_references`
  - evidence: `expected_citations, also_acceptable_citations, gold_evidence` (gold_evidence is the relevance set for Recall@5)
  - negative cases: `forbidden_citations` (always includes the Appendix C page and Figure C-1), `distractor_values` (values that must not be given as the answer)
  - bookkeeping: `behaviours`, `source_check` (the verifiable source of each value)
  - Correctness uses `expected_value` ±1% (`ANSWER_NUMERIC_TOLERANCE`) or `answer_keywords`, plus `expected_status`. Citation accuracy compares against `expected_citations` ∪ `also_acceptable_citations`. Groundedness is rated by humans against the cited evidence.
- **Verification (RESULT, automated against the PDFs with PyMuPDF 1.28.2, 485 checks, all PASS):**
  - exactly 25 rows; exact category counts; unique IDs and questions; two multi-turn conversations with consecutive turns;
  - every status in `ALLOWED_STATUS`; citations and labels match the notebook's `CITATION_PATTERN` / `LABEL_PATTERN`;
  - every cited label is captioned on a page that is also cited; `figure_references` ⊆ cited labels;
  - every `source_check` text is present on its stated page;
  - no low-trust page or figure appears in any expected, acceptable or gold-evidence citation; every answer is ≤ 120 words.
  - The six chart values that exist only as printed data labels (A-2, A-5, A-6/A-7, B-4, B-2, B-5 / B-5 corrected) were read from the rendered pages.
- **Leakage check (RESULT):** an automated scan compared the golden questions with `Questions.csv`. It printed only similarity scores and counts, never question text.
  - The first draft had **4 questions word-for-word identical to hidden-set questions and 4 more with similarity ≥ 0.70**. These were coincidental short phrasings of the KB's built-in test facts.
  - All 8 were rewritten before freezing, 6 with a different target fact, keeping every required behaviour covered. The rewrite was driven only by the leakage scan, not by any system output.
  - **Final:** maximum similarity 0.62, 0 exact matches, 0 shared word 8-grams. No `Questions.csv` ID or `[QC]###` pattern in any repository text file.
  - The P2 and P3 notebooks contain one `C###`-shaped substring each, inside base64 image data in saved outputs. Neither is a `Questions.csv` ID; flagged for clearing outputs before the first commit.

### D-093 — Status: artifacts frozen before any tuning; nothing committed yet (2026-10-21)
- `eval/p1_golden_set.csv` and `eval/p2_prompts.csv` were **created before any tuning or training experiment**. No golden-set question has been answered by the system, no P2 prompt has been generated, and no evaluation result exists.
- **No evaluation result has been used to tune anything.** No TUNE value has changed since D-066, apart from the GPU compatibility and harness fixes recorded in D-089 and D-090, which are not tuning.
- Both files are **not yet committed**. D-045 requires them to be in the first Git commit, before P1-EXP-001 or P2-EXP-001 starts.
- P1-EXP-001, the P1 baseline/final runs and P2 training have **not** started.

---

> **Part 1 implementation before frozen evaluation (2026-10-21).** Entries D-094 to D-099 record the implementation of the complete Part 1 pipeline in `notebooks/p1_rag.ipynb` (the D-013 to D-035 architecture). They are implementation choices and pre-experiment checks, **not P1-EXP-001**. During this work `eval/p1_golden_set.csv` and `Questions.csv` were never opened: the notebook reads them only behind `RUN_EVAL` / `RUN_SUBMISSION` (both `False`), and a file-access audit hook confirms it (D-099). The harness uses only the golden-set column names and category counts already recorded in D-092. No TUNE value was changed.

### D-094 — Ingestion, indexing and the supersession registry: implementation choices (2026-10-21)
- **Objects.** Every captioned label becomes one object (`DOC#:<label>`), located with the D-017/D-042 helpers. Text blocks lying ≥ `OBJECT_BLOCK_OVERLAP = 0.6` inside an object's region belong to that object (caption, title, axis labels, rows, source lines), not to the text chunks. DOC1 margin captions take their title from the block stacked under the label. Figure crops are rendered at `RENDER_DPI`; low-trust figures are never rendered for the VLM.
- **Notices.** Text blocks matching `NOTICE_PATTERN` (`revision notice | correction to | erratum` at the block start) are atomic `notice` objects (D-019). Result: the DOC2 p3 revision notice and the DOC3 p6 erratum.
- **Text chunks (D-019).** Running headers/footers are dropped: the same text, digits ignored, in the top/bottom `MARGIN_BAND_FRAC = 0.08` of ≥ `RUNNING_TEXT_MIN_PAGES = 3` pages. A block ≥ `HEADING_MIN_FONT_PT = 12.5` pt with ≤ 14 words is a section heading; chunks never cross a page or a heading. Paragraph-aware packing to ~220 words (max 350), with a 40-word overlap only when the result stays ≤ 350. DOC1 line-break hyphens are removed. Prefix `[doc | p# | section]`.
- **Table representation (resolves D-043 OPEN).** One line per normalised value, `row | column: value [kind]`, from the cleaned `table_long_rows` records, plus caption, units and source/footnote lines. PyMuPDF markdown is not used. If a table yields no records, a cleaned pipe grid is the fallback (not needed for any KB table). This is the simplest deterministic format that keeps the forecast/outturn kind of every value explicit.
- **Index texts (D-026).** Dense text: prefix, caption, notes, up to `REFERENCING_SENTENCES_MAX = 3` sentences from evidence-eligible text that name the label, text printed inside the figure, and the VLM description. BM25 and reranker text add every table value. Figures get a structured JSON chart description from the answer VLM (`MAX_NEW_TOKENS_DESCRIBE`); low-trust figures are never described.
- **Label mentions** in free text (`Fig. A3`, `figures A-6 and A-7`, `Tables 1-2, 1-3 and 1-4`, `Figure B-5 (corrected)`) are parsed by one function and resolved **only** against the caption inventory (D-043 router safety).
- **Registry (implements D-029, built at ingestion, structure only):**
  1. `X (corrected)` supersedes `X`.
  2. A notice links to every inventory object it names; a "revised from A … to B" notice marks the linked table record whose year, old value, measure and subject all appear in the notice.
  3. Series key `(subject, measure, year)`: subject = row entity, else a known entity named in the caption/header (`SUBJECT_ALIASES = {"u.s.": "united states"}`); measure = variable without units and the word "rate".
  4. Relations between objects: `outturn_supersedes_forecast`; `sources_disagree` (non-forecast values from different documents, different values, no revision).
  - Result from the KB: 1 revision (DOC1 Table 1-2 output growth 2010, 3.0 → 2.4 by the DOC2 notice), 24 outturn-supersedes-forecast relations, 1 cross-document disagreement (DOC1 Table 1-2 vs DOC3 Table B-2, U.S. unemployment 2010), and the B-5 erratum link.
- **Index.** 195 objects (157 text chunks, 26 figures + Figure C-1, 9 tables, 2 notices); 192 evidence-eligible. Chroma collection `p1_kb` (cosine, our embeddings; Chroma requires names of ≥ 3 characters). Low-trust objects stay indexed with `evidence_ok = False`. Index fingerprint taken after ingestion and asserted unchanged at the end.
- **Notebook utilities.** Stage timers, GPU memory reports and a `sys.addaudithook` file-access audit recording any open of `Questions.csv` or `p1_golden_set.csv`.
- **Flags:** `RUN_SELF_CHECKS = True`, `RUN_SUBMISSION = False`, `RUN_EVAL = False`, `EVAL_MODES = ("baseline", "final")`; `RUN_SMOKE_TEST` restored to its D-036 default `False`. Helpers shared with the smoke appendix (`bm25_tokenize`, `chroma_records`, `parse_json_object`, `fit_pixels`, `load_vlm`, `numbers_in`, `within_tol`) moved into the pipeline sections, so nothing is defined twice; the appendix releases the pipeline models before loading its own (D-037).

### D-095 — Retrieval and model residency: implementation choices (2026-10-21)
- **Baseline (D-015):** dense top-20 with the `evidence_ok` filter; context = first `RERANK_KEEP = 8` (same context budget as final). No router, BM25, RRF, reranker, registry expansion or registry notes. Table value lines keep their `[kind]` tags in both modes (they are the table representation, not retrieval logic).
- **Final:** router pins named labels (+ their superseding objects); unknown labels and named low-trust labels are reported, never pinned. Dense top-20 + BM25 top-20, plus a document-restricted dense list when the query names a document (patterns built from the manifest: `doc N`, title lead such as "Supplement A", publisher), fused by RRF k = 60; the fused top 24 (+ same-page text of pinned objects) are reranked by `bge-reranker-v2-m3` (max length 512); context = pinned + top 8; then registry expansion adds at most `EXPANSION_MAX = 3` (TUNE) superseding objects, linked notices and cross-document counterparts (restricted to the query's years when it names any).
- **Figure exclusion (refines D-027):** other figures are removed only when a **figure** is named. Naming only a table keeps figures, because a question may combine a named table with a figure (sample submission format).
- **Recall@5 list:** pinned + reranked (final) or dense ranking (baseline); registry additions are not ranked.
- **Residency (refines D-025/D-037):** models are loaded sequentially (VLM → embedder → reranker), each measured, and then stay co-resident on `cuda:0` for query time, because together they fit the 16 GB rubric budget: RESULT peak allocated 11,919 MB ≤ `VRAM_BUDGET_MB = 14,336` (D-099). `EMBED_DEVICE` / `RERANK_DEVICE` may be set to `"cpu"` if a smaller GPU needs it. The fallback VLM is loaded only if the primary fails to load.

### D-096 — Grounded generation and validation: implementation choices (2026-10-21)
- **Prompt.** A system prompt that inserts the manifest's precedence rules verbatim (read from `kb_manifest.json`, not typed), defines the five statuses, the supersession/near-identical-figure/citation rules, the 120-word limit and the JSON schema. Wording is general; no KB fact or question appears in it.
- **Evidence blocks:** `<<E# | cite as: … | doc p# | type label | trust | document data vintage>>` … `<<END E#>>`; final mode appends the registry notes for the block's values. At most `MAX_FIGURE_IMAGES = 2` figure images (TUNE, D-026), listed by label. Conversation history, user-supplied values and system notes are separate, labelled sections.
- **Deterministic post-processing (implements D-029, D-032):**
  - citations normalised and kept only if shown on an evidence-eligible block (low-trust never);
  - figure references kept only if in the context, and synced with label citations both ways;
  - a superseded object is never cited without its superseding object when that was shown;
  - forced statuses from conversation rules;
  - `session_override` without a user value → `answered`;
  - `not_found` clears the lists, and a bare status word as the answer becomes a standard sentence;
  - answered / conflict / false_premise need ≥ 1 valid citation; ≤ 120 words; pydantic schema.
- **Content rules (added after synthetic self-checks, D-099):** a `conflict` answer must state ≥ 2 distinct non-year values; the turn that introduces a user value must state that value **and** a value found in the cited evidence. These are assignment rules ("return both values"; "report what the documents say"), not question-specific. They trigger the repair retry; if only they remain after it, the answer is accepted and the issue recorded.
- **Failure path:** one repair retry with the rejection reasons; then, if only the length is wrong, deterministic truncation; otherwise the deterministic `not_found` fallback.

### D-097 — Conversation handling: implementation choices (2026-10-21)
- One `ConversationState` per `conversation_id`, created on the first turn and discarded (turns, values, refusals cleared) after the conversation's last turn.
- Follow-ups (any turn after the first) are rewritten into a standalone retrieval query by the VLM (`MAX_NEW_TOKENS_REWRITE = 64`) from that conversation's last `HISTORY_TURNS = 3` turns only; the generator sees the original question, the standalone form and the same history.
- **User-supplied value:** detected when the turn contains a decimal or percentage (labels and years excluded) **and** an assumption cue (`OVERRIDE_CUE_PATTERN`) or a KB-edit request. The VLM extracts entity/variable/year/value/unit (`MAX_NEW_TOKENS_OVERRIDE = 96`); the regex value is the fallback. The value lives only in the conversation state and gives `session_override`.
- **Permanent KB edits:** detected by `KB_EDIT_PATTERN`, recorded as refused, answered with the read-only explanation; status `REFUSED_KB_EDIT_STATUS = "session_override"` (still OPEN, D-030/D-035).
- The submission path (`RUN_SUBMISSION`) reads the hidden-set question text from a `question` column, else the first non-ID column: the column name of `Questions.csv` is **not verified** (the file is not opened), so it stays OPEN until the first submission run.

### D-098 — Evaluation metric definitions, fixed before any golden-set run (2026-10-21)
- **Correct:** predicted status = `expected_status` **and**: numeric → a number in the answer within ±1% of `expected_value` or of an `also_acceptable_values` entry; text → every comma-separated `answer_keywords` entry appears (case-insensitive, `a|b` = either); status_only → status only.
- **Recall@5:** per question, the share of `gold_evidence` units (`DOC#:<label>` or `DOC#:p#`) covered by the top-5 ranked objects (an object covers its label citation and its page); mean over questions with gold evidence. Hit@5 is reported too.
- **Citation correct:** no `forbidden_citations`; expected `NONE` → no citations; otherwise ≥ 1 citation and all ⊆ `expected_citations` ∪ `also_acceptable_citations`. Citation accuracy = mean.
- **Seconds:** wall time of the whole turn (rewrite + retrieval + generation); the median is reported.
- **Diagnostics only:** figure-reference F1, `distractor_mentioned`. **Groundedness:** MANUAL, pending team rating; never computed.
- `RUN_EVAL` requires a `P1-EXP-###` experiment ID and asserts the D-092 schema (25 rows, category counts) before running both modes on the same ingestion.

### D-099 — RESULT: pre-experiment self-checks and Restart & Run All (2026-10-21) — not an experiment
- **Probes used:** smoke-test fixtures (D-036), inventory labels and caption titles, the low-trust objects' own text, and fictional "Testland" evidence. Ground truth is read from the parsed tables. No golden-set row and no `Questions.csv` row.
- **Development iterations on these probes (not tuning):**
  1. Subjects followed by punctuation were not matched, so DOC1 Tables 1-2…1-4 had no subject → word-boundary match (relations went from 6 to 24 + 1 disagreement).
  2. Chroma collection name too short → `p1_kb`.
  3. Synthetic conflict answer gave one value, and the synthetic session-override turn omitted the document value → the D-096 content rules; the first version counted the "1" of "pp per 1% growth" as a document value, so the document value must now come from the cited evidence.
  4. A self-check expectation error (G6) corrected.
- **RESULT (nbconvert Restart & Run All in the GPU container, outputs saved in the notebook):** exit 0, 0 error outputs, total runtime 269.6 s (figure descriptions 203.4 s for 26 figures).
  - **43/43 GATE checks PASS:** ingestion inventory, low-trust never in any context (both modes) and its citations dropped, router pins all 35 evidence labels first with no other figure, alias and unknown labels, every table in the final top-5 from its caption title (baseline 9/9 too), revision/outturn/disagreement registry and expansion, repair/fallback/length/status/content rules, the five fictional cases (revision, conflict, not_found, false_premise, embedded instruction), two synthetic conversations (override isolated, document value reported, KB edit refused, follow-up rewritten from its own history, index unchanged, state discarded), and the harness in both modes on a 5-item synthetic fixture.
  - Peak allocated VRAM 11,919 MB (max device used 14,382 MB, including ~1,680 MB held by other processes before the run).
  - Index fingerprint unchanged; `files_opened = []`, `questions_csv_opened = False`, `golden_set_opened = False`.
  - The synthetic-fixture numbers (baseline 5/5, final 5/5) are plumbing checks, **not** P1 results.
- **Remaining OPEN before or at P1-EXP-001:** D-030/D-035 refused-edit status; `Questions.csv` text-column name (D-097); exact `requirements.txt` pins from this environment (D-040: transformers 4.57.6, sentence-transformers 5.7.0, chromadb 1.5.9, accelerate 1.15.0, pymupdf 1.28.2, rank-bm25 0.2.2, pydantic 2.12.3, torch 2.7.1+cu128); the Kaggle commit hash (D-007); Kaggle internet access (D-035).
