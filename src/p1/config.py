"""Part 1 configuration. `final` = hybrid system; `baseline_config()` = dense retrieval only."""
import dataclasses
import glob
import os
from dataclasses import dataclass, field


def find_data_dir():
    env = os.environ.get("P1_DATA_DIR")
    if env:
        return env
    for root in ("data/p1", "/kaggle/input"):
        hits = glob.glob(os.path.join(root, "**", "kb_manifest.json"), recursive=True)
        if hits:
            return os.path.dirname(hits[0])
    return "data/p1"


@dataclass
class P1Config:
    data_dir: str = field(default_factory=find_data_dir)
    work_dir: str = field(default_factory=lambda: os.environ.get("P1_WORK_DIR", "outputs/p1"))
    embed_model: str = "BAAI/bge-small-en-v1.5"
    query_prefix: str = "Represent this sentence for searching relevant passages: "
    vlm_model: str = field(default_factory=lambda: os.environ.get("P1_VLM", "Qwen/Qwen2.5-VL-3B-Instruct"))
    vlm_4bit: bool = field(default_factory=lambda: os.environ.get("P1_VLM_4BIT", "0") == "1")
    reranker_model: str = "BAAI/bge-reranker-base"
    # --- switches that distinguish baseline from final ---
    use_bm25: bool = True             # hybrid dense + BM25 (RRF fusion)
    use_label_lookup: bool = True     # exact Figure/Table label routing + document hints
    filter_untrusted: bool = True     # never pass low-trust sections (Appendix C) as evidence
    use_reranker: bool = False        # bonus: cross-encoder reranker
    # --- ingestion ---
    describe_figures: bool = True     # VLM text descriptions make figures searchable
    fallback_untrusted_sections: tuple = ("Appendix C",)  # used only if the manifest lists no sections
    chunk_chars: int = 900
    chunk_overlap: int = 150
    render_dpi: int = 150
    # --- retrieval / generation ---
    dense_k: int = 20
    bm25_k: int = 20
    rerank_k: int = 20
    final_k: int = field(default_factory=lambda: int(os.environ.get("P1_FINAL_K", "6")))
    rrf_k: int = 60
    max_images: int = field(default_factory=lambda: int(os.environ.get("P1_MAX_IMAGES", "2")))
    max_new_tokens: int = 350
    max_answer_words: int = 120
    permanent_change_status: str = "session_override"
    cite_figure_pages: bool = True    # sample_submission cites a figure together with its page

    def variant(self, **kw):
        return dataclasses.replace(self, **kw)


def baseline_config(base=None):
    """Baseline required by 1.4: dense retrieval only, no BM25 / label routing / trust filter."""
    return (base or P1Config()).variant(use_bm25=False, use_label_lookup=False,
                                        filter_untrusted=False, use_reranker=False)
