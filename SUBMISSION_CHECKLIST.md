# Submission checklist — DATA 266 Lab 2, Pair Programming Team 44 (status 2026-11-18)

**Requirement source.** The 17 requirements below were verified by the team from `DATA266_Lab2_Requirements.pdf` and `DATA266_Fall2026_Lab_2.pdf`. The PDFs themselves are not on this machine. Statuses come from evidence checked locally.

**Overall verdict: READY WITH CONDITIONS (updated 2026-11-18, D-119).**
- **Done locally:**
  - The report contains all verified results.
  - Part 2 human evaluation: complete (D-118).
  - Part 3: one human evaluator plus one disclosed AI evaluator. This is supplemental, and the 18 disagreements are unresolved.
- **Remaining:**
  - team details (contributions, recordings; the author names are known);
  - the Kaggle notebook URL;
  - the PDF build;
  - repository privacy, push and tags;
  - Hugging Face publication;
  - the Canvas ZIP.

Legend: **COMPLETE** · **PENDING HUMAN INPUT** · **PENDING PUBLICATION** (needs your authorization) · **BLOCKED** · **NOT VERIFIED**

| # | Requirement | Status | Evidence / what is missing |
|---|---|---|---|
| 1 | One IEEE PDF covering Parts 1–3, ≤ 12 pages per part + appendices | **PENDING HUMAN INPUT** | `report/data266_lab2_report.tex`: all three parts, about 6,400 words. It has been structure-checked: braces, environments and references are consistent. The Part 2 and Part 3 evaluation results are filled in. **4 `\pending{}` remain, all team input:** repository access, UI screenshots, Hugging Face publication, contributions. The author names and the Part 1 final version (V14-R1) are filled in. **No PDF yet:** there is no TeX toolchain here, so compile on Overleaf (§3). |
| 2 | Architecture diagram, baseline/final results, analysis, safety per part | COMPLETE (draft) | Figs. 1–2 (TikZ), Tables I–VI, safety sections for each part |
| 3 | Executed notebooks with saved outputs | COMPLETE | `p1_rag.ipynb` (final P1-KAGGLE-V14-R1, Kaggle T4, 13 of 17 code cells with outputs, D-120), `p2_finetune.ipynb` (P2-EXP-001 FULL_RUN, 61), `p2_finetune_REPORT_ONLY_human_eval.ipynb` (P2-EXP-001 REPORT_ONLY with the real ratings, D-118), `p3_agents.ipynb` (P3-EXP-003 FULL_EVALUATION, 67) |
| 4 | Reproducible requirements, README, fixed seeds, run metadata | COMPLETE for P2/P3 · **NOT VERIFIED** for P1 | P2/P3: `docker/requirements-p2p3.lock.txt` (207 pins), run manifests, seed 266. P1: `requirements-p1.txt` holds the versions recorded by the final Kaggle run (transformers 5.16.1, bitsandbytes 0.49.0, torch 2.11.0+cu130); there is no full freeze, and model revisions are not pinned. |
| 5 | Private GitHub repo with instructor/ISA read access | **BLOCKED** | `shulamite512/DATA266_LAB2_PAIR44` is **PUBLIC** and empty (GitHub API, 2026-11-18). Make it private and add the instructor/ISA before pushing. Naming differs from `data266-lab2-team##` (team choice; flag). |
| 6 | Tags `p1-v1.0`, `p2-v1.0`, `p3-v1.0` | COMPLETE locally · **not pushed** | Annotated local tags: `p1-v1.0` → `79af4ba` (Part 1 V14-R1), `p2-v1.0` → `5570487` (P2-EXP-001), `p3-v1.0` → the Part 3 release commit (D-121). Push after the repository is private (§4). |
| 7 | Part 2 adapters + generated-image dataset on Hugging Face | **PENDING PUBLICATION** | Staged; `publication/HF_PUBLICATION_PLAN.md`. **Re-check before upload:** the D-118 `REPORT_ONLY` run added the human result to the staged `run_A/README.md` (sha256 now `3a722831…`), so `publication/hf_publication_manifest.json` (`d63bcf5a…`) is stale for that card. **Re-verified 2026-11-18:** 4 repos, 150 files. All hashes match except `run_A/README.md`. There are no missing, extra or forbidden files, and the OpenRAIL-M notice is present in the 3 Part 2 cards. To do: approve the new card hash `3a722831…`, then upload. |
| 8 | Part 2 model card, Part 3 system card | COMPLETE (local) | Cards in the HF staging folders (real repo ids, D-117); system card `eval/p3_P3-EXP-003_system_card.md` (copy of `$WORK/p3/experiments/P3-EXP-003/system_card.md`; summary in the report) |
| 9 | Part 3 reproducible input images on Hugging Face | **PENDING PUBLICATION** | `p3_inputs_v2` staged (20 files, manifest with licences and hashes) |
| 10 | ≥ 3 genuine Part 2 raters | COMPLETE | `eval/p2_human_ratings.csv` (3 raters × 25 pairs × 2 criteria = 150 rows, validated, committed `e53130b` before scoring), scored by `notebooks/p2_finetune_REPORT_ONLY_human_eval.ipynb`: LoRA A win rate 38.7 % style / 41.3 % prompt (D-118). The team should confirm that the rater composition (both members + one outside person) is as designed. |
| 11 | Independent Part 3 judgments by both members | **NOT MET AS WRITTEN** (supplemental substitute) | `member_a` completed 52/52. The second evaluator is an AI (Claude Opus 5.5), disclosed in the report, `AI_USAGE.md` and D-119. Agreement: scenarios 20/30, κ 0.40; 18 disagreements unresolved. The team reports a **verbal** instructor allowance for AI judging; **get it in writing**, or have `member_b` judge before the deadline. |
| 12 | CONTRIBUTIONS.md with real contributions + recording links | **PENDING HUMAN INPUT** | Task table prepared; names, handles, owners and recording links are blank |
| 13 | AI_USAGE.md | COMPLETE | Updated through this preparation. The "Other AI tools" section must be completed by the team if any were used. |
| 14 | links.txt (repo, tag commits, HF links, final Kaggle notebook) | **PENDING HUMAN INPUT / PUBLICATION** | GitHub URL, the selected Kaggle submission and the planned HF URLs are filled in. The tag commit IDs are written into the working-tree copy after tagging. Still pending: the uploads, the Kaggle notebook URL and the recordings. |
| 15 | Canvas ZIP `Pair_Programming_Team_44.zip` | **PENDING** | `publication/build_canvas_zip.py` builds a **PREVIEW** now; `--final` refuses until the PDF and links are complete |
| 16 | Final Part 1 Kaggle submission selected on the leaderboard | COMPLETE (team-confirmed) | The final submission is the output of P1-KAGGLE-V14-R1 (`eval/p1_submission.csv`, 40 rows, validator valid), confirmed by the team (D-120). Its leaderboard score is not recorded. |
| 17 | Workloads runnable on a single 16 GB GPU | P1 **VERIFIED on a Kaggle T4** · P2/P3 **NOT VERIFIED** | P1: the final run used a Kaggle T4 (14.9 GB): 2,616 s of 5,400 s, at most 4.6 GB per model call, 4-bit NF4. P2 6.3–6.5 GB and P3 12.5 GB peaks were measured on an RTX 5090 with a 16 GB allocator cap, which is not proof for real 16 GB hardware. |

