"""Tolerant reader for kb_manifest.json (document IDs, file names, trust levels and any
section-level trust such as an untrusted appendix)."""
import json
import os
import re

TRUST_KEYS = ("trust_level", "trust", "trustLevel", "trust_rating")
TRUST_WORDS = {"high", "medium", "low", "untrusted", "none"}
TRUST_RANK = {"high": 3, "medium": 2, "low": 1, "untrusted": 0, "none": 0}
APX = re.compile(r"appendix\s+([A-Z])\b", re.I)


def _first(d, keys, default=None):
    for k in keys:
        if isinstance(d, dict) and k in d and d[k] not in (None, ""):
            return d[k]
    return default


def _section_trust(obj, out):
    if isinstance(obj, dict):
        name = _first(obj, ("section", "name", "title", "part", "id"))
        t = _first(obj, TRUST_KEYS)
        if name is not None and t is not None:
            m = APX.search(str(name))
            if m:
                out[f"Appendix {m.group(1).upper()}"] = str(t).lower()
        for k, v in obj.items():
            mk = APX.search(str(k))
            if mk:
                if isinstance(v, str) and v.lower() in TRUST_WORDS:
                    out[f"Appendix {mk.group(1).upper()}"] = v.lower()
                elif isinstance(v, dict) and _first(v, TRUST_KEYS):
                    out[f"Appendix {mk.group(1).upper()}"] = str(_first(v, TRUST_KEYS)).lower()
            elif isinstance(v, str):
                m = APX.search(v)
                if m and re.search(r"\b(low|untrusted|not trusted|do not trust)\b", v, re.I):
                    out[f"Appendix {m.group(1).upper()}"] = "low"
            elif isinstance(v, list) and re.search(r"untrust|low", str(k), re.I):
                for s in v:
                    m = APX.search(str(s))
                    if m:
                        out[f"Appendix {m.group(1).upper()}"] = "low"
            if isinstance(v, (dict, list)):
                _section_trust(v, out)
    elif isinstance(obj, list):
        for v in obj:
            if isinstance(v, (dict, list)):
                _section_trust(v, out)
    return out


def load_manifest(data_dir, fallback_untrusted_sections=("Appendix C",)):
    with open(os.path.join(data_dir, "kb_manifest.json"), encoding="utf-8") as f:
        raw = json.load(f)
    entries = raw
    if isinstance(raw, dict):
        for key in ("documents", "docs", "files", "kb", "items", "sources"):
            if key in raw:
                entries = raw[key]
                break
    if isinstance(entries, dict):
        entries = [dict(v, doc_id=k) if isinstance(v, dict) else {"doc_id": k, "file": v}
                   for k, v in entries.items()]
    docs = {}
    for e in entries:
        doc_id = str(_first(e, ("doc_id", "id", "document_id", "docid", "name")))
        fname = str(_first(e, ("file", "file_name", "filename", "path", "pdf")))
        trust = str(_first(e, TRUST_KEYS, "medium")).lower()
        sections = _section_trust(e, {})
        page_trust = {}
        for ov in e.get("section_trust_overrides", []) if isinstance(e, dict) else []:
            t = _first(ov, TRUST_KEYS)
            for p in ov.get("pages", []) if t else []:
                page_trust[int(p)] = str(t).lower()
        docs[doc_id] = {"doc_id": doc_id, "file": os.path.basename(fname), "trust_level": trust,
                        "section_trust": sections, "page_trust": page_trust, "raw": e}
    if not any(d["section_trust"] for d in docs.values()):
        # Manifest lists no section trust: apply the documented fallback to non-high-trust docs.
        for d in docs.values():
            if TRUST_RANK.get(d["trust_level"], 2) < 3:
                d["section_trust"] = {s: "low" for s in fallback_untrusted_sections}
    return docs


def doc_aliases(docs):
    """Names a user may use for each document: DOC2, doc 2, document 2, supplement a, briefing b..."""
    aliases = {}
    for did, d in docs.items():
        names = {did.lower()}
        m = re.search(r"(\d+)$", did)
        if m:
            n = m.group(1)
            names |= {f"doc {n}", f"doc{n}", f"document {n}"}
        toks = re.split(r"[_\s\-]+", os.path.splitext(d["file"])[0])
        for a, b in zip(toks, toks[1:]):
            if a.isalpha() and len(a) > 2 and len(b) == 1 and b.isalpha():
                names.add(f"{a.lower()} {b.lower()}")
        aliases[did] = names
    return aliases


def detect_doc(text, aliases):
    q = " " + re.sub(r"[^a-z0-9 ]", " ", text.lower()) + " "
    q = re.sub(r"\s+", " ", q)
    found = [did for did, names in aliases.items() if any(f" {n} " in q for n in names)]
    return found[0] if len(found) == 1 else None
