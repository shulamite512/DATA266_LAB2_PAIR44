"""2.1 Data preparation: drop corrupted / caption-less / duplicate images, 90/10 split
with seed 266, center-crop resize to 512x512, and write the in-domain prompts."""
import hashlib
import io
import json
import os
import random
import statistics

import numpy as np
from PIL import Image, ImageOps

from . import config as C


def dhash(img, size=16):
    g = img.convert("L").resize((size + 1, size), Image.LANCZOS)
    a = np.asarray(g, dtype=np.int16)
    return np.packbits((a[:, 1:] > a[:, :-1]).flatten()).tobytes().hex()


def prepare(dataset=C.DATASET, out_dir=C.DATA_DIR, seed=C.SEED, res=C.RESOLUTION):
    from datasets import Image as HFImage, load_dataset
    ds = load_dataset(dataset, split="train").cast_column("image", HFImage(decode=False))
    kept, report = [], {"source": dataset, "raw": len(ds), "corrupted": 0, "missing_caption": 0,
                        "exact_duplicates": 0, "near_duplicates": 0}
    seen_md5, seen_dh = set(), set()
    for ex in ds:
        try:
            raw = ex["image"]["bytes"] or open(ex["image"]["path"], "rb").read()
            img = Image.open(io.BytesIO(raw))
            img.load()
            img = img.convert("RGB")
            if min(img.size) < 64:
                raise ValueError("too small")
        except Exception:
            report["corrupted"] += 1
            continue
        cap = (ex.get("text") or "").strip()
        if not cap:
            report["missing_caption"] += 1
            continue
        md5 = hashlib.md5(img.tobytes()).hexdigest()
        if md5 in seen_md5:
            report["exact_duplicates"] += 1
            continue
        dh = dhash(img)
        if dh in seen_dh:
            report["near_duplicates"] += 1
            continue
        seen_md5.add(md5)
        seen_dh.add(dh)
        kept.append((img, cap))
    report["kept"] = len(kept)
    report["removed_total"] = report["raw"] - len(kept)
    idx = list(range(len(kept)))
    random.Random(seed).shuffle(idx)
    n_test = round(C.TEST_FRACTION * len(kept))
    splits = {"test": idx[:n_test], "train": idx[n_test:]}
    for split, ids in splits.items():
        d = os.path.join(out_dir, split)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "metadata.jsonl"), "w", encoding="utf-8") as f:
            for j, i in enumerate(ids):
                img, cap = kept[i]
                name = f"{split}_{j:04d}.png"
                ImageOps.fit(img, (res, res), Image.BICUBIC).save(os.path.join(d, name))
                f.write(json.dumps({"file_name": name, "text": cap}) + "\n")
        report[f"n_{split}"] = len(ids)
    caps = [c for _, c in kept]
    lens = [len(c.split()) for c in caps]
    report["caption_words_mean"] = round(statistics.mean(lens), 2)
    report["caption_words_min_max"] = [min(lens), max(lens)]
    report["orig_sizes_top"] = _top_sizes([im.size for im, _ in kept])
    os.makedirs(C.OUT_DIR, exist_ok=True)
    with open(os.path.join(C.OUT_DIR, "data_report.json"), "w") as f:
        json.dump(report, f, indent=2)
    return report


def _top_sizes(sizes, k=3):
    from collections import Counter
    return [[f"{w}x{h}", n] for (w, h), n in Counter(sizes).most_common(k)]


def load_split(split, data_dir=C.DATA_DIR):
    d = os.path.join(data_dir, split)
    with open(os.path.join(d, "metadata.jsonl"), encoding="utf-8") as f:
        rows = [json.loads(l) for l in f]
    return [(os.path.join(d, r["file_name"]), r["text"]) for r in rows]


def write_prompts(fixed_path="prompts/p2_prompts_fixed.json", out_path="prompts/p2_prompts.json",
                  data_dir=C.DATA_DIR, seed=C.SEED, n_in_domain=10):
    """10 in-domain prompts sampled from TEST captions + the fixed OOD/compositional ones.
    Commit the resulting file BEFORE training finishes (C2.3)."""
    with open(fixed_path, encoding="utf-8") as f:
        fixed = json.load(f)
    test = load_split("test", data_dir)
    picks = random.Random(seed).sample(range(len(test)), n_in_domain)
    prompts = [{"id": f"in_{k:02d}", "category": "in_domain", "prompt": test[i][1],
                "test_image": os.path.basename(test[i][0])} for k, i in enumerate(picks)]
    prompts += fixed["out_of_domain"] + fixed["compositional"]
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(prompts, f, indent=2)
    return prompts
