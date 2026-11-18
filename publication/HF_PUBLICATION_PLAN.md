# Hugging Face publication plan — Pair 44 (NOT AUTHORIZED, nothing uploaded)

Account `Parthp01`; all four repositories are **private**. Checked file lists, sizes and SHA-256 values: `publication/hf_publication_manifest.json`, generated from the staging folders. Staging paths below are inside the container (`$WORK` = `/app/data266_lab2_work`).

| # | Repository | Type | Staged folder | Files | Size | Card | Approval |
|---|---|---|---|---|---|---|---|
| 1 | `Parthp01/data266-lab2-lora-a` | model | `$WORK/p2/hf_staging/P2-EXP-001/run_A` | 4 | 3.3 MB | yes (`README.md`) | ☐ team |
| 2 | `Parthp01/data266-lab2-lora-b` | model | `$WORK/p2/hf_staging/P2-EXP-001/run_B` | 4 | 48.9 MB | yes | ☐ team |
| 3 | `Parthp01/data266-lab2-generated-images` | dataset | `$WORK/p2/hf_staging/P2-EXP-001/images` | 122 (120 PNG + metadata.jsonl + card) | 40.3 MB | yes | ☐ team |
| 4 | `Parthp01/data266-lab2-p3-inputs` | dataset | `$WORK/p3/hf_staging/p3_inputs_v2` | 20 | 5.2 MB | yes | ☐ team |

**Verified (2026-11-18):**
- The LoRA A weights (`20d8d67121db…`) equal `SELECTED_FINAL_ADAPTER.json`.
- `metadata.jsonl` parses as strict JSON: 120 rows, 0 `NaN`. All 120 image hashes match the frozen generation directory.
- No private, local-only, answer-key, judging-packet or `DO_NOT_PUBLISH` file is in any staged folder.
- Red-team outputs are not staged.
- The `final/` staging folder is a duplicate of `run_A` and is deliberately **not** uploaded: repo 1 is the selected adapter.

## Rights and licence audit

| Artifact | Rights holders / licences | Finding |
|---|---|---|
| LoRA A/B weights | Base SD 1.5: CreativeML **OpenRAIL-M** (use restrictions pass on to derivatives). Training data `reach-vb/pokemon-blip-captions`: card states **CC BY-NC-SA 4.0**. Images depict **copyrighted Pokémon characters** (Nintendo / Game Freak / The Pokémon Company). | Publish only privately for grading, as non-commercial research. The dataset licence does not grant rights to the characters. **Before upload:** add the OpenRAIL-M use-restriction notice (or a link to the licence) to both cards, because OpenRAIL-M requires passing the restrictions on. |
| 120 generated images | Same chain (derivatives of an NC-SA-trained model; character resemblance) | Private only; card states NC-SA and research-only. The 12 safety-flagged images are stored black, as produced. |
| P3 inputs | Commons photos: CC BY 4.0 (dog, cat) and CC BY-SA 4.0 (tray meal, brick building), redistributed as resized derivatives with attribution in `manifest.csv` (BY-SA derivatives shared alike). Portrait of Henry Solon Graves: public domain (Library of Congress, no known restrictions). Injection posters and broken files: CC0 (team-made). | OK to publish privately. The 3 Part 2 test images (`p2_test:*`) are **referenced only, not re-hosted** (NC-SA, copyrighted characters). No red-team output of the real person is included or allowed. |

**A private repository does not remove these restrictions.** It only limits who can see the files. Graders cannot open private repositories unless they are added as collaborators, or the repositories belong to an organization they can access. Confirm with the instructor which access method is expected.

## Upload commands (run only after written authorization)
```bash
docker exec -it data266-lab2 bash
hf auth login                      # WRITE token, entered interactively; never stored in the repository
S=/app/data266_lab2_work
hf upload Parthp01/data266-lab2-lora-a             $S/p2/hf_staging/P2-EXP-001/run_A  . --repo-type model   --private
hf upload Parthp01/data266-lab2-lora-b             $S/p2/hf_staging/P2-EXP-001/run_B  . --repo-type model   --private
hf upload Parthp01/data266-lab2-generated-images   $S/p2/hf_staging/P2-EXP-001/images . --repo-type dataset --private
hf upload Parthp01/data266-lab2-p3-inputs          $S/p3/hf_staging/p3_inputs_v2      . --repo-type dataset --private
hf auth logout
```

## After upload
1. Grant grader access.
2. Record each repository URL and its commit hash (from the repository page → *Files and versions* → history) in `links.txt`.
3. Re-run `python3 publication/build_canvas_zip.py` (Canvas ZIP).
