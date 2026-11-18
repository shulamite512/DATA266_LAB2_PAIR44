# Part 1 results - Chelsi

Notebook: [`notebooks/Chelsi/p1_rag.ipynb`](../../notebooks/Chelsi/p1_rag.ipynb) (Colab, Tesla T4, seed 266)

## Run summary (from the notebook output)
| Item | Value |
|---|---|
| Answer / figure-description model | `Qwen/Qwen2.5-VL-7B-Instruct`, 4-bit NF4 (`BACKEND = "qwen7b"`) |
| Embeddings | `BAAI/bge-small-en-v1.5` + BM25, fused with RRF (final_k = 6) |
| Indexed records | 212 text chunks, 36 figures/tables (DOC1 17, DOC2 10, DOC3 9) |
| Excluded from evidence | 3 records: DOC3 p7 Appendix C text and Figure C-1 (low trust / injection pattern) |
| Index build time | about 14 min (dominated by VLM descriptions of 36 figures) |
| Questions answered | 40 in 285 s, median 6.6 s per question; `validate_submission.py`: valid, 40 rows |
| Status mix | 31 answered, 2 false_premise, 1 conflict, 1 not_found, 5 session_override |

## Files
| File | What it is |
|---|---|
| `submission_p1_rag_notebook_run.csv` | the `submission.csv` written by the notebook above |
| `submission_earlier_run_score0.56.csv` | earlier run with the same model (Kaggle public score 0.56) |

Kaggle public scores: Qwen2.5-VL-3B 0.50, Qwen2.5-VL-7B 0.56 (earlier run), Qwen2.5-VL-7B about 0.50 (this notebook run).
