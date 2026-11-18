"""1.1 indexing (ChromaDB + BM25) and 1.2 hybrid retrieval with exact Figure/Table routing."""
import json
import os
import re

import numpy as np
import torch

from .ingest import ingest_all
from .manifest import detect_doc, doc_aliases, load_manifest

import logging
logging.getLogger("chromadb.telemetry.product.posthog").setLevel(logging.CRITICAL)  # harmless telemetry noise

COLLECTION = "kb_lab2"  # chromadb >= 1.0 requires 3-512 characters
STOP = set("the a an of in on for to and or is are was were what which how did does do at by with from as be "
           "this that it its according document documents".split())


def tokenize(text):
    toks = re.findall(r"[a-z0-9]+(?:[-.][a-z0-9]+)*", text.lower())
    return [t for t in toks if t not in STOP]


def _meta(r):
    return {"doc_id": r["doc_id"], "page": int(r["page"]), "figure_id": r.get("figure_id", ""),
            "trust_level": r["trust_level"], "kind": r["kind"], "section": r["section"] or "",
            "label": r["label"] or "", "cite": r["cite"], "evidence_ok": bool(r["evidence_ok"]),
            "image_path": r.get("image_path", "") or ""}


class KnowledgeBase:
    """Read-only store: built once from the PDFs; conversations never write to it."""

    def __init__(self, cfg, docs, records, embedder, collection):
        from rank_bm25 import BM25Okapi
        self.cfg, self.docs, self.records = cfg, docs, records
        self.by_id = {r["id"]: r for r in records}
        self.figures = [r for r in records if r["kind"] != "text"]
        self.embedder, self.collection = embedder, collection
        self.bm25 = BM25Okapi([tokenize(r["text"]) for r in records])
        self.aliases = doc_aliases(docs)
        self._reranker = None

    @classmethod
    def build(cls, cfg, vlm=None):
        import chromadb
        from chromadb.config import Settings
        from sentence_transformers import SentenceTransformer
        os.makedirs(cfg.work_dir, exist_ok=True)
        docs = load_manifest(cfg.data_dir, cfg.fallback_untrusted_sections)
        records = ingest_all(cfg, docs, vlm)
        with open(os.path.join(cfg.work_dir, "corpus.jsonl"), "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps({k: v for k, v in r.items() if k != "bbox"}, ensure_ascii=False) + "\n")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        embedder = SentenceTransformer(cfg.embed_model, device=device)
        embs = embedder.encode([r["text"] for r in records], batch_size=32, normalize_embeddings=True,
                               show_progress_bar=False)
        client = chromadb.PersistentClient(path=os.path.join(cfg.work_dir, "chroma"),
                                           settings=Settings(anonymized_telemetry=False))
        try:
            client.delete_collection(COLLECTION)
        except Exception:
            pass
        col = client.create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})
        for i in range(0, len(records), 256):
            batch = records[i:i + 256]
            col.add(ids=[r["id"] for r in batch], embeddings=embs[i:i + 256].tolist(),
                    documents=[r["text"] for r in batch], metadatas=[_meta(r) for r in batch])
        return cls(cfg, docs, records, embedder, col)

    def summary(self):
        import collections
        c = collections.Counter((r["doc_id"], r["kind"]) for r in self.records)
        low = sum(not r["evidence_ok"] for r in self.records)
        return {"records": len(self.records), "by_doc_kind": {f"{d}/{k}": n for (d, k), n in sorted(c.items())},
                "not_evidence (low trust or injected)": low,
                "labels": sorted({f["figure_id"] for f in self.figures})}

    # ------------------------------------------------------------------ retrieval
    def _reranker_model(self):
        if self._reranker is None:
            from sentence_transformers import CrossEncoder
            self._reranker = CrossEncoder(self.cfg.reranker_model,
                                          device="cuda" if torch.cuda.is_available() else "cpu")
        return self._reranker

    def lookup_labels(self, labels, cfg, doc_hint=None):
        out = []
        for base, corrected in labels:
            cands = [r for r in self.figures if r["base_label"] == base and (r["evidence_ok"] or not cfg.filter_untrusted)]
            if doc_hint:
                cands = [r for r in cands if r["doc_id"] == doc_hint] or cands
            if corrected is True:
                cands = [r for r in cands if r["corrected"]] or cands
            elif corrected is False:
                cands = [r for r in cands if not r["corrected"]] or cands
            # corrected version first: a correction replaces the earlier value (rule 1)
            for r in sorted(cands, key=lambda r: (not r["corrected"], r["doc_id"], r["page"])):
                if r not in out:
                    out.append(r)
        return out

    def search(self, query, cfg, labels=(), doc_hint=None):
        n = len(self.records)
        qemb = self.embedder.encode([cfg.query_prefix + query], normalize_embeddings=True)[0]
        kwargs = {"where": {"evidence_ok": True}} if cfg.filter_untrusted else {}
        res = self.collection.query(query_embeddings=[qemb.tolist()], n_results=min(cfg.dense_k, n), **kwargs)
        scores = {}
        for rank, rid in enumerate(res["ids"][0]):
            scores[rid] = scores.get(rid, 0.0) + 1.0 / (cfg.rrf_k + rank + 1)
        if cfg.use_bm25:
            bm = self.bm25.get_scores(tokenize(query))
            rank = 0
            for idx in np.argsort(-bm):
                if bm[idx] <= 0 or rank >= cfg.bm25_k:
                    break
                r = self.records[idx]
                if cfg.filter_untrusted and not r["evidence_ok"]:
                    continue
                scores[r["id"]] = scores.get(r["id"], 0.0) + 1.0 / (cfg.rrf_k + rank + 1)
                rank += 1
        fused = sorted(scores, key=scores.get, reverse=True)
        if cfg.use_reranker and fused:
            top = fused[:cfg.rerank_k]
            rs = self._reranker_model().predict([(query, self.by_id[i]["text"][:2000]) for i in top])
            fused = [top[i] for i in np.argsort(-np.asarray(rs))] + fused[cfg.rerank_k:]
        hits = [self.by_id[i] for i in fused]
        if cfg.use_label_lookup:
            if doc_hint:
                hits = [h for h in hits if h["doc_id"] == doc_hint] + [h for h in hits if h["doc_id"] != doc_hint]
            if labels:
                exact = self.lookup_labels(labels, cfg, doc_hint)
                if exact:
                    ids = {h["id"] for h in exact}
                    # never mix in other, look-alike figures when the user named one
                    hits = exact + [h for h in hits if h["id"] not in ids and h["kind"] == "text"]
        return hits

    def detect_doc(self, text):
        return detect_doc(text, self.aliases)
