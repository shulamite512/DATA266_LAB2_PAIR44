# AI usage — Pair Programming Team 44

| Tool | Model | Used by | Parts |
|---|---|---|---|
| Claude Code (VS Code extension) | Claude Opus 5.5 (`claude-opus-5-5`) | Parth Patel, Chelsi Shulamite | 1, 2, 3 |

No hosted AI API was used in any submitted run. Chelsi's Part 1 code has optional `gemini` and `claude` backends, which were explored during development but not used for submitted results.

## Chelsi's implementation (selected Part 2; alternative Parts 1 and 3)
- **Code:** the assistant wrote the code in `src/` (Part 1 ingestion, retrieval, answering and evaluation; Part 2 data preparation, LoRA training, generation and evaluation; Part 3 agents, orchestrator and Gradio app), the notebook generators in `tools/`, the dependency installer and the upload-zip builder.
- **Evaluation templates:** it drafted the Part 3 scenarios, the red-team cases and the empty rating sheets.
- **Debugging:** it fixed installation, ChromaDB naming, a shadowed variable, the Hugging Face upload, the red-team counting bug and the human-agreement calculation.
- **Golden set:** it checked the golden-set answers against the PDFs and flagged two rows (G03, G20). The team decided how to change them.
- **Results and documentation:** it wrote the code behind `notebooks/evaluation/chelsi_human_eval_results.ipynb`, extracted result tables, ran Git commands, and drafted the README and model card.
- **Done by the team:** ran every notebook on Colab/Kaggle GPUs; chose the final backend and the final Part 2 run; wrote the golden set; did all human ratings; wrote the Part 2 dataset description.

## Parth's implementation (selected Parts 1 and 3; alternative Part 2)
- **Design:** the assistant proposed architecture options that the team corrected and approved. They are logged as decisions in `docs/DECISIONS.md` and `docs/part1/DECISIONS_P1.md`.
- **Implementation:** it wrote and debugged the notebooks, the Docker environment, the evaluation freezes, the rating tools and the documentation. It validated them statically before each experiment.
- **Execution:** with the team's explicit authorization, it executed P3-EXP-003 (headless, in the team's Docker container) and the Part 2 `REPORT_ONLY` scoring. The team ran the Part 1 Kaggle notebook and the Part 2 training.
- **Release:** it prepared the release commits and tags, and combined both repositories into this one.

The complete dated log is in `docs/AI_USAGE_LOG_parth.md`.

## AI used as an evaluator (Part 3, Parth's P3-EXP-003)
Claude Opus 5.5 served as the **second, supplemental task-success evaluator** for Parth's Part 3. It is not a team member, and its judgements are not human judgements.
- **Method:**
  - It judged the 52 items of the blinded packet (30 scenarios, 20 critic attempts, 2 red-team cases) with the frozen rubrics.
  - It inspected every image itself.
  - It recorded and hashed its judgements before it saw the human answers or the answer key.
- **Files:** `eval/p3_ai_judge_P3-EXP-003_*` with `_PROVENANCE.md`; the comparison is in `eval/p3_ai_vs_human_P3-EXP-003_REPORT.md`.
- **Result:** agreement with the human evaluator was 20/30 scenarios (κ = 0.40), and 18 disagreements are unresolved.
- **Compliance note:** the written lab requirement asks for judgements by both team members. The team reports that the instructor allowed AI judging verbally; this is not confirmed in writing.

## What the team did
- Ran the experiments.
- Supplied and approved all human ratings and judgements.
- Made the selection decisions.
- Reviewed every result reported here.