**Security and size (verified).**
- 142 tracked files, 7.8 MB.
- No weights, archives, `.env`, tokens, local-only raw replies, private keys or judging packets are tracked.
- Images are only the report figures. The five Wikimedia originals in `traces/` are git-ignored.
- The Jupyter token appears in no tracked file.

## 1. Experiments (preserved, final evidence)

| Experiment | Status | Final? |
|---|---|---|
| P1-EXP-001 / 002 / 003 | executed; history merged (`dbd01db`); 003 = checkpoint `eb87662` (historical) | no |
| P1-KAGGLE-V14-R1 | executed on a Kaggle T4; notebook + submission committed `79af4ba` (D-120) | **yes** |
| P1-EXP-004 (uncommitted, original Part 1 folder) | 2 executed runs (50/52, 52/53 self-checks), D-110/D-111 code never run | not integrated |
| P2-EXP-001 | complete; REPORT_ONLY re-staged the upload folders (D-117); human ratings scored by REPORT_ONLY (D-118) | yes |
| P3-EXP-001 / 002 / 003 | complete; 003 has 6 `FAILED_MODEL` records (confirmed repetition loop) | P3-EXP-003 |

## 2. Report inputs still needed
Search `report/data266_lab2_report.tex` for `PENDING`:
- **Front matter:** repository access (the names are filled in).
- **Part 1:** done (V14-R1; its Kaggle score is stated as not recorded). Groundedness is stated as *not rated*, with the reason given.
- **Part 3:** UI screenshots, which need a team decision. A DEMO run would load models, so either take screenshots or delete the `\pending` line. The evaluator results are filled in.
- **End matter:** contributions; Hugging Face publication status.
- **Done:** memorization and safety-flag text are worded from the evidence. The conclusions are updated. The Qwen and BGE references are kept as model-card citations; verify them on Overleaf if the course requires papers.

## 3. Build the PDF (Overleaf)
1. In Overleaf, choose New Project → Upload Project and upload a ZIP of the repository's `report/` folder (`data266_lab2_report.tex` + `figures/`).
2. Set the compiler to pdfLaTeX and the main document to `data266_lab2_report.tex`, then compile twice so cross-references resolve.
3. Check:
   - no `??` in the PDF;
   - all 6 figures render;
   - every part stays within 12 pages.
4. Download the PDF and save it as `report/data266_lab2_report.pdf`.

## 4. GitHub (after making the repository private; do not force-push)
The target repository is empty, so there is no teammate history to reconcile. Re-check with `git ls-remote <url>` immediately before pushing.
```bash
docker exec -it data266-lab2 bash
cd /app/implementation
git remote add origin https://github.com/shulamite512/DATA266_LAB2_PAIR44.git
git ls-remote origin                         # must print nothing (empty) - otherwise STOP and reconcile
git push -u origin main                      # needs the repo owner's credentials
# the three annotated tags already exist locally (p1-v1.0 -> 79af4ba, p2-v1.0 -> 5570487, p3-v1.0 -> Part 3 release commit)
git push origin p1-v1.0 p2-v1.0 p3-v1.0
git rev-parse p1-v1.0^{commit} p2-v1.0^{commit} p3-v1.0^{commit}   # copy into links.txt
```
- The old Part 1 remote `Parthp28/DATA266_LAB2_Pair44` received only `d9bbd68`. Decide whether it should be archived, or kept as the source of the earlier timestamps; its history is already contained here.
- The local commit `b035d2a` has the truncated message "Record". It can only be reworded before the first push.

## 5. Canvas
```bash
docker exec -w /app/implementation data266-lab2 python3 publication/build_canvas_zip.py --final
```
Output: `C:\Users\parth3\data266_lab2_work\submission\Pair_Programming_Team_44.zip`, containing:
- `data266_lab2_report.pdf`
- `CONTRIBUTIONS.md`
- `AI_USAGE.md`
- `links.txt`
- `SHA256SUMS.txt`

Upload it only after explicit authorization.
