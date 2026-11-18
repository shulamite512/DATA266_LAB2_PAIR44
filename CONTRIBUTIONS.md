# Contributions — Pair Programming Team 44

| Member | GitHub |
|---|---|
| Parth Patel | [@Parthp28](https://github.com/Parthp28) |
| Chelsi Shulamite | [@shulamite512](https://github.com/shulamite512) |

Each member built a complete, independent implementation of all three parts. Authorship is verifiable in Git: Parth's history (commits by Parth Patel) and Chelsi's history (commits by shulamite512) are both preserved in this repository. The team then selected one implementation per part.

## Implementations

| Part | Parth's implementation (lead: Parth) | Chelsi's implementation (lead: Chelsi) | Selected |
|---|---|---|---|
| 1. Multimodal RAG | Ingestion, trust handling, revision/conflict registry, hybrid retrieval and reranking, answer validation, conversation memory, golden set, P1-EXP-001…003 and the final Kaggle run P1-KAGGLE-V14-R1 | Ingestion with figure/table crops, Chroma + BM25 retrieval, answering, conversation memory, golden set, `p1_eval` evaluation, Kaggle submissions | **Parth** |
| 2. LoRA fine-tuning | Pokémon dataset, LoRA rank 4 / rank 64 (P2-EXP-001), KID/CLIP/LPIPS, memorization, safety analysis, 3-rater blinded evaluation | Naruto dataset, LoRA rank 8 / rank 32, KID/CLIP/LPIPS, memorization, 2-rater blinded evaluation, Hugging Face publication | **Chelsi** |
| 3. Five-agent system | Typed state, five agents, orchestrator, guardrails, frozen scenarios and red-team set, P3-EXP-001…003, traces, Gradio demo, evaluation tooling | Five agents, orchestrator, Gradio app, scenario and red-team runs, critic labels and human judgements | **Parth** |

## Evaluation work (as recorded in the evaluation files)
- **Part 2 (selected, Chelsi):** blinded pair ratings by the raters recorded as `chelsi` and `parth` (`eval/p2_human_ratings.csv`).
- **Part 3 (selected, Parth):**
  - Task-success judgements by one team member, recorded as `member_a` (`eval/p3_member_a_judgements_P3-EXP-003.csv`).
  - A disclosed AI evaluator as the second evaluator; see `AI_USAGE.md`.
- **Alternatives:**
  - Parth's Part 2: 3 raters, recorded as `RATER_1` to `RATER_3`.
  - Chelsi's Part 1 groundedness and Part 3 judgements: 2 raters, recorded as `rater_A` and `rater_B`.

  The files do not record which person each anonymous rater ID belongs to.

## Shared work
- Choosing the final implementation for each part (team decision).
- Combining both repositories into this one, done by Parth with an AI assistant. It preserves both histories.

## Not recorded
- Per-subtask partner roles beyond the authorship above.
- The IEEE report authorship split.
- Meeting recordings: none have been provided.
