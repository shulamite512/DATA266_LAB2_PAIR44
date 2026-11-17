# Submission checklist — DATA 266 Lab 2 (status 2026-11-17)

**Source of requirements.** The official documents (`DATA266_Lab2_Requirements.pdf`, `DATA266_Fall2026_Lab_2.pdf`, kickoff slides) are **not on this machine**. The items below come from the requirements the team recorded in `DECISIONS.md` (e.g. D-001, D-007, D-011, D-039, D-105). Rows marked *assumption* must be checked against the PDF before submitting.

Status legend: **COMPLETE** · **PENDING HUMAN INPUT** · **PENDING PUBLICATION** (needs your authorization) · **BLOCKED** · **NOT VERIFIED**

## 1. Readiness

| Item | Status | Evidence / what is missing |
|---|---|---|
| **Part 1** RAG notebook + Kaggle submission | **BLOCKED** | `notebooks/p1_rag.ipynb` has design + extraction helpers only; retrieval/answering/`submission.csv` were never implemented. No Part 1 work exists elsewhere on this machine. |
| P2 models (base, LoRA A r4, LoRA B r64) trained and compared | COMPLETE | P2-EXP-001; `notebooks/p2_finetune.ipynb` (executed, committed `b035d2a`) |
| P2 120 images, KID/CLIP/LPIPS/memorization/safety | COMPLETE | `$WORK/p2/results/P2-EXP-001/` |
| P2 frozen prompts/split committed before training | COMPLETE | `eval/p2_*` (commit `4150da8`) |
| P2 human evaluation (≥ 3 raters, 25 pairs) | **PENDING HUMAN INPUT** | `HUMAN_EVALUATION.md` § Part 2 |
| P2 adapter + images on Hugging Face | **PENDING PUBLICATION** | § 3 below |
| P3 five agents, shared state, ≤ 2 revisions, JSON traces | COMPLETE | `notebooks/p3_agents.ipynb`; `traces/P3-EXP-00{1,2,3}/` |
| P3 15 scenarios × critique on/off + 10 red-team, executed | COMPLETE | P3-EXP-003: 40/40 executed (6 `FAILED_MODEL`: confirmed repetition loop, reported as a limitation) |
| P3 critique comparison, latency, revisions (automated) | COMPLETE | `$WORK/p3/experiments/P3-EXP-003/evaluation_summary.json`, `report/` |
| P3 human judgements (2 judges) + red-team R01/R02 review | **PENDING HUMAN INPUT** | `HUMAN_EVALUATION.md` § Part 3 |
| P3 evaluation inputs on Hugging Face (*"must be available on Hugging Face"*, D-105) | **PENDING PUBLICATION** | § 3 below |
| P3 Gradio demo | COMPLETE (local) | launched and tested 2026-11-17 (DECISIONS P3-EXP-003 — RESULT); screenshots/video **PENDING HUMAN INPUT** if required |
| Notebook cell 1 = professor's run-information cell, verbatim | COMPLETE | all three notebooks (D-007) |
| Required notebook outputs saved | COMPLETE for P2/P3 | executed notebooks committed (`b035d2a`, `13495ce`) |
| 16 GB GPU compatibility | **NOT VERIFIED** | only an allocator cap on an RTX 5090 (peaks: P2 6.5 GB, P3 12.5 GB); no T4/P100 run |
| `README.md` | COMPLETE (team name missing) | team number placeholder |
| `DECISIONS.md` | COMPLETE | through D-116 |
| `AI_USAGE.md` | COMPLETE | updated through this preparation |
| `CONTRIBUTIONS.md` | **PENDING HUMAN INPUT** | template only; names, handles, task owners, recordings |
| `links.txt` | **PENDING HUMAN INPUT / PUBLICATION** | every link currently `MISSING` |
| IEEE report | **PENDING HUMAN INPUT** | `report/data266_lab2_report.tex` (Parts 2–3 draft; `\pending{}` / `\missing{}` markers) |
| Private GitHub repo `data266-lab2-team##`, instructor access | **PENDING PUBLICATION** | no remote configured; nothing pushed |
| Version tags | **NOT VERIFIED** (*assumption*) | DECISIONS D-007 mentions a `p1-v1.0` commit; check the PDF for required tag names |
| Canvas ZIP | **NOT VERIFIED** (*assumption*) | D-011 (`links.txt` for the Canvas ZIP) and D-039 (ZIP of the repository working files); check the PDF |

