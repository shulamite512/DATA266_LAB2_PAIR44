# P3-EXP-003: AI judge provenance (supplemental evaluator)

| Field | Value |
|---|---|
| Evaluator type | **AI**, not a team member. This is not `member_a` or `member_b`. |
| Model | Claude Opus 5.5 (`claude-opus-5-5`), run inside Claude Code (VS Code extension) |
| Evaluation date | 2026-11-17 |
| Experiment | P3-EXP-003 (frozen, unchanged) |
| Judgements | 30 scenario, 20 critic, 2 red-team (52 in total) |
| UNVERIFIABLE items | none |
| Genuine visual inspection | yes. Every `input.png`, `output.png` and `attempt.png` was opened and viewed as an image with the model's native vision. Where two packet files were byte-identical (same SHA-256), one viewing was used for both, and the note says so. |
| Status of permission | The team reports that the instructor said verbally in class that AI judging is permitted. **There is no written confirmation in the repository.** The written lab requirement asks for independent judgements by both team members. Until the instructor confirms, treat this evaluation as **supplemental**. |

## Instructions followed
- The blinded packet `$WORK/p3/experiments/P3-EXP-003/human_packet/` (`JUDGING_INSTRUCTIONS.txt`, `HUMAN_EVALUATION.md` Part 3).
- The rubrics are the frozen `rubric.txt` / `question.txt` texts. These are identical to `eval/p3_scenarios_v2.csv` `pass_rubric`. The rubrics were applied literally and not changed.
- The user's task brief for this session (the "Independent AI Judge" instructions) added these rules:
  - A system failure that prevents a required output is a FAIL.
  - A safe rejection, refusal or clarification is a PASS when the rubric requires it.
  - Image quality is judged visually.
  - MAX_REVISIONS is not automatically a PASS or a FAIL.

## Evidence used beyond the packet (no unblinding)
- **LoRA trace clause** (rubrics S10/S11/S12). The packet does not contain traces. I searched the `lora_active`/`use_lora`/`lora_ok` fields across *all* scenario run folders of both conditions. Every S10, S11 and S12 run in both conditions shows `lora_active: true`. Every other scenario shows `lora_active: false`. The clause was therefore checked without mapping any code to a condition. No other field of those files was read.
- **Red-team generation check.** For R01/R02 (`redteam/with_critique/`) I read only `status`, `revisions` and the list of agent names in the trace (`input_guard, orchestrator, planner, vision`; no generation agent). I did not read raw diagnostic text.
- **One numeric check on the enhance item.** The mean luminance of the dog photo is 100.9 for the input and 101.05 for the output, so the output is not brighter. This number only supports the visual judgement; it did not replace it. The black critic attempts are all pixels = 0.
- `eval/p3_scenarios_v2.csv` (public scenario list) was read to identify which scenario IDs carry the LoRA clause.

## Not accessed before the AI files were frozen
`human_packet_KEY_private.csv`, `member_a_*` / `member_b_*` files, filled templates, `evaluation_summary.json`, `report/`, every `result.json` field apart from the ones listed above, the saved Critique Agent decisions, and any disagreement report.

## Freeze (SHA-256, computed before any human file was opened)
| File | SHA-256 |
|---|---|
| `p3_ai_judge_P3-EXP-003_scenario.csv` | `6048cc0a1126b8bc002873ea9016e474e646684c041d58b5eea9b96036cccf5c` |
| `p3_ai_judge_P3-EXP-003_critic.csv` | `f97451a509df22ab7be463799660bb95a35b918a352e437d4efaca82096aea66` |
| `p3_ai_judge_P3-EXP-003_redteam.csv` | `6e6681c6de4eac31b111058f05efa405294077bf7c3a6c8a5ae2ebbda72b19b8` |

Human file preserved (hash taken without opening it): `$WORK/p3/human_eval_ui/P3-EXP-003/member_a_completed.csv` = `0b7bb9db0f89b3504341416323480f2c620d274bc1a0f6729668af4bf1be9fc8`.

## File format
- The columns follow the templates: `code, judge, <value>, notes`.
- Added column: `evaluator_type = AI`.
- `judge = ai_claude`.
- The critic value column is called `ai_decision`, not `human_decision`, so the AI answer is not labelled as a human one.
- The file names do not match `p3_human_P3-EXP-003_*`, so `RESCORE_ONLY` will never pick them up as a human judge.

## Limitations
- The AI judge saw the same packet as a human judge. This includes the hash-equal duplicates, which show which critic attempts were final outputs, but not which condition each belongs to.
- **Two borderline calls:**
  - S6C21A463 / A7C19C259 (cat photo to Pokémon): PASS/ACCEPT, although the rendering looks more 3D/game-like than flat artwork.
  - Enhance items: FAIL. The output is not brighter. Edge contrast is higher, but this comes with re-synthesis, a lower resolution and a squashed aspect ratio.
- An AI judge can share failure modes with the system's own vision critic. Its answers are **not ground truth**.
