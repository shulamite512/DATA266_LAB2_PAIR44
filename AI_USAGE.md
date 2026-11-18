# AI usage

| Tool | Model / version | Parts |
|---|---|---|
| Claude Code (VS Code extension) | Claude Opus 5.5 (`claude-opus-5-5`) | 1, 2, 3 |

## What the AI assistant was used for
* **Code:** wrote the code in `src/` for all three parts (Part 1 ingestion, retrieval, answering and evaluation;
  Part 2 data preparation, LoRA training, generation and evaluation; Part 3 agents, orchestrator and Gradio app),
  the notebook generators in `tools/`, the dependency installer and the upload-zip builder.
* **Evaluation templates:** drafted the Part 3 scenarios and red-team cases (`eval/p3_scenarios.json`,
  `eval/p3_redteam.json`) and the empty rating sheets.
* **Debugging:** diagnosed and fixed errors we hit on Colab/Kaggle (package installs, ChromaDB naming, a shadowed
  variable in Part 2, Hugging Face upload, the red-team counting bug, the human-agreement calculation).
* **Checking our golden set:** compared each of our 25 golden-set answers with the PDFs and pointed out two rows that
  conflicted with the documents' own rules (G03, G20); we chose how to change them.
* **Analysis code:** wrote the code that computes the human-evaluation numbers from our rating files
  (`notebooks/Chelsi/human_eval_results.ipynb`, built by `tools/build_human_eval_notebook.py`) and extracted result
  tables from notebook outputs into `part1/`-`part3/`.
* **Repository and documentation:** organized the repository, ran the git commands (commits, tags, pushes), and
  drafted `README.md` and the Hugging Face model card.

## What we did ourselves
* Ran every notebook on Colab/Kaggle GPUs and chose the final Part 1 backend and the final Part 2 run.
* Wrote the 25 golden-set questions and answers (Part 1).
* All human ratings: Part 1 groundedness, Part 2 blinded pair comparisons, Part 3 scenario judgements and critic
  labels, including resolving our disagreements.
* Wrote the Part 2 dataset description.
* Wrote the report and all analysis in our own words. Every number in the report comes from an executed notebook output.

_(Both members: check and correct this list before submitting.)_