## 2. Report inputs still needed from the team
Search `report/data266_lab2_report.tex` for `PENDING` and `MISSING`:
- Author names, team number, GitHub URL.
- Part 1 content (if one report covers Parts 1–3).
- Part 2: human win rates, plus the visual judgement of memorization and the safety-flag check.
- Part 3: human pass rates per condition, Cohen's κ, critic/human agreement, the R01/R02 verdicts and the final attack-success rate out of 10.
- Gradio screenshots, per-member contributions, conclusions after the human evaluation.
- Verify every bibliography entry.

## 3. Hugging Face publication (do NOT run without explicit authorization)

| Artifact | Staged folder (`$WORK` = `/app/data266_lab2_work`) | Size | Licence / redistribution | Card |
|---|---|---|---|---|
| P2 selected adapter (LoRA A, r4) | `p2/hf_staging/P2-EXP-001/final/` | 3.4 MB | OpenRAIL-M + CC BY-NC-SA 4.0; non-commercial, share-alike; copyrighted characters → research only | yes |
| P2 run A | `p2/hf_staging/P2-EXP-001/run_A/` | 3.4 MB | same | yes (same weights as `final`) |
| P2 run B (r64) | `p2/hf_staging/P2-EXP-001/run_B/` | 50 MB | same | yes |
| P2 120 generated images | `p2/hf_staging/P2-EXP-001/images/` | 41 MB | same; images resemble copyrighted characters | yes — **regenerate before upload** (below) |
| P3 evaluation inputs v2 | `p3/hf_staging/p3_inputs_v2/` | 5.3 MB | Commons CC BY / CC BY-SA 4.0 / public domain; fixtures CC0; the 3 Part 2 test images are **referenced, not re-hosted** (CC BY-NC-SA, copyrighted characters) | yes |

**Not to publish:** red-team outputs (`DO_NOT_PUBLISH.txt`), the human packets and private answer keys, `*_LOCAL_ONLY*` raw replies, `human_packet_KEY_private.csv`, `.env`.

**Before uploading the P2 image dataset:** its staged `metadata.jsonl` was written before D-116 and contains `NaN` (80 of 120 lines), which strict JSON-Lines readers reject. Running `p2_finetune.ipynb` with `MODE = "REPORT_ONLY"` (which you do after the human ratings anyway) re-stages it with the fixed writer. Check afterwards:
`docker exec data266-lab2 grep -c NaN /app/data266_lab2_work/p2/hf_staging/P2-EXP-001/images/metadata.jsonl` must print `0`.

**Upload procedure, once authorized.** This uses the CLI from the staged folders, so no notebook code changes. Changing the upload settings inside `p3_agents.ipynb` would alter its frozen code fingerprint.
```bash
docker exec -it data266-lab2 bash
hf auth login                      # paste a WRITE token interactively; never put it in a file in the repo
U=<your-hf-username>               # decide repo names, e.g.:
hf upload $U/data266-lab2-p2-lora-r4      /app/data266_lab2_work/p2/hf_staging/P2-EXP-001/final  . --repo-type model   --private
hf upload $U/data266-lab2-p2-lora-r64     /app/data266_lab2_work/p2/hf_staging/P2-EXP-001/run_B  . --repo-type model   --private
hf upload $U/data266-lab2-p2-images       /app/data266_lab2_work/p2/hf_staging/P2-EXP-001/images . --repo-type dataset --private
hf upload $U/data266-lab2-p3-inputs-v2    /app/data266_lab2_work/p3/hf_staging/p3_inputs_v2      . --repo-type dataset --private
hf auth logout
```
- Repos are created **private**. If the instructor must access them, either add the instructor as a collaborator or make them public. Making them public is a separate decision, because the Pokémon-derived content is non-commercial and depicts copyrighted characters.
- Record the repo URLs and commit hashes in `links.txt` and `README.md`.

## 4. GitHub and Canvas (do NOT run without explicit authorization)
1. Create the **private** GitHub repository `data266-lab2-team<##>` (D-001) and give the instructor/TA access.
2. Push, from `/app/implementation` in the container:
   ```bash
   git remote add origin <url>
   git push -u origin main
   ```
3. Optional: fix the message of local commit `b035d2a` with `git rebase -i` **before** the first push, or leave it.
4. Tags, if the PDF requires them (names *not verified*), e.g.:
   ```bash
   git tag -a p2-v1.0 <commit>
   git tag -a p3-v1.0 <commit>
   git push --tags
   ```
5. Canvas ZIP (*assumption*, D-011, D-039): the repository working files plus `links.txt`, without `.git/`, caches, model weights, `$WORK` data, `.env`, professor PDFs/data. Add the final report PDF.
