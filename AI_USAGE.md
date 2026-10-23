# AI Usage Declaration

This file lists every AI coding assistant used in this project and what it was used for.

## Claude Code (Anthropic)

- **Interface:** Claude Code VS Code extension
- **Model:** Claude Opus 5.5 (`claude-opus-5-5`)
- **Used by:** `[MEMBER NAME — TO BE FILLED]`
- **Used for (cumulative; append as usage grows):**
  - 2026-10-17: inspected the lab requirements and provided files, and summarised the Part 1 requirements.
  - 2026-10-17: created the repository skeleton (`README.md`, `DECISIONS.md`, `CONTRIBUTIONS.md`, `AI_USAGE.md`, `.gitignore`, and the `notebooks/p1_rag.ipynb` skeleton) under the team's direction.
  - 2026-10-17: Part 1 architecture design and review: proposed options, which the team corrected and approved (DECISIONS.md D-013 to D-035).
  - 2026-10-17: implemented and refined the gated pre-experiment smoke-test harness in `p1_rag.ipynb`, plus the helper functions it validates (caption/figure/table extraction, table normalization, `ConversationState`, index fingerprint).
  - 2026-10-17: ran it locally on a Mac (CPU only) and debugged the PDF, figure and table extraction checks against the provided documents.
  - 2026-10-17: validated the answer schema, citation/label grammar (against `validate_submission.py`), conversation isolation and index immutability through the local smoke test.
  - 2026-10-17: maintained `DECISIONS.md` from the measured local smoke-test results (D-041 to D-044).
  - **Not done yet:** GPU-dependent smoke stages (embedder, reranker, VLM, GPU memory) are untested; no full RAG pipeline exists; no P1-EXP-001 run has occurred.
  - 2026-10-17: Part 2 architecture design: proposed options, which the team corrected and approved; verified the dataset cards, leading to the Pokémon dataset decision (DECISIONS.md D-045 to D-064).
  - 2026-10-17: implemented the gated smoke-test harness in `notebooks/p2_finetune.ipynb` (local P2-L\* stages and the prepared GPU P2-S\* stages), plus the helper functions it validates.
  - 2026-10-17: ran local tests of dataset cleaning and deduplication, the split, 512×512 preprocessing, tokenization, and LoRA plumbing on a tiny randomly initialised UNet (no pretrained diffusion weights).
  - 2026-10-17: debugged the Hugging Face dataset-column handling issue (a parquet physical-column index mismatch in the caption-size check).
  - 2026-10-17: maintained `DECISIONS.md` for Part 2 from the measured local results.
  - **Part 2 not done yet:** no real diffusion training has occurred; no GPU Part 2 stage (P2-S0 to P2-S7) has run; P2-EXP-001 has not occurred.
  - 2026-10-17: Part 3 architecture design: proposed options, which the team corrected and approved (DECISIONS.md D-068 to D-088).
  - 2026-10-17: implemented `notebooks/p3_agents.ipynb`: typed state and state machine, the five agents, orchestrator, JSON traces, Gradio app, evaluation helpers, the local P3-L\* smoke stages, and the prepared GPU P3-S\* stages.
  - 2026-10-17: ran the local smoke test with mock backends (no VLM or diffusion weights) and debugged what it found: the vision Q&A contract was not enforced; an injected payload survived trigger-word stripping; tests mutated a global config value; a test-data error. Also resolved the gradio / huggingface-hub / kubernetes / pydantic dependency conflict.
  - **Part 3 not done yet:** no real agent model (VLM, SD 1.5, instruct-pix2pix, CLIP) has been run; no GPU Part 3 stage (P3-S0 to P3-S10) has run; P3-EXP-001 has not occurred.
  - 2026-10-21: on the GPU machine, diagnosed and fixed GPU-environment issues found by the smoke tests: pinned PyMuPDF to 1.28.2 after a 2.0 table-extraction regression (D-089); replaced the Part 3 S6/S7 smoke fixtures and fixed the `vram_released` reporting arithmetic (D-090). Neither is tuning.
  - 2026-10-21: helped prepare the pre-tuning evaluation artifacts (D-091, D-092):
    - drew the 10 in-domain Part 2 prompts with the notebook's own seed-266 split and draw code, and drafted the 5 out-of-domain and 5 compositional prompts (`eval/p2_prompts.csv`);
    - drafted the 25-question Part 1 golden set (`eval/p1_golden_set.csv`) from the three knowledge-base PDFs and the manifest, in the professor's category distribution supplied by the team;
    - verified every answer, status and citation against the PDFs with an automated script and by reading the rendered charts;
    - ran an automated leakage scan against `Questions.csv` that printed only similarity scores and counts, and rewrote the 8 golden questions it flagged. `Questions.csv` itself was not read.
  - **Evaluation not done yet:** no golden-set question has been answered by the system, no Part 2 image has been generated, and nothing has been tuned or committed.
  - 2026-10-21: implemented the complete Part 1 pipeline in `notebooks/p1_rag.ipynb` from the team-approved architecture (DECISIONS.md D-094 to D-099):
    - ingestion: objects, notices, page-bounded chunks, table value lines, VLM figure descriptions, ChromaDB and BM25;
    - the supersession/conflict registry;
    - baseline and final retrieval (router, RRF, reranker, registry expansion);
    - prompt, evidence packaging, JSON validation and repair;
    - conversation handling;
    - the gated submission path, the evaluation harness, and pre-experiment self-checks.
  - 2026-10-21: debugged it on the GPU machine using only synthetic and source-derived probes, and ran Restart & Run All (43/43 self-checks).
    - `eval/p1_golden_set.csv` and `Questions.csv` were not opened; a file-access audit in the notebook records this.
    - No golden-set evaluation and no tuning has been done; P1-EXP-001 has not started.
  - 2026-10-21: fixed the data-path detection after the first P1-EXP-001 attempt (D-100) and ran P1-EXP-001 at the team's request.
  - 2026-10-21: analysed the P1-EXP-001 failures against the golden set (D-101, a team-approved change to the golden-set policy). Implemented the D-102 generation and conversation fixes and validated them with isolated unit tests on fictional evidence. The notebook was not run, and P1-EXP-002 is prepared for the team to start manually.
  - 2026-10-22: removed the Part 1 smoke-test appendix and its smoke-only configuration from `p1_rag.ipynb` after GPU compatibility testing was complete (D-103). Production code was not changed. Checks were static only (JSON validity, compilation, name resolution, leakage scan with counts only). The notebook was not run.
  - 2026-10-22: recorded P1-EXP-002 and its Kaggle checkpoint, analysed general failure patterns (EXP-001 per-question outputs and the shape of our own EXP-002 `submission.csv`; `Questions.csv` was not opened), and implemented the D-104 post-processing and prompt fixes for P1-EXP-003. They were validated with isolated CPU unit tests on fictional evidence with stubbed retrieval and VLM (32/32) and static checks. The notebook was not run; P1-EXP-003 is prepared for the team to start manually.
  - 2026-10-23: recorded the P1-EXP-003 checkpoint from the team's results and the saved notebook, and identified from the saved outputs that the second run in the same kernel had loaded the models twice. Implemented the D-105 one-run workflow, status-logic consolidation, registry-based conflict/supersession rules and retry reductions for P1-EXP-004, and updated the README workflow. Validation was static checks and CPU-only unit tests with the GPU hidden from the process (36/36). No notebook, model or GPU work was run, and no kernel or process was touched; P1-EXP-004 is prepared for the team to start manually.

All design decisions were reviewed and approved by the team before implementation. They are logged in `DECISIONS.md`.

## Other AI tools

`[None so far — add any other assistant here with what it was used for]`
