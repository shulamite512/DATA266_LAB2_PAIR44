"""Helpers shared by the notebooks: seeding and library-version reporting."""
import importlib
import random

import numpy as np
import torch

SEED = 266


def seed_everything(seed=SEED):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def library_versions(names=("transformers", "diffusers", "peft", "accelerate", "sentence_transformers",
                            "chromadb", "fitz", "rank_bm25", "torchmetrics", "lpips", "gradio", "datasets")):
    out = {}
    for n in names:
        try:
            m = importlib.import_module(n)
            out[n] = getattr(m, "__version__", getattr(m, "VersionBind", "?"))
        except Exception:
            out[n] = "not installed"
    return out
